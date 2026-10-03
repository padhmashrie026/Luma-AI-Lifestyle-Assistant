# Architecture

## System overview

```text
Browser (React + Vite)
  pages -> feature services -> shared apiClient -> /api/*
                                            |
                                   Vite development proxy
                                            |
Django URL configuration -> feature app URLs -> views -> serializers
                                                   -> models / service modules
                                            |
                                      SQLite database
```

The frontend and backend are separate applications. The browser owns presentation, input state, and calls to the API; the backend owns validation, persistence, and summary/calculation rules. The frontend does not contain a second API client or calculate backend-owned expense/tracking summaries.

## Frontend

- `frontend/src/App.jsx` holds the current path-to-page mapping and navigation state.
- `frontend/src/components/` contains the shared shell, sidebar, header, buttons, cards, icons, and section headers.
- `frontend/src/pages/` contains the route-level feature screens.
- `frontend/src/services/apiClient.js` provides the shared `fetch` wrapper, JSON handling, and normalized request errors.
- The other files in `frontend/src/services/` provide feature-specific request functions.
- `frontend/vite.config.js` proxies `/api` to `VITE_API_PROXY_TARGET`, defaulting to `http://127.0.0.1:8000`.
- `VITE_API_BASE_URL` changes the API base URL used by the shared client (default `/api`).

## Backend

- `backend/config/settings.py` configures installed Django apps, middleware, SQLite, timezone, and development CORS origins.
- `backend/config/urls.py` includes feature URL modules below `/api/`.
- `backend/apps/` contains the feature Django apps. A typical API flow is URL pattern -> view -> DRF serializer -> model/queryset.
- Business calculations are separated where useful: body shape calculation, outfit recommendations, diet planning, expense summaries, and tracking summaries.
- `backend/db.sqlite3` is the local development database created by migrations.

## Shared data relationships

`body_shape.Profile` is the profile root and is linked one-to-one to Django's user model. Wardrobe items, meals/preferences, outfits, expenses, Daily Plans, and tracking records reference that profile. Daily Plans can optionally refer to an existing outfit and meal plan. Tracking can optionally refer to a Daily Plan.

The interfaces do not create all those related records automatically. For example, a diet plan response is a preview marked unsaved, and the body-shape calculation endpoint accepts measurements without saving them. The Outfit API returns a recommendation rather than creating an Outfit record.

## Development identity model

Django's user and profile models exist, but application authentication is not wired into the feature APIs. Several APIs use a caller-provided `profile_id`; current views allow anonymous requests. This is a local development assumption, not authorization or tenant isolation. Do not expose this setup to real users or data.
