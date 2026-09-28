extends SceneTree

var failures: Array[String] = []

func _initialize() -> void:
	_run.call_deferred()

func _run() -> void:
	var scene := load("res://scenes/main.tscn") as PackedScene
	var screen := scene.instantiate()
	root.add_child(screen)
	await process_frame
	_check(is_instance_valid(screen.modal), "Run opens at the Fracture Entry modal")

	screen._select_node("fracture_event")
	await process_frame
	_check(screen.run_manager.current_event.has("choices"), "Event UI receives structured event choices")
	screen._resolve_event_choice("leave")
	await process_frame
	_check(screen.run_manager.state.current_layer == 1, "Event UI advances to Layer 2")

	screen._select_node("supply_cache")
	screen._resolve_cache_choice("echo")
	await process_frame
	_check(screen.run_manager.state.echo == 30, "Cache UI applies its selected reward")

	screen._select_node("neglect_wraith_elite")
	await process_frame
	_check(screen.state.is_elite and screen.state.enemy["name"].contains("ELITE"), "Elite route launches an Elite combat")
	screen._on_battle_finished(true)
	await process_frame
	screen._choose_breather("press_on")
	await process_frame
	screen._claim_relic("clear_lens")
	await process_frame
	_check("clear_lens" in screen.run_manager.state.relics, "Elite reward UI grants the selected Relic")
	_check(screen.run_manager.state.current_layer == 3, "Elite completion advances to the exit layer")

	screen._select_node("extract")
	await process_frame
	_check(screen.run_manager.state.completed and screen.run_manager.state.extracted, "Extract UI completes the Run safely")

	screen.queue_free()
	if failures.is_empty():
		print("UI_FLOW_SMOKE: PASS")
		quit(0)
	else:
		for failure in failures:
			push_error(failure)
		print("UI_FLOW_SMOKE: FAIL (%d)" % failures.size())
		quit(1)

func _check(condition: bool, description: String) -> void:
	if not condition:
		failures.append(description)
