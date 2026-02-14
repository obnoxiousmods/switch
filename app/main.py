import logging
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware

from app.routes.pages import index, api_docs_page
from app.routes.api import list_entries, download_entry, submit_report, compute_file_hashes
from app.routes.admin import (
    admin_init_page, admin_init_submit, admin_dashboard,
    admin_directories, admin_add_directory, admin_delete_directory,
    admin_scan_directory, admin_clear_entries, admin_rescan_all,
    admin_users, admin_update_user_role, admin_force_password_change,
    admin_api_keys, admin_revoke_api_key, admin_user_api_usage,
    admin_audit_logs, admin_activity_logs, admin_storage_info,
    admin_upload_statistics, admin_reports, admin_resolve_report,
    admin_migrate_passwords, admin_password_migration_status
)
from app.routes.auth import login_page, login_submit, register_page, register_submit, logout
from app.routes.settings import settings_page, change_password, download_history_page, totp_setup_page, totp_enable, totp_verify_and_enable, totp_disable
from app.routes.api_keys import api_keys_page, generate_api_key, revoke_api_key, api_usage_page
from app.routes.mod import (
    mod_dashboard, mod_requests, mod_approve_request, mod_reject_request,
    mod_force_password_change, user_submit_request, user_requests_page,
    mod_corrupt_games, mod_mark_entry_valid, mod_clear_all_corrupt_flags
)
from app.routes.uploader import (
    uploader_dashboard, uploader_game_requests, uploader_approve_request,
    uploader_reject_request, uploader_upload_page, uploader_upload_submit,
    uploader_get_directories
)
from app.database import db
from app.config import Config
from app.middleware.api_auth import APIAuthMiddleware

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
    Route("/api-docs", api_docs_page),
    Route("/api/list", list_entries),
    Route("/api/download/{entry_id}", download_entry),
    Route("/api/reports/submit", submit_report, methods=["POST"]),
    Route("/api/entries/{entry_id}/hashes", compute_file_hashes, methods=["GET"]),
    Route("/login", login_page, methods=["GET"]),
    Route("/login", login_submit, methods=["POST"]),
    Route("/register", register_page, methods=["GET"]),
    Route("/register", register_submit, methods=["POST"]),
    Route("/logout", logout, methods=["GET"]),
    Route("/settings", settings_page, methods=["GET"]),
    Route("/settings/change-password", change_password, methods=["POST"]),
    Route("/settings/download-history", download_history_page, methods=["GET"]),
    Route("/settings/totp", totp_setup_page, methods=["GET"]),
    Route("/settings/totp/enable", totp_enable, methods=["POST"]),
    Route("/settings/totp/verify", totp_verify_and_enable, methods=["POST"]),
    Route("/settings/totp/disable", totp_disable, methods=["POST"]),
    Route("/settings/api-keys", api_keys_page, methods=["GET"]),
    Route("/settings/api-keys/generate", generate_api_key, methods=["POST"]),
    Route("/settings/api-keys/revoke", revoke_api_key, methods=["POST"]),
    Route("/settings/api-usage", api_usage_page, methods=["GET"]),
    Route("/requests", user_requests_page, methods=["GET"]),
    Route("/requests/submit", user_submit_request, methods=["POST"]),
    Route("/modcp", mod_dashboard),
    Route("/modcp/requests", mod_requests, methods=["GET"]),
    Route("/modcp/requests/approve", mod_approve_request, methods=["POST"]),
    Route("/modcp/requests/reject", mod_reject_request, methods=["POST"]),
    Route("/modcp/users/force-change-password", mod_force_password_change, methods=["POST"]),
    Route("/modcp/corrupt-games", mod_corrupt_games, methods=["GET"]),
    Route("/modcp/corrupt-games/mark-valid", mod_mark_entry_valid, methods=["POST"]),
    Route("/modcp/corrupt-games/clear-all", mod_clear_all_corrupt_flags, methods=["POST"]),
    Route("/uploadercp", uploader_dashboard),
    Route("/uploadercp/game-requests", uploader_game_requests, methods=["GET"]),
    Route("/uploadercp/game-requests/approve", uploader_approve_request, methods=["POST"]),
    Route("/uploadercp/game-requests/reject", uploader_reject_request, methods=["POST"]),
    Route("/uploadercp/upload", uploader_upload_page, methods=["GET"]),
    Route("/uploadercp/upload", uploader_upload_submit, methods=["POST"]),
    Route("/uploadercp/directories", uploader_get_directories, methods=["GET"]),
    Route("/admincp/init", admin_init_page, methods=["GET"]),
    Route("/admincp/init", admin_init_submit, methods=["POST"]),
    Route("/admincp", admin_dashboard),
    Route("/admincp/directories", admin_directories, methods=["GET"]),
    Route("/admincp/directories/add", admin_add_directory, methods=["POST"]),
    Route("/admincp/directories/delete", admin_delete_directory, methods=["POST"]),
    Route("/admincp/directories/scan", admin_scan_directory, methods=["POST"]),
    Route("/admincp/directories/clear", admin_clear_entries, methods=["POST"]),
    Route("/admincp/directories/rescan", admin_rescan_all, methods=["POST"]),
    Route("/admincp/users", admin_users, methods=["GET"]),
    Route("/admincp/users/update-role", admin_update_user_role, methods=["POST"]),
    Route("/admincp/users/force-change-password", admin_force_password_change, methods=["POST"]),
    Route("/admincp/api-keys", admin_api_keys, methods=["GET"]),
    Route("/admincp/api-keys/revoke", admin_revoke_api_key, methods=["POST"]),
    Route("/admincp/api-usage", admin_user_api_usage, methods=["GET"]),
    Route("/admincp/audit-logs", admin_audit_logs, methods=["GET"]),
    Route("/admincp/activity-logs", admin_activity_logs, methods=["GET"]),
    Route("/admincp/storage-info", admin_storage_info, methods=["GET"]),
    Route("/admincp/upload-statistics", admin_upload_statistics, methods=["GET"]),
    Route("/admincp/reports", admin_reports, methods=["GET"]),
    Route("/admincp/reports/resolve", admin_resolve_report, methods=["POST"]),
    Route("/admincp/password-migration/status", admin_password_migration_status, methods=["GET"]),
    Route("/admincp/password-migration/migrate", admin_migrate_passwords, methods=["POST"]),
    Mount("/static", StaticFiles(directory="static"), name="static"),
]

# Middleware
middleware = [
    Middleware(SessionMiddleware, secret_key=Config.SECRET_KEY()),
    Middleware(APIAuthMiddleware)
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