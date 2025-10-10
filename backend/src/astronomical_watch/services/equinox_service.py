"""
Facade service for vernal equinox calculation with hybrid precision.
Coordinates internet fetch, analytic calculation, and approximation methods.
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
import traceback

from solar.equinox_precise import compute_vernal_equinox_precise, validate_equinox_solution
from net.equinox_fetch import fetch_equinox_datetime, is_fetch_configured
from offline.cache import (
    get_cached_equinox, set_cached_equinox, create_entry, 
    parse_cached_datetime, EquinoxEntry
)
from astronomical_watch import compute_vernal_equinox  # Legacy approximation

# Default precision ordering
DEFAULT_PREFER_ORDER = ("internet", "analytic", "approx")

# Uncertainty estimates (seconds)
UNCERTAINTY_INTERNET = 5.0      # Assume internet sources are quite accurate
UNCERTAINTY_ANALYTIC = 10.0     # Our analytic method uncertainty
UNCERTAINTY_APPROX = 10800.0    # 3 hours for legacy approximation

# Network timeout for internet fetch
INTERNET_FETCH_TIMEOUT = 10.0


def get_vernal_equinox(
    year: int, 
    prefer_order: Tuple[str, ...] = DEFAULT_PREFER_ORDER
) -> Dict[str, Any]:
    """
    Get vernal equinox using hybrid method with specified preference order.
    
    Args:
        year: Target year
        prefer_order: Tuple of method preferences ("internet", "analytic", "approx")
    
    Returns:
        Dictionary with:
        - utc: ISO 8601 UTC timestamp
        - precision: Method used ("internet", "analytic", or "approx")
        - uncertainty_s: Estimated uncertainty in seconds
        - source: Description of method/source used
        - cached: Whether result came from cache
        - retrieved_at: ISO timestamp when computed/fetched
    """
    # Check cache first
    cached_entry = get_cached_equinox(year)
    if cached_entry:
        try:
            dt = parse_cached_datetime(cached_entry)
            return {
                "utc": cached_entry.utc,
                "precision": cached_entry.precision,
                "uncertainty_s": cached_entry.uncertainty_s,
                "source": cached_entry.source,
                "cached": True,
                "retrieved_at": cached_entry.retrieved_at,
                "datetime": dt
            }
        except ValueError:
            # Cache entry is corrupted, continue with calculation
            pass
    
    # Try methods in preference order
    errors = []
    
    for method in prefer_order:
        try:
            if method == "internet":
                result = _try_internet_method(year)
                if result:
                    _cache_result(year, result)
                    result["cached"] = False
                    return result
                    
            elif method == "analytic":
                result = _try_analytic_method(year)
                if result:
                    _cache_result(year, result)
                    result["cached"] = False
                    return result
                    
            elif method == "approx":
                result = _try_approx_method(year)
                if result:
                    _cache_result(year, result)
                    result["cached"] = False
                    return result
            
        except Exception as e:
            errors.append(f"{method}: {str(e)}")
            continue
    
    # If all methods failed, raise exception with details
    error_msg = f"All methods failed for year {year}. Errors: " + "; ".join(errors)
    raise RuntimeError(error_msg)


def _try_internet_method(year: int) -> Optional[Dict[str, Any]]:
    """Try to get equinox from internet source."""
    if not is_fetch_configured():
        return None
    
    try:
        dt = fetch_equinox_datetime(year, timeout=INTERNET_FETCH_TIMEOUT)
        if dt is None:
            return None
        
        # Validate the result is reasonable
        if not validate_equinox_solution(dt, tolerance_deg=0.1):
            return None
        
        utc_iso = dt.isoformat().replace('+00:00', 'Z')
        retrieved_at = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        
        return {
            "utc": utc_iso,
            "precision": "internet",
            "uncertainty_s": UNCERTAINTY_INTERNET,
            "source": "remote_fetch",
            "retrieved_at": retrieved_at,
            "datetime": dt
        }
        
    except Exception:
        return None


def _try_analytic_method(year: int) -> Optional[Dict[str, Any]]:
    """Try to get equinox using analytic calculation."""
    try:
        dt = compute_vernal_equinox_precise(year, method="brent", tolerance_sec=2.0)
        
        # Validate the solution
        if not validate_equinox_solution(dt, tolerance_deg=0.01):
            return None
        
        utc_iso = dt.isoformat().replace('+00:00', 'Z')
        retrieved_at = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        
        return {
            "utc": utc_iso,
            "precision": "analytic",
            "uncertainty_s": UNCERTAINTY_ANALYTIC,
            "source": "meeus_root_finding",
            "retrieved_at": retrieved_at,
            "datetime": dt
        }
        
    except Exception:
        return None


def _try_approx_method(year: int) -> Optional[Dict[str, Any]]:
    """Try to get equinox using legacy approximation."""
    try:
        dt = compute_vernal_equinox(year)
        
        utc_iso = dt.isoformat().replace('+00:00', 'Z')
        retrieved_at = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        
        return {
            "utc": utc_iso,
            "precision": "approx",
            "uncertainty_s": UNCERTAINTY_APPROX,
            "source": "legacy_approximation",
            "retrieved_at": retrieved_at,
            "datetime": dt
        }
        
    except Exception:
        return None


def _cache_result(year: int, result: Dict[str, Any]) -> None:
    """Cache the equinox result."""
    try:
        entry = create_entry(
            dt=result["datetime"],
            precision=result["precision"],
            uncertainty_s=result["uncertainty_s"],
            source=result["source"]
        )
        set_cached_equinox(year, entry)
    except Exception:
        # Don't fail if caching fails
        pass


def get_vernal_equinox_datetime(
    year: int,
    prefer_order: Tuple[str, ...] = DEFAULT_PREFER_ORDER
) -> datetime:
    """
    Get vernal equinox datetime using hybrid method.
    
    Args:
        year: Target year
        prefer_order: Method preference order
    
    Returns:
        UTC datetime of vernal equinox
    
    Raises:
        RuntimeError: If all methods fail
    """
    result = get_vernal_equinox(year, prefer_order)
    return result["datetime"]


def clear_cache() -> None:
    """Clear the equinox cache."""
    from offline.cache import clear_cache as _clear_cache
    _clear_cache()


def get_service_status() -> Dict[str, Any]:
    """
    Get status information about the equinox service.
    
    Returns:
        Dictionary with service status and configuration
    """
    from offline.cache import get_cache_stats
    from net.equinox_fetch import get_fetch_status
    
    return {
        "available_methods": ["internet", "analytic", "approx"],
        "default_prefer_order": list(DEFAULT_PREFER_ORDER),
        "cache_status": get_cache_stats(),
        "internet_status": get_fetch_status(),
        "uncertainty_estimates": {
            "internet": UNCERTAINTY_INTERNET,
            "analytic": UNCERTAINTY_ANALYTIC,
            "approx": UNCERTAINTY_APPROX
        }
    }


def check_all_methods(year: int) -> Dict[str, Any]:
    """
    Check all available methods for a given year.
    
    Args:
        year: Target year
    
    Returns:
        Dictionary with results from all methods
    """
    results = {}
    
    # Test internet method
    try:
        internet_result = _try_internet_method(year)
        results["internet"] = {
            "success": internet_result is not None,
            "result": internet_result,
            "configured": is_fetch_configured()
        }
    except Exception as e:
        results["internet"] = {
            "success": False,
            "error": str(e),
            "configured": is_fetch_configured()
        }
    
    # Test analytic method
    try:
        analytic_result = _try_analytic_method(year)
        results["analytic"] = {
            "success": analytic_result is not None,
            "result": analytic_result
        }
    except Exception as e:
        results["analytic"] = {
            "success": False,
            "error": str(e)
        }
    
    # Test approx method
    try:
        approx_result = _try_approx_method(year)
        results["approx"] = {
            "success": approx_result is not None,
            "result": approx_result
        }
    except Exception as e:
        results["approx"] = {
            "success": False,
            "error": str(e)
        }
    
    return results


def compare_methods(year: int) -> Dict[str, Any]:
    """
    Compare results from different methods.
    
    Args:
        year: Target year
    
    Returns:
        Dictionary comparing all methods
    """
    results = check_all_methods(year)
    
    # Extract successful results
    successful_results = []
    for method, data in results.items():
        if data["success"] and data.get("result"):
            successful_results.append((method, data["result"]))
    
    if len(successful_results) < 2:
        return {
            "comparison": "insufficient_data",
            "successful_methods": len(successful_results),
            "results": results
        }
    
    # Compare timestamps
    comparisons = []
    for i, (method1, result1) in enumerate(successful_results):
        for method2, result2 in successful_results[i+1:]:
            try:
                dt1 = result1["datetime"]
                dt2 = result2["datetime"]
                diff_sec = abs((dt1 - dt2).total_seconds())
                
                comparisons.append({
                    "methods": f"{method1}_vs_{method2}",
                    "difference_seconds": diff_sec,
                    "difference_minutes": diff_sec / 60.0,
                    "within_analytic_tolerance": diff_sec <= 30.0
                })
            except Exception as e:
                comparisons.append({
                    "methods": f"{method1}_vs_{method2}",
                    "error": str(e)
                })
    
    return {
        "comparison": "success",
        "successful_methods": len(successful_results),
        "comparisons": comparisons,
        "results": results
              }
