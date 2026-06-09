from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from vouchers.models import Voucher


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        PAID = 'paid', _('Paid')
        FAILED = 'failed', _('Failed')
        REFUNDED = 'refunded', _('Refunded')

    class Provider(models.TextChoices):
        STRIPE = 'stripe', _('Stripe')

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    voucher = models.OneToOneField(Voucher, on_delete=models.CASCADE, related_name='payment', null=True, blank=True)
    offer = models.ForeignKey('offers.Offer', on_delete=models.PROTECT, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='RON')
    provider = models.CharField(max_length=20, choices=Provider.choices, default=Provider.STRIPE)
    provider_payment_id = models.CharField(max_length=255, blank=True)
    provider_session_id = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Payment {self.id} - {self.status}'
