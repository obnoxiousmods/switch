from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class VoteType(str, Enum):
    """Vote type enum"""

    LIKE = "like"
    DISLIKE = "dislike"


class Like:
    """Like model representing a user's like/dislike on an entry"""

    def __init__(
        self,
        entry_id: str,
        user_id: str,
        vote_type: VoteType,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
    ):
        self.entry_id = entry_id
        self.user_id = user_id
        self.vote_type = vote_type
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = updated_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert like to dictionary for database storage"""
        data = {
            "entry_id": self.entry_id,
            "user_id": self.user_id,
            "vote_type": self.vote_type.value
            if isinstance(self.vote_type, VoteType)
            else self.vote_type,
            "created_at": self.created_at,
        }
        if self.updated_at:
            data["updated_at"] = self.updated_at
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Like":
        """Create like from dictionary"""
        return cls(
            entry_id=data.get("entry_id", ""),
            user_id=data.get("user_id", ""),
            vote_type=VoteType(data.get("vote_type", "like")),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
