# HA Instance Stats

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Eine HACS-Erweiterung für Home Assistant, die dir detaillierte Statistiken zu deiner eigenen Instanz bereitstellt – direkt als Sensoren und als elegante Lovelace-Karte.

---

## 📊 Verfügbare Statistiken

### Konfiguration
| Sensor | Beschreibung |
|--------|-------------|
| `sensor.ha_stats_automation_count` | Anzahl der Automationen |
| `sensor.ha_stats_automations_yaml_size` | Größe der `automations.yaml` in KB |
| `sensor.ha_stats_unavailable_automations` | Anzahl fehlgeschlagener/unavailable Automationen |
| `sensor.ha_stats_blueprint_count` | Anzahl installierter Blueprints |
| `sensor.ha_stats_script_count` | Anzahl der Skripte |
| `sensor.ha_stats_scene_count` | Anzahl der Szenen |

### Geräte & Entities
| Sensor | Beschreibung |
|--------|-------------|
| `sensor.ha_stats_active_integrations` | Anzahl aktiver Integrationen |
| `sensor.ha_stats_config_entries_total` | Gesamtanzahl Config Entries |
| `sensor.ha_stats_hacs_installed` | Anzahl installierter HACS-Erweiterungen |
| `sensor.ha_stats_entity_count` | Gesamtanzahl aller Entities |
| `sensor.ha_stats_device_count` | Anzahl registrierter Geräte |
| `sensor.ha_stats_person_count` | Anzahl konfigurierter Personen |
| `sensor.ha_stats_persons_home` | Anzahl der aktuell zuhause befindlichen Personen |
| `sensor.ha_stats_zone_count` | Anzahl konfigurierter Zonen |

### System
| Sensor | Beschreibung |
|--------|-------------|
| `sensor.ha_stats_cpu_usage` | CPU-Auslastung in % |
| `sensor.ha_stats_cpu_cores` | Anzahl logischer CPU-Kerne |
| `sensor.ha_stats_cpu_frequency` | Aktuelle CPU-Taktfrequenz in MHz |
| `sensor.ha_stats_ram_used_percent` | RAM-Auslastung in % |
| `sensor.ha_stats_ram_used` | Belegter RAM in GB |
| `sensor.ha_stats_ram_free` | Verfügbarer RAM in GB |
| `sensor.ha_stats_ram_total` | Gesamter RAM in GB |
| `sensor.ha_stats_disk_free` | Freier Festplattenspeicher (GB) |
| `sensor.ha_stats_disk_total` | Gesamter Festplattenspeicher (GB) |
| `sensor.ha_stats_disk_used` | Belegter Festplattenspeicher (GB) |
| `sensor.ha_stats_disk_used_percent` | Festplattenauslastung in % |
| `sensor.ha_stats_system_uptime` | Systemlaufzeit in Stunden |
| `sensor.ha_stats_last_boot` | Zeitpunkt des letzten Systemstarts |
| `sensor.ha_stats_last_boot_duration` | Dauer des letzten Bootvorgangs in Sekunden |

### Dateien & Versionen
| Sensor | Beschreibung |
|--------|-------------|
| `sensor.ha_stats_ha_version` | Installierte Home Assistant Version |
| `sensor.ha_stats_python_version` | Python-Version des HA-Prozesses |
| `sensor.ha_stats_config_directory_size` | Gesamtgröße des Config-Verzeichnisses in MB |
| `sensor.ha_stats_recorder_db_size` | Größe der Recorder-Datenbank (home-assistant_v2.db) in MB |
| `sensor.ha_stats_log_file_size` | Größe der Log-Datei in KB |

---

## 🚀 Installation

### Option A: Via HACS (empfohlen)

1. Öffne HACS → **Integrationen** → Menü (⋮) → **Benutzerdefiniertes Repository hinzufügen**
2. URL: `https://github.com/yourusername/ha-instance-stats`
3. Kategorie: **Integration**
4. Klicke **Hinzufügen**, dann suche nach "HA Instance Stats" und installiere es.

Für die Lovelace-Karte:
1. HACS → **Frontend** → **Benutzerdefiniertes Repository hinzufügen**
2. URL: `https://github.com/yourusername/ha-instance-stats`
3. Kategorie: **Lovelace**
4. Installiere "HA Instance Stats Card"

### Option B: Manuell

1. Kopiere `custom_components/ha_instance_stats/` in deinen HA-Konfigurationsordner unter `custom_components/`
2. Kopiere `www/ha-instance-stats-card/ha-instance-stats-card.js` in `www/ha-instance-stats-card/`
3. Starte Home Assistant neu

---

## ⚙️ Einrichtung

### Integration einrichten

1. Gehe zu **Einstellungen** → **Geräte & Dienste** → **Integration hinzufügen**
2. Suche nach **HA Instance Stats**
3. Stelle das Aktualisierungsintervall ein (Standard: 5 Minuten)

### Lovelace-Karte registrieren

Füge folgendes zu deiner `configuration.yaml` hinzu:

```yaml
lovelace:
  resources:
    - url: /local/ha-instance-stats-card/ha-instance-stats-card.js
      type: module
```

Oder über die UI: **Einstellungen** → **Dashboards** → Menü → **Ressourcen** → Hinzufügen:
- URL: `/local/ha-instance-stats-card/ha-instance-stats-card.js`
- Typ: JavaScript-Modul

---

## 🃏 Karte verwenden

Füge die Karte zu deinem Dashboard hinzu (über den UI-Editor oder YAML):

```yaml
type: custom:ha-instance-stats-card
title: Meine HA Instanz  # Optional, Standard: "Home Assistant Statistiken"
```

---

## 🔧 Konfigurationsoptionen

Die Integration kann nach der Einrichtung über **Einstellungen** → **Geräte & Dienste** → **HA Instance Stats** → **Konfigurieren** angepasst werden:

| Option | Standard | Beschreibung |
|--------|----------|-------------|
| `update_interval` | 5 | Aktualisierungsintervall in Minuten (1–60) |

---

## 📋 Voraussetzungen

- Home Assistant 2023.1.0 oder neuer
- HACS (für einfache Installation)
- Linux-basiertes System (für Boot-Dauer benötigt systemd)
- `psutil` – wird automatisch von HA installiert (via `requirements` in `manifest.json`)

---

## 🐛 Bekannte Einschränkungen

- **Boot-Dauer**: Erfordert `systemd-analyze` auf dem Host-System. Funktioniert bei HA OS und HA Supervised. Bei Docker-Installationen wird `null` zurückgegeben.
- **Gerätezählung**: Erfordert die `device_registry`-API von Home Assistant.

---

## 📝 Lizenz

MIT License – freie Verwendung, Modifikation und Weitergabe.
