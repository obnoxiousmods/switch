import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration"""
    
    # ArangoDB settings
    ARANGODB_HOST = os.getenv("ARANGODB_HOST", "localhost")
    ARANGODB_PORT = int(os.getenv("ARANGODB_PORT", "8529"))
    ARANGODB_USERNAME = os.getenv("ARANGODB_USERNAME", "root")
    ARANGODB_PASSWORD = os.getenv("ARANGODB_PASSWORD", "password")
    ARANGODB_DATABASE = os.getenv("ARANGODB_DATABASE", "switch_db")
    
    # Application settings
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-to-a-very-long-random-secret-2026!")
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    
    @classmethod
    def get_arangodb_url(cls):
        """Get ArangoDB connection URL"""
        return f"http://{cls.ARANGODB_HOST}:{cls.ARANGODB_PORT}"
