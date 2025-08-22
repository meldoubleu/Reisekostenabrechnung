from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from backend.app.api.v1.routers import router as api_router
from backend.app.db.session import init_db
from pathlib import Path

app = FastAPI(title="TravelExpense - Reisekostenabrechnung", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await init_db()

# Mount the frontend static files
frontend_dir = Path(__file__).parent.parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

app.include_router(api_router, prefix="/api/v1")

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
