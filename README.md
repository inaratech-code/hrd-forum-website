# HRD Forum Nepal Website

Public website and staff management portal for **HRD Forum Nepal** ([hrdforum.org](https://hrdforum.org)) — human rights defenders networks, provincial helpdesks, news, resources, and incident reporting.

## Stack

| Layer | Technology |
|--------|------------|
| App | Django 4.2 |
| Database | Neon PostgreSQL (`DATABASE_URL`) — SQLite for local fallback |
| Media | Cloudflare R2 via `django-storages` + boto3 |
| Static | WhiteNoise |
| Hosting | Vercel (`vercel.json`) |
| DNS / CDN | Cloudflare → Vercel |

## Features

- Public site: stats, provinces map, news, gallery, videos, team, collaborations, membership & incident forms, gated resource downloads
- Staff portal at `/portal/` (session auth, staff/superuser only)
- Django admin at `/admin/` (superuser)
- Legacy JSON admin API (`/api/admin/*`) is **retired** (HTTP 410) — use `/portal/`

## Quick start (local)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env — for local SQLite you can omit DATABASE_URL
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

- Site: http://127.0.0.1:8000/
- Portal: http://127.0.0.1:8000/portal/login/

With Neon configured, set `DATABASE_URL` in `.env` (see `.env.example`).

## Environment variables

| Variable | Required | Notes |
|----------|----------|--------|
| `SECRET_KEY` | Production | Long random string |
| `DEBUG` | No | Defaults to `True` locally and `False` on Vercel/Render; set `False` in production |
| `DATABASE_URL` | Production / Vercel | Neon (or other Postgres) connection string with `sslmode=require` |
| `DJANGO_SUPERUSER_PASSWORD` | Production first boot | Used by `wsgi.py` to create `Superadmin` if missing |
| `R2_ACCOUNT_ID` | For uploads to R2 | Cloudflare account id |
| `R2_ACCESS_KEY_ID` | For R2 | R2 API token access key |
| `R2_SECRET_ACCESS_KEY` | For R2 | R2 API token secret |
| `R2_BUCKET_NAME` | No | Default `hrd-forum-media` |
| `R2_PUBLIC_BASE_URL` | No | Optional public CDN/custom domain for media URLs |

Never commit `.env`. Only `.env.example` is tracked.

## Staff access

1. Open `/portal/login/`
2. Sign in with a **staff** or **superuser** account
3. Manage news, gallery, resources, incidents, memberships, etc.

Security notes:

- Portal login blocks open redirects on `next=`
- Failed logins are rate-limited
- Logout is POST + CSRF
- Production refuses weak default `ADMIN_API_TOKEN` values if set

The old built-in `Superadmin` password is exposed and is now rejected at login. Immediately reset any existing account that used it with `python manage.py changepassword Superadmin` (or another affected username). New bootstrap admin accounts require a strong `DJANGO_SUPERUSER_PASSWORD`; no default password is created.

## Deploy (Vercel)

1. Push this repo to GitHub (already configured as origin when using the Inara Tech remote).
2. Import the project in [Vercel](https://vercel.com) — framework: other / Python via `vercel.json`.
3. Set environment variables in the Vercel project (at least `SECRET_KEY`, `DEBUG=False`, `DATABASE_URL`, `DJANGO_SUPERUSER_PASSWORD`, and R2 keys if using media).
4. Deploy. Migrations and initial seed run from `hrd_project/wsgi.py` on cold start.
5. Point Cloudflare DNS for `hrdforum.org` / `www` to Vercel; SSL mode **Full (strict)**.

Allowed hosts / CSRF origins already include `hrdforum.org`, `www.hrdforum.org`, and `*.vercel.app`.

## Project layout

```
hrd_project/          # Django settings, WSGI
main_app/             # Models, public APIs, portal views
templates/            # Public + portal templates
static/               # Source static assets
vercel.json           # Vercel Python entry
requirements.txt
.env.example
```

## Tests

```bash
# Local SQLite (ignore Neon URL from .env)
DATABASE_URL= DEBUG=True python manage.py test main_app
```

## License

Proprietary — Inara Tech / HRD Forum Nepal. All rights reserved unless otherwise agreed.
