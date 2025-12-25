"""
solar.py

Prividna ekliptička dužina Sunca i udaljenost, uz opcioni zahtev za maksimalnu grešku modela.

Osnovne heliocentričke geometrijske pozicije (demonstracija).
Korišćen je trunkirani VSOP87 (samo longituda iz vsop87_earth) + jednostavna korekcija nutacije
za geometrijsku sunčevu longitudu. Ovo NIJE fizički kompletno.

Updated to support configurable VSOP87D precision via max_error_arcsec parameter.

"""
from __future__ import annotations
import math
from datetime import datetime
from typing import Optional

from .timebase import timescales_from_datetime, J2000
from .vsop87_earth import earth_heliocentric_position, earth_heliocentric_longitude
from .nutation import nutation_simple

TAU = 2 * math.pi

def centuries_since_j2000(jd: float) -> float:
    """Convert Julian Day to centuries since J2000.0"""
    return (jd - J2000) / 36525.0

def apparent_solar_longitude(jd_tt: float, max_error_arcsec: Optional[float] = None) -> float:
    """
    Vraća aproksimativnu prividnu ekliptičku longitudu Sunca (radijani),
    koristeći trunkiranu heliocentričku longitudu Zemlje i dodavanje π (geocentrički).
    Dodaje i nutacionu korekciju dpsi * cos(eps).
    
    Args:
        jd_tt: Julian Day (Terrestrial Time)
        max_error_arcsec: Maximum acceptable error in arcseconds for VSOP87 calculation.
                         If None, uses default precision from current vsop87_earth module.
    """
    L_e, B_e, R_e = earth_heliocentric_position(jd_tt, max_error_arcsec=max_error_arcsec)
    L_geo = (L_e + math.pi) % TAU
    nut = nutation_simple(jd_tt)
    return (L_geo + nut.dpsi * math.cos(nut.eps)) % TAU

def solar_longitude_and_distance_from_datetime(dt: datetime, max_error_arcsec: Optional[float] = None):
    """Compute solar longitude and distance from datetime"""
    ts = timescales_from_datetime(dt)
    L_e, B_e, R_e = earth_heliocentric_position(ts.jd_tt, max_error_arcsec=max_error_arcsec)
    L_geo = (L_e + math.pi) % TAU
    nut = nutation_simple(ts.jd_tt)
    L_app = (L_geo + nut.dpsi * math.cos(nut.eps)) % TAU
    return L_app, R_e

def solar_longitude_from_datetime(dt: datetime, max_error_arcsec: Optional[float] = None) -> float:
    """Compute apparent solar longitude from datetime with optional precision control"""
    return solar_longitude_and_distance_from_datetime(dt, max_error_arcsec)[0]


__all__ = [
    "apparent_solar_longitude",
    "solar_longitude_from_datetime",
    "solar_longitude_and_distance_from_datetime",
]
