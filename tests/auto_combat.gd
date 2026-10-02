extends RefCounted

# Deterministic legal-card policy for integration checks, not a balance oracle.
static func fight(combat: CombatState, learn_toxic: bool = false) -> bool:
	var replace: Array[int] = []
	for card in combat.deck.hand:
		if replace.size() < 2 and (card.name in ["ERODE", "TOXIC"] and combat.word_for(card.name).current_state != "USABLE" or card.name == "STABILIZE" and combat.dominant_corruption_family().is_empty()):
			replace.append(int(card.instance_id))
	combat.finish_mulligan(replace)
	for step in range(60):
		if combat.finished:
			break
		if learn_toxic and combat.toxic_knowledge.current_state == "UNDERSTOOD":
			combat.toxic_knowledge.record_transfer(true)
			combat.toxic_knowledge.record_production(true)
		var reserve := combat.reaction_cost() if combat.can_react() and combat.intent.kind == "physical" else 0
		for action in ["OBSERVE", "RESTORE", "STABILIZE", "TOXIC", "ERODE", "STRIKE", "SHATTER", "BIND"]:
			for card in combat.deck.hand.duplicate():
				if card.name != action or not combat.can_use(action, int(card.instance_id)):
					continue
				if action == "OBSERVE" and not (combat.knowledge.current_state == "RECOGNIZED" or combat.battle_index == 1 and not combat.false_removed or combat.enemy.phase_state == "FADED"):
					continue
				if action == "RESTORE" and combat.hp > 42:
					continue
				if action == "TOXIC" and (combat.enemy_effects.duration("POISONED") > 1 or combat.poison_tick_damage() < 3):
					continue
				if action == "ERODE" and combat.erosion_turns > 1:
					continue
				if action == "SHATTER" and combat.enemy.structure <= 0:
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
			if card.name in ["STRIKE", "DEFLECT", "TOXIC"]:
				combat.deck.toggle_retain(int(card.instance_id), combat.retain_slots())
		combat.end_player_turn()
		if combat.turn_ending:
			combat.resolve_enemy_action(combat.can_react())
	return combat.finished and combat.hp > 0
