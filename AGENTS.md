# AI Lifestyle Assistant — Development Instructions

## Project context

AI Lifestyle Assistant is an MCA mini project. The developer is a beginner, so keep the work incremental and explain important decisions in clear, practical language.

The application is planned to include:

- User profile
- Body Shape Calculator
- Smart Wardrobe
- Outfit Recommendation
- Budget-Based Diet Planner
- Meal Preparation
- Grocery List
- Expense Manager
- Personalized Daily Lifestyle Plan
- Daily, weekly, and monthly tracking

Do not implement the whole application in one step. Work on one feature at a time and follow the approved project architecture.

## Architecture and technology

Keep the frontend and backend clearly separated.

- **Frontend:** React. Build reusable components, keep the UI responsive and professional, and place API calls in a service layer.
- **Backend:** Python, Django, and Django REST Framework. Keep business logic organized and maintainable.
- **Development database:** SQLite.

Before adding a new app, component, service, or pattern, inspect the existing project and reuse what is already suitable.

## Working process

1. Before changing code, inspect the relevant files and understand the existing implementation.
2. Implement only the requested feature or change. Do not rewrite unrelated files or replace working features unnecessarily.
3. Prefer simple, readable solutions that a beginner can follow. Avoid unnecessary abstractions and dependencies.
4. Validate user input and provide appropriate loading, error, and empty states.
5. Do not hardcode values that should be stored in or retrieved from the database.
6. Never expose passwords, API keys, tokens, or other secrets in source code, logs, or client-side bundles.
7. After meaningful changes, run relevant tests or checks and fix issues without broad, unrelated changes.
8. Update the README when setup or usage instructions change.
9. Explain important changes and how to run or verify them in beginner-friendly language.

## Accuracy and user-facing claims

- Do not claim that the application uses AI unless a real AI capability has been implemented and its role is accurately described. Describe transparent rule-based behavior as rule-based recommendations.
- Present body-shape and size results as approximate styling guidance, not definitive assessments.
- Present meal recommendations as general planning suggestions, not medical advice or dietary prescriptions.
- Present expense and budget features as organizational tools, not professional financial advice.

## Scope discipline

- Do not build the entire application in one change.
- Do not create duplicate components, services, or business logic.
- Keep changes consistent with the existing, approved architecture.
- If an important architectural choice is not yet established, inspect the repository and explain the proposed choice before expanding the project structure.
