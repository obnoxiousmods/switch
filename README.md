# Switch Game Repository - Community Edition

A community website for managing and distributing Nintendo Switch game files (.nsp, .nsz, .xci) with a modern, reactive search interface.

## Technology Stack

- **Backend**: Starlette (async Python web framework)
- **Database**: ArangoDB
- **Frontend**: HTML + JavaScript (served via Starlette templates)

## Features

- 🎮 Clean, modern interface with reactive search
- ⚡ Real-time client-side filtering as you type
- 🔍 Auto-focused search box for instant access
- 📦 Support for .nsp, .nsz, and .xci file types
- 🌐 Support for both local filepaths and URLs
- 🎨 Dark theme interface with smooth transitions

## Requirements

- Python 3.10 or higher (tested with Python 3.10+)
- ArangoDB 3.x or higher

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/obnoxiousmods/switch.git
cd switch
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up ArangoDB

Install ArangoDB from [https://www.arangodb.com/download/](https://www.arangodb.com/download/)

Start ArangoDB service:
```bash
# Linux/macOS
sudo systemctl start arangodb3

# Or manually
arangod
```

### 4. Configure environment variables

Copy the example environment file and update with your settings:

```bash
cp .env.example .env
```

Edit `.env` with your ArangoDB credentials:

```env
ARANGODB_HOST=localhost
ARANGODB_PORT=8529
ARANGODB_USERNAME=root
ARANGODB_PASSWORD=your_password
ARANGODB_DATABASE=switch_db
SECRET_KEY=your-secret-key-here
DEBUG=true
```

### 5. Run the application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at: `http://localhost:8000`

## Project Structure

```
switch/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Starlette app entry point
│   ├── config.py               # Configuration management
│   ├── database.py             # ArangoDB connection and queries
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── api.py             # API routes (/api/list)
│   │   └── pages.py           # Page routes (homepage)
│   ├── models/
│   │   ├── __init__.py
│   │   └── entry.py           # Entry model/schema
│   └── templates/
│       ├── base.html          # Base template
│       └── index.html         # Homepage with search dashboard
├── static/
│   ├── css/
│   │   └── style.css          # Styles for the dashboard
│   └── js/
│       └── search.js          # Reactive search logic
├── requirements.txt
├── .env.example               # Example environment variables
└── README.md
```

## API Endpoints

### GET `/api/list`

Returns all game entries from the database.

**Response:**
```json
{
  "entries": [
    {
      "id": "unique_id",
      "name": "Game Title",
      "source": "filepath or url",
      "type": "filepath|url",
      "file_type": "nsp|nsz|xci",
      "size": 1234567890,
      "created_at": "2026-02-13T12:00:00",
      "created_by": "username",
      "metadata": {
        "description": "Game description",
        "version": "1.0.0"
      }
    }
  ]
}
```

## Database Schema

The `entries` collection in ArangoDB uses the following schema:

```json
{
  "_key": "auto-generated",
  "name": "string (game title/name)",
  "source": "string (full filepath or HTTPS URL)",
  "type": "string (filepath or url)",
  "file_type": "string (nsp, nsz, or xci)",
  "size": "integer (bytes)",
  "created_at": "string (ISO timestamp)",
  "created_by": "string (username - for future use)",
  "metadata": {
    "description": "string (optional)",
    "version": "string (optional)"
  }
}
```

## Adding Sample Data

You can add sample entries using the Python shell:

```python
from app.database import db
from app.models.entry import Entry
import asyncio

async def add_sample_data():
    await db.connect()
    
    sample_entries = [
        {
            "name": "Super Mario Odyssey",
            "source": "/games/super_mario_odyssey.nsp",
            "type": "filepath",
            "file_type": "nsp",
            "size": 5800000000,
            "created_by": "admin",
            "metadata": {
                "description": "A 3D platform game",
                "version": "1.3.0"
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
                "version": "1.6.0"
            }
        }
    ]
    
    for entry_data in sample_entries:
        await db.add_entry(entry_data)
    
    await db.disconnect()

asyncio.run(add_sample_data())
```

## Development

### Running in development mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Checking logs

The application uses Python's logging module. Logs will be printed to stdout.

## Future Features

The following features are planned but not yet implemented:

- User registration and authentication
- Admin control panel
- User roles (admin/mod/uploader/downloader)
- Mod panel and uploader panel
- File serving endpoint for local files
- HTTPS proxy for external URLs
- File upload functionality

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

See LICENSE file for details.

## Support

For issues and questions, please use the GitHub issue tracker.