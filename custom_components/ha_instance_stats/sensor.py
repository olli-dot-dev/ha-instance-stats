"""Sensor platform for HA Instance Stats."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfDataRate,
    UnitOfInformation,
    UnitOfTime,
    PERCENTAGE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import HAInstanceStatsCoordinator


@dataclass
class HAStatsSensorDescription(SensorEntityDescription):
    """Extended sensor description for HA Stats."""
    data_key: str = ""
    icon_override: str | None = None


SENSOR_DESCRIPTIONS: list[HAStatsSensorDescription] = [
    HAStatsSensorDescription(
        key="automation_count",
        data_key="automation_count",
        name="Automation Count",
        icon="mdi:robot",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HAStatsSensorDescription(
        key="automation_yaml_size",
        data_key="automation_yaml_size_kb",
        name="Automations YAML Size",
        native_unit_of_measurement="KB",
        icon="mdi:file-code",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HAStatsSensorDescription(
        key="integration_count",
        data_key="integration_count",
        name="Active Integrations",
        icon="mdi:puzzle",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HAStatsSensorDescription(
        key="config_entries_count",
        data_key="config_entries_count",
        name="Config Entries Total",
        icon="mdi:puzzle-outline",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HAStatsSensorDescription(
        key="entity_count",
        data_key="entity_count",
        name="Entity Count",
        icon="mdi:counter",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HAStatsSensorDescription(
        key="device_count",
        data_key="device_count",
        name="Device Count",
        icon="mdi:devices",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HAStatsSensorDescription(
        key="script_count",
        data_key="script_count",
        name="Script Count",
        icon="mdi:script-text",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HAStatsSensorDescription(
        key="scene_count",
        data_key="scene_count",
        name="Scene Count",
        icon="mdi:palette",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HAStatsSensorDescription(
        key="disk_free",
        data_key="disk_free_gb",
        name="Disk Free",
        native_unit_of_measurement="GB",
        device_class=SensorDeviceClass.DATA_SIZE,
        icon="mdi:harddisk",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HAStatsSensorDescription(
        key="disk_total",
        data_key="disk_total_gb",
        name="Disk Total",
        native_unit_of_measurement="GB",
        device_class=SensorDeviceClass.DATA_SIZE,
        icon="mdi:harddisk",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HAStatsSensorDescription(
        key="disk_used",
        data_key="disk_used_gb",
        name="Disk Used",
        native_unit_of_measurement="GB",
        device_class=SensorDeviceClass.DATA_SIZE,
        icon="mdi:harddisk",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HAStatsSensorDescription(
        key="disk_used_percent",
        data_key="disk_used_percent",
        name="Disk Used Percent",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:harddisk",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HAStatsSensorDescription(
        key="uptime_hours",
        data_key="uptime_hours",
        name="System Uptime",
        native_unit_of_measurement="h",
        device_class=SensorDeviceClass.DURATION,
        icon="mdi:timer-outline",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HAStatsSensorDescription(
        key="last_boot",
        data_key="last_boot",
        name="Last Boot",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:restart",
    ),
    HAStatsSensorDescription(
        key="boot_duration",
        data_key="boot_duration_seconds",
        name="Last Boot Duration",
        native_unit_of_measurement="s",
        device_class=SensorDeviceClass.DURATION,
        icon="mdi:timer-play",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HAStatsSensorDescription(
        key="ha_version",
        data_key="ha_version",
        name="HA Version",
        icon="mdi:home-assistant",
    ),
    HAStatsSensorDescription(
        key="config_dir_size",
        data_key="config_dir_size_mb",
        name="Config Directory Size",
        native_unit_of_measurement="MB",
        device_class=SensorDeviceClass.DATA_SIZE,
        icon="mdi:folder-information",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # --- RAM ---
    HAStatsSensorDescription(
        key="ram_used_percent",
        data_key="ram_used_percent",
        name="RAM Used Percent",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:memory",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HAStatsSensorDescription(
        key="ram_used_gb",
        data_key="ram_used_gb",
        name="RAM Used",
        native_unit_of_measurement="GB",
        device_class=SensorDeviceClass.DATA_SIZE,
        icon="mdi:memory",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HAStatsSensorDescription(
        key="ram_free_gb",
        data_key="ram_free_gb",
        name="RAM Free",
        native_unit_of_measurement="GB",
        device_class=SensorDeviceClass.DATA_SIZE,
        icon="mdi:memory",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HAStatsSensorDescription(
        key="ram_total_gb",
        data_key="ram_total_gb",
        name="RAM Total",
        native_unit_of_measurement="GB",
        device_class=SensorDeviceClass.DATA_SIZE,
        icon="mdi:memory",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # --- CPU ---
    HAStatsSensorDescription(
        key="cpu_used_percent",
        data_key="cpu_used_percent",
        name="CPU Usage",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:cpu-64-bit",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HAStatsSensorDescription(
        key="cpu_count",
        data_key="cpu_count",
        name="CPU Cores",
        icon="mdi:cpu-64-bit",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HAStatsSensorDescription(
        key="cpu_freq_mhz",
        data_key="cpu_freq_mhz",
        name="CPU Frequency",
        native_unit_of_measurement="MHz",
        icon="mdi:speedometer",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # --- Recorder DB ---
    HAStatsSensorDescription(
        key="recorder_db_size",
        data_key="recorder_db_size_mb",
        name="Recorder DB Size",
        native_unit_of_measurement="MB",
        device_class=SensorDeviceClass.DATA_SIZE,
        icon="mdi:database",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # --- Blueprints ---
    HAStatsSensorDescription(
        key="blueprint_count",
        data_key="blueprint_count",
        name="Blueprint Count",
        icon="mdi:source-branch",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # --- Log file ---
    HAStatsSensorDescription(
        key="log_file_size",
        data_key="log_file_size_kb",
        name="Log File Size",
        native_unit_of_measurement="KB",
        icon="mdi:text-box-outline",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # --- Failed automations ---
    HAStatsSensorDescription(
        key="automation_failed_count",
        data_key="automation_failed_count",
        name="Unavailable Automations",
        icon="mdi:robot-dead",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # --- Python ---
    HAStatsSensorDescription(
        key="python_version",
        data_key="python_version",
        name="Python Version",
        icon="mdi:language-python",
    ),
    # --- HACS ---
    HAStatsSensorDescription(
        key="hacs_installed_count",
        data_key="hacs_installed_count",
        name="HACS Installed",
        icon="mdi:store",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # --- Persons & Zones ---
    HAStatsSensorDescription(
        key="person_count",
        data_key="person_count",
        name="Person Count",
        icon="mdi:account-group",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HAStatsSensorDescription(
        key="persons_home_count",
        data_key="persons_home_count",
        name="Persons Home",
        icon="mdi:account-check",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HAStatsSensorDescription(
        key="zone_count",
        data_key="zone_count",
        name="Zone Count",
        icon="mdi:map-marker-radius",
        state_class=SensorStateClass.MEASUREMENT,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HA Instance Stats sensors."""
    coordinator: HAInstanceStatsCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        HAInstanceStatsSensor(coordinator, description)
        for description in SENSOR_DESCRIPTIONS
    ]
    async_add_entities(entities)


class HAInstanceStatsSensor(CoordinatorEntity, SensorEntity):
    """Sensor entity for a single HA Instance Stat."""

    entity_description: HAStatsSensorDescription

    def __init__(
        self,
        coordinator: HAInstanceStatsCoordinator,
        description: HAStatsSensorDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{DOMAIN}_{description.key}"
        self._attr_name = f"HA Stats {description.name}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, "ha_instance_stats")},
            "name": "HA Instance Stats",
            "manufacturer": "Custom",
            "model": "HA Instance Stats",
            "entry_type": "service",
        }

    @property
    def native_value(self) -> Any:
        """Return the sensor value."""
        if self.coordinator.data is None:
            return None
        value = self.coordinator.data.get(self.entity_description.data_key)
        # Handle timestamp sensors
        if self.entity_description.device_class == "timestamp" and value:
            from datetime import datetime, timezone
            try:
                from homeassistant.util.dt import parse_datetime
                return parse_datetime(value)
            except Exception:
                return None
        return value

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra attributes."""
        attrs = {}
        data = self.coordinator.data or {}

        if self.entity_description.key == "automation_count":
            attrs["yaml_size_bytes"] = data.get("automation_yaml_size_bytes")
        elif self.entity_description.key == "disk_free":
            attrs["disk_total_gb"] = data.get("disk_total_gb")
            attrs["disk_used_gb"] = data.get("disk_used_gb")
            attrs["disk_used_percent"] = data.get("disk_used_percent")
        elif self.entity_description.key == "last_boot":
            attrs["uptime_seconds"] = data.get("uptime_seconds")
            attrs["boot_duration_seconds"] = data.get("boot_duration_seconds")
        elif self.entity_description.key == "ram_used_percent":
            attrs["ram_total_gb"] = data.get("ram_total_gb")
            attrs["ram_used_gb"] = data.get("ram_used_gb")
            attrs["ram_free_gb"] = data.get("ram_free_gb")
        elif self.entity_description.key == "cpu_used_percent":
            attrs["cpu_count"] = data.get("cpu_count")
            attrs["cpu_freq_mhz"] = data.get("cpu_freq_mhz")
        elif self.entity_description.key == "hacs_installed_count":
            attrs["categories"] = data.get("hacs_categories", {})
        elif self.entity_description.key == "automation_failed_count":
            attrs["failed_entity_ids"] = data.get("automation_failed_ids", [])
        elif self.entity_description.key == "python_version":
            attrs["implementation"] = data.get("python_implementation")
        elif self.entity_description.key == "person_count":
            attrs["persons_home"] = data.get("persons_home_count")

        return attrs
