"""
equinox.py (Core)
Numerical search for vernal equinox time: apparent geocentric solar ecliptic longitude = 0°.
License: Astronomical Watch Core License v1.0 (NO MODIFICATION). See LICENSE.CORE
"""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Optional
from .solar import apparent_solar_longitude
from .timebase import datetime_to_jd

def compute_vernal_equinox(
    year: int, 
    max_iter: int = 10, 
    tol_seconds: float = 10.0,
    max_error_arcsec: Optional[float] = 1.0
) -> datetime:
    """
    Compute vernal equinox instant for given year using VSOP87D and numerical iteration.
    
    Args:
        year: Calendar year for equinox
        max_iter: Maximum Newton-Raphson iterations (default: 10)
        tol_seconds: Convergence tolerance in seconds (default: 10.0 for high precision)
        max_error_arcsec: Maximum VSOP87D error in arcseconds (default: 1.0 for <1" accuracy)
                         Set to None to use default truncated coefficients.
    
    Returns:
        datetime: UTC instant of vernal equinox (apparent geocentric longitude = 0°)
    """
    guess = datetime(year, 3, 20, 12, 0, 0, tzinfo=timezone.utc)
    def f(dt: datetime) -> float:
        lam = apparent_solar_longitude(datetime_to_jd(dt), max_error_arcsec=max_error_arcsec)
        # lam je u radijanima, konvertuj u stepene za lakše računanje
        lam_deg = lam * 180.0 / 3.14159265359
        # Vraća razliku od 0° (prolećna ravnodnevnica)
        diff = ((lam_deg + 180) % 360) - 180
        return diff
    dt0 = guess
    step = timedelta(hours=6)
    prev_val = f(dt0)
    for _ in range(10):
        dt1 = dt0 - step
        dt2 = dt0 + step
        v1 = f(dt1)
        v2 = f(dt2)
        if v1 == 0:
            return dt1
        if v2 == 0:
            return dt2
        if abs(v1) < abs(prev_val):
            dt0, prev_val = dt1, v1
        if abs(v2) < abs(prev_val):
            dt0, prev_val = dt2, v2
        step /= 2
    current = dt0
    for _ in range(max_iter):
        val = f(current)
        dldt = 0.98564736 / 86400.0
        dt_correction_seconds = val / dldt
        new_current = current - timedelta(seconds=dt_correction_seconds)
        if abs(dt_correction_seconds) < tol_seconds:
            return new_current
        current = new_current
    return current
