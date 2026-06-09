import colorsys
import urllib.request
from datetime import date, timedelta
from io import BytesIO
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models.signals import post_save

from accounts.models import User
from merchants.models import Merchant
from merchants.signals import merchant_created
from offers.models import Category, Offer, OfferImage

DEMO_MERCHANT_EMAIL = 'demo-merchant@experio.local'

# Bundled images — each key must match its offer content (see static/img/samples/README.md)
SAMPLES_DIR = Path(settings.BASE_DIR) / 'static' / 'img' / 'samples'

SAMPLE_IMAGE_FILES = {
    'arboretum': 'arboretum.jpg',           # botanical garden path
    'vintage-cars': 'vintage-cars.jpg',     # classic / vintage automobiles
    'beach': 'beach.jpg',                   # sandy beach and sea
    'spa': 'spa.jpg',                       # thermal spa / pool
    'restaurant': 'restaurant.jpg',         # gourmet plated dinner
    'massage': 'massage.jpg',               # massage therapy
    'beauty': 'beauty.jpg',                 # facial skincare treatment
    'adventure': 'adventure.jpg',           # zip line / ropes course
    'supercar': 'supercar.jpg',             # sports / supercar (driving experience)
    'escape-room': 'escape-room.jpg',       # team in escape room
    'balloon': 'balloon.jpg',               # hot air balloons in sky
    'brunch': 'brunch.jpg',                 # brunch table spread
    'city-break': 'city-break.jpg',         # European old town / travel
    'fitness': 'fitness.jpg',               # outdoor group fitness
    'wine-course': 'wine-course.jpg',       # wine tasting glasses
    'gift-card': 'gift-card.jpg',           # wrapped gift box
}

# Verified Pexels photo IDs (slug on pexels.com must match offer content)
PEXELS = 'https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg?auto=compress&cs=tinysrgb&w=1200'

SAMPLE_IMAGE_SOURCES = {
    'arboretum': PEXELS.format(pid=2255935),       # greenhouse / plants
    'vintage-cars': PEXELS.format(pid=170811),     # vintage automobiles
    'beach': PEXELS.format(pid=457882),            # tropical beach
    'spa': PEXELS.format(pid=3757952),             # spa pool
    'restaurant': PEXELS.format(pid=941861),       # restaurant dining
    'massage': PEXELS.format(pid=269077),          # spa massage
    'beauty': PEXELS.format(pid=3997985),          # woman skincare / facial
    'adventure': PEXELS.format(pid=1371667),       # zip line
    'supercar': PEXELS.format(pid=2444429),       # sports car (color)
    'escape-room': PEXELS.format(pid=3945313),     # puzzle / mystery escape
    'balloon': PEXELS.format(pid=670061),          # hot air balloons at sunset
    'brunch': PEXELS.format(pid=1527603),          # brunch food table
    'city-break': PEXELS.format(pid=1179225),      # colorful European street
    'fitness': PEXELS.format(pid=2261476),         # group fitness training
    'wine-course': PEXELS.format(pid=6029684),    # wine tasting pour
    'gift-card': PEXELS.format(pid=1303080),       # colorful wrapped gift
}

DOWNLOAD_HEADERS = {'User-Agent': 'Experio/1.0 (sample-seed)'}

# Reject downloads that look grayscale / wrong (e.g. house B&W for balloon)
MIN_COLOR_SATURATION = 0.12
MAX_GRAY_RATIO = 0.55

SAMPLE_OFFERS = [
    {
        'slug': 'folly-arboretum-entry',
        'title': 'Folly Arboretum Entry & Wine Tasting',
        'short_description': 'Full-day access to the arboretum with a guided wine tasting.',
        'description': 'Walk through botanical gardens and enjoy a premium wine tasting at the on-site winery.',
        'highlight_tag': 'Beautiful surroundings',
        'category': 'Adventure',
        'city': 'Szekszárd',
        'original_price': '840',
        'sale_price': '749',
        'discount': 11,
        'rating': '4.7',
        'featured': True,
        'image_key': 'arboretum',
    },
    {
        'slug': 'classic-car-exhibition',
        'title': 'Classic Car Exhibition Pass',
        'short_description': 'Access to vintage car collection and interactive exhibits.',
        'description': 'Discover rare automobiles from the 1920s to 1980s with audio guides included.',
        'highlight_tag': 'Family friendly',
        'category': 'Events',
        'city': 'Budapest',
        'original_price': '4000',
        'sale_price': '3200',
        'discount': 20,
        'rating': '4.9',
        'featured': True,
        'image_key': 'vintage-cars',
    },
    {
        'slug': 'summer-beach-getaway',
        'title': 'All-Inclusive Summer Beach Day',
        'short_description': 'Beach access, lunch, and sun lounger for one day.',
        'description': 'Relax on the Black Sea coast with lunch and drinks included.',
        'highlight_tag': 'Best seller',
        'category': 'Travel',
        'city': 'Mamaia',
        'original_price': '55000',
        'sale_price': '45000',
        'discount': 18,
        'rating': '4.8',
        'featured': True,
        'image_key': 'beach',
    },
    {
        'slug': 'luxury-spa-day',
        'title': 'Luxury Spa Day Package',
        'short_description': '3-hour spa access with massage and thermal pools.',
        'description': 'Unwind with sauna, thermal baths, and a 45-minute aromatherapy massage.',
        'highlight_tag': 'Relaxation',
        'category': 'Spa',
        'city': 'Cluj-Napoca',
        'original_price': '450',
        'sale_price': '299',
        'discount': 34,
        'rating': '4.6',
        'featured': True,
        'image_key': 'spa',
    },
    {
        'slug': 'gourmet-dinner-for-two',
        'title': 'Gourmet Dinner for Two',
        'short_description': 'Five-course tasting menu with wine pairing.',
        'description': 'An evening at a top local restaurant with chef-selected courses.',
        'highlight_tag': 'Fine dining',
        'category': 'Restaurant',
        'city': 'Brașov',
        'original_price': '520',
        'sale_price': '349',
        'discount': 33,
        'rating': '4.8',
        'featured': False,
        'image_key': 'restaurant',
    },
    {
        'slug': 'therapeutic-massage',
        'title': 'Therapeutic Massage Session',
        'short_description': '60-minute deep tissue or relaxation massage.',
        'description': 'Professional massage in a calm wellness studio.',
        'highlight_tag': 'Health & wellness',
        'category': 'Spa',
        'city': 'Timișoara',
        'original_price': '280',
        'sale_price': '179',
        'discount': 36,
        'rating': '4.5',
        'featured': False,
        'image_key': 'massage',
    },
    {
        'slug': 'beauty-facial-treatment',
        'title': 'Premium Facial Treatment',
        'short_description': '90-minute facial with organic skincare products.',
        'description': 'Hydrating facial treatment tailored to your skin type.',
        'highlight_tag': 'Self-care',
        'category': 'Beauty',
        'city': 'Bucharest',
        'original_price': '350',
        'sale_price': '199',
        'discount': 43,
        'rating': '4.7',
        'featured': False,
        'image_key': 'beauty',
    },
    {
        'slug': 'adventure-park-family',
        'title': 'Adventure Park Family Pass',
        'short_description': 'Full-day access for 2 adults and 2 children.',
        'description': 'Zip lines, rope courses, and kids zone in a forest adventure park.',
        'highlight_tag': 'Outdoor fun',
        'category': 'Family',
        'city': 'Sinaia',
        'original_price': '380',
        'sale_price': '249',
        'discount': 34,
        'rating': '4.9',
        'featured': True,
        'image_key': 'adventure',
    },
    {
        'slug': 'supercar-driving-experience',
        'title': 'Supercar Driving Experience',
        'short_description': '20-minute track session in a high-performance sports car.',
        'description': 'Drive a supercar on a professional circuit with instructor briefing and safety gear included.',
        'highlight_tag': 'Adrenaline rush',
        'category': 'Adventure',
        'city': 'Budapest',
        'original_price': '1200',
        'sale_price': '899',
        'discount': 25,
        'rating': '4.9',
        'featured': True,
        'image_key': 'supercar',
    },
    {
        'slug': 'escape-room-mystery',
        'title': 'Escape Room — Mystery Manor',
        'short_description': '60-minute themed escape game for up to 4 players.',
        'description': 'Solve puzzles and clues to escape before time runs out. Choose from three difficulty levels.',
        'highlight_tag': 'Team building',
        'category': 'Events',
        'city': 'Bucharest',
        'original_price': '320',
        'sale_price': '219',
        'discount': 32,
        'rating': '4.8',
        'featured': False,
        'image_key': 'escape-room',
    },
    {
        'slug': 'hot-air-balloon-flight',
        'title': 'Sunrise Hot Air Balloon Flight',
        'short_description': '45-minute flight with champagne toast after landing.',
        'description': 'Float over rolling hills at sunrise with a licensed pilot and ground crew support.',
        'highlight_tag': 'Unforgettable views',
        'category': 'Travel',
        'city': 'Sibiu',
        'original_price': '1800',
        'sale_price': '1299',
        'discount': 28,
        'rating': '4.9',
        'featured': True,
        'image_key': 'balloon',
    },
    {
        'slug': 'weekend-brunch-for-two',
        'title': 'Weekend Brunch & Prosecco for Two',
        'short_description': 'Buffet brunch with welcome prosecco at a city bistro.',
        'description': 'Enjoy a relaxed late-morning brunch with fresh pastries, eggs, salads, and a glass of prosecco each.',
        'highlight_tag': 'Weekend treat',
        'category': 'Restaurant',
        'city': 'Budapest',
        'original_price': '380',
        'sale_price': '249',
        'discount': 34,
        'rating': '4.6',
        'featured': False,
        'image_key': 'brunch',
    },
    {
        'slug': 'transylvania-city-break',
        'title': '2-Night Transylvania City Break',
        'short_description': 'Hotel stay with breakfast and guided old-town walking tour.',
        'description': 'Two nights in a boutique hotel plus a guided walking tour of the historic city center.',
        'highlight_tag': 'Culture & history',
        'category': 'Travel',
        'city': 'Brașov',
        'original_price': '2200',
        'sale_price': '1599',
        'discount': 27,
        'rating': '4.7',
        'featured': False,
        'image_key': 'city-break',
    },
    {
        'slug': 'outdoor-fitness-bootcamp',
        'title': 'Outdoor Fitness Bootcamp — 10 Sessions',
        'short_description': 'Small-group HIIT and strength training in the park.',
        'description': 'Ten coached outdoor sessions suitable for all fitness levels. Equipment provided.',
        'highlight_tag': 'Get fit outdoors',
        'category': 'Fitness',
        'city': 'Cluj-Napoca',
        'original_price': '600',
        'sale_price': '399',
        'discount': 34,
        'rating': '4.5',
        'featured': False,
        'image_key': 'fitness',
    },
    {
        'slug': 'wine-tasting-workshop',
        'title': 'Intro to Wine Tasting Workshop',
        'short_description': '2-hour guided tasting of 6 regional wines with cheese pairing.',
        'description': 'Learn aroma, body, and pairing basics from a certified sommelier in an intimate cellar setting.',
        'highlight_tag': 'Learn & taste',
        'category': 'Courses',
        'city': 'Szekszárd',
        'original_price': '420',
        'sale_price': '279',
        'discount': 34,
        'rating': '4.8',
        'featured': False,
        'image_key': 'wine-course',
    },
    {
        'slug': 'experio-spa-gift-card',
        'title': 'Experio Spa Gift Card — 300 RON',
        'short_description': 'Redeemable at partner spas nationwide for any treatment.',
        'description': 'Digital gift card valid for 12 months. Recipient chooses massage, facial, or spa day packages.',
        'highlight_tag': 'Perfect gift',
        'category': 'Gift Cards',
        'city': 'Romania',
        'original_price': '300',
        'sale_price': '249',
        'discount': 17,
        'rating': '4.9',
        'featured': False,
        'image_key': 'gift-card',
    },
]


def load_sample_image(image_key):
    filename = SAMPLE_IMAGE_FILES[image_key]
    path = SAMPLES_DIR / filename
    if not path.is_file():
        raise FileNotFoundError(
            f'Missing sample image {path}. Expected bundled files in static/img/samples/.'
        )
    return ContentFile(path.read_bytes(), name=filename)


class Command(BaseCommand):
    help = 'Seed demo merchants and sample offers with category-matched images'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Remove previously seeded demo offers',
        )
        parser.add_argument(
            '--refresh-images',
            action='store_true',
            default=True,
            help='Replace offer images with bundled samples (default: on)',
        )
        parser.add_argument(
            '--no-refresh-images',
            action='store_false',
            dest='refresh_images',
            help='Skip image updates for existing offers',
        )
        parser.add_argument(
            '--fetch-images',
            action='store_true',
            help='Download bundled sample JPEGs from Pexels before seeding',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['fetch_images']:
            self._fetch_sample_images()

        if options['clear']:
            deleted, _ = Offer.objects.filter(merchant__business_name='Experio Demo Partners').delete()
            self.stdout.write(self.style.WARNING(f'Removed {deleted} demo offer records.'))
            return

        missing = [
            key for key, fname in SAMPLE_IMAGE_FILES.items()
            if not (SAMPLES_DIR / fname).is_file()
        ]
        if missing:
            self.stderr.write(self.style.ERROR(f'Missing sample images: {", ".join(missing)}'))
            return

        self.stdout.write('Seeding categories (if needed)...')
        from django.core.management import call_command
        call_command('seed_categories')

        merchant = self._ensure_merchant()
        valid_until = date.today() + timedelta(days=180)
        refreshed = 0

        for item in SAMPLE_OFFERS:
            category = Category.objects.get(name=item['category'])
            offer, was_created = Offer.objects.update_or_create(
                merchant=merchant,
                slug=item['slug'],
                defaults={
                    'category': category,
                    'title': item['title'],
                    'short_description': item['short_description'],
                    'description': item['description'],
                    'highlight_tag': item['highlight_tag'],
                    'terms_and_conditions': 'Voucher valid on weekdays unless stated otherwise. Non-refundable.',
                    'original_price': Decimal(item['original_price']),
                    'sale_price': Decimal(item['sale_price']),
                    'discount_percentage': item['discount'],
                    'display_rating': Decimal(item['rating']),
                    'quantity_available': 50,
                    'voucher_valid_until': valid_until,
                    'featured': item['featured'],
                    'status': Offer.Status.APPROVED,
                },
            )
            if was_created or options['refresh_images'] or not offer.images.exists():
                self._attach_image(offer, item['image_key'])
                refreshed += 1

        self.stdout.write(self.style.SUCCESS(
            f'Seeded {len(SAMPLE_OFFERS)} offers ({refreshed} images updated) for {merchant.business_name}.'
        ))
        self.stdout.write(f'Merchant login: {DEMO_MERCHANT_EMAIL} / demo1234')

    def _ensure_merchant(self):
        post_save.disconnect(merchant_created, sender=Merchant)
        try:
            return self._ensure_merchant_inner()
        finally:
            post_save.connect(merchant_created, sender=Merchant)

    def _ensure_merchant_inner(self):
        user, _ = User.objects.get_or_create(
            email=DEMO_MERCHANT_EMAIL,
            defaults={'first_name': 'Demo', 'last_name': 'Merchant', 'is_merchant': True, 'is_active': True},
        )
        if not user.has_usable_password():
            user.set_password('demo1234')
            user.save(update_fields=['password'])
        merchant, _ = Merchant.objects.get_or_create(
            user=user,
            defaults={
                'business_name': 'Experio Demo Partners',
                'description': 'Sample merchant for demo offers.',
                'city': 'Bucharest',
                'county': 'Bucharest',
                'country': 'Romania',
                'address': 'Strada Demo 1',
                'phone': '+40 700 000 000',
                'email': DEMO_MERCHANT_EMAIL,
                'status': Merchant.Status.APPROVED,
            },
        )
        if merchant.status != Merchant.Status.APPROVED:
            Merchant.objects.filter(pk=merchant.pk).update(status=Merchant.Status.APPROVED)
            merchant.refresh_from_db()
        user.is_merchant = True
        user.save(update_fields=['is_merchant'])
        return merchant

    def _image_color_stats(self, data):
        from PIL import Image

        image = Image.open(BytesIO(data)).convert('RGB')
        image.thumbnail((400, 400))
        pixels = list(image.getdata())
        saturations = [colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)[1] for r, g, b in pixels]
        gray_ratio = sum(
            1 for r, g, b in pixels if max(r, g, b) - min(r, g, b) < 15
        ) / len(pixels)
        return sum(saturations) / len(saturations), gray_ratio

    def _fetch_sample_images(self):
        SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
        request = urllib.request.Request
        for key, url in SAMPLE_IMAGE_SOURCES.items():
            path = SAMPLES_DIR / SAMPLE_IMAGE_FILES[key]
            self.stdout.write(f'Downloading {path.name} ({key})...')
            req = request(url, headers=DOWNLOAD_HEADERS)
            with urllib.request.urlopen(req, timeout=60) as response:
                data = response.read()
            saturation, gray_ratio = self._image_color_stats(data)
            if saturation < MIN_COLOR_SATURATION or gray_ratio > MAX_GRAY_RATIO:
                raise CommandError(
                    f'Downloaded image for "{key}" looks grayscale or off-topic '
                    f'(saturation={saturation:.2f}, gray_ratio={gray_ratio:.2f}). '
                    f'Update SAMPLE_IMAGE_SOURCES.'
                )
            path.write_bytes(data)
        self.stdout.write(self.style.SUCCESS('Sample images downloaded and verified.'))

    def _attach_image(self, offer, image_key):
        content = load_sample_image(image_key)
        OfferImage.objects.filter(offer=offer).delete()
        image = OfferImage(offer=offer, sort_order=0)
        image.image.save(f'{offer.slug}.jpg', content, save=True)
