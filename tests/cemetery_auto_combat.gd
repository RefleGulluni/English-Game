extends RefCounted

# Legal drawn-card policy; no synthetic cards, HP, Focus or knowledge advantages.
static func fight(c: CombatState) -> bool:
	var replace: Array[int] = []
	for card in c.deck.hand:
		if replace.size() < 2 and card.name in ["ERODE", "TOXIC"] and c.word_for(card.name).current_state != "USABLE":
			replace.append(int(card.instance_id))
	c.finish_mulligan(replace)
	for turn in range(90):
		if c.finished: break
		var order: Array[String] = ["RESTORE", "OBSERVE", "TOXIC", "ERODE", "STRIKE", "SHATTER", "STABILIZE", "BIND"]
		if c.bone_remains: order = ["SHATTER", "RESTORE", "STRIKE", "BIND", "STABILIZE"]
		for action in order:
			for card in c.deck.hand.duplicate():
				if card.name != action or not c.can_use(action, int(card.instance_id)): continue
				var reserve := c.reaction_cost() if c.can_react() and c.intent.kind == "physical" and not c.bone_remains else 0
				if action == "RESTORE" and c.hp > 42: continue
				if action == "OBSERVE" and not (c.enemy.phase_state == "FADED" or not c.false_intent.is_empty() and not c.false_removed or bool(c.intent.get("hidden", false)) and not c.hidden_revealed or c.mourning >= 3): continue
				if action == "TOXIC" and (c.enemy_effects.duration("POISONED") > 1 or c.poison_tick_damage() < 3): continue
				if action == "ERODE" and c.erosion_turns > 1: continue
				if action == "SHATTER" and c.enemy.structure <= 0 and not c.bone_remains: continue
				if action == "STABILIZE" and int(c.corruption.get(c.dominant_corruption_family(), 0)) < 20: continue
				if c.focus - c.card_cost(card) < reserve and action != "RESTORE": continue
				c.use_card(int(card.instance_id), "hp" if action == "RESTORE" else "")
				if c.pending_counter: c.resolve_enemy_action(c.can_react())
				if c.finished: break
			if c.finished: break
		if c.finished: break
		for card in c.deck.hand:
			if card.name in (["SHATTER", "STRIKE"] if c.bone_remains else ["STRIKE", "DEFLECT", "TOXIC"]):
				c.deck.toggle_retain(int(card.instance_id), c.retain_slots())
		c.end_player_turn()
		if c.turn_ending: c.resolve_enemy_action(c.can_react())
	return c.finished and c.hp > 0
