from django.urls import path

from . import views

app_name = 'offers'

urlpatterns = [
    path('', views.offer_list, name='list'),
    path('manage/', views.merchant_offer_list, name='merchant_list'),
    path('manage/create/', views.merchant_offer_create, name='merchant_create'),
    path('manage/<int:pk>/edit/', views.merchant_offer_edit, name='merchant_edit'),
    path('manage/<int:pk>/preview/', views.merchant_offer_preview, name='merchant_preview'),
    path('manage/<int:pk>/delete/', views.merchant_offer_delete, name='merchant_delete'),
    path('<slug:slug>/', views.offer_detail, name='detail'),
    path('<slug:slug>/buy/', views.buy_offer, name='buy'),
]
