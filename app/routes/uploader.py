import logging
import os
from datetime import datetime
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse, JSONResponse
from starlette.templating import Jinja2Templates
from starlette.datastructures import UploadFile

from app.config import Config
from app.database import db
from app.models.request import Request as UserRequest, RequestStatus, RequestType
from app.models.entry import Entry, EntryType, FileType
from app.utils.ip_utils import get_ip_info, format_ip_for_log

logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="app/templates")


async def uploader_dashboard(request: Request) -> Response:
    """Uploader control panel dashboard"""
    if not Config.is_initialized():
        return RedirectResponse(url="/admincp/init", status_code=303)
    
    # Check if user is logged in
    if not request.session.get('user_id'):
        return RedirectResponse(url="/login", status_code=303)
    
    # Check if user is uploader, moderator, or admin
    is_uploader = request.session.get('is_uploader', False)
    is_mod = request.session.get('is_moderator', False)
    is_admin = request.session.get('is_admin', False)
    
    if not (is_uploader or is_mod or is_admin):
        return templates.TemplateResponse(
            request,
            "error.html",
            {
                "title": "Access Denied",
                "error_message": "You do not have permission to access the uploader dashboard.",
                "app_name": Config.get('app.name', 'Switch Game Repository')
            },
            status_code=403
        )
    
    # Get pending game requests count
    game_requests = await db.get_all_requests(status='pending')
    game_requests = [r for r in game_requests if r.get('request_type') == 'game_request']
    
    # Get user's upload statistics
    user_id = request.session.get('user_id')
    upload_stats = await db.get_upload_statistics(user_id)
    
    return templates.TemplateResponse(
        request,
        "uploader/dashboard.html",
        {
            "title": "Uploader Dashboard",
            "app_name": Config.get('app.name', 'Switch Game Repository'),
            "pending_game_requests": len(game_requests),
            "upload_stats": upload_stats,
            "is_admin": is_admin,
            "is_moderator": is_mod
        }
    )


async def uploader_game_requests(request: Request) -> Response:
    """View game requests"""
    if not Config.is_initialized():
        return RedirectResponse(url="/admincp/init", status_code=303)
    
    # Check if user is logged in
    if not request.session.get('user_id'):
        return RedirectResponse(url="/login", status_code=303)
    
    # Check if user is uploader, moderator, or admin
    is_uploader = request.session.get('is_uploader', False)
    is_mod = request.session.get('is_moderator', False)
    is_admin = request.session.get('is_admin', False)
    
    if not (is_uploader or is_mod or is_admin):
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
    
    # Get game requests based on filter
    if status_filter == 'all':
        requests = await db.get_all_requests()
    else:
        requests = await db.get_all_requests(status=status_filter)
    
    # Filter only game requests
    game_requests = [r for r in requests if r.get('request_type') == 'game_request']
    
    return templates.TemplateResponse(
        request,
        "uploader/game_requests.html",
        {
            "title": "Game Requests",
            "app_name": Config.get('app.name', 'Switch Game Repository'),
            "requests": game_requests,
            "status_filter": status_filter,
            "is_admin": is_admin,
            "is_moderator": is_mod
        }
    )


async def uploader_approve_request(request: Request) -> Response:
    """Approve a game request"""
    if not Config.is_initialized():
        return JSONResponse({"success": False, "error": "System not initialized"}, status_code=400)
    
    # Check if user is logged in and is uploader, moderator or admin
    user_id = request.session.get('user_id')
    username = request.session.get('username')
    is_uploader = request.session.get('is_uploader', False)
    is_mod = request.session.get('is_moderator', False)
    is_admin = request.session.get('is_admin', False)
    
    if not user_id or not (is_uploader or is_mod or is_admin):
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
        
        # Check if it's a game request
        if user_request.get('request_type') != 'game_request':
            return JSONResponse({"success": False, "error": "This is not a game request"}, status_code=400)
        
        # Update request status
        success = await db.update_request_status(request_id, 'approved', username)
        if not success:
            return JSONResponse({"success": False, "error": "Failed to update request"}, status_code=500)
        
        return JSONResponse({
            "success": True, 
            "message": f"Game request approved successfully"
        })
    
    except Exception as e:
        logger.error(f"Error approving game request: {e}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


async def uploader_reject_request(request: Request) -> Response:
    """Reject a game request"""
    if not Config.is_initialized():
        return JSONResponse({"success": False, "error": "System not initialized"}, status_code=400)
    
    # Check if user is logged in and is uploader, moderator or admin
    user_id = request.session.get('user_id')
    username = request.session.get('username')
    is_uploader = request.session.get('is_uploader', False)
    is_mod = request.session.get('is_moderator', False)
    is_admin = request.session.get('is_admin', False)
    
    if not user_id or not (is_uploader or is_mod or is_admin):
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
        
        # Check if it's a game request
        if user_request.get('request_type') != 'game_request':
            return JSONResponse({"success": False, "error": "This is not a game request"}, status_code=400)
        
        # Update request status
        success = await db.update_request_status(request_id, 'rejected', username)
        if not success:
            return JSONResponse({"success": False, "error": "Failed to update request"}, status_code=500)
        
        return JSONResponse({
            "success": True, 
            "message": f"Game request rejected successfully"
        })
    
    except Exception as e:
        logger.error(f"Error rejecting game request: {e}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


async def uploader_upload_page(request: Request) -> Response:
    """Upload game page"""
    if not Config.is_initialized():
        return RedirectResponse(url="/admincp/init", status_code=303)
    
    # Check if user is logged in
    if not request.session.get('user_id'):
        return RedirectResponse(url="/login", status_code=303)
    
    # Check if user is uploader, moderator, or admin
    is_uploader = request.session.get('is_uploader', False)
    is_mod = request.session.get('is_moderator', False)
    is_admin = request.session.get('is_admin', False)
    
    if not (is_uploader or is_mod or is_admin):
        return templates.TemplateResponse(
            request,
            "error.html",
            {
                "title": "Access Denied",
                "error_message": "You do not have permission to upload games.",
                "app_name": Config.get('app.name', 'Switch Game Repository')
            },
            status_code=403
        )
    
    return templates.TemplateResponse(
        request,
        "uploader/upload.html",
        {
            "title": "Upload Game",
            "app_name": Config.get('app.name', 'Switch Game Repository'),
            "is_admin": is_admin,
            "is_moderator": is_mod
        }
    )


async def uploader_upload_submit(request: Request) -> Response:
    """Handle game upload submission"""
    if not Config.is_initialized():
        return JSONResponse({"success": False, "error": "System not initialized"}, status_code=400)
    
    # Check if user is logged in and is uploader, moderator or admin
    user_id = request.session.get('user_id')
    username = request.session.get('username')
    is_uploader = request.session.get('is_uploader', False)
    is_mod = request.session.get('is_moderator', False)
    is_admin = request.session.get('is_admin', False)
    
    if not user_id or not (is_uploader or is_mod or is_admin):
        return JSONResponse({"success": False, "error": "Unauthorized"}, status_code=403)
    
    try:
        form_data = await request.form()
        
        # Get form fields
        entry_type = form_data.get('type', '').strip()
        
        # Validate required fields
        if not entry_type or entry_type != 'filepath':
            return JSONResponse({"success": False, "error": "Only file upload is supported"}, status_code=400)
        
        # File upload
        file = form_data.get('file')
        if not file or not isinstance(file, UploadFile):
            return JSONResponse({"success": False, "error": "File is required"}, status_code=400)
        
        # Get filename
        filename = file.filename
        if not filename:
            return JSONResponse({"success": False, "error": "Invalid filename"}, status_code=400)
        
        # Auto-detect file type from extension
        file_ext = filename.lower().split('.')[-1]
        if file_ext not in ['nsp', 'nsz', 'xci']:
            return JSONResponse({"success": False, "error": "Invalid file type. Supported: NSP, NSZ, XCI"}, status_code=400)
        
        file_type = file_ext
        
        # Extract game name from filename (remove extension)
        name = '.'.join(filename.split('.')[:-1])
        
        # Create uploads directory if it doesn't exist
        upload_dir = Config.get('upload.directory', '/app/uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, filename)
        
        # Read and save file
        content = await file.read()
        size = len(content)
        
        with open(file_path, 'wb') as f:
            f.write(content)
        
        source = file_path
        logger.info(f"File saved to {file_path}, size: {size} bytes")
        
        # Create entry
        entry = Entry(
            name=name,
            source=source,
            type=EntryType(entry_type),
            file_type=FileType(file_type),
            size=size,
            created_by=username,
            metadata={}
        )
        
        # Add to database
        entry_id = await db.add_entry(entry.to_dict())
        if not entry_id:
            return JSONResponse({"success": False, "error": "Failed to create entry"}, status_code=500)
        
        # Record upload statistics
        await db.record_upload(user_id, username, entry_id, size)
        
        # Log activity with IP information
        ip_info = get_ip_info(request)
        activity_data = {
            'event_type': 'upload',
            'user_id': user_id,
            'username': username,
            'entry_id': entry_id,
            'entry_name': name,
            'size_bytes': size,
            'ip_address': ip_info['ip_address'],
            'client_ip': ip_info['client_ip']
        }
        if 'forwarded_ip' in ip_info:
            activity_data['forwarded_ip'] = ip_info['forwarded_ip']
        
        await db.add_activity_log(activity_data)
        
        logger.info(f"User {username} uploaded game '{name}' ({size} bytes) from {format_ip_for_log(request)}")
        return JSONResponse({
            "success": True, 
            "message": f"Game '{name}' uploaded successfully!",
            "entry_id": entry_id
        })
    
    except Exception as e:
        logger.error(f"Error uploading game: {e}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)
