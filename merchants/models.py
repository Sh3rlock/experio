from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Merchant(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        APPROVED = 'approved', _('Approved')
        REJECTED = 'rejected', _('Rejected')

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='merchant')
    business_name = models.CharField(_('Business name'), max_length=255)
    description = models.TextField(_('Description'), blank=True)
    logo = models.ImageField(_('Logo'), upload_to='merchants/logos/', blank=True, null=True)
    website = models.URLField(_('Website'), blank=True)
    phone = models.CharField(_('Phone'), max_length=20, blank=True)
    email = models.EmailField(_('Email'), blank=True)
    address = models.CharField(_('Address'), max_length=255, blank=True)
    city = models.CharField(_('City'), max_length=100, blank=True)
    county = models.CharField(_('County'), max_length=100, blank=True)
    country = models.CharField(_('Country'), max_length=100, default='Romania')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=15.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.business_name

    @property
    def is_approved(self):
        return self.status == self.Status.APPROVED


class Commission(models.Model):
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='commissions')
    voucher = models.OneToOneField('vouchers.Voucher', on_delete=models.CASCADE, related_name='commission')
    sale_amount = models.DecimalField(max_digits=10, decimal_places=2)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2)
    merchant_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Commission {self.commission_amount} for {self.merchant}'
