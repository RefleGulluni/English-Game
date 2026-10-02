extends RefCounted

const CARDS := preload("res://scripts/combat/card_definitions.gd")
var draw_pile: Array[Dictionary] = []
var hand: Array[Dictionary] = []
var discard_pile: Array[Dictionary] = []
var exhaust_pile: Array[Dictionary] = []
var retained_cards: Array[int] = []
var rng := RandomNumberGenerator.new()
var next_id := 0
var mulligan_pending := true
var mulligan_used := false

func reset(seed_value: int, temporary_cards: Array = []) -> void:
	for pile in [draw_pile, hand, discard_pile, exhaust_pile]:
		pile.clear()
	retained_cards.clear()
	next_id = 0
	rng.seed = seed_value
	mulligan_pending = true
	mulligan_used = false
	for card_id in CARDS.STARTER:
		draw_pile.append(make_card(card_id))
	for card_id in temporary_cards:
		var card := make_card(str(card_id))
		card["time_properties"].append("EXHAUST")
		card["temporary"] = true
		card["exhaust_on_use"] = true
		draw_pile.append(card)
	_shuffle(draw_pile)
	draw_to(5)

func make_card(card_id: String, cost_bonus: int = 0, echo_copy: bool = false) -> Dictionary:
	var card := CARDS.definition(card_id)
	card["instance_id"] = next_id
	next_id += 1
	card["cost_bonus"] = cost_bonus
	card["echo"] = echo_copy
	if echo_copy:
		card["time_properties"].append("EXHAUST")
		card["temporary"] = true
		card["exhaust_on_use"] = true
	return card

func _shuffle(pile: Array[Dictionary]) -> void:
	for index in range(pile.size() - 1, 0, -1):
		var other := rng.randi_range(0, index)
		var card := pile[index]
		pile[index] = pile[other]
		pile[other] = card

func draw_to(target: int) -> void:
	while hand.size() < target:
		if draw_pile.is_empty():
			if discard_pile.is_empty():
				break
			draw_pile.append_array(discard_pile)
			discard_pile.clear()
			_shuffle(draw_pile)
		var card: Dictionary = draw_pile.pop_back()
		card["retained_last_turn"] = false
		hand.append(card)

func find_card(card_id: String, instance_id: int = -1) -> Dictionary:
	for card in hand:
		if str(card["card_id"]) == card_id and (instance_id < 0 or int(card["instance_id"]) == instance_id):
			return card
	return {}

func consume(card: Dictionary) -> void:
	hand.erase(card)
	retained_cards.erase(int(card["instance_id"]))
	if "EXHAUST" in card["time_properties"]:
		exhaust_pile.append(card)
	else:
		discard_pile.append(card)

func toggle_retain(instance_id: int, slots: int) -> bool:
	if mulligan_pending:
		return false
	for card in hand:
		if int(card["instance_id"]) == instance_id:
			if instance_id in retained_cards:
				retained_cards.erase(instance_id)
				return true
			if bool(card.get("retained_last_turn", false)):
				return false
			if retained_cards.size() < slots:
				retained_cards.append(instance_id)
				return true
	return false

func end_turn(keep_reactions: bool = true) -> void:
	for card in hand.duplicate():
		if int(card["instance_id"]) in retained_cards:
			continue
		if keep_reactions and "REACTION" in card["time_properties"]:
			continue
		hand.erase(card)
		discard_pile.append(card)

func begin_turn() -> void:
	# Mark only instances that survived in hand. Redrawing resets eligibility.
	for card in hand:
		card["retained_last_turn"] = int(card["instance_id"]) in retained_cards
	retained_cards.clear()
	draw_to(5)

func mulligan(ids: Array[int]) -> bool:
	if not mulligan_pending or mulligan_used or ids.size() > 2:
		return false
	var replacements: Array[Dictionary] = []
	for instance_id in ids:
		var found := false
		for card in hand:
			if int(card["instance_id"]) == instance_id and not card in replacements:
				replacements.append(card)
				found = true
		if not found:
			return false
	for card in replacements:
		hand.erase(card)
	# Draw replacements before putting returned cards back: no immediate redraw.
	draw_to(5)
	draw_pile.append_array(replacements)
	_shuffle(draw_pile)
	mulligan_pending = false
	mulligan_used = true
	return true
