# StockFlow — Inventory Management System

A Django-backed inventory manager for a small business. Built on top of the
provided Bootstrap frontend, wired to a real database through a small
REST-style API.

## What's inside

```
stockflow/          Django project (settings, root urls, wsgi/asgi)
inventory/           Django app
  models.py           Product model
  views.py             Dashboard view + JSON API views
  urls.py               URL routes
  admin.py               Registers Product in /admin/
templates/inventory/dashboard.html   The frontend, now fetching from the API
requirements.txt, Procfile, runtime.txt   Deployment config for Railway
```

## The model

```python
class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    low_stock_threshold = models.PositiveIntegerField(default=5)
```

`is_low_stock` is a property (`quantity <= low_stock_threshold`) so the
"LOW STOCK" flag is always computed live, never stored/out of sync.

## API

All endpoints return/accept JSON.

| Method | URL                     | Does what                                   |
|--------|-------------------------|----------------------------------------------|
| GET    | `/api/products/`        | List all products + dashboard summary        |
| POST   | `/api/products/`        | Create a product (validates each field)       |
| GET    | `/api/products/<id>/`   | Fetch one product                             |
| PUT    | `/api/products/<id>/`   | Update a product                              |
| DELETE | `/api/products/<id>/`   | Delete a product                              |

`GET /api/products/` response shape:
```json
{
  "products": [ { "id": 1, "name": "...", "quantity": 15, "price": 29.99, "is_low_stock": false, ... } ],
  "summary": { "total_products": 2, "current_stock": 15, "low_stock_count": 1, "total_value": 449.85 }
}
```

The dashboard cards (Total Products / Current Stock / Low Stock / Total
Value) are just this `summary` object rendered on the page — no separate
endpoint needed.

CSRF: the dashboard page sets the `csrftoken` cookie (`@ensure_csrf_cookie`);
the frontend JS reads it and sends it back as `X-CSRFToken` on every
POST/PUT/DELETE, the standard Django pattern for same-origin AJAX.

## Running it locally

```bash
python -m venv venv
source venv/bin/activate        # venv\Scripts\activate on Windows
pip install -r requirements.txt

cp .env.example .env            # optional, defaults already work
python manage.py migrate
python manage.py createsuperuser   # optional, for /admin/
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`. This uses SQLite locally out of the box —
no extra setup.

## Deploying to Railway

Railway auto-detects Django/Python via the `Procfile` + `requirements.txt`,
so there's no Dockerfile needed.

1. **Push this project to a GitHub repo** (Railway deploys from git).
   ```bash
   git init
   git add .
   git commit -m "StockFlow: Django inventory MVP"
   git branch -M main
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **Create a new Railway project** → *Deploy from GitHub repo* → pick this repo.

3. **Add a PostgreSQL database**: in the Railway project, *New* → *Database*
   → *Add PostgreSQL*. Railway automatically injects a `DATABASE_URL`
   variable into your web service — `settings.py` already picks this up via
   `dj_database_url`, so no code changes are needed.

4. **Set environment variables** on the web service (*Variables* tab):
   | Key | Value |
   |---|---|
   | `SECRET_KEY` | a long random string (e.g. `python -c "import secrets; print(secrets.token_urlsafe(50))"`) |
   | `DEBUG` | `False` |

   You do **not** need to set `ALLOWED_HOSTS` — the app reads Railway's
   `RAILWAY_PUBLIC_DOMAIN` automatically and trusts `*.up.railway.app` too.

5. **Deploy.** Railway runs the `release` command (`python manage.py
   migrate`) before every deploy, then starts the `web` command
   (`gunicorn stockflow.wsgi`). Static files are served by WhiteNoise, so no
   separate static host is needed.

6. Once live, visit `https://<your-app>.up.railway.app/admin/` and create a
   superuser to manage products from the Django admin too:
   ```bash
   railway run python manage.py createsuperuser
   ```

## Notes / where this deliberately stayed MVP-sized

- No auth on the dashboard itself yet (the sidebar's "Manager" role is
  static) — add `django.contrib.auth` login views if/when multiple users
  need separate accounts.
- No pagination on the products table — fine at small-business scale,
  revisit if the list gets into the hundreds.
- Delete was added (small, standard CRUD need) but there's no bulk
  import/export — deliberately out of scope per the brief ("don't build an
  ERP").
