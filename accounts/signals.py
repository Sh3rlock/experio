from allauth.account.signals import user_signed_up
from django.dispatch import receiver

from notifications.services import send_welcome_customer


@receiver(user_signed_up)
def on_user_signed_up(request, user, **kwargs):
    send_welcome_customer(user)
