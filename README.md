# English Game

Godot 4 project for **Mini Run Prototype 0.4 — Knowledge Loop**.

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

0.4 adds one complete ERODE learning loop: enter the Fracture, infer meaning from the Eroded Inscription, choose Root Husk, connect ERODE to its combat effects, then complete a new water/stone context and a river/cliff production challenge after the Breather. The Lexicon button shows word state and evidence without losing the active choice or Reaction window. Learning can be skipped; wrong answers do not cost resources.

ERODE progresses through ENCOUNTERED → RECOGNIZED → UNDERSTOOD → USABLE. Recognition improves ERODE Intent clarity; ERODE Insight predicts Decay-related structural weakening without changing combat damage or immunity. Knowledge lasts for the current Run and resets with Restart Run. Long-term saves and review are outside this prototype.

Combat STABILIZE now costs 1 Focus and reduces dominant Corruption by **8**. Breather Stabilize remains -12 and Stabilizer Supply remains -15.

## Run

Open `project.godot` in Godot 4.7 and run the project, or execute:

```sh
/Applications/Godot.app/Contents/MacOS/Godot --path .
```

Architecture and scope decisions are documented in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).
Knowledge evidence and UI behavior are documented in [`docs/KNOWLEDGE_LOOP.md`](docs/KNOWLEDGE_LOOP.md).

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

/Applications/Godot.app/Contents/MacOS/Godot \
  --headless --path . \
  --script res://tests/knowledge_loop_smoke.gd

/Applications/Godot.app/Contents/MacOS/Godot \
  --headless --path . \
  --script res://tests/knowledge_ui_smoke.gd
```
