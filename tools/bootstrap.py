#!/usr/bin/env python3
"""Fetch the public engine at the exact revision in dependencies.json."""
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    pin = json.loads((ROOT / "dependencies.json").read_text())["nesrecomp"]
    dest = ROOT / ".deps" / "nesrecomp"
    if not dest.exists():
        dest.parent.mkdir(exist_ok=True)
        subprocess.run(["git", "clone", "--no-checkout", "--filter=blob:none",
                        pin["repository"], str(dest)], check=True)
        subprocess.run(["git", "-C", str(dest), "checkout", "--detach", pin["commit"]], check=True)
    actual = subprocess.check_output(["git", "-C", str(dest), "rev-parse", "HEAD"], text=True).strip()
    dirty = subprocess.check_output(["git", "-C", str(dest), "status", "--porcelain"], text=True).strip()
    if actual != pin["commit"] or dirty:
        raise SystemExit("Existing engine checkout differs from the pin or has local changes; left untouched.")
    print(f"NESRecomp pinned at {actual}")


if __name__ == "__main__":
    main()
