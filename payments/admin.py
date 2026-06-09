from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'offer', 'amount', 'status', 'provider', 'created_at')
    list_filter = ('status', 'provider')
    search_fields = ('customer__email', 'provider_payment_id')
