import logging
from datetime import datetime
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse, JSONResponse
from starlette.templating import Jinja2Templates

from app.config import Config
from app.database import db
from app.models.request import Request as UserRequest, RequestStatus, RequestType

logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="app/templates")


async def mod_dashboard(request: Request) -> Response:
    """Moderator control panel dashboard"""
    if not Config.is_initialized():
        return RedirectResponse(url="/admincp/init", status_code=303)
    
    # Check if user is logged in
    if not request.session.get('user_id'):
        return RedirectResponse(url="/login", status_code=303)
    
    # Check if user is moderator or admin
    is_mod = request.session.get('is_moderator', False)
    is_admin = request.session.get('is_admin', False)
    
    if not (is_mod or is_admin):
        return templates.TemplateResponse(
            request,
            "error.html",
            {
                "title": "Access Denied",
                "error_message": "You do not have permission to access the moderator dashboard.",
                "app_name": Config.get('app.name', 'Switch Game Repository')
            },
            status_code=403
        )
    
    # Get pending requests count
    pending_requests = await db.get_all_requests(status='pending')
    
    return templates.TemplateResponse(
        request,
        "mod/dashboard.html",
        {
            "title": "Moderator Dashboard",
            "app_name": Config.get('app.name', 'Switch Game Repository'),
            "pending_count": len(pending_requests),
            "is_admin": is_admin
        }
    )


async def mod_requests(request: Request) -> Response:
    """View all requests"""
    if not Config.is_initialized():
        return RedirectResponse(url="/admincp/init", status_code=303)
    
    # Check if user is logged in
    if not request.session.get('user_id'):
        return RedirectResponse(url="/login", status_code=303)
    
    # Check if user is moderator or admin
    is_mod = request.session.get('is_moderator', False)
    is_admin = request.session.get('is_admin', False)
    
    if not (is_mod or is_admin):
        return templates.TemplateResponse(
            request,
            "error.html",
            {
                "title": "Access Denied",
                "error_message": "You do not have permission to access this page.",
                "app_name": Config.get('app.name', 'Switch Game Repository')
            },
            status_code=403
        )
    
    # Get filter from query params
    status_filter = request.query_params.get('status', 'pending')
    
    # Get requests based on filter
    if status_filter == 'all':
        requests = await db.get_all_requests()
    else:
        requests = await db.get_all_requests(status=status_filter)
    
    return templates.TemplateResponse(
        request,
        "mod/requests.html",
        {
            "title": "Manage Requests",
            "app_name": Config.get('app.name', 'Switch Game Repository'),
            "requests": requests,
            "status_filter": status_filter,
            "is_admin": is_admin
        }
    )


async def mod_approve_request(request: Request) -> Response:
    """Approve a request"""
    if not Config.is_initialized():
        return JSONResponse({"success": False, "error": "System not initialized"}, status_code=400)
    
    # Check if user is logged in and is moderator or admin
    user_id = request.session.get('user_id')
    username = request.session.get('username')
    is_mod = request.session.get('is_moderator', False)
    is_admin = request.session.get('is_admin', False)
    
    if not user_id or not (is_mod or is_admin):
        return JSONResponse({"success": False, "error": "Unauthorized"}, status_code=403)
    
    try:
        form_data = await request.form()
        request_id = form_data.get('request_id', '').strip()
        
        if not request_id:
            return JSONResponse({"success": False, "error": "Request ID is required"}, status_code=400)
        
        # Get the request
        user_request = await db.get_request_by_id(request_id)
        if not user_request:
            return JSONResponse({"success": False, "error": "Request not found"}, status_code=404)
        
        # Update request status
        success = await db.update_request_status(request_id, 'approved', username)
        if not success:
            return JSONResponse({"success": False, "error": "Failed to update request"}, status_code=500)
        
        # If request is for moderator access, grant it
        if user_request.get('request_type') == 'moderator_access':
            await db.update_user_moderator_status(user_request.get('user_id'), True)
            logger.info(f"Granted moderator status to user {user_request.get('username')}")
        
        return JSONResponse({
            "success": True, 
            "message": f"Request approved successfully"
        })
    
    except Exception as e:
        logger.error(f"Error approving request: {e}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


async def mod_reject_request(request: Request) -> Response:
    """Reject a request"""
    if not Config.is_initialized():
        return JSONResponse({"success": False, "error": "System not initialized"}, status_code=400)
    
    # Check if user is logged in and is moderator or admin
    user_id = request.session.get('user_id')
    username = request.session.get('username')
    is_mod = request.session.get('is_moderator', False)
    is_admin = request.session.get('is_admin', False)
    
    if not user_id or not (is_mod or is_admin):
        return JSONResponse({"success": False, "error": "Unauthorized"}, status_code=403)
    
    try:
        form_data = await request.form()
        request_id = form_data.get('request_id', '').strip()
        
        if not request_id:
            return JSONResponse({"success": False, "error": "Request ID is required"}, status_code=400)
        
        # Get the request
        user_request = await db.get_request_by_id(request_id)
        if not user_request:
            return JSONResponse({"success": False, "error": "Request not found"}, status_code=404)
        
        # Update request status
        success = await db.update_request_status(request_id, 'rejected', username)
        if not success:
            return JSONResponse({"success": False, "error": "Failed to update request"}, status_code=500)
        
        return JSONResponse({
            "success": True, 
            "message": f"Request rejected successfully"
        })
    
    except Exception as e:
        logger.error(f"Error rejecting request: {e}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


async def user_submit_request(request: Request) -> Response:
    """Submit a new request"""
    if not Config.is_initialized():
        return JSONResponse({"success": False, "error": "System not initialized"}, status_code=400)
    
    # Check if user is logged in
    user_id = request.session.get('user_id')
    username = request.session.get('username')
    
    if not user_id:
        return JSONResponse({"success": False, "error": "You must be logged in to submit a request"}, status_code=403)
    
    try:
        form_data = await request.form()
        request_type = form_data.get('request_type', '').strip()
        message = form_data.get('message', '').strip()
        
        if not request_type or not message:
            return JSONResponse({"success": False, "error": "All fields are required"}, status_code=400)
        
        # Validate request type
        valid_types = ['upload_access', 'moderator_access', 'other']
        if request_type not in valid_types:
            return JSONResponse({"success": False, "error": "Invalid request type"}, status_code=400)
        
        # Create the request
        user_request = UserRequest(
            user_id=user_id,
            username=username,
            request_type=RequestType(request_type),
            message=message,
            status=RequestStatus.PENDING
        )
        
        request_id = await db.create_request(user_request.to_dict())
        if not request_id:
            return JSONResponse({"success": False, "error": "Failed to create request"}, status_code=500)
        
        logger.info(f"User {username} submitted a {request_type} request")
        return JSONResponse({
            "success": True, 
            "message": "Request submitted successfully. A moderator will review it soon."
        })
    
    except Exception as e:
        logger.error(f"Error submitting request: {e}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


async def user_requests_page(request: Request) -> Response:
    """View user's own requests"""
    if not Config.is_initialized():
        return RedirectResponse(url="/admincp/init", status_code=303)
    
    # Check if user is logged in
    user_id = request.session.get('user_id')
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)
    
    # Get user's requests
    user_requests = await db.get_user_requests(user_id)
    
    return templates.TemplateResponse(
        request,
        "user/requests.html",
        {
            "title": "My Requests",
            "app_name": Config.get('app.name', 'Switch Game Repository'),
            "requests": user_requests
        }
    )
