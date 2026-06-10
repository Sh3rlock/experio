(function () {
    const form = document.querySelector('.landing-partner-form');
    const loader = document.getElementById('landing-form-loader');
    if (!form || !loader) return;

    let submitted = false;

    form.addEventListener('submit', (event) => {
        if (submitted) {
            event.preventDefault();
            return;
        }

        submitted = true;
        form.classList.add('is-submitting');
        loader.hidden = false;
        loader.setAttribute('aria-busy', 'true');
    });
})();
