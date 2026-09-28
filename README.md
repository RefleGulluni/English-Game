# English Game

Godot 4 project for **Mini Run Prototype 0.3**.

The design documents in the Obsidian `English Game` folder are read-only references. Runtime code, scenes, tests, and game assets live here.

## Playable prototype

The project now launches into a complete short Roguelite run and includes:

- OBSERVE, SHATTER, BIND, DEFLECT, STABILIZE, and RESTORE;
- 3 Focus per turn with a 1 Focus carry limit;
- Obscured, Partial, and Clear Enemy Intent;
- Physical damage, Armor, three Corruption families, Status, and Reaction;
- HP and Corruption persistence, 30% Armor rebuilding, and post-combat Breathers;
- a fixed four-layer route with Encounter, Event, Cache, Elite, Extract, and Final nodes;
- Recover, Stabilize, and Press On decisions between encounters;
- three hand-authored events and three Prototype Relics;
- Root Husk, Veil Moth, Neglect Wraith, Elite Neglect Wraith, and Fractured Husk encounters;
- keyboard shortcuts `1`–`6` and `Space`, plus full mouse control;
- headless combat and run-state smoke tests.

## Run

Open `project.godot` in Godot 4.7 and run the project, or execute:

```sh
/Applications/Godot.app/Contents/MacOS/Godot --path .
```

Architecture and scope decisions are documented in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Verify

```sh
/Applications/Godot.app/Contents/MacOS/Godot \
  --headless --path . \
  --script res://tests/combat_state_smoke.gd

/Applications/Godot.app/Contents/MacOS/Godot \
  --headless --path . \
  --script res://tests/run_state_smoke.gd

/Applications/Godot.app/Contents/MacOS/Godot \
  --headless --path . \
  --script res://tests/ui_flow_smoke.gd
```
