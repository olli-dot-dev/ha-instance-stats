"""HA Instance Stats - Custom component for Home Assistant statistics."""
from __future__ import annotations

import asyncio
import json
import logging
import pathlib

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import HAInstanceStatsCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

_CARD_PATH = pathlib.Path(__file__).parent / "www" / "ha-instance-stats-card.js"
_CARD_URL_BASE = "/ha_instance_stats/ha-instance-stats-card.js"
try:
    _CARD_VERSION = json.loads(
        (pathlib.Path(__file__).parent / "manifest.json").read_text()
    ).get("version", "0")
except Exception:
    _CARD_VERSION = "0"
_CARD_URL = f"{_CARD_URL_BASE}?v={_CARD_VERSION}"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the HA Instance Stats component."""
    hass.data.setdefault(DOMAIN, {})

    try:
        from homeassistant.components.http import StaticPathConfig
        await hass.http.async_register_static_paths(
            [StaticPathConfig(_CARD_URL_BASE, str(_CARD_PATH), False)]
        )
    except (ImportError, AttributeError):
        hass.http.register_static_path(_CARD_URL_BASE, str(_CARD_PATH), False)

    async def _register_card(_event=None):
        await _async_register_lovelace_resource(hass, _CARD_URL, _CARD_URL_BASE)

    if hass.is_running:
        await _register_card()
    else:
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, _register_card)

    return True


def _get_lovelace_resources(hass: HomeAssistant):
    """Return the Lovelace resource store, compatible with old (dict) and new (object) HA layouts."""
    lovelace = hass.data.get("lovelace")
    if lovelace is None:
        return None
    if isinstance(lovelace, dict):
        return lovelace.get("resources")
    return getattr(lovelace, "resources", None)


async def _async_register_lovelace_resource(
    hass: HomeAssistant, url: str, base_url: str
) -> None:
    """Register the JS card so HA loads it on every frontend page.

    Tries three mechanisms in order, logging the outcome of each at a
    level that is visible in HA's default log configuration (WARNING/INFO).
    """
    # 1. Frontend module injection (session-scoped, works in all Lovelace modes)
    try:
        from homeassistant.components import frontend as _frontend
        for _fn_name in ("add_extra_js_url", "add_extra_module_url"):
            _fn = getattr(_frontend, _fn_name, None)
            if callable(_fn):
                _fn(hass, url)
                _LOGGER.info("JS module injected via frontend.%s: %s", _fn_name, url)
                break
        else:
            _LOGGER.warning(
                "Neither add_extra_js_url nor add_extra_module_url found in "
                "homeassistant.components.frontend — skipping session injection."
            )
    except Exception as err:
        _LOGGER.warning("Frontend module injection failed: %s", err)

    # 2. Lovelace resource store (persistent, visible in Settings → Dashboards → Resources)
    for attempt in range(3):
        try:
            resources = _get_lovelace_resources(hass)
            if resources is None:
                _LOGGER.debug(
                    "Lovelace resource store not yet available (attempt %d/3)", attempt + 1
                )
                if attempt < 2:
                    await asyncio.sleep(2)
                continue

            to_remove = []
            for item in resources.async_items():
                item_url = item.get("url", "")
                if item_url == url:
                    _LOGGER.debug("Lovelace resource already registered: %s", url)
                    return
                if item_url.startswith(base_url):
                    item_id = item.get("id")
                    if item_id:
                        to_remove.append(item_id)

            await resources.async_create_item({"res_type": "module", "url": url})
            _LOGGER.info("Lovelace resource registered: %s", url)
            for item_id in to_remove:
                await resources.async_delete_item(item_id)
            return
        except Exception as err:
            _LOGGER.warning(
                "Lovelace resource store attempt %d/3 failed: %s", attempt + 1, err
            )
        if attempt < 2:
            await asyncio.sleep(2)

    _LOGGER.warning(
        "Automatic Lovelace resource registration failed. "
        "Add the card resource manually: "
        "Settings → Dashboards → Resources → + → URL: %s | Type: JavaScript Module",
        url,
    )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HA Instance Stats from a config entry."""
    coordinator = HAInstanceStatsCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Refresh once more after full startup so entity counts etc. are accurate
    if not hass.is_running:
        async def _refresh_on_start(_event=None):
            await coordinator.async_refresh()
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, _refresh_on_start)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
