extends SceneTree

var failures: Array[String] = []

func _initialize() -> void:
	_run.call_deferred()

func _settle() -> void:
	for frame in range(10):
		await process_frame

func _check(condition: bool, message: String) -> void:
	if not condition:
		failures.append(message)

func _press(screen: Control, index: int = 0) -> void:
	var button: Button = screen.modal.find_child("Action%d" % index, true, false)
	button.pressed.emit()
	await _settle()

func _run() -> void:
	var screen := (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(screen)
	await _settle()
	# Real dialogs: ERODE inference, TOXIC first exposure and context recognition.
	for choice in range(6):
		await _press(screen)
	_check(screen.run_manager.state.toxic_knowledge.current_state == "RECOGNIZED", "Toxic entry inference records Recognition without auto-unlocking")
	screen._select_node("iron_shell")
	await _settle()
	await _press(screen)
	_check("ARMOR 18/18" in screen.enemy_armor_label.text and "SEALED PLATING" in screen.tutorial_label.text, "Iron Shell displays all defensive resources and its trait")
	screen._on_end_turn()
	await _settle()
	_check("TOXIC · A NEW CONTEXT" == screen.modal.find_child("Title", true, false).text and screen.state.hp == 47, "actual poison consequence offers transfer during combat")
	await _press(screen)
	await _press(screen)
	await _press(screen)
	_check(screen.run_manager.state.toxic_knowledge.current_state == "USABLE" and not is_instance_valid(screen.modal) and screen.state.battle_index == 4 and screen.run_manager.state.current_layer == 0, "production unlocks Toxic and returns to the same combat, not the map")
	screen.state.focus = 0
	screen._refresh()
	await _settle()
	for column in screen.hand_row.get_children():
		var button: Button = column.get_child(0)
		_check(not button.disabled or ("NOT ENOUGH FOCUS" in button.text or "REACTION ONLY" in button.text or "REQUIRES USABLE" in button.text), "every disabled hand card displays a reason")
		var retain: Button = column.get_child(1)
		_check(retain.get_global_rect().end.y <= screen.hand_row.get_parent().get_global_rect().end.y + 1, "reason text does not push Retain below hand viewport")
	# UI-only synthetic settlement moves to a separately tested Ghost branch.
	screen._on_battle_finished(true)
	screen._clear_modal()
	screen._select_node("root_husk")
	screen._clear_modal()
	screen._on_battle_finished(true)
	screen._clear_modal()
	screen._select_node("ghost")
	screen._clear_modal()
	screen.state.finish_mulligan()
	screen._refresh()
	await _settle()
	_check("STRUCTURE NONE" in screen.enemy_armor_label.text and "HIGH TOXIC RESISTANCE" in screen.tutorial_label.text, "Ghost shows no Structure and high resistance")
	_check(not screen.enemy_armor_bar.visible and screen.enemy_armor_bar.max_value == 1, "no-Structure targets never render a misleading full Structure bar")
	screen._on_end_turn()
	await _settle()
	_check("FADED" in screen.tutorial_label.text, "Ghost's phase appears in the status area")
	var card: Dictionary = screen.state.deck.hand[0]
	screen.state.deck.toggle_retain(int(card.instance_id), 1)
	screen.state.resolve_enemy_action(false)
	screen._clear_modal()
	screen._refresh()
	await _settle()
	var retained_button: Button = screen.hand_row.get_child(0).get_child(1)
	_check(retained_button.disabled and retained_button.text == "CANNOT RETAIN CONSECUTIVELY", "retained instance has a persistent visible reason on next turn")
	screen._show_lexicon()
	await _settle()
	_check("Word: TOXIC" in screen.modal.find_child("Body", true, false).text, "Lexicon includes Toxic's state and semantic mechanism")
	await _press(screen)
	screen._show_semantic_anomaly()
	await _settle()
	var body: Label = screen.modal.find_child("Body", true, false)
	_check("Which concept" in body.text and "Known concept" in body.text, "semantic event asks for judgment and offers recognized-word hints")
	# Apply USABLE through the real knowledge interface to expose its hidden option.
	var word = screen.run_manager.state.knowledge
	word.record_combat_context(true)
	word.record_transfer(true)
	word.record_production(true)
	screen._show_semantic_anomaly()
	await _settle()
	_check("ANCHOR THE MISSING CONCEPT" == screen.modal.find_child("Action3", true, false).text, "USABLE adds the hidden semantic option")
	screen.queue_free()
	await process_frame
	for failure in failures:
		push_error(failure)
	print("ECOLOGY_UI_SMOKE: %s" % ("PASS" if failures.is_empty() else "FAIL"))
	quit(0 if failures.is_empty() else 1)
