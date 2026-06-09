from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from offers.models import Offer


class Voucher(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', _('Active')
        REDEEMED = 'redeemed', _('Redeemed')
        EXPIRED = 'expired', _('Expired')
        CANCELLED = 'cancelled', _('Cancelled')

    offer = models.ForeignKey(Offer, on_delete=models.PROTECT, related_name='vouchers')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vouchers')
    voucher_code = models.CharField(max_length=20, unique=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    qr_image = models.ImageField(upload_to='vouchers/qr/', blank=True, null=True)
    pdf_file = models.FileField(upload_to='vouchers/pdf/', blank=True, null=True)
    purchased_at = models.DateTimeField(auto_now_add=True)
    redeemed_at = models.DateTimeField(null=True, blank=True)
    redeemed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='redeemed_vouchers',
    )
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ['-purchased_at']

    def __str__(self):
        return self.voucher_code

    @property
    def is_redeemable(self):
        from django.utils import timezone
        return (
            self.status == self.Status.ACTIVE
            and self.expires_at > timezone.now()
        )
