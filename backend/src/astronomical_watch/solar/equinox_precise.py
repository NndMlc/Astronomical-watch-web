"""
Precise vernal equinox solver using root-finding on apparent solar longitude = 0°.
Uses bracket and binary search or Brent's method over March window.
"""
from __future__ import annotations
import math
from datetime import datetime, timezone, timedelta
from typing import Tuple, Optional, Callable
from solar.solar_longitude_light import solar_longitude_from_datetime, vernal_equinox_solar_longitude_target
from astro.timescales import ensure_utc

# Constants
SECONDS_PER_DAY = 86400.0
MAX_ITERATIONS = 30
CONVERGENCE_TOLERANCE_SECONDS = 1.0  # Target accuracy in seconds
PI = math.pi
TAU = 2.0 * PI


def angle_difference(a: float, b: float) -> float:
    """
    Calculate the smallest angular difference between two angles in radians.
    
    Args:
        a, b: Angles in radians
    
    Returns:
        Signed difference (a - b) in range [-π, π]
    """
    diff = a - b
    # Normalize to [-π, π]
    while diff > PI:
        diff -= TAU
    while diff < -PI:
        diff += TAU
    return diff


def solar_longitude_objective(dt: datetime) -> float:
    """
    Objective function for root finding: λ_app - 0°
    
    Args:
        dt: Datetime to evaluate
    
    Returns:
        Signed angular difference from vernal equinox (radians)
    """
    lambda_app = solar_longitude_from_datetime(dt)
    target = vernal_equinox_solar_longitude_target()
    return angle_difference(lambda_app, target)


def find_march_bracket(year: int) -> Tuple[datetime, datetime]:
    """
    Find a bracketing interval around March 20 where the equinox occurs.
    
    Args:
        year: Target year
    
    Returns:
        Tuple of (start_dt, end_dt) that bracket the equinox
    """
    # Start with March 18-22 window
    start_dt = datetime(year, 3, 18, tzinfo=timezone.utc)
    end_dt = datetime(year, 3, 22, tzinfo=timezone.utc)
    
    # Check if we have a sign change in this window
    obj_start = solar_longitude_objective(start_dt)
    obj_end = solar_longitude_objective(end_dt)
    
    # If no sign change, expand the window
    if obj_start * obj_end > 0:
        # Try expanding to March 16-24
        start_dt = datetime(year, 3, 16, tzinfo=timezone.utc)
        end_dt = datetime(year, 3, 24, tzinfo=timezone.utc)
        
        obj_start = solar_longitude_objective(start_dt)
        obj_end = solar_longitude_objective(end_dt)
        
        if obj_start * obj_end > 0:
            raise ValueError(f"Cannot find sign change for equinox in year {year}")
    
    # Make sure we have the correct order (negative to positive)
    if obj_start > obj_end:
        start_dt, end_dt = end_dt, start_dt
    
    return start_dt, end_dt


def bisection_solve(
    func: Callable[[datetime], float],
    dt_a: datetime,
    dt_b: datetime,
    tolerance_sec: float = CONVERGENCE_TOLERANCE_SECONDS,
    max_iter: int = MAX_ITERATIONS
) -> datetime:
    """
    Solve for root using bisection method.
    
    Args:
        func: Objective function
        dt_a, dt_b: Bracketing datetimes
        tolerance_sec: Convergence tolerance in seconds
        max_iter: Maximum iterations
    
    Returns:
        Root datetime
    """
    fa = func(dt_a)
    fb = func(dt_b)
    
    if fa * fb > 0:
        raise ValueError("Function values must have opposite signs at endpoints")
    
    for iteration in range(max_iter):
        # Calculate midpoint
        mid_seconds = (dt_a.timestamp() + dt_b.timestamp()) / 2.0
        dt_mid = datetime.fromtimestamp(mid_seconds, tz=timezone.utc)
        
        fm = func(dt_mid)
        
        # Check convergence
        interval_sec = abs(dt_b.timestamp() - dt_a.timestamp())
        if interval_sec <= tolerance_sec:
            return dt_mid
        
        # Choose new bracket
        if fa * fm < 0:
            dt_b = dt_mid
            fb = fm
        else:
            dt_a = dt_mid
            fa = fm
    
    # Return best estimate even if not converged
    mid_seconds = (dt_a.timestamp() + dt_b.timestamp()) / 2.0
    return datetime.fromtimestamp(mid_seconds, tz=timezone.utc)


def brent_solve(
    func: Callable[[datetime], float],
    dt_a: datetime,
    dt_b: datetime,
    tolerance_sec: float = CONVERGENCE_TOLERANCE_SECONDS,
    max_iter: int = MAX_ITERATIONS
) -> datetime:
    """
    Solve for root using Brent's method (more sophisticated than bisection).
    
    Args:
        func: Objective function
        dt_a, dt_b: Bracketing datetimes  
        tolerance_sec: Convergence tolerance in seconds
        max_iter: Maximum iterations
    
    Returns:
        Root datetime
    """
    # Convert to timestamps for numerical work
    a = dt_a.timestamp()
    b = dt_b.timestamp()
    
    fa = func(dt_a)
    fb = func(dt_b)
    
    if fa * fb > 0:
        raise ValueError("Function values must have opposite signs at endpoints")
    
    if abs(fa) < abs(fb):
        a, b = b, a
        fa, fb = fb, fa
    
    c = a
    fc = fa
    mflag = True
    
    for iteration in range(max_iter):
        if abs(b - a) <= tolerance_sec:
            break
            
        if fa != fc and fb != fc:
            # Inverse quadratic interpolation
            s = a * fb * fc / ((fa - fb) * (fa - fc)) + \
                b * fa * fc / ((fb - fa) * (fb - fc)) + \
                c * fa * fb / ((fc - fa) * (fc - fb))
        else:
            # Secant method
            s = b - fb * (b - a) / (fb - fa)
        
        # Check if we should use bisection instead
        use_bisection = (
            not ((3*a + b)/4 <= s <= b) or
            (mflag and abs(s - b) >= abs(b - c)/2) or
            (not mflag and abs(s - b) >= abs(c - c)/2) or
            (mflag and abs(b - c) < tolerance_sec) or
            (not mflag and abs(c - c) < tolerance_sec)
        )
        
        if use_bisection:
            s = (a + b) / 2
            mflag = True
        else:
            mflag = False
        
        # Evaluate at s
        dt_s = datetime.fromtimestamp(s, tz=timezone.utc)
        fs = func(dt_s)
        
        c = b
        fc = fb
        
        if fa * fs < 0:
            b = s
            fb = fs
        else:
            a = s
            fa = fs
        
        if abs(fa) < abs(fb):
            a, b = b, a
            fa, fb = fb, fa
    
    return datetime.fromtimestamp(b, tz=timezone.utc)


def compute_vernal_equinox_precise(
    year: int,
    method: str = "brent",
    tolerance_sec: float = CONVERGENCE_TOLERANCE_SECONDS,
    max_iter: int = MAX_ITERATIONS
) -> datetime:
    """
    Compute precise vernal equinox for given year using root finding.
    
    Args:
        year: Target year
        method: "brent" or "bisection"
        tolerance_sec: Convergence tolerance in seconds
        max_iter: Maximum iterations
    
    Returns:
        Precise vernal equinox datetime (UTC)
    
    Raises:
        ValueError: If bracketing fails or invalid method
    """
    if method not in ["brent", "bisection"]:
        raise ValueError(f"Invalid method: {method}. Must be 'brent' or 'bisection'")
    
    # Find bracketing interval
    dt_a, dt_b = find_march_bracket(year)
    
    # Solve using selected method
    if method == "brent":
        result = brent_solve(solar_longitude_objective, dt_a, dt_b, tolerance_sec, max_iter)
    else:
        result = bisection_solve(solar_longitude_objective, dt_a, dt_b, tolerance_sec, max_iter)
    
    return ensure_utc(result)


def validate_equinox_solution(dt: datetime, tolerance_deg: float = 0.01) -> bool:
    """
    Validate that a datetime is close to the vernal equinox.
    
    Args:
        dt: Datetime to validate
        tolerance_deg: Angular tolerance in degrees
    
    Returns:
        True if within tolerance
    """
    obj_val = solar_longitude_objective(dt)
    tolerance_rad = tolerance_deg * PI / 180.0
    return abs(obj_val) <= tolerance_rad


def equinox_iteration_stats(year: int, method: str = "brent") -> dict:
    """
    Get detailed statistics about the equinox solution process.
    
    Args:
        year: Target year
        method: Solution method
    
    Returns:
        Dictionary with solution statistics
    """
    dt_a, dt_b = find_march_bracket(year)
    
    # Track iterations manually
    iteration_count = 0
    final_residual = 0.0
    
    def counting_objective(dt: datetime) -> float:
        nonlocal iteration_count, final_residual
        iteration_count += 1
        result = solar_longitude_objective(dt)
        final_residual = result
        return result
    
    if method == "brent":
        solution = brent_solve(counting_objective, dt_a, dt_b)
    else:
        solution = bisection_solve(counting_objective, dt_a, dt_b)
    
    return {
        "year": year,
        "method": method,
        "solution": solution,
        "iterations": iteration_count,
        "final_residual_rad": final_residual,
        "final_residual_deg": final_residual * 180.0 / PI,
        "bracket_start": dt_a,
        "bracket_end": dt_b,
        "bracket_width_hours": (dt_b - dt_a).total_seconds() / 3600.0
  }
