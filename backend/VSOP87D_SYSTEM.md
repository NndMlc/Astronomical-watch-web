# VSOP87D Dynamic Coefficient Loading System

This system provides on-demand loading of VSOP87D Earth coefficients with configurable precision based on accuracy requirements.

## Overview

The VSOP87D system allows users to specify a maximum acceptable error in arcseconds, and the system will automatically select and load the most appropriate set of coefficients to meet that requirement. This enables a balance between computational speed and astronomical accuracy.

## Components

### 1. Generator Script (`scripts/generate_vsop87.py`)

Downloads VSOP87D.EAR data and generates Python coefficient files with configurable precision.

**Usage:**
```bash
# Generate with specific amplitude threshold
python scripts/generate_vsop87.py --threshold 1e-6

# Auto-select threshold for 10 arcsecond accuracy
python scripts/generate_vsop87.py --auto-upgrade --target-arcsec 10

# Generate full precision (no truncation)
python scripts/generate_vsop87.py --threshold 0
```

**Features:**
- Downloads VSOP87D.EAR from IMCCE FTP server
- Parses into L0..L5, B0..B5, R0..R5 series  
- Truncates by minimum amplitude threshold
- Computes conservative upper bound error for Earth heliocentric longitude
- Auto-upgrade mode selects optimal threshold for target accuracy

### 2. Runtime Loader (`core/vsop87_earth.py`)

Enhanced VSOP87 Earth module with dynamic coefficient loading.

**API Changes:**
```python
# All functions now accept optional max_error_arcsec parameter
earth_heliocentric_longitude(t, max_error_arcsec=None)
earth_heliocentric_latitude(t, max_error_arcsec=None) 
earth_radius_vector(t, max_error_arcsec=None)
earth_heliocentric_position(jd, max_error_arcsec=None)
```

**Behavior:**
- `max_error_arcsec=None`: Uses built-in default coefficients (backward compatible)
- `max_error_arcsec=X`: Automatically loads appropriate coefficient file for X arcsec accuracy
- Falls back to default coefficients if no suitable file found
- Caches loaded coefficients for performance

### 3. Solar Module Updates (`core/solar.py`)

Solar longitude functions now support precision control.

**API:**
```python
apparent_solar_longitude(jd, max_error_arcsec=None)
solar_longitude_from_datetime(dt, max_error_arcsec=None)
```

**Example:**
```python
from core.solar import solar_longitude_from_datetime
from datetime import datetime, timezone

dt = datetime(2024, 3, 20, 12, 0, tzinfo=timezone.utc)

# Default precision
lon = solar_longitude_from_datetime(dt)

# High precision (1 arcsecond accuracy)
lon_precise = solar_longitude_from_datetime(dt, max_error_arcsec=1.0)
```

## File Organization

```
scripts/
├── generate_vsop87.py              # Generator script
├── vsop87d.ear                     # Downloaded VSOP87D data (auto-generated)
└── vsop87_coefficients/            # Generated coefficient files
    ├── vsop87d_earth_baseline_10arcsec.py    # 10 arcsec accuracy (~8.4 arcsec)
    ├── vsop87d_earth_baseline_60arcsec.py    # 60 arcsec accuracy (~42.4 arcsec)
    ├── vsop87d_earth_thresh_1e+03.py         # Custom threshold files
    └── vsop87d_earth_thresh_3e+03.py
```

## Error Bounds

The system computes conservative upper bounds for Earth heliocentric longitude error:

**Formula:** `Σ|A_discarded| / 1e8 * RAD_TO_ARCSEC`

Where:
- `A_discarded` are amplitude coefficients below the threshold
- Only longitude (L) series terms contribute to the error bound
- Result is a conservative estimate in arcseconds

## Coefficient File Format

Generated coefficient files contain:
- Metadata with threshold and error bound information
- Coefficient arrays (L0-L5, B0-B5, R0-R5) as tuples (A, B, C)
- Standard computation functions
- Each term contributes `A * cos(B + C * t)` to the series

## Performance

- **Caching:** Loaded coefficient sets are cached for subsequent use
- **Fallback:** System gracefully falls back to default coefficients if file loading fails
- **Auto-selection:** Finds the smallest suitable coefficient file for given accuracy requirement

## Integration

The system is fully backward compatible. Existing code continues to work unchanged, while new code can optionally specify precision requirements:

```python
# Existing code (unchanged)
from core.solar import solar_longitude_from_datetime
lon = solar_longitude_from_datetime(dt)

# New precision-aware code
lon_precise = solar_longitude_from_datetime(dt, max_error_arcsec=5.0)
```

## Testing

Run the comprehensive test suite:
```bash
python -m unittest tests.test_vsop87d_system -v
```

Tests cover:
- Backward compatibility
- Precision parameter handling
- Coefficient file detection and loading
- Caching functionality
- Integration with main astronomical_watch module

## Future Enhancements

1. **Real VSOP87D Data:** Replace test data with full VSOP87D.EAR download
2. **Additional Precision Levels:** Generate more baseline coefficient files
3. **Other Planets:** Extend system to Venus, Mars, etc.
4. **Automatic Updates:** Periodic refresh of coefficient files
5. **Memory Optimization:** Lazy loading of individual series
