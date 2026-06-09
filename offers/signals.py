from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from notifications.services import send_offer_approved

from .models import Offer


@receiver(pre_save, sender=Offer)
def offer_status_changed(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = Offer.objects.get(pk=instance.pk)
    except Offer.DoesNotExist:
        return
    if old.status != Offer.Status.APPROVED and instance.status == Offer.Status.APPROVED:
        instance._send_approval_email = True


@receiver(post_save, sender=Offer)
def offer_approved_notify(sender, instance, **kwargs):
    if getattr(instance, '_send_approval_email', False):
        send_offer_approved(instance)
