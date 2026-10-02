extends SceneTree

var failures: Array[String] = []

func _initialize() -> void:
	# A real deck, no injected cards / Focus / healing: exercise full encounter flow.
	var manager := RunManager.new()
	manager.start_run()
	var word = manager.state.knowledge
	word.encounter()
	word.recognize("inscription")
	for node_id in ["root_husk", "veil_moth", "neglect_wraith"]:
		var node := manager.select_node(node_id)
		var snapshot := manager.state.combat_snapshot()
		snapshot["objective"] = node.get("objective", "kill")
		var combat := CombatState.new()
		combat.start_battle(int(node.battle), snapshot)
		manager.state.temporary_cards.clear()
		var replace: Array[int] = []
		for card in combat.deck.hand:
			if replace.size() < 2 and (card.name == "ERODE" and word.current_state != "USABLE" or card.name == "STABILIZE" and combat.dominant_corruption_family().is_empty()):
				replace.append(int(card.instance_id))
		combat.finish_mulligan(replace)
		for step in range(60):
			if combat.finished:
				break
			var reserve := combat.reaction_cost() if combat.can_react() and combat.intent.kind == "physical" else 0
			for action in ["OBSERVE", "RESTORE", "STABILIZE", "ERODE", "STRIKE", "SHATTER", "BIND"]:
				for card in combat.deck.hand.duplicate():
					if card.name != action or not combat.can_use(action, int(card.instance_id)):
						continue
					if action == "OBSERVE" and not (word.current_state == "RECOGNIZED" or combat.battle_index == 1 and not combat.false_removed):
						continue
					if action == "RESTORE" and combat.hp > 42:
						continue
					if action == "STABILIZE" and combat.dominant_corruption_family().is_empty():
						continue
					if action == "ERODE" and combat.erosion_turns > 1:
						continue
					if combat.focus - combat.card_cost(card) < reserve and action != "RESTORE":
						continue
					combat.use_card(int(card.instance_id), "hp" if action == "RESTORE" else "")
					if combat.pending_counter:
						combat.resolve_enemy_action(combat.can_react())
					if combat.finished:
						break
			if combat.finished:
				break
			for card in combat.deck.hand:
				if card.name == "STRIKE" or card.name == "DEFLECT" or card.name == "ERODE" and word.current_state == "USABLE":
					combat.deck.toggle_retain(int(card.instance_id), combat.retain_slots())
			combat.end_player_turn()
			if combat.turn_ending:
				combat.resolve_enemy_action(combat.can_react())
		print("PLAYTHROUGH · %s · HP %d · Rounds %d" % [node_id, combat.hp, combat.completed_rounds])
		if not combat.finished or combat.hp <= 0:
			failures.append("Legal-card playthrough failed: %s" % node_id)
			break
		manager.complete_combat(combat)
		manager.choose_breather("recover")
		if node_id == "root_husk":
			manager.claim_relic("clear_lens")
			manager.select_node("semantic_anomaly")
			manager.resolve_anomaly("erode")
		elif node_id == "veil_moth":
			word.record_transfer(true)
			word.record_production(true)
	if failures.is_empty():
		manager.select_node("extract")
		manager.extract()
		if not manager.state.extracted or word.current_state != "USABLE":
			failures.append("Playthrough must finish with extraction and usable knowledge")
	for failure in failures:
		push_error(failure)
	print("PLAYTHROUGH_SMOKE: %s" % ("PASS" if failures.is_empty() else "FAIL"))
	quit(0 if failures.is_empty() else 1)
