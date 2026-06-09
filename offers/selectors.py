from decimal import Decimal, InvalidOperation

from django.db import connection
from django.db.models import Count, Q

from offers.models import Category, Offer


def get_approved_offers():
    return Offer.objects.filter(
        status=Offer.Status.APPROVED,
        merchant__status='approved',
        quantity_available__gt=0,
    ).select_related('merchant', 'category').prefetch_related('images')


def get_featured_offers(limit=8):
    return get_approved_offers().filter(featured=True)[:limit]


def get_newest_offers(limit=8):
    return get_approved_offers()[:limit]


def get_top_discounts(limit=8):
    return get_approved_offers().order_by('-discount_percentage')[:limit]


def get_popular_categories(limit=10):
    return (
        Category.objects.annotate(offer_count=Count('offers', filter=Q(offers__status=Offer.Status.APPROVED)))
        .filter(offer_count__gt=0)
        .order_by('-offer_count')[:limit]
    )


def _parse_decimal(value):
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return Decimal(text)
    except (InvalidOperation, ValueError):
        return None


def _parse_int(value):
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return int(text)
    except (ValueError, TypeError):
        return None


def filter_offers(
    queryset=None,
    category_slug=None,
    city=None,
    min_price=None,
    max_price=None,
    min_discount=None,
    max_discount=None,
    search=None,
    sort='newest',
):
    qs = queryset or get_approved_offers()

    category_slug = (category_slug or '').strip()
    city = (city or '').strip()
    search = (search or '').strip()

    if category_slug:
        qs = qs.filter(category__slug=category_slug)
    if city:
        qs = qs.filter(merchant__city__icontains=city)

    parsed_min_price = _parse_decimal(min_price)
    parsed_max_price = _parse_decimal(max_price)
    if parsed_min_price is not None:
        qs = qs.filter(sale_price__gte=parsed_min_price)
    if parsed_max_price is not None:
        qs = qs.filter(sale_price__lte=parsed_max_price)

    parsed_min_discount = _parse_int(min_discount)
    parsed_max_discount = _parse_int(max_discount)
    if parsed_min_discount is not None:
        qs = qs.filter(discount_percentage__gte=parsed_min_discount)
    if parsed_max_discount is not None:
        qs = qs.filter(discount_percentage__lte=parsed_max_discount)

    if search:
        qs = _search_offers(qs, search)

    sort_map = {
        'newest': '-created_at',
        'discount': '-discount_percentage',
        'price_asc': 'sale_price',
        'price_desc': '-sale_price',
    }
    return qs.order_by(sort_map.get(sort, '-created_at'))


def _search_offers(queryset, search_term):
    if connection.vendor == 'postgresql':
        from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector

        vector = (
            SearchVector('title', weight='A')
            + SearchVector('short_description', weight='B')
            + SearchVector('description', weight='C')
            + SearchVector('merchant__business_name', weight='B')
        )
        query = SearchQuery(search_term)
        return (
            queryset.annotate(rank=SearchRank(vector, query))
            .filter(rank__gte=0.1)
            .order_by('-rank')
        )
    return queryset.filter(
        Q(title__icontains=search_term)
        | Q(short_description__icontains=search_term)
        | Q(description__icontains=search_term)
        | Q(merchant__business_name__icontains=search_term)
    )


def get_related_offers(offer, limit=4):
    return (
        get_approved_offers()
        .filter(category=offer.category)
        .exclude(pk=offer.pk)[:limit]
    )
