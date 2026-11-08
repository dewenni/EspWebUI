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
