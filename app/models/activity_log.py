from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class ActivityLog:
    """Activity log model for normal site operations"""
    event_type: str  # e.g., "download", "login", "registration", "file_scan", "directory_scan"
    user_id: Optional[str] = None  # User ID (if applicable)
    username: Optional[str] = None  # Username (if applicable)
    details: Optional[dict] = None  # Event-specific details
    ip_address: Optional[str] = None  # IP address
    timestamp: Optional[str] = None
    _key: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert activity log to dictionary for database storage"""
        data = {
            'event_type': self.event_type,
            'user_id': self.user_id,
            'username': self.username,
            'details': self.details or {},
            'ip_address': self.ip_address,
            'timestamp': self.timestamp or datetime.utcnow().isoformat()
        }
        if self._key:
            data['_key'] = self._key
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ActivityLog':
        """Create an ActivityLog from dictionary"""
        return cls(
            event_type=data['event_type'],
            user_id=data.get('user_id'),
            username=data.get('username'),
            details=data.get('details', {}),
            ip_address=data.get('ip_address'),
            timestamp=data.get('timestamp'),
            _key=data.get('_key')
        )
