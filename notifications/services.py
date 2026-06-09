from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.html import strip_tags
from django.utils.translation import gettext as _


def _user_language(user):
    if user is None:
        return settings.LANGUAGE_CODE
    return getattr(user, 'language', None) or settings.LANGUAGE_CODE


def _send_email(subject, template_name, context, to_email, user=None):
    with translation.override(_user_language(user)):
        html_content = render_to_string(f'emails/{template_name}', context)
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(
            subject=str(subject),
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        msg.attach_alternative(html_content, 'text/html')
        if context.get('attachment'):
            msg.attach(*context['attachment'])
        msg.send(fail_silently=False)


def send_welcome_customer(user):
    _send_email(
        _('Welcome to Experio!'),
        'welcome_customer.html',
        {'user': user, 'site_url': settings.SITE_URL},
        user.email,
        user=user,
    )


def send_merchant_registration(merchant):
    user = merchant.user
    _send_email(
        _('Merchant Registration Received'),
        'merchant_registration.html',
        {'merchant': merchant, 'site_url': settings.SITE_URL},
        user.email,
        user=user,
    )


def send_merchant_approved(merchant):
    user = merchant.user
    _send_email(
        _('Your Merchant Account is Approved!'),
        'merchant_approved.html',
        {'merchant': merchant, 'site_url': settings.SITE_URL},
        user.email,
        user=user,
    )


def send_offer_approved(offer):
    user = offer.merchant.user
    _send_email(
        _('Your Offer "%(title)s" is Live!') % {'title': offer.title},
        'offer_approved.html',
        {'offer': offer, 'site_url': settings.SITE_URL},
        user.email,
        user=user,
    )


def send_voucher_purchased(voucher):
    user = voucher.customer
    attachment = None
    if voucher.pdf_file:
        voucher.pdf_file.open('rb')
        attachment = (f'voucher_{voucher.voucher_code}.pdf', voucher.pdf_file.read(), 'application/pdf')
        voucher.pdf_file.close()
    _send_email(
        _('Your Experio Voucher - %(code)s') % {'code': voucher.voucher_code},
        'voucher_purchased.html',
        {'voucher': voucher, 'site_url': settings.SITE_URL, 'attachment': attachment},
        user.email,
        user=user,
    )


def send_voucher_redeemed(voucher):
    user = voucher.customer
    _send_email(
        _('Voucher Redeemed - %(code)s') % {'code': voucher.voucher_code},
        'voucher_redeemed.html',
        {'voucher': voucher, 'site_url': settings.SITE_URL},
        user.email,
        user=user,
    )


def send_payment_failed(payment):
    user = payment.customer
    _send_email(
        _('Payment Failed - Experio'),
        'payment_failed.html',
        {'payment': payment, 'site_url': settings.SITE_URL},
        user.email,
        user=user,
    )


def _partner_application_notify_email():
    if settings.PARTNER_APPLICATION_NOTIFY_EMAIL:
        return settings.PARTNER_APPLICATION_NOTIFY_EMAIL

    from django.contrib.auth import get_user_model

    return (
        get_user_model().objects.filter(is_superuser=True, is_active=True)
        .values_list('email', flat=True)
        .first()
    ) or settings.DEFAULT_FROM_EMAIL


def send_partner_application(application):
    _send_email(
        _('New founding partner application: %(business)s') % {'business': application['business_name']},
        'partner_application.html',
        {'application': application, 'site_url': settings.SITE_URL},
        _partner_application_notify_email(),
    )
