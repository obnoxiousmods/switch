import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

try:
    from argon2 import PasswordHasher
    from argon2.exceptions import (
        InvalidHashError,
        VerificationError,
        VerifyMismatchError,
    )

    ARGON2_AVAILABLE = True
except ImportError:
    ARGON2_AVAILABLE = False


@dataclass
class User:
    """User model for authentication"""

    username: str
    password_hash: str
    is_admin: bool = False
    is_moderator: bool = False
    is_uploader: bool = False
    created_at: Optional[str] = None
    totp_secret: Optional[str] = None
    totp_enabled: bool = False
    _key: Optional[str] = None

    # Class-level password hasher for Argon2
    _ph = PasswordHasher() if ARGON2_AVAILABLE else None

    @staticmethod
    def hash_password_sha256(password: str) -> str:
        """Hash a password using SHA-256 (legacy method)"""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using Argon2 (preferred method) or SHA-256 as fallback"""
        if ARGON2_AVAILABLE and User._ph:
            return User._ph.hash(password)
        else:
            # Fallback to SHA-256 if Argon2 is not available
            return User.hash_password_sha256(password)

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against a hash, supporting both Argon2 and SHA-256"""
        # Try Argon2 first (new format)
        if ARGON2_AVAILABLE and User._ph and password_hash.startswith("$argon2"):
            try:
                User._ph.verify(password_hash, password)
                return True
            except (VerifyMismatchError, VerificationError, InvalidHashError):
                return False

        # Fall back to SHA-256 (legacy format)
        return User.hash_password_sha256(password) == password_hash

    @staticmethod
    def needs_rehash(password_hash: str) -> bool:
        """Check if a password hash needs to be upgraded to Argon2"""
        if not ARGON2_AVAILABLE or not User._ph:
            return False

        # If it's not an Argon2 hash, it needs rehashing
        if not password_hash.startswith("$argon2"):
            return True

        # If it's Argon2 but with outdated parameters, it needs rehashing
        try:
            return User._ph.check_needs_rehash(password_hash)
        except (InvalidHashError, Exception):
            return True

    def to_dict(self) -> dict:
        """Convert user to dictionary for database storage"""
        data = {
            "username": self.username,
            "password_hash": self.password_hash,
            "is_admin": self.is_admin,
            "is_moderator": self.is_moderator,
            "is_uploader": self.is_uploader,
            "created_at": self.created_at or datetime.utcnow().isoformat(),
            "totp_secret": self.totp_secret,
            "totp_enabled": self.totp_enabled,
        }
        if self._key:
            data["_key"] = self._key
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Create a User from dictionary"""
        return cls(
            username=data["username"],
            password_hash=data["password_hash"],
            is_admin=data.get("is_admin", False),
            is_moderator=data.get("is_moderator", False),
            is_uploader=data.get("is_uploader", False),
            created_at=data.get("created_at"),
            totp_secret=data.get("totp_secret"),
            totp_enabled=data.get("totp_enabled", False),
            _key=data.get("_key"),
        )
