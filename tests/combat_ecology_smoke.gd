extends SceneTree

const WORD := preload("res://scripts/run/word_knowledge.gd")
const FIXTURE := preload("res://tests/mechanics_fixture.gd")
var failures: Array[String] = []

func _initialize() -> void:
	_test_actions()
	_test_semantics()
	_test_ghost_and_shell()
	_test_retain()
	_test_survival()
	_test_knowledge_and_anomaly()
	for failure in failures:
		push_error(failure)
	print("COMBAT_ECOLOGY_SMOKE: %s" % ("PASS" if failures.is_empty() else "FAIL (%d)" % failures.size()))
	quit(0 if failures.is_empty() else 1)

func _check(condition: bool, message: String) -> void:
	if not condition:
		failures.append(message)

func _word(id: String):
	var word := WORD.new(id)
	word.encounter()
	word.recognize("test_context")
	word.record_combat_context(true)
	word.record_transfer(true)
	word.record_production(true)
	return word

func _combat(index: int = 4) -> CombatState:
	var combat := CombatState.new()
	combat.start_battle(index, {"knowledge": _word("erode"), "toxic_knowledge": _word("toxic")})
	combat.finish_mulligan()
	combat.focus = 100
	return combat

func _round(combat: CombatState) -> void:
	combat.end_player_turn()
	if combat.turn_ending and not combat.finished:
		combat.resolve_enemy_action(false)

func _test_actions() -> void:
	var combat := _combat()
	FIXTURE.play(combat, "SHATTER")
	_check(combat.enemy.structure == 0 and combat.enemy.armor == 18 and combat.enemy.hp == 32, "SHATTER breaks Structure without removing Armor or dealing collapse damage")
	_check(combat.enemy_effects.duration("EXPOSED") == 2, "collapse applies two-turn EXPOSED")
	FIXTURE.play(combat, "STRIKE")
	_check(combat.enemy.hp == 32 and combat.enemy.armor == 8, "EXPOSED STRIKE deals ten, absorbed by Armor")
	combat.enemy.armor = 0
	FIXTURE.play(combat, "STRIKE")
	_check(combat.enemy.hp == 22, "EXPOSED STRIKE has +2 direct damage")
	_round(combat)
	_check(combat.enemy_effects.duration("EXPOSED") == 1, "EXPOSED current round counts as its first window")
	_round(combat)
	_check(not combat.enemy_effects.has("EXPOSED"), "EXPOSED expires after two rounds")
	combat = _combat()
	FIXTURE.play(combat, "STRIKE")
	_check(combat.enemy.structure == 6 and combat.enemy.armor == 10 and combat.enemy.hp == 32, "STRIKE has low Structure damage and high direct damage")
	combat.enemy.structure = 0
	combat.enemy.armor = 4
	FIXTURE.play(combat, "SHATTER")
	_check(combat.enemy.armor == 0 and combat.enemy.hp == 31, "SHATTER chips two Armor before its three direct damage")
	combat = _combat()
	combat.relics.append("iron_script")
	FIXTURE.play(combat, "SHATTER")
	_check(combat.enemy_effects.duration("EXPOSED") == 3 and combat.enemy.hp == 32, "IRON SCRIPT extends EXPOSED rather than damage")
	combat = _combat()
	combat.enemy.structure = 1
	FIXTURE.play(combat, "ERODE")
	_round(combat)
	_check(combat.enemy_effects.duration("EXPOSED") == 2, "collapse during end-of-round erosion preserves two future usable windows")

func _test_semantics() -> void:
	var combat := _combat()
	FIXTURE.play(combat, "ERODE")
	FIXTURE.play(combat, "SHATTER")
	_check(combat.erosion_turns == 4 and combat.erosion_tick == 3, "Fractured Erosion upgrades and extends")
	FIXTURE.play(combat, "SHATTER")
	_check(combat.erosion_turns == 4, "a second SHATTER does not extend the same combo repeatedly")
	FIXTURE.play(combat, "ERODE")
	_check(combat.erosion_turns == 3 and combat.erosion_tick == 2, "reapplication refreshes base effect, never inherits stacking")
	combat = _combat()
	combat.enemy.structure = 0
	combat.enemy.armor = 18
	FIXTURE.play(combat, "ERODE")
	FIXTURE.play(combat, "STRIKE")
	_check(combat.enemy.armor == 10 and combat.enemy.hp == 32, "penetration does not add damage when remaining Armor can absorb eight")
	combat = _combat()
	combat.enemy.structure = 0
	combat.enemy.armor = 2
	FIXTURE.play(combat, "ERODE")
	FIXTURE.play(combat, "STRIKE")
	_check(combat.enemy.hp == 24 and combat.enemy.armor == 2, "low Armor is ignored, not destroyed or converted into bonus damage")
	_check("weakened_opening" in combat.knowledge.discovered_combos, "Weakened Opening discovery recorded")
	combat = _combat()
	FIXTURE.play(combat, "TOXIC")
	_check(combat.enemy.hp == 32 and combat.enemy_effects.duration("POISONED") == 3, "TOXIC has no immediate damage")
	FIXTURE.play(combat, "TOXIC")
	_check(combat.enemy_effects.duration("POISONED") == 3 and combat.enemy_effects.active.POISONED.stack_count == 1, "POISONED refreshes instead of stacking")
	_round(combat)
	_check(combat.enemy.hp == 29 and combat.enemy.structure == 8 and combat.enemy.armor == 18, "poison bypasses both defenses at round end")
	combat.focus = 100
	FIXTURE.play(combat, "TOXIC")
	FIXTURE.play(combat, "STRIKE")
	_check("venomous_strike" in combat.toxic_knowledge.discovered_combos and combat.enemy_effects.duration("POISONED") == 3, "Venomous Strike refreshes poison without extra burst")
	combat = _combat()
	combat.relics.append("echo_chamber")
	FIXTURE.play(combat, "TOXIC")
	var copy: Dictionary = {}
	for card in combat.deck.hand:
		if card.echo:
			copy = card
	_check(copy.name == "TOXIC" and combat.card_cost(copy) == 2, "Echo Chamber supports TOXIC with +1 cost")
	combat.use_card(int(copy.instance_id))
	_check(copy in combat.deck.exhaust_pile and combat.enemy_effects.duration("POISONED") == 3, "Echo TOXIC exhausts and refreshes once")
	var copies := 0
	for card in combat.deck.hand:
		copies += 1 if card.echo else 0
	_check(copies == 0, "Echo TOXIC cannot recursively copy")

func _test_ghost_and_shell() -> void:
	var combat := _combat(5)
	_check(not combat.enemy.has_structure and combat.enemy.structure == 0 and combat.enemy.hp == 28, "Ghost profile has Structure NONE")
	FIXTURE.play(combat, "SHATTER")
	_check(combat.enemy.hp == 25 and not combat.enemy_effects.has("EXPOSED"), "Ghost SHATTER is low damage without collapse")
	FIXTURE.play(combat, "TOXIC")
	_check(combat.poison_tick_damage() == 1, "75 percent resistance rounds poison tick to one")
	_round(combat)
	_check(combat.enemy.phase_state == "FADED" and combat.enemy.hp == 24, "even turns are predictably FADED")
	combat.focus = 100
	FIXTURE.play(combat, "STRIKE")
	_check(combat.enemy.hp == 20, "FADED halves STRIKE to four")
	FIXTURE.play(combat, "OBSERVE")
	_check(combat.enemy.phase_state == "REVEALED" and combat.enemy_effects.duration("REVEALED") == 1, "OBSERVE reveals for one turn")
	FIXTURE.play(combat, "STRIKE")
	_check(combat.enemy.hp == 12 and combat.poison_tick_damage() == 1, "REVEALED restores direct damage but not poison potency")
	_round(combat)
	_check(combat.corruption.Obscurity == 20 and combat.enemy.phase_state == "NORMAL" and not combat.enemy_effects.has("REVEALED"), "Phantom Touch adds Obscurity and Reveal expires")
	combat.enemy.toxic_immune = true
	_check(combat.disabled_reason("TOXIC") == "TARGET IMMUNE", "immune target has an explicit disabled reason")
	_check(combat.disabled_reason("ERODE") == "NO VALID STRUCTURE TARGET", "Erode has a reason when neither Structure nor Armor exists")
	combat = _combat()
	combat.enemy.armor = 10
	for round_index in range(3):
		_round(combat)
	_check(combat.enemy.armor == 14 and combat.enemy.structure == 8, "third-round REINFORCE repairs only Armor by four")
	combat.enemy.armor = 17
	combat.intent = combat.enemy.actions[2].duplicate(true)
	combat.resolve_enemy_action(false)
	_check(combat.enemy.armor == 18, "REINFORCE caps Armor at eighteen")

func _test_retain() -> void:
	var combat := _combat()
	var card: Dictionary = combat.deck.hand[0]
	var uid := int(card.instance_id)
	_check(combat.deck.toggle_retain(uid, 1), "first Retain permitted")
	_round(combat)
	_check(card in combat.deck.hand and card.retained_last_turn, "retained instance is marked on next turn")
	_check(not combat.deck.toggle_retain(uid, 1) and combat.retain_disabled_reason(card) == "CANNOT RETAIN CONSECUTIVELY", "consecutive Retain blocked with a readable reason")
	combat.deck.consume(card)
	combat.deck.draw_pile.clear()
	combat.deck.discard_pile.clear()
	combat.deck.hand.clear()
	combat.deck.discard_pile.append(card)
	combat.deck.draw_to(1)
	_check(not card.retained_last_turn and combat.deck.toggle_retain(uid, 1), "redrawing the same instance starts a new Retain eligibility cycle")
	combat.relics.append("unfinished_sentence")
	_check(combat.retain_slots() == 2, "approved Unfinished Sentence exception remains")

func _test_survival() -> void:
	var combat := _combat(2)
	combat.objective = "survive"
	combat.enemy.hp = 1
	combat.enemy.structure = 0
	FIXTURE.play(combat, "STRIKE")
	_check(combat.dispersed and not combat.finished, "zero HP disperses instead of winning")
	var hp := combat.hp
	_round(combat)
	_check(combat.hp == hp and combat.completed_rounds == 1 and combat.enemy.hp == combat.enemy.max_hp and not combat.dispersed, "safe window cancels enemy action and next turn reforms at full HP")
	for round_index in range(4):
		_round(combat)
	_check(combat.finished and combat.completed_rounds == 5 and combat.hp > 0, "only five completed survival rounds win")
	combat = _combat(2)
	combat.objective = "survive"
	combat.completed_rounds = 4
	combat.hp = 1
	combat.armor = 0
	combat.intent = {"word": "RAP", "kind": "physical", "damage": 7}
	combat.deck.hand.clear()
	_round(combat)
	_check(combat.finished and combat.hp == 0, "death on the fifth round is not a survival victory")
	combat = _combat()
	combat.enemy.hp = 1
	combat.hp = 1
	combat.enemy_effects.apply("POISONED", 3, 3, "test")
	combat.player_effects.apply("POISONED", 3, 3, "test")
	var outcomes: Array[bool] = []
	combat.battle_finished.connect(func(victory: bool): outcomes.append(victory))
	_round(combat)
	_check(outcomes == [false], "simultaneous poison deaths settle once with player defeat taking priority")

func _test_knowledge_and_anomaly() -> void:
	var toxic := WORD.new("toxic")
	toxic.encounter()
	toxic.recognize("vial")
	_check(toxic.current_state == "RECOGNIZED", "Toxic has its own knowledge progression")
	var combat := CombatState.new()
	combat.start_battle(4, {"toxic_knowledge": toxic})
	combat.finish_mulligan()
	_round(combat)
	_check(toxic.current_state == "UNDERSTOOD" and combat.hp == 47, "real player poison consequence teaches Toxic without damage immunity")
	toxic.record_transfer(true)
	toxic.record_production(true)
	_check(toxic.current_state == "USABLE" and "TOXIC" in toxic.entry_text(), "Toxic transfer and production unlock card and Lexicon")
	var manager := RunManager.new()
	manager.start_run()
	manager.state.current_layer = 1
	manager.select_node("semantic_anomaly")
	manager.resolve_anomaly("bind")
	_check(manager.state.corruption.Obscurity == 8 and manager.state.temporary_cards.is_empty(), "wrong semantic answer risks eight Corruption without a reward")
	manager.start_run()
	manager.state.current_layer = 1
	manager.select_node("semantic_anomaly")
	manager.resolve_anomaly("anchor")
	_check(not manager.state.anomaly_resolved, "hidden Anchor cannot bypass USABLE requirement")
	manager.resolve_anomaly("erode")
	_check(manager.state.current_layer == 1 and manager.state.temporary_cards == ["STABILIZE"], "correct semantic judgment earns reward without consuming layer")
	manager.start_run()
	manager.select_node("iron_shell")
	combat.start_battle(4, manager.state.combat_snapshot())
	manager.complete_combat(combat)
	_check(manager.state.current_layer == 0 and "iron_shell" in manager.state.completed_detours, "fixed ecology branch does not advance main route and cannot be repeated")
