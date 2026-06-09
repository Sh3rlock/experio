from django.contrib import admin

from .models import Category, Offer, OfferImage


class OfferImageInline(admin.TabularInline):
    model = OfferImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug', 'icon')


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'merchant', 'category', 'sale_price', 'status', 'featured', 'created_at')
    list_filter = ('status', 'featured', 'category')
    search_fields = ('title', 'merchant__business_name')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [OfferImageInline]
    actions = ['approve_offers', 'reject_offers']

    @admin.action(description='Approve selected offers')
    def approve_offers(self, request, queryset):
        queryset.update(status=Offer.Status.APPROVED)

    @admin.action(description='Reject selected offers')
    def reject_offers(self, request, queryset):
        queryset.update(status=Offer.Status.REJECTED)
