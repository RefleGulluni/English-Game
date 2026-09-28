# English Game

Godot 4 project for **Combat Prototype 0.1**.

The design documents in the Obsidian `English Game` folder are read-only references. Runtime code, scenes, tests, and game assets live here.

## Playable prototype

The project now launches directly into the combat prototype and includes:

- OBSERVE, SHATTER, BIND, DEFLECT, STABILIZE, and RESTORE;
- 3 Focus per turn with a 1 Focus carry limit;
- Obscured, Partial, and Clear Enemy Intent;
- Physical damage, Armor, three Corruption families, Status, and Reaction;
- Root Husk, Veil Moth, Neglect Wraith, and Fractured Husk encounters;
- keyboard shortcuts `1`–`6` and `Space`, plus full mouse control;
- a headless combat-state smoke test.

## Run

Open `project.godot` in Godot 4.7 and run the project, or execute:

```sh
/Applications/Godot.app/Contents/MacOS/Godot --path .
```

Architecture and scope decisions are documented in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).
