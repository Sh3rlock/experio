from django.urls import path

from . import views

app_name = 'vouchers'

urlpatterns = [
    path('<int:pk>/download/', views.download_pdf, name='download'),
]
