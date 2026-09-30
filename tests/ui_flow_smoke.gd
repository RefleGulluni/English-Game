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

	screen.run_manager.state.next_reward_multiplier = RunState.PRESS_ON_MULTIPLIER
	screen._select_node("supply_cache")
	await process_frame
	var cache_card: Control = screen.modal.get_child(1)
	var echo_button: Button = cache_card.find_child("Action2", true, false)
	_check("+30 → +38 Echo" in echo_button.text, "Cache UI previews the rounded Press On reward")
	screen._resolve_cache_choice("echo")
	await process_frame
	_check(screen.run_manager.state.echo == 38, "Cache UI applies its selected Press On reward")

	screen._show_map()
	await process_frame
	var map_card: Control = screen.modal.get_child(1)
	for frame in range(8):
		await process_frame
	var map_body: Label = map_card.find_child("Body", true, false)
	var first_route_button: Button = map_card.find_child("Action0", true, false)
	_check(map_body.get_global_rect().end.y <= first_route_button.global_position.y, "route details do not overlap Layer 3 buttons")
	_check(map_body.size.x < map_card.size.x and map_body.get_line_count() > 1, "route text wraps within the modal width")
	_check(absf(map_body.get_global_rect().get_center().x - map_card.get_global_rect().get_center().x) < 12, "route text is centered within the modal")

	screen._select_node("neglect_wraith_elite")
	await process_frame
	_check(screen.state.is_elite and screen.state.enemy["name"].contains("ELITE"), "Elite route launches an Elite combat")
	screen.state.armor = 0
	screen.state.corruption["Inattention"] = 90
	screen.state.statuses["CARELESS"] = 99
	screen._on_battle_finished(true)
	await process_frame
	_check(screen.state.armor == 4 and screen.state.corruption["Inattention"] == 85, "post-combat HUD synchronizes settlement values while the Breather modal is open")
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
