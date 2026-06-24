"""Tests for HAInstanceStatsCoordinator."""
import json
from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest

from custom_components.ha_instance_stats.coordinator import (
    HAInstanceStatsCoordinator,
    _count_yaml_lines,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_entry(options=None, data=None):
    entry = MagicMock()
    entry.options = options or {}
    entry.data = data or {}
    return entry


def _make_coordinator(entry=None):
    return HAInstanceStatsCoordinator(MagicMock(), entry or _make_entry())


def _hass_with_states(entity_ids_by_domain=None, states_by_id=None, all_states=None, config_entries=None):
    """Return a MagicMock hass with predictable state responses."""
    hass = MagicMock()
    entity_ids_by_domain = entity_ids_by_domain or {}
    hass.states.async_entity_ids.side_effect = lambda d: entity_ids_by_domain.get(d, [])
    hass.states.async_all.return_value = all_states or []
    if states_by_id:
        hass.states.get.side_effect = lambda eid: states_by_id.get(eid)
    else:
        hass.states.get.return_value = MagicMock(state="on")
    hass.config_entries.async_entries.return_value = config_entries or []
    return hass


# ---------------------------------------------------------------------------
# _count_yaml_lines
# ---------------------------------------------------------------------------

def test_count_yaml_lines_counts_content_lines(tmp_path):
    (tmp_path / "f.yaml").write_text("key: value\nanother: line\n")
    assert _count_yaml_lines(tmp_path / "f.yaml") == 2


def test_count_yaml_lines_skips_comments_and_blanks(tmp_path):
    (tmp_path / "f.yaml").write_text("key: value\n# comment\n\nanother: line\n")
    assert _count_yaml_lines(tmp_path / "f.yaml") == 2


def test_count_yaml_lines_missing_file(tmp_path):
    assert _count_yaml_lines(tmp_path / "nope.yaml") is None


def test_count_yaml_lines_empty_file(tmp_path):
    (tmp_path / "f.yaml").write_text("")
    assert _count_yaml_lines(tmp_path / "f.yaml") == 0


# ---------------------------------------------------------------------------
# update_interval resolution
# ---------------------------------------------------------------------------

def test_update_interval_default():
    assert _make_coordinator().update_interval == timedelta(minutes=5)


def test_update_interval_from_options():
    coord = _make_coordinator(_make_entry(options={"update_interval": 10}))
    assert coord.update_interval == timedelta(minutes=10)


def test_update_interval_from_data():
    coord = _make_coordinator(_make_entry(data={"update_interval": 15}))
    assert coord.update_interval == timedelta(minutes=15)


def test_update_interval_options_take_priority_over_data():
    coord = _make_coordinator(_make_entry(options={"update_interval": 10}, data={"update_interval": 30}))
    assert coord.update_interval == timedelta(minutes=10)


# ---------------------------------------------------------------------------
# _collect_io_data — file system logic
# ---------------------------------------------------------------------------

def test_collect_io_data_automation_yaml_size(tmp_path):
    (tmp_path / "automations.yaml").write_text("- alias: test\n  trigger: []\n")
    result = _make_coordinator()._collect_io_data(str(tmp_path))
    assert result["automation_yaml_size_bytes"] > 0
    assert result["automation_yaml_lines"] == 2


def test_collect_io_data_missing_automations_yaml(tmp_path):
    result = _make_coordinator()._collect_io_data(str(tmp_path))
    assert result["automation_yaml_size_bytes"] == 0
    assert result["automation_yaml_lines"] is None


def test_collect_io_data_script_yaml_lines(tmp_path):
    (tmp_path / "scripts.yaml").write_text("script1:\n  sequence: []\n# comment\n")
    result = _make_coordinator()._collect_io_data(str(tmp_path))
    assert result["script_yaml_lines"] == 2


def test_collect_io_data_blueprint_count(tmp_path):
    bp = tmp_path / "blueprints" / "automation"
    bp.mkdir(parents=True)
    (bp / "a.yaml").write_text("")
    (bp / "b.yaml").write_text("")
    result = _make_coordinator()._collect_io_data(str(tmp_path))
    assert result["blueprint_count"] == 2


def test_collect_io_data_no_blueprints(tmp_path):
    result = _make_coordinator()._collect_io_data(str(tmp_path))
    assert result["blueprint_count"] == 0


def test_collect_io_data_disk_keys_present(tmp_path):
    result = _make_coordinator()._collect_io_data(str(tmp_path))
    for key in ("disk_total_gb", "disk_used_gb", "disk_free_gb", "disk_used_percent"):
        assert result[key] is not None


def test_collect_io_data_hacs_installed_count(tmp_path):
    storage = tmp_path / ".storage"
    storage.mkdir()
    (storage / "hacs.repositories").write_text(json.dumps({
        "data": {
            "r1": {"installed": True, "category": "integration"},
            "r2": {"installed": True, "category": "plugin"},
            "r3": {"installed": False, "category": "integration"},
        }
    }))
    result = _make_coordinator()._collect_io_data(str(tmp_path))
    assert result["hacs_installed_count"] == 2
    assert result["hacs_categories"] == {"integration": 1, "plugin": 1}


def test_collect_io_data_hacs_not_present(tmp_path):
    result = _make_coordinator()._collect_io_data(str(tmp_path))
    assert result["hacs_installed_count"] is None
    assert result["hacs_categories"] == {}


def test_collect_io_data_custom_component_count(tmp_path):
    cc = tmp_path / "custom_components"
    cc.mkdir()
    (cc / "my_integration").mkdir()
    (cc / "another_one").mkdir()
    (cc / "__pycache__").mkdir()
    result = _make_coordinator()._collect_io_data(str(tmp_path))
    assert result["custom_component_count"] == 2


def test_collect_io_data_custom_component_count_missing(tmp_path):
    result = _make_coordinator()._collect_io_data(str(tmp_path))
    assert result["custom_component_count"] == 0


def test_collect_io_data_recorder_db_size(tmp_path):
    db = tmp_path / "home-assistant_v2.db"
    db.write_bytes(b"x" * 1024 * 1024)  # 1 MB
    result = _make_coordinator()._collect_io_data(str(tmp_path))
    assert result["recorder_db_size_mb"] == pytest.approx(1.0, rel=0.01)


# ---------------------------------------------------------------------------
# _collect_ha_data — HA state machine logic
# ---------------------------------------------------------------------------

def _ha_data_patches():
    """Context manager that patches both dr and er for _collect_ha_data tests."""
    from contextlib import ExitStack
    from unittest.mock import patch, MagicMock
    stack = ExitStack()
    mock_dr = stack.enter_context(patch("custom_components.ha_instance_stats.coordinator.dr"))
    mock_er = stack.enter_context(patch("custom_components.ha_instance_stats.coordinator.er"))
    mock_dr.async_get.return_value = MagicMock(devices={})
    mock_er.async_get.return_value = MagicMock(entities={})
    return stack


def test_collect_ha_data_automation_count():
    coord = _make_coordinator()
    coord.hass = _hass_with_states(
        entity_ids_by_domain={"automation": ["automation.a", "automation.b"]},
    )
    with _ha_data_patches():
        result = coord._collect_ha_data()
    assert result["automation_count"] == 2


def test_collect_ha_data_failed_automations():
    coord = _make_coordinator()
    states = {
        "automation.a": MagicMock(state="on"),
        "automation.b": MagicMock(state="unavailable"),
        "automation.c": MagicMock(state="unavailable"),
    }
    coord.hass = _hass_with_states(
        entity_ids_by_domain={"automation": list(states)},
        states_by_id=states,
    )
    with _ha_data_patches():
        result = coord._collect_ha_data()
    assert result["automation_failed_count"] == 2
    assert set(result["automation_failed_ids"]) == {"automation.b", "automation.c"}


def test_collect_ha_data_entity_count():
    coord = _make_coordinator()
    coord.hass = _hass_with_states(all_states=[MagicMock(entity_id=f"s.{i}", state="on") for i in range(37)])
    with _ha_data_patches():
        result = coord._collect_ha_data()
    assert result["entity_count"] == 37


def test_collect_ha_data_device_count():
    coord = _make_coordinator()
    coord.hass = _hass_with_states()
    with patch("custom_components.ha_instance_stats.coordinator.dr") as mock_dr, \
         patch("custom_components.ha_instance_stats.coordinator.er") as mock_er:
        mock_dr.async_get.return_value = MagicMock(devices={"d1": 1, "d2": 2, "d3": 3})
        mock_er.async_get.return_value = MagicMock(entities={})
        result = coord._collect_ha_data()
    assert result["device_count"] == 3


def test_collect_ha_data_persons_home(tmp_path):
    coord = _make_coordinator()
    states = {
        "person.alice": MagicMock(state="home"),
        "person.bob": MagicMock(state="not_home"),
    }
    coord.hass = _hass_with_states(
        entity_ids_by_domain={"person": list(states)},
        states_by_id=states,
    )
    with _ha_data_patches():
        result = coord._collect_ha_data()
    assert result["person_count"] == 2
    assert result["persons_home_count"] == 1


# ---------------------------------------------------------------------------
# _collect_ha_data — health sensors
# ---------------------------------------------------------------------------

def test_collect_ha_data_helper_count():
    coord = _make_coordinator()
    coord.hass = _hass_with_states(entity_ids_by_domain={
        "input_boolean": ["input_boolean.a", "input_boolean.b"],
        "input_number": ["input_number.x"],
        "timer": ["timer.t"],
    })
    with _ha_data_patches():
        result = coord._collect_ha_data()
    assert result["helper_count"] == 4
    assert result["helper_counts_by_type"]["input_boolean"] == 2
    assert result["helper_counts_by_type"]["input_number"] == 1
    assert result["helper_counts_by_type"]["timer"] == 1
    assert result["helper_counts_by_type"]["counter"] == 0


def test_collect_ha_data_dashboard_count():
    coord = _make_coordinator()
    coord.hass = _hass_with_states(config_entries=[
        MagicMock(domain="lovelace"),
        MagicMock(domain="lovelace"),
        MagicMock(domain="zha"),
    ])
    with _ha_data_patches():
        result = coord._collect_ha_data()
    assert result["dashboard_count"] == 3  # 2 custom + 1 default


def test_collect_ha_data_unavailable_entity_count():
    coord = _make_coordinator()
    all_states = [
        MagicMock(entity_id="sensor.a", state="unavailable"),
        MagicMock(entity_id="sensor.b", state="on"),
        MagicMock(entity_id="sensor.c", state="unavailable"),
    ]
    coord.hass = _hass_with_states(all_states=all_states)
    with patch("custom_components.ha_instance_stats.coordinator.dr") as mock_dr, \
         patch("custom_components.ha_instance_stats.coordinator.er") as mock_er:
        mock_dr.async_get.return_value = MagicMock(devices={})
        mock_er.async_get.return_value = MagicMock(entities={})
        result = coord._collect_ha_data()
    assert result["unavailable_entity_count"] == 2
    assert set(result["unavailable_entity_ids"]) == {"sensor.a", "sensor.c"}


def test_collect_ha_data_pending_updates():
    coord = _make_coordinator()
    update_states = {
        "update.ha": MagicMock(state="on"),
        "update.addon": MagicMock(state="on"),
        "update.hacs": MagicMock(state="off"),
    }
    coord.hass = _hass_with_states(
        entity_ids_by_domain={"update": list(update_states)},
        states_by_id=update_states,
    )
    with patch("custom_components.ha_instance_stats.coordinator.dr") as mock_dr, \
         patch("custom_components.ha_instance_stats.coordinator.er") as mock_er:
        mock_dr.async_get.return_value = MagicMock(devices={})
        mock_er.async_get.return_value = MagicMock(entities={})
        result = coord._collect_ha_data()
    assert result["pending_updates_count"] == 2
    assert set(result["pending_update_ids"]) == {"update.ha", "update.addon"}


def test_collect_ha_data_battery_low():
    coord = _make_coordinator()
    coord.hass = _hass_with_states()

    low_entity = MagicMock()
    low_entity.entity_id = "sensor.door_battery"
    low_entity.device_class = "battery"
    low_entity.original_device_class = None

    ok_entity = MagicMock()
    ok_entity.entity_id = "sensor.phone_battery"
    ok_entity.device_class = "battery"
    ok_entity.original_device_class = None

    other_entity = MagicMock()
    other_entity.entity_id = "sensor.temperature"
    other_entity.device_class = "temperature"
    other_entity.original_device_class = None

    states = {
        "sensor.door_battery": MagicMock(state="12"),
        "sensor.phone_battery": MagicMock(state="85"),
    }
    coord.hass.states.get.side_effect = lambda eid: states.get(eid)

    with patch("custom_components.ha_instance_stats.coordinator.dr") as mock_dr, \
         patch("custom_components.ha_instance_stats.coordinator.er") as mock_er:
        mock_dr.async_get.return_value = MagicMock(devices={})
        mock_er.async_get.return_value = MagicMock(entities={
            "sensor.door_battery": low_entity,
            "sensor.phone_battery": ok_entity,
            "sensor.temperature": other_entity,
        })
        result = coord._collect_ha_data()

    assert result["battery_low_count"] == 1
    assert result["battery_low_entities"][0]["entity_id"] == "sensor.door_battery"
    assert result["battery_low_entities"][0]["level"] == 12.0
