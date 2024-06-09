from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

app = FastAPI()

TEMPLATES_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


STATIC_FILES_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_FILES_DIR), name="static")


MACHINE_STATUS = "operational"


@app.get("/")
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html.jinja",
        context={"machine_status": MACHINE_STATUS},
    )


@app.post("/")
async def update_machine_status(
    machine_status: Annotated[str, Form()],
) -> RedirectResponse:
    globals()["MACHINE_STATUS"] = machine_status
    return RedirectResponse("/", status_code=303)
