import os

from django.conf import settings
from django.core.exceptions import ValidationError


def validate_image_file(value):
    ext = os.path.splitext(value.name)[1].lower().lstrip('.')
    if ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(f'Allowed image types: {", ".join(settings.ALLOWED_IMAGE_EXTENSIONS)}')
    if value.size > settings.MAX_IMAGE_SIZE:
        raise ValidationError('Image file too large (max 5MB).')
