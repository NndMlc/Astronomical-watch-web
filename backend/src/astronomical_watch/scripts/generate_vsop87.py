#!/usr/bin/env python3
"""
VSOP87D Earth Coefficient Generator

Downloads VSOP87D Earth data and generates Python coefficient files with configurable
precision based on amplitude thresholds.

Usage:
    python scripts/generate_vsop87.py [--threshold AMPLITUDE] [--auto-upgrade --target-arcsec ARCSEC]
    
Examples:
    # Generate with specific amplitude threshold
    python scripts/generate_vsop87.py --threshold 1e-6
    
    # Auto-select threshold for 10 arcsecond accuracy
    python scripts/generate_vsop87.py --auto-upgrade --target-arcsec 10
    
    # Generate full precision (no truncation)
    python scripts/generate_vsop87.py --threshold 0
"""

import argparse
import urllib.request
from pathlib import Path
from typing import List, Tuple, Optional, Dict
import sys

# Constants
RAD_TO_ARCSEC = 206264.806247096  # radians to arcseconds conversion
VSOP87D_URL = "https://ftp.imcce.fr/pub/ephem/planets/vsop87/vsop87d.ear"
SCRIPT_DIR = Path(__file__).parent
DATA_FILE = SCRIPT_DIR / "vsop87d.ear"
OUTPUT_DIR = SCRIPT_DIR / "vsop87_coefficients"

def download_vsop87d_file():
    """Download VSOP87D.EAR file if not present locally."""
    if DATA_FILE.exists():
        print(f"VSOP87D file already exists: {DATA_FILE}")
        return
        
    print(f"Downloading VSOP87D file from {VSOP87D_URL}...")
    try:
        urllib.request.urlretrieve(VSOP87D_URL, DATA_FILE)
        print(f"Downloaded successfully to {DATA_FILE}")
    except Exception as e:
        print(f"Failed to download VSOP87D file: {e}")
        sys.exit(1)

def parse_vsop87d_file() -> Dict[str, List[List[Tuple[float, float, float]]]]:
    """
    Parse VSOP87D.EAR file into structured data.
    
    Returns:
        Dictionary with keys L0-L5, B0-B5, R0-R5, each containing list of terms.
        Each term is a tuple (A, B, C) where the contribution is A * cos(B + C*t).
    """
    print(f"Parsing VSOP87D file: {DATA_FILE}")
    
    if not DATA_FILE.exists():
        print(f"Error: VSOP87D file not found: {DATA_FILE}")
        sys.exit(1)
    
    series_data = {}
    for coord in ['L', 'B', 'R']:
        for power in range(6):  # 0 through 5
            series_data[f"{coord}{power}"] = []
    
    current_series = None
    
    try:
        with open(DATA_FILE, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Look for series headers like "VSOP87D    3   0   L   0"
                if "VSOP87D" in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        coord = parts[3]  # L, B, or R
                        power = int(parts[4])  # 0, 1, 2, 3, 4, or 5
                        current_series = f"{coord}{power}"
                        print(f"Found series: {current_series}")
                        continue
                
                # Parse coefficient lines
                if current_series:
                    parts = line.split()
                    if len(parts) >= 3:
                        try:
                            A = float(parts[0])  # Amplitude
                            B = float(parts[1])  # Phase (radians)
                            C = float(parts[2])  # Frequency (radians/millennium)
                            
                            series_data[current_series].append((A, B, C))
                        except (ValueError, IndexError):
                            # Skip malformed lines
                            continue
    
    except Exception as e:
        print(f"Error parsing VSOP87D file: {e}")
        sys.exit(1)
    
    # Print summary
    total_terms = sum(len(terms) for terms in series_data.values())
    print(f"Parsed {total_terms} total terms across all series")
    for series_name, terms in series_data.items():
        if terms:
            print(f"  {series_name}: {len(terms)} terms")
    
    return series_data

def compute_conservative_error_bound(discarded_terms: List[Tuple[float, float, float]]) -> float:
    """
    Compute conservative upper bound error for discarded terms in Earth heliocentric longitude.
    
    Args:
        discarded_terms: List of (A, B, C) tuples that were discarded
        
    Returns:
        Conservative error bound in arcseconds
    """
    if not discarded_terms:
        return 0.0
    
    # Sum absolute amplitudes of discarded terms
    sum_amplitudes = sum(abs(A) for A, B, C in discarded_terms)
    
    # Convert from VSOP87 units to arcseconds
    # VSOP87 longitude is in units of 10^-8 radians
    error_arcsec = (sum_amplitudes / 1e8) * RAD_TO_ARCSEC
    
    return error_arcsec

def truncate_series_by_threshold(series_data: Dict[str, List[Tuple[float, float, float]]], 
                                threshold: Optional[float]) -> Tuple[Dict, float]:
    """
    Truncate series by amplitude threshold and compute error bound.
    
    Args:
        series_data: Dictionary of series data
        threshold: Minimum amplitude threshold (None for no truncation)
        
    Returns:
        Tuple of (truncated_series_data, conservative_error_arcsec)
    """
    if threshold is None:
        print("No truncation applied (full precision)")
        return series_data, 0.0
    
    print(f"Applying amplitude threshold: {threshold}")
    
    truncated_data = {}
    all_discarded_terms = []
    
    for series_name, terms in series_data.items():
        kept_terms = []
        discarded_terms = []
        
        for term in terms:
            A, B, C = term
            if abs(A) >= threshold:
                kept_terms.append(term)
            else:
                discarded_terms.append(term)
        
        truncated_data[series_name] = kept_terms
        
        # Only accumulate discarded longitude terms for error calculation
        if series_name.startswith('L'):
            all_discarded_terms.extend(discarded_terms)
        
        if discarded_terms:
            print(f"  {series_name}: kept {len(kept_terms)}, discarded {len(discarded_terms)}")
    
    error_bound = compute_conservative_error_bound(all_discarded_terms)
    print(f"Conservative error bound for longitude: {error_bound:.3f} arcseconds")
    
    return truncated_data, error_bound

def find_optimal_threshold(series_data: Dict[str, List[Tuple[float, float, float]]], 
                          target_arcsec: float) -> Optional[float]:
    """
    Find the smallest amplitude threshold that meets the target accuracy.
    
    Args:
        series_data: Dictionary of series data
        target_arcsec: Target accuracy in arcseconds
        
    Returns:
        Optimal threshold (None if full precision needed)
    """
    print(f"Finding optimal threshold for target accuracy: {target_arcsec} arcseconds")
    
    # Collect all longitude amplitudes and sort them
    longitude_amplitudes = []
    for series_name, terms in series_data.items():
        if series_name.startswith('L'):
            longitude_amplitudes.extend(abs(A) for A, B, C in terms)
    
    longitude_amplitudes.sort(reverse=True)  # Largest first
    
    if not longitude_amplitudes:
        print("No longitude terms found")
        return None
    
    # Test thresholds by trying different cut-off points
    print("Testing amplitude thresholds...")
    
    best_threshold = None
    
    # Try various threshold candidates
    candidates = []
    
    # Add some specific powers of 10
    for exp in range(-12, 2):  # 1e-12 to 1e1
        candidates.append(10**exp)
    
    # Add amplitudes from the series as candidates
    candidates.extend(longitude_amplitudes[::max(1, len(longitude_amplitudes)//20)])
    
    # Sort and deduplicate candidates
    candidates = sorted(set(candidates), reverse=True)
    
    for threshold in candidates:
        _, error_bound = truncate_series_by_threshold(series_data, threshold)
        
        print(f"  Threshold {threshold:.2e}: error {error_bound:.3f} arcsec")
        
        if error_bound <= target_arcsec:
            best_threshold = threshold
            break
    
    # Check if full precision is needed
    if best_threshold is None:
        _, full_error = truncate_series_by_threshold(series_data, None)
        if full_error <= target_arcsec:
            print(f"Full precision achieves target accuracy: {full_error:.3f} arcsec")
            return None
        else:
            print(f"Warning: Even full precision exceeds target ({full_error:.3f} > {target_arcsec} arcsec)")
            return None
    
    print(f"Selected threshold: {best_threshold:.2e}")
    return best_threshold

def generate_python_module(series_data: Dict[str, List[Tuple[float, float, float]]], 
                          threshold: Optional[float], error_bound: float, 
                          output_file: Path):
    """Generate Python module with VSOP87 coefficients."""
    
    print(f"Generating Python module: {output_file}")
    
    with open(output_file, 'w') as f:
        f.write('"""\n')
        f.write('VSOP87D Earth coefficients\n')
        f.write('Generated automatically from VSOP87D.EAR\n')
        f.write('\n')
        if threshold is not None:
            f.write(f'Amplitude threshold: {threshold:.2e}\n')
        else:
            f.write('Amplitude threshold: None (full precision)\n')
        f.write(f'Conservative error bound (longitude): {error_bound:.3f} arcseconds\n')
        f.write('\n')
        f.write('Each coefficient is a tuple (A, B, C) where the term contributes:\n')
        f.write('A * cos(B + C * t) to the series.\n')
        f.write('\n')
        f.write('Units:\n')
        f.write('- L (longitude): 10^-8 radians\n')
        f.write('- B (latitude): 10^-8 radians\n')
        f.write('- R (radius): 10^-8 AU\n')
        f.write('"""\n\n')
        
        f.write('import math\n\n')
        
        # Generate coefficient arrays
        for coord in ['L', 'B', 'R']:
            for power in range(6):
                series_name = f"{coord}{power}"
                terms = series_data.get(series_name, [])
                
                f.write(f"{series_name} = [\n")
                for A, B, C in terms:
                    f.write(f"    ({A}, {B}, {C}),\n")
                f.write("]\n\n")
        
        # Add the computation functions
        f.write('''def _sum(terms, t):
    """Sum a series of periodic terms."""
    return sum(A * math.cos(B + C * t) for A, B, C in terms)

def _eval(series, t):
    """Evaluate a VSOP87 series at time t."""
    return sum(_sum(group, t) * t**n for n, group in enumerate(series))

def _t(jd):
    """Convert Julian Day to VSOP87 time parameter (millennia since J2000.0)."""
    return (jd - 2451545.0) / 365250.0

def earth_heliocentric_longitude(t):
    """Earth heliocentric longitude (radians) at VSOP87 time t."""
    return (_eval([L0, L1, L2, L3, L4, L5], t) / 1e8) % (2 * math.pi)

def earth_heliocentric_latitude(t):
    """Earth heliocentric latitude (radians) at VSOP87 time t."""
    return _eval([B0, B1, B2, B3, B4, B5], t) / 1e8

def earth_radius_vector(t):
    """Earth radius vector (AU) at VSOP87 time t."""
    return _eval([R0, R1, R2, R3, R4, R5], t) / 1e8

def earth_heliocentric_position(jd):
    """Earth heliocentric position (L, B, R) at Julian Day jd."""
    t = _t(jd)
    return (
        earth_heliocentric_longitude(t),
        earth_heliocentric_latitude(t),
        earth_radius_vector(t),
    )

# Metadata
AMPLITUDE_THRESHOLD = {threshold}
CONSERVATIVE_ERROR_ARCSEC = {error_bound:.6f}
'''.format(threshold=repr(threshold), error_bound=error_bound))

def main():
    parser = argparse.ArgumentParser(description='Generate VSOP87D Earth coefficients')
    parser.add_argument('--threshold', type=float, 
                       help='Minimum amplitude threshold (use 0 for no truncation)')
    parser.add_argument('--auto-upgrade', action='store_true',
                       help='Automatically select optimal threshold')
    parser.add_argument('--target-arcsec', type=float, default=10.0,
                       help='Target accuracy in arcseconds for auto-upgrade mode')
    parser.add_argument('--output', type=str, 
                       help='Output Python module file')
    
    args = parser.parse_args()
    
    if args.auto_upgrade and args.threshold is not None:
        print("Error: Cannot use both --auto-upgrade and --threshold")
        sys.exit(1)
    
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Download VSOP87D file if needed
    download_vsop87d_file()
    
    # Parse the data file
    series_data = parse_vsop87d_file()
    
    # Determine threshold
    if args.auto_upgrade:
        threshold = find_optimal_threshold(series_data, args.target_arcsec)
    else:
        threshold = args.threshold
    
    # Truncate series and compute error
    truncated_data, error_bound = truncate_series_by_threshold(series_data, threshold)
    
    # Generate output file
    if args.output:
        output_file = Path(args.output)
    else:
        if threshold is None:
            suffix = "full"
        else:
            suffix = f"thresh_{threshold:.0e}"
        output_file = OUTPUT_DIR / f"vsop87d_earth_{suffix}.py"
    
    generate_python_module(truncated_data, threshold, error_bound, output_file)
    
    print("\nGeneration complete!")
    print(f"Output file: {output_file}")
    print(f"Error bound: {error_bound:.3f} arcseconds")

if __name__ == "__main__":
    main()
