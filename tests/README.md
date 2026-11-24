# Host checks

Run from the EspWebUI repository with Python 3.9+, Node.js 18+ and a C++17
compiler supporting AddressSanitizer/UndefinedBehaviorSanitizer:

```sh
python3 tests/test_config_files.py /path/to/ArduinoJson/src
node tests/test_config_files_ui.cjs
python3 tests/test_check_text.py
node tests/test_initial_language.cjs
```

ArduinoJson 7 headers must already be installed. If no path is supplied, the
file test uses the sibling Jarolift checkout's PlatformIO dependencies.

The file test compiles the actual `config_files.cpp` and `config_transfer.cpp`
against an in-memory filesystem and request objects. It covers project checks
(`jaro`/`km271`), partial writes, failed replacement, space/open errors,
interrupted/concurrent/multiple-file uploads, authentication and loop-task
commit. The UI test checks confirmations, translated dates/status, errors,
HTTP acceptance versus confirmed commit, success/error fly-ins, fly-in timer replacement,
backup download and reload after restoration. The file test also checks download
authentication, missing backups, attachment filename/path and unchanged files.

These checks do not measure ESP heap usage, real browser layout, flash
power-loss behavior, clock synchronization or actual restart/reconnection.
Build each consumer sequentially: generated EspWebUI headers are shared.

On hardware, verify backup replacement and restoration after changed settings,
import with an arbitrary filename, rejection of the other project's JSON,
timestamps with/without synchronized time, disconnected uploads and restart
with the restored network/authentication settings. Backups contain credentials
and only cover `config.json`, not NVS counters/history or external data.
