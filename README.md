# English Game

Godot 4 project for **Mini Run Prototype 0.5 — Semantic Deck & Combat Identity**.

The design documents in the Obsidian `English Game` folder are read-only references. Runtime code, scenes, tests, and game assets live here.

## Playable prototype

The project now launches into a complete short Roguelite run and includes:

- a ten-card deck: SHATTER ×2, OBSERVE ×2, BIND ×2, STABILIZE, DEFLECT, RESTORE, ERODE;
- five-card hands, draw/discard/exhaust piles and automatic reshuffling;
- a once-per-combat opening Mulligan (up to two cards) and one free Retain slot;
- 3 Focus per turn with a 1 Focus carry limit;
- Obscured, Partial, and Clear Enemy Intent;
- Physical damage, Armor, three Corruption families, Status, and Reaction;
- HP and Corruption persistence, 30% Armor rebuilding, and post-combat Breathers;
- a fixed four-layer route with Encounter, Event, Cache, Elite, Extract, and Final nodes;
- Recover, Stabilize, and Press On decisions between encounters;
- three hand-authored events, an optional Semantic Anomaly, and five Relics;
- Root Husk, Veil Moth, Neglect Wraith, Elite Neglect Wraith, and Fractured Husk encounters;
- keyboard shortcuts `1`–`9` for current hand positions and `Space`, plus full mouse control;
- headless combat and run-state smoke tests.

The 0.4 ERODE learning loop remains intact: enter the Fracture, infer meaning from the Eroded Inscription, connect ERODE to Root Husk's combat effects, then complete the water/stone and river/cliff challenges after Veil Moth. The Lexicon button preserves active decisions and Reaction windows. Learning can be skipped; wrong answers do not cost resources.

0.5 unlocks ERODE as a Semantic Modifier at USABLE: 1 Focus, three turns of gradual Structure erosion, then Armor erosion when exposed; never direct HP damage. Playing ERODE before SHATTER in the same turn discovers **Fractured Erosion**. Unknown ERODE remains a non-playable context card. Root Husk gains REGROWTH and SPLINTER RESPONSE; Veil Moth gains FALSE INTENT; Neglect Wraith degrades Reaction information with Inattention. The normal Wraith encounter now requires surviving five completed turns instead of a kill.

UNFINISHED SENTENCE grants a second Retain slot; ECHO CHAMBER creates the first usable Word's temporary, cost-plus-one Exhaust copy each turn. CLEAR LENS, QUIET MIND, and IRON SCRIPT remain available. DEFLECT requires both its hand card and sufficient Focus; it stays available until the enemy action resolves and is then discarded unless retained.

ERODE progresses through ENCOUNTERED → RECOGNIZED → UNDERSTOOD → USABLE. Recognition improves ERODE Intent clarity; ERODE Insight predicts Decay-related structural weakening without changing combat damage or immunity. Knowledge lasts for the current Run and resets with Restart Run. Long-term saves and review are outside this prototype.

Combat STABILIZE now costs 1 Focus and reduces dominant Corruption by **8**. Breather Stabilize remains -12 and Stabilizer Supply remains -15.

## Run

Open `project.godot` in Godot 4.7 and run the project, or execute:

```sh
/Applications/Godot.app/Contents/MacOS/Godot --path .
```

Architecture and scope decisions are documented in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).
Knowledge evidence and UI behavior are documented in [`docs/KNOWLEDGE_LOOP.md`](docs/KNOWLEDGE_LOOP.md).
Deck rules, integration choices and 0.5 validation are documented in [`docs/SEMANTIC_DECK.md`](docs/SEMANTIC_DECK.md).

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

/Applications/Godot.app/Contents/MacOS/Godot \
  --headless --path . \
  --script res://tests/semantic_deck_smoke.gd

/Applications/Godot.app/Contents/MacOS/Godot \
  --headless --path . \
  --script res://tests/semantic_ui_smoke.gd

/Applications/Godot.app/Contents/MacOS/Godot \
  --headless --path . \
  --script res://tests/playthrough_smoke.gd
```
