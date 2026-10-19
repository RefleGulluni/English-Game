# English Game

Godot 4 project. Current entry: **0.9 Milestone 01 — Broken Graveyard Vertical Slice**, not the entire 0.9 release.

Run the project, move with WASD/arrows, approach the gate and press **E** to ENTER. Approach the Skeleton, confirm the opening hand, then use the existing Word Actions/Retain/Reaction system. First collapse gives 15 automatic Echo and rolls a real world object. Bone Remains have 10 Integrity and reassemble after **3 completed rounds**; clearing them grants another 5 Echo and restores movement. Walk to a dropped object and press **E** to PICK UP. **L** opens the permission-safe Lexicon; **Tab** opens the Run Bag. **R** replays after victory/defeat. **F2** offers forced-drop acceptance mode and ordinary 10% mode.

First-delivery debug acceptance mode intentionally forces Weathered Chisel; ordinary mode uses 10%. Chisel is collected into Run State only, with no invented combat effect. All art and sound remain placeholders/empty hooks. The old 0.8 screen is preserved at `scenes/ui/legacy_combat.tscn` for regression, not used as the new combat page. This slice stays in one moving 2D world throughout combat.

See [`docs/BROKEN_GRAVEYARD_M01.md`](docs/BROKEN_GRAVEYARD_M01.md) for delivery scope, temporary values, known limitations and QA, and [`docs/ART_CODE_CONTRACT_0_9.md`](docs/ART_CODE_CONTRACT_0_9.md) for art ownership and integration slots. Until this slice is accepted, do not expand to the other six Cemetery scenes, Keeper or prologue.

## Historical 0.8 systems retained

**Mini Run Prototype 0.8 — Pacing & Director Update** remains available in its legacy scene and tests.

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
- a seeded six-layer Cemetery route with three ordinary choices, functional tags, risk-floor lookahead and mandatory pre-Boss Recovery;
- selective REST, CALM, REPAIR or PREPARE recovery; post-combat settlement is automatic and is not another map encounter;
- native world scenes, layered Black Mist Well danger, Rest, Elite and three-choice Relic rewards plus Skip;
- a 5–8-sense active learning pool (QA default six), cross-run knowledge/scheduling and four learning pace preferences;
- Ghost, Veil Ghost, Grave Skeleton, Neglect Wraith, Mourning Wraith and the two-phase Mourning Keeper;
- encounter-local Grave Pressure, Bone Remains/reassembly and preserved 0.6 combat mechanics;
- debug-only DEV PANEL (button or F2): Seed, Layer, words, resources, Relics, enemy/event tests, timeline and Map/Learning/Weight inspectors;
- keyboard shortcuts `1`–`9` for current hand positions and `Space`, plus full mouse control;
- headless combat and run-state smoke tests.

The ERODE/TOXIC evidence and card gates remain intact, but their learning now follows the same encounter boundaries and spacing as other senses. Grave Skeleton's actual consequences can supply eligible primary context; recognition and production happen in native world scenes, never as nested Combat learning events. Legacy Root/Veil/Iron Shell mechanics remain available for regression and DEV tests, not in the normal Cemetery pool. The Lexicon preserves active decisions and Reaction windows. Learning can be skipped; wrong answers receive natural corrective context without resource costs or immediate retry loops.

0.6 separates breaking Structure from killing: SHATTER breaks 8 Structure, while STRIKE deals 8 HP-directed damage and weakly breaks 2 Structure. Collapse applies two-turn EXPOSED (+2 STRIKE damage), not direct damage. Without Structure, SHATTER chips 2 Armor before 3 HP-directed damage. Armor absorbs ordinary direct damage. USABLE ERODE weakens Structure or Armor over three rounds without damaging HP; USABLE TOXIC applies three rounds of Armor-bypassing poison. Reapplications refresh one effect rather than stacking copies. ERODE → SHATTER, ERODE → STRIKE and TOXIC → STRIKE have discoverable combinations.

Ghost has no Structure, alternates into FADED, and resists poison; OBSERVE reveals it. Veil Ghost adds false intent. Grave Skeleton becomes Bone Remains at zero HP; SHATTER/STRIKE handle the remains and BIND delays reassembly. Mourning Wraith accumulates grief that worsens pressure. Normal Neglect Wraith still requires surviving five completed rounds, with temporary dispersal and reformation. The Mourning Keeper shifts at half HP from hidden-intent mourning to accelerated Grave Pressure.

UNFINISHED SENTENCE grants a second Retain slot without exempting consecutive retention. ECHO CHAMBER creates the first usable Word's temporary, cost-plus-one Exhaust copy each turn. IRON SCRIPT adds one EXPOSED turn instead of Collapse damage. CLEAR LENS and QUIET MIND remain available. DEFLECT requires both its hand card and sufficient Focus; it stays available until the enemy action resolves and is then discarded unless retained.

Senses independently progress through ENCOUNTERED → RECOGNIZED → UNDERSTOOD → USABLE. Ambient appearance never grants earned stages. One Encounter has at most one major focus and advances at most one earned stage; two intervening complete Encounters are required before that sense becomes eligible again. Familiarity may decay, but earned knowledge never decays. Learning streaks are capped at two, and the second opportunity is genuinely less likely. Target words improve information and scene use; they do not add four undefined combat cards. The old 0.7 all-words-in-one-event learning guarantee is intentionally removed. Additional Biomes, multi-enemy combat and formal art remain out of scope.

Knowledge and scheduling save locally to Godot's `user://learning_schedule_0_8.json`, with recoverable previous-state backups. Invalid saves are preserved and put into read-only protection. DEV mutations enter a non-saving sandbox: relaunch the game to return to the real saved Lexicon. All undefined balance numbers are provisional, configurable QA baselines in `scripts/run/pacing_config.gd`.

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
Current Director rules, persistence, interpretation decisions and QA mapping are documented in [`docs/PACING_0_8.md`](docs/PACING_0_8.md). [`docs/CEMETERY_0_7.md`](docs/CEMETERY_0_7.md) preserves historical 0.7 rules.

## Verify

Run all twenty-seven smoke suites (stop the running game first; the new slice suites cover real movement and drawn-card combat):

```sh
for test in tests/*_smoke.gd; do
  /Applications/Godot.app/Contents/MacOS/Godot --headless --path . --script "res://$test"
done
```

Each suite must print its PASS marker without script/runtime errors. Automated correctness is not a guarantee of balanced or enjoyable play.

Local note: the user's separately installed Godot AI plugin can emit shutdown resource warnings even for the historical 0.8 scene. This is documented in the M01 report and is not hidden or patched by the gameplay test runner.

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
