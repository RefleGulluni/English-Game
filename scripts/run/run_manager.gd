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
	state.deck_seed = 5050 + run_index * 101
	changed.emit()

func available_nodes() -> Array:
	var nodes := RunContent.layer_nodes(state.current_layer)
	if state.current_layer == 2:
		# Keep the ecology tests reachable after ERODE's full learning loop.
		for node_id in ["iron_shell", "ghost"]:
			nodes.append(RunContent.node_by_id(node_id))
	if state.anomaly_resolved:
		for node in nodes.duplicate():
			if node["id"] == "semantic_anomaly":
				nodes.erase(node)
	for node in nodes.duplicate():
		if str(node["id"]) in state.completed_detours:
			nodes.erase(node)
	return nodes

func select_node(node_id: String) -> Dictionary:
	var node := RunContent.node_by_id(node_id)
	if node.is_empty() or node_id not in _available_node_ids():
		push_error("Node is not available: %s" % node_id)
		return {}
	selected_node = node
	if str(node["type"]) == "anomaly":
		# This optional, rewardless interlude must not consume a Press On bonus.
		state.current_node_id = node_id
		state.history.append("Entered %s." % node_id)
	else:
		state.begin_node(node_id)
	if str(node["type"]) == "event":
		current_event = RunContent.event_for_run(run_index)
	changed.emit()
	return selected_node.duplicate(true)

func resolve_anomaly(choice: String) -> String:
	if state.anomaly_resolved or str(selected_node.get("id", "")) != "semantic_anomaly":
		return "This anomaly has already passed."
	if choice == "anchor" and state.knowledge.current_state != "USABLE":
		return "REQUIRES USABLE · The hidden option is unavailable."
	if not choice in ["erode", "bind", "restore", "anchor", "leave"]:
		return "Choose a meaning before receiving a reward."
	state.anomaly_resolved = true
	var result := "The phrase fades."
	if choice == "erode":
		state.temporary_cards.append("STABILIZE")
		result = "Correct: ERODE means gradual wearing away. A temporary STABILIZE joins the next combat deck (EXHAUST after use)."
	elif choice == "anchor":
		var family := state.dominant_corruption_family()
		if not family.is_empty():
			state.corruption[family] = maxi(0, int(state.corruption[family]) - 8)
			state.refresh_lingering_statuses()
		result = "You anchor the missing concept. Dominant Corruption recedes by up to 8."
	elif choice in ["bind", "restore"]:
		state.corruption["Obscurity"] = mini(100, int(state.corruption["Obscurity"]) + 8)
		state.refresh_lingering_statuses()
		result = "The concept does not fit this context. Obscurity +8."
	state.history.append("Semantic Anomaly: " + result)
	changed.emit()
	return result

func complete_combat(combat: CombatState) -> Dictionary:
	state.capture_combat(combat)
	var base_echo := int(selected_node.get("echo", 0))
	if selected_node.has("reward_multiplier"):
		base_echo = int(round(float(base_echo) * float(selected_node["reward_multiplier"])))
	var awarded := state.grant_echo(base_echo, str(selected_node["title"]))
	var settlement := state.apply_post_combat()
	if bool(selected_node.get("detour", false)):
		state.completed_detours.append(str(selected_node["id"]))
		state.active_reward_multiplier = 1.0
	else:
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
