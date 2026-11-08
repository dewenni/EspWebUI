"""Run with: python3 -m unittest discover -s tests."""
import importlib.util
import logging
from pathlib import Path
import sys
import tempfile
import unittest

path = Path(__file__).resolve().parents[1] / "scripts" / "checkText.py"
spec = importlib.util.spec_from_file_location("checkText", path)
check = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = check
spec.loader.exec_module(check)


class JavaScriptKeysTests(unittest.TestCase):
    def uses(self, source):
        return check.javascript_keys(source)[1]

    def test_declarations_do_not_count_as_reads(self):
        keys, uses = check.javascript_keys('''
          const lib_translations = {first: {de: "first", en: "first"}, 'second-key': {de: 'x', en: 'x'}};
          const user_translations = {first: {de: 'x', en: 'x'}};
          // user_translations["comment"]
          /* lib_translations.comment */
          const text = "user_translations.fake";
          const pattern = /user_translations["not_a_read"]/g;
        ''')
        self.assertEqual(keys, ['first', 'second-key', 'first'])
        self.assertEqual(uses, set())

    def test_direct_reads_and_conditionals(self):
        self.assertEqual(self.uses('''
            lib_translations.title[lang]; user_translations['message'][lang];
            user_translations[mode === 'anything' ? "yes" : condition ? "maybe" : "no"];
            user_translations.hasOwnProperty(key);
        '''), {'title', 'message', 'yes', 'maybe', 'no'})

    def test_named_helpers_and_forwarding(self):
        self.assertEqual(self.uses('''
          function arbitraryText(key) { return user_translations[key][language]; }
          function relay(lang, textKey) { return arbitraryText(textKey); }
          const fail = (message) => { status.textContent = relay('de', message); };
          fail('unknown_is_still_a_use');
          relay('en', condition === 'not_a_key' ? 'first' : 'second');
          arbitraryText('direct');
        '''), {'unknown_is_still_a_use', 'first', 'second', 'direct'})

    def test_arrows_function_expressions_and_templates(self):
        self.assertEqual(self.uses('''
          const read = key => lib_translations[key].de;
          const forward = (key) => read(key);
          const message = function(key) { return forward(key); };
          const result = `ignore ${message("inside_template")} ${forward('another')} raw text`;
          user_translations[`literal_template`];
          user_translations[`dynamic_${value}`];
        '''), {'inside_template', 'another', 'literal_template'})

    def test_unrelated_literals_and_shadowed_helpers_are_not_reads(self):
        self.assertEqual(self.uses('''
          function translate(key) { return lib_translations[key].de; }
          translate('used');
          function unrelated() {
            const translate = (key) => console.log(key);
            translate('unrelated');
          }
          console.log('unused');
          const value = 'unused';
          // translate('comment');
        '''), {'used'})

    def test_runtime_generated_keys_are_not_reported_as_literal_keys(self):
        self.assertEqual(self.uses('''
          function text(key) { return user_translations[key].de; }
          text('prefix_' + runtimeValue);
          user_translations[computed];
        '''), set())

    def test_html_literals_and_suffixes(self):
        html = check._HtmlKeys()
        html.feed('''<p data-i18n='first$ / $second++suffix'></p>
                     <p data-i18n="simple"></p>''')
        self.assertEqual(html.keys, {'first', 'second', 'simple'})


class CheckerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name)

    def run_check(self, lib, user, html=''):
        (self.output / 'lib.js').write_text(lib)
        (self.output / 'user.js').write_text(user)
        (self.output / 'index.html').write_text(html)
        return check.check_translations(self.output)

    def test_cross_bundle_helper_missing_and_unused(self):
        with self.assertLogs(level=logging.WARNING) as logs:
            success = self.run_check('''
                const lib_translations = {visible: {de:'x', en:'x'}};
                function text(key) { return user_translations[key].de; }
              ''', '''
                const user_translations = {js_only:{de:'x',en:'x'}, unused:{de:'x',en:'x'}};
                text('js_only'); text('missing_js');
              ''', '<p data-i18n="visible"></p><p data-i18n="missing_html"></p>')
        self.assertFalse(success)
        self.assertTrue(any("'unused'" in line and 'WARNING' in line for line in logs.output))
        self.assertTrue(any("'missing_js'" in line and 'JavaScript' in line for line in logs.output))
        self.assertTrue(any("'missing_html'" in line and 'HTML' in line for line in logs.output))
        self.assertFalse(any("'js_only'" in line for line in logs.output))

    def test_missing_dictionary_and_duplicate_keys(self):
        with self.assertLogs(level=logging.ERROR):
            self.assertFalse(self.run_check('// const lib_translations = {};', 'const user_translations = {};'))
        with self.assertLogs(level=logging.WARNING) as logs:
            self.assertTrue(self.run_check('const lib_translations={same:{de:"x"}};',
                                           'const user_translations={same:{de:"y"}};',
                                           '<p data-i18n="same"></p>'))
        self.assertTrue(any('Doppelter' in line for line in logs.output))


if __name__ == '__main__':
    unittest.main()
