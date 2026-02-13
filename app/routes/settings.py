import logging
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse, JSONResponse
from starlette.templating import Jinja2Templates

from app.config import Config
from app.database import db
from app.models.user import User

logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="app/templates")


async def settings_page(request: Request) -> Response:
    """Show user settings page"""
    # Check if user is logged in
    if not request.session.get('user_id'):
        return RedirectResponse(url="/login", status_code=303)
    
    return templates.TemplateResponse(
        request,
        "settings/settings.html",
        {
            "title": "Settings",
            "app_name": Config.get('app.name', 'Switch Game Repository')
        }
    )


async def change_password(request: Request) -> Response:
    """Handle password change"""
    # Check if user is logged in
    if not request.session.get('user_id'):
        return JSONResponse(
            {"success": False, "error": "Not authenticated"},
            status_code=401
        )
    
    try:
        form_data = await request.form()
        current_password = form_data.get('current_password', '')
        new_password = form_data.get('new_password', '')
        confirm_password = form_data.get('confirm_password', '')
        
        # Validate input
        if not current_password or not new_password or not confirm_password:
            return JSONResponse(
                {"success": False, "error": "All fields are required"},
                status_code=400
            )
        
        if len(new_password) < 6:
            return JSONResponse(
                {"success": False, "error": "New password must be at least 6 characters"},
                status_code=400
            )
        
        if new_password != confirm_password:
            return JSONResponse(
                {"success": False, "error": "New passwords do not match"},
                status_code=400
            )
        
        # Get user from database
        user_id = request.session.get('user_id')
        user_data = await db.get_user_by_id(user_id)
        
        if not user_data:
            return JSONResponse(
                {"success": False, "error": "User not found"},
                status_code=404
            )
        
        # Verify current password
        user = User.from_dict(user_data)
        if not User.verify_password(current_password, user.password_hash):
            return JSONResponse(
                {"success": False, "error": "Current password is incorrect"},
                status_code=401
            )
        
        # Update password
        new_password_hash = User.hash_password(new_password)
        success = await db.update_user_password(user_id, new_password_hash)
        
        if not success:
            return JSONResponse(
                {"success": False, "error": "Failed to update password"},
                status_code=500
            )
        
        # Log the password change to audit log
        username = request.session.get('username', user.username)
        ip_address = request.client.host if request.client else 'unknown'
        
        await db.add_audit_log({
            'action': 'password_changed',
            'actor_id': user_id,
            'actor_username': username,
            'target_id': user_id,
            'target_username': username,
            'details': {
                'changed_by': 'self',
                'reason': 'User changed own password'
            },
            'ip_address': ip_address
        })
        
        logger.info(f"Password changed for user: {user.username}")
        return JSONResponse({"success": True, "message": "Password changed successfully"})
        
    except Exception as e:
        logger.error(f"Password change error: {e}")
        return JSONResponse(
            {"success": False, "error": "An error occurred while changing password"},
            status_code=500
        )


async def download_history_page(request: Request) -> Response:
    """Show user's download history"""
    # Check if user is logged in
    if not request.session.get('user_id'):
        return RedirectResponse(url="/login", status_code=303)
    
    try:
        user_id = request.session.get('user_id')
        history = await db.get_user_download_history(user_id)
        
        return templates.TemplateResponse(
            request,
            "settings/download_history.html",
            {
                "title": "Download History",
                "app_name": Config.get('app.name', 'Switch Game Repository'),
                "history": history
            }
        )
    except Exception as e:
        logger.error(f"Error loading download history: {e}")
        return templates.TemplateResponse(
            request,
            "error.html",
            {
                "title": "Error",
                "app_name": Config.get('app.name', 'Switch Game Repository'),
                "error": "Failed to load download history"
            },
            status_code=500
        )
