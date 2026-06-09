from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _

from allauth.account.forms import (
    AddEmailForm,
    ChangeEmailForm,
    ChangePasswordForm,
    ConfirmEmailVerificationCodeForm,
    LoginForm,
    ReauthenticateForm,
    ResetPasswordForm,
    ResetPasswordKeyForm,
    SetPasswordForm,
    SignupForm,
)
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit

from .models import User


def _apply_auth_field_styles(form):
    for name, field in form.fields.items():
        if field.widget.is_hidden:
            continue
        if isinstance(field.widget, forms.CheckboxInput):
            css_class = 'form-check-input'
        else:
            css_class = 'form-control form-control-lg'
        if form.is_bound and form.errors.get(name):
            css_class += ' is-invalid'
        field.widget.attrs['class'] = css_class


def _clear_help_text(form):
    for field in form.fields.values():
        field.help_text = ''


class ExperioLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'].label = _('Email')
        self.fields['login'].widget.attrs.update({
            'placeholder': _('you@example.com'),
            'autocomplete': 'email',
            'type': 'email',
            'required': 'required',
        })
        self.fields['password'].widget.attrs.update({
            'placeholder': _('Your password'),
            'autocomplete': 'current-password',
            'required': 'required',
        })
        self.fields['password'].help_text = ''
        if 'remember' in self.fields:
            self.fields['remember'].help_text = ''
        _clear_help_text(self)
        _apply_auth_field_styles(self)

    def clean_login(self):
        login = self.cleaned_data.get('login', '').strip()
        if not login:
            raise ValidationError(_('Please enter your email address.'))
        try:
            validate_email(login)
        except ValidationError:
            raise ValidationError(_('Please enter a valid email address.'))
        return login


class ExperioSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'email' in self.fields:
            self.fields['email'].label = _('Email')
            self.fields['email'].widget.attrs.update({
                'placeholder': _('you@example.com'),
                'autocomplete': 'email',
                'type': 'email',
                'required': 'required',
            })
        if 'password1' in self.fields:
            self.fields['password1'].label = _('Password')
            self.fields['password1'].widget.attrs.update({
                'placeholder': _('Create a password'),
                'autocomplete': 'new-password',
                'minlength': '8',
                'required': 'required',
            })
        if 'password2' in self.fields:
            self.fields['password2'].label = _('Confirm password')
            self.fields['password2'].widget.attrs.update({
                'placeholder': _('Repeat your password'),
                'autocomplete': 'new-password',
                'minlength': '8',
                'required': 'required',
            })
        _clear_help_text(self)
        _apply_auth_field_styles(self)

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if not email:
            raise ValidationError(_('Please enter your email address.'))
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError(_('Please enter a valid email address.'))
        return email


class ExperioResetPasswordForm(ResetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].label = _('Email')
        self.fields['email'].widget.attrs.update({
            'placeholder': _('you@example.com'),
            'autocomplete': 'email',
            'type': 'email',
            'required': 'required',
        })
        _clear_help_text(self)
        _apply_auth_field_styles(self)


class ExperioResetPasswordKeyForm(ResetPasswordKeyForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = _('New password')
        self.fields['password2'].label = _('Confirm new password')
        for name in ('password1', 'password2'):
            self.fields[name].widget.attrs.update({
                'autocomplete': 'new-password',
                'minlength': '8',
                'required': 'required',
            })
        _clear_help_text(self)
        _apply_auth_field_styles(self)


class ExperioReauthenticateForm(ReauthenticateForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].label = _('Password')
        self.fields['password'].widget.attrs.update({
            'placeholder': _('Your password'),
            'autocomplete': 'current-password',
            'required': 'required',
        })
        _clear_help_text(self)
        _apply_auth_field_styles(self)


class ExperioSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = _('Password')
        self.fields['password2'].label = _('Confirm password')
        for name in ('password1', 'password2'):
            self.fields[name].widget.attrs.update({
                'minlength': '8',
                'required': 'required',
            })
        _clear_help_text(self)
        _apply_auth_field_styles(self)


class ExperioChangeEmailForm(ChangeEmailForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'email' in self.fields:
            self.fields['email'].label = _('Email')
            self.fields['email'].widget.attrs.update({
                'placeholder': _('you@example.com'),
                'type': 'email',
                'required': 'required',
            })
        _clear_help_text(self)
        _apply_auth_field_styles(self)


class ExperioAddEmailForm(AddEmailForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'email' in self.fields:
            self.fields['email'].label = _('Email')
            self.fields['email'].widget.attrs.update({
                'placeholder': _('you@example.com'),
                'type': 'email',
                'required': 'required',
            })
        _clear_help_text(self)
        _apply_auth_field_styles(self)


class ExperioConfirmEmailVerificationCodeForm(ConfirmEmailVerificationCodeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'code' in self.fields:
            self.fields['code'].label = _('Verification code')
            self.fields['code'].widget.attrs.update({
                'placeholder': _('Enter code'),
                'required': 'required',
                'autocomplete': 'one-time-code',
            })
        _clear_help_text(self)
        _apply_auth_field_styles(self)


class ExperioChangePasswordForm(ChangePasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['oldpassword'].label = _('Current password')
        self.fields['password1'].label = _('New password')
        self.fields['password2'].label = _('Confirm new password')
        for name in ('oldpassword', 'password1', 'password2'):
            self.fields[name].widget.attrs.update({
                'minlength': '8',
                'required': 'required',
            })
        _clear_help_text(self)
        _apply_auth_field_styles(self)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'avatar']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='col-md-6'),
                Column('last_name', css_class='col-md-6'),
            ),
            'phone',
            'avatar',
            Submit('submit', _('Save Profile'), css_class='btn btn-primary'),
        )
