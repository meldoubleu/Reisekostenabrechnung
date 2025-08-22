# Reisekostenabrechnung (MVP)

FastAPI backend + OCR (Tesseract) + PDF export. Local setup with Python venv.

## Stack
- Backend: FastAPI
- DB: SQLite by default (switchable to Postgres via DATABASE_URL)
- OCR: Tesseract via pytesseract
- PDF: ReportLab
- Storage: Local filesystem (uploads/)

## Prerequisites (macOS)
- Python 3.11+ (3.12 recommended)
- Homebrew
- Tesseract OCR and Poppler for PDF OCR
  - brew install tesseract poppler

## 1) Setup
- Copy env: cp .env.example .env (optional; defaults are fine)
- Run setup script:
  - chmod +x scripts/dev_setup.sh scripts/run_api.sh
  - ./scripts/dev_setup.sh

This creates .venv and installs Python deps.

## 2) Run API
- ./scripts/run_api.sh
- API docs: http://localhost:8000/docs

Env vars:
- DATABASE_URL: default sqlite+aiosqlite:///./app.db
- SECRET_KEY: devsecret
- UPLOAD_DIR: ./uploads

## Notes
- First run will create SQLite DB and tables automatically (MVP).
- Postgres is supported: set DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/dbname
