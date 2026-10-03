# AI Lifestyle Assistant

An MCA mini project for organizing everyday clothing, meal planning, expenses, and routine progress in one place. It provides a React dashboard backed by a Django REST API, with a shared profile record connecting profile-scoped data.

The application is intended as a practical personal organization tool. Its body-shape output is approximate styling guidance, outfit suggestions use transparent rules over saved wardrobe items, and meal planning is a general planning aid rather than medical or nutrition advice.

## Technology stack

- **Frontend:** React 19, Vite 8, JavaScript, and CSS.
- **Backend:** Python, Django 5.2, Django REST Framework, and `django-cors-headers`.
- **Database:** SQLite for local development.
- **Tests:** Django's test framework and the production Vite build.

## Main modules

- **Body Shape:** submits four measurements to a rule-based calculator and displays approximate styling guidance. The calculator request does not save measurements.
- **Smart Wardrobe:** creates, lists, filters, edits, and deletes saved wardrobe items.
- **Outfit Recommendation:** recommends a combination from available wardrobe items for an occasion. It may use a supplied body-shape label or an existing saved measurement. It does not save the generated recommendation.
- **Diet Planner:** builds a seven-day preview using meals and food preferences already saved for a profile. The API reports the generated plan as unsaved; the current frontend does not persist it. No food prices are stored, so the API does not estimate a budget.
- **Expense Manager:** records and filters expenses and displays totals, category spending, and budget status from the API.
- **Daily Plan & Tracking:** saves daily plans with optional existing outfit/meal-plan references and notes. Tracking records four check-ins and the API returns progress summaries.
- **Profile & Settings:** reads and updates fields on an existing Django user/profile and its currency preference.
- **Insights:** the route is a placeholder and has no API.

## Architecture

The React application is in `frontend/`. `src/App.jsx` maps browser paths to pages, reusable layout/components live in `src/components/`, pages live in `src/pages/`, and endpoint-specific functions live in `src/services/`. `apiClient.js` is the shared HTTP client. Vite proxies `/api` to Django while developing.

The Django project is in `backend/`. `config/` holds project settings and root URL registration; feature apps in `apps/` hold their models, serializers, views, URLs, and tests. Some calculations are kept in service modules such as `outfits/recommendations.py`, `diet/planning.py`, `expenses/summaries.py`, and `tracking/summaries.py`. The local database is `backend/db.sqlite3`.

See [architecture](docs/architecture.md), [setup](docs/setup.md), and [API reference](docs/api.md) for detail.

## Project structure

```text
backend/
  config/                 Django settings and root URLs
  apps/                   Feature models, serializers, views, URLs, services, and tests
  manage.py
frontend/
  src/components/         Shared dashboard and form components
  src/pages/              Dashboard and feature pages
  src/services/           Shared API client and feature request functions
  vite.config.js
docs/                     Setup, architecture, API, and testing references
```

## Windows development setup

Use separate PowerShell terminals for the backend and frontend. The commands below are run from the repository root.

### Backend

```powershell
cd backend
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

The API is served at `http://127.0.0.1:8000/`. To use profile-based modules, create a Django user and an associated Profile record. A superuser can be created with `python manage.py createsuperuser` and records can be managed at `/admin/`.

### Frontend

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Open the local URL Vite prints (normally `http://localhost:5173`). Vite proxies `/api` to `http://127.0.0.1:8000`. `VITE_API_BASE_URL` changes the API base URL; `VITE_API_PROXY_TARGET` changes the development proxy target. The installed Vite and React plugin packages require Node.js `^20.19.0` or `>=22.12.0`.

The complete Windows commands and troubleshooting notes are in [docs/setup.md](docs/setup.md).

## Routes

- `/dashboard`
- `/body-shape`
- `/wardrobe`
- `/outfits`
- `/diet`
- `/expenses`
- `/daily-plan`
- `/profile`
- `/settings`
- `/insights` (placeholder)

## Verification

At the most recent integration verification, `python manage.py check` passed, the full Django suite passed **62 tests**, the Vite production build passed, all listed frontend routes returned HTTP 200 from the development server, and all documented API paths resolved in Django. See [docs/testing.md](docs/testing.md) for commands and the final checklist.

## Development and deployment limitations

Application authentication is not implemented. Profile-based APIs accept an explicit `profile_id` and are open in the development configuration; this is not secure multi-user access control. The Profile and Settings pages require an existing profile ID. The project settings use `DEBUG = True`, a development-only Django secret key, SQLite, and local CORS origins. These settings are for local work and must be replaced or secured before deployment. No production deployment is configured; see [docs/setup.md](docs/setup.md#production-preparation).
