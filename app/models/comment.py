from datetime import datetime
from typing import Any, Dict, Optional


class Comment:
    """Comment model representing a user comment on an entry"""

    def __init__(
        self,
        entry_id: str,
        user_id: str,
        username: str,
        text: str,
        parent_comment_id: Optional[str] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
    ):
        self.entry_id = entry_id
        self.user_id = user_id
        self.username = username
        self.text = text
        self.parent_comment_id = parent_comment_id
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = updated_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert comment to dictionary for database storage"""
        data = {
            "entry_id": self.entry_id,
            "user_id": self.user_id,
            "username": self.username,
            "text": self.text,
            "created_at": self.created_at,
        }
        if self.parent_comment_id:
            data["parent_comment_id"] = self.parent_comment_id
        if self.updated_at:
            data["updated_at"] = self.updated_at
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Comment":
        """Create comment from dictionary"""
        return cls(
            entry_id=data.get("entry_id", ""),
            user_id=data.get("user_id", ""),
            username=data.get("username", ""),
            text=data.get("text", ""),
            parent_comment_id=data.get("parent_comment_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
