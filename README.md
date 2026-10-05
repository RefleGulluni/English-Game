# English Game

Godot 4 project for **Mini Run Prototype 0.7 — Cemetery Biome MiniRun**.

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
- a seeded six-layer Cemetery route, weighted native pools, learning/rhythm/repetition Director and safe Layer 5 alternatives;
- Recover, Stabilize, and Press On decisions between encounters;
- seven Cemetery events, Rest, Elite and Relic opportunities, with three-choice rewards plus Skip;
- four core targets (MOURN, LINGER, CONCEAL, REASSEMBLE) and one compatible elastic word;
- Ghost, Veil Ghost, Grave Skeleton, Neglect Wraith, Mourning Wraith and the two-phase Mourning Keeper;
- encounter-local Grave Pressure, Bone Remains/reassembly and preserved 0.6 combat mechanics;
- debug-only DEV PANEL (button or F2): Seed, Layer, words, resources, Relics, enemy/event tests and Weight Inspector;
- keyboard shortcuts `1`–`9` for current hand positions and `Space`, plus full mouse control;
- headless combat and run-state smoke tests.

The ERODE/TOXIC evidence and card gates remain intact. The entry still offers their initial inference; Grave Skeleton's real ERODE and TOXIC DUST consequences can provide combat context in Cemetery, followed by their existing transfer/production exercises. Legacy Root/Veil/Iron Shell mechanics remain available for regression and DEV tests, not in the normal Cemetery random pool. The Lexicon preserves active decisions and Reaction windows. Learning can be skipped; wrong learning answers do not cost resources.

0.6 separates breaking Structure from killing: SHATTER breaks 8 Structure, while STRIKE deals 8 HP-directed damage and weakly breaks 2 Structure. Collapse applies two-turn EXPOSED (+2 STRIKE damage), not direct damage. Without Structure, SHATTER chips 2 Armor before 3 HP-directed damage. Armor absorbs ordinary direct damage. USABLE ERODE weakens Structure or Armor over three rounds without damaging HP; USABLE TOXIC applies three rounds of Armor-bypassing poison. Reapplications refresh one effect rather than stacking copies. ERODE → SHATTER, ERODE → STRIKE and TOXIC → STRIKE have discoverable combinations.

Ghost has no Structure, alternates into FADED, and resists poison; OBSERVE reveals it. Veil Ghost adds false intent. Grave Skeleton becomes Bone Remains at zero HP; SHATTER/STRIKE handle the remains and BIND delays reassembly. Mourning Wraith accumulates grief that worsens pressure. Normal Neglect Wraith still requires surviving five completed rounds, with temporary dispersal and reformation. The Mourning Keeper shifts at half HP from hidden-intent mourning to accelerated Grave Pressure.

UNFINISHED SENTENCE grants a second Retain slot without exempting consecutive retention. ECHO CHAMBER creates the first usable Word's temporary, cost-plus-one Exhaust copy each turn. IRON SCRIPT adds one EXPOSED turn instead of Collapse damage. CLEAR LENS and QUIET MIND remain available. DEFLECT requires both its hand card and sufficient Focus; it stays available until the enemy action resolves and is then discarded unless retained.

Targets and ERODE/TOXIC independently progress through ENCOUNTERED → RECOGNIZED → UNDERSTOOD → USABLE. Target words improve information and scene use; they do not add four undefined combat cards. The Director provides missing learning opportunities, never automatic evidence or correct answers. Recognition and Insight do not inflate damage or remove danger. Knowledge resets each Run; permanent Lexicon, additional Biomes, multi-enemy combat and formal art remain out of scope.

Combat STABILIZE now costs 1 Focus and reduces dominant Corruption by **8**. Breather Stabilize remains -12 and Stabilizer Supply remains -15.

## Run

Open `project.godot` in Godot 4.7 and run the project, or execute:

```sh
/Applications/Godot.app/Contents/MacOS/Godot --path .
```

Architecture and scope decisions are documented in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).
Knowledge evidence and UI behavior are documented in [`docs/KNOWLEDGE_LOOP.md`](docs/KNOWLEDGE_LOOP.md).
Deck rules, integration choices and 0.5 validation are documented in [`docs/SEMANTIC_DECK.md`](docs/SEMANTIC_DECK.md).
Inherited 0.6 combat rules are documented in [`docs/COMBAT_ECOLOGY.md`](docs/COMBAT_ECOLOGY.md).
Current Cemetery rules, provisional numbers, Seed reproduction and 0.7 validation are documented in [`docs/CEMETERY_0_7.md`](docs/CEMETERY_0_7.md).

## Verify

Run all eighteen smoke suites (stop the running game first):

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
