"""
Time scale utilities with precise ΔT using Espenak & Meeus polynomials.
Provides UTC to Terrestrial Time (TT) conversion for high-precision calculations.
"""
from __future__ import annotations
import math
from datetime import datetime, timezone
from dataclasses import dataclass

# Constants
J2000_TT = 2451545.0  # JD of 2000-01-01 12:00:00 TT
DAY_SECONDS = 86400.0


def ensure_utc(dt: datetime) -> datetime:
    """Ensure datetime is in UTC timezone."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def datetime_to_jd_utc(dt: datetime) -> float:
    """Convert UTC datetime to Julian Day (UTC)."""
    dt = ensure_utc(dt)
    y = dt.year
    m = dt.month
    d = dt.day + (dt.hour + (dt.minute + (dt.second + dt.microsecond / 1e6) / 60.0) / 60.0) / 24.0
    
    if m <= 2:
        y -= 1
        m += 12
    
    A = y // 100
    B = 2 - A + (A // 4)
    jd = math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + d + B - 1524.5
    return jd


def decimal_year_from_datetime(dt: datetime) -> float:
    """Convert datetime to decimal year for ΔT calculation."""
    dt = ensure_utc(dt)
    year_start = datetime(dt.year, 1, 1, tzinfo=timezone.utc)
    next_year_start = datetime(dt.year + 1, 1, 1, tzinfo=timezone.utc)
    year_duration = (next_year_start - year_start).total_seconds()
    year_progress = (dt - year_start).total_seconds()
    return dt.year + year_progress / year_duration


def delta_t_espenak_meeus(year: float) -> float:
    """
    Calculate ΔT using Espenak & Meeus polynomials (1900-2050 focus).
    
    Args:
        year: Decimal year
    
    Returns:
        ΔT in seconds (TT - UTC)
    
    Reference: Espenak & Meeus, "Five Millennium Canon of Solar Eclipses"
    """
    y = year
    
    # Before 948 CE
    if y < 948:
        t = (y - 2000) / 100
        return 2177 + 497 * t + 44.1 * t * t
    
    # 948 - 1600
    elif 948 <= y < 1600:
        t = (y - 2000) / 100
        return 102 + 102 * t + 25.3 * t * t
    
    # 1600 - 1700
    elif 1600 <= y < 1700:
        t = y - 1600
        return 120 - 0.9808 * t - 0.01532 * t * t + t * t * t / 7129
    
    # 1700 - 1800
    elif 1700 <= y < 1800:
        t = y - 1700
        return 8.83 + 0.1603 * t - 0.0059285 * t * t + 0.00013336 * t * t * t - t * t * t * t / 1174000
    
    # 1800 - 1860
    elif 1800 <= y < 1860:
        t = y - 1800
        return 13.72 - 0.332447 * t + 0.0068612 * t * t + 0.0041116 * t * t * t - 0.00037436 * t * t * t * t + \
               0.0000121272 * t * t * t * t * t - 0.0000001699 * t * t * t * t * t * t + \
               0.000000000875 * t * t * t * t * t * t * t
    
    # 1860 - 1900
    elif 1860 <= y < 1900:
        t = y - 1860
        return 7.62 + 0.5737 * t - 0.251754 * t * t + 0.01680668 * t * t * t - \
               0.0004473624 * t * t * t * t + t * t * t * t * t / 233174
    
    # 1900 - 1920
    elif 1900 <= y < 1920:
        t = y - 1900
        return -2.79 + 1.494119 * t - 0.0598939 * t * t + 0.0061966 * t * t * t - 0.000197 * t * t * t * t
    
    # 1920 - 1941
    elif 1920 <= y < 1941:
        t = y - 1920
        return 21.20 + 0.84493 * t - 0.076100 * t * t + 0.0020936 * t * t * t
    
    # 1941 - 1961
    elif 1941 <= y < 1961:
        t = y - 1950
        return 29.07 + 0.407 * t - t * t / 233 + t * t * t / 2547
    
    # 1961 - 1986
    elif 1961 <= y < 1986:
        t = y - 1975
        return 45.45 + 1.067 * t - t * t / 260 - t * t * t / 718
    
    # 1986 - 2005
    elif 1986 <= y < 2005:
        t = y - 2000
        return 63.86 + 0.3345 * t - 0.060374 * t * t + 0.0017275 * t * t * t + \
               0.000651814 * t * t * t * t + 0.00002373599 * t * t * t * t * t
    
    # 2005 - 2050
    elif 2005 <= y <= 2050:
        t = y - 2000
        return 62.92 + 0.32217 * t + 0.005589 * t * t
    
    # After 2050 - parabolic extrapolation
    else:
        u = (y - 1820) / 100
        return -20 + 32 * u * u


@dataclass
class TimeScales:
    """Container for various time scales."""
    jd_utc: float      # Julian Day in UTC
    jd_tt: float       # Julian Day in Terrestrial Time
    delta_t: float     # ΔT in seconds (TT - UTC)
    decimal_year: float # Decimal year for input datetime


def utc_to_tt(jd_utc: float, year: float) -> float:
    """
    Convert Julian Day from UTC to Terrestrial Time.
    
    Args:
        jd_utc: Julian Day in UTC
        year: Decimal year for ΔT calculation
    
    Returns:
        Julian Day in TT
    """
    delta_t_sec = delta_t_espenak_meeus(year)
    return jd_utc + delta_t_sec / DAY_SECONDS


def timescales_from_datetime(dt: datetime) -> TimeScales:
    """
    Convert datetime to all relevant time scales.
    
    Args:
        dt: Input datetime (will be converted to UTC)
    
    Returns:
        TimeScales object with UTC, TT, and ΔT
    """
    dt_utc = ensure_utc(dt)
    jd_utc = datetime_to_jd_utc(dt_utc)
    decimal_year = decimal_year_from_datetime(dt_utc)
    delta_t_sec = delta_t_espenak_meeus(decimal_year)
    jd_tt = jd_utc + delta_t_sec / DAY_SECONDS
    
    return TimeScales(
        jd_utc=jd_utc,
        jd_tt=jd_tt,
        delta_t=delta_t_sec,
        decimal_year=decimal_year
  )"""
Time scale utilities with precise ΔT using Espenak & Meeus polynomials.
Provides UTC to Terrestrial Time (TT) conversion for high-precision calculations.
"""
from __future__ import annotations
import math
from datetime import datetime, timezone
from dataclasses import dataclass

# Constants
J2000_TT = 2451545.0  # JD of 2000-01-01 12:00:00 TT
DAY_SECONDS = 86400.0


def ensure_utc(dt: datetime) -> datetime:
    """Ensure datetime is in UTC timezone."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def datetime_to_jd_utc(dt: datetime) -> float:
    """Convert UTC datetime to Julian Day (UTC)."""
    dt = ensure_utc(dt)
    y = dt.year
    m = dt.month
    d = dt.day + (dt.hour + (dt.minute + (dt.second + dt.microsecond / 1e6) / 60.0) / 60.0) / 24.0
    
    if m <= 2:
        y -= 1
        m += 12
    
    A = y // 100
    B = 2 - A + (A // 4)
    jd = math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + d + B - 1524.5
    return jd


def decimal_year_from_datetime(dt: datetime) -> float:
    """Convert datetime to decimal year for ΔT calculation."""
    dt = ensure_utc(dt)
    year_start = datetime(dt.year, 1, 1, tzinfo=timezone.utc)
    next_year_start = datetime(dt.year + 1, 1, 1, tzinfo=timezone.utc)
    year_duration = (next_year_start - year_start).total_seconds()
    year_progress = (dt - year_start).total_seconds()
    return dt.year + year_progress / year_duration


def delta_t_espenak_meeus(year: float) -> float:
    """
    Calculate ΔT using Espenak & Meeus polynomials (1900-2050 focus).
    
    Args:
        year: Decimal year
    
    Returns:
        ΔT in seconds (TT - UTC)
    
    Reference: Espenak & Meeus, "Five Millennium Canon of Solar Eclipses"
    """
    y = year
    
    # Before 948 CE
    if y < 948:
        t = (y - 2000) / 100
        return 2177 + 497 * t + 44.1 * t * t
    
    # 948 - 1600
    elif 948 <= y < 1600:
        t = (y - 2000) / 100
        return 102 + 102 * t + 25.3 * t * t
    
    # 1600 - 1700
    elif 1600 <= y < 1700:
        t = y - 1600
        return 120 - 0.9808 * t - 0.01532 * t * t + t * t * t / 7129
    
    # 1700 - 1800
    elif 1700 <= y < 1800:
        t = y - 1700
        return 8.83 + 0.1603 * t - 0.0059285 * t * t + 0.00013336 * t * t * t - t * t * t * t / 1174000
    
    # 1800 - 1860
    elif 1800 <= y < 1860:
        t = y - 1800
        return 13.72 - 0.332447 * t + 0.0068612 * t * t + 0.0041116 * t * t * t - 0.00037436 * t * t * t * t + \
               0.0000121272 * t * t * t * t * t - 0.0000001699 * t * t * t * t * t * t + \
               0.000000000875 * t * t * t * t * t * t * t
    
    # 1860 - 1900
    elif 1860 <= y < 1900:
        t = y - 1860
        return 7.62 + 0.5737 * t - 0.251754 * t * t + 0.01680668 * t * t * t - \
               0.0004473624 * t * t * t * t + t * t * t * t * t / 233174
    
    # 1900 - 1920
    elif 1900 <= y < 1920:
        t = y - 1900
        return -2.79 + 1.494119 * t - 0.0598939 * t * t + 0.0061966 * t * t * t - 0.000197 * t * t * t * t
    
    # 1920 - 1941
    elif 1920 <= y < 1941:
        t = y - 1920
        return 21.20 + 0.84493 * t - 0.076100 * t * t + 0.0020936 * t * t * t
    
    # 1941 - 1961
    elif 1941 <= y < 1961:
        t = y - 1950
        return 29.07 + 0.407 * t - t * t / 233 + t * t * t / 2547
    
    # 1961 - 1986
    elif 1961 <= y < 1986:
        t = y - 1975
        return 45.45 + 1.067 * t - t * t / 260 - t * t * t / 718
    
    # 1986 - 2005
    elif 1986 <= y < 2005:
        t = y - 2000
        return 63.86 + 0.3345 * t - 0.060374 * t * t + 0.0017275 * t * t * t + \
               0.000651814 * t * t * t * t + 0.00002373599 * t * t * t * t * t
    
    # 2005 - 2050
    elif 2005 <= y <= 2050:
        t = y - 2000
        return 62.92 + 0.32217 * t + 0.005589 * t * t
    
    # After 2050 - parabolic extrapolation
    else:
        u = (y - 1820) / 100
        return -20 + 32 * u * u


@dataclass
class TimeScales:
    """Container for various time scales."""
    jd_utc: float      # Julian Day in UTC
    jd_tt: float       # Julian Day in Terrestrial Time
    delta_t: float     # ΔT in seconds (TT - UTC)
    decimal_year: float # Decimal year for input datetime


def utc_to_tt(jd_utc: float, year: float) -> float:
    """
    Convert Julian Day from UTC to Terrestrial Time.
    
    Args:
        jd_utc: Julian Day in UTC
        year: Decimal year for ΔT calculation
    
    Returns:
        Julian Day in TT
    """
    delta_t_sec = delta_t_espenak_meeus(year)
    return jd_utc + delta_t_sec / DAY_SECONDS


def timescales_from_datetime(dt: datetime) -> TimeScales:
    """
    Convert datetime to all relevant time scales.
    
    Args:
        dt: Input datetime (will be converted to UTC)
    
    Returns:
        TimeScales object with UTC, TT, and ΔT
    """
    dt_utc = ensure_utc(dt)
    jd_utc = datetime_to_jd_utc(dt_utc)
    decimal_year = decimal_year_from_datetime(dt_utc)
    delta_t_sec = delta_t_espenak_meeus(decimal_year)
    jd_tt = jd_utc + delta_t_sec / DAY_SECONDS
    
    return TimeScales(
        jd_utc=jd_utc,
        jd_tt=jd_tt,
        delta_t=delta_t_sec,
        decimal_year=decimal_year
  )
