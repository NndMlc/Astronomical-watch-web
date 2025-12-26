# astronomical_watch_core

Minimalni Python modul za izračunavanje astronomskog vremena (Dies, miliDies) i ekvinocijuma, spreman za embedovanje u druge aplikacije.

## Sadrži
- Funkcije za izračunavanje dies/miliDies prema referentnom meridijanu
- Funkciju za izračunavanje trenutka prolećne ravnodnevice (ekvinocijuma)
- Nema zavisnosti osim standardne biblioteke

## Primer korišćenja
```python
from astronomical_watch_core import astronomical_time, compute_vernal_equinox
from datetime import datetime, timezone

dt = datetime.now(timezone.utc)
dies, milidies = astronomical_time(dt)
print(f"Dies: {dies}, miliDies: {milidies}")

ve = compute_vernal_equinox(2026)
print(f"Vernal equinox 2026: {ve.isoformat()}")
```

## Instalacija (lokalno)
```bash
pip install .
```

## API
- `astronomical_time(dt: datetime) -> tuple[int, int]`
- `compute_vernal_equinox(year: int) -> datetime`

## Licenca
Core algoritam pod Astronomical Watch Core License (restriktivna, vidi LICENSE.CORE)
