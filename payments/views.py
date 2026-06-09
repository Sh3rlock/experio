import json

import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from payments.models import Payment
from payments.services import (
    fulfill_payment,
    handle_checkout_completed,
    handle_payment_failed,
    handle_refund,
)


@login_required
def payment_success(request):
    session_id = request.GET.get('session_id')
    mock = request.GET.get('mock')
    payment_id = request.GET.get('payment_id')

    if mock and payment_id:
        payment = get_object_or_404(Payment, pk=payment_id, customer=request.user)
        return render(request, 'payments/success.html', {'voucher': payment.voucher})

    if session_id and settings.STRIPE_SECRET_KEY:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.retrieve(session_id)
        payment_id = session.metadata.get('payment_id')
        if payment_id:
            voucher = fulfill_payment(payment_id, session.payment_intent)
            return render(request, 'payments/success.html', {'voucher': voucher})

    return render(request, 'payments/success.html', {})


@login_required
def download_voucher(request, pk):
    from vouchers.models import Voucher
    v = get_object_or_404(Voucher, pk=pk, customer=request.user)
    if not v.pdf_file:
        from vouchers.services import generate_voucher_pdf
        generate_voucher_pdf(v)
    from django.http import FileResponse
    return FileResponse(v.pdf_file.open('rb'), as_attachment=True, filename=f'voucher_{v.voucher_code}.pdf')


@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    if settings.STRIPE_WEBHOOK_SECRET:
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except (ValueError, stripe.error.SignatureVerificationError):
            return HttpResponseBadRequest('Invalid payload')
    else:
        event = json.loads(payload)

    event_type = event['type'] if isinstance(event, dict) else event.type
    data = event['data']['object'] if isinstance(event, dict) else event.data.object

    if event_type == 'checkout.session.completed':
        handle_checkout_completed(data if isinstance(data, dict) else data.to_dict())
    elif event_type == 'payment_intent.payment_failed':
        handle_payment_failed(data if isinstance(data, dict) else data.to_dict())
    elif event_type in ('charge.refunded', 'charge.refund.updated'):
        handle_refund(data if isinstance(data, dict) else data.to_dict())

    return HttpResponse(status=200)
