import logging
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from app.routes.pages import index
from app.routes.api import list_entries
from app.routes.admin import admin_init_page, admin_init_submit, admin_dashboard
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
    Route("/admincp/init", admin_init_page, methods=["GET"]),
    Route("/admincp/init", admin_init_submit, methods=["POST"]),
    Route("/admincp", admin_dashboard),
    Mount("/static", StaticFiles(directory="static"), name="static"),
]

# Create Starlette application
app = Starlette(
    debug=True,
    routes=routes,
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