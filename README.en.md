# Yanımda

[Türkçe](README.md)

Yanımda ("by my side") is a web application for families who apply for services such as home care, companionship and hospital escort for an elderly relative, and for the team that manages those applications.

- **Public interface:** a warm, photo based, mobile first service site. It offers a **quick inquiry form** that needs no account (name, email, service, description) and a trackable **five step application** with an account.
- **Admin panel:** information-dense screens for requests, users and statistics (PrimeVue).
- **API:** Django REST Framework, PostgreSQL, JWT authentication.

> **Status:** The complete backend API, the public interface, one-click start and the Render deployment configuration are ready. The admin panel **screens** were not built (their APIs are ready); see [Known gaps](#known-gaps).

## Delivery

| | |
| --- | --- |
| Live URL | _Added after the Render deployment_ |
| Source code | https://github.com/erhankoclar/yanimda |
| Delivery commit | _Added after the release tag_ |
| AI usage log | [AI_LOG.md](AI_LOG.md) (Turkish) |

Where the evaluation criteria are met:

| Criterion | Where |
| --- | --- |
| Mobile and desktop friendly landing page | Landing page (`frontend/src/views/public/LandingView.vue`); e2e tests run on phone and desktop |
| Form with name, email, service selection and description | The "Talebinizi bırakın" (leave your inquiry) form on the landing page (`InquiryForm.vue`) |
| Client and server side field validation | `frontend/src/utils/inquiryValidation.js` and `backend/apps/care/inquiry_serializers.py` |
| Sending, success and error states | The button reads "Gönderiliyor…" (sending) and the form locks; a success message with the record number; field and general error messages |
| The record is stored permanently on the server | PostgreSQL table `care_serviceinquiry`; visible through `GET /api/admin/inquiries/` |
| Success is shown only when the record is saved | The message appears only after the server returns the saved record with its id; tests cover 4xx, 5xx, network errors and responses without an id |
| README, AI_LOG.md, delivery commit | This file, [AI_LOG.md](AI_LOG.md), the table above |

## Contents

- [Delivery](#delivery)
- [Quick start](#quick-start)
- [Addresses and credentials](#addresses-and-credentials)
- [Stopping and resetting](#stopping-and-resetting)
- [Architecture](#architecture)
- [Business rules](#business-rules)
- [API](#api)
- [Configuration](#configuration)
- [Tests](#tests)
- [Development without the scripts](#development-without-the-scripts)
- [Security notes](#security-notes)
- [Live deployment (Render)](#live-deployment-render)
- [Git workflow](#git-workflow)
- [Known gaps](#known-gaps)
- [Sources and templates](#sources-and-templates)
- [Troubleshooting](#troubleshooting)

## Quick start

All you need to do is run the file for your operating system. The script:

1. installs Docker if it is missing,
2. starts Docker and waits until it is ready,
3. brings up the database, backend and frontend **in order**,
4. opens the site in your browser.

| Operating system | Start | Stop |
| --- | --- | --- |
| Windows 10/11 | Double-click `start-windows.bat` | `stop-windows.bat` |
| macOS | Double-click `start-mac.command` | `stop-mac.command` |
| Linux | `./start-linux.sh` in a terminal | `./stop-linux.sh` |

To skip opening the browser: `start-windows.bat -NoBrowser` on Windows, `--no-browser` on macOS/Linux.

### How Docker is installed

| System | Method | Notes |
| --- | --- | --- |
| Windows | `winget install Docker.DockerDesktop`; without winget the official installer is downloaded and installed silently | Administrator approval is requested. After the first installation you may need to **restart the computer** for WSL 2, then run the script again. |
| macOS | `brew install --cask docker` when Homebrew exists; otherwise the official `.dmg` for your processor (Apple Silicon / Intel) is downloaded | Your password may be requested. Docker Desktop may ask you to accept its license on first launch. |
| Linux | Docker's official `get.docker.com` script (with `sudo`) | `curl` is required. Your user is added to the `docker` group; in the current session commands run with `sudo`, from the next session they do not need it. |

The first start may take a few minutes while images are downloaded; later starts take seconds.

## Addresses and credentials

| What | Address |
| --- | --- |
| Site | http://localhost:5173 |
| Admin panel | http://localhost:5173/admin |
| API docs (Swagger) | http://localhost:8000/api/docs/ |
| API docs (ReDoc) | http://localhost:8000/api/redoc/ |
| PostgreSQL (from the host) | `localhost:5433`, database/user/password: `yanimda` |

An admin account is created automatically for local development:

- Email: `admin@yanimda.local`
- Password: `Yanimda-Admin-2026`

> These credentials are only for development on your own computer and must not be used in production.

Register on the site for an applicant account. The default service types (home care support, companionship, hospital and doctor escort, shopping and housework, health monitoring, small home repairs) are loaded automatically on first start.

## Stopping and resetting

- **Stop:** the `stop-*` scripts or `docker compose down`. Data is kept.
- **Delete all data and start from scratch:** `docker compose down -v`, then the start script.
- **See logs:** `docker compose logs -f backend` (or `frontend`, `db`).

## Architecture

```
yanimda/
├── backend/               Django + DRF API
│   ├── apps/accounts/     Users, registration, JWT, admin user API
│   ├── apps/care/         Service types, requests, admin request and statistics API
│   ├── config/            Settings, URLs, project level tests
│   └── locale/            Turkish translations
├── frontend/              Vue 3 + Vite
│   ├── src/api/           axios client, token storage, API calls
│   ├── src/layouts/       PublicLayout (applicants) and AdminLayout (management)
│   ├── src/router/        Routes and guards
│   ├── src/stores/        Pinia stores
│   ├── src/styles/        Public visual language
│   ├── src/views/         public/ and admin/ pages
│   └── tests/             Tests grouped by type
├── scripts/               Start/stop scripts and their tests
├── docker-compose.yml     The whole stack
└── prd.md                 Product requirements (Turkish)
```

### Backend layers

| Layer | Responsibility |
| --- | --- |
| `services/*_service.py` | All workflows **and read operations** (e.g. `care_request_service.create_request`, `list_for_admin`, `dashboard_service.build_dashboard`). A Celery task, if added, lives in the related service file at module level, not inside a class. |
| `managers.py` | Only methods that return querysets (`active()`, `open()`, `waiting_for_review()`, `with_request_count()`). Services reach models through these managers; managers never import services at module level. Django's required hooks (`create_user`, `create_superuser`, `get_by_natural_key`) delegate to the service. |
| `serializers.py` | Validation and response shape only; no `create`/`update`. Business rule checks ask the service. |
| `views.py` | Permissions, throttles, filters and pagination; reading and saving are delegated to services, and business rule errors from services become 400 responses. |

The rules are guarded by `config/tests/regression/test_architecture.py`: the test fails if a serializer defines `create`/`update`, if a view or serializer builds ORM queries, or if a manager imports services.

### Services and start order

| Service | Image | Port | Healthy when |
| --- | --- | --- | --- |
| `db` | postgres:17-alpine | 5433 → 5432 | `pg_isready` |
| `backend` | python:3.12-slim | 8000 | migrations, default data and admin account are ready and `/api/services/` responds |
| `frontend` | node:22-alpine | 5173 | the Vite dev server responds |

`depends_on: condition: service_healthy` guarantees the order: **db → backend → frontend**. On start the backend compiles translations, applies migrations, loads the default services (`care_create_defaults`, safe to rerun) and creates the admin account if missing. Source folders are mounted into the containers, so changes apply immediately.

The frontend forwards `/api` requests to the backend through the Vite proxy; the browser only talks to `localhost:5173`.

### Technologies

| Layer | Technology |
| --- | --- |
| Backend | Python 3.12, Django 5.2, Django REST Framework, Simple JWT (with token blacklist), drf-spectacular, django-filter, django-environ |
| Database | PostgreSQL 17 (SQLite is not used) |
| Frontend | Vue 3 (`<script setup>`), Vue Router, Pinia, axios, Vite |
| Admin UI | PrimeVue (admin side only, in separately loaded bundles) |
| Tests | Django test runner, Vitest + Vue Test Utils + axe-core, screenshot checks with the Playwright image |

### Two separate interfaces

- **Public** (`PublicLayout`): no PrimeVue, tables or dashboard components. A warm, photo based, full width service site: white base, light sage and peach sections, deep pine green primary (`#1F5F55`), apricot accent (`#F29E4C`) and a dark green footer. Headings use **Bricolage Grotesque** and body text uses **Atkinson Hyperlegible Next**, designed for low-vision readers; base text size is 19 px and tap targets are kept large (at least 44 px). The sticky header turns into a menu on phones. Keyboard focus is always visible, a "Skip to content" link exists and reduced motion is respected. Photos use the Pexels license; their sources are listed in `frontend/public/images/CREDITS.md` and they can be replaced with your own photos under the same names.
- **Admin** (`AdminLayout`): sidebar, top bar, tables, filters, dialogs. All admin pages are loaded in separate (lazy) bundles.

## Business rules

### Quick inquiry form (no account)

- Name (at least 2 characters), a valid email, an active service, a 10–2000 character description and consent are required. The rules are the same on the client and the server; the server always validates again.
- While sending, the button reads "Gönderiliyor…" and the fields lock. The success message appears **only** after the server stores the record and returns its number. On errors the typed data is kept; field errors appear under the fields and other errors above the form.
- The email is stored in lower case, the name with extra spaces removed, and the consent time is recorded.
- A hidden honeypot field stops spam bots and requests are limited to 5 per hour per IP.
- The service cards on the landing page open the form with that service selected.

### Accounts

- Login is **by email and password only**; there are no usernames.
- An email address belongs to **exactly one account**. Comparison ignores case and surrounding spaces (`Ayse@Example.com` = `ayse@example.com`). Emails are stored in lower case; how they are typed at login does not matter.
- Passwords must satisfy Django's password rules (at least 8 characters, not too common, not entirely numeric, not similar to personal data).
- Only first name, last name and phone can be changed in the profile; email and admin rights cannot.
- Admin rights (`is_staff`) cannot be obtained through registration or the profile.
- A disabled account loses access immediately, including its open session.
- A wrong password and an unregistered email return the same error (registered emails cannot be discovered).

### Session (JWT)

- Access tokens live 15 minutes, refresh tokens 7 days.
- Refresh tokens are **rotated** on every refresh and the old one is **blacklisted**; it cannot be reused.
- On logout the refresh token is blacklisted on the server. Even if the server cannot be reached, the browser session is cleared.
- The frontend refreshes an expired access token once automatically; concurrent 401 responses share one refresh request. Tokens are only sent to our own API.
- Redirects after login only go to in-app paths (open redirect protection).

### Applications

- Applying requires login and **consent to personal data processing**; the consent time is stored.
- The preferred date cannot be in the past and can be at most 90 days ahead.
- The elder's age must be between 40 and 120.
- Phone numbers must have 10–15 digits; spaces, parentheses and dashes are removed before saving.
- An alternate contact name and phone must be given together.
- Only active services can be requested. Old applications of a retired service remain visible.
- **Duplicate application rule:** The same user cannot open a new application for **the same service and the same elder** while one is open (new / reviewing / assigned). They can apply again after it is completed or cancelled. The same person may apply for their mother and father separately, or for different services for the same elder. Elder names are compared ignoring case, extra spaces and the Turkish **I/İ/ı/i** variants ("FATMA YILMAZ" = "fatma yilmaz"). The rule is also enforced by a partial unique database constraint, so two simultaneous requests are blocked as well.
- Users see **only their own** applications; another user's application responds with not found (404).
- Users cannot change or delete their applications. The **admin note** is never shown to them.
- Each user can create at most 20 applications per day.

### Status flow

```
new ──► reviewing ──► assigned ──► completed
 │          │             │
 └──────────┴─────────────┴────► cancelled
```

- Steps cannot be skipped or reversed. Completed and cancelled are final.
- Sending the current status again is allowed, so only the admin note can be updated.
- Admins cannot change the personal data in an application; only the status and the admin note (at most 2000 characters) can be updated.

### Admin

- Admin APIs and pages are open only to `is_staff` users. Django's own admin site is not used and not exposed.
- Dashboard: total, open and last 7 days application counts; active applicant count; counts for every status and every service (including zeros); a daily series for the last 14 days.
- User management is read-only for now.

## API

All endpoints live under `/api/`. Use Swagger for detailed field descriptions and a try-it-out screen: http://localhost:8000/api/docs/ (enter `Bearer <access>` with **Authorize** at the top right).

| Method | Path | Access | Description |
| --- | --- | --- | --- |
| POST | `/api/auth/register/` | Anyone | Register |
| POST | `/api/auth/token/` | Anyone | Log in (access + refresh) |
| POST | `/api/auth/token/refresh/` | Anyone | Refresh tokens |
| POST | `/api/auth/logout/` | Anyone | Log out (blacklists the refresh token) |
| GET, PATCH | `/api/auth/me/` | Logged in | Profile |
| GET | `/api/services/` | Anyone | Active services (not paginated) |
| POST | `/api/inquiries/` | Anyone | Quick inquiry form (no account) |
| GET, POST | `/api/requests/` | Logged in | My applications / new application |
| GET | `/api/requests/{id}/` | Logged in | Detail of my application |
| GET | `/api/admin/stats/` | Admin | Dashboard statistics |
| GET | `/api/admin/inquiries/` | Admin | Quick inquiries; `service`, `search` |
| GET | `/api/admin/requests/` | Admin | All applications; `status`, `service`, `applicant`, `created_from`, `created_to`, `search`, `ordering` |
| GET, PATCH | `/api/admin/requests/{id}/` | Admin | Detail; update status and admin note |
| GET | `/api/admin/users/` | Admin | Users with application counts; `is_staff`, `is_active`, `search`, `ordering` |
| GET | `/api/admin/users/{id}/` | Admin | User detail |
| GET | `/api/schema/`, `/api/docs/`, `/api/redoc/` | Anyone (only with `API_DOCS_ENABLED`) | OpenAPI schema and docs |

Lists are paginated by 20: `{count, next, previous, results}`. Error messages are returned in Turkish or English depending on the request language (`Accept-Language`).

## Configuration

Backend settings are read from environment variables. Example file: `backend/.env.example` (copy it to `backend/.env` when running outside Docker). In Docker the values live in `docker-compose.yml`.

| Variable | Default | Description |
| --- | --- | --- |
| `SECRET_KEY` | development key | Django secret key; always change it in production |
| `DEBUG` | `False` | Debug mode |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Allowed hosts |
| `DATABASE_URL` | `postgres://yanimda:yanimda@localhost:5433/yanimda` | PostgreSQL connection |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Frontend origins |
| `API_DOCS_ENABLED` | value of `DEBUG` | Publishes the schema, Swagger and ReDoc |
| `JWT_ACCESS_MINUTES` | `15` | Access token lifetime (minutes) |
| `JWT_REFRESH_DAYS` | `7` | Refresh token lifetime (days) |
| `CARE_MAX_PREFERRED_DAYS_AHEAD` | `90` | Maximum days ahead for the preferred date |
| `DJANGO_SUPERUSER_EMAIL`, `DJANGO_SUPERUSER_PASSWORD` | — | When set, an admin account is created on start if missing |

### Rate limits (throttles)

| Purpose | Scope | Default | Environment variable |
| --- | --- | --- | --- |
| Registration (per IP) | `accounts_register` | `10/hour` | `THROTTLE_ACCOUNTS_REGISTER` |
| Login (per IP) | `accounts_login` | `10/minute` | `THROTTLE_ACCOUNTS_LOGIN` |
| Creating applications (per user) | `care_request_create` | `20/day` | `THROTTLE_CARE_REQUEST_CREATE` |
| Quick inquiry form (per IP) | `care_inquiry_create` | `5/hour` | `THROTTLE_CARE_INQUIRY_CREATE` |

To override them in project settings:

```python
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'accounts_register': '10/hour',
    'accounts_login': '10/minute',
    'care_request_create': '20/day',
    'care_inquiry_create': '5/hour',
}
```

In the local `docker-compose.yml` environment these limits are relaxed because the e2e tests send many requests from one IP; in production (Render) the defaults above apply.

The frontend uses `VITE_API_PROXY_TARGET` (default `http://localhost:8000`) and `VITE_USE_POLLING=true` for file watching on mounted folders on Windows.

## Tests

Tests are grouped by type and the full set runs as a regression check before every change. Tests run **inside the Docker containers, on PostgreSQL**.

### Backend (169 tests)

| Type | Folder | What it checks |
| --- | --- | --- |
| `unit` | `apps/*/tests/unit` | Model rules, status transitions, validators, name key, throttle settings |
| `integration` | `apps/*/tests/integration`, `config/tests/integration` | Endpoint behaviour, filters/search/ordering, default data command, Swagger |
| `security` | `apps/*/tests/security`, `config/tests/security` | Unauthorized access, access to other users' data (IDOR), mass assignment, privilege escalation, token reuse, rate limits, data leaks |
| `regression` | `apps/*/tests/regression`, `config/tests/regression` | Fixed bugs staying fixed, missing migrations, PostgreSQL requirement, Django admin being off |
| `contract` | `apps/*/tests/contract`, `config/tests/contract` | Response shapes the frontend depends on, OpenAPI schema validity without warnings |
| `performance` | `apps/*/tests/performance` | No N+1 queries in lists, constant query counts |
| `scenario` | `config/tests/scenario` | End-to-end business workflows with real registration/login: one email one account, email login, duplicate applications, full lifecycle, family isolation, dashboard |

```bash
docker compose exec backend sh run_tests.sh              # all
docker compose exec backend sh run_tests.sh security     # one type
docker compose exec backend sh run_tests.sh unit scenario
```

### Frontend (170 tests)

| Type | Folder | What it checks |
| --- | --- | --- |
| `unit` | `tests/unit` | Route table, token storage, safe redirects |
| `component` | `tests/component` | Component behaviour (e.g. session aware menu) |
| `integration` | `tests/integration` | HTTP client and token refresh, auth store, routing |
| `security` | `tests/security` | Route guards, tokens never sent to other origins, open redirects |
| `accessibility` | `tests/accessibility` | axe-core audit, skip link, landmarks |

```bash
docker compose exec frontend npx vitest run
docker compose exec frontend npx vitest run tests/security
```

### End to end (Playwright, 18 tests)

The tests in `e2e/` run against the running stack (real frontend, backend and PostgreSQL) on phone and desktop viewports: sending, success and error states of the quick form and the stored record found in the database, server validation when the client is bypassed, registration + five step application + duplicate rejection, and checks for horizontal overflow and console errors.

```bash
docker compose up -d --wait
docker compose --profile e2e run --rm e2e
# Against another address (e.g. the production image):
docker compose --profile e2e run --rm -e E2E_BASE_URL=https://example.onrender.com e2e
```

### Start scripts

The scripts are tested with stub commands that record calls instead of installing anything.

```bash
# macOS and Linux flows (30 checks) — on any system with Docker
docker run --rm -v "$PWD:/src:ro" ubuntu:24.04 bash /src/scripts/tests/start-unix.test.sh
```

```powershell
# Windows flow (20 checks) — Windows PowerShell 5.1 or PowerShell 7
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\tests\start-windows.tests.ps1
```

## Development without the scripts

```bash
docker compose up -d --build --wait          # the whole stack, in order
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py care_create_defaults
docker compose exec backend python manage.py createsuperuser
```

After adding a package, rebuild the image: `docker compose up -d --build -V frontend` (`-V` renews the old `node_modules` volume).

### Translations

User-facing backend texts are written in English and marked with `gettext`; their Turkish versions live in `backend/locale/tr/LC_MESSAGES/django.po`.

```bash
python manage.py makemessages -l tr -e py -e html -e json -i "venv/*" --no-location
python manage.py compilemessages -l tr
```

`.mo` files are not committed; they are compiled when the container starts.

## Security notes

- Passwords and keys in `docker-compose.yml` are for local development only.
- In production use `DEBUG=False`, a strong `SECRET_KEY` and real `ALLOWED_HOSTS`, and remove the `DJANGO_SUPERUSER_*` variables. `API_DOCS_ENABLED` follows `DEBUG` by default, so the docs are off in production.
- The browser keeps tokens in `localStorage`; access tokens are short-lived and refresh tokens are rotated and blacklisted.

## Live deployment (Render)

The root `Dockerfile` builds the Vue site and serves it together with the Django API from a single gunicorn service (WhiteNoise). Page addresses (such as `/requests/5`) go to Vue and `/api/` addresses go to Django.

1. In Render choose **New → Blueprint** and connect this GitHub repository; `render.yaml` is read.
2. Render creates the free PostgreSQL database and the web service; `SECRET_KEY` is generated automatically.
3. When asked, enter a strong password for `DJANGO_SUPERUSER_PASSWORD` (admin email: `admin@yanimda.example`).
4. After the deployment the address is `https://<service-name>.onrender.com`. Migrations, default services and the admin account are prepared automatically on start.

Production notes:
- `DEBUG=False`, HSTS is on and cookies are sent only over HTTPS. Render redirects HTTP to HTTPS; `SECURE_SSL_REDIRECT` stays off in the app, because otherwise Render's internal HTTP health check would get a 301 and fail.
- Swagger is enabled for the evaluation (`API_DOCS_ENABLED=True`); set it to `False` to hide it.
- To try the production image locally: `docker build -t yanimda-prod .` and run it with `DATABASE_URL`, `SECRET_KEY` and `ALLOWED_HOSTS`.

## Git workflow

- Git Flow is used: new features are developed on `feature/*` branches and bug fixes on `hotfix/*` branches; `develop` and `master` are never written to directly.
- Commits are small, meaningful and each one works on its own; all tests run before every commit.
- Commit messages contain an English summary and bullets followed by a Turkish summary and bullets.

## Known gaps

- **The admin panel screens were not built.** The admin APIs (requests, status updates, statistics, users, quick inquiries) are ready and tested; the Vue admin pages only contain a heading for now.
- No email notification is sent for quick inquiries; they are stored and visible through the admin API.
- Applications cannot be edited or cancelled online.
- The contact phone and opening hours are placeholders.
- On Render's free tier the service sleeps when idle (the first request takes about 30 s) and the free PostgreSQL database is deleted after 30 days.
- The macOS and Linux start scripts were tested with stub commands, not on a real macOS or Linux machine.

## Sources and templates

- No project template (boilerplate) was used. The Django skeleton was created with `django-admin startproject/startapp` and the Vite configuration was written by hand. The rest of the code was written for this project.
- The code was produced with AI (Claude Code), guided by the developer's decisions; see [AI_LOG.md](AI_LOG.md) for details.
- Photos: stock photos under the Pexels license; sources are listed in `frontend/public/images/CREDITS.md`.
- Fonts: Atkinson Hyperlegible Next and Bricolage Grotesque via Google Fonts (SIL Open Font License).
- Open source libraries used: `backend/requirements.txt`, `frontend/package.json` and `e2e/package.json`.

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| Windows: "Docker was not ready within 4 minutes" | Restart the computer after the first installation (WSL 2), open Docker Desktop once to accept its terms, run the script again. |
| macOS: Docker does not start | Open Docker Desktop from Applications, accept the license, run the script again. |
| Linux: `permission denied ... docker.sock` | Log out and back in (docker group), or run the commands with `sudo`. |
| Port in use (5173, 8000, 5433) | Close the application using it or change the left-hand port in `docker-compose.yml`. |
| The site opens but no data loads | Check that services are `healthy` with `docker compose ps` and look for errors with `docker compose logs backend`. |
| The frontend cannot find a new package | `docker compose up -d --build -V frontend` |
| Reset everything | `docker compose down -v` and the start script |
