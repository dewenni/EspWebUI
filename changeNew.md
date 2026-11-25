# v0.0.16

## Improvements and fixes

- Generate gzip assets with a fixed zero timestamp so unchanged WebUI sources produce stable headers.
- Write assembled HTML, CSS, JavaScript and generated C headers only when their content changes. Repeated builds preserve file timestamps and avoid unnecessary firmware recompilation.
- Add host regression checks for clean generation, unchanged repeat runs, changed HTML and login titles, and lossless deterministic gzip.

This release addresses the WebUI generator portion of [ESP_Buderus_KM271 #189](https://github.com/dewenni/ESP_Buderus_KM271/issues/189). The simulation source and output handling are fixed in the application repository.
