"""Data coordinator for HA Instance Stats."""
from __future__ import annotations

import logging
import platform
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def _count_yaml_lines(path: Path) -> int | None:
    """Count non-empty, non-comment lines in a YAML file."""
    if not path.exists():
        return None
    count = 0
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                count += 1
    return count

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class HAInstanceStatsCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch all HA instance statistics."""

    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def _async_update_data(self) -> dict:
        """Fetch all statistics."""
        try:
            # HA API calls must run in the event loop
            data = self._collect_ha_data()
            # Blocking I/O runs in executor
            io_data = await self.hass.async_add_executor_job(
                self._collect_io_data, self.hass.config.config_dir
            )
            data.update(io_data)
            return data
        except Exception as err:
            raise UpdateFailed(f"Error fetching stats: {err}") from err

    def _collect_ha_data(self) -> dict:
        """Collect data from HA state machine and registries (event loop only)."""
        data = {}

        try:
            automation_ids = self.hass.states.async_entity_ids("automation")
            data["automation_count"] = len(automation_ids)
        except Exception:
            data["automation_count"] = None
            automation_ids = []

        try:
            failed = [
                eid for eid in automation_ids
                if (s := self.hass.states.get(eid)) and s.state == "unavailable"
            ]
            data["automation_failed_count"] = len(failed)
            data["automation_failed_ids"] = failed[:20]
        except Exception:
            data["automation_failed_count"] = None
            data["automation_failed_ids"] = []

        try:
            all_entries = self.hass.config_entries.async_entries()
            data["config_entries_count"] = len(all_entries)
            data["integration_count"] = sum(
                1 for e in all_entries
                if e.state.value in ("loaded", "setup_in_progress")
            )
        except Exception:
            data["config_entries_count"] = None
            data["integration_count"] = None

        try:
            data["entity_count"] = len(self.hass.states.async_all())
        except Exception:
            data["entity_count"] = None

        try:
            registry = dr.async_get(self.hass)
            data["device_count"] = len(registry.devices)
        except Exception:
            data["device_count"] = None

        try:
            data["script_count"] = len(self.hass.states.async_entity_ids("script"))
        except Exception:
            data["script_count"] = None

        try:
            data["scene_count"] = len(self.hass.states.async_entity_ids("scene"))
        except Exception:
            data["scene_count"] = None

        try:
            person_ids = self.hass.states.async_entity_ids("person")
            data["person_count"] = len(person_ids)
            data["persons_home_count"] = sum(
                1 for pid in person_ids
                if (s := self.hass.states.get(pid)) and s.state == "home"
            )
        except Exception:
            data["person_count"] = None
            data["persons_home_count"] = None

        try:
            data["zone_count"] = len(self.hass.states.async_entity_ids("zone"))
        except Exception:
            data["zone_count"] = None

        try:
            from homeassistant.const import __version__
            data["ha_version"] = __version__
        except Exception:
            data["ha_version"] = None

        return data

    def _collect_io_data(self, config_dir: str) -> dict:
        """Collect I/O-intensive data (runs in executor thread)."""
        data = {}
        config_path = Path(config_dir)

        try:
            f = config_path / "automations.yaml"
            if f.exists():
                size = f.stat().st_size
                data["automation_yaml_size_bytes"] = size
                data["automation_yaml_size_kb"] = round(size / 1024, 2)
            else:
                data["automation_yaml_size_bytes"] = 0
                data["automation_yaml_size_kb"] = 0.0
        except Exception:
            data["automation_yaml_size_bytes"] = None
            data["automation_yaml_size_kb"] = None

        try:
            data["automation_yaml_lines"] = _count_yaml_lines(config_path / "automations.yaml")
        except Exception:
            data["automation_yaml_lines"] = None

        try:
            data["script_yaml_lines"] = _count_yaml_lines(config_path / "scripts.yaml")
        except Exception:
            data["script_yaml_lines"] = None

        try:
            disk = shutil.disk_usage(config_dir)
            data["disk_total_gb"] = round(disk.total / (1024 ** 3), 2)
            data["disk_used_gb"] = round(disk.used / (1024 ** 3), 2)
            data["disk_free_gb"] = round(disk.free / (1024 ** 3), 2)
            data["disk_used_percent"] = round((disk.used / disk.total) * 100, 1)
        except Exception:
            data["disk_total_gb"] = None
            data["disk_used_gb"] = None
            data["disk_free_gb"] = None
            data["disk_used_percent"] = None

        try:
            with open("/proc/uptime") as f:
                uptime_seconds = float(f.readline().split()[0])
            now = datetime.now(timezone.utc)
            boot_dt = datetime.fromtimestamp(now.timestamp() - uptime_seconds, tz=timezone.utc)
            data["last_boot"] = boot_dt.isoformat()
            data["uptime_seconds"] = int(uptime_seconds)
            data["uptime_hours"] = round(uptime_seconds / 3600, 2)
        except Exception:
            data["last_boot"] = None
            data["uptime_seconds"] = None
            data["uptime_hours"] = None

        try:
            result = subprocess.run(
                ["systemd-analyze"], capture_output=True, text=True, timeout=5
            )
            output = result.stdout
            if "=" in output:
                total_part = output.split("=")[-1].strip().rstrip(".")
                if "min" in total_part:
                    parts = total_part.replace("min", "").replace("s", "").split()
                    boot_dur = float(parts[0]) * 60 + float(parts[1]) if len(parts) > 1 else 0.0
                elif "s" in total_part:
                    boot_dur = float(total_part.replace("s", "").strip())
                else:
                    boot_dur = None
                data["boot_duration_seconds"] = boot_dur
            else:
                data["boot_duration_seconds"] = None
        except Exception:
            data["boot_duration_seconds"] = None

        try:
            import psutil
            mem = psutil.virtual_memory()
            data["ram_total_gb"] = round(mem.total / (1024 ** 3), 2)
            data["ram_used_gb"] = round(mem.used / (1024 ** 3), 2)
            data["ram_free_gb"] = round(mem.available / (1024 ** 3), 2)
            data["ram_used_percent"] = round(mem.percent, 1)
        except ImportError:
            _LOGGER.warning("psutil not available – RAM stats will be unavailable")
            data["ram_total_gb"] = None
            data["ram_used_gb"] = None
            data["ram_free_gb"] = None
            data["ram_used_percent"] = None
        except Exception:
            data["ram_total_gb"] = None
            data["ram_used_gb"] = None
            data["ram_free_gb"] = None
            data["ram_used_percent"] = None

        try:
            import psutil
            data["cpu_used_percent"] = psutil.cpu_percent(interval=0.5)
            data["cpu_count"] = psutil.cpu_count(logical=True)
            freq = psutil.cpu_freq()
            data["cpu_freq_mhz"] = round(freq.current, 0) if freq else None
        except ImportError:
            data["cpu_used_percent"] = None
            data["cpu_count"] = None
            data["cpu_freq_mhz"] = None
        except Exception:
            data["cpu_used_percent"] = None
            data["cpu_count"] = None
            data["cpu_freq_mhz"] = None

        try:
            db_size = None
            for name in ("home-assistant_v2.db", "home-assistant.db"):
                p = config_path / name
                if p.exists():
                    db_size = round(p.stat().st_size / (1024 ** 2), 2)
                    break
            data["recorder_db_size_mb"] = db_size
        except Exception:
            data["recorder_db_size_mb"] = None

        try:
            bp_dir = config_path / "blueprints"
            data["blueprint_count"] = len(list(bp_dir.rglob("*.yaml"))) if bp_dir.exists() else 0
        except Exception:
            data["blueprint_count"] = None

        try:
            log_size = None
            for name in ("home-assistant.log", "home-assistant.log.1"):
                p = config_path / name
                if p.exists():
                    log_size = round(p.stat().st_size / 1024, 2)
                    break
            data["log_file_size_kb"] = log_size
        except Exception:
            data["log_file_size_kb"] = None

        try:
            total = sum(f.stat().st_size for f in config_path.rglob("*") if f.is_file())
            data["config_dir_size_mb"] = round(total / (1024 ** 2), 2)
        except Exception:
            data["config_dir_size_mb"] = None

        try:
            storage_path = config_path / ".storage" / "hacs.repositories"
            if storage_path.exists():
                import json
                with open(storage_path, encoding="utf-8") as f:
                    hacs_storage = json.load(f)
                repos = hacs_storage.get("data", {})
                if isinstance(repos, dict):
                    installed = [r for r in repos.values() if isinstance(r, dict) and r.get("installed")]
                    data["hacs_installed_count"] = len(installed)
                    categories: dict[str, int] = {}
                    for r in installed:
                        cat = r.get("category", "unknown")
                        categories[cat] = categories.get(cat, 0) + 1
                    data["hacs_categories"] = categories
                else:
                    data["hacs_installed_count"] = None
                    data["hacs_categories"] = {}
            else:
                data["hacs_installed_count"] = None
                data["hacs_categories"] = {}
        except Exception:
            data["hacs_installed_count"] = None
            data["hacs_categories"] = {}

        try:
            data["python_version"] = platform.python_version()
            data["python_implementation"] = platform.python_implementation()
        except Exception:
            data["python_version"] = None
            data["python_implementation"] = None

        return data
