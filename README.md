# Vow Motors

A dealership website built with Flask, matching the black/white/serif design
language of the original static mockup. Public site (home, inventory,
financing, contact) plus a separate dealer login for staff to add, edit,
and remove inventory.

## Features

- **Home** — hero banner, body-style tiles with live counts, recently added inventory
- **Inventory** — filterable/sortable full listing (body style, make, model, keyword, price, sort), mileage in km
- **Vehicle detail** — photo gallery, specs, price
- **Financing** — pre-approval request form (stored in the database)
- **Contact** — contact form (stored in the database)
- **Dealer portal** (`/dealer/login`) — separate auth from the public site
  - Add / edit / delete vehicles, with photo uploads (max 20 photos per vehicle)
  - Mark vehicles sold/available
  - Dashboard stats (total / available / sold)
  - View submitted contact messages and financing requests
  - Change password while logged in, or reset a forgotten password by email

## Stack

Flask, Flask-SQLAlchemy (SQLite by default), Flask-Login, Flask-WTF (CSRF + forms),
Flask-Mail (password-reset emails), Flask-Limiter (rate limiting), Waitress (production server).

## Setup

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env       # then fill in the values (see below)
python create_dealer.py      # creates your dealer login (prompts for name, email, password)
python run.py
```

Visit **http://127.0.0.1:5000** and log in at `/dealer/login`.

`python seed.py` is optional: it creates a demo dealer and sample vehicles for
local testing only. Never run it on a live site, because the demo password is
public.

## Configuration (`.env`)

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Signs login sessions, CSRF tokens and reset links. Use a long random value: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `DEALERSHIP_NAME` | Name shown in the header, footer and emails |
| `DATABASE_URL` | Optional. Leave it out to use `vowmotors.db` next to `run.py` |
| `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_DEFAULT_SENDER` | Gmail address and a 16-character Gmail **app password** (not your normal password), used to send reset emails |
| `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USE_TLS` | Default to Gmail (`smtp.gmail.com`, 587, true) |
| `SECURE_COOKIES` | **Production only.** Set `true` once the site is served over HTTPS |
| `BEHIND_PROXY` | **Production only.** Set `true` when the host puts a proxy in front of the app, so reset links use `https://` and rate limits see real visitor IPs |

Never commit `.env`. Do not set `SECURE_COOKIES` locally, or login over
`http://127.0.0.1` stops working.

## Dealer accounts

- Create a login, or reset a password, by running `python create_dealer.py`.
  If the email already exists, its password is updated.
- There is no public self-signup route on purpose.
- A dealer who forgets their password uses **Forgot your password?** on the login
  page; a reset link (valid for 1 hour) is emailed to the address on the account.

## Security notes

- Passwords are hashed; forms are CSRF-protected; session cookies are `HttpOnly` and `SameSite=Lax`.
- Rate limits (per visitor IP): login 5/minute and 30/hour, password-reset requests 5/hour,
  contact and financing forms 10/hour each. Limits are held in memory, so they reset
  when the server restarts.
- Run production with Waitress, not `python run.py`:
  ```bash
  waitress-serve --port=5000 run:app
  ```
  Debug mode is off unless `FLASK_DEBUG=1` is set (local development only).

## Project layout

```
vowmotors-flask/
  run.py                 # entry point
  create_dealer.py       # create a dealer login / reset its password
  seed.py                # local demo data only
  config.py
  requirements.txt
  vowapp/
    __init__.py           # app factory
    extensions.py         # db, login_manager, csrf, mail, limiter
    models.py              # Dealer, Vehicle, VehiclePhoto, ContactMessage, FinancingApplication
    utils.py                # photo upload + reset email helpers
    main/                    # public blueprint: home, inventory, financing, contact
    dealer/                  # dealer blueprint: login, reset, dashboard, vehicle CRUD
    templates/
    static/
      css/style.css
      js/main.js
      images/                # logo, favicon, category and hero images
      uploads/vehicles/       # uploaded vehicle photos land here
```

## Notes

- `static/images/banner-placeholder.jpg` isn't included. Drop a photo at that path
  (referenced from `style.css`) for a home-page banner image, or leave it out;
  the layout works fine without it.
- SQLite and uploaded photos live on disk, so the host must keep its disk between
  restarts and deploys. Set `DATABASE_URL` to Postgres/MySQL if you move to a
  host without a persistent disk.
