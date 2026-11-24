// --------------------------------------
// localization texts
// --------------------------------------
const lib_translations = {
  config_files_export: { de: "Backup exportieren", en: "Export backup" },
  config_files_exported: { de: "Backup exportiert.", en: "Backup exported." },
  config_files_device: { de: "Backup auf dem Gerät", en: "Backup on device" },
  config_files_computer: { de: "Import / Export", en: "Import / export" },
  config_files_saved_at: { de: "Zuletzt gespeichert", en: "Last saved" },
  config_files_backup_at: { de: "Backup erstellt", en: "Backup created" },
  config_files_unknown: { de: "Zeitpunkt unbekannt", en: "Time unknown" },
  config_files_missing: { de: "Kein Backup vorhanden", en: "No backup available" },
  config_files_create: { de: "Backup erstellen", en: "Create backup" },
  config_files_restore: { de: "Backup wiederherstellen", en: "Restore backup" },
  config_files_replace_confirm: { de: "Vorhandenes Backup ersetzen?", en: "Replace the existing backup?" },
  config_files_restore_confirm: { de: "Backup wiederherstellen? Aktuelle Einstellungen werden ersetzt und das Gerät startet neu.", en: "Restore the backup? Current settings will be replaced and the device will restart." },
  config_files_import_confirm: { de: "Konfiguration importieren? Aktuelle Einstellungen werden ersetzt und das Gerät startet neu.", en: "Import configuration? Current settings will be replaced and the device will restart." },
  config_files_working: { de: "Datei wird verarbeitet …", en: "Processing file \u2026" },
  config_files_created: { de: "Backup erstellt.", en: "Backup created." },
  config_files_restored: { de: "Backup wiederhergestellt. Das Gerät startet neu.", en: "Backup restored. The device is restarting." },
  config_files_imported: { de: "Konfiguration importiert. Das Gerät startet neu.", en: "Configuration imported. The device is restarting." },
  config_files_invalid: { de: "Ungültige Konfigurationsdatei oder falsches Projekt.", en: "Invalid configuration file or wrong project." },
  config_files_failed: { de: "Dateivorgang fehlgeschlagen. Bitte erneut versuchen.", en: "File operation failed. Please try again." },
  config_files_space: { de: "Nicht genügend freier Dateispeicher.", en: "Not enough free filesystem space." },
  config_files_busy: { de: "Gerät beschäftigt. Bitte später erneut versuchen.", en: "Device busy. Please try again later." },
  config_files_connection: { de: "Keine Verbindung. Bitte nach dem Wiederverbinden erneut prüfen.", en: "Connection lost. Please check again after reconnecting." },
  settings_area: { de: "Bereich", en: "Category" },
  settings_general: { de: "Allgemein", en: "General" },
  settings_network: { de: "Netzwerk", en: "Network" },
  settings_integrations: { de: "Integrationen", en: "Integrations" },
  settings_device: { de: "Gerät", en: "Device" },
  settings_maintenance: { de: "Zugriff & Wartung", en: "Access & maintenance" },
  settings_time: { de: "Datum & Uhrzeit", en: "Date & time" },
  system: {
    de: "System",
    en: "System",
  },
  settings: {
    de: "Einstellungen",
    en: "Settings",
  },
  ok: {
    de: "OK",
    en: "OK",
  },
  network_info: {
    de: "Netzwerk-Information",
    en: "Network-Informations",
  },
  wifi_ip: {
    de: "WiFi IP-Adresse",
    en: "WiFi IP-Address",
  },
  wifi_signal: {
    de: "WiFi Signal",
    en: "WiFi Signal",
  },
  wifi_rssi: {
    de: "WiFi Rssi",
    en: "WiFi Rssi",
  },
  eth_ip: {
    de: "ETH IP-Adresse",
    en: "ETH IP-Address",
  },
  eth_status: {
    de: "ETH Status",
    en: "ETH Status",
  },
  static_ip: {
    de: "feste IP-Adresse",
    en: "static ip address",
  },
  eth_link_speed: {
    de: "ETH Geschwindigkeit",
    en: "ETH Link Speed",
  },
  eth_full_duplex: {
    de: "ETH Vollduplex",
    en: "ETH Full Duplex",
  },
  sw_version: {
    de: "Software-Version",
    en: "Software-Version",
  },
  version_info: {
    de: "Versionsinformationen",
    en: "Version Informations",
  },
  esp_maxallocheap: {
    de: "ESP MaxAllocHeap",
    en: "ESP MaxAllocHeap",
  },
  esp_minfreeheap: {
    de: "ESP MinFreeHeap",
    en: "ESP MinFreeHeap",
  },
  esp_flash_usage: {
    de: "ESP Flash usage",
    en: "ESP Flash usage",
  },
  esp_heap_usage: {
    de: "ESP Heap usage",
    en: "ESP Heap usage",
  },
  sysinfo: {
    de: "Systeminformationen",
    en: "System Informations",
  },
  date: {
    de: "Datum",
    en: "Date",
  },
  wifi: {
    de: "WiFi",
    en: "WiFi",
  },
  ssid: {
    de: "SSID",
    en: "SSID",
  },
  password: {
    de: "Passwort",
    en: "Password",
  },
  user: {
    de: "Benutzer",
    en: "User",
  },
  hostname: {
    de: "Hostname",
    en: "Hostname",
  },
  server: {
    de: "Server",
    en: "Server",
  },
  topic: {
    de: "Topic",
    en: "Topic",
  },
  mqtt: {
    de: "MQTT",
    en: "MQTT",
  },
  port: {
    de: "Port",
    en: "Port",
  },
  ntp: {
    de: "NTP-Server",
    en: "NTP-Server",
  },
  ntp_tz: {
    de: "Time-Zone",
    en: "Time-Zone",
  },
  restart: {
    de: "Neustart",
    en: "restart",
  },
  ota: {
    de: "OTA Firmware Update",
    en: "OTA Firmware Update",
  },
  config_mgn: {
    de: "Konfiguration import/export",
    en: "configuration import/export",
  },
  tools: {
    de: "Tools",
    en: "Tools",
  },
  activate: {
    de: "Aktivieren",
    en: "activate",
  },
  ip_adr: {
    de: "IP-Adresse",
    en: "IP-Address",
  },
  ip_subnet: {
    de: "Subnetz",
    en: "Subnet",
  },
  ip_gateway: {
    de: "Gateway",
    en: "Gateway",
  },
  ip_dns: {
    de: "DNS-Server",
    en: "DNS-Server",
  },
  access: {
    de: "Zugangskontrolle",
    en: "Authentication",
  },
  logger: {
    de: "Logbuch",
    en: "Logger",
  },
  clear: {
    de: "L\u00f6schen",
    en: "clear",
  },
  refresh: {
    de: "Aktualisieren",
    en: "refresh",
  },
  lifetime: {
    de: "Laufzeit",
    en: "Runtime",
  },
  restart_reason: {
    de: "Neustart Grund",
    en: "restart reason",
  },
  language: {
    de: "Sprache",
    en: "language",
  },
  german: {
    de: "Deutsch",
    en: "german",
  },
  english: {
    de: "Englisch",
    en: "english",
  },
  lost_connection: {
    de: "keine Verbindung!",
    en: "no connection",
  },
  sort_up: {
    de: "aufsteigend \u2B06",
    en: "ascending \u2B06",
  },
  sort_down: {
    de: "absteigend \u2B07",
    en: "descending \u2B07",
  },
  log_level_4: {
    de: "Level: Debug",
    en: "Level: Debug",
  },
  log_level_3: {
    de: "Level: Info",
    en: "Level: Info",
  },
  log_level_2: {
    de: "Level: Warnung",
    en: "Level: Warning",
  },
  log_level_1: {
    de: "Level: Fehler",
    en: "Level: Error",
  },
  import: {
    de: "import (config.json)",
    en: "import (config.json)",
  },
  export: {
    de: "export (config.json)",
    en: "export (config.json)",
  },
  open: {
    de: "öffne (config.json)",
    en: "open (config.json)",
  },
  update_done: {
    de: "Update erfolgreich!",
    en: "Update sucessfull!",
  },
  update_failed: {
    de: "Update nicht erfolgreich!",
    en: "Update not sucessfull!",
  },
  update_ready: {
    de: "Update bereit!",
    en: "Update ready!",
  },
  update_info: {
    de: "ESP muss neu gestartet werden um das Update zu übernehmen.",
    en: "ESP must be restarted to apply the update",
  },
  error_text: {
    de: "Fehler:",
    en: "Error:",
  },
  update_error_info: {
    de: "Bitte das Update erneut ausführen!",
    en: "Please run the update again!",
  },
  import_ready: {
    de: "Import bereit!",
    en: "import ready!",
  },
  close: {
    de: "schließen",
    en: "close",
  },
  act_version: {
    de: "aktuelle Version",
    en: "actual version",
  },
  github_version: {
    de: "letztes Release",
    en: "latest release",
  },
  mqtt_info: {
    de: "MQTT-Informationen",
    en: "MQTT information",
  },
  last_error: {
    de: "letzter Fehler",
    en: "last error",
  },
  connection: {
    de: "Verbindung",
    en: "connection",
  },
  state: {
    de: "Zustand",
    en: "State",
  },
  check_github: {
    de: "Prüfe GitHub OTA Update",
    en: "Check for GitHub OTA Update",
  },
};
