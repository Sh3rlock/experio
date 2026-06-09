from django.conf import settings
from django.urls import path

from . import views

app_name = 'core'

if settings.LANDING_PAGE_MODE:
    urlpatterns = [
        path('', views.landing, name='landing'),
    ]
else:
    urlpatterns = [
        path('', views.home, name='home'),
    ]
