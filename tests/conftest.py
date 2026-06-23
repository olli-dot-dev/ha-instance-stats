"""Mock the homeassistant package so tests run without a full HA install."""
import sys
from types import ModuleType
from unittest.mock import MagicMock


class _FakeDataUpdateCoordinator:
    def __init__(self, hass, logger, *, name, update_interval):
        self.hass = hass
        self.name = name
        self.update_interval = update_interval


_update_coordinator = ModuleType("homeassistant.helpers.update_coordinator")
_update_coordinator.DataUpdateCoordinator = _FakeDataUpdateCoordinator
_update_coordinator.UpdateFailed = RuntimeError
sys.modules["homeassistant.helpers.update_coordinator"] = _update_coordinator

for _mod in [
    "homeassistant",
    "homeassistant.core",
    "homeassistant.config_entries",
    "homeassistant.helpers",
    "homeassistant.helpers.device_registry",
    "homeassistant.const",
]:
    sys.modules.setdefault(_mod, MagicMock())
