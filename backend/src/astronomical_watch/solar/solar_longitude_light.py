"""
Lightweight high-precision apparent solar longitude using Meeus algorithms.
Includes equation of center, aberration, and simplified nutation corrections.
"""
from __future__ import annotations
import math
from datetime import datetime
from astro.timescales import timescales_from_datetime

# Constants
TAU = 2.0 * math.pi
RAD_TO_DEG = 180.0 / math.pi
DEG_TO_RAD = math.pi / 180.0
ARCSEC_TO_RAD = math.pi / (180.0 * 3600.0)


def mod_360(degrees: float) -> float:
    """Normalize angle to [0, 360) degrees."""
    return degrees - 360.0 * math.floor(degrees / 360.0)


def centuries_since_j2000(jd_tt: float) -> float:
    """Calculate centuries since J2000.0 in TT."""
    return (jd_tt - 2451545.0) / 36525.0


def geometric_mean_longitude_sun(t: float) -> float:
    """
    Calculate geometric mean longitude of the Sun (Meeus Ch. 25).
    
    Args:
        t: Centuries since J2000.0 TT
    
    Returns:
        Geometric mean longitude in degrees
    """
    L0 = 280.46646 + t * (36000.76983 + t * 0.0003032)
    return mod_360(L0)


def mean_anomaly_sun(t: float) -> float:
    """
    Calculate mean anomaly of the Sun (Meeus Ch. 25).
    
    Args:
        t: Centuries since J2000.0 TT
    
    Returns:
        Mean anomaly in degrees
    """
    M = 357.52911 + t * (35999.05029 - t * 0.0001537)
    return mod_360(M)


def eccentricity_earth_orbit(t: float) -> float:
    """
    Calculate eccentricity of Earth's orbit (Meeus Ch. 25).
    
    Args:
        t: Centuries since J2000.0 TT
    
    Returns:
        Orbital eccentricity
    """
    return 0.016708634 - t * (0.000042037 + t * 0.0000001267)


def equation_of_center(t: float, M_deg: float, e: float) -> float:
    """
    Calculate equation of center for the Sun (Meeus Ch. 25).
    
    Args:
        t: Centuries since J2000.0 TT
        M_deg: Mean anomaly in degrees
        e: Orbital eccentricity
    
    Returns:
        Equation of center in degrees
    """
    M_rad = M_deg * DEG_TO_RAD
    
    # First, second, and third order terms
    C = (1.914602 - t * (0.004817 + t * 0.000014)) * math.sin(M_rad) + \
        (0.019993 - t * 0.000101) * math.sin(2.0 * M_rad) + \
        0.000289 * math.sin(3.0 * M_rad)
    
    return C


def true_longitude_sun(t: float) -> float:
    """
    Calculate true longitude of the Sun.
    
    Args:
        t: Centuries since J2000.0 TT
    
    Returns:
        True longitude in degrees
    """
    L0 = geometric_mean_longitude_sun(t)
    M = mean_anomaly_sun(t)
    e = eccentricity_earth_orbit(t)
    C = equation_of_center(t, M, e)
    
    return mod_360(L0 + C)


def mean_obliquity_ecliptic(t: float) -> float:
    """
    Calculate mean obliquity of the ecliptic (Meeus Ch. 22).
    
    Args:
        t: Centuries since J2000.0 TT
    
    Returns:
        Mean obliquity in degrees
    """
    eps0 = 23.0 + 26.0/60.0 + 21.448/3600.0 - \
           t * (46.815/3600.0 + t * (0.00059/3600.0 - t * 0.001813/3600.0))
    return eps0


def nutation_longitude_simple(t: float) -> float:
    """
    Simplified nutation in longitude (Meeus Ch. 22, main term only).
    
    Args:
        t: Centuries since J2000.0 TT
    
    Returns:
        Nutation in longitude in arcseconds
    """
    # Longitude of ascending node of Moon's mean orbit
    omega = 125.04452 - 1934.136261 * t + 0.0020708 * t * t + t * t * t / 450000.0
    omega_rad = omega * DEG_TO_RAD
    
    # Main term: -17.20 * sin(Omega)
    dpsi = -17.20 * math.sin(omega_rad)
    
    return dpsi  # arcseconds


def nutation_obliquity_simple(t: float) -> float:
    """
    Simplified nutation in obliquity (Meeus Ch. 22, main term only).
    
    Args:
        t: Centuries since J2000.0 TT
    
    Returns:
        Nutation in obliquity in arcseconds
    """
    # Longitude of ascending node of Moon's mean orbit
    omega = 125.04452 - 1934.136261 * t + 0.0020708 * t * t + t * t * t / 450000.0
    omega_rad = omega * DEG_TO_RAD
    
    # Main term: +9.20 * cos(Omega)
    deps = 9.20 * math.cos(omega_rad)
    
    return deps  # arcseconds


def aberration_correction(t: float) -> float:
    """
    Calculate aberration correction for the Sun (Meeus Ch. 25).
    
    Args:
        t: Centuries since J2000.0 TT
    
    Returns:
        Aberration correction in arcseconds
    """
    # Approximation: -20.4898 arcseconds
    return -20.4898


def apparent_solar_longitude_deg(jd_tt: float) -> float:
    """
    Calculate apparent longitude of the Sun including all corrections.
    
    Args:
        jd_tt: Julian Day in Terrestrial Time
    
    Returns:
        Apparent solar longitude in degrees [0, 360)
    """
    t = centuries_since_j2000(jd_tt)
    
    # True longitude
    lambda_true = true_longitude_sun(t)
    
    # Nutation in longitude
    dpsi_arcsec = nutation_longitude_simple(t)
    dpsi_deg = dpsi_arcsec / 3600.0
    
    # Aberration correction  
    aberr_arcsec = aberration_correction(t)
    aberr_deg = aberr_arcsec / 3600.0
    
    # Apparent longitude
    lambda_app = lambda_true + dpsi_deg + aberr_deg
    
    return mod_360(lambda_app)


def apparent_solar_longitude_rad(jd_tt: float) -> float:
    """
    Calculate apparent longitude of the Sun in radians.
    
    Args:
        jd_tt: Julian Day in Terrestrial Time
    
    Returns:
        Apparent solar longitude in radians [0, 2π)
    """
    lambda_deg = apparent_solar_longitude_deg(jd_tt)
    return lambda_deg * DEG_TO_RAD


def solar_longitude_from_datetime(dt: datetime) -> float:
    """
    Calculate apparent solar longitude from datetime.
    
    Args:
        dt: Input datetime (converted to UTC, then to TT)
    
    Returns:
        Apparent solar longitude in radians [0, 2π)
    """
    timescales = timescales_from_datetime(dt)
    return apparent_solar_longitude_rad(timescales.jd_tt)


def solar_longitude_deg_from_datetime(dt: datetime) -> float:
    """
    Calculate apparent solar longitude from datetime in degrees.
    
    Args:
        dt: Input datetime (converted to UTC, then to TT)
    
    Returns:
        Apparent solar longitude in degrees [0, 360)
    """
    timescales = timescales_from_datetime(dt)
    return apparent_solar_longitude_deg(timescales.jd_tt)


def vernal_equinox_solar_longitude_target() -> float:
    """
    Return the target solar longitude for vernal equinox.
    
    Returns:
        0.0 radians (0 degrees)
    """
    return 0.0
