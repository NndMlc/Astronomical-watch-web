from datetime import datetime, timezone
from fastapi import APIRouter
from services.equinox_service import get_vernal_equinox_datetime

router = APIRouter()

def _next_vernal_equinox(now_utc: datetime) -> datetime:
    year = now_utc.year
    candidate = get_vernal_equinox_datetime(year)
    if candidate <= now_utc:
        candidate = get_vernal_equinox_datetime(year + 1)
    return candidate

@router.get("/equinox/next")
def next_equinox():
    now = datetime.now(timezone.utc)
    target = _next_vernal_equinox(now)
    diff = target - now
    return {
        "utc": target.isoformat().replace("+00:00","Z"),
        "seconds_until": int(diff.total_seconds()),
        "days_until": diff.total_seconds() / 86400.0
    }

@router.get("/equinox/{year}")
def equinox_year(year: int):
    dt = get_vernal_equinox_datetime(year)
    return {
        "year": year,
        "utc": dt.isoformat().replace("+00:00","Z")
    }
