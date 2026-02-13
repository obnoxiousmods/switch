from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import secrets
import hashlib


@dataclass
class ApiKey:
    """API Key model for API authentication"""
    user_id: str
    key_name: str
    key_hash: str
    created_at: Optional[str] = None
    last_used_at: Optional[str] = None
    is_active: bool = True
    _key: Optional[str] = None
    
    @staticmethod
    def generate_key() -> str:
        """Generate a new random API key"""
        # Generate 32 bytes (256 bits) of random data
        # This will be shown once to the user
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def hash_key(key: str) -> str:
        """Hash an API key using SHA-256"""
        return hashlib.sha256(key.encode('utf-8')).hexdigest()
    
    @staticmethod
    def verify_key(key: str, key_hash: str) -> bool:
        """Verify an API key against a hash"""
        return ApiKey.hash_key(key) == key_hash
    
    def to_dict(self) -> dict:
        """Convert API key to dictionary for database storage"""
        data = {
            'user_id': self.user_id,
            'key_name': self.key_name,
            'key_hash': self.key_hash,
            'created_at': self.created_at or datetime.utcnow().isoformat(),
            'last_used_at': self.last_used_at,
            'is_active': self.is_active
        }
        if self._key:
            data['_key'] = self._key
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ApiKey':
        """Create an ApiKey from dictionary"""
        return cls(
            user_id=data['user_id'],
            key_name=data['key_name'],
            key_hash=data['key_hash'],
            created_at=data.get('created_at'),
            last_used_at=data.get('last_used_at'),
            is_active=data.get('is_active', True),
            _key=data.get('_key')
        )
