extends SceneTree

var failures: Array[String] = []
var checks := 0

func _initialize() -> void:
	_run.call_deferred()

func check(value: bool, message: String) -> void:
	checks += 1
	if not value: failures.append(message)

func settle() -> void:
	for frame in range(12): await process_frame

func press(screen: Control, text: String = "") -> void:
	for button in screen.modal.find_child("Actions", true, false).get_children():
		if button is Button and (text.is_empty() or button.text == text):
			button.pressed.emit()
			await settle()
			return
	check(false, "button exists: " + text)

func capture(screen: Control, name: String) -> void:
	var directory := OS.get_environment("PACING_QA_DIR")
	if directory.is_empty() or DisplayServer.get_name() == "headless": return
	await RenderingServer.frame_post_draw
	check(screen.get_viewport().get_texture().get_image().save_png(directory.path_join(name + ".png")) == OK, "rendered capture succeeds")

func _run() -> void:
	var screen := (load("res://scenes/ui/legacy_combat.tscn") as PackedScene).instantiate()
	screen.set_meta("qa_no_save", true)
	root.add_child(screen)
	await settle()
	check(screen.run_manager.pacing and screen.run_manager.learning.active_pool.size() == 6, "actual entry uses Director 2.0")
	await capture(screen, "entry")
	await press(screen, "ENTER CEMETERY")
	check("CEMETERY MAP" in screen.modal.find_child("Title", true, false).text, "entry skips old outside-map chained exercises")
	check(screen.modal.find_child("Actions", true, false).get_child_count() == 4, "three route choices plus pace setting")
	await capture(screen, "map")
	screen._show_learning_pace()
	await press(screen, "More Review")
	check(screen.run_manager.learning.pace == "More Review", "real pace selection works")
	# Use the documented DEV world-event tool to isolate UI exercise behavior.
	check(screen._dev_apply("Event", "mourning_stone"), "DEV world encounter tool works")
	await settle()
	var id: String = screen.run_manager.selected_node.primary
	check(not id.is_empty(), "native event carries one primary focus")
	await press(screen, "EXAMINE THE SCENE")
	var resources := [screen.run_manager.state.hp, screen.run_manager.state.armor, screen.run_manager.state.echo, screen.state.focus]
	var wrong := str(screen.current_learning_exercise.options[1])
	await press(screen, wrong)
	check(resources == [screen.run_manager.state.hp, screen.run_manager.state.armor, screen.run_manager.state.echo, screen.state.focus], "QA06: wrong answer costs no resources")
	check(screen.modal.find_child("Actions", true, false).get_child_count() == 1 and not screen.modal.find_child("Body", true, false).text.contains("WRONG"), "QA06: natural correction, no retry loop")
	await capture(screen, "corrective")
	await press(screen, "CONTINUE")
	check(screen.run_manager.learning.cooldown(id) == 2, "completed UI opportunity starts correct cooldown")
	# Isolate the next UI test, without bypassing the real runtime stochastic pacing rules.
	screen.run_manager.director.history.clear()
	screen._dev_apply("Event", "scattered_bones")
	await settle()
	id = str(screen.run_manager.selected_node.primary)
	if id.is_empty():
		screen.run_manager.learning.active_pool.assign(["REASSEMBLE", "MOURN", "LINGER", "CONCEAL", "ERODE", "TOXIC"])
		screen._dev_apply("Event", "scattered_bones")
		await settle()
		id = str(screen.run_manager.selected_node.primary)
	await press(screen, "EXAMINE THE SCENE")
	await press(screen, str(screen.current_learning_exercise.correctAnswer))
	check(screen.run_manager.learning.words[id].current_state == "RECOGNIZED", "one actual answer earns only recognition")
	check(screen.modal.find_child("Actions", true, false).get_child_count() == 1, "no chained context/production after success")
	await press(screen, "CONTINUE")
	screen._show_lexicon()
	await settle()
	var rows: Label = screen.modal.find_child("Lexicon_MOURN", true, false)
	check(rows != null and rows.text.contains("Current State"), "Lexicon keeps words readable")
	check(not rows.text.contains("Familiarity"), "hidden familiarity numbers not shown to players")
	await capture(screen, "lexicon")
	await press(screen, "CLOSE LEXICON")
	screen._show_dev_panel()
	screen._show_learning_inspector()
	await settle()
	check(screen.modal.find_child("Body", true, false).text.contains("Cooldown"), "Learning Inspector exposes diagnostics")
	await capture(screen, "learning_inspector")
	screen._show_pacing_weights()
	await settle()
	check(screen.modal.find_child("Body", true, false).text.contains("Eligible Group"), "weight inspector exposes actual normalization")
	await capture(screen, "weights")
	screen._dev_enter_enemy(7)
	await settle()
	await press(screen)
	check(not is_instance_valid(screen.modal), "combat starts without independent learning event")
	screen._dev_apply("Word State", "TOXIC,RECOGNIZED")
	# Diagnostic combat context through the actual knowledge interface must not open old toxic training.
	screen.run_manager.learning.begin({"id": "grave_skeleton", "title": "Skeleton", "primary": "TOXIC", "words": ["TOXIC"], "tags": ["COMBAT", "RISK"]}, 3)
	screen.state.toxic_knowledge.record_combat_context(true)
	await settle()
	check(screen.state.toxic_knowledge.current_state == "UNDERSTOOD" and not is_instance_valid(screen.modal), "QA16: combat evidence logs without a learning popup")
	screen._offer_toxic_training()
	await settle()
	check(not is_instance_valid(screen.modal), "QA16: stale deferred old training is disabled")
	check(screen.run_manager.dev_sandbox and screen.run_manager.learning.save_path.is_empty(), "DEV changes isolated from real persistent save")
	screen._restart_run()
	await settle()
	check(screen.run_manager.state.toxic_knowledge.current_state == "UNDERSTOOD", "restart keeps earned knowledge")
	check(screen.enemy_name.text == "CHOOSE A PATH" and screen.hand_row.get_child_count() == 0, "restart clears old enemy and hand visually, not only in memory")
	screen._show_cemetery_rest()
	await settle()
	check(screen.modal.find_child("Actions", true, false).get_child_count() == 4, "four selective recovery directions")
	await capture(screen, "recovery")
	screen.queue_free()
	await settle()
	for message in failures: push_error(message)
	print("PACING_UI_SMOKE: %s · %d checks" % ["PASS" if failures.is_empty() else "FAIL", checks])
	quit(0 if failures.is_empty() else 1)
