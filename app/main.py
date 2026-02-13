from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from app.routes import routes

# Templates – autoescape + modern defaults
templates = Jinja2Templates(
    directory="app/templates",
    # You can pass autoescape=True, extensions=["jinja2.ext.i18n"], etc.
)

# Optional: context processor (available in all templates)
@templates.context_processor
def add_global_vars(request):
    return {
        "app_name": "My Starlette App",
        "flash": request.session.pop("flash", None),   # one-time flash message
        "user": request.session.get("user"),           # example
    }

middleware = [
    Middleware(
        SessionMiddleware,
        secret_key="change-this-to-a-very-long-random-secret-2026!",
        max_age=3600 * 24 * 14,     # 2 weeks
        same_site="lax",
        https_only=False,           # ← set True in prod + HTTPS
    ),
    # Add more: CORSMiddleware, GZipMiddleware, etc.
]

app = Starlette(
    debug=True,
    routes=routes,
    middleware=middleware,
    template_engine=templates,   # optional but nice
    
)


# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# Optional startup / shutdown
@app.on_event("startup")
async def startup():
    print("→ App starting...")


@app.on_event("shutdown")
async def shutdown():
    print("→ App shutting down...")