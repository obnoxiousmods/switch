import logging
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse, JSONResponse
from starlette.templating import Jinja2Templates

from app.config import Config
from app.database import db
from app.models.user import User

logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="app/templates")


async def login_page(request: Request) -> Response:
    """Show login form"""
    # If already logged in, redirect to homepage
    if request.session.get('user_id'):
        return RedirectResponse(url="/", status_code=303)
    
    return templates.TemplateResponse(
        request,
        "auth/login.html",
        {
            "title": "Login",
            "app_name": Config.get('app.name', 'Switch Game Repository')
        }
    )


async def login_submit(request: Request) -> Response:
    """Handle login form submission"""
    try:
        form_data = await request.form()
        username = form_data.get('username', '').strip()
        password = form_data.get('password', '')
        
        if not username or not password:
            return JSONResponse(
                {"success": False, "error": "Username and password are required"},
                status_code=400
            )
        
        # Get user from database
        user_data = await db.get_user_by_username(username)
        if not user_data:
            return JSONResponse(
                {"success": False, "error": "Invalid username or password"},
                status_code=401
            )
        
        # Verify password
        user = User.from_dict(user_data)
        if not User.verify_password(password, user.password_hash):
            return JSONResponse(
                {"success": False, "error": "Invalid username or password"},
                status_code=401
            )
        
        # Set session
        request.session['user_id'] = user._key
        request.session['username'] = user.username
        request.session['is_admin'] = user.is_admin
        request.session['is_moderator'] = user.is_moderator
        request.session['is_uploader'] = user.is_uploader
        
        # Log the login activity
        ip_address = request.client.host if request.client else 'unknown'
        await db.add_activity_log({
            'event_type': 'login',
            'user_id': user._key,
            'username': user.username,
            'details': {
                'success': True
            },
            'ip_address': ip_address
        })
        
        logger.info(f"User logged in: {username}")
        return JSONResponse({"success": True, "redirect": "/"})
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return JSONResponse(
            {"success": False, "error": "An error occurred during login"},
            status_code=500
        )


async def register_page(request: Request) -> Response:
    """Show registration form"""
    # If already logged in, redirect to homepage
    if request.session.get('user_id'):
        return RedirectResponse(url="/", status_code=303)
    
    return templates.TemplateResponse(
        request,
        "auth/register.html",
        {
            "title": "Register",
            "app_name": Config.get('app.name', 'Switch Game Repository')
        }
    )


async def register_submit(request: Request) -> Response:
    """Handle registration form submission"""
    try:
        form_data = await request.form()
        username = form_data.get('username', '').strip()
        password = form_data.get('password', '')
        confirm_password = form_data.get('confirm_password', '')
        
        # Validate input
        if not username or not password or not confirm_password:
            return JSONResponse(
                {"success": False, "error": "All fields are required"},
                status_code=400
            )
        
        if len(username) < 3:
            return JSONResponse(
                {"success": False, "error": "Username must be at least 3 characters"},
                status_code=400
            )
        
        if len(password) < 6:
            return JSONResponse(
                {"success": False, "error": "Password must be at least 6 characters"},
                status_code=400
            )
        
        if password != confirm_password:
            return JSONResponse(
                {"success": False, "error": "Passwords do not match"},
                status_code=400
            )
        
        # Check if username already exists
        if await db.user_exists(username):
            return JSONResponse(
                {"success": False, "error": "Username already exists"},
                status_code=400
            )
        
        # Create user
        user = User(
            username=username,
            password_hash=User.hash_password(password),
            is_admin=False
        )
        user_id = await db.create_user(user.to_dict())
        
        if not user_id:
            return JSONResponse(
                {"success": False, "error": "Failed to create user"},
                status_code=500
            )
        
        # Auto-login after registration
        request.session['user_id'] = user_id
        request.session['username'] = username
        request.session['is_admin'] = False
        request.session['is_moderator'] = False
        request.session['is_uploader'] = False
        
        # Log the registration activity
        ip_address = request.client.host if request.client else 'unknown'
        await db.add_activity_log({
            'event_type': 'registration',
            'user_id': user_id,
            'username': username,
            'details': {
                'success': True
            },
            'ip_address': ip_address
        })
        
        logger.info(f"New user registered: {username}")
        return JSONResponse({"success": True, "redirect": "/"})
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return JSONResponse(
            {"success": False, "error": "An error occurred during registration"},
            status_code=500
        )


async def logout(request: Request) -> Response:
    """Handle logout"""
    username = request.session.get('username', 'Unknown')
    request.session.clear()
    logger.info(f"User logged out: {username}")
    return RedirectResponse(url="/login", status_code=303)
