from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from merchants.models import Merchant


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True, help_text='Bootstrap icon class e.g. bi-cup-hot')
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Offer(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', _('Draft')
        PENDING = 'pending', _('Pending')
        APPROVED = 'approved', _('Approved')
        REJECTED = 'rejected', _('Rejected')
        EXPIRED = 'expired', _('Expired')

    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='offers')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='offers')
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    short_description = models.CharField(max_length=500)
    description = models.TextField()
    terms_and_conditions = models.TextField(blank=True)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.PositiveIntegerField(default=0)
    quantity_available = models.PositiveIntegerField(default=0)
    voucher_valid_until = models.DateField()
    featured = models.BooleanField(default=False)
    display_rating = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)
    highlight_tag = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = [('merchant', 'slug')]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.original_price and self.sale_price:
            if self.original_price > 0:
                self.discount_percentage = int(
                    ((self.original_price - self.sale_price) / self.original_price) * 100
                )
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('offers:detail', kwargs={'slug': self.slug})

    @property
    def savings(self):
        return self.original_price - self.sale_price

    @property
    def is_purchasable(self):
        return (
            self.status == self.Status.APPROVED
            and self.quantity_available > 0
            and self.merchant.is_approved
        )

    @property
    def featured_image(self):
        return self.images.filter(sort_order=0).first() or self.images.first()


class OfferImage(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='offers/')
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return f'Image for {self.offer.title}'
