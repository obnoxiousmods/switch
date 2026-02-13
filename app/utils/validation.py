"""
Input validation utilities for user-provided data.
"""
import re
from typing import Optional


# Username validation regex: 3-32 chars, alphanumeric, dash, underscore
USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9_-]{3,32}$')

# Password minimum length
PASSWORD_MIN_LENGTH = 6
PASSWORD_MAX_LENGTH = 128  # Reasonable max to prevent DoS


def validate_username(username: str) -> tuple[bool, Optional[str]]:
    """
    Validate a username for registration/login.
    
    Args:
        username: Username to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not username:
        return False, "Username is required"
    
    if not USERNAME_REGEX.match(username):
        return False, "Username must be 3-32 characters, alphanumeric, dash, or underscore only"
    
    return True, None


def validate_password(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate a password for registration.
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {PASSWORD_MIN_LENGTH} characters"
    
    if len(password) > PASSWORD_MAX_LENGTH:
        return False, f"Password must be no more than {PASSWORD_MAX_LENGTH} characters"
    
    return True, None


def validate_file_extension(filename: str, allowed_extensions: list[str]) -> tuple[bool, Optional[str]]:
    """
    Validate a file has an allowed extension.
    
    Args:
        filename: Filename to check
        allowed_extensions: List of allowed extensions (without dots, e.g., ['nsp', 'nsz'])
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    import os
    
    if not filename:
        return False, "Filename is required"
    
    name, ext = os.path.splitext(filename)
    if not ext:
        return False, "File must have an extension"
    
    # Remove leading dot and normalize to lowercase
    ext_normalized = ext.lstrip('.').lower()
    
    if ext_normalized not in [e.lower() for e in allowed_extensions]:
        return False, f"Invalid file type. Allowed: {', '.join(allowed_extensions).upper()}"
    
    return True, None


def sanitize_filename(filename: str, max_length: int = 200) -> Optional[str]:
    """
    Sanitize a filename to make it safe for filesystem use.
    Removes path separators and dangerous characters.
    
    Args:
        filename: Original filename
        max_length: Maximum allowed length for the base name
        
    Returns:
        Sanitized filename or None if invalid
    """
    import os
    import re
    
    if not filename:
        return None
    
    # Get base name and extension
    name, ext = os.path.splitext(filename)
    
    # Remove path separators and dangerous characters from base name
    safe_name = re.sub(r'[/\\:\*\?"<>|]', '', name)
    safe_name = safe_name.strip('. ')  # Remove leading/trailing dots and spaces
    
    if not safe_name or len(safe_name) > max_length:
        return None
    
    # Reconstruct with safe extension (also sanitized)
    safe_ext = re.sub(r'[/\\:\*\?"<>|]', '', ext)
    
    return f"{safe_name}{safe_ext}"
