from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class EntryType(str, Enum):
    """Entry type enum"""

    FILEPATH = "filepath"
    URL = "url"


class FileType(str, Enum):
    """File type enum"""

    NSP = "nsp"
    NSZ = "nsz"
    XCI = "xci"


class Entry:
    """Entry model representing a game file entry"""

    def __init__(
        self,
        name: str,
        source: str,
        type: EntryType,
        file_type: FileType,
        size: int,
        created_by: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[str] = None,
        file_created_at: Optional[str] = None,
        file_modified_at: Optional[str] = None,
        corrupt: bool = False,
        md5_hash: Optional[str] = None,
        sha256_hash: Optional[str] = None,
    ):
        self.name = name
        self.source = source
        self.type = type
        self.file_type = file_type
        self.size = size
        self.created_by = created_by
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.file_created_at = file_created_at
        self.file_modified_at = file_modified_at
        self.corrupt = corrupt
        self.md5_hash = md5_hash
        self.sha256_hash = sha256_hash

    def to_dict(self) -> Dict[str, Any]:
        """Convert entry to dictionary for database storage"""
        data = {
            "name": self.name,
            "source": self.source,
            "type": self.type.value if isinstance(self.type, EntryType) else self.type,
            "file_type": self.file_type.value
            if isinstance(self.file_type, FileType)
            else self.file_type,
            "size": self.size,
            "created_by": self.created_by,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "corrupt": self.corrupt,
        }
        if self.file_created_at:
            data["file_created_at"] = self.file_created_at
        if self.file_modified_at:
            data["file_modified_at"] = self.file_modified_at
        if self.md5_hash:
            data["md5_hash"] = self.md5_hash
        if self.sha256_hash:
            data["sha256_hash"] = self.sha256_hash
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Entry":
        """Create entry from dictionary"""
        return cls(
            name=data.get("name", ""),
            source=data.get("source", ""),
            type=EntryType(data.get("type", "filepath")),
            file_type=FileType(data.get("file_type", "nsp")),
            size=data.get("size", 0),
            created_by=data.get("created_by", ""),
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at"),
            file_created_at=data.get("file_created_at"),
            file_modified_at=data.get("file_modified_at"),
            corrupt=data.get("corrupt", False),
            md5_hash=data.get("md5_hash"),
            sha256_hash=data.get("sha256_hash"),
        )
