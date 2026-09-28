class_name RunManager
extends RefCounted

signal changed

var state := RunState.new()
var selected_node: Dictionary = {}
var current_event: Dictionary = {}
var run_index := 0
var rng := RandomNumberGenerator.new()

func start_run() -> void:
	state.reset()
	selected_node.clear()
	current_event.clear()
	rng.seed = 4303 + run_index
	changed.emit()

func available_nodes() -> Array:
	return RunContent.layer_nodes(state.current_layer)

func select_node(node_id: String) -> Dictionary:
	var node := RunContent.node_by_id(node_id)
	if node.is_empty() or node_id not in _available_node_ids():
		push_error("Node is not available: %s" % node_id)
		return {}
	selected_node = node
	state.begin_node(node_id)
	if str(node["type"]) == "event":
		current_event = RunContent.event_for_run(run_index)
	changed.emit()
	return selected_node.duplicate(true)

func complete_combat(combat: CombatState) -> Dictionary:
	state.capture_combat(combat)
	var base_echo := int(selected_node.get("echo", 0))
	if selected_node.has("reward_multiplier"):
		base_echo = int(round(float(base_echo) * float(selected_node["reward_multiplier"])))
	var awarded := state.grant_echo(base_echo, str(selected_node["title"]))
	var settlement := state.apply_post_combat()
	state.finish_node()
	changed.emit()
	return {"echo": awarded, "settlement": settlement, "elite": bool(selected_node.get("elite", false)), "final": str(selected_node["type"]) == "final"}

func choose_breather(choice: String) -> Dictionary:
	var result := state.choose_breather(choice)
	changed.emit()
	return result

func resolve_event(choice_id: String) -> String:
	var event_id := str(current_event.get("id", ""))
	var result := "Nothing happens."
	match event_id:
		"polluted_well":
			match choice_id:
				"drink":
					var before := state.hp
					state.hp = mini(RunState.MAX_HP, state.hp + 10)
					state.corruption["Decay"] = mini(100, int(state.corruption["Decay"]) + 12)
					state.refresh_lingering_statuses()
					result = "HP %d → %d · Decay +12" % [before, state.hp]
				"examine":
					result = "Recovered %d Echo from the residue." % state.grant_echo(10, "Polluted Well")
		"broken_relay":
			if choice_id == "search":
				if rng.randf() < 0.5:
					result = "Recovered %d Echo from the relay." % state.grant_echo(25, "Broken Relay")
				else:
					state.corruption["Obscurity"] = mini(100, int(state.corruption["Obscurity"]) + 10)
					state.refresh_lingering_statuses()
					result = "The signal collapses · Obscurity +10"
		"injured_wanderer":
			if choice_id == "help":
				state.hp = maxi(1, state.hp - 5)
				result = "HP -5 · Received %d Echo" % state.grant_echo(30, "Injured Wanderer")
	state.history.append("Event %s: %s" % [event_id, result])
	state.finish_node()
	changed.emit()
	return result

func resolve_cache(choice_id: String) -> String:
	var result := ""
	match choice_id:
		"medical":
			var before := state.hp
			state.hp = mini(RunState.MAX_HP, state.hp + 8)
			result = "HP %d → %d" % [before, state.hp]
		"stabilizer":
			var family := state.dominant_corruption_family()
			if family.is_empty():
				result = "No active Corruption."
			else:
				var before := int(state.corruption[family])
				state.corruption[family] = maxi(0, before - 15)
				state.refresh_lingering_statuses()
				result = "%s %d → %d" % [family, before, int(state.corruption[family])]
		"echo":
			result = "Recovered %d Echo." % state.grant_echo(30, "Supply Cache")
	state.history.append("Cache: %s" % result)
	state.finish_node()
	changed.emit()
	return result

func claim_relic(relic_id: String) -> bool:
	var added := state.add_relic(relic_id)
	changed.emit()
	return added

func extract() -> void:
	state.extracted = true
	state.completed = true
	state.victory = true
	state.history.append("Extracted safely with %d Echo." % state.echo)
	changed.emit()

func complete_final() -> void:
	state.completed = true
	state.victory = true
	state.history.append("The Fracture's final pattern was understood.")
	changed.emit()

func fail_run(combat: CombatState) -> void:
	state.capture_combat(combat)
	state.completed = true
	state.victory = false
	state.extracted = false
	state.history.append("Connection broken inside %s." % str(selected_node.get("title", "the Fracture")))
	changed.emit()

func _available_node_ids() -> Array[String]:
	var ids: Array[String] = []
	for node in available_nodes():
		ids.append(str(node["id"]))
	return ids
