# API reference

All endpoints are rooted at `/api/`. The development server is `http://127.0.0.1:8000`. JSON request bodies are expected where a body is listed. `<id>` is a database primary key. DRF returns validation errors as JSON and uses standard HTTP method semantics. No API in this list requires login in the current development configuration.

## Body Shape

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/body-shape/calculate/` | Accepts required numeric `shoulder`, `bust`, `waist`, and `hip` measurements and returns approximate rule-based styling guidance. It does not persist measurements. |

## Smart Wardrobe

| Method | Path | Purpose |
|---|---|---|
| `GET`, `POST` | `/api/wardrobe/items/` | List items or create an item. List filters: `category`, `color`, `status`. |
| `GET`, `PUT`, `PATCH`, `DELETE` | `/api/wardrobe/items/<id>/` | Retrieve, replace/update, or delete an item. |

Item fields are `profile`, `name`, `category`, `color`, `brand`, `size_label`, `status`, and `notes` (plus read-only IDs/timestamps). Categories: `top`, `bottom`, `dress`, `outerwear`, `shoes`, `accessory`, `other`. Statuses: `available`, `laundry`, `repair`, `archived`.

## Outfit Recommendation

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/outfits/recommend/` | Returns a rule-based suggestion from available wardrobe items. |

Request fields: required `profile_id` and `occasion`; optional `body_shape`. Occasions: `everyday`, `work`, `formal`, `event`, `other`. Body-shape choices are `hourglass`, `pear`, `apple`, `rectangle`, and `inverted_triangle`. The service can use the latest saved measurement label if a label is omitted and one exists. Recommendations are not saved by this endpoint. Season is not a supported field.

## Diet Planner

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/diet/plan/` | Builds a seven-day meal-plan preview for existing profile meals and food preferences. |

Request fields: `profile_id` and `week_start` (date). Response includes `plan_available`, weekly meals, grocery-list information, and explanation/notes. The response explicitly marks a generated plan as unsaved. Budget estimates are unavailable because stored meal/ingredient data have no price amounts.

## Expense Manager

| Method | Path | Purpose |
|---|---|---|
| `GET`, `POST` | `/api/expenses/` | List or create expenses. Supported filters: `profile_id`, `category_id`, `category`, `daily_plan_id`, `month`, `start_date`, `end_date`, and `q`. |
| `GET` | `/api/expenses/summary/?profile_id=<id>&month=YYYY-MM` | Return profile total spending, requested-month spending, category breakdown, and budget status. `month` is optional and defaults to the current local month. |
| `GET`, `PUT`, `PATCH`, `DELETE` | `/api/expenses/<id>/` | Retrieve, replace/update, or delete an expense. |

Expense fields: `profile`, `category`, optional `daily_plan`, `description`, positive `amount` (up to two decimal places), `spent_on`, and `notes`. Categories are existing profile-owned BudgetCategory records, not a fixed API choice list. A linked Daily Plan must belong to the same profile and date.

## Daily Plan

| Method | Path | Purpose |
|---|---|---|
| `GET`, `POST` | `/api/lifestyle/daily-plan/` | List or create a plan. Query filters: `profile_id`, `start_date`, `end_date`. |
| `GET`, `PUT`, `PATCH`, `DELETE` | `/api/lifestyle/daily-plan/<id>/` | Retrieve, replace/update, or delete a plan. |

Fields: `profile`, `plan_date`, optional `outfit`, optional `meal_plan`, and `notes`. One plan per profile and date is allowed. Linked records must belong to the same profile; a linked meal plan must use the same date. The endpoint does not accept arbitrary task or habit lists.

## Tracking

| Method | Path | Purpose |
|---|---|---|
| `GET`, `POST` | `/api/tracking/` | List or create daily check-ins. Query filters: `profile_id`, `start_date`, `end_date`. |
| `GET`, `PATCH`, `PUT` | `/api/tracking/<id>/` | Retrieve/update a tracking record. |
| `GET` | `/api/tracking/summary/?profile_id=<id>&start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` | Return totals and per-field/daily progress for the date range. Date range is optional; defaults are handled by the API. |

Fields: `profile`, optional `daily_plan`, `track_date`, `outfit_completed`, `meals_completed`, `expenses_reviewed`, `daily_plan_completed`, and `notes`. One record per profile/date is allowed. Summary percentages and counts are computed by the backend from these four boolean fields.

## Profile and Settings

| Method | Path | Purpose |
|---|---|---|
| `GET`, `PATCH` | `/api/profile/?profile_id=<id>` | Retrieve/update the existing linked profile and Django user fields. |
| `GET`, `PATCH` | `/api/settings/?profile_id=<id>` | Retrieve/update the profile's `currency_code`. |

Profile response fields include read-only `id`, `username`, `created_at`, `updated_at`, and editable `first_name`, `last_name`, `email`, `display_name`. Settings fields are read-only `profile_id` and editable three-letter `currency_code`. Both require an existing profile ID.

## Authentication and ownership note

These routes are open in the current development configuration and accept explicit IDs. They do not authenticate a person or enforce user-level ownership. Do not treat a profile ID as an access token or deploy these endpoints with real personal data until authentication and authorization are implemented.
