import logging
from datetime import datetime, timedelta, timezone
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse, JSONResponse
from starlette.templating import Jinja2Templates

from app.config import Config
from app.database import db

logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="app/templates")

# Sample game data to populate during initialization
SAMPLE_GAMES = [
    {
        "name": "Super Mario Odyssey",
        "source": "/games/super_mario_odyssey.nsp",
        "type": "filepath",
        "file_type": "nsp",
        "size": 5800000000,
        "created_by": "admin",
        "metadata": {
            "description": "A 3D platform game where Mario explores various kingdoms",
            "version": "1.3.0",
            "publisher": "Nintendo",
            "release_date": "2017-10-27"
        }
    },
    {
        "name": "The Legend of Zelda: Breath of the Wild",
        "source": "https://example.com/zelda_botw.nsz",
        "type": "url",
        "file_type": "nsz",
        "size": 13400000000,
        "created_by": "admin",
        "metadata": {
            "description": "Open-world action-adventure game",
            "version": "1.6.0",
            "publisher": "Nintendo",
            "release_date": "2017-03-03"
        }
    },
    {
        "name": "Mario Kart 8 Deluxe",
        "source": "/games/mario_kart_8_deluxe.nsp",
        "type": "filepath",
        "file_type": "nsp",
        "size": 6900000000,
        "created_by": "admin",
        "metadata": {
            "description": "Racing game featuring Nintendo characters",
            "version": "2.3.0",
            "publisher": "Nintendo",
            "release_date": "2017-04-28"
        }
    },
    {
        "name": "Animal Crossing: New Horizons",
        "source": "/games/animal_crossing_new_horizons.xci",
        "type": "filepath",
        "file_type": "xci",
        "size": 7100000000,
        "created_by": "admin",
        "metadata": {
            "description": "Life simulation game set on a deserted island",
            "version": "2.0.6",
            "publisher": "Nintendo",
            "release_date": "2020-03-20"
        }
    },
    {
        "name": "Splatoon 3",
        "source": "https://example.com/splatoon_3.nsz",
        "type": "url",
        "file_type": "nsz",
        "size": 6200000000,
        "created_by": "admin",
        "metadata": {
            "description": "Third-person shooter game with ink-based gameplay",
            "version": "4.1.0",
            "publisher": "Nintendo",
            "release_date": "2022-09-09"
        }
    },
    {
        "name": "Pokemon Scarlet",
        "source": "/games/pokemon_scarlet.nsp",
        "type": "filepath",
        "file_type": "nsp",
        "size": 7500000000,
        "created_by": "admin",
        "metadata": {
            "description": "Open-world Pokemon adventure game",
            "version": "3.0.1",
            "publisher": "The Pokemon Company",
            "release_date": "2022-11-18"
        }
    },
    {
        "name": "Metroid Dread",
        "source": "/games/metroid_dread.nsp",
        "type": "filepath",
        "file_type": "nsp",
        "size": 4100000000,
        "created_by": "admin",
        "metadata": {
            "description": "Action-adventure side-scrolling game",
            "version": "1.0.4",
            "publisher": "Nintendo",
            "release_date": "2021-10-08"
        }
    },
    {
        "name": "Kirby and the Forgotten Land",
        "source": "https://example.com/kirby_forgotten_land.nsz",
        "type": "url",
        "file_type": "nsz",
        "size": 5900000000,
        "created_by": "admin",
        "metadata": {
            "description": "3D platform adventure starring Kirby",
            "version": "1.1.0",
            "publisher": "Nintendo",
            "release_date": "2022-03-25"
        }
    },
    {
        "name": "Xenoblade Chronicles 3",
        "source": "/games/xenoblade_chronicles_3.xci",
        "type": "filepath",
        "file_type": "xci",
        "size": 15600000000,
        "created_by": "admin",
        "metadata": {
            "description": "Action role-playing game",
            "version": "2.2.0",
            "publisher": "Nintendo",
            "release_date": "2022-07-29"
        }
    },
    {
        "name": "Fire Emblem Engage",
        "source": "/games/fire_emblem_engage.nsp",
        "type": "filepath",
        "file_type": "nsp",
        "size": 11300000000,
        "created_by": "admin",
        "metadata": {
            "description": "Tactical role-playing game",
            "version": "2.0.0",
            "publisher": "Nintendo",
            "release_date": "2023-01-20"
        }
    }
]


async def admin_init_page(request: Request) -> Response:
    """Show initialization form"""
    # If already initialized, redirect to admin dashboard
    if Config.is_initialized():
        return RedirectResponse(url="/admincp", status_code=303)
    
    return templates.TemplateResponse(
        request,
        "admin/init.html",
        {
            "title": "Initialize System"
        }
    )


async def admin_init_submit(request: Request) -> Response:
    """Handle initialization form submission"""
    # If already initialized, return error
    if Config.is_initialized():
        return JSONResponse(
            {"success": False, "error": "System already initialized"},
            status_code=400
        )
    
    try:
        # Parse form data
        form_data = await request.form()
        validated_data = {}
        
        # Validate required fields
        required_fields = ['website_name', 'db_host', 'db_port', 'db_username', 'db_password', 'db_name']
        for field in required_fields:
            if not form_data.get(field):
                return JSONResponse(
                    {"success": False, "error": f"Missing required field: {field}"},
                    status_code=400
                )
            validated_data[field] = form_data.get(field)
        
        # Validate port number
        try:
            validated_data['db_port'] = int(validated_data['db_port'])
            if not (0 < validated_data['db_port'] < 65536):
                raise ValueError
        except ValueError:
            return JSONResponse(
                {"success": False, "error": "Invalid port number"},
                status_code=400
            )
        
        # Initialize configuration
        Config.initialize({
            'website_name': validated_data['website_name'],
            'db_host': validated_data['db_host'],
            'db_port': validated_data['db_port'],
            'db_username': validated_data['db_username'],
            'db_password': validated_data['db_password'],
            'db_name': validated_data['db_name'],
        })
        
        # Connect to database and create dummy entries
        try:
            await db.connect()
            
            # Add sample games
            base_time = datetime.now(timezone.utc)
            for i, game in enumerate(SAMPLE_GAMES):
                game['created_at'] = (base_time - timedelta(hours=i*2)).isoformat()
                await db.add_entry(game)
            
            logger.info(f"Created {len(SAMPLE_GAMES)} sample entries")
            
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            # Rollback config
            Config.set('initialized', False)
            Config.save()
            return JSONResponse(
                {"success": False, "error": f"Database error: {str(e)}"},
                status_code=500
            )
        
        return JSONResponse({"success": True, "redirect": "/"})
        
    except Exception as e:
        logger.error(f"Initialization error: {e}")
        return JSONResponse(
            {"success": False, "error": str(e)},
            status_code=500
        )


async def admin_dashboard(request: Request) -> Response:
    """Admin control panel dashboard"""
    if not Config.is_initialized():
        return RedirectResponse(url="/admincp/init", status_code=303)
    
    return templates.TemplateResponse(
        request,
        "admin/dashboard.html",
        {
            "title": "Admin Dashboard",
            "app_name": Config.get('app.name', 'Switch Game Repository'),
            "db_host": Config.get('database.host', 'localhost'),
            "db_name": Config.get('database.database', 'switch_db'),
        }
    )
