from django import forms
from django.utils.translation import gettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit

from .models import Merchant


class MerchantRegistrationForm(forms.ModelForm):
    class Meta:
        model = Merchant
        fields = [
            'business_name', 'description', 'logo', 'website', 'phone', 'email',
            'address', 'city', 'county', 'country',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound and not self.initial.get('country') and not getattr(self.instance, 'pk', None):
            self.fields['country'].initial = _('Romania')
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'business_name', 'description', 'logo', 'website',
            'phone', 'email', 'address', 'city', 'county', 'country',
            Submit('submit', _('Register Business'), css_class='btn btn-primary'),
        )


class MerchantProfileForm(forms.ModelForm):
    class Meta:
        model = Merchant
        fields = [
            'business_name', 'description', 'logo', 'website', 'phone', 'email',
            'address', 'city', 'county', 'country',
        ]
