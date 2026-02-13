import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from arangoasync import ArangoClient
from arangoasync.auth import Auth
from arangoasync.database import StandardDatabase
from arangoasync.collection import StandardCollection

from app.config import Config

logger = logging.getLogger(__name__)

class Database:
    """ArangoDB database connection and operations"""
    
    def __init__(self):
        self.client: Optional[ArangoClient] = None
        self.db: Optional[StandardDatabase] = None
        self.entries_collection: Optional[StandardCollection] = None
        self.users_collection: Optional[StandardCollection] = None
        self.directories_collection: Optional[StandardCollection] = None
        self.download_history_collection: Optional[StandardCollection] = None
    
    async def connect(self):
        """Connect to ArangoDB and initialize database/collections"""
        try:
            # Initialize ArangoDB client
            self.client = ArangoClient(hosts=Config.get_arangodb_url())
            
            # Create auth object
            auth = Auth(username=Config.ARANGODB_USERNAME(), password=Config.ARANGODB_PASSWORD())
            
            # Connect to _system database to check if our database exists
            sys_db = await self.client.db('_system', auth=auth)
            
            # Create database if it doesn't exist
            if not await sys_db.has_database(Config.ARANGODB_DATABASE()):
                await sys_db.create_database(Config.ARANGODB_DATABASE())
                logger.info(f"Created database: {Config.ARANGODB_DATABASE()}")
            
            # Connect to the application database
            self.db = await self.client.db(
                Config.ARANGODB_DATABASE(),
                auth=auth
            )
            
            # Create entries collection if it doesn't exist
            if not await self.db.has_collection('entries'):
                self.entries_collection = await self.db.create_collection('entries')
                logger.info("Created collection: entries")
            else:
                self.entries_collection = self.db.collection('entries')
            
            # Create users collection if it doesn't exist
            if not await self.db.has_collection('users'):
                self.users_collection = await self.db.create_collection('users')
                logger.info("Created collection: users")
            else:
                self.users_collection = self.db.collection('users')
            
            # Create directories collection if it doesn't exist
            if not await self.db.has_collection('directories'):
                self.directories_collection = await self.db.create_collection('directories')
                logger.info("Created collection: directories")
            else:
                self.directories_collection = self.db.collection('directories')
            
            # Create download_history collection if it doesn't exist
            if not await self.db.has_collection('download_history'):
                self.download_history_collection = await self.db.create_collection('download_history')
                logger.info("Created collection: download_history")
            else:
                self.download_history_collection = self.db.collection('download_history')
            
            logger.info("Successfully connected to ArangoDB")
            
        except Exception as e:
            logger.error(f"Failed to connect to ArangoDB: {e}")
            raise
    
    async def disconnect(self):
        """Close database connection"""
        if self.client:
            await self.client.close()
            logger.info("Disconnected from ArangoDB")
    
    async def get_all_entries(self) -> List[Dict[str, Any]]:
        """Get all entries from the database"""
        try:
            cursor = await self.db.aql.execute(
                'FOR doc IN entries SORT doc.created_at DESC RETURN doc'
            )
            entries = []
            async with cursor:
                async for doc in cursor:
                    # Convert _key to id for API response
                    entry = {
                        'id': doc.get('_key'),
                        'name': doc.get('name'),
                        'source': doc.get('source'),
                        'type': doc.get('type'),
                        'file_type': doc.get('file_type'),
                        'size': doc.get('size'),
                        'created_at': doc.get('created_at'),
                        'created_by': doc.get('created_by', ''),
                        'metadata': doc.get('metadata', {})
                    }
                    entries.append(entry)
            return entries
        except Exception as e:
            logger.error(f"Error fetching entries: {e}")
            return []
    
    async def get_entry_by_id(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """Get a single entry by its ID"""
        try:
            doc = await self.entries_collection.get(entry_id)
            if doc:
                return {
                    'id': doc.get('_key'),
                    'name': doc.get('name'),
                    'source': doc.get('source'),
                    'type': doc.get('type'),
                    'file_type': doc.get('file_type'),
                    'size': doc.get('size'),
                    'created_at': doc.get('created_at'),
                    'created_by': doc.get('created_by', ''),
                    'metadata': doc.get('metadata', {})
                }
            return None
        except Exception as e:
            logger.error(f"Error fetching entry by ID: {e}")
            return None
    
    async def add_entry(self, entry_data: Dict[str, Any]) -> Optional[str]:
        """Add a new entry to the database"""
        try:
            # Add timestamp if not provided
            if 'created_at' not in entry_data:
                entry_data['created_at'] = datetime.utcnow().isoformat()
            
            result = await self.entries_collection.insert(entry_data)
            logger.info(f"Added entry with key: {result['_key']}")
            return result['_key']
        except Exception as e:
            logger.error(f"Error adding entry: {e}")
            return None
    
    async def delete_entry(self, entry_id: str) -> bool:
        """Delete an entry from the database"""
        try:
            await self.entries_collection.delete(entry_id)
            logger.info(f"Deleted entry: {entry_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting entry: {e}")
            return False
    
    # User management methods
    async def create_user(self, user_data: Dict[str, Any]) -> Optional[str]:
        """Create a new user"""
        try:
            # Add timestamp if not provided
            if 'created_at' not in user_data:
                user_data['created_at'] = datetime.utcnow().isoformat()
            
            result = await self.users_collection.insert(user_data)
            logger.info(f"Created user: {user_data['username']}")
            return result['_key']
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None
    
    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get a user by username"""
        try:
            cursor = await self.db.aql.execute(
                'FOR doc IN users FILTER doc.username == @username LIMIT 1 RETURN doc',
                bind_vars={'username': username}
            )
            async with cursor:
                async for doc in cursor:
                    return doc
            return None
        except Exception as e:
            logger.error(f"Error fetching user: {e}")
            return None
    
    async def user_exists(self, username: str) -> bool:
        """Check if a user exists"""
        user = await self.get_user_by_username(username)
        return user is not None
    
    # Directory management methods
    async def add_directory(self, path: str) -> Optional[str]:
        """Add a new directory to scan"""
        try:
            # Check if directory already exists
            existing = await self.get_directory_by_path(path)
            if existing:
                logger.warning(f"Directory already exists: {path}")
                return existing.get('_key')
            
            directory_data = {
                'path': path,
                'added_at': datetime.utcnow().isoformat(),
            }
            result = await self.directories_collection.insert(directory_data)
            logger.info(f"Added directory: {path}")
            return result['_key']
        except Exception as e:
            logger.error(f"Error adding directory: {e}")
            return None
    
    async def get_directory_by_path(self, path: str) -> Optional[Dict[str, Any]]:
        """Get a directory by path"""
        try:
            cursor = await self.db.aql.execute(
                'FOR doc IN directories FILTER doc.path == @path LIMIT 1 RETURN doc',
                bind_vars={'path': path}
            )
            async with cursor:
                async for doc in cursor:
                    return doc
            return None
        except Exception as e:
            logger.error(f"Error fetching directory: {e}")
            return None
    
    async def get_all_directories(self) -> List[Dict[str, Any]]:
        """Get all directories"""
        try:
            cursor = await self.db.aql.execute(
                'FOR doc IN directories SORT doc.added_at DESC RETURN doc'
            )
            directories = []
            async with cursor:
                async for doc in cursor:
                    directories.append(doc)
            return directories
        except Exception as e:
            logger.error(f"Error fetching directories: {e}")
            return []
    
    async def delete_directory(self, directory_id: str) -> bool:
        """Delete a directory"""
        try:
            await self.directories_collection.delete(directory_id)
            logger.info(f"Deleted directory: {directory_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting directory: {e}")
            return False
    
    async def clear_all_entries(self) -> bool:
        """Clear all entries from the database"""
        try:
            await self.db.aql.execute('FOR doc IN entries REMOVE doc IN entries')
            logger.info("Cleared all entries")
            return True
        except Exception as e:
            logger.error(f"Error clearing entries: {e}")
            return False
    
    async def entry_exists(self, source: str) -> bool:
        """Check if an entry with this source already exists"""
        try:
            cursor = await self.db.aql.execute(
                'FOR doc IN entries FILTER doc.source == @source LIMIT 1 RETURN doc',
                bind_vars={'source': source}
            )
            async with cursor:
                async for doc in cursor:
                    return True
            return False
        except Exception as e:
            logger.error(f"Error checking entry existence: {e}")
            return False
    
    # User settings methods
    async def update_user_password(self, user_id: str, new_password_hash: str) -> bool:
        """Update a user's password"""
        try:
            await self.users_collection.update(
                {'_key': user_id},
                {'password_hash': new_password_hash}
            )
            logger.info(f"Updated password for user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating password: {e}")
            return False
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a user by ID"""
        try:
            doc = await self.users_collection.get(user_id)
            return doc
        except Exception as e:
            logger.error(f"Error fetching user by ID: {e}")
            return None
    
    # Download history methods
    async def add_download_history(self, user_id: str, entry_id: str, entry_name: str) -> Optional[str]:
        """Add a download history record"""
        try:
            download_data = {
                'user_id': user_id,
                'entry_id': entry_id,
                'entry_name': entry_name,
                'downloaded_at': datetime.utcnow().isoformat()
            }
            result = await self.download_history_collection.insert(download_data)
            logger.info(f"Added download history for user {user_id}, entry {entry_id}")
            return result['_key']
        except Exception as e:
            logger.error(f"Error adding download history: {e}")
            return None
    
    async def get_user_download_history(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get download history for a user"""
        try:
            cursor = await self.db.aql.execute(
                'FOR doc IN download_history FILTER doc.user_id == @user_id SORT doc.downloaded_at DESC LIMIT @limit RETURN doc',
                bind_vars={'user_id': user_id, 'limit': limit}
            )
            history = []
            async with cursor:
                async for doc in cursor:
                    history.append({
                        'id': doc.get('_key'),
                        'entry_id': doc.get('entry_id'),
                        'entry_name': doc.get('entry_name'),
                        'downloaded_at': doc.get('downloaded_at')
                    })
            return history
        except Exception as e:
            logger.error(f"Error fetching download history: {e}")
            return []

# Global database instance
db = Database()
