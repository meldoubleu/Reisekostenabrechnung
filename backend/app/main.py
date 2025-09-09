from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from .api.v1.routers import router as api_router
from .db.session import init_db
from .core.exceptions import (
    custom_http_exception_handler,
    custom_validation_exception_handler,
    custom_general_exception_handler,
    custom_starlette_exception_handler
)
from .core.logging import logger
from pathlib import Path

app = FastAPI(title="TravelExpense - Reisekostenabrechnung", version="0.1.0")

# Add exception handlers
app.add_exception_handler(HTTPException, custom_http_exception_handler)
app.add_exception_handler(RequestValidationError, custom_validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, custom_starlette_exception_handler)
app.add_exception_handler(Exception, custom_general_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting TravelExpense API server...")
    await init_db()
    logger.info("Database initialized successfully")

# Mount the frontend static files
frontend_dir = Path(__file__).parent.parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

app.include_router(api_router, prefix="/api/v1")

@app.get("/favicon.ico")
async def favicon():
    """Return a simple favicon to prevent 404 errors."""
    # Return a minimal ICO file content (1x1 transparent pixel)
    ico_content = (
        b'\x00\x00\x01\x00\x01\x00\x01\x01\x00\x00\x01\x00\x08\x00h\x05\x00\x00'
        b'\x16\x00\x00\x00(\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x01\x00'
        b'\x08\x00\x00\x00\x00\x00@\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        b'\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x01\x01\x00' + b'\x00' * 1282
    )
    return Response(content=ico_content, media_type="image/x-icon")

@app.get("/robots.txt")
async def robots():
    """Return a robots.txt file."""
    robots_content = """User-agent: *
Allow: /
"""
    return Response(content=robots_content, media_type="text/plain")

@app.get("/")
async def root():
    """Serve the landing page directly at root."""
    frontend_dir = Path(__file__).parent.parent.parent / "frontend"
    index_path = frontend_dir / "index.html"
    if index_path.exists():
        return HTMLResponse(content=index_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>TravelExpense - Landing page not found</h1>")

@app.get("/landingpage")
async def landingpage():
    """Serve the landing page at /landingpage."""
    frontend_dir = Path(__file__).parent.parent.parent / "frontend"
    index_path = frontend_dir / "index.html"
    if index_path.exists():
        return HTMLResponse(content=index_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>TravelExpense - Landing page not found</h1>")

@app.get("/api/v1/ui")
async def ui_redirect():
    """Redirect to the main dashboard."""
    return RedirectResponse(url="/dashboard")

@app.get("/dashboard")
async def dashboard():
    """Serve the dashboard page."""
    frontend_dir = Path(__file__).parent.parent.parent / "frontend"
    dashboard_path = frontend_dir / "dashboard.html"
    if dashboard_path.exists():
        return HTMLResponse(content=dashboard_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Dashboard not found</h1>")

@app.get("/admin")
async def admin():
    """Serve the admin page."""
    frontend_dir = Path(__file__).parent.parent.parent / "frontend"
    admin_path = frontend_dir / "admin.html"
    if admin_path.exists():
        return HTMLResponse(content=admin_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Admin page not found</h1>")

@app.get("/travel-form")
async def travel_form():
    """Serve the travel form page."""
    frontend_dir = Path(__file__).parent.parent.parent / "frontend"
    form_path = frontend_dir / "travel-form.html"
    if form_path.exists():
        return HTMLResponse(content=form_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Travel form not found</h1>")

@app.get("/admin.html")
async def admin_html():
    """Serve the admin page at admin.html."""
    frontend_dir = Path(__file__).parent.parent.parent / "frontend"
    admin_path = frontend_dir / "admin.html"
    if admin_path.exists():
        return HTMLResponse(content=admin_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Admin page not found</h1>")

@app.get("/dashboard.html")
async def dashboard_html():
    """Serve the dashboard page at dashboard.html."""
    frontend_dir = Path(__file__).parent.parent.parent / "frontend"
    dashboard_path = frontend_dir / "dashboard.html"
    if dashboard_path.exists():
        return HTMLResponse(content=dashboard_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Dashboard not found</h1>")

@app.get("/travel-form.html")
async def travel_form_html():
    """Serve the travel form page at travel-form.html."""
    frontend_dir = Path(__file__).parent.parent.parent / "frontend"
    form_path = frontend_dir / "travel-form.html"
    if form_path.exists():
        return HTMLResponse(content=form_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Travel form not found</h1>")

@app.get("/travel-form-new.html")
async def travel_form_new_html():
    """Serve the new two-stage travel form page."""
    frontend_dir = Path(__file__).parent.parent.parent / "frontend"
    form_path = frontend_dir / "travel-form-start.html"
    if form_path.exists():
        return HTMLResponse(content=form_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>New travel form not found</h1>")

@app.get("/travel-form-start.html")
async def travel_form_start_html():
    """Serve the travel form start page."""
    frontend_dir = Path(__file__).parent.parent.parent / "frontend"
    form_path = frontend_dir / "travel-form-start.html"
    if form_path.exists():
        return HTMLResponse(content=form_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Travel form start not found</h1>")

@app.get("/index.html")
async def index_html():
    """Serve the index page at index.html."""
    frontend_dir = Path(__file__).parent.parent.parent / "frontend"
    index_path = frontend_dir / "index.html"
    if index_path.exists():
        return HTMLResponse(content=index_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>TravelExpense - Landing page not found</h1>")
