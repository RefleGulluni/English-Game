extends RefCounted

# Old rule tests isolate effects; real deck availability is covered separately.
static func play(combat: CombatState, name: String, target: String = "") -> bool:
	if combat.deck.mulligan_pending:
		combat.finish_mulligan()
	var card := combat.deck.make_card(name)
	combat.deck.hand.append(card)
	return combat.use_card(int(card["instance_id"]), target)
