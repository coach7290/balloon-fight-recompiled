#!/usr/bin/env python3
"""Launch the local prototype with its verified private ROM."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--build", type=Path, default=ROOT / "build")
    args = ap.parse_args()
    exe = args.build.resolve() / ("balloon_fight.exe" if sys.platform == "win32" else "balloon_fight")
    if not exe.exists():
        ap.error("Prototype binary missing; follow the README build steps first.")
    rom = ROOT / "private/balloon-fight-usa.nes"
    subprocess.run([sys.executable, str(ROOT / "tools/prepare_rom.py"), str(rom), "--check"], check=True)
    return subprocess.call([str(exe), str(rom)], cwd=ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
