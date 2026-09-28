# Combat Prototype 0.1 Architecture

## Product boundary

This project implements the smallest playable proof described by the approved English Game documents:

- six fixed Core Word Skills;
- 3 Focus per turn and at most 1 carried Focus;
- Enemy Intent with Obscured, Partial, and Clear information;
- Physical and Conceptual pressure;
- per-family Corruption and threshold Status;
- a non-QTE DEFLECT Reaction window;
- three teaching encounters and one two-family Elite;
- no draw pile and no mandatory language quiz.

Town exploration, AI NPCs, Companions, the full Roguelite map, Modifier builds, Relics, Exposure persistence, the first story death, and formal art remain outside Prototype 0.1.

## Runtime layers

```text
combat_content.gd
  Static Word Skill, Word Sense, enemy, Concept Family, and encounter data
        ↓
combat_state.gd
  Deterministic combat rules and turn-state transitions
        ↓ signals
combat_screen.gd
  Presentation, player input, modal choices, and battle progression
        ↓
main.tscn
  Godot entry scene
```

The rules layer has no dependency on the visual tree. It can be run headlessly, which keeps balance tests and future save/load work separate from presentation.

## Data boundaries

The prototype already keeps the framework's important distinctions:

- the displayed Word is not the Ability implementation;
- every skill and Hostile Word carries a specific Word Sense;
- Concept Family is combat metadata, not an absolute ontology;
- Mastery is represented first through information and recognition (`exposure`), not permanent damage inflation;
- Corruption is pressure, while Status is the consequence of crossing a threshold.

## Verification

`tests/combat_state_smoke.gd` verifies the first encounter's critical rule chain:

1. ERODE starts unknown;
2. OBSERVE reveals information;
3. BIND delays without deleting the action;
4. ERODE changes Armor and Decay independently;
5. DEFLECT spends reserved Focus and reduces physical damage;
6. STABILIZE and RESTORE retain distinct semantic roles.

Run it with:

```sh
/Applications/Godot.app/Contents/MacOS/Godot \
  --headless --path . \
  --script res://tests/combat_state_smoke.gd
```

## Next implementation milestone

Playtest and tune the four encounters before expanding scope. The next code milestone should add structured Word/Sense resources and recorded Exposure events, while keeping the same combat-state API.
