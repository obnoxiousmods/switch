import logging
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.database import db
from app.models.api_key import ApiKey

logger = logging.getLogger(__name__)


class APIAuthMiddleware(BaseHTTPMiddleware):
    """Middleware to authenticate API requests using API keys"""
    
    async def dispatch(self, request: Request, call_next):
        # Only authenticate API endpoints
        if not request.url.path.startswith('/api/'):
            return await call_next(request)
        
        # Extract API key from Authorization header or query parameter
        api_key = None
        
        # Check Authorization header (Bearer token)
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            api_key = auth_header.replace('Bearer ', '').strip()
        
        # Check query parameter as fallback
        if not api_key:
            api_key = request.query_params.get('api_key')
        
        # If no API key provided, allow request but mark as unauthenticated
        # (Some endpoints might allow unauthenticated access)
        if not api_key:
            # Store auth info in request state
            request.state.authenticated = False
            request.state.user_id = None
            request.state.api_key_id = None
            
            # Process request
            response = await call_next(request)
            return response
        
        # Validate API key
        try:
            key_hash = ApiKey.hash_key(api_key)
            api_key_doc = await db.get_api_key_by_hash(key_hash)
            
            if not api_key_doc:
                return JSONResponse(
                    {"error": "Invalid API key"},
                    status_code=401
                )
            
            if not api_key_doc.get('is_active', False):
                return JSONResponse(
                    {"error": "API key has been revoked"},
                    status_code=401
                )
            
            # Store auth info in request state
            request.state.authenticated = True
            request.state.user_id = api_key_doc.get('user_id')
            request.state.api_key_id = api_key_doc.get('_key')
            
            # Update last used timestamp (async, don't wait)
            await db.update_api_key_last_used(api_key_doc.get('_key'))
            
            # Process request
            response = await call_next(request)
            
            # Log API usage
            await self.log_api_usage(request, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error authenticating API key: {e}")
            return JSONResponse(
                {"error": "Authentication error"},
                status_code=500
            )
    
    async def log_api_usage(self, request: Request, response):
        """Log API usage to database"""
        try:
            # Get IP address
            ip_address = request.client.host if request.client else 'unknown'
            
            # Prepare usage data
            usage_data = {
                'user_id': request.state.user_id,
                'api_key_id': request.state.api_key_id,
                'endpoint': request.url.path,
                'method': request.method,
                'status_code': response.status_code,
                'ip_address': ip_address
            }
            
            # Log to database (async, fire and forget)
            await db.log_api_usage(usage_data)
            
        except Exception as e:
            logger.error(f"Error logging API usage: {e}")
