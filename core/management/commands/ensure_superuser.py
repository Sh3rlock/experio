import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create the default superuser on deploy if it does not exist yet.'

    def handle(self, *args, **options):
        if os.environ.get('CREATE_DEFAULT_SUPERUSER', 'True').lower() in ('false', '0', 'no'):
            self.stdout.write('Skipping default superuser creation (CREATE_DEFAULT_SUPERUSER=False)')
            return

        User = get_user_model()
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'matyas')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', f'{username}@experio.local')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'QweAsd789')

        if User.objects.filter(email=email).exists():
            self.stdout.write(f'Superuser already exists: {email}')
            return

        User.objects.create_superuser(
            email=email,
            password=password,
            first_name=username,
        )
        self.stdout.write(self.style.SUCCESS(f'Created superuser: {email}'))
