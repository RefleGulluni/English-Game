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

	if failures.is_empty():
		print("COMBAT_STATE_SMOKE: PASS")
		quit(0)
	else:
		for failure in failures:
			push_error(failure)
		print("COMBAT_STATE_SMOKE: FAIL (%d)" % failures.size())
		quit(1)

func _check(condition: bool, description: String) -> void:
	if not condition:
		failures.append(description)
