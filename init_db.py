#!/usr/bin/env python3
"""
Database Initialization Script for Switch Game Repository

This script initializes the ArangoDB database for the Switch game repository.
It creates the database, collections, and populates them with sample/dummy data.

Usage:
    python init_db.py

Default credentials: root:root
Database name: switch_db
"""

import sys
from datetime import datetime, timedelta
from arango import ArangoClient
from arango.exceptions import DatabaseCreateError, CollectionCreateError

# Configuration
ARANGODB_HOST = "localhost"
ARANGODB_PORT = 8529
ARANGODB_USERNAME = "root"
ARANGODB_PASSWORD = "root"
ARANGODB_DATABASE = "switch_db"

# Sample game data to populate the database
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
        "created_by": "uploader1",
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
        "created_by": "uploader2",
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
        "created_by": "uploader1",
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
        "created_by": "uploader2",
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
        "created_by": "uploader1",
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
        "created_by": "uploader2",
        "metadata": {
            "description": "Tactical role-playing game",
            "version": "2.0.0",
            "publisher": "Nintendo",
            "release_date": "2023-01-20"
        }
    }
]


def init_database():
    """Initialize the ArangoDB database with collections and sample data"""
    
    print("=" * 60)
    print("Switch Game Repository - Database Initialization")
    print("=" * 60)
    print()
    
    # Connect to ArangoDB
    print(f"Connecting to ArangoDB at {ARANGODB_HOST}:{ARANGODB_PORT}...")
    try:
        client = ArangoClient(hosts=f"http://{ARANGODB_HOST}:{ARANGODB_PORT}")
    except Exception as e:
        print(f"❌ Failed to connect to ArangoDB: {e}")
        print("\nMake sure ArangoDB is running:")
        print("  - Linux/macOS: sudo systemctl start arangodb3")
        print("  - Or manually: arangod")
        sys.exit(1)
    
    # Connect to _system database
    print(f"Authenticating with username: {ARANGODB_USERNAME}")
    try:
        sys_db = client.db(
            '_system',
            username=ARANGODB_USERNAME,
            password=ARANGODB_PASSWORD
        )
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print("\nPlease check your ArangoDB credentials.")
        sys.exit(1)
    
    print("✓ Connected successfully")
    print()
    
    # Create database
    print(f"Creating database: {ARANGODB_DATABASE}")
    try:
        if sys_db.has_database(ARANGODB_DATABASE):
            print(f"⚠ Database '{ARANGODB_DATABASE}' already exists")
            response = input("Do you want to DELETE and recreate it? (yes/no): ")
            if response.lower() == 'yes':
                sys_db.delete_database(ARANGODB_DATABASE)
                print(f"✓ Deleted existing database")
                sys_db.create_database(ARANGODB_DATABASE)
                print(f"✓ Created database: {ARANGODB_DATABASE}")
            else:
                print("Using existing database...")
        else:
            sys_db.create_database(ARANGODB_DATABASE)
            print(f"✓ Created database: {ARANGODB_DATABASE}")
    except DatabaseCreateError as e:
        print(f"❌ Failed to create database: {e}")
        sys.exit(1)
    print()
    
    # Connect to the application database
    print(f"Connecting to database: {ARANGODB_DATABASE}")
    try:
        db = client.db(
            ARANGODB_DATABASE,
            username=ARANGODB_USERNAME,
            password=ARANGODB_PASSWORD
        )
        print("✓ Connected to database")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        sys.exit(1)
    print()
    
    # Create entries collection
    print("Creating collection: entries")
    try:
        if db.has_collection('entries'):
            print("⚠ Collection 'entries' already exists")
            entries_collection = db.collection('entries')
            
            # Check if collection has data
            count = entries_collection.count()
            if count > 0:
                print(f"⚠ Collection has {count} existing documents")
                response = input("Do you want to DELETE existing data? (yes/no): ")
                if response.lower() == 'yes':
                    entries_collection.truncate()
                    print("✓ Deleted existing documents")
                else:
                    print("Keeping existing data...")
        else:
            entries_collection = db.create_collection('entries')
            print("✓ Created collection: entries")
    except CollectionCreateError as e:
        print(f"❌ Failed to create collection: {e}")
        sys.exit(1)
    print()
    
    # Insert sample data
    print(f"Inserting {len(SAMPLE_GAMES)} sample game entries...")
    print()
    
    inserted_count = 0
    base_time = datetime.utcnow()
    
    for i, game in enumerate(SAMPLE_GAMES):
        # Add timestamp (stagger the created_at times)
        game['created_at'] = (base_time - timedelta(hours=i*2)).isoformat()
        
        try:
            result = entries_collection.insert(game)
            inserted_count += 1
            print(f"  ✓ [{inserted_count}/{len(SAMPLE_GAMES)}] {game['name']}")
            print(f"    - Type: {game['file_type'].upper()} ({game['type']})")
            print(f"    - Size: {game['size'] / 1_000_000_000:.2f} GB")
            print(f"    - ID: {result['_key']}")
        except Exception as e:
            print(f"  ❌ Failed to insert {game['name']}: {e}")
    
    print()
    print("=" * 60)
    print("Database Initialization Complete!")
    print("=" * 60)
    print()
    print(f"Database: {ARANGODB_DATABASE}")
    print(f"Collection: entries")
    print(f"Total Entries: {inserted_count}/{len(SAMPLE_GAMES)}")
    print()
    print("You can now start the application with:")
    print("  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print()
    print("Web interface will be available at:")
    print("  http://localhost:8000")
    print()


if __name__ == "__main__":
    try:
        init_database()
    except KeyboardInterrupt:
        print("\n\n⚠ Initialization cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
