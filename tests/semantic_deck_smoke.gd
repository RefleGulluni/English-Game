extends SceneTree

const DECK := preload("res://scripts/combat/deck_state.gd")
const FIXTURE := preload("res://tests/mechanics_fixture.gd")
var failures: Array[String] = []

func _initialize() -> void:
	_test_deck()
	_test_reactions()
	_test_erosion()
	_test_traits()
	_test_relics_and_anomaly()
	for failure in failures:
		push_error(failure)
	print("SEMANTIC_DECK_SMOKE: %s" % ("PASS" if failures.is_empty() else "FAIL (%d)" % failures.size()))
	quit(0 if failures.is_empty() else 1)

func _check(condition: bool, message: String) -> void:
	if not condition:
		failures.append(message)

func _usable():
	var word := preload("res://scripts/run/word_knowledge.gd").new()
	word.encounter()
	word.recognize("inscription")
	word.record_combat_context(true)
	word.record_transfer(true)
	word.record_production(true)
	return word

func _round(combat: CombatState) -> void:
	combat.end_player_turn()
	if combat.turn_ending and not combat.finished:
		combat.resolve_enemy_action(false)

func _test_deck() -> void:
	var deck := DECK.new()
	deck.reset(5)
	_check(deck.hand.size() == 5 and deck.draw_pile.size() == 5, "starter draws five from ten")
	var counts := {}
	var ids := {}
	for card in deck.hand + deck.draw_pile:
		counts[card.name] = int(counts.get(card.name, 0)) + 1
		ids[card.instance_id] = true
	_check(ids.size() == 10 and counts == {"SHATTER": 2, "OBSERVE": 2, "BIND": 2, "STABILIZE": 1, "DEFLECT": 1, "RESTORE": 1, "ERODE": 1}, "exact starter composition and unique instances")
	var original := deck.hand.duplicate()
	var three: Array[int] = [original[0].instance_id, original[1].instance_id, original[2].instance_id]
	_check(not deck.mulligan(three) and deck.hand == original, "three-card mulligan is atomic and rejected")
	var duplicate: Array[int] = [original[0].instance_id, original[0].instance_id]
	_check(not deck.mulligan(duplicate), "duplicate mulligan selection rejected")
	var two: Array[int] = [original[0].instance_id, original[1].instance_id]
	_check(deck.mulligan(two), "two-card opening mulligan accepted")
	_check(not original[0] in deck.hand and not original[1] in deck.hand, "mulligan cannot immediately redraw returned cards")
	_check(not deck.mulligan([]), "opening mulligan once only")
	var retained := int(deck.hand[0].instance_id)
	_check(deck.toggle_retain(retained, 1), "one Retain accepted")
	_check(not deck.toggle_retain(int(deck.hand[1].instance_id), 1), "default Retain limit enforced")
	deck.end_turn(false)
	_check(deck.hand.size() == 1 and int(deck.hand[0].instance_id) == retained, "only retained card persists")
	deck.retained_cards.clear()
	deck.draw_to(5)
	deck.end_turn(false)
	deck.draw_to(5)
	_check(deck.hand.size() == 5 and deck.hand.size() + deck.draw_pile.size() + deck.discard_pile.size() == 10, "discard reshuffles without losses or duplication")
	var combat := CombatState.new()
	combat.start_battle(0)
	_check(not combat.use_card(int(combat.deck.hand[0].instance_id)), "cannot play before opening hand confirmation")
	combat.finish_mulligan()
	combat.deck.hand.clear()
	_check(not combat.can_use("SHATTER"), "fixed skills unavailable without a matching hand card")

func _test_reactions() -> void:
	var combat := CombatState.new()
	combat.start_battle(0)
	combat.finish_mulligan()
	combat.intent = {"word": "LASH", "kind": "physical", "damage": 8}
	combat.deck.hand.clear()
	var card := combat.deck.make_card("DEFLECT")
	combat.deck.hand.append(card)
	_check(not combat.use_card(int(card.instance_id)), "DEFLECT cannot be played as a normal action")
	combat.end_player_turn()
	_check(combat.turn_ending and card in combat.deck.hand, "reaction card survives end-turn until enemy resolution")
	combat.resolve_enemy_action(true)
	_check(combat.armor == 10 and combat.metrics.deflect_uses == 1 and card in combat.deck.discard_pile, "Reaction spends and discards DEFLECT; reduces physical damage")
	combat.start_battle(0)
	combat.finish_mulligan()
	combat.deck.hand.clear()
	combat.intent = {"word": "LASH", "kind": "physical", "damage": 8}
	combat.end_player_turn()
	_check(combat.turn == 2 and combat.armor == 4, "without DEFLECT the hit resolves without a reaction window")
	combat.start_battle(0)
	combat.finish_mulligan()
	combat.deck.hand.clear()
	card = combat.deck.make_card("DEFLECT")
	combat.deck.hand.append(card)
	combat.deck.toggle_retain(int(card.instance_id), 1)
	_round(combat)
	_check(card in combat.deck.hand and combat.deck.retained_cards.is_empty(), "retained DEFLECT persists and next turn retention must be selected again")

func _test_erosion() -> void:
	var combat := CombatState.new()
	combat.start_battle(0)
	combat.finish_mulligan()
	combat.deck.hand.append(combat.deck.make_card("ERODE"))
	_check(not combat.can_use("ERODE"), "unlearned ERODE stays a context card")
	var word = _usable()
	_check(word.current_state == "USABLE" and "ERODE" in word.unlocked_cards, "knowledge unlocks ERODE build component")
	_check(not "fractured_erosion" in word.entry_text(), "combo remains hidden before discovery")
	combat.start_battle(0, {"knowledge": word})
	var hp := int(combat.enemy.hp)
	FIXTURE.play(combat, "ERODE")
	_check(combat.focus == 2 and combat.erosion_turns == 3, "ERODE cost one applies three turns")
	_round(combat)
	_check(int(combat.enemy.structure) == 16 and int(combat.enemy.hp) == hp and combat.erosion_turns == 2, "erosion ticks Structure not HP")
	combat.enemy.structure = 1
	_round(combat)
	_check(int(combat.enemy.structure) == 0 and int(combat.enemy.hp) == hp, "erosion collapse does not introduce direct HP damage")
	combat.enemy.armor = 4
	_round(combat)
	_check(int(combat.enemy.armor) == 3 and int(combat.enemy.hp) == hp and combat.erosion_turns == 0, "exposed erosion reduces extra Armor and expires")
	combat.start_battle(3, {"knowledge": word})
	combat.focus = 9
	FIXTURE.play(combat, "SHATTER")
	FIXTURE.play(combat, "ERODE")
	_check(word.discovered_combos.is_empty(), "reverse card order does not discover combination")
	combat.start_battle(3, {"knowledge": word})
	FIXTURE.play(combat, "ERODE")
	FIXTURE.play(combat, "SHATTER")
	_check(combat.erosion_turns == 4 and combat.erosion_tick == 3 and word.discovered_combos == ["fractured_erosion"], "ERODE then SHATTER upgrades erosion and records discovery")
	_check("FRACTURED EROSION" in word.entry_text(), "discovered combination appears in Lexicon")
	combat.erosion_turns = 0
	combat.focus = 3
	FIXTURE.play(combat, "ERODE")
	_check(combat.erosion_tick == 2, "new erosion after expiration does not inherit an old combination boost")

func _test_traits() -> void:
	var combat := CombatState.new()
	combat.start_battle(0)
	combat.finish_mulligan()
	combat.enemy.structure = 6
	_round(combat)
	_round(combat)
	_check(int(combat.enemy.structure) == 12, "Root Husk regrows six after two turns without structural pressure")
	combat.start_battle(0)
	FIXTURE.play(combat, "SHATTER")
	_round(combat)
	FIXTURE.play(combat, "SHATTER")
	_round(combat)
	combat.focus = 4
	combat.armor = 10
	combat.deck.hand.append(combat.deck.make_card("DEFLECT"))
	FIXTURE.play(combat, "SHATTER")
	_check(combat.pending_counter and combat.splinter_revealed, "third consecutive Shatter turn reveals Splinter counter")
	var armor := combat.armor
	combat.resolve_enemy_action(true)
	_check(not combat.pending_counter and combat.armor == armor - 1, "Splinter counter supports normal DEFLECT response")
	combat.start_battle(1)
	_check(combat.intent_options.size() == 2 and "Intent A" in combat.intent_title(), "Moth presents two unordered possible intents")
	FIXTURE.play(combat, "OBSERVE")
	_check(combat.false_removed and not "Intent A" in combat.intent_title(), "OBSERVE removes the false possibility")
	combat.start_battle(2, {"objective": "survive"})
	combat.finish_mulligan()
	for turn in range(4):
		_round(combat)
	_check(not combat.finished and combat.completed_rounds == 4, "survival does not finish early")
	_round(combat)
	_check(combat.finished and combat.hp > 0 and combat.enemy.hp > 0 and combat.completed_rounds == 5, "survival succeeds after five completed turns without a kill")
	combat.end_player_turn()
	_check(combat.completed_rounds == 5, "finished combat cannot settle twice")

func _test_relics_and_anomaly() -> void:
	var combat := CombatState.new()
	combat.start_battle(3, {"knowledge": _usable(), "relics": ["echo_chamber", "unfinished_sentence", "quiet_mind", "clear_lens"]})
	_check(combat.retain_slots() == 2 and combat.skill_cost("OBSERVE") == 0, "rule-changing Retain and first Observe discount")
	FIXTURE.play(combat, "ERODE")
	var echo: Dictionary = {}
	for card in combat.deck.hand:
		if card.echo:
			echo = card
	_check(not echo.is_empty() and combat.card_cost(echo) == 2 and "EXHAUST" in echo.time_properties, "Echo Chamber creates cost-plus-one exhaust copy")
	combat.use_card(int(echo.instance_id))
	_check(echo in combat.deck.exhaust_pile, "used Echo goes to Exhaust")
	combat.focus = 4
	FIXTURE.play(combat, "ERODE")
	var copies := 0
	for card in combat.deck.hand:
		if card.echo:
			copies += 1
	_check(copies == 0, "Echo Chamber cannot recursively generate copies or retrigger this turn")
	combat._add_corruption("Inattention", 14)
	combat._add_corruption("Inattention", 14)
	_check(combat.corruption.Inattention == 23, "Quiet Mind reduces only first Inattention gain by five")
	var manager := RunManager.new()
	manager.start_run()
	manager.state.current_layer = 1
	manager.state.next_reward_multiplier = 1.25
	manager.select_node("semantic_anomaly")
	manager.resolve_anomaly("examine")
	_check(manager.state.next_reward_multiplier == 1.25, "optional anomaly preserves Press On for the next rewarding node")
	_check(manager.state.current_layer == 1 and manager.state.temporary_cards == ["STABILIZE"], "anomaly grants temporary card without consuming route layer")
	var anomaly_found := false
	for node in manager.available_nodes():
		anomaly_found = anomaly_found or node.id == "semantic_anomaly"
	_check(not anomaly_found, "resolved anomaly cannot be farmed")
	combat.start_battle(1, manager.state.combat_snapshot())
	_check(combat.deck.hand.size() + combat.deck.draw_pile.size() == 11, "anomaly card joins next battle deck")
	manager.state.knowledge.enemy_records["ROOT HUSK"] = "revealed"
	manager.state.knowledge.discovered_combos.append("fractured_erosion")
	manager.start_run()
	_check(manager.state.knowledge.enemy_records.is_empty() and manager.state.knowledge.discovered_combos.is_empty() and manager.state.temporary_cards.is_empty(), "Restart clears run-local Codex, combinations and temporary rewards")
