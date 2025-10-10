
"""Astro Time Core

Implements a global, uniform astronomical time system based on:
- Reference meridian: 168°58'30" W ( -168.975 degrees )
- Global day boundary at mean solar noon for that meridian (LMST = 12h)
- Fixed daily boundary in UTC at 23:15:54 UTC (derived from longitude / 15)
- Uniform division of the mean solar day (86400 SI seconds) into 1000 equal units (milidans)
- Astronomical year bounded by successive real vernal equinox instants
- day_index resets exactly at vernal equinox instant (milidan continues)

This core is intentionally minimal and stable so higher layers (UI, features) can rely on
(day_index, milidan) being globally identical.
"""
from __future__ import annotations

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone, timedelta

# ---------------------- Constants (frozen interface) ---------------------- #
LONGITUDE_REF_DEG: float = -168.975  # 168°58'30" W
NOON_UTC_HOUR: int = 23
NOON_UTC_MINUTE: int = 15
NOON_UTC_SECOND: int = 54
NOON_UTC_SECONDS: int = (
    NOON_UTC_HOUR * 3600 + NOON_UTC_MINUTE * 60 + NOON_UTC_SECOND
)  # 83754
SECONDS_PER_DAY: int = 86400
MILLIDAN_PER_DAY: int = 1000
SECONDS_PER_MILLIDAN: float = SECONDS_PER_DAY / MILLIDAN_PER_DAY  # 86.4 s

__all__ = [
    "AstroReading",
    "AstroYear",
    "LONGITUDE_REF_DEG",
    "NOON_UTC_HOUR",
    "NOON_UTC_MINUTE",
    "NOON_UTC_SECOND",
    "NOON_UTC_SECONDS",
    "SECONDS_PER_DAY",
    "MILLIDAN_PER_DAY",
    "SECONDS_PER_MILLIDAN",
]

# ---------------------- Data Classes ---------------------- #

@dataclass(frozen=True)
class AstroReading:
    """Snapshot of astronomical time.

    Attributes
    ----------
    utc : datetime
        UTC timestamp of the reading (timezone-aware, UTC).
    day_index : int
        Day index within current astronomical year (>=0) or -1 if before current cycle.
    milidan : int
        Integer in [0, 999], uniform subdivision of the current mean solar day.
    fraction : float
        milidan / 1000.0 convenience value.
    """

    utc: datetime
    day_index: int
    milidan: int
    fraction: float

    def iso(self) -> str:  # convenience
        return self.utc.isoformat().replace("+00:00", "Z")


# ---------------------- Core Year Object ---------------------- #

class AstroYear:
    """Represents one astronomical year between two real vernal equinox instants.

    The astronomical year begins exactly at current_equinox.
    - At that instant: day_index resets to 0 (even if mid-day), milidan unaffected.
    - Day boundary: fixed mean solar noon for reference meridian at 23:15:54 UTC.
    - Each subsequent boundary increments day_index.
    - On reaching next_equinox (if set and current time >= it) the year rolls over:
      * current_equinox <- next_equinox
      * day_index will appear as 0 for times >= new equinox prior to first noon
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
        milidan = int(fraction * MILLIDAN_PER_DAY)
        if milidan == MILLIDAN_PER_DAY:  # float edge
            milidan = MILLIDAN_PER_DAY - 1
            fraction = milidan / MILLIDAN_PER_DAY

        # day_index determination
        if t < self.current_equinox:
            day_index = -1  # before current cycle
        else:
            if t < self._first_noon_after_eq:
                day_index = 0
            else:
                delta = t - self._first_noon_after_eq
                day_index = 1 + int(delta.total_seconds() // SECONDS_PER_DAY)

        return AstroReading(
            utc=t,
            day_index=day_index,
            milidan=milidan,
            fraction=milidan / MILLIDAN_PER_DAY,
        )

    # Convenience for reverse mapping (approximate, ignoring equinox resets mid-day)
    def approximate_utc_from_day_milidan(self, day_index: int, milidan: int) -> datetime:
        if day_index < 0:
            raise ValueError("day_index must be >= 0")
        if not (0 <= milidan < MILLIDAN_PER_DAY):
            raise ValueError("milidan out of range")
        base_noon = self._first_noon_after_eq - timedelta(days=1)  # day_index 0 starts at equinox, may be mid-day
        # day_index 1 corresponds to first noon after eq, so base_noon aligning logic:
        # For approximate mapping we treat day_index 1 boundary as first_noon_after_eq.
        # Thus, effective noon for day_index d>=1: first_noon_after_eq + (d-1) days.
        if day_index == 0:
            # We cannot reconstruct exact UTC (since day 0 began at equinox). We return equinox + milidan offset.
            return self.current_equinox + timedelta(seconds=milidan * SECONDS_PER_MILLIDAN)
        target_noon = self._first_noon_after_eq + timedelta(days=day_index - 1)
        return target_noon + timedelta(seconds=milidan * SECONDS_PER_MILLIDAN)


# End of astro_time_core.py
# Reference meridian (decimal degrees, West negative). Provided by project specification.
LONGITUDE_REF_DEG: float = -168.975  # -168° 58′ 30″

# Local Mean Time (LMT) = UTC + LONGITUDE/15 h.
# For the reference longitude this is an offset of about -11.265 hours, meaning that when
# local mean time is 12:00:00, UTC is approximately 23:15:54.
NOON_UTC_HOUR: int = 23
NOON_UTC_MINUTE: int = 15
NOON_UTC_SECOND: int = 54

# Sub‑day subdivision.
MILIDIES_PER_DAY: int = 1000
SECONDS_PER_DAY: int = 86400
SECONDS_PER_MILIDIES: float = SECONDS_PER_DAY / MILIDIES_PER_DAY  # 86.4 seconds

# Legacy compatibility constants (aliases – keep until full migration).
MILLIDAN_PER_DAY = MILIDIES_PER_DAY  # legacy name
SECONDS_PER_MILLIDIES = SECONDS_PER_MILIDIES  # spelled from original draft

@dataclass(frozen=True)
class AstroReading:
    """Snapshot of astronomical time representation.

    Attributes:
        utc: Original UTC instant.
        dies: Day index within the astronomical (tropical) year, starting at 0.
        milidies: Subdivision of the current day (0..999).
        fraction: Floating fraction of the day in [0.0, 1.0) matching milidies / 1000 plus remainder.

    Deprecated alias properties (day_index, milidan) are provided for transitional compatibility.
    They intentionally emit no warnings yet; a future PR may introduce DeprecationWarning.
    """
    utc: datetime
    dies: int
    milidies: int
    fraction: float

    # Deprecated aliases --------------------------------------------------
    @property
    def day_index(self) -> int:  # legacy
        return self.dies

    @property
    def milidan(self) -> int:  # legacy
        return self.milidies

class AstroYear:
    """Encapsulates an astronomical year bounded by vernal equinox instants.

    Day boundaries are defined by the reference meridian's mean noon, which corresponds
    to a fixed UTC clock time of 23:15:54. The *first* boundary *after* the vernal equinox
    begins dies=1; the interval from the equinox instant up to that boundary is dies=0.
    Subsequent days are uniform 86400 s segments each subdivided into 1000 milidies.

    The length of dies=0 may be shorter or longer than a full day depending on the equinox
    instant. We still map its intra‑day progress onto the 0..999 milidies range for simplicity.
    """

    def __init__(self, current_equinox: datetime, next_equinox: datetime):
        if current_equinox.tzinfo is None or next_equinox.tzinfo is None:
            raise ValueError("Equinox datetimes must be timezone-aware (UTC)")
        if current_equinox >= next_equinox:
            raise ValueError("next_equinox must be after current_equinox")
        if current_equinox.tzinfo != timezone.utc or next_equinox.tzinfo != timezone.utc:
            raise ValueError("Equinox datetimes must be in UTC")
        self.current_equinox = current_equinox
        self.next_equinox = next_equinox
        # Pre-compute the first noon boundary after current equinox.
        self.first_noon_after_equinox = self._compute_first_noon_after(current_equinox)

    # ------------------------------------------------------------------
    @staticmethod
    def _compute_first_noon_after(instant: datetime) -> datetime:
        # Compute the UTC datetime of the next (or same if strictly later) reference noon after 'instant'.
        candidate = instant.replace(hour=NOON_UTC_HOUR, minute=NOON_UTC_MINUTE, second=NOON_UTC_SECOND, microsecond=0)
        if candidate <= instant:
            candidate += timedelta(days=1)
        return candidate

    # ------------------------------------------------------------------
    def to_reading(self, t: datetime) -> AstroReading:
        """Produce an AstroReading for UTC instant t (auto-handles rollover if needed)."""
        if t.tzinfo is None:
            raise ValueError("Input datetime must be timezone-aware UTC")
        if t.tzinfo != timezone.utc:
            raise ValueError("Input datetime must be UTC")

        # Rollover if t is beyond current astronomical year.
        if t >= self.next_equinox:
            raise ValueError("Instant beyond this AstroYear's range – construct a new AstroYear")

        if t < self.first_noon_after_equinox:
            dies = 0
            day_start = self.current_equinox
        else:
            delta = t - self.first_noon_after_equinox
            complete_days = int(delta.total_seconds() // SECONDS_PER_DAY)
            dies = 1 + complete_days
            day_start = self.first_noon_after_equinox + timedelta(days=complete_days)

        intra_seconds = (t - day_start).total_seconds()
        # Clamp potential floating errors just below 86400.
        if intra_seconds < 0:
            intra_seconds = 0.0
        if intra_seconds >= SECONDS_PER_DAY:
            intra_seconds = SECONDS_PER_DAY - 1e-9

        milidies = int((intra_seconds / SECONDS_PER_DAY) * MILIDIES_PER_DAY)
        fraction = intra_seconds / SECONDS_PER_DAY

        return AstroReading(utc=t, dies=dies, milidies=milidies, fraction=fraction)

    # Legacy alias -----------------------------------------------------
    def to_legacy_reading(self, t: datetime) -> AstroReading:
        return self.to_reading(t)

    # ------------------------------------------------------------------
    def approximate_utc_from_dies_milidies(self, dies: int, milidies: int) -> datetime:
        """Approximate UTC instant for given dies & milidies within this astronomical year.

        For dies=0 we map milidies over a synthetic 86400 s span starting at the equinox.
        For dies>=1 we map day spans of exactly 86400 s beginning at the first noon boundary.
        Raises ValueError if dies would exceed the year span.
        """
        if dies < 0:
            raise ValueError("dies must be >= 0")
        if not (0 <= milidies < MILIDIES_PER_DAY):
            raise ValueError("milidies out of range 0..999")

        if dies == 0:
            base = self.current_equinox
        else:
            base = self.first_noon_after_equinox + timedelta(days=dies - 1)

        approx = base + timedelta(seconds=(milidies + 0.5) * SECONDS_PER_MILIDIES)
        if approx >= self.next_equinox:
            raise ValueError("(dies, milidies) outside this astronomical year")
        return approx

    # Legacy alias name -------------------------------------------------
    def approximate_utc_from_day_milidan(self, day_index: int, milidan: int) -> datetime:
        return self.approximate_utc_from_dies_milidies(day_index, milidan)

    # Convenience -------------------------------------------------------
    @classmethod
    def from_equinoxes(cls, current_equinox: datetime, next_equinox: datetime) -> 'AstroYear':
        return cls(current_equinox, next_equinox)
