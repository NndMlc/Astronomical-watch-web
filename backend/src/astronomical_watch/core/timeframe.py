"""
timeframe.py (Core)
Convert UTC datetime into (dies, miliDies) relative to vernal equinox frame.
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

    # Izračunaj podne na referentnom meridijanu za dati dan
    def ref_noon(dt_):
        return reference_noon_utc_for_day(dt_)

    # Ako je trenutak pre prvog podneva nakon ekvinocija
    if dt < day0:
        dies = 0
        # miliDies se računa od poslednjeg podneva (pre dt)
        # Pronađi poslednji podne na referentnom meridijanu
        prev_noon = ref_noon(dt)
        if dt < prev_noon:
            prev_noon -= timedelta(days=1)
        intra = (dt - prev_noon).total_seconds()
        if intra < 0:
            intra = 0
        miliDies = int((intra / DAY_SECONDS) * 1000)
        if miliDies > 999:
            miliDies = 999
        return dies, miliDies

    # Nakon prvog podneva: dies = 1, 2, ...
    seconds_since_day0 = (dt - day0).total_seconds()
    dies = int(seconds_since_day0 // DAY_SECONDS) + 1
    current_day_start = day0 + timedelta(days=dies - 1)
    intra = (dt - current_day_start).total_seconds()
    if intra < 0:
        intra = 0
    miliDies = int((intra / DAY_SECONDS) * 1000)
    if miliDies > 999:
        miliDies = 999
    return dies, miliDies
