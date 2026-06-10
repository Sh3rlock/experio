from django import forms
from django.utils.translation import gettext_lazy as _

class PartnerApplicationForm(forms.Form):
    class BusinessCategory:
        EXPERIENCE = 'experience'
        TRAVEL = 'travel'
        GASTRO = 'gastro'
        HEALTH = 'health'
        BEAUTY = 'beauty'
        COURSE = 'course'
        OTHER = 'other'

        @classmethod
        def choices(cls):
            return [
                (cls.EXPERIENCE, _('Experience')),
                (cls.TRAVEL, _('Travel')),
                (cls.GASTRO, _('Gastro')),
                (cls.HEALTH, _('Health')),
                (cls.BEAUTY, _('Beauty')),
                (cls.COURSE, _('Course')),
                (cls.OTHER, _('Other')),
            ]

    class VoucherInterest:
        YES = 'yes'
        MAYBE = 'maybe'
        NOT_SURE = 'not_sure'

        @classmethod
        def choices(cls):
            return [
                (cls.YES, _('Yes')),
                (cls.MAYBE, _('Maybe, I would like more information')),
                (cls.NOT_SURE, _('Not sure yet')),
            ]

    class VoucherType:
        FIXED_VALUE = 'fixed_value'
        EXPERIENCE = 'experience_packages'
        SPECIAL_OFFERS = 'special_offers'
        SEASONAL = 'seasonal_promotions'
        CUSTOM = 'custom_vouchers'

        @classmethod
        def choices(cls):
            return [
                (cls.FIXED_VALUE, _('Fixed value vouchers (e.g. 50, 100, 200, 500 RON)')),
                (cls.EXPERIENCE, _('Experience packages')),
                (cls.SPECIAL_OFFERS, _('Special offers')),
                (cls.SEASONAL, _('Seasonal promotions')),
                (cls.CUSTOM, _('Custom vouchers')),
            ]

        @classmethod
        def label_for(cls, value):
            return dict(cls.choices()).get(value, value)

    business_name = forms.CharField(
        label=_('Business Name'),
        max_length=255,
    )
    business_category = forms.ChoiceField(
        label=_('Business Category'),
        choices=BusinessCategory.choices,
        widget=forms.Select(attrs={'class': 'landing-field landing-field--select'}),
    )
    website_or_social = forms.CharField(
        label=_('Website or Facebook Page'),
        max_length=255,
        required=False,
    )
    business_address = forms.CharField(
        label=_('Business Address - City'),
        max_length=255,
    )
    contact_person = forms.CharField(
        label=_('Contact Person'),
        max_length=255,
    )
    email = forms.EmailField(label=_('Email Address'))
    phone = forms.CharField(label=_('Phone Number'), max_length=20)
    description = forms.CharField(
        label=_('Brief Description'),
        help_text=_('Tell us about your business and what makes it special.'),
        widget=forms.Textarea(attrs={'rows': 4}),
    )
    voucher_interest = forms.ChoiceField(
        label=_('Would you be interested in selling gift vouchers online?'),
        choices=VoucherInterest.choices,
        widget=forms.RadioSelect,
    )
    voucher_types = forms.MultipleChoiceField(
        label=_('What types of vouchers would you like to offer?'),
        choices=VoucherType.choices,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        text_widgets = (forms.TextInput, forms.EmailInput, forms.Textarea)
        for name, field in self.fields.items():
            if isinstance(field.widget, text_widgets):
                field.widget.attrs.setdefault('class', 'landing-field')
            elif isinstance(field.widget, forms.RadioSelect):
                field.widget.attrs.update({'class': 'landing-choice-input'})
            elif isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs.update({'class': 'landing-choice-input'})

    def category_label(self):
        if not self.is_bound and not self.data:
            return ''
        value = self.cleaned_data.get('business_category') if self.is_valid() else self.data.get('business_category')
        return dict(self.BusinessCategory.choices()).get(value, value)

    def interest_label(self):
        if not self.is_bound and not self.data:
            return ''
        value = self.cleaned_data.get('voucher_interest') if self.is_valid() else self.data.get('voucher_interest')
        return dict(self.VoucherInterest.choices()).get(value, value)

    def voucher_type_labels(self):
        values = []
        if self.is_valid():
            values = self.cleaned_data.get('voucher_types', [])
        elif self.data:
            values = self.data.getlist('voucher_types')
        return [self.VoucherType.label_for(v) for v in values]
