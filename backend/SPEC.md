# Astronomical Watch Specification v1.0 (Immutable Reference)

Status: FROZEN – textual specification may be copied but not altered when redistributed. Propose changes upstream.

## Purpose
Define a reproducible astronomical time frame starting at the vernal equinox and expressing instants as (day_index, milli_day).

## Frame Definition
1. Epoch: Vernal equinox (apparent geocentric solar ecliptic longitude = 0°) for the governing tropical year.
2. Day 0 Start: First computed reference mean noon (λ_ref = -168.975°) that is >= equinox timestamp.
3. Day Index: Integer number of full SI days (86400 s) since Day 0 Start.
4. Sub-day Fraction: milli_day = floor(1000 * seconds_in_current_day / 86400), range 0..999.
5. Rollover: When a new day boundary (multiple of 86400 s from Day 0 Start) is crossed, day_index increments and milli_day resets.

## Solar & Equinox Computation (Simplified)
- Solar position: Simplified Meeus low-precision series (no full nutation / ΔT refinement yet).
- Apparent longitude λ_app used; equinox solves λ_app ≡ 0° (mod 360) via iterative linear correction.
- Improvement room: Higher order terms, ΔT modeling, robust root-finding, error bounds.

## Constraints
Compliant "Core" implementations MUST match algorithmic steps above (within later published tolerance criteria) to claim the name "Astronomical Watch".

## Invariance Policy
The contents of src/astronomical_watch/core/* are the canonical reference implementation. Modifications require upstream acceptance.
