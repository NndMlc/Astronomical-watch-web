"""
Cache system for equinox data with schema version 2.
Supports migration from schema v1 (legacy approx) to v2 (structured data).
"""
from __future__ import annotations
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict
import threading

# Cache schema versions
CURRENT_SCHEMA_VERSION = 2
LEGACY_SCHEMA_VERSION = 1

# Default cache location
DEFAULT_CACHE_DIR = Path.home() / ".astronomical_watch"
DEFAULT_CACHE_FILE = "equinox_cache.json"

# Thread lock for cache operations
_cache_lock = threading.Lock()


@dataclass
class EquinoxEntry:
    """Schema v2 equinox cache entry."""
    utc: str                    # ISO 8601 UTC timestamp
    precision: str              # "internet", "analytic", or "approx"  
    uncertainty_s: float        # Uncertainty in seconds
    source: str                 # Description of calculation method/source
    retrieved_at: str           # ISO 8601 timestamp when computed/fetched
    legacy_approx: Optional[str] = None  # Original approx value if migrated


def get_cache_file_path() -> Path:
    """Get the path to the cache file."""
    cache_dir = Path(os.environ.get("ASTRON_CACHE_DIR", DEFAULT_CACHE_DIR))
    return cache_dir / DEFAULT_CACHE_FILE


def ensure_cache_dir() -> None:
    """Ensure cache directory exists."""
    cache_file = get_cache_file_path()
    cache_file.parent.mkdir(parents=True, exist_ok=True)


def load_cache() -> Dict[str, Any]:
    """
    Load cache from disk.
    
    Returns:
        Cache dictionary (empty if file doesn't exist or is invalid)
    """
    cache_file = get_cache_file_path()
    
    if not cache_file.exists():
        return {"schema": CURRENT_SCHEMA_VERSION, "entries": {}}
    
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate basic structure
        if not isinstance(data, dict):
            return {"schema": CURRENT_SCHEMA_VERSION, "entries": {}}
        
        return data
        
    except (json.JSONDecodeError, IOError):
        return {"schema": CURRENT_SCHEMA_VERSION, "entries": {}}


def save_cache(cache_data: Dict[str, Any]) -> None:
    """
    Save cache to disk.
    
    Args:
        cache_data: Cache dictionary to save
    """
    ensure_cache_dir()
    cache_file = get_cache_file_path()
    
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
    except IOError:
        # Silently fail on write errors
        pass


def migrate_legacy_entry(year: int, legacy_timestamp: str) -> EquinoxEntry:
    """
    Migrate a legacy schema v1 entry to schema v2.
    
    Args:
        year: Year for the entry
        legacy_timestamp: Original timestamp string
    
    Returns:
        New EquinoxEntry with legacy data preserved
    """
    now_iso = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    
    return EquinoxEntry(
        utc=legacy_timestamp,
        precision="approx",
        uncertainty_s=10800.0,  # 3 hours uncertainty for legacy approx
        source="legacy_approximation",
        retrieved_at=now_iso,
        legacy_approx=legacy_timestamp
    )


def migrate_cache_if_needed(cache_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Migrate cache from schema v1 to v2 if needed.
    
    Args:
        cache_data: Cache dictionary (possibly v1)
    
    Returns:
        Migrated cache dictionary (v2)
    """
    schema_version = cache_data.get("schema", LEGACY_SCHEMA_VERSION)
    
    if schema_version == CURRENT_SCHEMA_VERSION:
        return cache_data
    
    if schema_version == LEGACY_SCHEMA_VERSION:
        # Migrate from v1 to v2
        new_cache = {
            "schema": CURRENT_SCHEMA_VERSION,
            "entries": {}
        }
        
        # Convert old entries
        old_entries = cache_data.get("entries", {})
        if isinstance(old_entries, dict):
            for year_str, timestamp in old_entries.items():
                if isinstance(timestamp, str) and year_str.isdigit():
                    year = int(year_str)
                    entry = migrate_legacy_entry(year, timestamp)
                    new_cache["entries"][year_str] = asdict(entry)
        
        return new_cache
    
    # Unknown schema version - reset cache
    return {"schema": CURRENT_SCHEMA_VERSION, "entries": {}}


def get_cached_equinox(year: int) -> Optional[EquinoxEntry]:
    """
    Get cached equinox entry for given year.
    
    Args:
        year: Target year
    
    Returns:
        EquinoxEntry if found, None otherwise
    """
    with _cache_lock:
        cache_data = load_cache()
        cache_data = migrate_cache_if_needed(cache_data)
        
        # Save migrated cache if it was changed
        if cache_data.get("schema") == CURRENT_SCHEMA_VERSION:
            save_cache(cache_data)
        
        entries = cache_data.get("entries", {})
        year_str = str(year)
        
        if year_str not in entries:
            return None
        
        entry_dict = entries[year_str]
        if not isinstance(entry_dict, dict):
            return None
        
        try:
            return EquinoxEntry(**entry_dict)
        except (TypeError, ValueError):
            return None


def set_cached_equinox(year: int, entry: EquinoxEntry) -> None:
    """
    Store equinox entry in cache.
    
    Args:
        year: Target year
        entry: EquinoxEntry to store
    """
    with _cache_lock:
        cache_data = load_cache()
        cache_data = migrate_cache_if_needed(cache_data)
        
        # Ensure entries dict exists
        if "entries" not in cache_data:
            cache_data["entries"] = {}
        
        # Store the entry
        year_str = str(year)
        cache_data["entries"][year_str] = asdict(entry)
        
        # Save to disk
        save_cache(cache_data)


def clear_cache() -> None:
    """Clear all cached entries."""
    with _cache_lock:
        cache_data = {"schema": CURRENT_SCHEMA_VERSION, "entries": {}}
        save_cache(cache_data)


def get_cache_stats() -> Dict[str, Any]:
    """
    Get statistics about the cache.
    
    Returns:
        Dictionary with cache statistics
    """
    with _cache_lock:
        cache_data = load_cache()
        cache_data = migrate_cache_if_needed(cache_data)
        
        entries = cache_data.get("entries", {})
        
        # Count entries by precision
        precision_counts = {}
        migrated_count = 0
        
        for entry_dict in entries.values():
            if isinstance(entry_dict, dict):
                precision = entry_dict.get("precision", "unknown")
                precision_counts[precision] = precision_counts.get(precision, 0) + 1
                
                if entry_dict.get("legacy_approx"):
                    migrated_count += 1
        
        return {
            "schema_version": cache_data.get("schema", "unknown"),
            "total_entries": len(entries),
            "precision_counts": precision_counts,
            "migrated_entries": migrated_count,
            "cache_file": str(get_cache_file_path())
        }


def is_cache_available() -> bool:
    """Check if cache is available and readable."""
    try:
        cache_data = load_cache()
        return isinstance(cache_data, dict)
    except Exception:
        return False


def create_entry(
    dt: datetime,
    precision: str,
    uncertainty_s: float,
    source: str,
    legacy_approx: Optional[str] = None
) -> EquinoxEntry:
    """
    Create a new EquinoxEntry.
    
    Args:
        dt: Equinox datetime (will be converted to UTC)
        precision: "internet", "analytic", or "approx"
        uncertainty_s: Uncertainty in seconds
        source: Description of method/source
        legacy_approx: Legacy approximation value if migrating
    
    Returns:
        New EquinoxEntry
    """
    # Ensure UTC and format as ISO with Z suffix
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    
    utc_iso = dt.isoformat().replace('+00:00', 'Z')
    retrieved_at_iso = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    
    return EquinoxEntry(
        utc=utc_iso,
        precision=precision,
        uncertainty_s=uncertainty_s,
        source=source,
        retrieved_at=retrieved_at_iso,
        legacy_approx=legacy_approx
    )


def parse_cached_datetime(entry: EquinoxEntry) -> datetime:
    """
    Parse datetime from cache entry.
    
    Args:
        entry: EquinoxEntry
    
    Returns:
        UTC datetime
    
    Raises:
        ValueError: If timestamp cannot be parsed
    """
    timestamp = entry.utc
    if timestamp.endswith('Z'):
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    else:
        dt = datetime.fromisoformat(timestamp)
    
    # Ensure UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    
    return dt
