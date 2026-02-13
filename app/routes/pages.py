from starlette.requests import Request
from starlette.responses import Response, RedirectResponse
from starlette.templating import Jinja2Templates

from app.config import Config
from app.database import db

# We'll import templates from main.py after we update it
templates = Jinja2Templates(directory="app/templates")

async def index(request: Request) -> Response:
    """Homepage with search dashboard"""
    # Check if system is initialized
    if not Config.is_initialized():
        return RedirectResponse(url="/admincp/init", status_code=303)
    
    # Check if user is moderator or admin to show pending requests
    is_moderator = request.session.get('is_moderator', False) or request.session.get('is_admin', False)
    pending_count = 0
    
    if is_moderator:
        # Get pending requests count for mods (efficient count query)
        pending_count = await db.count_requests(status='pending')
    
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "title": "Home",
            "app_name": Config.get('app.name', 'Switch Game Repository'),
            "is_moderator": is_moderator,
            "pending_count": pending_count
        }
    )
