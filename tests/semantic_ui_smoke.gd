extends SceneTree

var failures: Array[String] = []

func _initialize() -> void:
	_run.call_deferred()

func _settle() -> void:
	for frame in range(8):
		await process_frame

func _check(condition: bool, message: String) -> void:
	if not condition:
		failures.append(message)

func _run() -> void:
	var screen := (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(screen)
	await _settle()
	screen._finish_inscription()
	screen._select_node("root_husk")
	await _settle()
	_check(screen.state.deck.mulligan_pending and "OPENING HAND" == screen.modal.find_child("Title", true, false).text, "real combat opens the Mulligan UI")
	var first := int(screen.state.deck.hand[0].instance_id)
	var second := int(screen.state.deck.hand[1].instance_id)
	var third := int(screen.state.deck.hand[2].instance_id)
	screen._toggle_mulligan(first)
	screen._toggle_mulligan(second)
	screen._toggle_mulligan(third)
	_check(screen.mulligan_selection.size() == 2, "UI cannot select a third replacement")
	var confirm: Button = screen.modal.find_child("Action0", true, false)
	confirm.pressed.emit()
	await _settle()
	_check(not is_instance_valid(screen.modal) and screen.hand_row.get_child_count() == 5 and not screen.end_turn_button.disabled, "confirm reveals five live hand cards and enables End Turn")
	var retained := int(screen.state.deck.hand[0].instance_id)
	var retain_button: Button = screen.hand_row.get_child(0).get_child(1)
	retain_button.pressed.emit()
	await _settle()
	_check(screen.state.deck.retained_cards == [retained] and "RETAIN 1/1" in screen.pile_label.text, "Retain button selects its own card and updates pile UI")
	var observe: Dictionary = screen.state.deck.find_card("OBSERVE")
	if not observe.is_empty():
		var uid := int(observe.instance_id)
		var button: Button = screen.hand_row.find_child("Card%d" % uid, true, false)
		button.pressed.emit()
		await _settle()
		_check(observe in screen.state.deck.discard_pile, "hand button plays and discards the exact instance")
	screen._on_end_turn()
	await _settle()
	_check(screen.state.turn == 2 and screen.state.deck.hand.size() == 5, "normal end-turn transitions refill the UI hand")
	_check(int(screen.state.enemy.armor) == 0 and "STRUCTURE" in screen.enemy_armor_label.text, "HUD separates Structure from extra Armor")
	_check("REGROWTH" in screen.tutorial_label.text, "enemy trait appears in a bounded scroll region")
	screen.state.battle_index = 2
	for tier in [2, 3, 4]:
		screen.state.inattention_tier = tier
		screen._show_reaction({"word": "BLUNT CUT"}, 2)
		await _settle()
		var body: Label = screen.modal.find_child("Body", true, false)
		if tier == 2:
			_check("incoming" in body.text and not "reserved" in body.text, "PRESSURED simplifies Reaction wording")
		elif tier == 3:
			_check("Details are obscured" in body.text, "CARELESS hides details")
		else:
			_check(body.text == "Reaction Available", "NEGLIGENT shows only Reaction Available")
		screen._clear_modal()
	screen._show_lexicon()
	await _settle()
	_check("COMBAT CODEX" in screen.modal.find_child("Body", true, false).text, "Lexicon includes encountered enemy traits")
	screen.queue_free()
	await process_frame
	for failure in failures:
		push_error(failure)
	print("SEMANTIC_UI_SMOKE: %s" % ("PASS" if failures.is_empty() else "FAIL"))
	quit(0 if failures.is_empty() else 1)
