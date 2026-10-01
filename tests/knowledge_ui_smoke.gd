extends SceneTree

var failures: Array[String] = []

func _initialize() -> void:
	_run.call_deferred()

func _settle() -> void:
	for frame in range(8):
		await process_frame

func _press(screen: Control, index: int) -> void:
	var button: Button = screen.modal.find_child("Action%d" % index, true, false)
	button.pressed.emit()
	await _settle()

func _run() -> void:
	var screen := (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(screen)
	await _settle()
	await _press(screen, 0)
	var knowledge = screen.run_manager.state.knowledge
	_check(knowledge.current_state == "ENCOUNTERED", "entry leads to inscription discovery")
	var previous: Control = screen.modal
	screen._show_lexicon()
	await _settle()
	_check(not previous.visible and "ENCOUNTERED" in screen.modal.find_child("Body", true, false).text, "Lexicon shows state while retaining the active decision")
	await _press(screen, 0)
	_check(screen.modal == previous and previous.visible, "closing Lexicon restores the previous dialog")
	await _press(screen, 0)
	await _press(screen, 0)
	_check(knowledge.current_state == "RECOGNIZED", "correct inference grants Recognition Evidence")
	await _press(screen, 0)
	await _press(screen, 0)
	_check(screen.state.enemy["name"] == "ROOT HUSK" and screen.state.intent_clarity == 1, "map launches recognized ERODE combat")
	_check("KNOWN WORD" in screen.knowledge_indicator.text, "combat explains its knowledge advantage")
	screen._on_skill_pressed("OBSERVE")
	await _settle()
	_check(knowledge.current_state == "UNDERSTOOD", "combat reading updates the same Lexicon object")
	screen.state.resolve_enemy_action(false)
	screen._on_battle_finished(true)
	await _settle()
	await _press(screen, 0)
	await _press(screen, 0)
	_check("A NEW CONTEXT" in screen.modal.find_child("Title", true, false).text, "post-combat Breather leads to third context")
	await _press(screen, 0)
	await _press(screen, 0)
	await _press(screen, 0)
	_check(knowledge.current_state == "USABLE", "third context and production complete the UI loop")
	await _press(screen, 0)
	_check(screen.run_manager.state.current_layer == 1, "learning interludes do not consume route layers")
	screen._show_lexicon()
	await _settle()
	_check("ERODE INSIGHT" in screen.modal.find_child("Body", true, false).text, "Lexicon reports unlocked Insight")
	await _press(screen, 0)
	screen._restart_run()
	await _settle()
	_check(knowledge.current_state == "UNKNOWN", "restart starts a fresh knowledge loop")
	screen._show_inscription()
	screen._answer_recognition("explode")
	await _settle()
	_check(knowledge.current_state == "ENCOUNTERED" and screen.run_manager.state.hp == 50 and screen.run_manager.state.echo == 0, "wrong inference has no resource or knowledge reward")
	screen._finish_inscription()
	screen._clear_modal()
	screen._select_node("root_husk")
	await _settle()
	_check(screen.state.intent_clarity == 0, "unknown ERODE does not gain knowledge clarity")
	screen._on_skill_pressed("OBSERVE")
	await _settle()
	_check(knowledge.context_evidence == 0, "one OBSERVE without semantic recognition does not grant understanding")
	screen.queue_free()
	await process_frame
	for failure in failures:
		push_error(failure)
	print("KNOWLEDGE_UI_SMOKE: %s" % ("PASS" if failures.is_empty() else "FAIL"))
	quit(0 if failures.is_empty() else 1)

func _check(condition: bool, message: String) -> void:
	if not condition:
		failures.append(message)
