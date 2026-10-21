#!/usr/bin/env python3
"""Validate owner-supplied USA game data; never download or publish a ROM."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile

PAYLOAD_SHA256 = "7328b2eb1c9fe06b98e0cba5c9058bf026e06a94900d490f79436d714eb48d6b"
HEADER = bytes.fromhex("4e45531a010100000000000000000000")
ROOT = Path(__file__).resolve().parents[1]


def read_input(path):
    if path.suffix.lower() != ".zip":
        if path.stat().st_size != 24592:
            raise ValueError("Expected a 24,592-byte USA NES cartridge image.")
        return path.read_bytes()
    with zipfile.ZipFile(path) as archive:
        candidates = [item for item in archive.infolist()
                      if not item.is_dir() and item.filename.lower().endswith(".nes")
                      and not item.filename.startswith("__MACOSX/")]
        if len(candidates) != 1:
            raise ValueError("ZIP must contain exactly one NES image.")
        if candidates[0].file_size != 24592:
            raise ValueError("ZIP entry is not the expected 24,592-byte cartridge image.")
        return archive.read(candidates[0])


def validate(data):
    if len(data) != 24592 or data[:4] != b"NES\x1a":
        raise ValueError("Expected an iNES/NES 2.0 image of the supported size.")
    h = data[:16]
    if h[4:7] != b"\x01\x01\x00" or (h[7] & 0xF3):
        raise ValueError("Expected mapper 0, horizontal mirroring, no trainer, and 16 KiB PRG / 8 KiB CHR.")
    if (h[7] & 0x0C) not in (0, 8):
        raise ValueError("Unrecognized NES header format.")
    if (h[7] & 0x0C) == 8 and (h[8] or h[9]):
        raise ValueError("Unexpected NES 2.0 mapper/submapper or extended ROM size.")
    payload = data[16:]
    if hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA256:
        raise ValueError("Game data does not match supported Balloon Fight (USA). Patches and other regions are not supported.")
    return HEADER + payload


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input", type=Path, help="Your local .nes or ZIP file")
    ap.add_argument("--check", action="store_true", help="Validate only, without writing")
    args = ap.parse_args()
    try:
        original = read_input(args.input)
        normalized = validate(original)
        if not args.check:
            folder = ROOT / "private"
            folder.mkdir(exist_ok=True)
            target = folder / "balloon-fight-usa.nes"
            if target.exists() and target.read_bytes() != normalized:
                raise ValueError("Refusing to overwrite a different file at the prepared ROM path.")
            target.write_bytes(normalized)
            (folder / "rom-identity.json").write_text(json.dumps({
                "title": "Balloon Fight (USA)", "mapper": 0,
                "payload_sha256": PAYLOAD_SHA256,
                "input_sha256": hashlib.sha256(original).hexdigest(),
                "prepared_sha256": hashlib.sha256(normalized).hexdigest(),
                "header_normalized": original[:16] != HEADER,
            }, indent=2) + "\n")
            print("Prepared private/balloon-fight-usa.nes (git-ignored).")
        print("Verified Balloon Fight (USA): 16 KiB PRG, 8 KiB CHR, mapper 0.")
    except (OSError, ValueError, zipfile.BadZipFile, RuntimeError) as error:
        print(f"ROM verification failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
