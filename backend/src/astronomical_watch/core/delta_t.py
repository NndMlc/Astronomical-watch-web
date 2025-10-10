"""
Piecewise ΔT model (Espenak & Meeus, trunkirani primer).
Ulaz: decimalna godina (npr. 2024.5)
Izlaz: ΔT u sekundama.
"""
def delta_t_seconds(year: float) -> float:
    y = year
    if y < 948:
        t = (y - 2000) / 100
        return 2177 + 497*t + 44.1*t*t
    if 948 <= y < 1600:
        t = (y - 2000) / 100
        return 102 + 102*t + 25.3*t*t
    if 1600 <= y < 2000:
        t = (y - 2000) / 100
        return 102 + 102*t + 25.3*t*t
    if 2000 <= y < 2100:
        t = y - 2000
        return 62.92 + 0.32217*t + 0.005589*t*t
    if 2100 <= y:
        u = (y - 1820) / 100
        return -20 + 32*u*u
    return 0.0
