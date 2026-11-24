// Run with: node tests/test_initial_language.cjs
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = process.env.ESPWEBUI_TEST_ROOT || path.join(__dirname, '..');
const fun = fs.readFileSync(path.join(root, 'web/js/lib_fun.js'), 'utf8');
const doc = fs.readFileSync(path.join(root, 'web/js/lib_doc.js'), 'utf8');

async function check(language, expected) {
  const translations = [];
  const events = new Map();
  const languageSelect = { tagName: 'SELECT', value: '', addEventListener: (type, fn) => events.set(type, fn) };
  const title = {
    getAttribute: () => 'title',
    set innerText(value) { translations.push(value); },
  };
  let start;
  let resolveConfig;
  let finished;
  const genericElement = { addEventListener() {} };
  const context = vm.createContext({
    console: { log() {}, error(message) { throw new Error(message); } },
    document: {
      documentElement: { lang: 'de' },
      addEventListener(type, callback) { if (type === 'DOMContentLoaded') start = callback; },
      getElementById(id) { return id === 'version_dialog' ? null : id === 'cfg_lang' ? languageSelect : genericElement; },
      querySelectorAll(selector) { return selector === '[data-i18n]' ? [title] : []; },
    },
    window: { addEventListener() {} },
    lib_translations: { title: { de: 'Deutsch', en: 'English' } },
    user_translations: {},
    fetch: () => new Promise(resolve => { resolveConfig = resolve; }),
    initializeSettingsNavigation() {},
    initializeConfigFiles() {},
    renderConfigFileStatus() {},
    setTimeout, clearTimeout,
  });
  vm.runInContext(fun, context);
  // Keep the real startup handler and config loader, but simulate no WebSocket.
  context.setupWS = () => {};
  context.initializeVisibilityBasedOnSwitches = () => {};
  const load = context.loadConfig;
  context.loadConfig = () => { finished = load(); return finished; };
  vm.runInContext(doc, context);
  start();
  assert.deepEqual(translations, [], 'Do not translate before the delayed config response');
  resolveConfig({ ok: true, json: async () => language === undefined ? {} : { lang: language } });
  await finished;
  assert.deepEqual(translations, [expected], 'First translation must use the configured language');
  languageSelect.value = '1';
  events.get('change').call(languageSelect);
  assert.equal(translations.at(-1), 'English', 'Language selector still works');
  context.setLanguage({ language: 'de' });
  assert.equal(translations.at(-1), 'Deutsch', 'WebSocket language updates still work');
}

(async () => {
  for (const [language, expected] of [[1, 'English'], ['1', 'English'], [0, 'Deutsch'], ['0', 'Deutsch'], [undefined, 'Deutsch'], [99, 'Deutsch']]) {
    await check(language, expected);
  }
  console.log('PASS: delayed config, DE/EN, missing/invalid language, no WebSocket and runtime language changes');
})().catch(error => { console.error(error); process.exitCode = 1; });
