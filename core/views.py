from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
from django.views.i18n import set_language as django_set_language

from core.forms import PartnerApplicationForm
from notifications.services import send_partner_application
from offers.selectors import (
    get_featured_offers,
    get_newest_offers,
    get_popular_categories,
    get_top_discounts,
)


def health(request):
    return HttpResponse('ok', content_type='text/plain')


@require_POST
def set_language(request):
    response = django_set_language(request)
    lang = request.POST.get('language', '')
    if request.user.is_authenticated and lang in dict(settings.LANGUAGES):
        get_user_model().objects.filter(pk=request.user.pk).update(language=lang)
    return response


def landing(request):
    application_form = PartnerApplicationForm()

    if request.method == 'POST' and 'submit_application' in request.POST:
        application_form = PartnerApplicationForm(request.POST)
        if application_form.is_valid():
            data = application_form.cleaned_data.copy()
            data['business_category_display'] = application_form.category_label()
            data['voucher_interest_display'] = application_form.interest_label()
            data['voucher_types_display'] = application_form.voucher_type_labels()
            send_partner_application(data)
            messages.success(
                request,
                _(
                    'Thank you for your interest! We will contact you within 2 business '
                    'days to discuss how we can help your business reach new customers '
                    'through digital gift vouchers.'
                ),
            )
            return redirect('core:landing#register')

    return render(request, 'core/landing.html', {
        'application_form': application_form,
        'has_merchant': request.user.is_authenticated and hasattr(request.user, 'merchant'),
    })


def home(request):
    carousel_offers = list(get_featured_offers(limit=6))
    if not carousel_offers:
        carousel_offers = list(get_newest_offers(limit=6))
    carousel_ids = {o.pk for o in carousel_offers}
    grid_offers = [
        o for o in list(get_newest_offers(limit=12)) + list(get_top_discounts(limit=12))
        if o.pk not in carousel_ids
    ][:8]
    return render(request, 'core/home.html', {
        'carousel_offers': carousel_offers,
        'grid_offers': grid_offers,
        'categories': get_popular_categories(),
    })
