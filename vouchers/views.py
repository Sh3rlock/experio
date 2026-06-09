from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.shortcuts import get_object_or_404

from vouchers.models import Voucher
from vouchers.services import generate_voucher_pdf


@login_required
def download_pdf(request, pk):
    voucher = get_object_or_404(Voucher, pk=pk, customer=request.user)
    if not voucher.pdf_file:
        generate_voucher_pdf(voucher)
    return FileResponse(
        voucher.pdf_file.open('rb'),
        as_attachment=True,
        filename=f'voucher_{voucher.voucher_code}.pdf',
    )
