# Windows setup and operation

## Requirements

- Windows with PowerShell.
- Python 3.10 or later (Django 5.2 requirement).
- Node.js `^20.19.0` or `>=22.12.0` (Vite 8 and its React plugin package requirement).
- npm, installed with Node.js.

## Backend setup

From the repository root, open PowerShell:

```powershell
cd backend
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Django serves at `http://127.0.0.1:8000/`. Keep this terminal open while using the frontend. To access the Django admin and create development records:

```powershell
# In a second backend terminal, activate the same environment first
cd backend
.venv\Scripts\Activate.ps1
python manage.py createsuperuser
```

Then visit `http://127.0.0.1:8000/admin/`. Create a Django user, then an associated Profile through the Profile admin. Create any profile-owned meals, preferences, wardrobe items, budget categories, or other records needed to explore a feature; the project does not seed fictional data.

If PowerShell blocks virtual-environment activation, use the current PowerShell session's standard execution-policy guidance for local scripts, or run the interpreter directly as `backend\.venv\Scripts\python.exe` from the repository root. Do not change machine-wide policy just for this project.

## Frontend setup

Open a second PowerShell terminal at the repository root:

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Open the local address printed by Vite, normally `http://localhost:5173`. The Vite config forwards `/api` requests to Django at `http://127.0.0.1:8000` by default.

Optional environment settings can be placed in a local `frontend/.env.local` file:

```text
VITE_API_BASE_URL=/api
VITE_API_PROXY_TARGET=http://127.0.0.1:8000
```

`VITE_API_BASE_URL` is read by the shared client. `VITE_API_PROXY_TARGET` configures Vite's development proxy. Do not put secrets in `VITE_*` values: frontend values are delivered to the browser.

## Production build preview

```powershell
cd frontend
npm.cmd run build
npm.cmd run preview
```

This builds and previews static frontend assets; it does not deploy the backend or configure production hosting.

## Common startup problems

- **`py` or Python is not found:** install Python and enable its launcher/PATH option, then reopen PowerShell. Check with `py --version`.
- **Virtual environment activation is blocked:** use the environment activation guidance above or call `.venv\Scripts\python.exe` directly.
- **`No module named django` or DRF:** activate `backend\.venv` and run `python -m pip install -r requirements.txt` from `backend`.
- **Frontend reports unsupported Node:** install a Node release matching `^20.19.0` or `>=22.12.0`, then reopen PowerShell and reinstall with `npm.cmd install` if needed.
- **Frontend cannot reach the API:** keep Django running on port 8000. If it uses another host/port, set `VITE_API_PROXY_TARGET` and restart Vite.
- **Django reports an unapplied migration:** run `python manage.py migrate` in the activated backend environment.
- **Vite chooses another port because 5173 is busy:** use the URL it prints. The development proxy remains configured for that Vite server.
- **Profile-scoped page asks for a profile ID or returns 404:** create a Django user and associated Profile in `/admin/`; profile IDs are not usernames and are not automatically seeded.

## Production preparation

The repository does not contain a production deployment configuration. Before a real deployment, configure a production-grade database and backups, load `SECRET_KEY` from a secret store/environment, set `DEBUG=False`, configure trusted `ALLOWED_HOSTS`, HTTPS and secure cookie/proxy settings, and restrict CORS/CSRF origins to the deployed site. Implement and enforce authentication and per-user authorization before exposing profile-scoped data. Configure static asset serving/build hosting, environment-specific API URLs, database migrations, logging/monitoring, and a tested backup/restore process. Review data privacy and retention for personal measurements, profile details, and expenses. The current SQLite/local development setup is not a production deployment.
