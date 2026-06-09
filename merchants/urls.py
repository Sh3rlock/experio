from django.urls import path

from . import views

app_name = 'merchants'

urlpatterns = [
    path('register/', views.register_merchant, name='register'),
    path('pending/', views.pending, name='pending'),
    path('redeem/', views.redeem_page, name='redeem'),
    path('sales/', views.sales, name='sales'),
]
