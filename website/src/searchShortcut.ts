// "/" focuses the search like on contributors.home-assistant.io. The shortcut of the search plugin compares the Shift
// key exactly, so "/" (Shift+7 on a German keyboard) would only work with one keyboard layout.
if (typeof document !== 'undefined') {
    document.addEventListener('keydown', (event: KeyboardEvent) => {
        if (event.key !== '/' || event.ctrlKey || event.metaKey || event.altKey) {
            return;
        }

        const target: Element | null = event.target instanceof Element ? event.target : null;

        if (target?.closest('input, textarea, select, [contenteditable="true"]')) {
            return;
        }

        const input: HTMLInputElement | null = document.querySelector('.navbar__search-input');

        if (input) {
            event.preventDefault();
            input.focus();
        }
    });
}
