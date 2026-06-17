/**
 * ha-instance-stats-card
 * A Lovelace card displaying Home Assistant instance statistics.
 * Version: 2.0.0
 */

const CARD_VERSION = "2.0.0";

// Groups with their stats — renders section headers between groups
const STAT_GROUPS = [
  {
    label: "Configuration",
    stats: [
      { key: "automations",       entity: "sensor.ha_stats_automation_count",        label: "Automations",          icon: "mdi:robot",            unit: "",   color: "#4FC3F7" },
      { key: "automations_yaml",  entity: "sensor.ha_stats_automations_yaml_size",    label: "automations.yaml",     icon: "mdi:file-code",        unit: "KB", color: "#81C784" },
      { key: "automation_failed", entity: "sensor.ha_stats_unavailable_automations",  label: "Failed Automations",   icon: "mdi:robot-dead",       unit: "",   color: "#EF9A9A", isAlert: true },
      { key: "blueprints",        entity: "sensor.ha_stats_blueprint_count",          label: "Blueprints",           icon: "mdi:source-branch",    unit: "",   color: "#B39DDB" },
      { key: "scripts",           entity: "sensor.ha_stats_script_count",             label: "Scripts",              icon: "mdi:script-text",      unit: "",   color: "#80CBC4" },
      { key: "scenes",            entity: "sensor.ha_stats_scene_count",              label: "Scenes",               icon: "mdi:palette",          unit: "",   color: "#FFCC80" },
    ],
  },
  {
    label: "Devices & Entities",
    stats: [
      { key: "integrations",  entity: "sensor.ha_stats_active_integrations", label: "Active Integrations",  icon: "mdi:puzzle",           unit: "", color: "#FFB74D" },
      { key: "hacs",          entity: "sensor.ha_stats_hacs_installed",      label: "HACS Extensions",      icon: "mdi:store",            unit: "", color: "#FF8A65" },
      { key: "entities",      entity: "sensor.ha_stats_entity_count",        label: "Entities",             icon: "mdi:counter",          unit: "", color: "#CE93D8" },
      { key: "devices",       entity: "sensor.ha_stats_device_count",        label: "Devices",              icon: "mdi:devices",          unit: "", color: "#F48FB1" },
      { key: "persons",       entity: "sensor.ha_stats_person_count",        label: "Persons",              icon: "mdi:account-group",    unit: "", color: "#80CBC4" },
      { key: "persons_home",  entity: "sensor.ha_stats_persons_home",        label: "Persons Home",         icon: "mdi:account-check",    unit: "", color: "#A5D6A7" },
      { key: "zones",         entity: "sensor.ha_stats_zone_count",          label: "Zones",                icon: "mdi:map-marker-radius", unit: "", color: "#FFF59D" },
    ],
  },
  {
    label: "System",
    stats: [
      { key: "cpu_used",    entity: "sensor.ha_stats_cpu_usage",          label: "CPU Usage",      icon: "mdi:cpu-64-bit",    unit: "%",  color: "#EF9A9A", isBar: true },
      { key: "cpu_freq",    entity: "sensor.ha_stats_cpu_frequency",      label: "CPU Clock",      icon: "mdi:speedometer",   unit: "MHz",color: "#FFCC80" },
      { key: "ram_used",    entity: "sensor.ha_stats_ram_used_percent",   label: "RAM Usage",      icon: "mdi:memory",        unit: "%",  color: "#CE93D8", isBar: true },
      { key: "ram_free",    entity: "sensor.ha_stats_ram_free",           label: "RAM Free",       icon: "mdi:memory",        unit: "GB", color: "#B39DDB" },
      { key: "disk_free",   entity: "sensor.ha_stats_disk_free",          label: "Disk Free",      icon: "mdi:harddisk",      unit: "GB", color: "#80DEEA" },
      { key: "disk_pct",    entity: "sensor.ha_stats_disk_used_percent",  label: "Disk Usage",     icon: "mdi:chart-donut",   unit: "%",  color: "#EF9A9A", isBar: true },
      { key: "uptime",      entity: "sensor.ha_stats_system_uptime",      label: "Uptime",         icon: "mdi:timer-outline", unit: "h",  color: "#A5D6A7" },
      { key: "last_boot",   entity: "sensor.ha_stats_last_boot",          label: "Last Boot",      icon: "mdi:restart",       unit: "",   color: "#BCAAA4", isTimestamp: true },
      { key: "boot_dur",    entity: "sensor.ha_stats_last_boot_duration", label: "Boot Duration",  icon: "mdi:timer-play",    unit: "s",  color: "#FFF59D" },
    ],
  },
  {
    label: "Files & Versions",
    stats: [
      { key: "ha_version",   entity: "sensor.ha_stats_ha_version",           label: "HA Version",        icon: "mdi:home-assistant",     unit: "",  color: "#90CAF9" },
      { key: "py_version",   entity: "sensor.ha_stats_python_version",        label: "Python Version",    icon: "mdi:language-python",    unit: "",  color: "#FFD54F" },
      { key: "config_size",  entity: "sensor.ha_stats_config_directory_size", label: "Config Directory",  icon: "mdi:folder-information", unit: "MB",color: "#BCAAA4" },
      { key: "db_size",      entity: "sensor.ha_stats_recorder_db_size",      label: "Recorder DB",       icon: "mdi:database",           unit: "MB",color: "#80CBC4" },
      { key: "log_size",     entity: "sensor.ha_stats_log_file_size",         label: "Log File",          icon: "mdi:text-box-outline",   unit: "KB",color: "#B0BEC5" },
    ],
  },
];

// --- MDI SVG paths ---
const MDI_PATHS = {
  "mdi:robot":            "M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7H3a7 7 0 0 1 7-7h1V5.73A2 2 0 0 1 10 4a2 2 0 0 1 2-2M7.5 13a.5.5 0 0 0-.5.5v1a.5.5 0 0 0 .5.5h1a.5.5 0 0 0 .5-.5v-1a.5.5 0 0 0-.5-.5h-1m7 0a.5.5 0 0 0-.5.5v1a.5.5 0 0 0 .5.5h1a.5.5 0 0 0 .5-.5v-1a.5.5 0 0 0-.5-.5h-1M3 19a4 4 0 0 0 4 4h10a4 4 0 0 0 4-4v-1H3v1z",
  "mdi:robot-dead":       "M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7H3a7 7 0 0 1 7-7h1V5.73A2 2 0 0 1 10 4a2 2 0 0 1 2-2M8 13l1.5 1.5L11 13l1.5 1.5L14 13l-1.5 1.5L14 16l-1.5-1.5L11 16l-1.5-1.5L8 16l1.5-1.5L8 13M3 19a4 4 0 0 0 4 4h10a4 4 0 0 0 4-4v-1H3v1z",
  "mdi:file-code":        "M14 2H6a2 2 0 0 0-2 2v16c0 1.11.89 2 2 2h12a2 2 0 0 0 2-2V8L14 2m-1 1.5L18.5 9H13V3.5M10.08 14.07l-1.49-1.5 1.49-1.5L9 9.93 6 13l3 3 1.08-1.93m3.84 1.86L17 13l-3-3-1.08 1.07 1.49 1.5-1.49 1.5L14 15.93z",
  "mdi:source-branch":    "M13 14c-3.36.88-4 2.78-4 4H7c0-2.42 1.72-4.44 4-4.9V11c-2.28-.46-4-2.48-4-4.9 0-2.76 2.24-5 5-5s5 2.24 5 5c0 2.42-1.72 4.44-4 4.9V14m-1-11a3 3 0 0 0-3 3 3 3 0 0 0 3 3 3 3 0 0 0 3-3 3 3 0 0 0-3-3z",
  "mdi:puzzle":           "M20.5 11H19V7a2 2 0 0 0-2-2h-4V3.5A2.5 2.5 0 0 0 10.5 1A2.5 2.5 0 0 0 8 3.5V5H4a2 2 0 0 0-2 2v3.8h1.5c1.5 0 2.7 1.2 2.7 2.7S5 16.2 3.5 16.2H2V20a2 2 0 0 0 2 2h3.8v-1.5c0-1.5 1.2-2.7 2.7-2.7 1.5 0 2.7 1.2 2.7 2.7V22H17a2 2 0 0 0 2-2v-4h1.5A2.5 2.5 0 0 0 23 13.5 2.5 2.5 0 0 0 20.5 11z",
  "mdi:store":            "M12 18H6v-4h6m9-4V8l-3-4H5a2 2 0 0 0-2 2v11a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2m-1.5-9H5.5v-.5L7 4h10l1.5 2V5z",
  "mdi:counter":          "M4 4h4v4H4V4m6 0h4v4h-4V4m6 0h4v4h-4V4M4 10h4v4H4v-4m6 0h4v4h-4v-4m6 0h4v4h-4v-4M4 16h4v4H4v-4m6 0h4v4h-4v-4m6 0h4v4h-4v-4z",
  "mdi:devices":          "M3 6h18v2H3V6m0 4h18v2H3v-2m0 4h18v2H3v-2z",
  "mdi:account-group":    "M12 5.5A3.5 3.5 0 0 1 15.5 9a3.5 3.5 0 0 1-3.5 3.5A3.5 3.5 0 0 1 8.5 9 3.5 3.5 0 0 1 12 5.5M5 8c.56 0 1.08.15 1.53.42-.15 1.43.27 2.85 1.13 3.96C7.16 13.34 6.16 14 5 14a3 3 0 0 1-3-3 3 3 0 0 1 3-3m14 0a3 3 0 0 1 3 3 3 3 0 0 1-3 3c-1.16 0-2.16-.66-2.66-1.62a5.536 5.536 0 0 0 1.13-3.96A3.07 3.07 0 0 1 19 8M5.5 18.25c0-2.07 2.91-3.75 6.5-3.75s6.5 1.68 6.5 3.75V20h-13v-1.75M0 20v-1.5c0-1.39 1.89-2.56 4.45-2.9A5.4 5.4 0 0 0 3.5 18.25V20H0m24 0h-3.5v-1.75a5.4 5.4 0 0 0-.97-3.15C22.11 15.44 24 16.61 24 18v1.5V20z",
  "mdi:account-check":    "M21.1 12.5l1.4 1.41-6.53 6.59L13.5 17l1.4-1.41 2.07 2.08 5.13-5.17M10 17l3 3H3v-2c0-2.21 3.58-4 8-4l1.89.05L10 17m1-13a4 4 0 0 1 4 4 4 4 0 0 1-4 4 4 4 0 0 1-4-4 4 4 0 0 1 4-4z",
  "mdi:map-marker-radius":"M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z",
  "mdi:script-text":      "M14 17H7v-2h7v2m3-4H7v-2h10v2m0-4H7V7h10v2M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2z",
  "mdi:palette":          "M12 3c-4.97 0-9 4.03-9 9s4.03 9 9 9c.83 0 1.5-.67 1.5-1.5 0-.39-.15-.74-.39-1.01-.23-.26-.38-.61-.38-.99 0-.83.67-1.5 1.5-1.5H16c2.76 0 5-2.24 5-5 0-4.42-4.03-8-9-8zm-5.5 9c-.83 0-1.5-.67-1.5-1.5S5.67 9 6.5 9 8 9.67 8 10.5 7.33 12 6.5 12zm3-4C8.67 8 8 7.33 8 6.5S8.67 5 9.5 5s1.5.67 1.5 1.5S10.33 8 9.5 8zm5 0c-.83 0-1.5-.67-1.5-1.5S13.67 5 14.5 5s1.5.67 1.5 1.5S15.33 8 14.5 8zm3 4c-.83 0-1.5-.67-1.5-1.5S16.67 9 17.5 9s1.5.67 1.5 1.5-.67 1.5-1.5 1.5z",
  "mdi:cpu-64-bit":       "M9 3H7v2H5v2H3v2h2v2H3v2h2v2H3v2h2v2h2v2h2v-2h2v2h2v-2h2v2h2v-2h2v-2h2v-2h-2v-2h2v-2h-2V9h2V7h-2V5h-2V3h-2v2h-2V3h-2v2H9V3m0 4h6v6H9V7m2 2v2h2V9h-2z",
  "mdi:speedometer":      "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2M7.07 18.28c.43-.9 3.05-1.78 4.93-1.78s4.5.88 4.93 1.78C15.57 19.36 13.86 20 12 20s-3.57-.64-4.93-1.72m11.29-1.45c-1.43-1.74-4.9-2.33-6.36-2.33s-4.93.59-6.36 2.33A7.95 7.95 0 0 1 4 12c0-4.41 3.59-8 8-8s8 3.59 8 8c0 1.82-.62 3.5-1.64 4.83M12 6c-1.94 0-3.5 1.56-3.5 3.5S10.06 13 12 13s3.5-1.56 3.5-3.5S13.94 6 12 6m0 5c-.83 0-1.5-.67-1.5-1.5S11.17 8 12 8s1.5.67 1.5 1.5S12.83 11 12 11z",
  "mdi:memory":           "M17 17H7V7h10m0-4H7C5.9 3 5 3.9 5 5v14c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2m-4 14h-2v-2h2v2m0-4h-2V7h2v6z",
  "mdi:harddisk":         "M6 2h12a2 2 0 0 1 2 2v16a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2m0 14v4h12v-4H6m10 1h2v2h-2v-2M6 4v8h12V4H6m2 1h8l2 6H6L8 5z",
  "mdi:chart-donut":      "M13 2.05V4.08c1.96.28 3.7 1.13 5.07 2.41L16.64 7.92c-1-.85-2.23-1.44-3.64-1.69V2.05M11 2.05C5.95 2.56 2 6.82 2 12a10 10 0 0 0 10 10c1.1 0 2.17-.18 3.18-.5l-.55-1.93C13.82 19.83 12.93 20 12 20A8 8 0 0 1 4 12c0-4.07 3.06-7.44 7-7.93V2.05M18.93 13c-.28 1.96-1.13 3.7-2.41 5.07l1.42 1.41A9.94 9.94 0 0 0 20.95 13h-2.02M19.94 11c-.28-2.06-1.19-3.91-2.55-5.34l-1.41 1.41c1 1.09 1.7 2.47 1.92 3.93h2.04M12 10a2 2 0 0 0-2 2 2 2 0 0 0 2 2 2 2 0 0 0 2-2 2 2 0 0 0-2-2z",
  "mdi:timer-outline":    "M12 20a8 8 0 0 0 8-8 8 8 0 0 0-8-8 8 8 0 0 0-8 8 8 8 0 0 0 8 8m0-18a10 10 0 0 1 10 10 10 10 0 0 1-10 10A10 10 0 0 1 2 12 10 10 0 0 1 12 2m.5 5v5.25l4.5 2.67-.75 1.23L11 13V7h1.5z",
  "mdi:restart":          "M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z",
  "mdi:timer-play":       "M13 2.05V4.08c1.96.28 3.7 1.13 5.07 2.41L16.64 7.92c-1-.85-2.23-1.44-3.64-1.69V2.05M11 2.05C5.95 2.56 2 6.82 2 12c0 5.52 4.47 10 9.99 10A10 10 0 0 0 22 12c0-5.18-3.95-9.44-9-9.95M11 20C6.47 20 2.76 16.22 4.05 11.53 4.78 8.77 7 6.62 9.78 5.97V4.05C5.4 4.59 2 7.97 2 12a9 9 0 0 0 9 9v-1m7.93-8C18.72 9.3 16.83 7.4 14.5 6.61V12l4.43 4.43c.59-.79 1.02-1.69 1.25-2.68l-1.25-.75M10 8v9l6-4.5-6-4.5z",
  "mdi:home-assistant":   "M21 9.5v11a.5.5 0 0 1-.5.5H16v-5h-2v5H3.5a.5.5 0 0 1-.5-.5V9.5a.5.5 0 0 1 .16-.36l8.5-7.71a.5.5 0 0 1 .68 0l8.5 7.71A.5.5 0 0 1 21 9.5M9 11.5v2h6v-2H9z",
  "mdi:language-python":  "M19.14 7.5A2.86 2.86 0 0 1 22 10.36v3.78A2.86 2.86 0 0 1 19.14 17H12c0 .39.32.64.71.64H17v1.79A2.86 2.86 0 0 1 14.14 22H9.86A2.86 2.86 0 0 1 7 19.14v-3.78A2.86 2.86 0 0 1 9.86 12.5H17c-.39 0-.71-.25-.71-.64V10.5h-2.29v.64c0 .39-.32.64-.71.64H9.86C9.46 11.78 9 11.4 9 11v-.64H4.86A2.86 2.86 0 0 0 2 13.14v3.79A2.86 2.86 0 0 0 4.86 19.72H7v-1.79c0-.39.32-.64.71-.64h3.79c.39 0 .71.25.71.64V19.14A2.86 2.86 0 0 0 14.14 22H9.86A2.86 2.86 0 0 1 7 19.14v-1.43H4.86A4.29 4.29 0 0 1 .57 13.43v-3.57A4.29 4.29 0 0 1 4.86 5.57H7V4.86A2.86 2.86 0 0 1 9.86 2h4.28A2.86 2.86 0 0 1 17 4.86V6.5h2.14M9.86 4.29c-.39 0-.71.32-.71.71v.5h5.71v-.5c0-.39-.32-.71-.71-.71H9.86m0 14.63c.39 0 .71-.32.71-.71v-.5H4.86v.5c0 .39.32.71.71.71h4.29z",
  "mdi:folder-information":"M13 9h1.5v3H16v1.5h-3V9M13 5v1.5h5v11H6V5h7M11 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-5-5h-4m-1 6h3v.5H10V9m1 3H9v-.5h2V12m-1 2h3v.5h-3V14z",
  "mdi:database":         "M12 3C7.58 3 4 4.79 4 7v10c0 2.21 3.59 4 8 4s8-1.79 8-4V7c0-2.21-3.58-4-8-4m0 2c3.87 0 6 1.5 6 2s-2.13 2-6 2-6-1.5-6-2 2.13-2 6-2m6 12c0 .5-2.13 2-6 2s-6-1.5-6-2v-2.23c1.61.78 3.72 1.23 6 1.23s4.39-.45 6-1.23V17m0-4.5c0 .5-2.13 2-6 2s-6-1.5-6-2v-2.23C7.61 11.05 9.72 11.5 12 11.5s4.39-.45 6-1.23V12.5z",
  "mdi:text-box-outline": "M5 3c-1.11 0-2 .89-2 2v14c0 1.11.89 2 2 2h14c1.11 0 2-.89 2-2V5c0-1.11-.89-2-2-2H5m0 2h14v14H5V5m2 3v2h10V8H7m0 4v2h10v-2H7m0 4v2h7v-2H7z",
};

function renderIcon(iconKey, color) {
  const path = MDI_PATHS[iconKey] || MDI_PATHS["mdi:home-assistant"];
  return `<svg viewBox="0 0 24 24" width="20" height="20" style="fill:${color};flex-shrink:0"><path d="${path}"/></svg>`;
}

function formatTimestamp(isoString) {
  if (!isoString || isoString === "unavailable" || isoString === "unknown") return "—";
  try {
    const d = new Date(isoString);
    return d.toLocaleString(undefined, { day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit" });
  } catch { return isoString; }
}

function formatValue(stat, state) {
  if (!state || state === "unavailable" || state === "unknown") return "—";
  if (stat.isTimestamp) return formatTimestamp(state);
  const num = parseFloat(state);
  if (!isNaN(num)) return num % 1 === 0 ? num.toString() : num.toFixed(1);
  return state;
}

class HAInstanceStatsCard extends HTMLElement {
  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  setConfig(config) {
    this._config = config || {};
  }

  getCardSize() { return 10; }

  _renderGroup(group) {
    const items = group.stats.map((stat) => {
      const stateObj = this._hass.states[stat.entity];
      const rawState = stateObj ? stateObj.state : null;
      const displayValue = formatValue(stat, rawState);
      const unavailable = !rawState || rawState === "unavailable" || rawState === "unknown";
      const isAlertActive = stat.isAlert && !unavailable && parseFloat(rawState) > 0;

      let extraHtml = "";
      if (stat.isBar && !unavailable) {
        const pct = Math.min(100, Math.max(0, parseFloat(rawState) || 0));
        const barColor = pct > 85 ? "#EF5350" : pct > 60 ? "#FFB74D" : "#81C784";
        extraHtml = `<div class="bar-track"><div class="bar-fill" style="width:${pct}%;background:${barColor}"></div></div>`;
      }

      const itemColor = unavailable ? "var(--secondary-text-color, #757575)" : (isAlertActive ? "#EF5350" : stat.color);
      const itemBorder = isAlertActive ? "border:1px solid rgba(239,83,80,0.4);background:rgba(239,83,80,0.07);" : "";

      return `
        <div class="stat-item${unavailable ? " unavailable" : ""}" style="${itemBorder}">
          <div class="stat-icon">${renderIcon(stat.icon, itemColor)}</div>
          <div class="stat-content">
            <div class="stat-label">${stat.label}</div>
            <div class="stat-value" style="color:${itemColor}">
              ${displayValue}${stat.unit && !unavailable && !stat.isTimestamp ? `<span class="stat-unit">${stat.unit}</span>` : ""}
            </div>
            ${extraHtml}
          </div>
        </div>`;
    }).join("");

    return `
      <div class="group">
        <div class="group-label">${group.label}</div>
        <div class="stats-grid">${items}</div>
      </div>`;
  }

  _render() {
    if (!this._hass) return;
    if (!this.shadowRoot) this.attachShadow({ mode: "open" });

    const title = this._config?.title || "Home Assistant Statistics";
    const groups = STAT_GROUPS.map((g) => this._renderGroup(g)).join("");

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; font-family: var(--primary-font-family, 'Roboto', sans-serif); }
        .card {
          background: var(--ha-card-background, var(--card-background-color, #fff));
          border-radius: 16px;
          padding: 20px;
          box-shadow: var(--ha-card-box-shadow, 0 2px 8px rgba(0,0,0,0.1));
          border: 1px solid var(--ha-card-border-color, var(--divider-color, #e0e0e0));
        }
        .card-header {
          display: flex; align-items: center; gap: 10px;
          margin-bottom: 18px; padding-bottom: 14px;
          border-bottom: 1px solid var(--divider-color, rgba(0,0,0,0.12));
        }
        .card-title { font-size: 1.05rem; font-weight: 600; color: var(--primary-text-color, #212121); letter-spacing: 0.02em; }
        .card-subtitle { font-size: 0.7rem; color: var(--secondary-text-color, #757575); margin-top: 2px; }
        .group { margin-bottom: 18px; }
        .group:last-child { margin-bottom: 0; }
        .group-label {
          font-size: 0.65rem; font-weight: 600; letter-spacing: 0.1em;
          text-transform: uppercase; color: var(--secondary-text-color, #757575);
          margin-bottom: 8px; padding-left: 2px;
        }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(185px, 1fr)); gap: 8px; }
        .stat-item {
          background: var(--secondary-background-color, rgba(0,0,0,0.04));
          border-radius: 10px; padding: 11px 13px;
          display: flex; align-items: flex-start; gap: 10px;
          border: 1px solid var(--divider-color, rgba(0,0,0,0.08));
          transition: background 0.15s;
        }
        .stat-item:hover { background: var(--primary-background-color, rgba(0,0,0,0.08)); }
        .stat-item.unavailable { opacity: 0.4; }
        .stat-icon { margin-top: 2px; }
        .stat-content { flex: 1; min-width: 0; }
        .stat-label {
          font-size: 0.68rem; color: var(--secondary-text-color, #757575);
          text-transform: uppercase; letter-spacing: 0.05em;
          margin-bottom: 3px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        }
        .stat-value { font-size: 1.15rem; font-weight: 700; letter-spacing: -0.01em; line-height: 1.2; }
        .stat-unit { font-size: 0.62rem; font-weight: 400; margin-left: 2px; opacity: 0.7; vertical-align: middle; }
        .bar-track { margin-top: 6px; height: 3px; border-radius: 2px; background: var(--divider-color, rgba(0,0,0,0.1)); overflow: hidden; }
        .bar-fill { height: 100%; border-radius: 2px; transition: width 0.5s ease; }
        .footer {
          margin-top: 14px; padding-top: 10px;
          border-top: 1px solid var(--divider-color, rgba(0,0,0,0.08));
          font-size: 0.67rem; color: var(--disabled-text-color, #9e9e9e); text-align: right;
        }
      </style>
      <div class="card">
        <div class="card-header">
          ${renderIcon("mdi:home-assistant", "#90CAF9")}
          <div>
            <div class="card-title">${title}</div>
            <div class="card-subtitle">Instance Statistics · updated every 5 min</div>
          </div>
        </div>
        ${groups}
        <div class="footer">HA Instance Stats v${CARD_VERSION}</div>
      </div>`;
  }
}

customElements.define("ha-instance-stats-card", HAInstanceStatsCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "ha-instance-stats-card",
  name: "HA Instance Stats",
  description: "Displays your Home Assistant instance statistics grouped by category.",
  preview: false,
  documentationURL: "https://github.com/olli-dot-dev/ha-instance-stats",
});

console.info(
  `%c HA-INSTANCE-STATS-CARD %c v${CARD_VERSION} `,
  "background:#0d47a1;color:#90CAF9;font-weight:bold;padding:2px 6px;border-radius:3px 0 0 3px",
  "background:#1565C0;color:#fff;padding:2px 6px;border-radius:0 3px 3px 0"
);
