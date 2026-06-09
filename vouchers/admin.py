from django.contrib import admin

from .models import Voucher


@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ('voucher_code', 'offer', 'customer', 'status', 'purchase_price', 'purchased_at', 'redeemed_at')
    list_filter = ('status',)
    search_fields = ('voucher_code', 'customer__email')
