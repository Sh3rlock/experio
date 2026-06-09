from decimal import Decimal

import stripe
from django.conf import settings
from django.db import transaction

from notifications.services import send_payment_failed, send_voucher_purchased
from payments.models import Payment
from vouchers.services import create_voucher

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(offer, customer):
    payment = Payment.objects.create(
        customer=customer,
        offer=offer,
        amount=offer.sale_price,
        currency='RON',
        status=Payment.Status.PENDING,
    )

    if not settings.STRIPE_SECRET_KEY:
        return _mock_checkout(payment, offer, customer)

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        mode='payment',
        customer_email=customer.email,
        line_items=[{
            'price_data': {
                'currency': 'ron',
                'unit_amount': int(offer.sale_price * 100),
                'product_data': {
                    'name': offer.title,
                    'description': offer.short_description[:500],
                },
            },
            'quantity': 1,
        }],
        metadata={
            'payment_id': str(payment.id),
            'offer_id': str(offer.id),
            'customer_id': str(customer.id),
        },
        success_url=f'{settings.SITE_URL}/payments/success/?session_id={{CHECKOUT_SESSION_ID}}',
        cancel_url=f'{settings.SITE_URL}/offers/{offer.slug}/',
    )
    payment.provider_session_id = session.id
    payment.save(update_fields=['provider_session_id'])
    return session.url


def _mock_checkout(payment, offer, customer):
    """Development fallback when Stripe keys are not configured."""
    with transaction.atomic():
        voucher = create_voucher(offer, customer, offer.sale_price)
        payment.voucher = voucher
        payment.status = Payment.Status.PAID
        payment.provider_payment_id = f'mock_{payment.id}'
        payment.save()
    send_voucher_purchased(voucher)
    return f'{settings.SITE_URL}/payments/success/?mock=1&payment_id={payment.id}'


@transaction.atomic
def fulfill_payment(payment_id, provider_payment_id=None):
    payment = Payment.objects.select_for_update().get(pk=payment_id)
    if payment.status == Payment.Status.PAID:
        return payment.voucher

    offer = payment.offer
    if not offer.is_purchasable:
        payment.status = Payment.Status.FAILED
        payment.save(update_fields=['status'])
        send_payment_failed(payment)
        return None

    voucher = create_voucher(offer, payment.customer, payment.amount)
    payment.voucher = voucher
    payment.status = Payment.Status.PAID
    if provider_payment_id:
        payment.provider_payment_id = provider_payment_id
    payment.save()
    send_voucher_purchased(voucher)
    return voucher


def handle_checkout_completed(session):
    payment_id = session.get('metadata', {}).get('payment_id')
    if not payment_id:
        return
    fulfill_payment(payment_id, session.get('payment_intent', session.get('id')))


def handle_payment_failed(session):
    payment_id = session.get('metadata', {}).get('payment_id')
    if not payment_id:
        return
    payment = Payment.objects.filter(pk=payment_id).first()
    if payment:
        payment.status = Payment.Status.FAILED
        payment.save(update_fields=['status'])
        send_payment_failed(payment)


def handle_refund(charge):
    payment = Payment.objects.filter(provider_payment_id=charge.get('payment_intent', '')).first()
    if payment:
        payment.status = Payment.Status.REFUNDED
        payment.save(update_fields=['status'])
        if payment.voucher:
            payment.voucher.status = payment.voucher.Status.CANCELLED
            payment.voucher.save(update_fields=['status'])
