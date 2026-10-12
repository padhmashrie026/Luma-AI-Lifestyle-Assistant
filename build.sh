#!/usr/bin/env bash
set -euo pipefail

# Render runs this from the repository root. Django serves the compiled React
# files from the same origin as the API so session cookies and CSRF work normally.
python -m pip install -r backend/requirements.txt
npm --prefix frontend ci
npm --prefix frontend run build

mkdir -p backend/static_src
cp -R frontend/dist/. backend/static_src/

python backend/manage.py collectstatic --noinput
