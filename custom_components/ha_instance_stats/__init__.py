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
_CARD_VERSION = json.loads(
    (pathlib.Path(__file__).parent / "manifest.json").read_text()
).get("version", "0")
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


async def _async_register_lovelace_resource(
    hass: HomeAssistant, url: str, base_url: str
) -> None:
    """Register the JS card in the Lovelace resource store.

    Retries up to 3 times (2 s apart) to handle the case where the Lovelace
    resource store is not yet initialised when HA_STARTED fires.  On each
    attempt any stale entry for the same base path but a different version is
    removed first, so that browser cache-busting via the ?v= query string
    works correctly across upgrades.
    """
    for attempt in range(3):
        try:
            resources = hass.data.get("lovelace", {}).get("resources")
            if resources is not None:
                to_remove = []
                for item in resources.async_items():
                    item_url = item.get("url", "")
                    if item_url == url:
                        return  # Correct version already registered
                    if item_url.startswith(base_url):
                        to_remove.append(item["id"])
                for item_id in to_remove:
                    await resources.async_delete_item(item_id)
                await resources.async_create_item({"res_type": "module", "url": url})
                _LOGGER.debug("Lovelace resource registered: %s", url)
                return
        except Exception as err:
            _LOGGER.debug(
                "Lovelace resource store attempt %d/%d failed: %s",
                attempt + 1, 3, err,
            )

        if attempt < 2:
            await asyncio.sleep(2)

    # Fallback for YAML-mode Lovelace or older HA versions
    try:
        from homeassistant.components.frontend import add_extra_js_url
        add_extra_js_url(hass, url)
        _LOGGER.debug("Lovelace resource registered via add_extra_js_url: %s", url)
    except Exception as err:
        _LOGGER.warning("Could not register Lovelace card resource: %s", err)


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
