# Mini Run 0.7 — Cemetery Implementation and QA

## Scope and approved interpretation

Normal play now uses Cemetery, six layers and a two-phase Mourning Keeper. No formal art, multi-enemy combat, other Biomes, permanent Lexicon, Transition Area or third Boss phase was added. Bone Keeper, Buried Legionnaire and Lingering Wraith remain unimplemented.

The user approved implementing MOURN / LINGER / CONCEAL / REASSEMBLE as learning, information and scene interactions without inventing four new combat cards. ERODE and TOXIC retain their existing learned-card gates, deck/Focus/Retain rules, combinations and evidence loops. The 0.6 rule fixture remains loadable through `RunManager.start_run()`; default UI uses `start_cemetery_run()` and regression UI tests explicitly select the legacy fixture.

## Seed, pools and Director

Each new Run gets an integer Seed. DEV → Set Seed restarts it with a specified value. Seed controls elastic target selection, layer choices, enemy/event availability, reward offers, exercise order and hand RNG. Combat hand seeds additionally include layer depth so a repeated enemy need not repeat its opening hand.

Replay requires the same Seed, choices, exercise outcomes and state; adaptive routes intentionally respond to learning/history. Nodes are generated lazily per layer and cached. Opening the map twice, opening Lexicon or inspecting weights does not reroll. The Weight Inspector shows the actual generation snapshot's Base × Biome × Layer × Learning × Rhythm × Repetition components; knowledge gained after generation affects future layers rather than silently replacing current options.

Layers 1–5 offer two or three distinct choices; Layer 1 cannot include Elite. Layer 6 always offers the Boss. Native pools contain Ghost, Veil Ghost, Grave Skeleton, Neglect Wraith and Mourning Wraith, with Skeleton/Veil elites from Layer 2. Root Husk / Iron Shell remain DEV tests, not random native content. All native entries have high Biome weight. Repeated recent content is penalized. Two consecutive fights increase safe opportunities and ensure a noncombat alternative; two consecutive noncombat choices increase fight weight and ensure a fight alternative. These are offered choices, not forced outcomes: a player may intentionally choose a long combat or noncombat sequence.

Layer 5 always has a relatively safe Event, Rest or Relic alternative; it is not a forced campfire. Guaranteed learning scenes are safe. Rest offers existing Recover / Stabilize / Press On. Relic opportunities and Elite rewards offer three distinct unowned Relics plus Skip, retaining run effects. With fewer than three unowned Relics remaining, the offer contains all remaining choices plus Skip.

## Learning opportunities

Core targets are fixed MOURN, LINGER, CONCEAL and REASSEMBLE. The fifth comes from REMAINS / HOLLOW / BURY / HAUNT / WITHER / SCATTER / GRAVE / ECHO, filtered for actual native carriers and weighted for semantic overlap (HAUNT/HOLLOW lower than other supported choices). Each elastic word has a real non-production scene or enemy carrier, not only a dictionary entry.

Events: The Mourning Stone, Hidden Epitaph, Scattered Bones, Lingering Bell, Grave Inscription, Caretaker's Note and Withered Flowers. The first scenes connect concrete native concepts; inscriptions/notes support missing targets and their sentence production. Each core can learn through world scenes and its enemy family, then through a production scene. Event exercises separately ask meaning, contextual relationship and sentence use; correct answers grant deduplicated sources. Wrong answers and Skip never auto-unlock or remove past evidence/resources.

Layer 3 boosts unrecognized targets and supplies a missing-learning scene. Layer 4 boosts production and supplies it for understood core words. Layer 5 explicitly offers all still-incomplete core targets in one scene, including every one-step-from-USABLE word. This guarantees selectable opportunities, not correct answers, compulsory study or all five USABLE. A scene may offer several targets; choosing to study multiple words is explicit, not an automatic batch reward. Ordinary inflections share state, while derivations such as EROSION remain separate.

ERODE's inscription and TOXIC's vial are retained at entry. Grave Skeleton's ERODE (Decay +6, player Armor -1) and TOXIC DUST (three-round player poison) provide real combat contexts. TOXIC can finish its existing transfer/production interlude during Skeleton combat and return to the same hand/Focus state. ERODE retains its existing map-based transfer/production after contextual learning. Skipping these still leaves their card gates closed. New targets are visible in Lexicon even before recognition, with state/evidence and progressively unlocked information; summary reports targets and newly usable words, including learned ERODE/TOXIC.

## Grave Pressure and numerical baseline

Pressure starts at zero per encounter, increases after each completed round, and resets on victory/defeat. It does not persist across nodes. At 0–2 there is no extra penalty. At 3–4 the first positive Obscurity gain each turn adds 2; at 5+ that remains and each player-turn start adds 3 to current dominant Corruption. Ties use existing family order; all-zero falls back to Obscurity. If dominant is Obscurity, its +3 is a gain and can receive the first-gain +2. These consequences and status rows are explicit in Combat Trace/UI.

Provisional numbers chosen where the handoff deliberately leaves QA tuning:

- Grave Skeleton: 24 HP, 12 Structure, 5-damage physical attack, grave dust information pressure, ERODE and TOXIC DUST. Zero HP enters 10-integrity BONE REMAINS rather than Victory. The two-completed-round countdown begins immediately; Remains do not attack, though already-applied player poison can still tick. SHATTER removes 8 integrity, STRIKE 3, BIND adds one countdown once per Remains phase. Destroying them prevents reassembly and wins. Otherwise it returns at half maximum HP/Structure; enemy temporary effects clear. Repeated reassembly remains possible, so a missed Remains window is meaningful.
- Veil Ghost: 28 HP, Structure NONE, 75% Toxic Resistance, even-turn FADED and false intent. OBSERVE reveals it and restores direct-action effectiveness for the current window, not poison effectiveness.
- Mourning Wraith: 30 HP, 8 Structure; Mourning +1 per completed round. At 3+, each round adds 2 Obscurity and 1 extra Cemetery Pressure. OBSERVE reduces Mourning by 2. Its physical touch deals 5. No learned-word HP reduction is added.
- Mourning Keeper: 64 HP, 16 Structure. Phase 1 has hidden MOURN/CONCEAL intents and a 6-damage staff attack. UNDERSTOOD MOURN interprets unknown sorrow as increasing pressure. OBSERVE reveals hidden intent and reduces Mourning. At half HP, Phase 2 raises round Pressure growth to 2, adds one Mourning on transition, and changes staff damage to 7; Pressure 5+ adds 2 staff damage. Clear warnings show the actual phase/pressure-adjusted damage. Mourning's existing threshold can add another Pressure. Defeat proceeds directly to Biome Clear.

Bone Remains card descriptions adapt to current integrity damage instead of showing ordinary HP damage. BIND flags reset on new encounters and Remains intent transitions, preventing stale delays. Pressure, Mourning, Boss phase, remaining countdown and ordinary semantic effects use bounded, separate status rows.

## Relics and Biome Resonance

Pool: CLEAR LENS, UNFINISHED SENTENCE, REFINED IRON SCRIPT (same `iron_script` ID), VENOM VESSEL, MOURNER'S THREAD, OSSUARY KEY, PALE CANDLE and ECHO CHAMBER. QUIET MIND remains legacy/DEV-loadable but is not in the eight-item Cemetery reward pool.

Existing first-free OBSERVE, second Retain slot, EXPOSED +1 turn and first-Word Echo copy remain unchanged. VENOM VESSEL adds one duration to the first Poisoned application per combat; later applications remain base refresh, not stacking. MOURNER'S THREAD triggers once per combat on a genuine hidden/false-intent reveal and discounts the next played ERODE/TOXIC by 1 Focus, including Echo copies; Cemetery additionally reduces Pressure by 1. OSSUARY KEY adds 2 Remains integrity damage; first prevented reassembly additionally reduces Cemetery Pressure by 1. In single-enemy fights, prevention also ends the encounter and resets Pressure, so this resonance has no lasting cross-node effect. PALE CANDLE reduces first positive Obscurity gain by 4; first Awakened entry additionally reduces dominant Corruption by 3 before the usual start-turn pressure. Resonance applies only in Cemetery; base effects are not biome-locked.

Build tendencies in summary derive from acquired Relics, not Classes. Numerical tuning and actual strategic diversity require human playtesting; legal auto-policy wins do not prove that builds are equally strong.

## DEV workflow

In editor/debug runs, use the DEV button or F2. Release builds hide it. Actual editable inputs support Seed, Layer 1–6, fixed four core targets plus another compatible fifth target, Word State (including an inflected surface), Relic ID, HP 0–50, Focus 0–4, family Corruption 0–100 and Pressure 0–100. Test buttons enter Ghost, Veil Ghost, Skeleton, Neglect/Mourning Wraith, Boss, Root and Iron Shell. Specific Event, reset Lexicon and Weight Inspector are available. Invalid input does not mutate run state. Seed starts fresh; other edits are QA state mutations and recorded in history.

DEV over a decision preserves it for Close; changing Seed/Layer/Event/test abandons the old decision intentionally. Lexicon and DEV cannot be nested. Inputs and inspector reuse the adaptive modal/scroll layout; no manually positioned popup text was introduced. Event tests can advance the selected test Run; use a known Seed again for clean reproduction.

## Verification

18 smoke suites pass: all 14 inherited regressions and 4 new suites. `cemetery_director_smoke.gd` checks 240 Seeds, 14,125 conditions and 186 distinct first-layer variants, including deterministic routes/targets/rewards, safe options, no duplicates, native carriers, weighting, learning and eight Relics. `cemetery_combat_smoke.gd` verifies Pressure stages, base-versus-resonance behavior, real reveals, discount/Echo/poison refresh, Skeleton handling and BIND transitions, Mourning and Boss phases/information/warnings. `cemetery_ui_smoke.gd` exercises the actual main scene and editable DEV input, incorrect/correct learning, Lexicon return, rewards, summary and test controls. `cemetery_playthrough_smoke.gd` completes eight distinct seeded six-layer routes with legal drawn-card/Focus policy and explicit correct exercise outcomes, reaching Boss defeat and at least two usable target words without injecting combat HP, Focus or cards.

Rendered QA covers the actual entry, Seed input, Boss/status display and Weight Inspector. Engine smoke tests must print PASS without script/runtime errors; exit code alone is insufficient in Godot. Backups remain separately recoverable. No main merge or GitHub push is part of this implementation.
