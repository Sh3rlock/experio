import json
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import render
from django.utils import timezone

from core.permissions import merchant_required, staff_required
from merchants.models import Commission, Merchant
from offers.models import Offer
from payments.models import Payment
from vouchers.models import Voucher


@login_required
def customer_dashboard(request):
    vouchers = Voucher.objects.filter(customer=request.user).select_related('offer', 'offer__merchant')
    payments = Payment.objects.filter(customer=request.user).select_related('offer')
    return render(request, 'dashboard/customer.html', {
        'vouchers': vouchers,
        'payments': payments,
    })


@merchant_required
def merchant_dashboard(request):
    merchant = request.user.merchant
    vouchers = Voucher.objects.filter(offer__merchant=merchant)
    commissions = Commission.objects.filter(merchant=merchant)
    return render(request, 'dashboard/merchant.html', {
        'active_offers': Offer.objects.filter(merchant=merchant, status=Offer.Status.APPROVED).count(),
        'total_sales': vouchers.count(),
        'revenue': commissions.aggregate(total=Sum('merchant_amount'))['total'] or Decimal('0'),
        'redeemed': vouchers.filter(status=Voucher.Status.REDEEMED).count(),
        'recent_sales': vouchers.select_related('offer', 'customer')[:10],
    })


@staff_required
def admin_dashboard(request):
    paid = Payment.objects.filter(status=Payment.Status.PAID)
    commissions = Commission.objects.all()
    sales_by_month = (
        paid.annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Sum('amount'), count=Count('id'))
        .order_by('month')
    )
    top_merchants = (
        commissions.values('merchant__business_name')
        .annotate(revenue=Sum('merchant_amount'), sales=Count('id'))
        .order_by('-revenue')[:10]
    )
    top_categories = (
        Offer.objects.filter(vouchers__isnull=False)
        .values('category__name')
        .annotate(sales=Count('vouchers'))
        .order_by('-sales')[:10]
    )
    sales_list = [
        {
            'month': item['month'].isoformat() if item['month'] else '',
            'total': float(item['total'] or 0),
            'count': item['count'],
        }
        for item in sales_by_month
    ]
    return render(request, 'dashboard/admin.html', {
        'total_revenue': paid.aggregate(t=Sum('amount'))['t'] or 0,
        'commission_revenue': commissions.aggregate(t=Sum('commission_amount'))['t'] or 0,
        'active_merchants': Merchant.objects.filter(status=Merchant.Status.APPROVED).count(),
        'active_offers': Offer.objects.filter(status=Offer.Status.APPROVED).count(),
        'sold_vouchers': Voucher.objects.count(),
        'sales_by_month_json': json.dumps(sales_list),
        'top_merchants': list(top_merchants),
        'top_categories': list(top_categories),
        'recent_transactions': paid.select_related('customer', 'offer')[:20],
    })
