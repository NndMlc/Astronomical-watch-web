"""
Primer validnog plugina za astronomical_watch_core
"""
from datetime import datetime

def dies_notification(dt: datetime):
    # Notifikacija kada je dies deljiv sa 100
    from astronomical_watch_core import astronomical_time
    dies, _ = astronomical_time(dt)
    if dies % 100 == 0:
        return f"Jubilarni dies: {dies:03d}!"
    return None

# Plugin je običan objekat ili dict sa funkcijama
plugin = {
    "dies_notification": dies_notification
}
