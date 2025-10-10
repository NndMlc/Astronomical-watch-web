```
List of files constituting the protected Core (hash optional for future verification):

- src/astronomical_watch/core/__init__.py
- src/astronomical_watch/core/solar.py
- src/astronomical_watch/core/equinox.py
- src/astronomical_watch/core/timeframe.py
- src/astronomical_watch/core/timebase.py
- src/astronomical_watch/core/vsop87_earth.py
- src/astronomical_watch/core/nutation.py
- src/astronomical_watch/core/frames.py
- src/astronomical_watch/core/delta_t.py

Any file not listed here is NOT part of the immutable Core and may be modified under its own license (e.g., MIT).

# Core Skeleton Files

Ovaj skeleton obuhvata:

- `core/timebase.py` – Julian Day, TT aproksimacija, ΔT stub.
- `core/vsop87_earth.py` – Trunkirani VSOP87 koeficijenti za longitudu Zemlje (DEMO).
- `core/nutation.py` – Uprošćena nutacija + srednja kosoća.
- `core/solar.py` – Prividna sunčeva longitudа (stub).
- `core/frames.py` – Konverzija ekliptičke u ekvatorijalnu koordinatu (srednja kosoća).
- `core/__init__.py` – Re-export ključnih funkcija.
- `core/delta_t.py` – Model za ΔT.
- `core/equinox.py` – Računanje prolećnog ekvinoksa.
- `core/timeframe.py` – Konverzija UTC u astronomsko vreme.

## TODO (dalje faze)

1. Proširiti VSOP87 (L,B,R kompletne serije) ili uvesti bolji model (ELP za Mesec kasnije).
2. Implementirati IAU 2000A/2006 nutaciju i precesiju.
3. Preciznije računanje ΔT (ephemeris + istorijski fit).
4. Dodati transformacije prema ITRF / topocentričke koordinate.
5. Test pokrivenost za numeričku stabilnost i regresije.

## Test

`tests/test_core_skeleton.py` proverava osnovne domene (raspon vrednosti, monotonost JD).
```
