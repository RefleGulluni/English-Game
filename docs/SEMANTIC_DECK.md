# Mini Run 0.5 — Implementation Notes

## Deck and timing

Each combat starts a fresh ten-card starter deck, plus any next-combat temporary reward. Cards have stable definition IDs and unique instance IDs. Draw five; opening Mulligan replaces zero to two cards once, drawing replacements before returned cards are shuffled back. No card is guaranteed by hand manipulation.

Playing an Action consumes its hand instance, spends its actual Focus cost and discards it. Exhaust instances instead enter an isolated Exhaust pile. At End Turn unretained Actions are discarded; DEFLECT remains until enemy resolution. An unused DEFLECT is then discarded unless retained. Retain is free, defaults to one slot and clears its selection on the next turn. Refill to five, reshuffling only the discard pile when needed. Retained cards count toward the five-card target.

Focus remains 3 plus at most 1 carry. DEFLECT requires a hand instance and sufficient Focus, including CARELESS cost penalties. It cannot be played as an ordinary Action. SPLINTER RESPONSE uses the same Reaction machinery without advancing the enemy's normal turn. Reaction windows have no timer.

## Structure, Armor and Erosion

The user approved separating enemy Structure from enemy Armor. Existing enemy structure values stay unchanged; extra Armor starts at zero. Enemy guard adds Armor. SHATTER removes 8 Structure, causes the existing one-time 6 damage collapse (10 with IRON SCRIPT), then deals 10 damage to exposed enemies. Armor absorbs HP-directed damage first.

USABLE ERODE costs 1 Focus and applies Erosion for three completed rounds. Erosion resolves after the enemy action or a BIND-delayed round: -2 Structure, or -1 extra Armor when Structure is zero. It never directly damages HP, including when erosion causes collapse. Reapplying active Erosion refreshes to at least three turns rather than stacking independent effects. A fresh application after expiration returns to the base tick of 2.

ERODE followed by SHATTER in the same turn triggers FRACTURED EROSION: duration +1, Structure tick becomes 3. The first discovery is visibly announced and recorded in Lexicon; subsequent triggers only log the resonance. Combo details are hidden in Lexicon until discovered. No permanent damage modifier is granted by word knowledge.

## Combat identities and objectives

- Root Husk: two completed rounds without Structure damage restore up to 6 Structure. After two consecutive SHATTER turns, the next SHATTER triggers 4 Physical Damage; DEFLECT reduces it to 1. The counter's full rule is revealed on first activation and saved in the run-local Combat Codex.
- Veil Moth: selected turns show two unordered possible intents. One is false; OBSERVE eliminates it. Normal Obscurity information penalties still apply to the real intent. BIND preserves the current intent, including its ambiguity.
- Neglect Wraith: PRESSURED simplifies Reaction wording; CARELESS hides details; NEGLIGENT shows only “Reaction Available” in the body. Card availability, cost and valid Reaction controls remain intact.
- Normal Neglect Wraith: survive five completed rounds with HP above zero. Killing is not required. A defeated enemy stops acting while remaining survival rounds complete. Death has priority over success on the fifth round. Elite and final encounters retain kill objectives.

## Relics and route

Relics carry rarity, rule type and trigger metadata. Six rarity colors are supported. CLEAR LENS makes the first OBSERVE free; QUIET MIND subtracts 5 from the first Inattention gain; UNFINISHED SENTENCE gives two Retain slots; ECHO CHAMBER creates a cost-plus-one Exhaust ERODE copy on the first usable Word play each turn, never recursively from the copy. IRON SCRIPT remains an optional fifth Relic.

The four-layer route is preserved. Root's reward now includes a Relic. Layer 2 offers an optional, once-only Semantic Anomaly which does not consume the layer: Examine grants a temporary STABILIZE for the next combat (Exhaust after use), Stabilize reduces dominant Corruption by 8, Leave costs nothing. The transfer / production interlude follows Veil Moth. Layer 3 offers normal Wraith survival or Elite Wraith kill; layer 4 offers extraction or the deeper final encounter. Event and Cache shortcuts are retained.

Knowledge, discoveries and Codex entries persist within the run and reset on Restart. There is no long-term save system in this prototype.

## UI and verification

Hand cards display current cost, category and effect; contextual ERODE is disabled until USABLE. Every card has a Retain control. Draw, discard, Exhaust and selected Retain counts are visible. Echo overflow uses horizontal scrolling. Trait text and long Codex entries use bounded scrolling. All modals use the shared adaptive layout, centered wrapping and sentence-aware line breaks; no per-popup width edits are needed.

Legacy effect tests use `mechanics_fixture.gd` to isolate their original rules with explicit hand fixtures. They no longer assume unlimited fixed skills. `semantic_deck_smoke.gd` covers actual deck constraints, Mulligan, Retain, Reaction timing, Erosion, combinations, enemy traits, survival, Relics and Anomaly rewards. `semantic_ui_smoke.gd` exercises real hand and Mulligan buttons and graded Reaction wording. `playthrough_smoke.gd` completes Root → Anomaly → Moth → USABLE ERODE → survival → extraction with real drawn cards and normal Focus, without injected combat advantages.

Automated correctness is not a balance guarantee; draw quality, difficulty, information readability and the fun of retaining cards require human playtesting.
