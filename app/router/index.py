from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


@router.post("/user_input", response_class=HTMLResponse)
def user_input(request: Request, input: str=Form(...)):
    pass


@router.post("/reddit_input", response_class=HTMLResponse)
def reddit_input(request: Request, url: str=Form(...)):
    pass