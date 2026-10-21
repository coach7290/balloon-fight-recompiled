# Prototype validation

Checked on 21 October 2026 on macOS arm64, Apple Clang 21.0.0, Python 3.12.14, CMake 3.31.10 and Ninja 1.13.2. The NESRecomp revision is `5a2eddeecc646e9325bef53f3c711e119423f99c`.

## Completed comparisons

All three scripted routes passed at CPU/PPU alignments 0, 1, 2 and 3. Each run completed 1,800 frames. Each alignment ran the compiled game, NESRecomp's interpreter-only mode, and the separate TriCNES reference implementation: 36 completed runs and 64,800 total frames across the comparison matrix.

| Route | Game state at frame 400 | Reference comparison | Interpreted ROM or RAM cycles in native runs |
| --- | --- | --- | --- |
| Normal play | Normal mode, demo flag zero, one player | Every frame matched at all four alignments | Zero |
| Balloon Trip | Trip mode, demo flag zero | Every frame matched at all four alignments | Zero |
| Two players | Normal mode, demo flag zero, two-player flag set | Every frame matched at all four alignments | Zero |

The reference comparison covers observable bus-trace hashes, memory/picture hashes, CPU registers and cycle counts after every frame. Native and interpreter-only runs additionally matched their internal hardware-state hashes. Those internal hashes are deliberately not compared to TriCNES because the implementations encode their internal state differently.

Balloon Trip initially reached 54 instruction addresses not discovered by the static analysis, causing 16,658 interpreter cycles in the first 1,800-frame profile. The committed address-only `tests/cycle-seeds.txt` supplies those locations to the next code-generation pass. The final runs above contained zero ROM/RAM interpreter cycles. The engine's printed percentage rounds small fallbacks to 100.0, so validation checks the integer fallback counts as well.

These are approximately 30-second routes through each selected mode. They establish startup and exercised gameplay behavior; they are not a complete-game or all-mechanics certification.

## Reproduce

After building with `-DBALLOON_FIGHT_ORACLE=ON`:

```sh
python3 -m unittest discover -s tests -v
python3 tools/verify_routes.py
python3 tools/audit_source.py
```

For an engine outside `.deps/nesrecomp`, pass `--engine /path/to/nesrecomp`. The detailed logs, RAM checkpoints, captures and machine-readable summary are written under ignored `reports/verification/`. The source repository includes only the input schedules and validation tooling, not captured game images or game data.

Six ROM-gate tests passed, covering malformed input, wrong game data, trainer/mapper mismatch, ambiguous ZIP input and reading an archive member without extracting its path. The supplied owner ROM also passed the real checksum gate.

## Remaining qualification

Physical keyboard/controller interaction, audible playback on real audio hardware, longer progression, bonus-phase coverage, save-state continuation, multiple host operating systems, and installation/update through Quiver remain to be tested. The current prototype lacks a first-run ROM picker and final release packaging. No catalog submission or release is claimed.

The optional TriCNES test target needs a Clang narrowing-diagnostic compatibility option and the cycle helper's paths at directory scope; the integration handles both without changing upstream engine sources.
