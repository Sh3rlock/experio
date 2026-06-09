# Deploy Experio to Railway (validation landing)

This guide deploys the **landing page only** (`LANDING_PAGE_MODE=True`) without PostgreSQL or Redis.

## Architecture

- **Web**: Docker container (Gunicorn + WhiteNoise)
- **Database**: SQLite (default when `DATABASE_URL` is unset)
- **Cache**: In-memory (default when `REDIS_URL` is unset)
- **Email**: SMTP for founding partner form notifications

> SQLite data is stored on the container filesystem. It resets on redeploy unless you add a Railway volume mounted at `/app`. For validation (form emails only), that is usually acceptable.

## 1. Push to GitHub

```bash
git init
git add .
git commit -m "Prepare Experio for Railway landing deploy"
git remote add origin https://github.com/Sh3rlock/experio.git
git branch -M main
git push -u origin main
```

## 2. Create Railway project

1. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**
2. Select your Experio repository
3. Railway detects `railway.toml` and builds from `Dockerfile`
4. **Do not** add PostgreSQL or Redis plugins for this validation stage

## 3. Environment variables

Set these in Railway → your service → **Variables**:

| Variable | Example |
|----------|---------|
| `SECRET_KEY` | Long random string |
| `DEBUG` | `False` |
| `LANDING_PAGE_MODE` | `True` |
| `ALLOWED_HOSTS` | `your-app.up.railway.app,.railway.app` |
| `CSRF_TRUSTED_ORIGINS` | `https://your-app.up.railway.app` |
| `SITE_URL` | `https://your-app.up.railway.app` |
| `SECURE_SSL_REDIRECT` | `False` (Railway handles HTTPS at the edge) |
| `EMAIL_BACKEND` | `django.core.mail.backends.smtp.EmailBackend` |
| `EMAIL_HOST` | Your SMTP host |
| `EMAIL_PORT` | `587` |
| `EMAIL_USE_TLS` | `True` |
| `EMAIL_USER` | SMTP username |
| `EMAIL_PASSWORD` | SMTP password |
| `DEFAULT_FROM_EMAIL` | Verified sender |
| `PARTNER_APPLICATION_NOTIFY_EMAIL` | `matyass91@gmail.com` (where form submissions are sent) |

**Do not set** `DATABASE_URL` or `REDIS_URL` unless you add those services later.

After Railway assigns a domain, update `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, and `SITE_URL` to match.

## 4. Admin login (auto-created on deploy)

`entrypoint.sh` runs `ensure_superuser` after migrations. Defaults:

| Field | Default |
|-------|---------|
| Email | `matyas@experio.local` |
| Password | `QweAsd789` |

Override with `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL`, and `DJANGO_SUPERUSER_PASSWORD`. Set `CREATE_DEFAULT_SUPERUSER=False` to disable.

Log in at `/admin/` after the first deploy. Partner applications are emailed to `PARTNER_APPLICATION_NOTIFY_EMAIL`, or the first superuser if that variable is unset.

## 5. Smoke test

- [ ] `https://your-app.up.railway.app/` — landing page with CSS
- [ ] Language switcher (EN / HU / RO)
- [ ] Founding partner form submits
- [ ] Email notification received
- [ ] `/offers/` redirects to `/`
- [ ] `/admin/` works with the default superuser

## Custom domain

Add the domain in Railway, then update `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, and `SITE_URL`.

## Later: full marketplace

1. Add Railway **PostgreSQL** and set `DATABASE_URL`
2. Optionally add **Redis** and set `REDIS_URL`
3. Set `LANDING_PAGE_MODE=False`
4. Run migrations and seed data as needed
