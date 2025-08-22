from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from . import travels
from importlib.resources import files

router = APIRouter()
router.include_router(travels.router, prefix="/travels", tags=["travels"])


@router.get("/ui", response_class=HTMLResponse)
def ui():
    # Load embedded HTML file
    html_path = files(__package__).joinpath("travel_form.html")
    return html_path.read_text(encoding="utf-8")
