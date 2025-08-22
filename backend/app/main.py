from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
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
    """Redirect to the new landing page."""
    return RedirectResponse(url="/api/v1/")
