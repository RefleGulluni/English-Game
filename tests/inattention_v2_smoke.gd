extends SceneTree

const RULES := preload("res://scripts/combat/inattention_rules.gd")
var failures: Array[String] = []

func _initialize() -> void:
	for tier in range(1, 5):
		_check(RULES.update_tier(0, RULES.ENTER[tier] - 1) == tier - 1, "entry boundary before tier %d" % tier)
		_check(RULES.update_tier(0, RULES.ENTER[tier]) == tier, "entry boundary at tier %d" % tier)
		_check(RULES.update_tier(tier, RULES.CLEAR[tier]) == tier, "strict clear boundary at tier %d" % tier)
		_check(RULES.update_tier(tier, RULES.CLEAR[tier] - 1) == tier - 1, "clear boundary below tier %d" % tier)
	_check(RULES.update_tier(4, 0) == 0, "large reduction clears multiple tiers")
	_check(RULES.update_tier(0, 100) == 4, "100 remains NEGLIGENT")
	var combat := CombatState.new()
	combat.start_battle(2, {}, true)
	combat.resolve_enemy_action(false)
	_check(combat.corruption["Inattention"] == 24 and combat.inattention_tier == 1, "first elite OVERLOOK enters DISTRACTED at 24")
	_check(combat.skill_cost("OBSERVE") == 1 and combat.reaction_cost() == 1, "DISTRACTED does not increase costs")
	for row in [[44, 2, 28, 1], [64, 3, 48, 2], [84, 4, 68, 3]]:
		combat.start_battle(2, {"corruption": {"Decay": 0, "Obscurity": 0, "Inattention": row[0]}})
		_check(combat.inattention_tier == row[1], "correct initial severity")
		combat.use_skill("STABILIZE")
		_check(combat.corruption["Inattention"] == row[2] and combat.inattention_tier == row[3], "STABILIZE crosses release threshold")
	combat.start_battle(0, {"corruption": {"Decay": 0, "Obscurity": 0, "Inattention": 80}})
	combat.intent = combat.enemy["actions"][0].duplicate(true)
	combat.intent_clarity = 2
	_check(not str(combat.intent["clear"]) in combat.intent_description(), "NEGLIGENT hides exact warning even after OBSERVE")
	_check(combat.intent_title() == combat.intent["word"], "NEGLIGENT retains move name")
	_check(combat.active_status_text().split("\n").size() == 5, "NEGLIGENT status and each modifier occupy separate rows")
	var run := RunState.new()
	run.capture_combat(combat)
	run.apply_post_combat()
	combat.start_battle(1, run.combat_snapshot())
	_check(combat.inattention_tier == 4 and combat.corruption["Inattention"] == 75, "hysteresis survives settlement and next combat")
	run.choose_breather("stabilize")
	_check(run.inattention_tier == 3, "breather releases NEGLIGENT below 70")
	for failure in failures:
		push_error(failure)
	print("INATTENTION_V2_SMOKE: %s" % ("PASS" if failures.is_empty() else "FAIL"))
	quit(0 if failures.is_empty() else 1)

func _check(condition: bool, message: String) -> void:
	if not condition:
		failures.append(message)
