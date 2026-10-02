# Mini Run 0.6 — Implemented Combat Ecology

## Approved integration choices

- SHATTER: while Structure is positive, break 8 Structure only. Without Structure, remove 2 Armor, then deal 3 HP-directed damage; remaining Armor absorbs that damage.
- Base Retain is one slot, two with UNFINISHED SENTENCE. No instance may be retained in consecutive turns, including Relic slots. Drawing it again after discard resets eligibility.
- IRON SCRIPT extends Collapse's EXPOSED by one turn, replacing its former Collapse damage.

## Actions and effects

The twelve-card starter is SHATTER ×1, STRIKE ×2, OBSERVE ×2, BIND ×2, STABILIZE ×1, DEFLECT ×1, RESTORE ×1, ERODE ×1 and TOXIC ×1. Five-card draws, opening Mulligan, Focus, discard/Exhaust and reserved DEFLECT timing remain intact. ERODE and TOXIC require their own USABLE knowledge.

STRIKE costs 2 Focus: 8 direct damage, plus 2 weak Structure damage. Existing EXPOSED adds 2 direct damage; a Collapse caused by this STRIKE does not retroactively buff the same hit. Structure Collapse applies two-turn EXPOSED, never automatic HP damage, and does not erase Armor. Root regrowth can make a later Collapse possible again.

ERODE costs 1 Focus: EROSION lasts three completed rounds, damaging 2 Structure, or 1 Armor after Structure is gone. It never directly damages HP. Reapplication refreshes exactly three rounds and base potency, not additive stacks. ERODE → SHATTER upgrades that turn's EROSION to 3 Structure per tick and adds one duration, at most once that turn. ERODE → STRIKE penetrates up to 3 Armor for that attack without removing the ignored Armor.

TOXIC costs 1 Focus: POISONED lasts three completed rounds, dealing 3 HP damage through Armor at round end. Reapplication refreshes one effect. TOXIC → STRIKE refreshes poison duration; it does not create extra copies or increase base potency. ECHO CHAMBER supports either learned Word and exhausts its cost-plus-one copy without recursion.

Enemy action resolves before EROSION, enemy poison and player poison. Both sides' end-round consequences resolve before outcome selection; player death has priority over simultaneous victory or fifth-round survival. Durations then decrement. EXPOSED newly caused by end-round EROSION retains its two upcoming action windows rather than immediately losing a turn. Poison / Erosion applied during player actions count that round's tick. Semantic effects are separate from corruption-threshold statuses and record duration, potency, source and explicit refresh behavior.

## Encounters and routes

The original four-layer route is preserved. Optional fixed Iron Shell / Ghost test paths do not consume a map layer, offer normal battle settlement, and each disappear after completion. Iron Shell is available from the first-layer map and Ghost from the second; both remain available at the third-layer map if not completed, allowing a later visit with USABLE ERODE. No random route replacement was introduced.

- Iron Shell: 32 HP, 8 Structure, 18 Armor. Every third normal action reinforces 4 Armor, capped at 18; BIND delays the current intent as usual. TOXIC LEAK applies real three-round player poison for the learning context; SHELL BASH is physical pressure. Breaking Structure alone cannot bypass its Armor.
- Ghost: 28 HP, no Structure or Armor; 75% poison resistance rounds the normal 3-damage tick up to 1. Even-numbered player turns enter FADED, halving STRIKE's direct damage. OBSERVE reveals it for the current window. PHANTOM TOUCH applies physical damage and Obscurity; WHISPER applies Obscurity and worsens next clarity. Revealing does not remove poison resistance. Optional elite profile supports poison immunity.
- Normal Neglect Wraith: survive five completed rounds while alive. Zero HP causes DISPERSED, cancelling an unresolved normal action; the next player turn reforms it at full HP. Existing Structure, Armor and timed effects are not reset by reformation. Defeating it is breathing room, not encounter victory. Elite Wraith and final Husk retain kill objectives.
- Root Husk's regrowth / counter and Veil Moth's false intent remain active.

## Knowledge and Anomaly

ERODE's prior learning path is preserved. TOXIC independently follows exposure, recognition, actual combat consequence, transfer and production. The first Toxic consequence offers its remaining exercises during combat, preserving encounter state. Learning is information-first and does not add permanent damage. See `KNOWLEDGE_LOOP.md`.

Semantic Anomaly now asks which word fits the rain-worn stone: ERODE, BIND or RESTORE. Correct ERODE rewards a temporary next-combat STABILIZE (Exhaust); wrong answers add 8 Obscurity but do not downgrade knowledge. Leave is safe. USABLE ERODE unlocks anchoring for dominant Corruption -8. Recognition / Understanding add progressively richer hints. The node is optional, once-only, and does not consume a route layer.

First combo discoveries and enemy-rule discoveries enter the run-local Lexicon / Combat Codex. Restart clears knowledge and discoveries; permanent saves are out of scope.

## Presentation and verification

Every hand card shows its current cost, category, role and concrete unavailable reason. Retain explains consecutive-turn rejection. Enemy Structure / Armor are distinct; Ghost explicitly displays STRUCTURE NONE. Phase, resistance, poison, Erosion and EXPOSED are separate rows in bounded status areas. Player buffs / debuffs stay one per row. All popups retain the shared adaptive layout, centered sentence breaks and scrolling.

All fourteen smoke suites pass, including the prior ten regression suites. New coverage:

- `combat_ecology_smoke.gd`: direct versus Structure damage, Armor penetration, refresh/no stacking, combinations, poison resistance, Ghost revelation, Retain eligibility, Wraith reformation, death priority, knowledge, Anomaly and test-node rules.
- `ecology_ui_smoke.gd`: actual Toxic exercises during combat, preserving state on return, both Lexicon entries, disabled reasons, Retain limits, Ghost status and Anomaly gating.
- `ecology_playthrough_smoke.gd`: complete legal drawn-card route through Root, Anomaly, Veil, Iron Shell, Ghost, survival and final encounter without injected Focus, HP or cards.
- `ecology_seed_smoke.gd`: 48 seeded encounter simulations and 963 invariant checks for deck identity, Focus, HP, Armor and timed effects. This uses fully learned Words / existing Relics to test mechanics, not to assert new-player difficulty.

Automated correctness and a legal complete run do not establish strategic diversity or enjoyment. Human playtesting remains necessary for draw frustration, Ghost resistance, Iron Shell pacing, survival pressure and relative action value.
