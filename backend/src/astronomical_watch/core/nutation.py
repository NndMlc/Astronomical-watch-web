"""
nutation.py
Trunkirana (DEMO) implementacija nutacije i kosog položaja ekliptike.
Za ozbiljniji rad treba dodati pun IAU 2000/2006 model.
"""
from __future__ import annotations
from dataclasses import dataclass
import math

ARCSEC_TO_RAD = math.radians(1/3600)
J2000 = 2451545.0

@dataclass
class NutationAngles:
    dpsi: float  # rad (nutacija u dužini)
    deps: float  # rad (nutacija u kosoj)
    eps: float   # rad (srednja kosoća)

def mean_obliquity(jd: float) -> float:
    """Srednja kosoća ekliptike (Laskar 1986)"""
    t = (jd - J2000) / 36525.0
    seconds = 84381.406 - 46.836769*t - 0.0001831*t*t + 0.00200340*t*t*t - 5.76e-7*t**4 - 4.34e-8*t**5
    return seconds * ARCSEC_TO_RAD

def nutation_simple(jd: float) -> NutationAngles:
    """Veoma uprošćena nutacija: koristimo glavne terme Munioka i Sunčev.
    Ovo je samo placeholder: greške ~ nekoliko lučnih sekundi.
    """
    t = (jd - J2000) / 36525.0
    # Srednje elongacije (rad) – približno
    D = math.radians((297.85036 + 445267.111480*t) % 360)
    # M = math.radians((357.52772 + 35999.050340*t) % 360)
    Mprime = math.radians((134.96298 + 477198.867398*t) % 360)
    F = math.radians((93.27191 + 483202.017538*t) % 360)
    # Dve najveće amplitude (IAU 1980 prva dva reda)
    dpsi_arcsec = (-17.20 * math.sin(Mprime) - 1.32 * math.sin(2*D) - 0.23 * math.sin(2*F) + 0.21 * math.sin(2*Mprime))
    deps_arcsec = (9.20 * math.cos(Mprime) + 0.57 * math.cos(2*D) + 0.10 * math.cos(2*F) - 0.09 * math.cos(2*Mprime))
    eps = mean_obliquity(jd)
    return NutationAngles(dpsi=dpsi_arcsec*ARCSEC_TO_RAD, deps=deps_arcsec*ARCSEC_TO_RAD, eps=eps)

__all__ = ["NutationAngles", "nutation_simple", "mean_obliquity"]
