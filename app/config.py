import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any

class Config:
    """Application configuration loaded from config.yaml"""
    
    _config: Optional[Dict[str, Any]] = None
    _config_path = Path(__file__).parent / "config.yaml"
    
    @classmethod
    def load(cls):
        """Load configuration from config.yaml"""
        if not cls._config_path.exists():
            # Create default config if it doesn't exist
            cls._config = {
                "initialized": False,
                "app": {
                    "name": "Switch Game Repository",
                    "debug": True,
                },
                "database": {},
                "security": {
                    "secret_key": "change-this-to-a-very-long-random-secret-2026!"
                }
            }
            cls.save()
        else:
            with open(cls._config_path, 'r') as f:
                cls._config = yaml.safe_load(f) or {}
    
    @classmethod
    def save(cls):
        """Save configuration to config.yaml"""
        with open(cls._config_path, 'w') as f:
            yaml.dump(cls._config, f, default_flow_style=False, sort_keys=False)
    
    @classmethod
    def get(cls, key: str, default=None):
        """Get a configuration value"""
        if cls._config is None:
            cls.load()
        
        keys = key.split('.')
        value = cls._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value
    
    @classmethod
    def set(cls, key: str, value):
        """Set a configuration value"""
        if cls._config is None:
            cls.load()
        
        keys = key.split('.')
        config = cls._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    @classmethod
    def is_initialized(cls) -> bool:
        """Check if the application has been initialized"""
        return cls.get('initialized', False)
    
    @classmethod
    def initialize(cls, data: Dict[str, Any]):
        """Initialize the application with configuration data"""
        cls._config = {
            "initialized": True,
            "app": {
                "name": data.get('website_name', 'Switch Game Repository'),
                "debug": True,
            },
            "database": {
                "host": data.get('db_host', 'localhost'),
                "port": int(data.get('db_port', 8529)),
                "username": data.get('db_username', 'root'),
                "password": data.get('db_password', ''),
                "database": data.get('db_name', 'switch_db'),
            },
            "security": {
                "secret_key": data.get('secret_key', os.urandom(32).hex())
            }
        }
        cls.save()
    
    # Accessor methods for common values
    @classmethod
    def APP_NAME(cls) -> str:
        return cls.get('app.name', 'Switch Game Repository')
    
    @classmethod
    def DEBUG(cls) -> bool:
        return cls.get('app.debug', True)
    
    @classmethod
    def ARANGODB_HOST(cls) -> str:
        return cls.get('database.host', 'localhost')
    
    @classmethod
    def ARANGODB_PORT(cls) -> int:
        return cls.get('database.port', 8529)
    
    @classmethod
    def ARANGODB_USERNAME(cls) -> str:
        return cls.get('database.username', 'root')
    
    @classmethod
    def ARANGODB_PASSWORD(cls) -> str:
        return cls.get('database.password', '')
    
    @classmethod
    def ARANGODB_DATABASE(cls) -> str:
        return cls.get('database.database', 'switch_db')
    
    @classmethod
    def SECRET_KEY(cls) -> str:
        return cls.get('security.secret_key', 'change-this-secret-key')
    
    @classmethod
    def get_arangodb_url(cls):
        """Get ArangoDB connection URL"""
        return f"http://{cls.ARANGODB_HOST()}:{cls.ARANGODB_PORT()}"

# Load config on module import
Config.load()
