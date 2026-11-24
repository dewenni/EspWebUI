// Run: node tests/test_config_files_ui.cjs (Node.js 18+, built-in modules only).
// Exercises actual frontend logic; does not test browser rendering or networking.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.join(__dirname, '..');

function fixture() {
  const nodes = new Map();
  for (const id of ['file_upload_form', 'file_input', 'config_saved_at', 'config_dialog_saved_at', 'config_backup_at',
    'config_backup_btn', 'config_restore_btn', 'config_backup_export_btn', 'msgBar', 'msgBarText']) {
    nodes.set(id, { style: {}, classList: { toggle() {}, add() {}, remove() {} }, handlers: {}, addEventListener(type, fn) { this.handlers[type] = fn; }, removeAttribute() {}, files: [{}] });
  }
  const listeners = new Map(), sent = [], downloads = [], timers = new Map();
  let timerId = 0;
  let reloads = 0;
  const context = vm.createContext({
    document: { documentElement: { lang: 'de' }, getElementById: id => nodes.get(id), querySelectorAll: () => [], body: { appendChild() {} },
      createElement: () => ({ click() { downloads.push({ name: this.download, href: this.href }); }, remove() {} }) },
    window: { addEventListener: (event, fn) => listeners.set(event, fn), location: { reload: () => ++reloads } },
    ws: { readyState: 1 }, WebSocket: { OPEN: 1 },
    sendData: (id, value) => sent.push([id, value]), confirm: () => true,
    setTimeout: (fn, ms) => { timers.set(++timerId, { fn, ms }); return timerId; }, clearTimeout: id => timers.delete(id),
    URL: { createObjectURL: () => 'blob:backup', revokeObjectURL() {} },
    FormData: class {}, fetch: async () => ({ ok: true, status: 202 }),
  });
  for (const file of ['lib_lang.js', 'lib_config_files.js']) vm.runInContext(fs.readFileSync(path.join(root, 'web/js', file), 'utf8'), context);
  const fun = fs.readFileSync(path.join(root, 'web/js/lib_fun.js'), 'utf8');
  vm.runInContext(fun.slice(fun.indexOf('let msgBarHideTimer;'), fun.indexOf('// Watch only visible pages:')), context);
  context.initializeConfigFiles();
  return { context, nodes, sent, downloads, timers, event: (type, detail) => listeners.get(type)?.({ detail }), reloads: () => reloads };
}

(async () => {
  const f = fixture();
  assert(f.nodes.get('config_restore_btn').disabled);
  assert(f.nodes.get('config_backup_export_btn').disabled);
  f.event('webui:connected');
  assert.deepEqual(f.sent.pop(), ['config_files', 'status']);
  const state = { type: 'configFiles', savedAt: '', backupAt: '', backupExists: false };
  f.event('webui:message', state);
  assert.equal(f.nodes.get('config_saved_at').textContent, 'Zeitpunkt unbekannt');
  assert.equal(f.nodes.get('config_backup_at').textContent, 'Kein Backup vorhanden');
  assert(f.nodes.get('config_restore_btn').disabled);
  f.nodes.get('config_backup_btn').handlers.click();
  assert.deepEqual(f.sent.pop(), ['config_files', 'backup']);
  assert(f.nodes.get('config_backup_btn').disabled);
  f.event('webui:message', { ...state, result: 'config_files_space' });
  assert(!f.nodes.get('config_backup_btn').disabled);
  assert.equal(f.nodes.get('msgBarText').textContent, 'Nicht genügend freier Dateispeicher.');
  f.event('webui:message', { ...state, backupExists: true, backupAt: '2026-11-24 20:00:00', result: 'config_files_created' });
  assert.equal(f.nodes.get('msgBarText').textContent, 'Backup erstellt.');
  assert.equal(f.nodes.get('msgBar').style.display, 'flex', 'Fly-in uses the footer flex alignment');
  const oldTimer = [...f.timers.keys()].find(id => f.timers.get(id).ms === 2500);
  f.context.showMsgBar({ text: 'Neue Meldung' });
  assert(!f.timers.has(oldTimer), 'A later fly-in cancels the earlier hide timer');
  const hide = [...f.timers.values()].find(timer => timer.ms === 2500);
  hide.fn();
  const remove = [...f.timers.values()].find(timer => timer.ms === 500);
  remove.fn();
  assert.equal(f.nodes.get('msgBar').style.display, 'none');
  f.context.confirm = () => false;
  f.nodes.get('config_restore_btn').handlers.click();
  f.nodes.get('config_backup_btn').handlers.click();
  assert.equal(f.sent.length, 0, 'Cancelled restore/overwrite sends nothing');
  f.context.confirm = () => true;
  f.nodes.get('config_restore_btn').handlers.click();
  assert.deepEqual(f.sent.pop(), ['config_files', 'restore']);
  f.event('webui:message', { ...state, result: 'config_files_restored' });
  f.event('webui:disconnected'); f.event('webui:connected');
  assert.equal(f.reloads(), 1);

  const upload = fixture();
  await upload.nodes.get('file_upload_form').handlers.submit({ preventDefault() {} });
  assert.equal(upload.nodes.get('msgBarText').textContent, undefined, 'HTTP 202 produces no success message');
  assert(upload.nodes.get('config_backup_btn').disabled, 'Operation stays busy until its result arrives');
  upload.event('webui:message', { ...state, result: 'config_files_invalid' });
  assert.equal(upload.nodes.get('msgBarText').textContent, 'Ungültige Konfigurationsdatei oder falsches Projekt.');
  upload.context.document.documentElement.lang = 'en';
  upload.event('webui:message', { ...state, result: 'config_files_invalid' });
  assert.equal(upload.nodes.get('msgBarText').textContent, 'Invalid configuration file or wrong project.');
  upload.context.fetch = async () => ({ ok: false, json: async () => ({ error: 'config_files_busy' }) });
  await upload.nodes.get('file_upload_form').handlers.submit({ preventDefault() {} });
  assert.equal(upload.nodes.get('msgBarText').textContent, 'Device busy. Please try again later.');
  const download = fixture();
  download.event('webui:message', { ...state, backupExists: true });
  assert(!download.nodes.get('config_backup_export_btn').disabled);
  download.context.fetch = async () => ({ ok: true, blob: async () => ({}) });
  await download.context.exportConfigBackup();
  assert.deepEqual(download.downloads, [{ name: 'config_backup.json', href: 'blob:backup' }]);
  assert.equal(download.sent.length, 0, 'Export sends no device command');
  assert.equal(download.nodes.get('msgBarText').textContent, 'Backup exportiert.');
  download.context.fetch = async () => ({ ok: false, status: 404 });
  await download.context.exportConfigBackup();
  assert.equal(download.nodes.get('msgBarText').textContent, 'Kein Backup vorhanden');
  console.log('PASS: backup/restore confirmation, status/time localization, errors, staged import and reload after restart.');
})().catch(error => { console.error(error); process.exitCode = 1; });
