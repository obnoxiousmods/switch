from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import hashlib
import secrets


@dataclass
class User:
    """User model for authentication"""
    username: str
    password_hash: str
    is_admin: bool = False
    is_moderator: bool = False
    created_at: Optional[str] = None
    _key: Optional[str] = None
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against a hash"""
        return User.hash_password(password) == password_hash
    
    def to_dict(self) -> dict:
        """Convert user to dictionary for database storage"""
        data = {
            'username': self.username,
            'password_hash': self.password_hash,
            'is_admin': self.is_admin,
            'is_moderator': self.is_moderator,
            'created_at': self.created_at or datetime.utcnow().isoformat()
        }
        if self._key:
            data['_key'] = self._key
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Create a User from dictionary"""
        return cls(
            username=data['username'],
            password_hash=data['password_hash'],
            is_admin=data.get('is_admin', False),
            is_moderator=data.get('is_moderator', False),
            created_at=data.get('created_at'),
            _key=data.get('_key')
        )
