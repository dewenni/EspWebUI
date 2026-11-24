# v0.0.15

## what's new

[NEW] Shared configuration backup, restore, backup download and file timestamps for application Tools pages.

## changelog

[NEW] Copy and verify backups through a temporary file before atomically replacing the destination. Preserve existing files on write, space or replacement errors.

[NEW] Stage imports under a separate filename, validate JSON and an optional project section, and commit completed imports from the application loop. Interrupted, concurrent or malformed uploads cannot replace the active configuration.

[NEW] Provide an authenticated backup download without restoring the saved configuration first.

[CHANGE] Report completed configuration operations through translated success/error fly-ins. Keep action buttons busy until the operation is confirmed.

[FIX] Vertically center fly-in messages and restart their hide timer when a newer message arrives.

[TEST] Add maintained file-transfer and frontend regression checks, including write/replacement failures, disconnected uploads and backup-download authentication.
