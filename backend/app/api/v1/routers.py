from fastapi import APIRouter
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from . import endpoints as travels_endpoints
from importlib.resources import files
from pathlib import Path

router = APIRouter()
router.include_router(travels_endpoints.router, prefix="/travels", tags=["travels"])

# Get the frontend directory path - go up to project root then into frontend
project_root = Path(__file__).parent.parent.parent.parent.parent
frontend_dir = project_root / "frontend"

@router.get("/", response_class=HTMLResponse)
async def landing_page():
    """Serve the main landing page with authentication."""
    index_path = frontend_dir / "index.html"
    if index_path.exists():
        return HTMLResponse(content=index_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>TravelExpense - Landing page not found</h1>")

@router.get("/landingpage", response_class=HTMLResponse)
async def landingpage():
    """Serve the main landing page with authentication at /landingpage."""
    index_path = frontend_dir / "index.html"
    if index_path.exists():
        return HTMLResponse(content=index_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>TravelExpense - Landing page not found</h1>")

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Serve the dashboard page."""
    dashboard_path = frontend_dir / "dashboard.html"
    if dashboard_path.exists():
        return HTMLResponse(content=dashboard_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Dashboard not found</h1>")

@router.get("/travel-form", response_class=HTMLResponse)
async def travel_form():
    """Serve the travel form page."""
    form_path = frontend_dir / "travel-form.html"
    if form_path.exists():
        return HTMLResponse(content=form_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Travel form not found</h1>")

@router.get("/ui", response_class=HTMLResponse)
async def ui():
    """Legacy UI endpoint - serve the new travel form."""
    form_path = frontend_dir / "travel-form.html"
    if form_path.exists():
        return HTMLResponse(content=form_path.read_text(encoding="utf-8"))
    
    # Fallback to embedded HTML file
    html_path = files(__package__).joinpath("travel_form.html")
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))

@router.get("/debug", response_class=HTMLResponse)
async def debug_page():
    """Serve debug page for troubleshooting localStorage and role detection."""
    debug_path = frontend_dir / "debug.html"
    if debug_path.exists():
        return HTMLResponse(content=debug_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Debug page not found</h1>")
