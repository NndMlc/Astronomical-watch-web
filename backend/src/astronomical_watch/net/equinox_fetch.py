"""
Remote fetch for equinox data from external JSON API.
Provides optional retrieval from ASTRON_EQUINOX_URL environment variable.
"""
from __future__ import annotations
import json
import os
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from urllib.request import urlopen
from urllib.parse import urlparse
from urllib.error import URLError, HTTPError
import socket

# Default timeout for network requests
DEFAULT_TIMEOUT_SECONDS = 10.0
MARCH_DAY_MIN = 18
MARCH_DAY_MAX = 22


def get_equinox_fetch_url() -> Optional[str]:
    """
    Get the equinox fetch URL from environment variable.
    
    Returns:
        URL string if ASTRON_EQUINOX_URL is set, None otherwise
    """
    return os.environ.get("ASTRON_EQUINOX_URL")


def validate_equinox_timestamp(timestamp_iso: str, year: int) -> bool:
    """
    Validate that an ISO timestamp is reasonable for a vernal equinox.
    
    Args:
        timestamp_iso: ISO 8601 timestamp string
        year: Expected year
    
    Returns:
        True if timestamp appears valid for vernal equinox
    """
    try:
        # Parse the timestamp
        if timestamp_iso.endswith('Z'):
            dt = datetime.fromisoformat(timestamp_iso.replace('Z', '+00:00'))
        else:
            dt = datetime.fromisoformat(timestamp_iso)
        
        # Convert to UTC if needed
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        
        # Check year
        if dt.year != year:
            return False
        
        # Check month (should be March)
        if dt.month != 3:
            return False
        
        # Check day (should be around March 18-22)
        if not (MARCH_DAY_MIN <= dt.day <= MARCH_DAY_MAX):
            return False
        
        return True
        
    except (ValueError, OverflowError):
        return False


def parse_equinox_json(json_text: str, year: int) -> Optional[str]:
    """
    Parse JSON response and extract equinox timestamp for given year.
    
    Expected JSON format:
    {
        "2024": "2024-03-20T03:06:14Z",
        "2025": "2025-03-20T09:01:28Z",
        ...
    }
    
    Args:
        json_text: JSON response text
        year: Target year
    
    Returns:
        ISO timestamp string if found and valid, None otherwise
    """
    try:
        data = json.loads(json_text)
        
        if not isinstance(data, dict):
            return None
        
        # Try both string and integer keys
        year_str = str(year)
        timestamp = None
        
        if year_str in data:
            timestamp = data[year_str]
        elif year in data:
            timestamp = data[year]
        
        if timestamp is None:
            return None
        
        if not isinstance(timestamp, str):
            return None
        
        # Validate the timestamp
        if validate_equinox_timestamp(timestamp, year):
            return timestamp
        
        return None
        
    except (json.JSONDecodeError, KeyError, TypeError):
        return None


def fetch_equinox_from_url(
    url: str, 
    year: int, 
    timeout: float = DEFAULT_TIMEOUT_SECONDS
) -> Optional[str]:
    """
    Fetch equinox timestamp from remote URL.
    
    Args:
        url: URL to fetch from
        year: Target year
        timeout: Request timeout in seconds
    
    Returns:
        ISO timestamp string if successful, None on any failure
    """
    try:
        # Basic URL validation
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return None
        
        # Make the request
        with urlopen(url, timeout=timeout) as response:
            if response.status != 200:
                return None
            
            content_type = response.headers.get('content-type', '').lower()
            if 'application/json' not in content_type and 'text/json' not in content_type:
                # Still try to parse as JSON - some servers don't set proper content-type
                pass
            
            json_text = response.read().decode('utf-8')
            return parse_equinox_json(json_text, year)
            
    except (URLError, HTTPError, socket.timeout, UnicodeDecodeError):
        return None
    except Exception:
        # Catch any other unexpected errors
        return None


def fetch_equinox_remote(year: int, timeout: float = DEFAULT_TIMEOUT_SECONDS) -> Optional[str]:
    """
    Fetch equinox timestamp from configured remote source.
    
    Args:
        year: Target year
        timeout: Request timeout in seconds
    
    Returns:
        ISO timestamp string if successful, None if unavailable or failed
    """
    url = get_equinox_fetch_url()
    if not url:
        return None
    
    return fetch_equinox_from_url(url, year, timeout)


def parse_remote_timestamp(timestamp_iso: str) -> datetime:
    """
    Parse ISO timestamp from remote source to datetime object.
    
    Args:
        timestamp_iso: ISO 8601 timestamp string
    
    Returns:
        UTC datetime object
    
    Raises:
        ValueError: If timestamp cannot be parsed
    """
    if timestamp_iso.endswith('Z'):
        dt = datetime.fromisoformat(timestamp_iso.replace('Z', '+00:00'))
    else:
        dt = datetime.fromisoformat(timestamp_iso)
    
    # Ensure UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    
    return dt


def fetch_equinox_datetime(year: int, timeout: float = DEFAULT_TIMEOUT_SECONDS) -> Optional[datetime]:
    """
    Fetch and parse equinox datetime from remote source.
    
    Args:
        year: Target year
        timeout: Request timeout in seconds
    
    Returns:
        UTC datetime if successful, None otherwise
    """
    timestamp_iso = fetch_equinox_remote(year, timeout)
    if not timestamp_iso:
        return None
    
    try:
        return parse_remote_timestamp(timestamp_iso)
    except ValueError:
        return None


# For testing/debugging
def is_fetch_configured() -> bool:
    """Check if remote fetch is configured."""
    return get_equinox_fetch_url() is not None


def get_fetch_status() -> Dict[str, Any]:
    """
    Get status information about fetch configuration.
    
    Returns:
        Dictionary with configuration and status info
    """
    url = get_equinox_fetch_url()
    return {
        "configured": url is not None,
        "url": url,
        "env_var": "ASTRON_EQUINOX_URL"
  }
