from decimal import Decimal

from merchants.models import Commission


def create_commission(voucher):
    merchant = voucher.offer.merchant
    sale_amount = voucher.purchase_price
    rate = merchant.commission_rate / Decimal('100')
    commission_amount = (sale_amount * rate).quantize(Decimal('0.01'))
    merchant_amount = sale_amount - commission_amount
    return Commission.objects.create(
        merchant=merchant,
        voucher=voucher,
        sale_amount=sale_amount,
        commission_rate=merchant.commission_rate,
        commission_amount=commission_amount,
        merchant_amount=merchant_amount,
    )
