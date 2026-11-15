# v0.0.14

## changelog

[FIX] Initialize the WebUI language from `config.json` instead of translating to German before the configured language is known. The configured language is also applied when WebSocket communication is unavailable.

[FIX] Use German as the fallback for a missing or invalid language setting; preserve language switching during operation.

Fixes the initial language switch reported in [ESP_Buderus_KM271 #183](https://github.com/dewenni/ESP_Buderus_KM271/issues/183).
