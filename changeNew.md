# v0.0.12

## what's new

[FIX] Make WebSocket connections more resilient when browser tabs are in the background.

## changelog

[CHANGE] Treat every received WebSocket message as a sign of life and allow 30 seconds without data while the page is visible.

[FIX] Pause the inactivity watchdog for hidden pages. On return, allow fresh data on open connections and immediately reconnect closed connections.

[FIX] Prevent duplicate connection attempts and reconnect timers, and ignore callbacks from obsolete sockets.
