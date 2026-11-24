let configFileState;
let configFileWorking = false;
let configFileRequestTimer;
let configFileRestarting = false;

function configFileText(key) {
  const language = document.documentElement.lang === "de" ? "de" : "en";
  return lib_translations[key]?.[language] || key;
}

function renderConfigFileStatus() {
  const state = configFileState;
  for (const id of ["config_saved_at", "config_dialog_saved_at"]) {
    const element = document.getElementById(id);
    if (element && state) {
      element.removeAttribute("data-i18n");
      element.textContent = state.savedAt || configFileText("config_files_unknown");
    }
  }
  const backup = document.getElementById("config_backup_at");
  if (backup && state) {
    backup.removeAttribute("data-i18n");
    backup.textContent = !state.backupExists ? configFileText("config_files_missing") : state.backupAt || configFileText("config_files_unknown");
  }
  const connected = typeof ws !== "undefined" && ws && ws.readyState === WebSocket.OPEN;
  const create = document.getElementById("config_backup_btn");
  const restore = document.getElementById("config_restore_btn");
  if (create) create.disabled = configFileWorking || !connected || !state;
  if (restore) restore.disabled = configFileWorking || !connected || !state?.backupExists;
  const download = document.getElementById("config_backup_export_btn");
  if (download) download.disabled = configFileWorking || !connected || !state?.backupExists;
}

function setConfigFileResult(key, working = false) {
  // Only completed operations produce a message; busy buttons show progress.
  if (!working) showMsgBar({ text: configFileText(key) });
  configFileWorking = working;
  renderConfigFileStatus();
  clearTimeout(configFileRequestTimer);
  if (working) configFileRequestTimer = setTimeout(() => setConfigFileResult("config_files_connection"), 30000);
}

function initializeConfigFiles() {
  const form = document.getElementById("file_upload_form");
  if (!form) return;
  document.querySelectorAll('[data-tab="tab11"]').forEach(link => {
    link.addEventListener("click", () => sendData("config_files", "status"));
  });
  window.addEventListener("webui:connected", () => {
    if (configFileRestarting) { window.location.reload(); return; }
    sendData("config_files", "status");
    renderConfigFileStatus();
  });
  window.addEventListener("webui:disconnected", () => {
    if (configFileWorking) setConfigFileResult("config_files_connection");
    renderConfigFileStatus();
  });
  window.addEventListener("webui:message", event => {
    const message = event.detail;
    if (message.type !== "configFiles") return;
    configFileState = message;
    if (message.result === "config_files_imported" || message.result === "config_files_restored") configFileRestarting = true;
    if (message.result) setConfigFileResult(message.result);
    else renderConfigFileStatus();
  });
  for (const [id, action] of [["config_backup_btn", "backup"], ["config_restore_btn", "restore"]]) {
    document.getElementById(id)?.addEventListener("click", () => {
      if (configFileWorking) return;
      if (action === "restore" && !confirm(configFileText("config_files_restore_confirm"))) return;
      if (action === "backup" && configFileState?.backupExists && !confirm(configFileText("config_files_replace_confirm"))) return;
      setConfigFileResult("config_files_working", true);
      sendData("config_files", action);
    });
  }
  document.getElementById("config_backup_export_btn")?.addEventListener("click", exportConfigBackup);
  form.addEventListener("submit", async event => {
    event.preventDefault();
    if (configFileWorking) return;
    const file = document.getElementById("file_input").files[0];
    if (!file || !confirm(configFileText("config_files_import_confirm"))) return;
    setConfigFileResult("config_files_working", true);
    try {
      const response = await fetch("/config-upload", { method: "POST", body: new FormData(form) });
      if (!response.ok) {
        let error = "config_files_failed";
        try { error = (await response.json()).error || error; } catch (_) { /* HTTP/network error */ }
        setConfigFileResult(error);
      }
      // 202 only means staged. The loop sends the actual validation/commit result.
    } catch (_) {
      setConfigFileResult("config_files_connection");
    }
  });
  renderConfigFileStatus();
}

async function exportConfigBackup() {
  if (configFileWorking || !configFileState?.backupExists) return;
  setConfigFileResult("config_files_working", true);
  try {
    const response = await fetch("/config-backup-download", { cache: "no-store" });
    if (!response.ok) {
      setConfigFileResult(response.status === 404 ? "config_files_missing" : "config_files_failed");
      return;
    }
    const url = URL.createObjectURL(await response.blob());
    const link = document.createElement("a");
    link.href = url;
    link.download = "config_backup.json";
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    setConfigFileResult("config_files_exported");
  } catch (_) {
    setConfigFileResult("config_files_connection");
  }
}
