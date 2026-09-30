extends SceneTree

var failures: Array[String] = []

func _initialize() -> void:
	var state := CombatState.new()
	state.start_battle(0)
	_check(state.intent["word"] == "ERODE", "Root Husk opens with ERODE")
	_check(state.intent_clarity == 0, "unknown hostile Word starts Obscured")

	state.use_skill("OBSERVE")
	_check(state.intent_clarity == 1 and state.focus == 2, "OBSERVE reveals one level for 1 Focus")
	state.use_skill("BIND")
	state.end_player_turn()
	_check(state.intent["word"] == "ERODE" and state.turn == 2, "BIND delays rather than deletes the intent")

	state.end_player_turn()
	_check(state.corruption["Decay"] == 12, "ERODE applies Decay Corruption")
	_check(state.armor == 8, "ERODE weakens Armor")
	_check(state.intent["word"] == "LASH", "enemy sequence advances after resolution")

	var hp_before := state.hp
	var armor_before := state.armor
	state.resolve_enemy_action(true)
	_check(state.hp == hp_before and state.armor == armor_before - 2, "DEFLECT reduces LASH to 25 percent")
	_check(state.focus == 4, "reserved Focus carries at most 1 into a 3 Focus turn")

	state.corruption["Inattention"] = 38
	state.use_skill("STABILIZE")
	_check(state.corruption["Inattention"] == 22, "STABILIZE reduces dominant Corruption by 16")

	state.hp = 30
	state.use_skill("RESTORE", "hp")
	_check(state.hp == 38, "RESTORE recovers 8 HP when not Withered")

	_test_shatter_branches()
	_test_inattention_feedback_and_clear_lens()

	if failures.is_empty():
		print("COMBAT_STATE_SMOKE: PASS")
		quit(0)
	else:
		for failure in failures:
			push_error(failure)
		print("COMBAT_STATE_SMOKE: FAIL (%d)" % failures.size())
		quit(1)

func _test_shatter_branches() -> void:
	var state := CombatState.new()
	state.start_battle(0)
	state.focus = 20
	var starting_hp := int(state.enemy["hp"])
	state.use_skill("SHATTER")
	_check(int(state.enemy["armor"]) == 10 and int(state.enemy["hp"]) == starting_hp, "SHATTER only damages Structure while Structure remains")
	state.use_skill("SHATTER")
	_check(int(state.enemy["armor"]) == 2 and int(state.enemy["hp"]) == starting_hp, "repeated SHATTER does not leak HP damage through Structure")
	state.use_skill("SHATTER")
	_check(int(state.enemy["armor"]) == 0 and int(state.enemy["hp"]) == starting_hp - 6, "SHATTER triggers Structure Collapse exactly when Structure reaches zero")
	state.use_skill("SHATTER")
	_check(int(state.enemy["hp"]) == starting_hp - 16, "SHATTER deals exposed damage after Structure has collapsed")
	var collapse_logs := 0
	for line in state.log_lines:
		if "STRUCTURE COLLAPSE" in line:
			collapse_logs += 1
	_check(collapse_logs == 1, "Structure Collapse triggers only once")

func _test_inattention_feedback_and_clear_lens() -> void:
	var state := CombatState.new()
	state.start_battle(3, {
		"corruption": {"Decay": 0, "Obscurity": 0, "Inattention": 95},
		"statuses": {"CARELESS": 99},
		"relics": ["clear_lens"],
	})
	_check(state.skill_cost("OBSERVE") == 0, "Clear Lens makes the first high-Inattention OBSERVE free")
	state.use_skill("OBSERVE")
	_check(state.skill_cost("OBSERVE") == 2, "high Inattention still applies after Clear Lens is consumed")
	_check(state.reaction_cost() == 2, "high Inattention increases DEFLECT cost")
	var feedback := state.active_status_text()
	_check("NEGLIGENT" in feedback and "OBSERVE +1 FOCUS" in feedback and "DEFLECT +1 FOCUS" in feedback, "Status HUD explains active Inattention consequences")

func _check(condition: bool, description: String) -> void:
	if not condition:
		failures.append(description)
