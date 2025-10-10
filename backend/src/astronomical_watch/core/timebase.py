"""
timebase.py
Osnovne konverzije vremena: UTC -> Julian Day, TT (aproks.), ΔT.
Skeleton – ΔT i preciznost će se kasnije poboljšati.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
import math

J2000 = 2451545.0  # JD of 2000-01-01 12:00:00 TT
DAY_SECONDS = 86400.0

def ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def datetime_to_jd(dt: datetime) -> float:
    dt = ensure_utc(dt)
    y = dt.year
    m = dt.month
    d = dt.day + (dt.hour + (dt.minute + (dt.second + dt.microsecond / 1e6)/60.0)/60.0)/24.0
    if m <= 2:
        y -= 1
        m += 12
    A = y // 100
    B = 2 - A + (A // 4)
    jd = math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + d + B - 1524.5
    return jd

def estimate_delta_t(year: float) -> float:
    # Gruba aproksimacija; zameniti boljim modelom
    t = year - 2000.0
    return 62.92 + 0.32217 * t + 0.005589 * t * t  # sekunde

def jd_tt(jd_utc: float) -> float:
    year = 2000.0 + (jd_utc - J2000) / 365.25
    delta_t_sec = estimate_delta_t(year)
    return jd_utc + delta_t_sec / DAY_SECONDS

@dataclass
class TimeScales:
    jd_utc: float
    jd_tt: float
    delta_t: float  # s

def timescales_from_datetime(dt: datetime) -> TimeScales:
    dt = ensure_utc(dt)
    jd_utc = datetime_to_jd(dt)
    year = dt.year + (dt.timetuple().tm_yday - 1 + dt.hour/24.0)/365.25
    delta_t = estimate_delta_t(year)
    return TimeScales(jd_utc=jd_utc, jd_tt=jd_tt(jd_utc), delta_t=delta_t)
