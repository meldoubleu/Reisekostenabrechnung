from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from backend.app.api.v1.routers import router as api_router
from backend.app.db.session import init_db

app = FastAPI(title="Reisekostenabrechnung API", version="0.1.0")

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

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return RedirectResponse(url="/api/v1/ui")
