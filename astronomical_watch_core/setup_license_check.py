"""
Ovaj skript se poziva iz setup.py pre instalacije, kako bi korisnik eksplicitno prihvatio LICENSE.CORE
"""
import sys
from accept_license import show_license, require_acceptance

if __name__ == "__main__":
    show_license()
    require_acceptance()
