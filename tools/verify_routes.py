#!/usr/bin/env python3
"""Compare scripted player-controlled routes against the pinned engine's oracle."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ROUTES = {"normal": (0, 0), "balloon_trip": (1, 0), "two_player": (0, 1)}


def snapshot_ram(path):
    data = path.read_bytes()
    if data[:8] != b"CYCFRAME" or struct.unpack_from("<I", data, 8)[0] != 2:
        raise RuntimeError("Unexpected engine frame-log format")
    header = struct.unpack_from("<9I", data, 12)
    if header[0] != 400 or header[3] != 2048:
        raise RuntimeError("Expected the complete CPU RAM snapshot at frame 400")
    return data[336:2384]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--build", type=Path, default=ROOT / "build")
    ap.add_argument("--engine", type=Path, default=ROOT / ".deps/nesrecomp")
    ap.add_argument("--frames", type=int, default=1800)
    ap.add_argument("--jobs", type=int, default=4)
    args = ap.parse_args()
    if args.frames < 401:
        ap.error("--frames must be at least 401 for the gameplay checkpoint")
    engine, build = args.engine.resolve(), args.build.resolve()
    ext = ".exe" if sys.platform == "win32" else ""
    exe, oracle = build / ("balloon_fight" + ext), build / ("balloon_fight_oracle" + ext)
    if not exe.exists() or not oracle.exists():
        ap.error("Build with -DBALLOON_FIGHT_ORACLE=ON first; pass its binary directory with --build")
    report_dir = ROOT / "reports/verification"
    report_dir.mkdir(parents=True, exist_ok=True)
    rom = ROOT / "private/balloon-fight-usa.nes"
    summary = {"frames_per_run": args.frames, "alignments": [0, 1, 2, 3],
               "engine_commit": json.loads((ROOT / "dependencies.json").read_text())["nesrecomp"]["commit"],
               "routes": {}}
    for name, (mode, players) in ROUTES.items():
        print(f"Checking {name}: {args.frames} frames at four alignments", flush=True)
        route = ROOT / f"tests/routes/{name}.txt"
        out = report_dir / name
        out.mkdir(exist_ok=True)
        command = [sys.executable, str(engine / "tools/cyc/cyc_verify.py"),
                   "--exe", str(exe), "--oracle", str(oracle), "--rom", str(rom),
                   "--input", str(route), "--frames", str(args.frames),
                   "--interp", "--jobs", str(args.jobs), "--out", str(out)]
        process = subprocess.run(command, capture_output=True, text=True)
        (out / "comparison.log").write_text(process.stdout + process.stderr)
        print(process.stdout, end="", flush=True)
        if process.returncode:
            raise RuntimeError(f"Reference comparison failed for {name}: see {out / 'comparison.log'}")
        for log in out.glob("*_native.txt.log"):
            text = log.read_text()
            match = re.search(r"interpreted: ROM (\d+).*RAM (\d+)", text)
            if not match or tuple(map(int, match.groups())) != (0, 0):
                raise RuntimeError(f"Interpreter fallback remains in {log}")
        checkpoint = out / "checkpoint.frames"
        subprocess.run([str(exe), str(rom), "--frames", "401", "--input", str(route),
                        "--frame-log", str(checkpoint), "--frame-log-frames", "400:400",
                        "--screenshot", str(out / "checkpoint.png")], check=True, capture_output=True)
        ram = snapshot_ram(checkpoint)
        state = {"game_mode": ram[0x16], "demo_flag": ram[0x3A], "two_player": ram[0x40]}
        if (state["game_mode"], state["two_player"], state["demo_flag"]) != (mode, players, 0):
            raise RuntimeError(f"{name} did not enter the intended player-controlled mode: {state}")
        summary["routes"][name] = {"comparison": "all match", "rom_fallback_cycles": 0,
                                    "ram_fallback_cycles": 0, "checkpoint": state,
                                    "input_sha256": hashlib.sha256(route.read_bytes()).hexdigest()}
        (report_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(f"PASS: {len(ROUTES) * 12} completed runs; see {report_dir / 'summary.json'}", flush=True)


if __name__ == "__main__":
    main()
