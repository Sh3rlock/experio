from django.contrib import admin

from .models import Commission, Merchant


@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'user', 'city', 'status', 'commission_rate', 'created_at')
    list_filter = ('status', 'country')
    search_fields = ('business_name', 'user__email')
    actions = ['approve_merchants', 'reject_merchants']

    @admin.action(description='Approve selected merchants')
    def approve_merchants(self, request, queryset):
        for m in queryset:
            m.status = Merchant.Status.APPROVED
            m.save()

    @admin.action(description='Reject selected merchants')
    def reject_merchants(self, request, queryset):
        queryset.update(status=Merchant.Status.REJECTED)


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ('merchant', 'voucher', 'sale_amount', 'commission_amount', 'merchant_amount', 'created_at')
    list_filter = ('merchant',)
