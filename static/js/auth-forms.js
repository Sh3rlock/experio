(function () {
    function getMessages(form) {
        return {
            valueMissing: form.dataset.msgRequired || 'This field is required.',
            typeMismatch: form.dataset.msgEmail || 'Please enter a valid email address.',
            tooShort: form.dataset.msgMinlength || 'Please use at least {min} characters.',
            patternMismatch: 'Please match the requested format.',
            passwordMatch: form.dataset.msgPasswordMatch || 'Passwords do not match.',
        };
    }

    function getMessage(input, messages) {
        const validity = input.validity;
        if (validity.valueMissing) return messages.valueMissing;
        if (validity.typeMismatch && input.type === 'email') return messages.typeMismatch;
        if (validity.tooShort) return messages.tooShort.replace('{min}', input.minLength);
        if (validity.patternMismatch) return messages.patternMismatch;
        return input.validationMessage;
    }

    function setFieldState(input, form, messages, show) {
        const field = input.closest('.auth-field');
        if (!field || field.classList.contains('auth-field--checkbox')) return;

        const feedback = field.querySelector('.js-field-error');
        const hasServerError = field.querySelector('.invalid-feedback.d-block');
        const invalid = !input.checkValidity();

        if (!show) {
            if (!hasServerError) input.classList.remove('is-invalid', 'is-valid');
            if (feedback) feedback.textContent = '';
            return;
        }

        if (!hasServerError) input.classList.toggle('is-invalid', invalid);
        if (feedback && !hasServerError) {
            feedback.textContent = invalid ? getMessage(input, messages) : '';
        }
    }

    document.querySelectorAll('.auth-form[novalidate]').forEach((form) => {
        const messages = getMessages(form);
        const inputs = form.querySelectorAll('.form-control');
        const password1 = form.querySelector('[name="password1"]');
        const password2 = form.querySelector('[name="password2"]');

        function validatePasswordMatch() {
            if (!password1 || !password2) return true;
            const field = password2.closest('.auth-field');
            const feedback = field && field.querySelector('.js-field-error');
            const hasServerError = field && field.querySelector('.invalid-feedback.d-block');
            const mismatch = password2.value && password1.value !== password2.value;

            if (!hasServerError) {
                password2.classList.toggle('is-invalid', mismatch);
                if (feedback) feedback.textContent = mismatch ? messages.passwordMatch : '';
            }
            return !mismatch;
        }

        inputs.forEach((input) => {
            input.addEventListener('blur', () => {
                if (input.value.trim() || form.classList.contains('was-validated')) {
                    setFieldState(input, form, messages, true);
                }
            });
            input.addEventListener('input', () => {
                if (form.classList.contains('was-validated') || input.classList.contains('is-invalid')) {
                    setFieldState(input, form, messages, true);
                }
            });
        });

        if (password2) {
            password2.addEventListener('input', validatePasswordMatch);
            if (password1) password1.addEventListener('input', validatePasswordMatch);
        }

        form.addEventListener('submit', (event) => {
            form.classList.add('was-validated');
            let valid = true;

            inputs.forEach((input) => {
                setFieldState(input, form, messages, true);
                if (!input.checkValidity()) valid = false;
            });

            if (!validatePasswordMatch()) valid = false;

            if (!valid) {
                event.preventDefault();
                event.stopPropagation();
                const firstInvalid = form.querySelector('.form-control.is-invalid');
                if (firstInvalid) firstInvalid.focus();
            }
        });
    });
})();
