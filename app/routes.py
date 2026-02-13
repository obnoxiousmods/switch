from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.routing import Route
from starlette.templating import Jinja2Templates

from app.main import templates  # shared instance

async def index(request: Request):
    # Example: set a flash message
    if "flash" not in request.session:
        request.session["flash"] = "Welcome back! 🎉"

    return templates.TemplateResponse(
        request,
        "index.html",
        {"title": "Home", "visits": request.session.get("visits", 0)}
    )


async def dashboard(request: Request):
    if not request.session.get("user"):
        request.session["flash"] = "Please log in first."
        return RedirectResponse(url="/", status_code=303)

    # Simulate page view counter
    request.session["visits"] = request.session.get("visits", 0) + 1

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {"title": "Dashboard", "username": request.session.get("user", "Guest")}
    )


async def login(request: Request):
    if request.method == "POST":
        form = await request.form()
        username = form.get("username")
        if username:
            request.session["user"] = username.strip()
            request.session["flash"] = f"Logged in as {username}!"
            return RedirectResponse(url="/dashboard", status_code=303)

    return templates.TemplateResponse(request, "index.html", {"title": "Login"})


async def logout(request: Request):
    request.session.pop("user", None)
    request.session["flash"] = "You have been logged out."
    return RedirectResponse(url="/", status_code=303)


# Class-based handler example (cleaner for complex logic)
class Profile:
    async def __call__(self, request: Request):
        user = request.session.get("user")
        if not user:
            return RedirectResponse(url="/login", status_code=302)

        return templates.TemplateResponse(
            request,
            "dashboard.html",
            {
                "title": "Your Profile",
                "username": user,
                "is_profile": True,
            }
        )


routes = [
    Route("/", index),
    Route("/dashboard", dashboard),
    Route("/profile", Profile(), methods=["GET"]),
    Route("/login", login, methods=["GET", "POST"]),
    Route("/logout", logout),
]