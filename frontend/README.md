# AI Lifestyle Assistant frontend

This React and Vite app contains the responsive layout and dashboard foundation for the AI Lifestyle Assistant. Dashboard examples are demo content; the feature modules are placeholders while they are being developed.

## Run locally

From this folder, install the existing project dependencies and start the development server:

```bash
npm install
npm run dev
```

Vite prints a local URL in the terminal. Open it in a browser to use the app. Build the production files with:

```bash
npm run build
```

## Pages

- `/dashboard`
- `/body-shape`
- `/wardrobe`
- `/outfits`
- `/diet`
- `/expenses`
- `/daily-plan`
- `/insights`
- `/profile`
- `/settings`

The feature pages are intentionally informational placeholders at this stage, except for the Body Shape Calculator, Smart Wardrobe, and Outfit Recommendation.

## Django API connection

The Body Shape Calculator sends measurements to `POST /api/body-shape/calculate/`. Smart Wardrobe uses the `/api/wardrobe/items/` collection and item detail URLs for CRUD operations. Outfit Recommendation sends `profile_id`, `occasion`, and an optional `body_shape` to `POST /api/outfits/recommend/`. During local development, Vite forwards `/api` requests to Django at `http://127.0.0.1:8000`; start Django with `python backend/manage.py runserver` from the project root. Set `VITE_API_BASE_URL` when the API is hosted at another base URL.
