from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext as _


def merchant_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        if not hasattr(request.user, 'merchant'):
            messages.error(request, _('You need a merchant account to access this page.'))
            return redirect('core:home')
        if not request.user.merchant.is_approved and not request.user.is_staff:
            messages.warning(request, _('Your merchant account is pending approval.'))
            return redirect('merchants:pending')
        return view_func(request, *args, **kwargs)
    return wrapper


def customer_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        return view_func(request, *args, **kwargs)
    return wrapper


def staff_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            messages.error(request, _('Admin access required.'))
            return redirect('core:home')
        return view_func(request, *args, **kwargs)
    return wrapper
