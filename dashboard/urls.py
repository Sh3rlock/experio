from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.customer_dashboard, name='customer'),
    path('merchant/', views.merchant_dashboard, name='merchant'),
    path('admin/', views.admin_dashboard, name='admin'),
]
