from starlette.responses import JSONResponse
from starlette.requests import Request

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
