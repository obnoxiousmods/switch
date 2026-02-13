import logging
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware

from app.routes.pages import index
from app.routes.api import list_entries
from app.routes.admin import (
    admin_init_page, admin_init_submit, admin_dashboard,
    admin_directories, admin_add_directory, admin_delete_directory,
    admin_scan_directory, admin_clear_entries, admin_rescan_all
)
from app.routes.auth import login_page, login_submit, register_page, register_submit, logout
from app.database import db
from app.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Templates
templates = Jinja2Templates(directory="app/templates")

# Routes
routes = [
    Route("/", index),
    Route("/api/list", list_entries),
    Route("/login", login_page, methods=["GET"]),
    Route("/login", login_submit, methods=["POST"]),
    Route("/register", register_page, methods=["GET"]),
    Route("/register", register_submit, methods=["POST"]),
    Route("/logout", logout, methods=["GET"]),
    Route("/admincp/init", admin_init_page, methods=["GET"]),
    Route("/admincp/init", admin_init_submit, methods=["POST"]),
    Route("/admincp", admin_dashboard),
    Route("/admincp/directories", admin_directories, methods=["GET"]),
    Route("/admincp/directories/add", admin_add_directory, methods=["POST"]),
    Route("/admincp/directories/delete", admin_delete_directory, methods=["POST"]),
    Route("/admincp/directories/scan", admin_scan_directory, methods=["POST"]),
    Route("/admincp/directories/clear", admin_clear_entries, methods=["POST"]),
    Route("/admincp/directories/rescan", admin_rescan_all, methods=["POST"]),
    Mount("/static", StaticFiles(directory="static"), name="static"),
]

# Middleware
middleware = [
    Middleware(SessionMiddleware, secret_key=Config.SECRET_KEY())
]

# Create Starlette application
app = Starlette(
    debug=True,
    routes=routes,
    middleware=middleware,
)

# Startup event
@app.on_event("startup")
async def startup():
    logger.info("→ App starting...")
    
    # Only try to connect to database if initialized
    if Config.is_initialized():
        try:
            await db.connect()
            logger.info("→ Database connected successfully")
        except Exception as e:
            logger.error(f"→ Failed to connect to database: {e}")
            logger.warning("→ App will continue but database features won't work")
    else:
        logger.info("→ System not initialized. Please visit /admincp/init to set up.")

# Shutdown event
@app.on_event("shutdown")
async def shutdown():
    logger.info("→ App shutting down...")
    if Config.is_initialized():
        try:
            await db.disconnect()
            logger.info("→ Database disconnected")
        except Exception as e:
            logger.error(f"→ Error disconnecting from database: {e}")