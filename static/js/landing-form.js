(function () {
    const form = document.querySelector('.landing-partner-form');
    const loader = document.getElementById('landing-form-loader');
    if (!form || !loader) return;

    form.addEventListener('submit', () => {
        form.classList.add('is-submitting');
        loader.hidden = false;
        loader.setAttribute('aria-busy', 'true');

        form.querySelectorAll('input, select, textarea, button').forEach((field) => {
            field.disabled = true;
        });
    });
})();
