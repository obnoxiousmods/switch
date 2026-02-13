import logging
from starlette.requests import Request
from starlette.responses import Response, JSONResponse, RedirectResponse
from starlette.templating import Jinja2Templates

from app.database import db
from app.models.api_key import ApiKey

logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="app/templates")


async def api_keys_page(request: Request) -> Response:
    """API keys management page for users"""
    # Check if user is logged in
    if not request.session.get('username'):
        return RedirectResponse(url="/login", status_code=303)
    
    user_id = request.session.get('user_id')
    
    # Get user's API keys
    api_keys = await db.get_user_api_keys(user_id)
    
    return templates.TemplateResponse(
        request,
        "settings/api_keys.html",
        {
            "title": "API Keys",
            "api_keys": api_keys
        }
    )


async def generate_api_key(request: Request) -> Response:
    """Generate a new API key"""
    # Check if user is logged in
    if not request.session.get('username'):
        return JSONResponse({"error": "Not authenticated"}, status_code=401)
    
    try:
        form = await request.form()
        key_name = form.get('key_name', '').strip()
        
        if not key_name:
            return JSONResponse({"error": "Key name is required"}, status_code=400)
        
        user_id = request.session.get('user_id')
        
        # Generate new API key
        api_key_plain = ApiKey.generate_key()
        api_key_hash = ApiKey.hash_key(api_key_plain)
        
        # Store in database
        api_key_data = {
            'user_id': user_id,
            'key_name': key_name,
            'key_hash': api_key_hash,
            'is_active': True
        }
        
        key_id = await db.create_api_key(api_key_data)
        
        if key_id:
            return JSONResponse({
                "success": True,
                "api_key": api_key_plain,  # Only time we return the plain key
                "key_id": key_id,
                "message": "API key generated successfully. Make sure to copy it now - you won't be able to see it again!"
            })
        else:
            return JSONResponse({"error": "Failed to create API key"}, status_code=500)
    
    except Exception as e:
        logger.error(f"Error generating API key: {e}")
        return JSONResponse({"error": "An error occurred"}, status_code=500)


async def revoke_api_key(request: Request) -> Response:
    """Revoke an API key"""
    # Check if user is logged in
    if not request.session.get('username'):
        return JSONResponse({"error": "Not authenticated"}, status_code=401)
    
    try:
        form = await request.form()
        key_id = form.get('key_id', '').strip()
        
        if not key_id:
            return JSONResponse({"error": "Key ID is required"}, status_code=400)
        
        user_id = request.session.get('user_id')
        
        # Verify the key belongs to the user
        user_keys = await db.get_user_api_keys(user_id)
        key_belongs_to_user = any(k.get('_key') == key_id for k in user_keys)
        
        if not key_belongs_to_user:
            return JSONResponse({"error": "API key not found"}, status_code=404)
        
        # Revoke the key
        success = await db.revoke_api_key(key_id)
        
        if success:
            return JSONResponse({
                "success": True,
                "message": "API key revoked successfully"
            })
        else:
            return JSONResponse({"error": "Failed to revoke API key"}, status_code=500)
    
    except Exception as e:
        logger.error(f"Error revoking API key: {e}")
        return JSONResponse({"error": "An error occurred"}, status_code=500)


async def api_usage_page(request: Request) -> Response:
    """API usage statistics page for users"""
    # Check if user is logged in
    if not request.session.get('username'):
        return RedirectResponse(url="/login", status_code=303)
    
    user_id = request.session.get('user_id')
    
    # Get usage statistics
    usage_stats = await db.get_api_usage_stats_by_user(user_id)
    recent_usage = await db.get_api_usage_by_user(user_id, limit=50)
    
    return templates.TemplateResponse(
        request,
        "settings/api_usage.html",
        {
            "title": "API Usage",
            "usage_stats": usage_stats,
            "recent_usage": recent_usage
        }
    )
