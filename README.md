# Balloon Fight Recompiled

An experimental NESRecomp integration for **Balloon Fight (USA)**. The first milestone is a reproducible native build with recorded validation of normal play and Balloon Trip. This is a static recompilation project, not a matching C decompilation. It is not yet a finished Quiver release.

No ROM, extracted graphics/audio, or generated game code belongs in this repository. Users provide the supported game image locally. The tools compare the game payload rather than the filename or header metadata.

## Build the prototype

Prerequisites: Python 3.11+, Git, CMake 3.20+, Ninja (or another CMake generator), a C11/C++ compiler, and SDL2 development files for a windowed build. The engine is pinned in `dependencies.json`.

```sh
python3 tools/bootstrap.py
python3 tools/prepare_rom.py "/path/to/your/Balloon Fight.zip"
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build
./build/balloon_fight private/balloon-fight-usa.nes
```

`prepare_rom.py` also accepts a `.nes` image. It writes a verified copy into git-ignored `private/`, normalizes only the 16-byte container header, and leaves the input file unchanged. Other regions and modified game payloads are rejected.

For a headless build add `-DBALLOON_FIGHT_HEADLESS=ON`. `-DNESRECOMP_ROOT=/path/to/pinned/nesrecomp` uses an existing engine checkout. Add `-DBALLOON_FIGHT_ORACLE=ON` to build the engine's separate TriCNES-based comparison executable.

Generated C and binaries stay under the ignored build directory. ROM-derived executables and captures are local development artifacts; do not upload them as releases until the distribution model has been reviewed.

## Validation

Validation routes, comparisons and remaining defects will be recorded in `docs/validation.md`. Successful compilation or a title screen does not establish full-game correctness. Interpreter fallback must be measured and disclosed.

## Attribution and licensing

The runtime and translator are [NESRecomp](https://github.com/mstan/nesrecomp), licensed under PolyForm Noncommercial 1.0.0 at the pinned revision. Game integration and project scripts are separate from that dependency; see `LICENSE` and `THIRD_PARTY.md`. Nintendo's game content is not covered by the integration license.

The [annotated Balloon Fight disassembly](https://github.com/LuigiBlood/balloonfight_dis) is a research reference. No assembly source from it is copied into this repository. The initial integration, scripts and tests were primarily generated with Codex. Validation claims describe checks actually performed, not an assumption that generated code works.

## Quiver

Intended project name: Balloon Fight Recompiled. Submit through [Quiver's website](https://quiverlauncher.com/submit) after installable releases have been tested. No listing or endorsement is claimed.
