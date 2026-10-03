# AI Lifestyle Assistant

An MCA mini project with a React frontend and a Django REST Framework backend. The project uses SQLite for local development and is being built feature by feature.

## Project structure

- `frontend/` — React and Vite user interface.
- `backend/` — Django, Django REST Framework, and SQLite API.

## Requirements

- Node.js 20.19+ or 22.12+.
- Python 3.10 or newer.

## Run locally

Start the backend in one PowerShell terminal:

```powershell
cd backend
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Start the frontend in a second terminal:

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Open the local URL printed by Vite (usually `http://localhost:5173`). During development, Vite forwards `/api` requests to Django at `http://127.0.0.1:8000`. Set `VITE_API_BASE_URL` to use a different API base URL, or `VITE_API_PROXY_TARGET` to change the Vite proxy target.

## Available modules and APIs

- **Body Shape Calculator:** `POST /api/body-shape/calculate/` returns approximate, rule-based styling guidance; it does not save measurements.
- **Wardrobe:** `GET/POST /api/wardrobe/items/` and `GET/PUT/PATCH/DELETE /api/wardrobe/items/<id>/` manage saved items.
- **Outfit Recommendation:** `POST /api/outfits/recommend/` returns a rule-based suggestion from available wardrobe items.
- **Diet Planner:** `POST /api/diet/plan/` returns a seven-day preview based on saved meals; generated plans are not saved.
- **Expense Manager:** `/api/expenses/` supports list/create and detail retrieval/update/delete. `GET /api/expenses/summary/?profile_id=<id>` returns spending and budget summaries.
- **Daily Plan:** `/api/lifestyle/daily-plan/` supports list/create and detail retrieve/update/delete.
- **Tracking:** `/api/tracking/` supports list/create and detail retrieve/update. `GET /api/tracking/summary/?profile_id=<id>` returns completion summaries.
- **Profile and Settings:** `GET/PATCH /api/profile/?profile_id=<id>` and `GET/PATCH /api/settings/?profile_id=<id>` use existing Profile and Django User records.
- **Insights:** the sidebar route is a placeholder; no Insights API is implemented.

## Development assumptions

Application authentication is not implemented. APIs that need a profile accept a `profile_id`; this is a development convenience, not a secure way to identify or authorize a user. Create Django users and their associated profiles through the Django admin or project data setup before using profile-based modules. The Profile API edits existing records and does not create users or profiles.

The Django secret key currently in `backend/config/settings.py` is a development-only value. Do not use it for a deployed application or replace it with a real secret in source control.

## Run backend checks

```powershell
cd backend
python manage.py check
python manage.py test
```
