<div align="center">
<img style="width: 100px;" src="./Doc/EspWebUI_Logo.svg">

<h3 style="text-align: center;">EspWebUI-Library</h3>
</div>

-----


<div align="center">

[![Current Release](https://img.shields.io/github/release/dewenni/EspWebUI.svg)](https://github.com/dewenni/EspWebUI/releases/latest)
![GitHub Release Date](https://img.shields.io/github/release-date/dewenni/EspWebUI)
![GitHub last commit](https://img.shields.io/github/last-commit/dewenni/EspWebUI)


![GitHub watchers](https://img.shields.io/github/watchers/dewenni/EspWebUI?style=social)
[![GitHub stars](https://img.shields.io/github/stars/dewenni/EspWebUI.svg?style=social&label=Star)](https://github.com/dewenni/EspWebUI/stargazers/)

</div>

-----

<div align="center">
If you like this project, feel free to push the <b>[Star ⭐️]</b> button and click <b>[Watch 👁]</b> to stay updated.
<br><br>
And if you'd like to support my work, you can also<p>

[![Sponsor](https://img.shields.io/badge/Sponsor%20me%20on-GitHub-%23EA4AAA.svg?style=for-the-badge&logo=github)](https://github.com/sponsors/dewenni)

</div>

-----

# ESP-WebUI

EspWebUI is a framework library to build flexible and powerfull webserver based on ESP

You can find the corresponding Template Project here: https://github.com/dewenni/EspWebUI-Template


## Features & Description

:construction:

A list of features and a detailed description will follow....

## Installation

### Arduino IDE

1. Download the latest version of this library from [GitHub](https://github.com/dewenni/EspWebUI).
2. Extract the ZIP file into your Arduino `libraries` folder.
3. Restart the Arduino IDE.

### PlatformIO

1. Add the library to your `platformio.ini` file:

   ```ini
   lib_deps =
       https://github.com/dewenni/EspWebUI

   ```

## Project font size

EspWebUI uses responsive base font sizes of 75%, 80%, 85%, 90%, 95%, and 100%
at viewport widths of 100, 576, 768, 1024, 1280, and 1536 pixels respectively.
Set an offset in your project's `web/css/custom.css` to adjust all breakpoints:

```css
:root {
  --pico-font-size-override: 10%;
}
```

The default offset is `0%`. The example adds 10 percentage points, resulting
in 85%, 90%, 95%, 100%, 105%, and 110%. Negative offsets such as `-5%` are also
supported. Use a percentage value, including `0%` for no adjustment.

Remove any project-specific `--pico-font-size` breakpoint declarations when
switching to this offset, since they override the library's calculated values.

## Build-time translation checks

The build checks translations declared in `lib_translations` and `user_translations`
against both `data-i18n` attributes in HTML and translation reads in JavaScript.
Library and project JavaScript are checked together, including project helper
functions; their names are not hardcoded. For example:

```js
function text(key) {
  return user_translations[key][lang];
}

status.textContent = text(success ? "connected" : "disconnected");
```

Direct accesses such as `user_translations.connected[lang]` or
`lib_translations["close"][lang]` are also recognized, as are forwarded key
parameters in named functions and assigned arrow functions, and calls inside
template interpolations. Declarations, comments and unrelated string literals
do not count as uses. Missing literal keys fail the build; unused declarations
and duplicate keys produce warnings.

This is a static check, not a JavaScript interpreter. Runtime-generated keys
(e.g. `text("state_" + state)`), variable aliases and other dynamic data flows
cannot be reliably resolved. Prefer explicit literal alternatives when possible.

Run the checker regression tests with:

```sh
python3 -B -m unittest discover -s tests
```

## WebSocket transport

The WebUI selects its WebSocket protocol from the page URL: HTTP uses `ws://`,
HTTPS uses `wss://`. The page's host and port are retained, with `/ws` as the
WebSocket endpoint. An HTTPS reverse proxy or tunnel must forward WebSocket
connections to the ESP. This selection does not add TLS support to the ESP;
when a proxy terminates TLS, its connection to the ESP can still use plain HTTP/WS.
