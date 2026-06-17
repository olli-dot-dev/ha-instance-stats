# HA Instance Stats

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

A HACS integration for Home Assistant that exposes detailed statistics about your own instance as sensors and displays them in an elegant Lovelace card.

---

## 📊 Available Statistics

### Configuration
| Sensor | Description |
|--------|-------------|
| `sensor.ha_stats_automation_count` | Number of automations |
| `sensor.ha_stats_automations_yaml_size` | Size of `automations.yaml` in KB |
| `sensor.ha_stats_unavailable_automations` | Number of failed/unavailable automations |
| `sensor.ha_stats_blueprint_count` | Number of installed blueprints |
| `sensor.ha_stats_script_count` | Number of scripts |
| `sensor.ha_stats_scene_count` | Number of scenes |

### Devices & Entities
| Sensor | Description |
|--------|-------------|
| `sensor.ha_stats_active_integrations` | Number of active integrations |
| `sensor.ha_stats_config_entries_total` | Total number of config entries |
| `sensor.ha_stats_hacs_installed` | Number of installed HACS extensions |
| `sensor.ha_stats_entity_count` | Total number of entities |
| `sensor.ha_stats_device_count` | Number of registered devices |
| `sensor.ha_stats_person_count` | Number of configured persons |
| `sensor.ha_stats_persons_home` | Number of persons currently home |
| `sensor.ha_stats_zone_count` | Number of configured zones |

### System
| Sensor | Description |
|--------|-------------|
| `sensor.ha_stats_cpu_usage` | CPU usage in % |
| `sensor.ha_stats_cpu_cores` | Number of logical CPU cores |
| `sensor.ha_stats_cpu_frequency` | Current CPU clock frequency in MHz |
| `sensor.ha_stats_ram_used_percent` | RAM usage in % |
| `sensor.ha_stats_ram_used` | Used RAM in GB |
| `sensor.ha_stats_ram_free` | Available RAM in GB |
| `sensor.ha_stats_ram_total` | Total RAM in GB |
| `sensor.ha_stats_disk_free` | Free disk space (GB) |
| `sensor.ha_stats_disk_total` | Total disk space (GB) |
| `sensor.ha_stats_disk_used` | Used disk space (GB) |
| `sensor.ha_stats_disk_used_percent` | Disk usage in % |
| `sensor.ha_stats_system_uptime` | System uptime in hours |
| `sensor.ha_stats_last_boot` | Time of last system boot |
| `sensor.ha_stats_last_boot_duration` | Duration of last boot in seconds |

### Files & Versions
| Sensor | Description |
|--------|-------------|
| `sensor.ha_stats_ha_version` | Installed Home Assistant version |
| `sensor.ha_stats_python_version` | Python version of the HA process |
| `sensor.ha_stats_config_directory_size` | Total size of the config directory in MB |
| `sensor.ha_stats_recorder_db_size` | Size of the recorder database in MB |
| `sensor.ha_stats_log_file_size` | Size of the log file in KB |

---

## 🚀 Installation

### Via HACS (recommended)

1. Open HACS → **Integrations** → Menu (⋮) → **Add custom repository**
2. URL: `https://github.com/olli-dot-dev/ha-instance-stats`
3. Category: **Integration**
4. Click **Add**, then search for "HA Instance Stats" and install it.
5. Restart Home Assistant.

### Manual

1. Copy `custom_components/ha_instance_stats/` into your HA configuration directory under `custom_components/`
2. Restart Home Assistant.

---

## ⚙️ Setup

1. Go to **Settings** → **Devices & Services** → **Add Integration**
2. Search for **HA Instance Stats**
3. Set the update interval (default: 5 minutes)

The Lovelace card is **automatically registered** — no manual resource configuration needed.

---

## 🃏 Using the Card

Add the card to your dashboard via the UI editor or YAML:

```yaml
type: custom:ha-instance-stats-card
title: My HA Instance  # Optional, default: "Home Assistant Statistics"
```

---

## 🔧 Configuration Options

The integration can be adjusted after setup via **Settings** → **Devices & Services** → **HA Instance Stats** → **Configure**:

| Option | Default | Description |
|--------|---------|-------------|
| `update_interval` | 5 | Update interval in minutes (1–60) |

---

## 📋 Requirements

- Home Assistant 2023.1.0 or newer
- HACS (for easy installation)
- Linux-based system (systemd required for boot duration sensor)
- `psutil` – installed automatically by HA via `requirements` in `manifest.json`

---

## 🐛 Known Limitations

- **Boot duration**: Requires `systemd-analyze` on the host. Works with HA OS and HA Supervised. Returns `null` on Docker installations.
- **Device count**: Uses the `device_registry` API — may vary between HA versions.

---

## 📝 License

MIT License – free to use, modify, and distribute.
