#!/usr/bin/env zsh
set -euo pipefail

if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

source .venv/bin/activate

export DATABASE_URL=${DATABASE_URL:-"sqlite+aiosqlite:///./app.db"}
export SECRET_KEY=${SECRET_KEY:-"devsecret"}
export UPLOAD_DIR=${UPLOAD_DIR:-"$(pwd)/uploads"}

python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
