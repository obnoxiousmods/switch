from starlette.responses import JSONResponse, FileResponse, RedirectResponse
from starlette.requests import Request
from starlette.background import BackgroundTask
import os
import logging
import hashlib
import asyncio

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
        sort_by = request.query_params.get('sort_by', 'name')
        
        # Validate sort_by parameter (name, downloads, size, or recent)
        if sort_by not in ['name', 'downloads', 'size', 'recent']:
            sort_by = 'name'
        
        # Get entries with download counts
        entries = await db.get_all_entries_with_download_counts(
            search_query=search_query,
            sort_by=sort_by
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


async def submit_report(request: Request):
    """API endpoint to submit a report for a file"""
    # Require authentication - either session or API key
    has_session = request.session.get('user_id') is not None
    has_api_auth = getattr(request.state, 'authenticated', False)
    
    if not has_session and not has_api_auth:
        return JSONResponse({
            "success": False,
            "error": "Authentication required. Please log in or use an API key."
        }, status_code=401)
    
    try:
        # Get user info
        user_id = request.session.get('user_id')
        username = request.session.get('username')
        
        # For API key authentication, use the authenticated user_id
        if not user_id and has_api_auth:
            user_id = request.state.user_id
            # Get username from database for API key users
            user_doc = await db.get_user_by_id(user_id)
            if user_doc:
                username = user_doc.get('username', 'api_user')
        
        if not user_id or not username:
            return JSONResponse({
                "success": False,
                "error": "User information not found"
            }, status_code=401)
        
        # Get form data
        form_data = await request.form()
        entry_id = form_data.get('entry_id', '').strip()
        entry_name = form_data.get('entry_name', '').strip()
        reason = form_data.get('reason', '').strip()
        description = form_data.get('description', '').strip()
        
        if not entry_id or not reason:
            return JSONResponse({
                "success": False,
                "error": "Missing required fields"
            }, status_code=400)
        
        # Verify entry exists
        entry = await db.get_entry_by_id(entry_id)
        if not entry:
            return JSONResponse({
                "success": False,
                "error": "Entry not found"
            }, status_code=404)
        
        # Create the report
        report_id = await db.create_report(
            entry_id=entry_id,
            entry_name=entry_name or entry.get('name', 'Unknown'),
            user_id=user_id,
            username=username,
            reason=reason,
            description=description
        )
        
        if not report_id:
            return JSONResponse({
                "success": False,
                "error": "Failed to create report"
            }, status_code=500)
        
        # Always mark the entry as corrupt when any report is submitted
        await db.mark_entry_corrupt(entry_id, True)
        logger.info(f"Entry {entry_id} marked as corrupt due to report submission")
        
        # Log the report activity
        ip_info = get_ip_info(request)
        activity_data = {
            'event_type': 'report_submitted',
            'user_id': user_id,
            'username': username,
            'details': {
                'report_id': report_id,
                'entry_id': entry_id,
                'entry_name': entry_name or entry.get('name', 'Unknown'),
                'reason': reason
            },
            'ip_address': ip_info['ip_address'],
            'client_ip': ip_info['client_ip']
        }
        if 'forwarded_ip' in ip_info:
            activity_data['forwarded_ip'] = ip_info['forwarded_ip']
        
        await db.add_activity_log(activity_data)
        
        logger.info(f"Report submitted for entry {entry_id} by user {username} from {format_ip_for_log(request)}")
        
        return JSONResponse({
            "success": True,
            "message": "Report submitted successfully"
        })
        
    except Exception as e:
        logger.error(f"Report submission error: {e}", exc_info=True)
        return JSONResponse({
            "success": False,
            "error": "An error occurred while submitting the report"
        }, status_code=500)



def _compute_hashes_sync(filepath: str) -> tuple:
    """Synchronous hash computation to run in a separate thread"""
    md5_hash = hashlib.md5()
    sha256_hash = hashlib.sha256()
    
    # Read file in chunks to handle large files
    chunk_size = 8192
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            md5_hash.update(chunk)
            sha256_hash.update(chunk)
    
    return md5_hash.hexdigest(), sha256_hash.hexdigest()


async def _compute_and_store_hashes(entry_id: str, filepath: str):
    """Background task to compute and store file hashes in a separate thread"""
    try:
        logger.info(f"Computing hashes for entry {entry_id}: {filepath}")
        
        # Mark entry as processing by setting temporary values
        await db.update_entry_hashes(entry_id, "processing", "processing")
        
        # Run the blocking hash computation in a separate thread
        md5_result, sha256_result = await asyncio.to_thread(_compute_hashes_sync, filepath)
        
        # Store hashes in database
        await db.update_entry_hashes(entry_id, md5_result, sha256_result)
        
        logger.info(f"Computed and stored hashes for entry {entry_id}")
    except Exception as e:
        logger.error(f"Error computing hashes in background: {e}", exc_info=True)
        # Clear processing markers on error
        try:
            await db.update_entry_hashes(entry_id, None, None)
        except:
            pass


async def compute_file_hashes(request: Request):
    """API endpoint to compute MD5 and SHA256 hashes for a file entry"""
    # Require authentication - either session or API key
    has_session = request.session.get('user_id') is not None
    has_api_auth = getattr(request.state, 'authenticated', False)
    
    if not has_session and not has_api_auth:
        return JSONResponse({
            "success": False,
            "error": "Authentication required. Please log in or use an API key."
        }, status_code=401)
    
    try:
        entry_id = request.path_params.get('entry_id')
        
        # Get the entry from the database
        entry = await db.get_entry_by_id(entry_id)
        
        if not entry:
            return JSONResponse({
                "success": False,
                "error": "Entry not found"
            }, status_code=404)
        
        # Check if hashes already exist
        if entry.get('md5_hash') and entry.get('sha256_hash'):
            return JSONResponse({
                "success": True,
                "md5": entry.get('md5_hash'),
                "sha256": entry.get('sha256_hash'),
                "cached": True
            })
        
        # Only compute hashes for filepath type entries
        if entry.get('type') != 'filepath':
            return JSONResponse({
                "success": False,
                "error": "Hash computation is only available for uploaded files"
            }, status_code=400)
        
        filepath = entry.get('source')
        
        # Validate the filepath exists and is accessible
        if not filepath or not os.path.exists(filepath) or not os.path.isfile(filepath):
            return JSONResponse({
                "success": False,
                "error": "File not found on server"
            }, status_code=404)
        
        # Return immediately and compute hashes in the background
        background_task = BackgroundTask(_compute_and_store_hashes, entry_id, filepath)
        
        return JSONResponse({
            "success": True,
            "processing": True,
            "message": "Hash computation started in background. Results will appear automatically when ready."
        }, background=background_task)
        
    except Exception as e:
        logger.error(f"Hash computation error: {e}", exc_info=True)
        return JSONResponse({
            "success": False,
            "error": "An error occurred while computing hashes"
        }, status_code=500)


async def get_entry_info(request: Request):
    """API endpoint to get entry information (for dynamic updates)"""
    # Require authentication - either session or API key
    has_session = request.session.get('user_id') is not None
    has_api_auth = getattr(request.state, 'authenticated', False)
    
    if not has_session and not has_api_auth:
        return JSONResponse({
            "success": False,
            "error": "Authentication required. Please log in or use an API key."
        }, status_code=401)
    
    try:
        entry_id = request.path_params.get('entry_id')
        
        # Get the entry from the database
        entry = await db.get_entry_by_id(entry_id)
        
        if not entry:
            return JSONResponse({
                "success": False,
                "error": "Entry not found"
            }, status_code=404)
        
        # Return entry information
        return JSONResponse({
            "success": True,
            "entry": {
                "_key": entry.get("_key"),
                "name": entry.get("name"),
                "file_type": entry.get("file_type"),
                "size": entry.get("size"),
                "created_by": entry.get("created_by"),
                "created_at": entry.get("created_at"),
                "corrupt": entry.get("corrupt", False),
                "md5_hash": entry.get("md5_hash"),
                "sha256_hash": entry.get("sha256_hash"),
                "type": entry.get("type"),
                "downloads": entry.get("downloads", 0)
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching entry info: {e}", exc_info=True)
        return JSONResponse({
            "success": False,
            "error": "An error occurred while fetching entry information"
        }, status_code=500)
