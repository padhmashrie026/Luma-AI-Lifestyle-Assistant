# AI Lifestyle Assistant

An MCA mini project for organizing lifestyle planning. The project is being built one feature at a time; this repository currently contains only the initial React and Django setup.

## Project structure

- `frontend/` — React interface built with Vite and JavaScript.
- `backend/` — Django and Django REST Framework API project; SQLite is used for local development.
- `docs/` — project documentation.

The frontend and backend run as separate development servers. The frontend uses Vite on port 5173, and Django serves the backend on port 8000. API requests can be added through a frontend service layer as features are developed.

## Requirements

- Node.js 20.19+ or 22.12+ (the installed Node.js 24.19.0 is supported by Vite 8).
- Python 3.10 or newer.

## Start the frontend

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite (usually `http://localhost:5173`).

## Start the backend

```powershell
cd backend
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

The Django server runs at `http://127.0.0.1:8000/`. The initial setup provides Django's admin route at `/admin/`; application API endpoints will be added with future features.

## Notes

The Django secret key in the initial development settings is for local development only. Before deployment, move it to an environment variable and set production security options. Do not put real secrets in source control.
