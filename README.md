# English Game

Godot 4 project for **Mini Run Prototype 0.6 — Combat Ecology & Strategic Diversity**.

The design documents in the Obsidian `English Game` folder are read-only references. Runtime code, scenes, tests, and game assets live here.

## Playable prototype

The project now launches into a complete short Roguelite run and includes:

- a twelve-card deck: SHATTER, STRIKE ×2, OBSERVE ×2, BIND ×2, STABILIZE, DEFLECT, RESTORE, ERODE, TOXIC;
- five-card hands, draw/discard/exhaust piles and automatic reshuffling;
- a once-per-combat opening Mulligan (up to two cards) and one free Retain slot; the same instance cannot be retained on consecutive turns;
- 3 Focus per turn with a 1 Focus carry limit;
- Obscured, Partial, and Clear Enemy Intent;
- Physical damage, Armor, three Corruption families, Status, and Reaction;
- HP and Corruption persistence, 30% Armor rebuilding, and post-combat Breathers;
- a fixed four-layer route with Encounter, Event, Cache, Elite, Extract, and Final nodes;
- Recover, Stabilize, and Press On decisions between encounters;
- three hand-authored events, an optional Semantic Anomaly, and five Relics;
- Root Husk, Veil Moth, Neglect Wraith, Elite Neglect Wraith, and Fractured Husk encounters, plus optional Iron Shell and Ghost tests;
- keyboard shortcuts `1`–`9` for current hand positions and `Space`, plus full mouse control;
- headless combat and run-state smoke tests.

The 0.4 ERODE learning loop remains intact: enter the Fracture, infer meaning from the Eroded Inscription, connect ERODE to Root Husk's combat effects, then complete the water/stone and river/cliff challenges after Veil Moth. The Lexicon button preserves active decisions and Reaction windows. Learning can be skipped; wrong answers do not cost resources.

0.6 separates breaking Structure from killing: SHATTER breaks 8 Structure, while STRIKE deals 8 HP-directed damage and weakly breaks 2 Structure. Collapse applies two-turn EXPOSED (+2 STRIKE damage), not direct damage. Without Structure, SHATTER chips 2 Armor before 3 HP-directed damage. Armor absorbs ordinary direct damage. USABLE ERODE weakens Structure or Armor over three rounds without damaging HP; USABLE TOXIC applies three rounds of Armor-bypassing poison. Reapplications refresh one effect rather than stacking copies. ERODE → SHATTER, ERODE → STRIKE and TOXIC → STRIKE have discoverable combinations.

Root Husk retains REGROWTH and SPLINTER RESPONSE; Veil Moth retains FALSE INTENT. Iron Shell has high Armor and periodic capped reinforcement. Ghost has no Structure, alternates into FADED, and resists poison; OBSERVE reveals it. Normal Wraith requires surviving five completed rounds: reducing it to zero temporarily disperses it, then it reforms at full HP next turn. Elite and final encounters retain kill objectives.

UNFINISHED SENTENCE grants a second Retain slot without exempting consecutive retention. ECHO CHAMBER creates the first usable Word's temporary, cost-plus-one Exhaust copy each turn. IRON SCRIPT adds one EXPOSED turn instead of Collapse damage. CLEAR LENS and QUIET MIND remain available. DEFLECT requires both its hand card and sufficient Focus; it stays available until the enemy action resolves and is then discarded unless retained.

ERODE and TOXIC independently progress through ENCOUNTERED → RECOGNIZED → UNDERSTOOD → USABLE. TOXIC begins with the cracked vial; experiencing Iron Shell's actual poison consequence unlocks transfer and production exercises during combat. Recognition and Insight improve information, not damage or immunity. Knowledge lasts for the current Run and resets with Restart Run. Long-term saves and review are outside this prototype.

Combat STABILIZE now costs 1 Focus and reduces dominant Corruption by **8**. Breather Stabilize remains -12 and Stabilizer Supply remains -15.

## Run

Open `project.godot` in Godot 4.7 and run the project, or execute:

```sh
/Applications/Godot.app/Contents/MacOS/Godot --path .
```

Architecture and scope decisions are documented in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).
Knowledge evidence and UI behavior are documented in [`docs/KNOWLEDGE_LOOP.md`](docs/KNOWLEDGE_LOOP.md).
Deck rules, integration choices and 0.5 validation are documented in [`docs/SEMANTIC_DECK.md`](docs/SEMANTIC_DECK.md).
Current rules, approved design choices and 0.6 validation are documented in [`docs/COMBAT_ECOLOGY.md`](docs/COMBAT_ECOLOGY.md); these supersede historical 0.5 differences.

## Verify

Run all fourteen smoke suites (stop the editor's running game first):

```sh
for test in tests/*_smoke.gd; do
  /Applications/Godot.app/Contents/MacOS/Godot --headless --path . --script "res://$test"
done
```

Each suite must print its PASS marker without script/runtime errors. Automated correctness is not a guarantee of balanced or enjoyable play.

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
