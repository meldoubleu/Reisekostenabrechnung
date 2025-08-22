# Reisekostenabrechnung (MVP)

FastAPI backend + OCR (Tesseract) + PDF export + Simple frontend. Local setup with Python venv.

## 🎯 Features
- ✅ **Travel Management**: Create, edit, and track business travels
- ✅ **Receipt Upload**: Upload images/PDFs with automatic OCR processing
- ✅ **Database Storage**: SQLite database with travels and receipts
- ✅ **PDF Export**: Generate expense reports as PDF
- ✅ **Simple Frontend**: Web interface for travel creation and management
- ✅ **REST API**: Full OpenAPI/Swagger documentation
- ✅ **Professional Testing**: 28 tests with 71% coverage using pytest
- ✅ **Real Receipt Testing**: OCR validation with real and synthetic receipt data
- ✅ **Integration Testing**: Complete workflow testing from creation to export

## 📋 Current Status
- Backend: FastAPI with SQLAlchemy (async)
- Database: SQLite (14 travels, 0 receipts currently)
- Frontend: HTML/JS form at `/api/v1/ui`
- OCR: Tesseract integration with real receipt testing
- Testing: 28 tests passing, 71% coverage
- Server: Running on http://localhost:8000

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

## 2) Run Application
**All-in-one script:**
```bash
./run_local.sh           # Start server (default)
./run_local.sh start     # Start server
./run_local.sh stop      # Stop server
./run_local.sh restart   # Restart server
./run_local.sh test      # Run test suite
./run_local.sh status    # Show system status
```

**Check Status:**
```bash
./run_local.sh status
```

**Testing:**
```bash
./run_local.sh test           # Run all tests
pytest --cov=backend         # Run with coverage
pytest tests/test_ocr.py -v   # Run specific test category
```

**Access Points:**
- Frontend UI: http://localhost:8000/api/v1/ui
- API docs: http://localhost:8000/docs
- Database: SQLite (app.db)
- Uploads: ./uploads/

**Environment Variables:**
- DATABASE_URL: default sqlite+aiosqlite:///./app.db
- SECRET_KEY: devsecret
- UPLOAD_DIR: ./uploads

## 🧪 Testing Framework

The project includes a comprehensive test suite with 28 tests covering:

- **Model Tests**: Travel and receipt model validation
- **API Tests**: All REST endpoints with error handling
- **OCR Tests**: Real and synthetic receipt processing
- **Integration Tests**: Complete workflow validation

**Test Coverage**: 71% overall with targeted areas for improvement.

See [TEST_SUMMARY.md](TEST_SUMMARY.md) for detailed testing information.

## Notes
- First run will create SQLite DB and tables automatically (MVP).
- Postgres is supported: set DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/dbname
