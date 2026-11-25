"""Run with python3 -B tests/test_build_webui.py (no PlatformIO required)."""
import gzip
import importlib.util
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
scons = types.ModuleType('SCons')
script = types.ModuleType('SCons.Script')
script.DefaultEnvironment = lambda: None
with patch.dict(sys.modules, {'SCons': scons, 'SCons.Script': script}):
    spec = importlib.util.spec_from_file_location('build_webui', ROOT / 'scripts/build_webui.py')
    build = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build)


class WebBuildTests(unittest.TestCase):
    def test_gzip_is_stable_and_lossless(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'asset.h'
            content = 'WebUI äöü'.encode('utf-8')
            build.write_gzip_c_array(content, target, 'asset')
            first = target.read_bytes()
            os.utime(target, ns=(1000000000, 1000000000))
            with patch('time.time', return_value=2000000000):
                build.write_gzip_c_array(content, target, 'asset')
            self.assertEqual(target.read_bytes(), first)
            self.assertEqual(target.stat().st_mtime_ns, 1000000000)
            compressed = bytes(int(n, 16) for n in re.findall(r'0x([0-9a-f]{2})', first.decode()))
            self.assertEqual(compressed[4:8], b'\0' * 4)
            self.assertEqual(gzip.decompress(compressed), content)

    def test_full_generation_preserves_unchanged_files_and_updates_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            library = root / 'library'
            (library / 'scripts').mkdir(parents=True)
            (library / 'include').mkdir()
            shutil.copytree(ROOT / 'web', library / 'web')
            project = root / 'project'
            for name in ('html', 'css', 'js'):
                (project / 'web' / name).mkdir(parents=True)
            html = project / 'web/html/00.html'
            html.write_text('<!--SECTION-START--><title>Build test</title><!--SECTION-END-->')
            (project / 'web/css/user.css').write_text('body { color: blue; }')
            (project / 'web/js/user.js').write_text('const test = 1;')
            previous = Path.cwd()
            os.chdir(library / 'scripts')
            try:
                with patch.object(build, 'DefaultEnvironment', return_value={'PROJECT_DIR': str(project)}):
                    build.main('web', 'output')
                    files = list((project / 'web/output').glob('*')) + list((library / 'include').glob('*'))
                    self.assertEqual(len(files), 12)  # five assets and seven gzip headers
                    original = {p: p.read_bytes() for p in files}
                    for p in files:
                        os.utime(p, ns=(1000000000, 1000000000))
                    build.main('web', 'output')
                    self.assertTrue(all(p.stat().st_mtime_ns == 1000000000 for p in files))
                    html.write_text('<!--SECTION-START--><title>Changed title</title><!--SECTION-END-->')
                    build.main('web', 'output')
                    changed = {p.name for p in files if p.read_bytes() != original[p]}
                    self.assertEqual(changed, {'index.html', 'gzip_user_html.h', 'gzip_login_html.h'})
                    self.assertIn('Changed title', (project / 'web/output/index.html').read_text())
            finally:
                os.chdir(previous)


if __name__ == '__main__':
    unittest.main()
