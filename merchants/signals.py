from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from notifications.services import send_merchant_approved, send_merchant_registration

from .models import Merchant


@receiver(post_save, sender=Merchant)
def merchant_created(sender, instance, created, **kwargs):
    if created:
        send_merchant_registration(instance)


@receiver(pre_save, sender=Merchant)
def merchant_status_changed(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = Merchant.objects.get(pk=instance.pk)
    except Merchant.DoesNotExist:
        return
    if old.status != Merchant.Status.APPROVED and instance.status == Merchant.Status.APPROVED:
        instance._send_approval_email = True


@receiver(post_save, sender=Merchant)
def merchant_approved(sender, instance, **kwargs):
    if getattr(instance, '_send_approval_email', False):
        send_merchant_approved(instance)
        instance.user.is_merchant = True
        instance.user.save(update_fields=['is_merchant'])
