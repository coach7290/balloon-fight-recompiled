#!/usr/bin/env python3
"""Reject private game inputs and generated artifacts in Git's tracked file list."""
from pathlib import Path, PurePosixPath
import subprocess

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_DIRS = {"private", "captures", "reports", ".deps", "__pycache__"}
FORBIDDEN_SUFFIXES = {".nes", ".fds", ".chr", ".rom", ".zip", ".sav", ".cycstate", ".wav", ".png", ".jpg", ".exe", ".dylib", ".o", ".frames"}


def main():
    files = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
    bad = []
    for name in filter(None, files):
        path = PurePosixPath(name)
        if (any(part in FORBIDDEN_DIRS or part.startswith("build") for part in path.parts)
                or path.suffix.lower() in FORBIDDEN_SUFFIXES
                or path.name.startswith("game_cyc")):
            bad.append(name)
    if bad:
        raise SystemExit("Refusing source publication; forbidden tracked files:\n" + "\n".join(bad))
    print(f"Source audit passed: {len(list(filter(None, files)))} tracked source/documentation files; no forbidden artifact paths.")


if __name__ == "__main__":
    main()
