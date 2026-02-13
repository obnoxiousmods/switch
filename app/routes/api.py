from starlette.responses import JSONResponse, FileResponse, RedirectResponse
from starlette.requests import Request
import os
import logging

from app.database import db
from app.utils.ip_utils import get_ip_info, format_ip_for_log
from app.config import Config

logger = logging.getLogger(__name__)

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
        # Get query parameters
        search_query = request.query_params.get('search')
        sort_by = request.query_params.get('sort_by')
        
        # Check if sorting by downloads
        sort_by_downloads = sort_by == 'downloads'
        
        # Get entries with download counts
        entries = await db.get_all_entries_with_download_counts(
            search_query=search_query,
            sort_by_downloads=sort_by_downloads
        )
        
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
                entry_name=entry.get('name', 'Unknown'),
                size_bytes=entry.get('size', 0)
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
        
        # If it's a filepath, serve the file with security validation
        filepath = entry.get('source')
        
        # Validate the filepath is within allowed directories
        try:
            filepath_resolved = os.path.abspath(filepath)
            
            # Get list of allowed directories from config or use defaults
            # These should be directories where game files are stored
            allowed_dirs = []
            
            # Add configured upload directory
            upload_dir = Config.get('upload.directory', '/app/uploads')
            if upload_dir:
                allowed_dirs.append(os.path.abspath(upload_dir))
            
            # Add any scan directories from the database
            scan_dirs = await db.get_all_directories()
            for dir_entry in scan_dirs:
                dir_path = dir_entry.get('path')
                if dir_path:
                    allowed_dirs.append(os.path.abspath(dir_path))
            
            # Check if filepath is within any allowed directory
            is_allowed = False
            for allowed_dir in allowed_dirs:
                # Ensure the file is within the allowed directory (not the directory itself)
                if filepath_resolved.startswith(allowed_dir + os.sep):
                    is_allowed = True
                    break
            
            if not is_allowed:
                logger.warning(f"Attempted unauthorized file access: {filepath} (resolved: {filepath_resolved})")
                return JSONResponse({
                    "error": "Access denied"
                }, status_code=403)
            
            # Additional security check - ensure it's actually a file and not a directory
            if not os.path.isfile(filepath_resolved):
                return JSONResponse({
                    "error": "File not found on server"
                }, status_code=404)
            
        except Exception as e:
            logger.error(f"Error validating file path: {e}")
            return JSONResponse({
                "error": "Invalid file path"
            }, status_code=400)
        
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
        logger.error(f"Download error: {e}", exc_info=True)
        return JSONResponse({
            "error": "An error occurred while processing your request"
        }, status_code=500)
