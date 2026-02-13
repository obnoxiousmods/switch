from starlette.requests import Request
from starlette.responses import Response, RedirectResponse
from starlette.templating import Jinja2Templates

from app.config import Config

# We'll import templates from main.py after we update it
templates = Jinja2Templates(directory="app/templates")

def index(request: Request) -> Response:
    """Homepage with search dashboard"""
    # Check if system is initialized
    if not Config.is_initialized():
        return RedirectResponse(url="/admincp/init", status_code=303)
    
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "title": "Home",
            "app_name": Config.get('app.name', 'Switch Game Repository')
        }
    )
