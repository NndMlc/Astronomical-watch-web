
"""Astro Time Core

Implements a global, uniform astronomical time system based on:
- Reference meridian: 168°58'30" W ( -168.975 degrees )
- Global day boundary at mean solar noon for that meridian (LMST = 12h)
- Fixed daily boundary in UTC at 23:15:54 UTC (derived from longitude / 15)
- Uniform division of the mean solar day (86400 SI seconds) into 1000 equal units (miliDies)
- Astronomical year bounded by successive real vernal equinox instants
- dies resets exactly at vernal equinox instant (miliDies continues)

This core is intentionally minimal and stable so higher layers (UI, features) can rely on
(dies, miliDies) being globally identical.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Optional

# ---------------------- Constants (frozen interface) ---------------------- #
LONGITUDE_REF_DEG: float = -168.975  # 168°58'30" W
NOON_UTC_HOUR: int = 0
NOON_UTC_MINUTE: int = 44
NOON_UTC_SECOND: int = 6
NOON_UTC_SECONDS: int = (
    NOON_UTC_HOUR * 3600 + NOON_UTC_MINUTE * 60 + NOON_UTC_SECOND
)  # 2646
SECONDS_PER_DAY: int = 86400
MILIDES_PER_DAY: int = 1000
SECONDS_PER_MILIDES: float = SECONDS_PER_DAY / MILIDES_PER_DAY  # 86.4 s

# mikroDies extension - 1/1000 of a miliDies
MIKRODIES_PER_MILIDES: int = 1000
MIKRODIES_PER_DAY: int = MILIDES_PER_DAY * MIKRODIES_PER_MILIDES  # 1,000,000
SECONDS_PER_MIKRODIES: float = SECONDS_PER_MILIDES / MIKRODIES_PER_MILIDES  # 0.0864 s

__all__ = [
    "AstroReading",
    "AstroYear",
    "LONGITUDE_REF_DEG",
    "NOON_UTC_HOUR",
    "NOON_UTC_MINUTE",
    "NOON_UTC_SECOND",
    "NOON_UTC_SECONDS",
    "SECONDS_PER_DAY",
    "MILIDES_PER_DAY",
    "SECONDS_PER_MILIDES",
    "MIKRODIES_PER_MILIDES",
    "MIKRODIES_PER_DAY",
    "SECONDS_PER_MIKRODIES",
]

# ---------------------- Data Classes ---------------------- #

@dataclass(frozen=True)
class AstroReading:
    """Snapshot of astronomical time.

    Attributes
    ----------
    utc : datetime
        UTC timestamp of the reading (timezone-aware, UTC).
    dies : int
        Dies index within current astronomical year (>=0) or -1 if before current cycle.
    miliDies : int
        Integer in [0, 999], uniform subdivision of the current mean solar day.
    fraction : float
        miliDies / 1000.0 convenience value.
    mikroDies : int
        Integer in [0, 999], subdivision of current miliDies (optional mikroDies precision).
    mikroDies_fraction : float
        Fractional part within current mikroDies for smooth animations.
    """

    utc: datetime
    dies: int
    miliDies: int
    fraction: float
    mikroDies: int = 0
    mikroDies_fraction: float = 0.0

    def iso(self) -> str:  # convenience
        return self.utc.isoformat().replace("+00:00", "Z")

    def timestamp(self) -> str:
        """Return DDD.mmm format"""
        return f"{self.dies:03d}.{self.miliDies:03d}"
    
    def timestamp_full(self) -> str:
        """Return DDD.mmm.µµµ format with mikroDies"""
        return f"{self.dies:03d}.{self.miliDies:03d}.{self.mikroDies:03d}"


# ---------------------- Core Year Object ---------------------- #

class AstroYear:
    """Represents one astronomical year between two real vernal equinox instants.

    The astronomical year begins exactly at current_equinox.
    - At that instant: dies resets to 0 (even if mid-day), milidan unaffected.
    - Day boundary: fixed mean solar noon for reference meridian at 23:15:54 UTC.
    - Each subsequent boundary increments dies.
    - On reaching next_equinox (if set and current time >= it) the year rolls over:
      * current_equinox <- next_equinox
      * dies will appear as 0 for times >= new equinox prior to first noon
      * next_equinox cleared (caller can set new one when computed)
    - milidan always derived from time since the last global noon, independent of equinox.

    Thread-safety: not inherently thread-safe (mutates internal state on rollover).
    Caller that needs concurrency safety should wrap with locks.
    """

    __slots__ = ("current_equinox", "next_equinox", "_first_noon_after_eq")

    def __init__(self, current_equinox: datetime, next_equinox: Optional[datetime] = None):
        if current_equinox.tzinfo != timezone.utc:
            raise ValueError("current_equinox must be timezone-aware UTC")
        if next_equinox and next_equinox.tzinfo != timezone.utc:
            raise ValueError("next_equinox must be timezone-aware UTC")
        self.current_equinox = current_equinox
        self.next_equinox = next_equinox
        self._first_noon_after_eq = self._compute_first_noon_after_eq()

    # ---------------------- Internal helpers ---------------------- #

    def _compute_first_noon_after_eq(self) -> datetime:
        eq_date = self.current_equinox.date()
        noon_candidate = datetime(
            eq_date.year,
            eq_date.month,
            eq_date.day,
            NOON_UTC_HOUR,
            NOON_UTC_MINUTE,
            NOON_UTC_SECOND,
            tzinfo=timezone.utc,
        )
        if noon_candidate >= self.current_equinox:
            return noon_candidate
        return noon_candidate + timedelta(days=1)

    @staticmethod
    def _last_noon(t: datetime) -> datetime:
        day_seconds = t.hour * 3600 + t.minute * 60 + t.second
        if day_seconds >= NOON_UTC_SECONDS:
            return datetime(
                t.year,
                t.month,
                t.day,
                NOON_UTC_HOUR,
                NOON_UTC_MINUTE,
                NOON_UTC_SECOND,
                tzinfo=timezone.utc,
            )
        prev = t - timedelta(days=1)
        return datetime(
            prev.year,
            prev.month,
            prev.day,
            NOON_UTC_HOUR,
            NOON_UTC_MINUTE,
            NOON_UTC_SECOND,
            tzinfo=timezone.utc,
        )

    def _maybe_rollover(self, t: datetime) -> bool:
        if self.next_equinox and t >= self.next_equinox:
            self.current_equinox = self.next_equinox
            self.next_equinox = None
            self._first_noon_after_eq = self._compute_first_noon_after_eq()
            return True
        return False

    # ---------------------- Public API ---------------------- #

    def update_next_equinox(self, next_equinox: datetime) -> None:
        """Provide the next equinox instant when it becomes known."""
        if next_equinox.tzinfo != timezone.utc:
            raise ValueError("next_equinox must be timezone-aware UTC")
        # Must be after current equinox
        if next_equinox <= self.current_equinox:
            raise ValueError("next_equinox must be after current_equinox")
        self.next_equinox = next_equinox

    def reading(self, t: datetime) -> AstroReading:
        """Return the astronomical time reading for UTC time t."""
        if t.tzinfo != timezone.utc:
            t = t.astimezone(timezone.utc)

        self._maybe_rollover(t)

        last_noon = self._last_noon(t)
        seconds_since = (t - last_noon).total_seconds()
        if seconds_since < 0:
            seconds_since = 0  # safeguard
        if seconds_since >= SECONDS_PER_DAY:
            # Exactly at boundary - treat as new cycle start
            seconds_since = 0
            last_noon = last_noon + timedelta(days=1)

        fraction = seconds_since / SECONDS_PER_DAY
        miliDies = int(fraction * MILIDES_PER_DAY)
        if miliDies == MILIDES_PER_DAY:  # float edge
            miliDies = MILIDES_PER_DAY - 1
            fraction = miliDies / MILIDES_PER_DAY

        # Calculate mikroDies precision within current miliDies
        # Total mikroDies since last noon
        total_mikroDies = seconds_since / SECONDS_PER_MIKRODIES
        mikroDies = int(total_mikroDies % MIKRODIES_PER_MILIDES)
        mikroDies_fraction = (total_mikroDies % 1.0)

        # dies determination
        if t < self.current_equinox:
            dies = -1  # before current cycle
        else:
            if t < self._first_noon_after_eq:
                dies = 0
            else:
                delta = t - self._first_noon_after_eq
                dies = 1 + int(delta.total_seconds() // SECONDS_PER_DAY)

        return AstroReading(
            utc=t,
            dies=dies,
            miliDies=miliDies,
            fraction=miliDies / MILIDES_PER_DAY,
            mikroDies=mikroDies,
            mikroDies_fraction=mikroDies_fraction,
        )

    # Convenience for reverse mapping (approximate, ignoring equinox resets mid-day)
    def approximate_utc_from_day_miliDies(self, dies: int, miliDies: int) -> datetime:
        if dies < 0:
            raise ValueError("dies must be >= 0")
        if not (0 <= miliDies < MILIDES_PER_DAY):
            raise ValueError("miliDies out of range")
        base_noon = self._first_noon_after_eq - timedelta(days=1)  # dies 0 starts at equinox, may be mid-day
        # dies 1 corresponds to first noon after eq, so base_noon aligning logic:
        # For approximate mapping we treat dies 1 boundary as first_noon_after_eq.
        # Thus, effective noon for dies d>=1: first_noon_after_eq + (d-1) days.
        if dies == 0:
            # We cannot reconstruct exact UTC (since day 0 began at equinox). We return equinox + miliDies offset.
            return self.current_equinox + timedelta(seconds=miliDies * SECONDS_PER_MILIDES)
        target_noon = self._first_noon_after_eq + timedelta(days=dies - 1)
        return target_noon + timedelta(seconds=miliDies * SECONDS_PER_MILIDES)


# End of astro_time_core.py
# Legacy compatibility constants (aliases – keep until full migration).
# These reference the corrected constants defined at the top of the file
MILLIDAN_PER_DAY = MILIDES_PER_DAY  # legacy name
SECONDS_PER_MILLIDIES = SECONDS_PER_MILIDES  # legacy alias from original draft




