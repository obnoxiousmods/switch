import logging
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from app.routes.pages import index
from app.routes.api import list_entries
from app.database import db

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
    try:
        await db.connect()
        logger.info("→ Database connected successfully")
    except Exception as e:
        logger.error(f"→ Failed to connect to database: {e}")
        logger.warning("→ App will continue but database features won't work")

# Shutdown event
@app.on_event("shutdown")
async def shutdown():
    logger.info("→ App shutting down...")
    try:
        await db.disconnect()
        logger.info("→ Database disconnected")
    except Exception as e:
        logger.error(f"→ Error disconnecting from database: {e}")