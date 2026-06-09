from django.conf import settings

from offers.models import Category
from offers.selectors import get_popular_categories


def site_context(request):
    return {
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
        'popular_categories': get_popular_categories(limit=6),
        'nav_categories': Category.objects.all().order_by('name')[:10],
    }
