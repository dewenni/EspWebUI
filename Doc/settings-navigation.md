# Settings categories

EspWebUI can group an existing settings page without changing the fields,
their IDs or the configuration callbacks. Categories use a list of buttons on
wide content areas and a single select on narrow content areas.

```html
<div class="settings-layout" data-settings data-settings-initial="network">
  <div class="settings-body">
    <aside class="settings-category-nav" aria-labelledby="settings-area-label">
      <label class="settings-category-picker">
        <span id="settings-area-label" data-i18n="settings_area"></span>
        <select data-settings-select data-ui-local></select>
      </label>
      <div class="settings-category-list" data-settings-list></div>
    </aside>
    <div class="settings-panels">
      <section id="settings-network" class="settings-panel"
               data-settings-group="network"
               data-settings-label="settings_network">
        <h2 data-i18n="settings_network"></h2>
        <details>
          <summary>WiFi</summary>
          <!-- Existing inputs, with their existing IDs and handlers. -->
        </details>
      </section>
      <section id="settings-device" class="settings-panel"
               data-settings-group="device"
               data-settings-label="settings_device">
        <h2 data-i18n="settings_device"></h2>
        <!-- Project-specific settings. -->
      </section>
    </div>
  </div>
</div>
```

Add another `section` to add a category. Its `id` must be unique; its
`data-settings-group` value identifies the category. Declare the
`data-settings-label` translation key in the project's `user_translations`
when it is not a shared library label. Use the same key on the heading.

The shared labels are General, Network, Integrations, Device and
Access & maintenance. A project can omit categories it does not need.

`initializeSettingsNavigation()` is called during the library's normal DOM
initialization, before localization. The category list and select are generated
from the sections. Calling it again does not create duplicate controls.

Only presentation changes: inactive sections are hidden, not removed. Values,
open sections and existing listeners are retained. The selection also survives
switching to another main page and back. It resets on a full page reload.

The generated buttons and the selector use `data-ui-local`; the library's
generic button/select handlers exclude these controls from device commands.
Do not assign them configuration IDs or attach project configuration handlers.

The 700px breakpoint uses the available settings width, independently of the
main navigation's responsive breakpoint. The main navigation is unchanged.
Without JavaScript all categories remain visible.

For horizontal categories above the content, add `data-settings-layout="tabs"`
to the `settings-layout` element. This opt-in layout uses one unwrapped row and
automatically replaces it with the select when the translated labels no longer
fit the available width. Resizing and language changes are handled without
reinitialization. The hidden button row stays measurable but is clipped and
inaccessible while the select is shown. Other projects keep the default side list.

This component does not add a save button or change how existing fields save.
