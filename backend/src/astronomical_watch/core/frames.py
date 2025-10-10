"""
frames.py
Minimalni koordinatni okviri (stub):
- Pretvaranje iz ekliptičkih u ekvatorijalne koordinate.
"""
from __future__ import annotations
import math
from typing import Tuple
from .nutation import mean_obliquity

def ecliptic_to_equatorial(lon: float, lat: float, jd: float) -> Tuple[float, float]:
    """
    Konverzija ekliptičkih (λ, β) u ekvatorijalne (α, δ) u radijanima.
    Koristi srednju kosost ekliptike.
    """
    eps = mean_obliquity(jd)
    sin_dec = (math.sin(lat) * math.cos(eps) +
               math.cos(lat) * math.sin(eps) * math.sin(lon))
    dec = math.asin(sin_dec)

    y = math.sin(lon) * math.cos(eps) - math.tan(lat) * math.sin(eps)
    x = math.cos(lon)
    ra = math.atan2(y, x) % (2 * math.pi)
    return ra, dec

__all__ = ["ecliptic_to_equatorial"]
