"""
Utility functions for extracting IP addresses from requests.
Handles Cloudflare and proxy headers.
"""

from typing import Optional, Dict
from starlette.requests import Request


def get_client_ip(request: Request) -> str:
    """
    Get the direct client IP address from the request.
    This is the IP that directly connected to the server.

    Args:
        request: Starlette Request object

    Returns:
        Client IP address or 'unknown' if not available
    """
    return request.client.host if request.client else "unknown"


def get_cloudflare_ip(request: Request) -> Optional[str]:
    """
    Get the original client IP from Cloudflare headers.
    Checks CF-Connecting-IP header first (most reliable for Cloudflare),
    then falls back to X-Forwarded-For (standard proxy header).

    Args:
        request: Starlette Request object

    Returns:
        Cloudflare/proxy IP address or None if not behind proxy
    """
    # CF-Connecting-IP is set by Cloudflare and contains the original client IP
    cf_ip = request.headers.get("CF-Connecting-IP")
    if cf_ip:
        return cf_ip.strip()

    # X-Forwarded-For can contain multiple IPs (client, proxy1, proxy2, ...)
    # The first IP is typically the original client
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take the first IP in the chain
        return forwarded_for.split(",")[0].strip()

    return None


def get_real_ip(request: Request) -> str:
    """
    Get the real client IP address, preferring Cloudflare/proxy headers
    over the direct connection IP when available.

    Args:
        request: Starlette Request object

    Returns:
        Most accurate client IP address available
    """
    # Try to get IP from Cloudflare/proxy headers first
    cf_ip = get_cloudflare_ip(request)
    if cf_ip:
        return cf_ip

    # Fall back to direct client IP
    return get_client_ip(request)


def get_ip_info(request: Request) -> Dict[str, str]:
    """
    Get comprehensive IP information for logging purposes.
    Returns both the direct connection IP and the Cloudflare/proxy IP if available.

    Args:
        request: Starlette Request object

    Returns:
        Dictionary with 'ip_address' (real IP) and 'client_ip' (direct connection)
        Also includes 'forwarded_ip' if behind proxy
    """
    client_ip = get_client_ip(request)
    cf_ip = get_cloudflare_ip(request)

    result = {
        "ip_address": cf_ip if cf_ip else client_ip,  # Real/best IP
        "client_ip": client_ip,  # Direct connection IP
    }

    # Add forwarded IP separately if it exists and differs from client IP
    if cf_ip and cf_ip != client_ip:
        result["forwarded_ip"] = cf_ip

    return result


def format_ip_for_log(request: Request) -> str:
    """
    Format IP information as a human-readable string for logging.
    Shows both IPs when behind a proxy/Cloudflare.

    Args:
        request: Starlette Request object

    Returns:
        Formatted string like "1.2.3.4" or "1.2.3.4 (via 5.6.7.8)"
    """
    client_ip = get_client_ip(request)
    cf_ip = get_cloudflare_ip(request)

    if cf_ip and cf_ip != client_ip:
        return f"{cf_ip} (via {client_ip})"

    return client_ip
