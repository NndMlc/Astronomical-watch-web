"""
CLI skripta za eksplicitno prihvatanje LICENSE.CORE
"""
import sys

LICENSE_FILE = "LICENSE.CORE"


def show_license():
    try:
        with open(LICENSE_FILE, "r", encoding="utf-8") as f:
            print(f.read())
    except Exception as e:
        print(f"Could not read license file: {e}")
        sys.exit(1)

def require_acceptance():
    print("\nYou must accept the LICENSE.CORE to use this software.")
    print("Type 'I ACCEPT' (case sensitive) to continue:")
    resp = input()
    if resp.strip() != 'I ACCEPT':
        print("License not accepted. Exiting.")
        sys.exit(1)
    print("License accepted. You may proceed.")

if __name__ == "__main__":
    show_license()
    require_acceptance()
