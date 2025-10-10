"""
VSOP87 Earth model with dynamic coefficient loading.
Supports both static truncated coefficients and on-demand loading of higher precision
coefficients based on accuracy requirements.

For full accuracy, use the scripts/generate_vsop87.py to create coefficient files.
All values in radians (L, B) and AU (R).
"""
import math
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any

# Default truncated series (for demonstration and baseline operation)
L0 = [
    (175347046.0, 0, 0),
    (3341656.0, 4.6692568, 6283.07585),
    (34894.0, 4.6261, 12566.1517),   
    (3497.0, 2.7441, 5753.3849),
    (3418.0, 2.8289, 3.5231),
]
L1 = [
    (628331966747.0, 0, 0),
    (206059.0, 2.678235, 6283.07585),
]
L2, L3, L4, L5 = [], [], [], []
B0 = [
    (280.0, 3.199, 84334.662),
    (102.0, 5.422, 5507.553),
]
B1, B2, B3, B4, B5 = [], [], [], [], []
R0 = [
    (100013989.0, 0, 0),
    (1670700.0, 3.0984635, 6283.07585),
    (13956.0, 3.05525, 12566.1517),
]
R1 = [
    (103019.0, 1.107490, 6283.07585),
    (1721.0, 1.0644, 12566.1517),
]
R2, R3, R4, R5 = [], [], [], []

# Cache for dynamically loaded coefficient sets
_coefficient_cache: Dict[str, Any] = {}
_default_coefficients: Optional[Dict[str, List[Tuple[float, float, float]]]] = None

def _get_script_dir() -> Path:
    """Get the scripts directory path."""
    current_dir = Path(__file__).parent
    return current_dir.parent / "scripts"

def _find_coefficient_file(max_error_arcsec: float) -> Optional[Path]:
    """
    Find the most suitable coefficient file for the given error tolerance.
    
    Args:
        max_error_arcsec: Maximum acceptable error in arcseconds
        
    Returns:
        Path to coefficient file or None if none suitable found
    """
    script_dir = _get_script_dir()
    coeff_dir = script_dir / "vsop87_coefficients"
    
    if not coeff_dir.exists():
        return None
    
    # Look for generated coefficient files
    best_file = None
    best_error = float('inf')
    
    for file_path in coeff_dir.glob("vsop87d_earth_*.py"):
        # Try to extract error information from the file
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Look for error bound comment
            for line in content.split('\n'):
                if 'Conservative error bound' in line and 'arcseconds' in line:
                    # Extract error value
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if 'arcseconds' in part and i > 0:
                            try:
                                error = float(parts[i-1])
                                if error <= max_error_arcsec and error < best_error:
                                    best_error = error
                                    best_file = file_path
                                break
                            except ValueError:
                                continue
                    break
        except Exception:
            continue
    
    return best_file

def _load_coefficient_file(file_path: Path) -> Dict[str, Any]:
    """
    Load coefficients from a generated Python file.
    
    Args:
        file_path: Path to the coefficient file
        
    Returns:
        Dictionary containing the loaded coefficients
    """
    cache_key = str(file_path)
    if cache_key in _coefficient_cache:
        return _coefficient_cache[cache_key]
    
    # Import the module dynamically
    import importlib.util
    import sys
    
    spec = importlib.util.spec_from_file_location("vsop87_coeffs", file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load coefficient file: {file_path}")
    
    module = importlib.util.module_from_spec(spec)
    sys.modules["vsop87_coeffs"] = module
    spec.loader.exec_module(module)
    
    # Extract coefficient arrays
    coeffs = {}
    for coord in ['L', 'B', 'R']:
        for power in range(6):
            series_name = f"{coord}{power}"
            if hasattr(module, series_name):
                coeffs[series_name] = getattr(module, series_name)
            else:
                coeffs[series_name] = []
    
    # Cache the loaded coefficients
    _coefficient_cache[cache_key] = coeffs
    return coeffs

def _get_coefficients(max_error_arcsec: Optional[float] = None) -> Dict[str, List[Tuple[float, float, float]]]:
    """
    Get appropriate coefficients based on error tolerance.
    
    Args:
        max_error_arcsec: Maximum acceptable error in arcseconds.
                         If None, uses default built-in coefficients.
        
    Returns:
        Dictionary of coefficient arrays
    """
    global _default_coefficients
    
    if max_error_arcsec is None:
        # Use built-in default coefficients (cached)
        if _default_coefficients is None:
            _default_coefficients = {
                'L0': L0, 'L1': L1, 'L2': L2, 'L3': L3, 'L4': L4, 'L5': L5,
                'B0': B0, 'B1': B1, 'B2': B2, 'B3': B3, 'B4': B4, 'B5': B5,
                'R0': R0, 'R1': R1, 'R2': R2, 'R3': R3, 'R4': R4, 'R5': R5,
            }
        return _default_coefficients
    
    # Try to find and load appropriate coefficient file
    coeff_file = _find_coefficient_file(max_error_arcsec)
    if coeff_file is not None:
        try:
            return _load_coefficient_file(coeff_file)
        except Exception as e:
            # Fall back to default coefficients if loading fails
            print(f"Warning: Failed to load coefficient file {coeff_file}: {e}")
    
    # Fall back to default coefficients
    if _default_coefficients is None:
        _default_coefficients = {
            'L0': L0, 'L1': L1, 'L2': L2, 'L3': L3, 'L4': L4, 'L5': L5,
            'B0': B0, 'B1': B1, 'B2': B2, 'B3': B3, 'B4': B4, 'B5': B5,
            'R0': R0, 'R1': R1, 'R2': R2, 'R3': R3, 'R4': R4, 'R5': R5,
        }
    return _default_coefficients

def _sum(terms, t):
    """Sum a series of periodic terms."""
    return sum(A * math.cos(B + C * t) for A, B, C in terms)

def _eval(series, t):
    """Evaluate a VSOP87 series at time t."""
    return sum(_sum(group, t) * t**n for n, group in enumerate(series))

def _t(jd):
    """Convert Julian Day to VSOP87 time parameter (millennia since J2000.0)."""
    return (jd - 2451545.0) / 365250.0

def earth_heliocentric_longitude(t, max_error_arcsec: Optional[float] = None):
    """
    Earth heliocentric longitude (radians) at VSOP87 time t.
    
    Args:
        t: VSOP87 time parameter (millennia since J2000.0)
        max_error_arcsec: Maximum acceptable error in arcseconds.
                         If specified, will attempt to load appropriate coefficients.
    """
    coeffs = _get_coefficients(max_error_arcsec)
    series = [coeffs['L0'], coeffs['L1'], coeffs['L2'], coeffs['L3'], coeffs['L4'], coeffs['L5']]
    return (_eval(series, t) / 1e8) % (2 * math.pi)

def earth_heliocentric_latitude(t, max_error_arcsec: Optional[float] = None):
    """
    Earth heliocentric latitude (radians) at VSOP87 time t.
    
    Args:
        t: VSOP87 time parameter (millennia since J2000.0)
        max_error_arcsec: Maximum acceptable error in arcseconds.
                         If specified, will attempt to load appropriate coefficients.
    """
    coeffs = _get_coefficients(max_error_arcsec)
    series = [coeffs['B0'], coeffs['B1'], coeffs['B2'], coeffs['B3'], coeffs['B4'], coeffs['B5']]
    return _eval(series, t) / 1e8

def earth_radius_vector(t, max_error_arcsec: Optional[float] = None):
    """
    Earth radius vector (AU) at VSOP87 time t.
    
    Args:
        t: VSOP87 time parameter (millennia since J2000.0)
        max_error_arcsec: Maximum acceptable error in arcseconds.
                         If specified, will attempt to load appropriate coefficients.
    """
    coeffs = _get_coefficients(max_error_arcsec)
    series = [coeffs['R0'], coeffs['R1'], coeffs['R2'], coeffs['R3'], coeffs['R4'], coeffs['R5']]
    return _eval(series, t) / 1e8

def earth_heliocentric_position(jd, max_error_arcsec: Optional[float] = None):
    """
    Earth heliocentric position (L, B, R) at Julian Day jd.
    
    Args:
        jd: Julian Day
        max_error_arcsec: Maximum acceptable error in arcseconds.
                         If specified, will attempt to load appropriate coefficients.
    """
    t = _t(jd)
    return (
        earth_heliocentric_longitude(t, max_error_arcsec),
        earth_heliocentric_latitude(t, max_error_arcsec),
        earth_radius_vector(t, max_error_arcsec),
    )
    
