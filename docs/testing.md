# Testing and verification

## Current verified result

The most recent integration pass reported:

- `python manage.py check`: passed with no system-check issues.
- `python manage.py test`: **62 tests passed**.
- `npm.cmd --prefix frontend run build`: passed with Vite.
- Development frontend responded with HTTP 200 for `/dashboard`, `/body-shape`, `/wardrobe`, `/outfits`, `/diet`, `/expenses`, `/daily-plan`, `/profile`, and `/settings`.
- Django URL resolution succeeded for the documented body-shape, wardrobe, outfit, diet, expense, Daily Plan, tracking, profile, and settings routes.
- `git diff --check`: passed at that verification point.

These are verification results for the project revision reviewed in the integration pass; rerun the commands after code changes.

## Run checks on Windows

Backend, from repository root:

```powershell
cd backend
.venv\Scripts\Activate.ps1
python manage.py check
python manage.py test
```

Frontend, in a separate terminal:

```powershell
cd frontend
npm.cmd run build
```

## Route and API checklist

- [ ] Open each frontend route listed in the root README using the Vite URL.
- [ ] Confirm the backend remains running and the browser's `/api` calls succeed for the feature being checked.
- [ ] Resolve/check every endpoint in [api.md](api.md) after changing Django URL configuration.
- [ ] Confirm profile-scoped pages use an existing Profile and do not assume authentication exists.
- [ ] Confirm no sample personal data is presented as real user data.

## Submission/review checklist

- [ ] `python manage.py check` passes.
- [ ] `python manage.py test` passes; record the actual test count and result.
- [ ] `npm.cmd --prefix frontend run build` passes.
- [ ] Dashboard and implemented feature routes load.
- [ ] Documented API paths match `backend/config/urls.py` and each feature's `urls.py`.
- [ ] Check `git status --short` and review all changes.
- [ ] Commit only when the project owner explicitly chooses to do so; this documentation pass does not stage or commit changes.
