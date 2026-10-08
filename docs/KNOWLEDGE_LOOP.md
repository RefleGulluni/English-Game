# Mini Run 0.8 — Persistent, Spaced Knowledge

Production play now separates ambient appearance, valid primary context and deliberate application. `learning_schedule.gd` owns persistent earned stages, familiarity, errors, weak-layer diagnostics, stability, active pool, cooldown and pending evidence. A world encounter offers one question, not a chain; correct or incorrect answers close that opportunity. Wrong answers get authored natural correction and never lose resources. Combat context is recorded in the trace without independent learning popups. Winning alone is not evidence of understanding every printed enemy word.

ERODE/TOXIC retain their USABLE combat-card gates, with staged learning in native Cemetery scenes. Familiarity affects readable Lexicon contrast, never the earned stage. All ordinary restart/end-run behavior preserves knowledge and scheduling; DEV reset is isolated in a non-saving sandbox. See `PACING_0_8.md` for exact spacing, persistence and QA. The following sections are retained historical 0.7/0.6 fixtures, not the current production flow.

## Historical 0.7 target loops

Cemetery uses four core targets and one supported elastic word. Each has independent recognition/context/production sources and run-local state, using a subclass of the same evidence model. World scenes support explicit inference, contextual judgment and actual sentence completion. Enemy entry offers recognition only; observed/resolved combat consequences provide context separately. Missing learning receives weighted support and late-layer scene opportunities, never automatic USABLE. Ordinary inflections resolve to one lemma; derivations are not automatically merged.

The new targets grant information and scene understanding, not unspecified skill cards. UNDERSTOOD MOURN interprets Boss sorrow as pressure; other understood targets describe their relevant mechanism. Their evidence and states appear in Lexicon and Run Summary. See `CEMETERY_0_7.md` for the Director and event/monster carriers.

The inherited ERODE/TOXIC model below is preserved. In Cemetery, Grave Skeleton carries actual ERODE and poison-dust consequences so these two learned combat cards remain reachable without placing Root Husk or Iron Shell in the native pool. TOXIC's remaining exercises can occur during that combat; ERODE uses the existing post-map transfer/production interlude after contextual understanding.

The prototype implements ERODE (DECAY; gradual wearing away / weakening) and TOXIC (DECAY; harmful / poisonous). Knowledge is run-local, represented by independent shared `word_knowledge.gd` objects in RunState and CombatState snapshots. Restart Run resets evidence; node transitions, victories, defeat summaries, and Breathers do not.

## TOXIC path

After the inscription, the cracked vial introduces TOXIC and a meaning inference. Correct inference grants RECOGNIZED; poison-bearing intents then gain the information benefit. Iron Shell's TOXIC LEAK applies an actual player POISONED effect; the end-round HP consequence provides context evidence, not merely seeing text or clicking the card. Recognized TOXIC then becomes UNDERSTOOD. Transfer (contaminated water / fish) and production (toxic fumes) can occur during combat so successful learning makes TOXIC usable against Iron Shell itself. Resuming preserves the encounter, hand and Focus. Post-combat map presentation also supports the understood learning interlude. Skipping exercises leaves the corresponding knowledge gate closed; wrong exercise answers do not remove resources. The Lexicon lists both words and their own evidence.

## Playable path

1. Fracture Entry opens the Eroded Inscription, without consuming a route layer.
2. INFER FROM CONTEXT offers the three designed meanings. EXAMINE provides environmental clues without automatically granting evidence. IGNORE preserves ENCOUNTERED and continues.
3. Correct inference grants unique inscription Recognition Evidence and RECOGNIZED. Choose Root Husk on the existing first-layer map to see the combat advantage.
4. Recognized ERODE gains +1 initial Intent clarity before Obscurity/Inattention penalties. Recognition displays semantic clues, not exact mechanic quantities.
5. Combat Context Evidence requires prior recognition plus either reading ERODE's exact effects at CLEAR through OBSERVE, or experiencing its actual resolution. BIND, SHATTER, an arbitrary single skill use, and passive repetition alone do not count. The combat context is counted once per Run.
6. A correct recognition and one context unlock UNDERSTOOD and ERODE Insight. It provides structural weakening / Armor loss + Decay gain predictions for ERODE and other Decay-Structure Intents. No combat quantities are modified.
7. In 0.5, after Root Husk and Veil Moth, returning to the map offers the water/stone transfer context. A correct answer awards a distinct context, then offers the river/cliff production challenge. Successful transfer plus correct production advances to USABLE and activates the ERODE card as a Semantic Modifier. Challenges can be skipped, and wrong answers never remove resources or prior evidence.

The first-layer Event route remains available. Choosing it instead of Root Husk intentionally bypasses the full combat-learning path in that Run; it is not silently replaced by another battle.

## Integration rules

- Evidence has stable source IDs, preventing repeated buttons or repeated ERODE actions from farming evidence.
- The Lexicon is a minimal modal entry showing word, current state, meaning, family, evidence counts, and gameplay knowledge. Opening it suspends and later restores the active modal, including Reactions.
- A combat indicator explains knowledge-based information; the footer and Combat Trace report discovery/state changes. Long Intent text scrolls rather than clipping new information.
- Existing OBSERVE and Corruption rules remain active. At NEGLIGENT, warning degradation hides detailed predictions as well as exact effects; knowledge does not bypass it.
- All new modals use the shared adaptive component and sentence-break formatter. Do not create independently positioned popup text for future features.
- Combat STABILIZE is 1 Focus / dominant Corruption -8; Breather -12 and Supply -15 remain unchanged.
- The starter deck contains non-playable ERODE and TOXIC Context Cards before USABLE. Semantic use, discovered combinations and run-local Combat Codex entries are documented in `COMBAT_ECOLOGY.md`. None of these changes make recognition or Insight reduce incoming damage.

## Tests

`knowledge_loop_smoke.gd` verifies state transitions, evidence deduplication, information-only combat advantages, Corruption interactions, persistence, and balance. `knowledge_ui_smoke.gd` presses real modal buttons through the full learning flow, checks Lexicon return behavior, and verifies that learning does not consume map layers. Existing combat, Run, Inattention, modal layout, and UI tests remain part of regression verification.
