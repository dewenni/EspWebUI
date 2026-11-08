# v0.0.11

## what's new

[ADD] Automatically use secure WebSockets (`wss://`) when the WebUI is opened over HTTPS.

## changelog

[CHANGE] Select `ws://` for HTTP and `wss://` for HTTPS using the page's protocol, host and port. This supports HTTPS reverse proxies and tunnels without changing direct HTTP access.

[CREDIT] Based on dewenni/ESP_Buderus_KM271#180 by @kwaaak. Implemented in the library source so generated WebUI builds retain the change.

---

# v0.0.10

## what's new

[ADD] Build-time translation validation now includes JavaScript reads as well as HTML.

## changelog

[FIX] Recognize translation keys passed through project-specific helper functions, including forwarded parameters, conditional literal arguments and template interpolations. No helper name is hardcoded.

[CHANGE] Analyze library and project JavaScript together. Unused-key warnings and missing-key errors now refer to HTML and JavaScript. Translation declarations, comments and unrelated strings do not count as uses.

[TEST] Add regression tests for translation reads, helper forwarding, missing/unused keys and duplicate declarations.

---

# v0.0.9

## what's new

[ADD] Project-specific font size adjustment with `--pico-font-size-override`.

## changelog

[CHANGE] Responsive base font sizes now range from 75% to 100%. The default offset is 0%; set it in the project's custom.css to adjust all breakpoints.

---

# v0.0.8

## what's new

## changelog

[CHANGE] Auth consolidation across a few routes #3 by @xn101de

---

# v0.0.7

## what's new

## changelog

[CHANGE] reduce debug messages

---

# v0.0.6

## what's new

## changelog

[ADD] Colorize logger messages depending on log level

---

# v0.0.5

## what's new

## changelog

[ADD] optional favicon parameter for WebUI.begin

---

# v0.0.4

## what's new

## changelog

[ADD] JavaScript - toggleElementVisibility() - add function to disable option elements in dropdown

---

# v0.0.3

## what's new

## changelog

[FIX] avoid sendData if there is no websocket connection (simulation mode)

---

# v0.0.2

## what's new

## changelog

remove toggleTimeInputs and add ´updateUIcallbackSelect()´

---

# v0.0.1

initial release

## changelog
