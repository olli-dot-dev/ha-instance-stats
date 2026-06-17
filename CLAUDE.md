# CLAUDE.md – Projektkontext für Claude Code

Dieses Dokument beschreibt Architektur, Konventionen und offene Aufgaben des Projekts **HA Instance Stats** – einer HACS-Erweiterung für Home Assistant.

---

## Projektübersicht

**Ziel:** Eine HACS-Erweiterung, die Statistiken zur eigenen Home Assistant-Instanz als Sensoren bereitstellt und in einer Lovelace-Karte anzeigt.

**Aktueller Stand:** v2.0.0 – voll funktionsfähige Basis, noch nicht auf GitHub veröffentlicht.

---

## Verzeichnisstruktur

```
ha-instance-stats/
├── CLAUDE.md                          ← diese Datei
├── hacs.json                          ← HACS-Metadaten
├── README.md                          ← Nutzerdokumentation
│
├── custom_components/ha_instance_stats/
│   ├── __init__.py                    ← Setup & Entry-Lifecycle
│   ├── manifest.json                  ← HA-Manifest (Version, Abhängigkeiten)
│   ├── const.py                       ← Alle Konstanten (DOMAIN, Sensor-Keys, etc.)
│   ├── coordinator.py                 ← DataUpdateCoordinator: sammelt alle Rohdaten
│   ├── sensor.py                      ← Sensor-Entities + SENSOR_DESCRIPTIONS Liste
│   ├── config_flow.py                 ← UI-Setup-Assistent + Options Flow
│   ├── strings.json                   ← UI-Strings (Basis)
│   └── translations/
│       ├── de.json                    ← Deutsche Übersetzungen
│       └── en.json                    ← Englische Übersetzungen
│
└── www/ha-instance-stats-card/
    └── ha-instance-stats-card.js      ← Lovelace Custom Card (Vanilla JS, kein Build)
```

---

## Architektur

### Datenfluss

```
Home Assistant Core
       │
       ▼
HAInstanceStatsCoordinator (coordinator.py)
  • Läuft alle 5 Minuten (SCAN_INTERVAL)
  • _fetch_all_stats() läuft im Executor (blockierender I/O erlaubt)
  • Gibt ein flaches dict zurück: { "automation_count": 42, "ram_used_percent": 61.3, ... }
       │
       ▼
HAInstanceStatsSensor (sensor.py) — eine Instanz pro SENSOR_DESCRIPTIONS-Eintrag
  • Liest aus coordinator.data[data_key]
  • Timestamp-Sensoren: parsen ISO-String → datetime-Objekt
  • Extra-Attribute: z.B. fehlgeschlagene Automation-IDs, HACS-Kategorien
       │
       ▼
Lovelace Card (ha-instance-stats-card.js)
  • Liest hass.states["sensor.ha_stats_..."].state
  • Kein Build-Schritt – reines Vanilla JS, läuft direkt im Browser
  • Gruppiert in: Konfiguration / Geräte & Entities / System / Dateien & Versionen
```

### Einen neuen Sensor hinzufügen – Checkliste

1. **`coordinator.py`** – Daten in `_fetch_all_stats()` unter einem neuen Key ins `data`-Dict schreiben
2. **`sensor.py`** – neuen `HAStatsSensorDescription`-Eintrag in `SENSOR_DESCRIPTIONS` hinzufügen
3. **`ha-instance-stats-card.js`** – Eintrag in `STAT_GROUPS` in der passenden Gruppe ergänzen
4. **`const.py`** – optional: Sensor-Key als Konstante eintragen
5. **`translations/de.json` + `en.json`** – falls neue UI-Strings nötig sind

---

## Wichtige Konventionen

### Python (Backend)
- Jeder Datenabruf in `_fetch_all_stats()` ist in einem eigenen `try/except`-Block – ein Fehler darf nie den gesamten Update-Zyklus abbrechen
- Fehlende Werte werden als `None` zurückgegeben (nicht als 0 oder leerer String)
- `psutil` ist als Requirement in `manifest.json` eingetragen – HA installiert es automatisch
- Die Boot-Dauer wird via `systemd-analyze` ermittelt – auf Docker-Instanzen liefert das `None`
- HACS-Daten werden aus `.storage/hacs.repositories` gelesen – falls die Datei nicht existiert, wird `None` zurückgegeben (HACS nicht installiert)

### JavaScript (Frontend)
- **Kein Build-Schritt** – die Datei muss direkt im Browser laufen (kein TypeScript, kein npm)
- Externe Abhängigkeiten: keine – MDI-Icons werden als inline SVG-Pfade eingebettet (`MDI_PATHS`-Objekt)
- Entity-IDs folgen dem Muster: `sensor.ha_stats_<beschreibung>` (HA normalisiert den Namen aus `_attr_name`)
- `isBar: true` → zeigt einen Fortschrittsbalken unter dem Wert (Farbe: grün/orange/rot je nach Schwellwert)
- `isAlert: true` → hebt die Kachel rot hervor wenn Wert > 0
- `isTimestamp: true` → formatiert den Wert als deutsches Datum/Uhrzeit

### Versionierung
- Backend + Frontend haben dieselbe Versionsnummer
- Version in: `manifest.json` → `version`, `ha-instance-stats-card.js` → `CARD_VERSION`

---

## Bekannte Einschränkungen & TODOs

### Offene Punkte
- [ ] **Tests fehlen** – noch keine `pytest`-Tests vorhanden; Priorität: `coordinator.py` testen
- [ ] **GitHub Actions** – kein CI/CD-Workflow, kein HACS-Validation-Workflow
- [ ] **GitHub-Repository** noch nicht erstellt
- [ ] **Releases** – kein `release.yaml`-Workflow für automatische HACS-Releases
- [ ] **Entity-ID-Mapping** – die Entity-IDs in der JS-Karte sind hartcodiert; bei Namensänderungen müssen beide Seiten synchron angepasst werden

### Bekannte Einschränkungen
- Boot-Dauer (`systemd-analyze`) funktioniert nur auf HA OS und HA Supervised, nicht auf Docker
- HACS-Zählung liest direkt eine interne Storage-Datei – könnte bei HACS-Updates brechen
- RAM/CPU via `psutil` – auf einigen ARM-Systemen (z.B. Raspberry Pi mit HA OS) kann `cpu_freq()` `None` zurückgeben
- Gerätezählung nutzt `device_registry` – API-Pfad kann sich zwischen HA-Versionen unterscheiden

---

## Entwicklungsumgebung

### Empfohlener Testaufbau
```bash
# HA-Testinstanz mit Docker starten
docker run -d \
  --name homeassistant \
  -v ./config:/config \
  -p 8123:8123 \
  ghcr.io/home-assistant/home-assistant:stable

# custom_components ins Config-Verzeichnis kopieren
cp -r custom_components/ha_instance_stats ./config/custom_components/

# www-Ordner kopieren
cp -r www/ha-instance-stats-card ./config/www/
```

### HACS-Validierung lokal
```bash
# hacs-action validator (benötigt Python)
pip install hacs-action
hacs-action validate
```

### Auf echtem HA testen
1. Dateien per SSH oder Samba in `/config/custom_components/ha_instance_stats/` kopieren
2. HA neu starten
3. Integration unter Einstellungen → Geräte & Dienste hinzufügen

---

## Nächste sinnvolle Schritte (Vorschläge)

1. **GitHub-Repo erstellen** und `git init` + erster Commit
2. **HACS-Validation-Workflow** einrichten (`.github/workflows/validate.yaml`)
3. **pytest-Tests** für `coordinator.py` schreiben (mock `hass`, mock Dateisystem)
4. **Release-Workflow** für automatische HACS-Releases via GitHub Releases
5. **Konfigurierbarer Scan-Intervall** – derzeit in `const.py` fix auf 5 Min, sollte aus `config_flow` kommen
