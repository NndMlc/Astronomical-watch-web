
from datetime import datetime, timezone, timedelta
import sys
sys.path.insert(0, '.')  # Omogući lokalni import ako nije instaliran
try:
    from astronomical_watch_core import astronomical_time
    from astronomical_watch_core.core.timeframe import DAY_SECONDS
except ImportError:
    # fallback za direktno pokretanje iz foldera
    from core.timeframe import astronomical_time, DAY_SECONDS

def test_milidies_rollover():
    # Test poslednji trenutak astronomskog dana (od podneva do podneva)
    from astronomical_watch_core.core.timeframe import reference_noon_utc_for_day
    base_date = datetime(2025, 3, 21, 0, 0, 0, tzinfo=timezone.utc)
    base = reference_noon_utc_for_day(base_date)
    next_noon = reference_noon_utc_for_day(base + timedelta(days=1))
    # Poslednji milidies pre sledećeg podneva
    almost_end = next_noon - timedelta(seconds=DAY_SECONDS/1000)
    dies, milidies = astronomical_time(almost_end)
    assert milidies == 999, f"Expected 999, got {milidies}"
    # Sledeći trenutak mora biti 0
    next_moment = next_noon
    dies2, milidies2 = astronomical_time(next_moment)
    assert milidies2 == 0, f"Expected 0, got {milidies2}"
    assert dies2 == dies + 1, f"Expected dies increment, got {dies2}"
    print("Test milidies rollover: OK")

if __name__ == "__main__":
    test_milidies_rollover()
