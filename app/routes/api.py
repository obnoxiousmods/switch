from starlette.responses import JSONResponse, FileResponse, RedirectResponse
from starlette.requests import Request
import os

from app.database import db
from app.utils.ip_utils import get_ip_info, format_ip_for_log

async def list_entries(request: Request):
    """API endpoint to list all entries"""
    # Require authentication - either session or API key
    has_session = request.session.get('user_id') is not None
    has_api_auth = getattr(request.state, 'authenticated', False)
    
    if not has_session and not has_api_auth:
        return JSONResponse({
            "error": "Authentication required. Please log in or use an API key."
        }, status_code=401)
    
    try:
        entries = await db.get_all_entries()
        return JSONResponse({
            "entries": entries
        })
    except Exception as e:
        return JSONResponse({
            "error": str(e)
        }, status_code=500)

async def download_entry(request: Request):
    """API endpoint to download an entry"""
    # Require authentication - either session or API key
    has_session = request.session.get('user_id') is not None
    has_api_auth = getattr(request.state, 'authenticated', False)
    
    if not has_session and not has_api_auth:
        return JSONResponse({
            "error": "Authentication required. Please log in or use an API key."
        }, status_code=401)
    
    try:
        entry_id = request.path_params.get('entry_id')
        
        # Get the entry from the database
        entry = await db.get_entry_by_id(entry_id)
        
        if not entry:
            return JSONResponse({
                "error": "Entry not found"
            }, status_code=404)
        
        # Track download if user is logged in (session-based)
        user_id = request.session.get('user_id')
        username = request.session.get('username')
        ip_info = get_ip_info(request)
        
        # For API key authentication, use the authenticated user_id
        if not user_id and has_api_auth:
            user_id = request.state.user_id
            # Get username from database for API key users
            user_doc = await db.get_user_by_id(user_id)
            if user_doc:
                username = user_doc.get('username', 'api_user')
        
        if user_id:
            await db.add_download_history(
                user_id=user_id,
                entry_id=entry_id,
                entry_name=entry.get('name', 'Unknown')
            )
            
            # Log the download activity with IP information
            activity_data = {
                'event_type': 'download',
                'user_id': user_id,
                'username': username,
                'details': {
                    'entry_id': entry_id,
                    'entry_name': entry.get('name', 'Unknown'),
                    'file_type': entry.get('file_type', 'unknown'),
                    'source_type': entry.get('type', 'unknown')
                },
                'ip_address': ip_info['ip_address'],
                'client_ip': ip_info['client_ip']
            }
            if 'forwarded_ip' in ip_info:
                activity_data['forwarded_ip'] = ip_info['forwarded_ip']
            
            await db.add_activity_log(activity_data)
        
        # If it's a URL, redirect to it
        if entry.get('type') == 'url':
            return RedirectResponse(url=entry.get('source'))
        
        # If it's a filepath, serve the file
        filepath = entry.get('source')
        
        if not os.path.exists(filepath):
            return JSONResponse({
                "error": "File not found on server"
            }, status_code=404)
        
        # Get the filename from the path
        filename = os.path.basename(filepath)
        
        # Return the file as a download
        return FileResponse(
            filepath,
            filename=filename,
            media_type='application/octet-stream'
        )
        
    except Exception as e:
        return JSONResponse({
            "error": str(e)
        }, status_code=500)
