from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class AuditLog:
    """Audit log model for security-related events"""
    action: str  # e.g., "password_changed", "role_granted", "role_revoked", "api_key_revoked"
    actor_id: str  # User ID who performed the action
    actor_username: str  # Username of actor
    target_id: Optional[str] = None  # User ID affected by the action (if applicable)
    target_username: Optional[str] = None  # Username affected by the action
    details: Optional[dict] = None  # Additional details about the action
    ip_address: Optional[str] = None  # IP address of the actor
    timestamp: Optional[str] = None
    _key: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert audit log to dictionary for database storage"""
        data = {
            'action': self.action,
            'actor_id': self.actor_id,
            'actor_username': self.actor_username,
            'target_id': self.target_id,
            'target_username': self.target_username,
            'details': self.details or {},
            'ip_address': self.ip_address,
            'timestamp': self.timestamp or datetime.utcnow().isoformat()
        }
        if self._key:
            data['_key'] = self._key
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AuditLog':
        """Create an AuditLog from dictionary"""
        return cls(
            action=data['action'],
            actor_id=data['actor_id'],
            actor_username=data['actor_username'],
            target_id=data.get('target_id'),
            target_username=data.get('target_username'),
            details=data.get('details', {}),
            ip_address=data.get('ip_address'),
            timestamp=data.get('timestamp'),
            _key=data.get('_key')
        )
