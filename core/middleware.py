from django.conf import settings
from django.shortcuts import redirect
from django.utils import translation

from .models import AuditLog


class LandingPageModeMiddleware:
    """When landing mode is on, only the landing page and essential paths are reachable."""

    ALLOWED_PREFIXES = (
        '/health/',
        '/i18n/setlang/',
        '/static/',
        '/media/',
        '/admin/',
        '/payments/webhook/',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not settings.LANDING_PAGE_MODE:
            return self.get_response(request)

        path = request.path
        if path in ('', '/', '/register/success/'):
            return self.get_response(request)
        if any(path.startswith(prefix) for prefix in self.ALLOWED_PREFIXES):
            return self.get_response(request)

        return redirect('core:landing')


class UserLanguageMiddleware:
    """Override locale with the authenticated user's saved language (Django 6 uses cookies)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        preferred = None
        if request.user.is_authenticated:
            lang = getattr(request.user, 'language', None)
            if lang and lang in dict(settings.LANGUAGES):
                preferred = lang
                translation.activate(lang)
                request.LANGUAGE_CODE = translation.get_language()

        response = self.get_response(request)

        if preferred and request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME) != preferred:
            response.set_cookie(
                settings.LANGUAGE_COOKIE_NAME,
                preferred,
                max_age=settings.LANGUAGE_COOKIE_AGE,
                path=settings.LANGUAGE_COOKIE_PATH,
                domain=settings.LANGUAGE_COOKIE_DOMAIN,
                secure=settings.LANGUAGE_COOKIE_SECURE,
                httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
                samesite=settings.LANGUAGE_COOKIE_SAMESITE,
            )
        return response


class AuditLogMiddleware:
    SENSITIVE_PATHS = ('/payments/webhook', '/accounts/login', '/accounts/signup')

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            if any(request.path.startswith(p) for p in self.SENSITIVE_PATHS):
                AuditLog.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    action=f'{request.method} {request.path}',
                    path=request.path[:500],
                    method=request.method,
                    ip_address=self._get_client_ip(request),
                )
        return response

    @staticmethod
    def _get_client_ip(request):
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        if xff:
            return xff.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
