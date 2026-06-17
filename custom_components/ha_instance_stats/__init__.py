"""HA Instance Stats - Custom component for Home Assistant statistics."""
from __future__ import annotations

import logging
import pathlib

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import HAInstanceStatsCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

_CARD_URL = "/ha_instance_stats/ha-instance-stats-card.js"
_CARD_PATH = pathlib.Path(__file__).parent / "www" / "ha-instance-stats-card.js"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the HA Instance Stats component."""
    hass.data.setdefault(DOMAIN, {})

    try:
        from homeassistant.components.http import StaticPathConfig
        await hass.http.async_register_static_paths(
            [StaticPathConfig(_CARD_URL, str(_CARD_PATH), False)]
        )
    except (ImportError, AttributeError):
        hass.http.register_static_path(_CARD_URL, str(_CARD_PATH), False)

    add_extra_js_url(hass, _CARD_URL)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HA Instance Stats from a config entry."""
    coordinator = HAInstanceStatsCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
