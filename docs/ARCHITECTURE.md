# Mini Run Prototype 0.3 Architecture

## Product boundary

This project keeps the Combat Prototype rules and places them inside the first complete Mini Run:

- six fixed Core Word Skills;
- 3 Focus per turn and at most 1 carried Focus;
- Enemy Intent with Obscured, Partial, and Clear information;
- Physical and Conceptual pressure;
- per-family Corruption and threshold Status;
- a non-QTE DEFLECT Reaction window;
- three teaching encounters, one rule-changing Elite, and one final encounter;
- a fixed four-layer route with meaningful path choices;
- cross-Encounter HP, Armor, Corruption, and Status rules;
- Breather, Event, Cache, Prototype Relic, Extract, and Run Result phases;
- no draw pile and no mandatory language quiz.

Town exploration, AI NPCs, Companions, procedural map generation, full Modifier builds, permanent Knowledge progression, the first story death, and formal art remain outside Prototype 0.3.

## Runtime layers

```text
combat_content.gd
  Static Word Skill, Word Sense, enemy, Concept Family, and encounter data
        ↓
combat_state.gd
  Deterministic combat rules and turn-state transitions
        ↕ combat snapshot/result
run_content.gd
  Fixed route, Event, Cache, and Prototype Relic definitions
        ↓
run_state.gd
  Persistent HP, Armor, Corruption, Status, Echo, Relics, and route progress
        ↓
run_manager.gd
  Node flow, rewards, Breather settlement, extraction, and Run completion
        ↓ signals / calls
combat_screen.gd
  Presentation, player input, combat screen, and modal Run phases
        ↓
main.tscn
  Godot entry scene
```

Both rules layers have no dependency on the visual tree. They can be run headlessly, which keeps balance tests and future save/load work separate from presentation.

## Run flow

```text
Fracture Entry
  → Map choice
  → Encounter / Event / Cache
  → automatic post-combat settlement
  → Breather choice
  → next map layer
  → Elite or safer route
  → Extract or Final Encounter
  → Run Result
```

Combat never advances the map directly. `CombatState` emits a result, `RunManager` captures the player snapshot, applies rewards and the Combat 0.2 persistence rules, then returns control to the Run UI.

## Combat 0.2 persistence rules

- HP persists exactly between Encounters.
- Focus starts each Encounter at 3.
- Armor automatically rebuilds by `ceil(Max Armor × 30%)` after victory.
- Decay, Obscurity, and Inattention each naturally dissipate by 5 after victory.
- Transient Status clears after battle.
- Lingering Status follows its Corruption apply and clear thresholds.
- Recover restores 6 HP, or 4 Armor when HP is already full.
- Stabilize reduces the dominant Corruption family by 12.
- Press On makes the next node's Echo reward `×1.25`.

## Data boundaries

The prototype already keeps the framework's important distinctions:

- the displayed Word is not the Ability implementation;
- every skill and Hostile Word carries a specific Word Sense;
- Concept Family is combat metadata, not an absolute ontology;
- Mastery is represented first through information and recognition (`exposure`), not permanent damage inflation;
- Corruption is pressure, while Status is the consequence of crossing a threshold.
- Inattention pressure is surfaced before CARELESS: Intent clarity worsens at 40, OBSERVE costs +1 at 50, DEFLECT costs +1 at 60, and CARELESS applies at 80.
- Clear Lens makes only the first OBSERVE free; once consumed, all active Inattention cost modifiers still apply.
- SHATTER damages Structure until its one-time collapse, then deals exposed HP damage on later uses.

## Verification

`tests/combat_state_smoke.gd` verifies the original encounter rule chain. `tests/run_state_smoke.gd` verifies:

1. HP, Armor, Corruption, and Status post-combat persistence;
2. all three Breather choices and Press On reward multiplication;
3. Combat snapshot import;
4. Elite scaling and its opening Inattention pressure;
5. Clear Lens, Iron Script, and Quiet Mind effects;
6. fixed route progression through Event, Cache, Encounter, and Exit.

`tests/ui_flow_smoke.gd` instantiates the real main scene and walks through Event → Cache → Elite → Breather → Relic → Extract to verify that presentation and rules stay connected.

Run it with:

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

## Next implementation milestone

Playtest the full 15–25 minute loop and tune rewards, recovery, and route pressure. Build Prototype 0.4 can then add Modifier Words, more Relics, and Semantic Combos without changing the Run/Combat boundary.
