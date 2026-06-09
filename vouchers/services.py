import io
import random
import string
from datetime import datetime

import qrcode
from django.core.files.base import ContentFile
from django.utils import timezone
from django.utils.translation import gettext as _
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from merchants.services import create_commission
from vouchers.models import Voucher


def generate_voucher_code():
    year = datetime.now().year
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    code = f'EXP-{year}-{suffix}'
    while Voucher.objects.filter(voucher_code=code).exists():
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        code = f'EXP-{year}-{suffix}'
    return code


def create_voucher(offer, customer, purchase_price):
    from datetime import datetime as dt

    expires = timezone.make_aware(
        dt.combine(offer.voucher_valid_until, dt.max.time().replace(microsecond=0))
    )
    voucher = Voucher.objects.create(
        offer=offer,
        customer=customer,
        voucher_code=generate_voucher_code(),
        purchase_price=purchase_price,
        expires_at=expires,
    )
    generate_qr_code(voucher)
    generate_voucher_pdf(voucher)
    offer.quantity_available = max(0, offer.quantity_available - 1)
    offer.save(update_fields=['quantity_available'])
    create_commission(voucher)
    return voucher


def generate_qr_code(voucher):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(voucher.voucher_code)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    filename = f'qr_{voucher.voucher_code}.png'
    voucher.qr_image.save(filename, ContentFile(buffer.read()), save=True)
    return voucher


def generate_voucher_pdf(voucher):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2 * cm, leftMargin=2 * cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#4F46E5'))
    elements = []

    elements.append(Paragraph(_('Experio Voucher'), title_style))
    elements.append(Spacer(1, 0.5 * cm))

    offer = voucher.offer
    merchant = offer.merchant
    data = [
        [_('Merchant'), merchant.business_name],
        [_('Offer'), offer.title],
        [_('Voucher Code'), voucher.voucher_code],
        [_('Purchase Price'), f'{voucher.purchase_price} RON'],
        [_('Valid Until'), voucher.expires_at.strftime('%d %B %Y')],
        [_('Status'), voucher.get_status_display()],
    ]
    table = Table(data, colWidths=[5 * cm, 12 * cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#EEF2FF')),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.5 * cm))

    if voucher.qr_image:
        qr_path = voucher.qr_image.path
        elements.append(Image(qr_path, width=4 * cm, height=4 * cm))

    if offer.terms_and_conditions:
        elements.append(Spacer(1, 0.5 * cm))
        elements.append(Paragraph(f'<b>{_("Terms & Conditions")}</b>', styles['Heading3']))
        elements.append(Paragraph(offer.terms_and_conditions, styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    filename = f'voucher_{voucher.voucher_code}.pdf'
    voucher.pdf_file.save(filename, ContentFile(buffer.read()), save=True)
    return voucher


def redeem_voucher(voucher_code, merchant_user):
    try:
        voucher = Voucher.objects.select_related('offer', 'offer__merchant').get(
            voucher_code=voucher_code.upper().strip()
        )
    except Voucher.DoesNotExist:
        return None, _('Voucher not found.')

    if voucher.offer.merchant.user_id != merchant_user.id and not merchant_user.is_staff:
        return None, _('This voucher belongs to another merchant.')

    if voucher.status != Voucher.Status.ACTIVE:
        return None, _('Voucher is %(status)s.') % {'status': voucher.get_status_display().lower()}

    if voucher.expires_at <= timezone.now():
        voucher.status = Voucher.Status.EXPIRED
        voucher.save(update_fields=['status'])
        return None, _('Voucher has expired.')

    voucher.status = Voucher.Status.REDEEMED
    voucher.redeemed_at = timezone.now()
    voucher.redeemed_by = merchant_user
    voucher.save(update_fields=['status', 'redeemed_at', 'redeemed_by'])
    return voucher, None
