from django.core.management.base import BaseCommand
from django.utils.text import slugify

from offers.models import Category

DEFAULT_CATEGORIES = [
    ('Restaurant', 'bi-cup-hot'),
    ('Spa', 'bi-droplet'),
    ('Beauty', 'bi-stars'),
    ('Fitness', 'bi-heart-pulse'),
    ('Travel', 'bi-airplane'),
    ('Adventure', 'bi-compass'),
    ('Family', 'bi-people'),
    ('Courses', 'bi-book'),
    ('Events', 'bi-calendar-event'),
    ('Gift Cards', 'bi-gift'),
]


class Command(BaseCommand):
    help = 'Seed default offer categories'

    def handle(self, *args, **options):
        created = 0
        for name, icon in DEFAULT_CATEGORIES:
            _, was_created = Category.objects.get_or_create(
                slug=slugify(name),
                defaults={'name': name, 'icon': icon},
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f'Seeded {created} new categories.'))
