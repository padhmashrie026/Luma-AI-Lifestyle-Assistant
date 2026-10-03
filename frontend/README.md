# AI Lifestyle Assistant frontend

React interface for the AI Lifestyle Assistant. The feature pages connect to the Django APIs through the shared client in `src/services/apiClient.js`; data and summaries come from backend responses rather than sample dashboard values.

## Run locally

From this folder:

```powershell
npm.cmd install
npm.cmd run dev
```

Vite prints the local URL, usually `http://localhost:5173`. Build production assets with:

```powershell
npm.cmd run build
```

During development, requests to `/api` are proxied to Django at `http://127.0.0.1:8000`. `VITE_API_BASE_URL` configures the API base URL, and `VITE_API_PROXY_TARGET` configures the development proxy target.

## Pages

- `/dashboard` — links to implemented modules without sample personal activity.
- `/body-shape` — approximate styling guidance.
- `/wardrobe` — wardrobe item management.
- `/outfits` — rule-based outfit suggestions.
- `/diet` — weekly meal plan preview.
- `/expenses` — expense records and API summaries.
- `/daily-plan` — daily plans and tracking check-ins.
- `/profile` and `/settings` — existing profile and currency preference APIs.
- `/insights` — placeholder; no Insights API exists yet.

The backend has no application authentication. Profile-based pages use an existing `profile_id` as a temporary development selector; this is not secure multi-user authorization. See the root README for backend setup and API details.

For the full project submission documentation, see [`../docs/setup.md`](../docs/setup.md), [`../docs/architecture.md`](../docs/architecture.md), and [`../docs/api.md`](../docs/api.md). The backend test and frontend build commands are listed in [`../docs/testing.md`](../docs/testing.md).
