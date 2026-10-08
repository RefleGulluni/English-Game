extends SceneTree

var failures: Array[String] = []

func _initialize() -> void:
	_run.call_deferred()

func settle() -> void:
	for frame in range(10): await process_frame

func check(value: bool, message: String) -> void:
	if not value: failures.append(message)

func capture(screen: Control, filename: String) -> void:
	var directory := OS.get_environment("CEMETERY_QA_DIR")
	if directory.is_empty(): return
	await RenderingServer.frame_post_draw
	var result := screen.get_viewport().get_texture().get_image().save_png(directory.path_join(filename))
	check(result == OK, "rendered QA screenshot saved")

func press(screen: Control, index: int = 0) -> void:
	var button: Button = screen.modal.find_child("Action%d" % index, true, false)
	button.pressed.emit()
	await settle()

func press_text(screen: Control, text: String) -> void:
	for button in screen.modal.find_child("Actions", true, false).get_children():
		if button is Button and button.text == text:
			button.pressed.emit()
			await settle()
			return
	check(false, "exercise choice exists: " + text)

func _run() -> void:
	var screen := (load("res://scenes/main.tscn") as PackedScene).instantiate()
	screen.set_meta("legacy_cemetery", true)
	root.add_child(screen)
	await settle()
	check(screen.run_manager.cemetery and screen.modal.find_child("Title", true, false).text == "CEMETERY ENTRY", "actual main scene launches Cemetery 0.7")
	check(screen.run_manager.state.target_knowledge.size() == 5, "five target words shown")
	for index in range(6): await press(screen)
	check("CEMETERY MAP" in screen.modal.find_child("Title", true, false).text, "old inscription and Toxic first exposure return to Cemetery map")
	await capture(screen, "map.png")
	screen._show_dev_panel()
	await settle()
	check(screen.dev_open and "DEV PANEL" in screen.modal.find_child("Title", true, false).text, "DEV opens over active map")
	screen._show_dev_input("Seed")
	await settle()
	var input: LineEdit = screen.modal.find_child("DevInput", true, false)
	check(is_instance_valid(input), "DEV uses actual editable input")
	input.text = "707"
	await capture(screen, "dev_input.png")
	await press(screen)
	check(screen.run_manager.state.seed_value == 707 and screen.run_manager.state.target_knowledge.MOURN.current_state == "UNKNOWN", "seed input resets reproducible run and knowledge")
	screen._show_map()
	screen._show_dev_panel()
	screen._show_dev_input("HP")
	await settle()
	input = screen.modal.find_child("DevInput", true, false)
	input.text = "99"
	await press(screen)
	check(screen.run_manager.state.hp == 50 and screen.modal.find_child("Title", true, false).text == "INVALID DEV VALUE", "invalid range does not mutate run")
	check(screen._dev_apply("Layer", "5"), "Layer DEV supports valid range")
	await settle()
	check(screen.run_manager.state.current_layer == 4 and screen.run_manager.available_nodes().any(func(n): return bool(n.get("guarantee", false))), "Layer five reveals learning compensation")
	var node: Dictionary = screen.run_manager.available_nodes()[0]
	screen._select_node(str(node.id))
	await settle()
	check("LEAVE THIS EVENT" == screen.modal.find_child("Action4", true, false).text, "compensation event offers all missing core words")
	await press(screen, 0)
	await press_text(screen, "restore physical health immediately")
	check(screen.run_manager.state.target_knowledge.MOURN.current_state == "ENCOUNTERED", "wrong recognition preserves gate")
	await press(screen)
	await press_text(screen, str(preload("res://scripts/run/cemetery_words.gd").DATA.MOURN[0]))
	check("CONTEXT" in screen.modal.find_child("Title", true, false).text, "correct inference offers a separate context")
	await press_text(screen, str(preload("res://scripts/run/cemetery_words.gd").DATA.MOURN[2]))
	check("PRODUCTION" in screen.modal.find_child("Title", true, false).text, "understanding offers actual production choice")
	await capture(screen, "production.png")
	await press_text(screen, "MOURN")
	check(screen.run_manager.state.target_knowledge.MOURN.current_state == "USABLE", "full UI exercise completes learning")
	screen._show_lexicon()
	await settle()
	check("Word: MOURN" in screen.modal.find_child("Body", true, false).text and "Word: REASSEMBLE" in screen.modal.find_child("Body", true, false).text, "Lexicon lists independent targets")
	await press(screen)
	screen._finish_cemetery_lesson()
	await settle()
	check(screen.run_manager.state.current_layer == 5 and "CEMETERY MAP" in screen.modal.find_child("Title", true, false).text, "leaving learning event settles once and returns to Boss map")
	screen._select_node("mourning_keeper")
	await settle()
	check(screen.lesson_is_combat, "Boss's vocabulary path is combat recognition, not free full learning")
	screen._finish_cemetery_lesson()
	await settle()
	await press(screen)
	check(not is_instance_valid(screen.modal) and screen.state.battle_index == 9, "confirmed opening hand enters Boss")
	screen._show_dev_panel()
	screen._show_weight_inspector()
	await settle()
	check("Final = Base" in screen.modal.find_child("Body", true, false).text, "Weight Inspector exposes equation")
	screen._close_dev_panel()
	screen._clear_modal()
	screen._show_relic_reward("QA reward")
	await settle()
	check(screen.modal.find_child("Action3", true, false).text == "SKIP RELIC", "Relic reward three choices plus skip")
	await press(screen, 3)
	check(screen.run_manager.state.relics.is_empty(), "skip does not grant Relic")
	screen._dev_enter_enemy(7)
	await settle()
	await press(screen)
	check(screen._dev_apply("Word State", "reassembled,UNDERSTOOD"), "DEV accepts inflected lemma")
	check(screen.run_manager.state.target_knowledge.REASSEMBLE.current_state == "UNDERSTOOD", "inflection shares same entry")
	check(screen._dev_apply("Relic", "ossuary_key") and screen._dev_apply("Grave Pressure", "4"), "DEV updates Relic and Pressure")
	screen.state.enemy.hp = 0
	screen.state._enemy_defeated()
	screen._refresh()
	check("BONE REMAINS" in screen.tutorial_label.text, "Remains visible in live status panel")
	check("REASSEMBLE · UNDERSTOOD" in screen.knowledge_indicator.text, "knowledge indicator identifies the current target Word, not ERODE by default")
	check("INTEGRITY 10/10" in screen.enemy_armor_label.text and screen.enemy_armor_bar.value == 10, "Remains display their own integrity rather than old Skeleton Structure")
	check("SHATTER -10 / STRIKE -5" in screen.intent_text.text, "Remains instructions include current Key bonus")
	await settle()
	await capture(screen, "bone_remains.png")
	screen._dev_reset_lexicon()
	check(screen.run_manager.state.target_knowledge.REASSEMBLE.current_state == "UNKNOWN", "DEV reset clears target knowledge")
	screen._clear_modal()
	screen._dev_abandon_previous()
	screen.run_manager.state.victory = true
	screen._show_run_summary()
	await settle()
	check(screen.modal.find_child("Title", true, false).text == "BIOME CLEAR" and "Seed 707" in screen.modal.find_child("Body", true, false).text and "Boss Result" in screen.modal.find_child("Body", true, false).text, "Boss summary includes Seed, words, relics and result")
	await capture(screen, "summary.png")
	screen._restart_run()
	await settle()
	check(screen.state.enemy.is_empty() and screen.state.hp == 50 and screen.run_manager.state.target_knowledge.MOURN.current_state == "UNKNOWN", "Restart clears previous enemy, resources and run-local target knowledge")
	screen.queue_free()
	await process_frame
	for message in failures: push_error(message)
	print("CEMETERY_UI_SMOKE: %s" % ("PASS" if failures.is_empty() else "FAIL"))
	quit(0 if failures.is_empty() else 1)
