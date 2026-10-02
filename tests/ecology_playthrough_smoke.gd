extends SceneTree

const AUTO := preload("res://tests/auto_combat.gd")
var failures: Array[String] = []

func _initialize() -> void:
	var manager := RunManager.new()
	manager.start_run()
	manager.state.knowledge.encounter()
	manager.state.knowledge.recognize("inscription")
	manager.state.toxic_knowledge.encounter()
	manager.state.toxic_knowledge.recognize("cracked_vial")
	for node_id in ["root_husk", "veil_moth", "iron_shell", "ghost", "neglect_wraith", "final_encounter"]:
		var node := manager.select_node(node_id)
		var snapshot := manager.state.combat_snapshot()
		snapshot["objective"] = node.get("objective", "kill")
		var combat := CombatState.new()
		combat.start_battle(int(node.battle), snapshot)
		manager.state.temporary_cards.clear()
		var victory := AUTO.fight(combat, true)
		print("ECOLOGY PLAYTHROUGH · %s · HP %d · Rounds %d" % [node_id, combat.hp, combat.completed_rounds])
		if not victory:
			failures.append("Legal full ecology route failed: " + node_id)
			break
		manager.complete_combat(combat)
		if node_id == "final_encounter":
			manager.complete_final()
			break
		manager.choose_breather("recover")
		if node_id == "root_husk":
			manager.claim_relic("clear_lens")
			manager.select_node("semantic_anomaly")
			manager.resolve_anomaly("erode")
		elif node_id == "veil_moth":
			manager.state.knowledge.record_transfer(true)
			manager.state.knowledge.record_production(true)
	if not manager.state.completed or not manager.state.victory or manager.state.toxic_knowledge.current_state != "USABLE":
		failures.append("Full route must reach Run Complete and real TOXIC unlock")
	for failure in failures:
		push_error(failure)
	print("ECOLOGY_PLAYTHROUGH_SMOKE: %s" % ("PASS" if failures.is_empty() else "FAIL"))
	quit(0 if failures.is_empty() else 1)
