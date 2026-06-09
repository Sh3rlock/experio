from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit

from core.permissions import merchant_required
from offers.forms import (
    IMAGE_FORMSET_PREFIX,
    OfferForm,
    bind_image_formset,
    image_formset_counts,
)
from offers.models import Offer
from offers.selectors import filter_offers, get_approved_offers, get_related_offers
from payments.services import create_checkout_session


def offer_list(request):
    qs = filter_offers(
        category_slug=request.GET.get('category'),
        city=request.GET.get('city'),
        min_price=request.GET.get('min_price'),
        max_price=request.GET.get('max_price'),
        min_discount=request.GET.get('min_discount'),
        max_discount=request.GET.get('max_discount'),
        search=request.GET.get('q'),
        sort=request.GET.get('sort', 'newest'),
    )
    paginator = Paginator(qs, 12)
    page = paginator.get_page(request.GET.get('page'))
    from offers.models import Category
    return render(request, 'offers/list.html', {
        'offers': page,
        'categories': Category.objects.all(),
        'filters': request.GET,
    })


def offer_detail(request, slug):
    offer = get_object_or_404(
        get_approved_offers().select_related('merchant', 'category').prefetch_related('images'),
        slug=slug,
    )
    return render(request, 'offers/detail.html', {
        'offer': offer,
        'related_offers': get_related_offers(offer),
    })


@login_required
@ratelimit(key='user', rate='10/m', method='POST', block=True)
@require_POST
def buy_offer(request, slug):
    offer = get_object_or_404(get_approved_offers(), slug=slug)
    if not offer.is_purchasable:
        messages.error(request, _('This offer is no longer available.'))
        return redirect('offers:detail', slug=slug)
    checkout_url = create_checkout_session(offer, request.user)
    return redirect(checkout_url)


@merchant_required
def merchant_offer_list(request):
    offers = Offer.objects.filter(merchant=request.user.merchant)
    return render(request, 'offers/merchant_list.html', {'offers': offers})


def _merchant_form_context(form, formset, title, offer=None):
    fs_initial, fs_total = image_formset_counts(offer)
    return {
        'form': form,
        'formset': formset,
        'title': title,
        'offer': offer,
        'fs_prefix': IMAGE_FORMSET_PREFIX,
        'fs_initial': fs_initial,
        'fs_total': fs_total,
    }


@merchant_required
def merchant_offer_create(request):
    merchant = request.user.merchant
    if request.method == 'POST':
        form = OfferForm(request.POST)
        formset = bind_image_formset(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            offer = form.save(commit=False)
            offer.merchant = merchant
            offer.status = Offer.Status.PENDING
            offer.save()
            formset.instance = offer
            formset.save()
            messages.success(request, _('Offer submitted for approval.'))
            return redirect('offers:merchant_list')
    else:
        form = OfferForm()
        formset = bind_image_formset()
    return render(
        request,
        'offers/merchant_form.html',
        _merchant_form_context(form, formset, _('Create Offer')),
    )


@merchant_required
def merchant_offer_edit(request, pk):
    offer = get_object_or_404(Offer, pk=pk, merchant=request.user.merchant)
    if request.method == 'POST':
        form = OfferForm(request.POST, instance=offer)
        formset = bind_image_formset(request.POST, request.FILES, instance=offer)
        if form.is_valid() and formset.is_valid():
            offer = form.save(commit=False)
            if offer.status == Offer.Status.APPROVED:
                offer.status = Offer.Status.PENDING
            offer.save()
            formset.save()
            messages.success(request, _('Offer updated.'))
            return redirect('offers:merchant_list')
    else:
        form = OfferForm(instance=offer)
        formset = bind_image_formset(instance=offer)
    return render(
        request,
        'offers/merchant_form.html',
        _merchant_form_context(form, formset, _('Edit Offer'), offer=offer),
    )


@merchant_required
def merchant_offer_preview(request, pk):
    offer = get_object_or_404(Offer, pk=pk, merchant=request.user.merchant)
    return render(request, 'offers/detail.html', {'offer': offer, 'preview': True})


@merchant_required
@require_POST
def merchant_offer_delete(request, pk):
    offer = get_object_or_404(Offer, pk=pk, merchant=request.user.merchant)
    offer.delete()
    messages.success(request, _('Offer deleted.'))
    return redirect('offers:merchant_list')
