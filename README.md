# Experio

Production-ready voucher and experiences marketplace built with Django 6, PostgreSQL, Stripe, and Bootstrap 5.

## Features

- **Customer portal**: browse, search, purchase vouchers, download PDFs
- **Merchant portal**: create offers, view sales, redeem vouchers
- **Admin portal**: approve merchants/offers, analytics dashboard
- **Payments**: Stripe Checkout (mock flow when keys unset)
- **Vouchers**: unique codes, QR images, ReportLab PDFs
- **Commission engine**: automatic split on purchase

## Quick Start (local)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_categories
python manage.py createsuperuser
python manage.py runserver
```

## Docker

```bash
cp .env.example .env
docker compose up --build
```

Set `DATABASE_URL=postgres://experio:experio@postgres:5432/experio` in `.env` for Docker.

## Environment Variables

See `.env.example` for `SECRET_KEY`, `DATABASE_URL`, Stripe keys, email, and AWS settings.

## Apps

| App | Purpose |
|-----|---------|
| accounts | Custom user, profile |
| merchants | Business profiles, commissions |
| offers | Categories, offers, marketplace |
| vouchers | Codes, QR, PDF |
| payments | Stripe checkout & webhooks |
| dashboard | Customer, merchant, admin UIs |
| notifications | Transactional email |
| core | Homepage, permissions, audit log |

## Stripe Webhook

Point Stripe to `POST /payments/webhook/` with events: `checkout.session.completed`, `payment_intent.payment_failed`, `charge.refunded`.

## MVP Checklist

- [x] Customer register, purchase, download PDF
- [x] Merchant create offer, sales, redeem
- [x] Admin approve merchant/offer, revenue dashboard
- [x] Docker (web, postgres, redis)
