from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.shortcuts import redirect, render

from core.permissions import merchant_required
from merchants.forms import MerchantProfileForm, MerchantRegistrationForm
from merchants.models import Merchant
from notifications.services import send_merchant_registration
from vouchers.models import Voucher
from vouchers.services import redeem_voucher


@login_required
def register_merchant(request):
    if hasattr(request.user, 'merchant'):
        return redirect('dashboard:merchant')
    if request.method == 'POST':
        form = MerchantRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            merchant = form.save(commit=False)
            merchant.user = request.user
            merchant.save()
            request.user.is_merchant = True
            request.user.save(update_fields=['is_merchant'])
            messages.success(request, _('Business registered! Awaiting admin approval.'))
            return redirect('merchants:pending')
    else:
        form = MerchantRegistrationForm()
    return render(request, 'merchants/register.html', {'form': form})


@login_required
def pending(request):
    if not hasattr(request.user, 'merchant'):
        return redirect('merchants:register')
    return render(request, 'merchants/pending.html', {'merchant': request.user.merchant})


@merchant_required
def redeem_page(request):
    result = None
    error = None
    if request.method == 'POST':
        code = request.POST.get('voucher_code', '').strip()
        voucher, error = redeem_voucher(code, request.user)
        if voucher:
            from notifications.services import send_voucher_redeemed
            send_voucher_redeemed(voucher)
            result = voucher
            messages.success(
                request,
                _('Voucher %(code)s redeemed successfully!') % {'code': voucher.voucher_code},
            )
        else:
            messages.error(request, error)
    return render(request, 'merchants/redeem.html', {'result': result, 'error': error})


@merchant_required
def sales(request):
    merchant = request.user.merchant
    vouchers = Voucher.objects.filter(offer__merchant=merchant).select_related('offer', 'customer')
    return render(request, 'merchants/sales.html', {'vouchers': vouchers})
