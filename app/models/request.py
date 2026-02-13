from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from enum import Enum


class RequestStatus(str, Enum):
    """Request status enum"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class RequestType(str, Enum):
    """Request type enum"""
    UPLOAD_ACCESS = "upload_access"
    MODERATOR_ACCESS = "moderator_access"
    GAME_REQUEST = "game_request"
    OTHER = "other"


@dataclass
class Request:
    """Request model for user requests"""
    user_id: str
    username: str
    request_type: RequestType
    message: str
    status: RequestStatus = RequestStatus.PENDING
    created_at: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[str] = None
    game_name: Optional[str] = None
    _key: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert request to dictionary for database storage"""
        data = {
            'user_id': self.user_id,
            'username': self.username,
            'request_type': self.request_type.value if isinstance(self.request_type, RequestType) else self.request_type,
            'message': self.message,
            'status': self.status.value if isinstance(self.status, RequestStatus) else self.status,
            'created_at': self.created_at or datetime.utcnow().isoformat(),
            'reviewed_by': self.reviewed_by,
            'reviewed_at': self.reviewed_at,
            'game_name': self.game_name
        }
        if self._key:
            data['_key'] = self._key
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Request':
        """Create a Request from dictionary"""
        return cls(
            user_id=data['user_id'],
            username=data['username'],
            request_type=RequestType(data.get('request_type', 'other')),
            message=data['message'],
            status=RequestStatus(data.get('status', 'pending')),
            created_at=data.get('created_at'),
            reviewed_by=data.get('reviewed_by'),
            reviewed_at=data.get('reviewed_at'),
            game_name=data.get('game_name'),
            _key=data.get('_key')
        )
