# v0.0.11

## what's new

[ADD] Automatically use secure WebSockets (`wss://`) when the WebUI is opened over HTTPS.

## changelog

[CHANGE] Select `ws://` for HTTP and `wss://` for HTTPS using the page's protocol, host and port. This supports HTTPS reverse proxies and tunnels without changing direct HTTP access.

[CREDIT] Based on dewenni/ESP_Buderus_KM271#180 by @kwaaak. Implemented in the library source so generated WebUI builds retain the change.
