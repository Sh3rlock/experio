from django.conf import settings
from django.urls import path

from . import views

app_name = 'core'

if settings.LANDING_PAGE_MODE:
    urlpatterns = [
        path('', views.landing, name='landing'),
        path('register/success/', views.landing_success, name='landing_success'),
    ]
else:
    urlpatterns = [
        path('', views.home, name='home'),
    ]
