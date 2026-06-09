from django import forms
from django.forms import inlineformset_factory

from .models import Offer, OfferImage

IMAGE_FORMSET_PREFIX = 'offer_images'
IMAGE_FORMSET_EXTRA = 3


class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = [
            'category', 'title', 'short_description', 'description', 'terms_and_conditions',
            'original_price', 'sale_price', 'quantity_available', 'voucher_valid_until',
            'meta_title', 'meta_description',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'terms_and_conditions': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'short_description': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'voucher_valid_until': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'original_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'sale_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'quantity_available': forms.NumberInput(attrs={'class': 'form-control'}),
            'meta_title': forms.TextInput(attrs={'class': 'form-control'}),
            'meta_description': forms.TextInput(attrs={'class': 'form-control'}),
        }


class OfferImageForm(forms.ModelForm):
    class Meta:
        model = OfferImage
        fields = ('image', 'sort_order')
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }


OfferImageFormSet = inlineformset_factory(
    Offer,
    OfferImage,
    form=OfferImageForm,
    fields=('image', 'sort_order'),
    extra=IMAGE_FORMSET_EXTRA,
    can_delete=True,
)


def image_formset_counts(offer=None):
    """Stable management-form counts (safe when management form validation failed)."""
    initial = offer.images.count() if offer and offer.pk else 0
    total = initial + IMAGE_FORMSET_EXTRA
    return initial, total


def bind_image_formset(data=None, files=None, instance=None):
    """Bind formset; repair missing management fields from broken or truncated POSTs."""
    prefix = IMAGE_FORMSET_PREFIX
    initial, total = image_formset_counts(instance)

    if data is not None:
        data = data.copy()
        if data.get(f'{prefix}-TOTAL_FORMS') in (None, ''):
            data[f'{prefix}-TOTAL_FORMS'] = str(total)
            data[f'{prefix}-INITIAL_FORMS'] = str(initial)
            data[f'{prefix}-MIN_NUM_FORMS'] = '0'
            data[f'{prefix}-MAX_NUM_FORMS'] = '1000'

    return OfferImageFormSet(data, files, instance=instance, prefix=IMAGE_FORMSET_PREFIX)
