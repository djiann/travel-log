#!/usr/bin/env python3
"""Sync all guide HTML variants from tokyo-2026-guide-light.html."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

SCRIPTS = (
    "build-dark-guide.py",
    "build-mobile-guide.py",
)


def main() -> None:
    gmaps = ROOT / "add-gmaps.py"
    if gmaps.exists():
        print("Running add-gmaps.py...")
        subprocess.run([sys.executable, str(gmaps)], check=True)
    for name in SCRIPTS:
        path = ROOT / name
        print(f"Running {name}...")
        subprocess.run([sys.executable, str(path)], check=True)
    print("Done: tokyo-2026-guide.html + tokyo-2026-guide-mobile.html synced from light.")


if __name__ == "__main__":
    main()
