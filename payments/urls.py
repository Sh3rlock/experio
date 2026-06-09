from django.urls import path

from . import views

app_name = 'payments'

urlpatterns = [
    path('success/', views.payment_success, name='success'),
    path('webhook/', views.stripe_webhook, name='webhook'),
    path('download/<int:pk>/', views.download_voucher, name='download'),
]
