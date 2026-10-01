extends SceneTree

var failures: Array[String] = []

func _initialize() -> void:
	_test_post_combat_rules()
	_test_breather_and_reward_multiplier()
	_test_combat_snapshot_and_relics()
	_test_fixed_run_route()

	if failures.is_empty():
		print("RUN_STATE_SMOKE: PASS")
		quit(0)
	else:
		for failure in failures:
			push_error(failure)
		print("RUN_STATE_SMOKE: FAIL (%d)" % failures.size())
		quit(1)

func _test_post_combat_rules() -> void:
	var run := RunState.new()
	run.reset()
	run.hp = 31
	run.armor = 2
	run.corruption = {"Decay": 34, "Obscurity": 28, "Inattention": 82}
	run.statuses = {"WITHERED": 2, "NEGLIGENT": 99}
	run.inattention_tier = 4
	var report := run.apply_post_combat()
	_check(run.hp == 31, "HP persists after combat")
	_check(run.armor == 6 and report["armor_after"] == 6, "Armor rebuilds by ceil(30 percent Max Armor)")
	_check(run.corruption == {"Decay": 29, "Obscurity": 23, "Inattention": 77}, "each Corruption family dissipates by 5")
	_check(not run.statuses.has("WITHERED"), "Transient Status clears after combat")
	_check(run.statuses.has("NEGLIGENT") and run.inattention_tier == 4, "NEGLIGENT persists at 77 until Inattention falls below 70")

func _test_breather_and_reward_multiplier() -> void:
	var run := RunState.new()
	run.reset()
	run.hp = 35
	var recovered := run.choose_breather("recover")
	_check(run.hp == 41 and recovered["description"] == "HP 35 → 41", "Recover restores 6 HP")
	run.corruption["Decay"] = 30
	run.choose_breather("stabilize")
	_check(run.corruption["Decay"] == 18, "Stabilize reduces dominant Corruption by 12")
	run.choose_breather("press_on")
	_check(run.preview_echo(30, true) == 38, "Press On preview shows the rounded next-node reward")
	run.begin_node("reward_test")
	_check(run.preview_echo(30) == 38, "active node preview matches the Press On settlement")
	_check(run.grant_echo(20, "test") == 25 and run.echo == 25, "Press On multiplies the next node reward by 1.25")

func _test_combat_snapshot_and_relics() -> void:
	var combat := CombatState.new()
	var snapshot := {
		"hp": 37,
		"armor": 6,
		"corruption": {"Decay": 10, "Obscurity": 5, "Inattention": 0},
		"statuses": {},
		"relics": ["clear_lens", "iron_script", "quiet_mind"],
	}
	combat.start_battle(2, snapshot, true)
	_check(combat.hp == 37 and combat.armor == 6, "Combat imports persistent HP and Armor")
	_check(combat.corruption["Decay"] == 10 and combat.corruption["Inattention"] == 5, "Elite pressure and Corruption persistence coexist")
	_check(combat.enemy["max_hp"] == 48 and combat.enemy["max_structure"] == 10, "Elite has 25 percent HP and Structure scaling")
	var focus_before := combat.focus
	preload("res://tests/mechanics_fixture.gd").play(combat, "OBSERVE")
	_check(combat.focus == focus_before, "Clear Lens makes the first OBSERVE free")
	combat.enemy["structure"] = 8
	var hp_before := int(combat.enemy["hp"])
	preload("res://tests/mechanics_fixture.gd").play(combat, "SHATTER")
	_check(int(combat.enemy["hp"]) == hp_before - 10, "Iron Script adds 4 Structure Collapse damage")

func _test_fixed_run_route() -> void:
	var manager := RunManager.new()
	manager.start_run()
	_check(manager.available_nodes().size() == 2, "Layer 1 exposes two route choices")
	manager.select_node("fracture_event")
	manager.resolve_event("leave")
	_check(manager.state.current_layer == 1, "Event completion advances the route")
	manager.select_node("supply_cache")
	manager.resolve_cache("echo")
	_check(manager.state.current_layer == 2 and manager.state.echo == 30, "Cache resolves and advances to the Elite layer")
	manager.select_node("neglect_wraith")
	var combat := CombatState.new()
	combat.start_battle(2, manager.state.combat_snapshot())
	combat.hp = 32
	combat.armor = 1
	var result := manager.complete_combat(combat)
	_check(result["echo"] == 25 and manager.state.current_layer == 3, "Combat reward and post-combat route progression are centralized")
	_check(manager.available_nodes()[0]["id"] == "extract", "Layer 4 offers extraction")

func _check(condition: bool, description: String) -> void:
	if not condition:
		failures.append(description)
