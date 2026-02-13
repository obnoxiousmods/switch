from starlette.responses import JSONResponse, FileResponse, RedirectResponse
from starlette.requests import Request
import os

from app.database import db

async def list_entries(request: Request):
    """API endpoint to list all entries"""
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
    try:
        entry_id = request.path_params.get('entry_id')
        
        # Get the entry from the database
        entry = await db.get_entry_by_id(entry_id)
        
        if not entry:
            return JSONResponse({
                "error": "Entry not found"
            }, status_code=404)
        
        # Track download if user is logged in
        user_id = request.session.get('user_id')
        if user_id:
            await db.add_download_history(
                user_id=user_id,
                entry_id=entry_id,
                entry_name=entry.get('name', 'Unknown')
            )
        
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
