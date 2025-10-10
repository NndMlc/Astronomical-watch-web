"""
timeframe.py (Core)
Convert UTC datetime into (day_index, milli_day) relative to vernal equinox frame.
License: Astronomical Watch Core License v1.0 (NO MODIFICATION). See LICENSE.CORE
"""
from __future__ import annotations
from datetime import datetime, timezone, timedelta
from .equinox import compute_vernal_equinox

DAY_SECONDS = 86400
LAMBDA_REF_DEG = -168.975

def reference_noon_utc_for_day(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        raise ValueError("Expect timezone-aware UTC datetime.")
    date0 = dt.date()
    base_noon = datetime(date0.year, date0.month, date0.day, 12, 0, 0, tzinfo=timezone.utc)
    offset_hours = -LAMBDA_REF_DEG / 15.0
    return base_noon - timedelta(hours=offset_hours)

def first_day_start_after_equinox(equinox: datetime) -> datetime:
    candidate = reference_noon_utc_for_day(equinox)
    if candidate < equinox:
        candidate += timedelta(days=1)
    return candidate

def astronomical_time(dt: datetime) -> tuple[int, int]:
    if dt.tzinfo is None:
        raise ValueError("Datetime must be UTC (tz-aware).")
    year_guess = dt.year
    eq = compute_vernal_equinox(year_guess)
    if dt < eq:
        eq = compute_vernal_equinox(year_guess - 1)
    next_eq = compute_vernal_equinox(eq.year + 1)
    if dt >= next_eq:
        eq = next_eq
        next_eq = compute_vernal_equinox(eq.year + 1)
    day0 = first_day_start_after_equinox(eq)
    if dt < day0:
        return (0, 0)
    seconds_since_day0 = (dt - day0).total_seconds()
    day_index = int(seconds_since_day0 // DAY_SECONDS)
    current_day_start = day0 + timedelta(days=day_index)
    intra = (dt - current_day_start).total_seconds()
    if intra < 0:
        intra = 0
    milli_day = int((intra / DAY_SECONDS) * 1000)
    if milli_day > 999:
        milli_day = 999
    return day_index, milli_day
"""
