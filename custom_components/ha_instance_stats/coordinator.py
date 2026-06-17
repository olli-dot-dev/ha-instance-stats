"""Data coordinator for HA Instance Stats."""
from __future__ import annotations

import logging
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class HAInstanceStatsCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch all HA instance statistics."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.hass = hass

    async def _async_update_data(self) -> dict:
        """Fetch all statistics."""
        try:
            return await self.hass.async_add_executor_job(self._fetch_all_stats)
        except Exception as err:
            raise UpdateFailed(f"Error fetching stats: {err}") from err

    def _fetch_all_stats(self) -> dict:
        """Collect all statistics synchronously."""
        data = {}

        # --- Automation stats ---
        try:
            automations = self.hass.states.async_entity_ids("automation")
            data["automation_count"] = len(automations)
        except Exception:
            data["automation_count"] = None

        # --- Automation YAML file size ---
        try:
            config_dir = self.hass.config.config_dir
            automation_file = Path(config_dir) / "automations.yaml"
            if automation_file.exists():
                size_bytes = automation_file.stat().st_size
                data["automation_yaml_size_bytes"] = size_bytes
                data["automation_yaml_size_kb"] = round(size_bytes / 1024, 2)
            else:
                data["automation_yaml_size_bytes"] = 0
                data["automation_yaml_size_kb"] = 0.0
        except Exception:
            data["automation_yaml_size_bytes"] = None
            data["automation_yaml_size_kb"] = None

        # --- Config entries (integrations) ---
        try:
            all_entries = self.hass.config_entries.async_entries()
            data["config_entries_count"] = len(all_entries)
            # Count only loaded/active entries
            active_entries = [
                e for e in all_entries
                if e.state.value in ("loaded", "setup_in_progress")
            ]
            data["integration_count"] = len(active_entries)
        except Exception:
            data["config_entries_count"] = None
            data["integration_count"] = None

        # --- Entity count ---
        try:
            data["entity_count"] = len(self.hass.states.async_all())
        except Exception:
            data["entity_count"] = None

        # --- Device count ---
        try:
            device_registry = self.hass.helpers.device_registry.async_get(self.hass)
            data["device_count"] = len(device_registry.devices)
        except Exception:
            data["device_count"] = None

        # --- Script count ---
        try:
            scripts = self.hass.states.async_entity_ids("script")
            data["script_count"] = len(scripts)
        except Exception:
            data["script_count"] = None

        # --- Scene count ---
        try:
            scenes = self.hass.states.async_entity_ids("scene")
            data["scene_count"] = len(scenes)
        except Exception:
            data["scene_count"] = None

        # --- Disk usage ---
        try:
            config_dir = self.hass.config.config_dir
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

        # --- Boot time & uptime ---
        try:
            # Use /proc/uptime for precise uptime (Linux)
            with open("/proc/uptime", "r") as f:
                uptime_seconds = float(f.readline().split()[0])

            now = datetime.now(timezone.utc)
            boot_time = now.timestamp() - uptime_seconds
            boot_dt = datetime.fromtimestamp(boot_time, tz=timezone.utc)

            data["last_boot"] = boot_dt.isoformat()
            data["uptime_seconds"] = int(uptime_seconds)
            data["uptime_hours"] = round(uptime_seconds / 3600, 2)

            # Boot duration via systemd (if available)
            try:
                result = subprocess.run(
                    ["systemd-analyze"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                output = result.stdout
                # Parse: "Startup finished in 5.321s (kernel) + 12.456s (userspace) = 17.777s"
                if "=" in output:
                    total_part = output.split("=")[-1].strip().rstrip(".")
                    # Extract seconds
                    if "min" in total_part:
                        parts = total_part.replace("min", "").replace("s", "").split()
                        boot_duration = float(parts[0]) * 60 + float(parts[1]) if len(parts) > 1 else 0
                    elif "s" in total_part:
                        boot_duration = float(total_part.replace("s", "").strip())
                    else:
                        boot_duration = None
                    data["boot_duration_seconds"] = boot_duration
                else:
                    data["boot_duration_seconds"] = None
            except Exception:
                data["boot_duration_seconds"] = None

        except Exception:
            data["last_boot"] = None
            data["uptime_seconds"] = None
            data["uptime_hours"] = None
            data["boot_duration_seconds"] = None

        # --- HA Version ---
        try:
            from homeassistant.const import __version__ as ha_version
            data["ha_version"] = ha_version
        except Exception:
            data["ha_version"] = "unknown"

        # --- Config dir size ---
        try:
            config_dir = self.hass.config.config_dir
            total_size = sum(
                f.stat().st_size
                for f in Path(config_dir).rglob("*")
                if f.is_file()
            )
            data["config_dir_size_mb"] = round(total_size / (1024 ** 2), 2)
        except Exception:
            data["config_dir_size_mb"] = None

        # --- RAM usage ---
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

        # --- CPU usage ---
        try:
            import psutil
            # interval=1 gives a real measurement; use 0.5 to keep polling fast
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

        # --- Recorder database size ---
        try:
            config_dir = self.hass.config.config_dir
            db_candidates = [
                Path(config_dir) / "home-assistant_v2.db",
                Path(config_dir) / "home-assistant.db",
            ]
            db_size = None
            for db_path in db_candidates:
                if db_path.exists():
                    db_size = round(db_path.stat().st_size / (1024 ** 2), 2)
                    break
            data["recorder_db_size_mb"] = db_size
        except Exception:
            data["recorder_db_size_mb"] = None

        # --- Blueprint count ---
        try:
            config_dir = self.hass.config.config_dir
            blueprints_dir = Path(config_dir) / "blueprints"
            if blueprints_dir.exists():
                blueprint_files = list(blueprints_dir.rglob("*.yaml"))
                data["blueprint_count"] = len(blueprint_files)
            else:
                data["blueprint_count"] = 0
        except Exception:
            data["blueprint_count"] = None

        # --- Log file size ---
        try:
            config_dir = self.hass.config.config_dir
            log_candidates = [
                Path(config_dir) / "home-assistant.log",
                Path(config_dir) / "home-assistant.log.1",
            ]
            log_size_kb = None
            for log_path in log_candidates:
                if log_path.exists():
                    log_size_kb = round(log_path.stat().st_size / 1024, 2)
                    break
            data["log_file_size_kb"] = log_size_kb
        except Exception:
            data["log_file_size_kb"] = None

        # --- Failed automations (error entries in logbook/states) ---
        try:
            automation_ids = self.hass.states.async_entity_ids("automation")
            failed = [
                eid for eid in automation_ids
                if (s := self.hass.states.get(eid)) and s.state == "unavailable"
            ]
            data["automation_failed_count"] = len(failed)
            data["automation_failed_ids"] = failed[:20]  # cap list for attributes
        except Exception:
            data["automation_failed_count"] = None
            data["automation_failed_ids"] = []

        # --- Python version ---
        try:
            data["python_version"] = platform.python_version()
            data["python_implementation"] = platform.python_implementation()
        except Exception:
            data["python_version"] = None
            data["python_implementation"] = None

        # --- HACS installed count ---
        try:
            hacs_data = None
            # Try reading HACS storage file directly
            storage_path = Path(self.hass.config.config_dir) / ".storage" / "hacs.repositories"
            if storage_path.exists():
                import json
                with open(storage_path, "r", encoding="utf-8") as f:
                    hacs_storage = json.load(f)
                repos = hacs_storage.get("data", {})
                if isinstance(repos, dict):
                    installed = [
                        r for r in repos.values()
                        if isinstance(r, dict) and r.get("installed", False)
                    ]
                    data["hacs_installed_count"] = len(installed)
                    # Break down by category
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

        # --- Active persons / zones ---
        try:
            persons = self.hass.states.async_entity_ids("person")
            data["person_count"] = len(persons)
            home_count = sum(
                1 for pid in persons
                if (s := self.hass.states.get(pid)) and s.state == "home"
            )
            data["persons_home_count"] = home_count
        except Exception:
            data["person_count"] = None
            data["persons_home_count"] = None

        try:
            zones = self.hass.states.async_entity_ids("zone")
            data["zone_count"] = len(zones)
        except Exception:
            data["zone_count"] = None

        return data
