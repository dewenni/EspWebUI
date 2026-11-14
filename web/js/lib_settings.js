// Settings categories change presentation only; the existing fields stay in the DOM.
function initializeSettingsNavigation() {
  document.querySelectorAll('[data-settings]').forEach(root => {
    if (root.classList.contains('settings-ready')) return;
    const groups = Array.from(root.querySelectorAll('[data-settings-group]'));
    const list = root.querySelector('[data-settings-list]');
    const select = root.querySelector('[data-settings-select]');
    if (!groups.length || !list || !select) return;
    const buttons = groups.map(group => {
      const button = document.createElement('button');
      button.type = 'button';
      button.dataset.uiLocal = '';
      button.dataset.i18n = group.dataset.settingsLabel;
      button.setAttribute('aria-controls', group.id);
      button.textContent = group.querySelector('h2').textContent;
      list.append(button);
      const option = document.createElement('option');
      option.value = group.dataset.settingsGroup;
      option.dataset.i18n = group.dataset.settingsLabel;
      option.textContent = button.textContent;
      select.append(option);
      button.addEventListener('click', () => activate(group.dataset.settingsGroup));
      return button;
    });
    function activate(key) {
      groups.forEach((group, index) => {
        const active = group.dataset.settingsGroup === key;
        group.hidden = !active;
        buttons[index].setAttribute('aria-pressed', String(active));
      });
      select.value = key;
    }
    select.addEventListener('change', () => activate(select.value));
    const initial = groups.find(group => group.dataset.settingsGroup === root.dataset.settingsInitial) || groups[0];
    activate(initial.dataset.settingsGroup);
    root.classList.add('settings-ready');
    // Opt-in: horizontal categories collapse when their actual labels no longer fit.
    if (root.dataset.settingsLayout === 'tabs') {
      const navigation = root.querySelector('.settings-category-nav');
      const updateLayout = () => {
        if (!navigation.clientWidth) return; // Main page is currently hidden.
        const compact = list.scrollWidth > navigation.clientWidth + 1;
        root.classList.toggle('settings-compact', compact);
        list.setAttribute('aria-hidden', String(compact));
      };
      new ResizeObserver(updateLayout).observe(navigation);
      new MutationObserver(updateLayout).observe(list, { childList: true, characterData: true, subtree: true });
      updateLayout();
    }
  });
}
