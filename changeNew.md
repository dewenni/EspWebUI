# v0.0.13

## what's new

[NEW] Shared settings categories with horizontal tabs or a sidebar, responsive dropdown navigation and German/English labels.

[NEW] Compact, theme-aware login page with the application title and German/English browser-language selection.

## changelog

[NEW] Add client-specific JSON WebSocket replies and a callback that includes the requesting client ID.

[NEW] Expose browser events for WebSocket connections, disconnections and application-specific messages.

[CHANGE] Support local-only controls through `data-ui-local` and make the legacy GitHub version dialog optional for projects that show updates directly on their Tools page.

[FIX] Only report unused project translations; shared library vocabulary may remain unused by individual applications.

[DOC] Document settings navigation and application integration hooks.
