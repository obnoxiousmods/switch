from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates

# We'll import templates from main.py after we update it
templates = Jinja2Templates(directory="app/templates")

def index(request: Request) -> Response:
    """Homepage with search dashboard"""
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "title": "Switch Game Repository"
        }
    )
