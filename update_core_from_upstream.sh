#!/bin/bash
# Skripta za automatsko preuzimanje i zamenu core fajlova iz Astronomical-watch repozitorijuma
# Pokreni iz root foldera Astronomical-watch-web

set -e

UPSTREAM_REPO="https://github.com/NndMlc/Astronomical-watch.git"
UPSTREAM_DIR="/tmp/astronomical-watch-upstream"
TARGET_CORE_DIR="backend/src/astronomical_watch/core"

# 1. Kloniraj ili ažuriraj upstream repo
if [ -d "$UPSTREAM_DIR" ]; then
    echo "[INFO] Ažuriram postojeći upstream repo..."
    cd "$UPSTREAM_DIR"
    git pull
else
    echo "[INFO] Kloniram upstream repo..."
    git clone "$UPSTREAM_REPO" "$UPSTREAM_DIR"
    cd "$UPSTREAM_DIR"
fi

# 2. Prekopiraj core fajlove
CORE_FILES=(
    "__init__.py"
    "solar.py"
    "equinox.py"
    "timeframe.py"
    "timebase.py"
    "vsop87_earth.py"
    "nutation.py"
    "frames.py"
    "delta_t.py"
    "astro_time_core.py"
)

SRC_CORE_DIR="$UPSTREAM_DIR/src/astronomical_watch/core"

if [ ! -d "$SRC_CORE_DIR" ]; then
    echo "[ERROR] Ne postoji core folder u upstream repou!"
    exit 1
fi

for f in "${CORE_FILES[@]}"; do
    if [ -f "$SRC_CORE_DIR/$f" ]; then
        cp -v "$SRC_CORE_DIR/$f" "$OLDPWD/$TARGET_CORE_DIR/"
    else
        echo "[WARNING] Fajl $f ne postoji u upstream core folderu!"
    fi
done

echo "[INFO] Core fajlovi su ažurirani. Proveri kompatibilnost i pokreni backend."
