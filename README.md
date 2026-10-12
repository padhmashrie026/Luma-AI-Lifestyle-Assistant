# Luma — AI Lifestyle Assistant

Luma is an MCA mini project that brings everyday lifestyle organization into one web application. Users can manage a personal profile, organize wardrobe and meal information, plan daily routines, track check-ins, and review expense and activity summaries.

The project keeps React and Django REST Framework as separate codebases, and production serves both from one Render web service and one origin. The name describes the project concept; current recommendations and calculations are transparent rule-based features, with no external AI service integration.

## Project objectives

- Build a beginner-friendly full-stack application with a responsive interface and a REST API.
- Keep personal records associated with the signed-in account.
- Bring clothing organization, meal planning, expense tracking, and daily planning into one place.
- Use simple, explainable calculations and present their limits clearly.
- Demonstrate modular frontend and backend organization suitable for an MCA mini project.

## Features

- **Authentication:** registration, login, logout, and current-account details using Django sessions.
- **Profile and settings:** update profile details and a preferred currency for the signed-in account.
- **Body Shape guidance:** enter measurements for approximate, rule-based styling guidance; saved measurements are managed separately. Results are not medical or definitive assessments.
- **Smart Wardrobe:** add, view, filter, edit, and remove personal wardrobe items.
- **Outfit recommendations:** receive an occasion-based suggestion from available wardrobe items, using transparent rules. Generated recommendations are not saved as outfits.
- **Diet Planner:** preview a seven-day plan from saved meals and food preferences. The preview is not persisted.
- **Expenses:** manage expenses and budget categories, filter records, and review spending summaries.
- **Daily planning:** create and manage daily plans with optional links to saved outfits and meal plans.
- **Tracking:** save daily check-ins for outfit, meals, expense review, and plan completion; review progress over a date range.
- **Insights:** review personal record counts, date-filtered spending by category, and tracking progress. New accounts receive an empty state.

## Technology stack

Versions below are taken from the project manifests. Version ranges indicate supported dependencies; npm resolves specific package versions in `frontend/package-lock.json`.

| Area | Technology |
| --- | --- |
| Frontend | React and React DOM `^19.2.8`, JavaScript (ES modules), CSS |
| Frontend tooling | Vite `^8.3.0`, `@vitejs/plugin-react` `^6.1.1` |
| Backend language | Python 3.10 or later (Django 5.2 minimum) |
| Backend framework | Django `>=5.2,<6.0`, Django REST Framework `>=3.16,<4.0` |
| Cross-origin support | `django-cors-headers >=4.7,<5.0` |
| Development database | SQLite |
| Production database | Neon PostgreSQL through `DATABASE_URL` and `psycopg` |
| Production web server/static files | Gunicorn and WhiteNoise |

The frontend toolchain requires Node.js `^20.19.0` or `>=22.12.0` and npm, according to the package engine requirements.

## Project structure

```text
.
├── build.sh                     # Render build: install, build React, collect Django static files
├── backend/
│   ├── config/                  # Django settings and root URL configuration
│   ├── apps/
│   │   ├── body_shape/          # Profile, authentication, and body-shape guidance
│   │   ├── wardrobe/            # Wardrobe records and API
│   │   ├── outfits/             # Outfit records and recommendations
│   │   ├── diet/                # Meals, preferences, and weekly plan preview
│   │   ├── expenses/            # Expenses, budget categories, and summaries
│   │   ├── lifestyle/           # Daily plans
│   │   ├── tracking/            # Daily check-ins and progress summaries
│   │   └── insights/            # Personal overview API
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── public/                  # Static public assets
│   ├── src/
│   │   ├── auth/                # Frontend account state
│   │   ├── components/          # Shared interface components
│   │   ├── pages/               # Dashboard and feature pages
│   │   ├── services/            # API client and feature request functions
│   │   ├── App.jsx              # Route-to-page mapping
│   │   └── App.css              # Application styles
│   ├── index.html
│   ├── package.json
│   └── vite.config.js           # Development API proxy
├── docs/                        # Setup, architecture, API, and testing notes
└── README.md
```

## Prerequisites

- Windows 10 or later with PowerShell.
- Python 3.10 or later and the Python launcher (`py`).
- Node.js `^20.19.0` or `>=22.12.0`, which includes npm.
- Git, if cloning the repository.

## Install and run on Windows

Open **two PowerShell terminals** in the project folder. Run the backend and frontend in separate terminals and leave both running while using the application.

### Terminal 1: Django backend

From the project root:

```powershell
cd backend
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

The backend runs at `http://127.0.0.1:8000/`. Django creates or updates the local SQLite database at `backend/db.sqlite3` when migrations run.

### Terminal 2: React frontend

From the project root in the second terminal:

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Open the local address printed by Vite, normally `http://localhost:5173`. During development, Vite forwards `/api` requests to Django at `http://127.0.0.1:8000`. Change the proxy target with `VITE_API_PROXY_TARGET` or the browser API base with `VITE_API_BASE_URL`. Put optional values in a local `frontend/.env.local` file. Do not put secrets in `VITE_*` variables because frontend values are exposed to the browser.

New users can register in the application. The backend creates a Profile for each registered account. Existing Django accounts get a Profile when account details are first accessed if one does not already exist.

## Tests and production build

Run backend checks and tests from the `backend` directory after activating the virtual environment:

```powershell
python manage.py check
python manage.py test
```

Build the frontend from the project root:

```powershell
npm.cmd --prefix frontend run build
```

The frontend production build is written to `frontend/dist/`. Render's root build script copies these files into Django's static source directory before collecting them.

## Deploy to Render with Neon PostgreSQL

Create one **Render Web Service** for this repository. Leave its Root Directory blank so the root `build.sh` can build both applications. Do not create a separate frontend service: Django serves the built React page, the `/api/` routes, and WhiteNoise static files from the same origin. This keeps the existing Django session cookie and CSRF-token flow on one host.

Use these Render service settings:

| Setting | Value |
| --- | --- |
| Runtime | Python 3 |
| Build Command | `bash build.sh` |
| Start Command | `cd backend && python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT` |

Add these environment variables in the Render service dashboard:

| Variable | Value |
| --- | --- |
| `DJANGO_SECRET_KEY` | A newly generated, private Django secret key |
| `DEBUG` | `false` |
| `DATABASE_URL` | The Neon PostgreSQL connection string, stored only in Render's environment settings |
| `ALLOWED_HOSTS` | Optional comma-separated extra hostnames; Render's `RENDER_EXTERNAL_HOSTNAME` is added automatically |
| `CSRF_TRUSTED_ORIGINS` | Optional comma-separated HTTPS origins; Render's service origin is added automatically |

In Neon, create a database and copy its connection string into Render's `DATABASE_URL` setting. The Django configuration requires SSL for PostgreSQL connections. Keep the secret and database URL out of Git and frontend `VITE_*` variables. Render terminates HTTPS and supplies its hostname; Django trusts the forwarded HTTPS header and uses secure session and CSRF cookies when `DEBUG=false`.

The live Neon database starts separately from the local SQLite database at `backend/db.sqlite3`. Deploy-time migrations create the live schema, but they do not copy your local development records. If you need sample or real records online, add them to the cloud database deliberately after deployment.

The frontend continues to call the relative `/api` path. Vite's development server still proxies `/api` to local Django; production assets are built under `/static/` and served by WhiteNoise from the same Render service.

## Authentication and personal-data ownership

The API uses Django session authentication and CSRF protection for browser requests. Registration, login, and the CSRF-token endpoint are available without an existing session. Personal profile, wardrobe, outfit, diet, expense, daily-plan, tracking, and Insights APIs require authentication and resolve ownership from the signed-in Django user. Client-supplied profile IDs do not grant access to another user's records.

The body-shape calculation endpoint accepts measurement values without requiring a session and returns an unsaved styling estimate. Saved measurement records belong to the signed-in user's Profile. Local development settings are intended for learning and local use; do not expose them to real users or sensitive data as-is.

## Known limitations

- There is no external AI integration. Outfit suggestions, body-shape guidance, diet-plan previews, and Insights use application rules and stored data.
- Body-shape output is approximate styling guidance, not a scientific or medical diagnosis. Clothing sizes vary by brand.
- Weekly meal plans are previews and are not saved. The project does not store meal or ingredient prices, so it cannot estimate a diet budget. Ingredient-name matches are planning hints, not nutrition analysis.
- Expense tools organize records and budget categories; they do not provide professional financial advice.
- Outfit recommendations are returned as suggestions and are not saved automatically.
- Insights summarizes implemented record counts, expenses, and tracking; it is not a predictive analytics system.
- Local development uses SQLite and a development-only secret-key fallback. Production requires `DJANGO_SECRET_KEY`, sets `DEBUG=false`, and uses Neon PostgreSQL when `DATABASE_URL` is configured.
- The frontend package defines a production build script but no automated frontend test script. Backend tests use Django's test runner.
