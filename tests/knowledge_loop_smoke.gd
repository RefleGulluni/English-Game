extends SceneTree

const WORD := preload("res://scripts/run/word_knowledge.gd")
var failures: Array[String] = []

func _initialize() -> void:
	var knowledge := WORD.new()
	knowledge.encounter()
	_check(knowledge.current_state == "ENCOUNTERED", "first exposure records ENCOUNTERED")
	knowledge.record_combat_context(true)
	_check(knowledge.current_state == "ENCOUNTERED", "combat repetition alone cannot produce understanding")
	knowledge.recognize("inscription")
	_check(knowledge.current_state == "RECOGNIZED" and knowledge.recognition_evidence == 1, "context recognition earns evidence")
	knowledge.recognize("inscription")
	_check(knowledge.recognition_evidence == 1, "repeated evidence cannot be farmed")
	var run := RunState.new()
	run.knowledge = knowledge
	var combat := CombatState.new()
	combat.start_battle(0, run.combat_snapshot())
	_check(combat.intent_clarity == 1, "Recognized ERODE gains a clarity level")
	_check("Recognized Concept" in combat.intent_description() and not "Armor -4" in combat.intent_description(), "recognition offers meaning without exact answers")
	combat.use_skill("BIND")
	_check(knowledge.current_state == "RECOGNIZED", "using an arbitrary skill does not teach the word")
	combat.focus = 3
	combat.use_skill("OBSERVE")
	_check(knowledge.current_state == "UNDERSTOOD" and knowledge.has_insight(), "reading exact combat consequences links meaning and mechanism")
	_check("Known Mechanism" in combat.intent_description(), "UNDERSTOOD grants mechanism prediction")
	combat.armor = 12
	combat.resolve_enemy_action(false)
	_check(combat.armor == 8 and combat.corruption["Decay"] == 12, "knowledge does not reduce ERODE harm")
	_check(knowledge.context_evidence == 1, "same combat context counts only once")
	run.capture_combat(combat)
	run.apply_post_combat()
	run.choose_breather("recover")
	_check(run.knowledge == knowledge and knowledge.current_state == "UNDERSTOOD", "knowledge persists through combat and Breather")
	knowledge.record_transfer(false)
	knowledge.record_production(false)
	_check(knowledge.current_state == "UNDERSTOOD", "wrong answers never reduce state")
	knowledge.record_production(true)
	_check(knowledge.current_state == "UNDERSTOOD", "production requires transfer evidence")
	knowledge.record_transfer(true)
	_check(knowledge.context_evidence == 2, "new meaning-transfer context earns separate evidence")
	knowledge.record_production(true)
	_check(knowledge.current_state == "USABLE" and knowledge.production_evidence == 1, "correct production completes Knowledge Loop")
	combat.start_battle(3, run.combat_snapshot())
	_check("Known Mechanism" in combat.intent_description(), "ERODE Insight transfers to Decay-Structure intent")
	combat.exposure.clear()
	combat.start_battle(0, {"knowledge": knowledge, "corruption": {"Decay": 0, "Obscurity": 0, "Inattention": 20}})
	_check(combat.intent_clarity == 0, "Inattention still erodes knowledge-based clarity")
	combat.start_battle(0, {"knowledge": knowledge, "corruption": {"Decay": 0, "Obscurity": 30, "Inattention": 0}})
	_check(combat.intent_clarity == 0, "Obscurity still erodes knowledge-based clarity")
	combat.start_battle(0, {"knowledge": knowledge, "corruption": {"Decay": 0, "Obscurity": 0, "Inattention": 80}})
	_check(not "Likely effect" in combat.intent_description(), "NEGLIGENT warning degradation is not bypassed by Insight")
	combat.start_battle(0)
	combat.corruption = {"Decay": 30, "Obscurity": 10, "Inattention": 0}
	combat.use_skill("STABILIZE")
	combat.use_skill("STABILIZE")
	_check(combat.focus == 1 and combat.corruption == {"Decay": 14, "Obscurity": 10, "Inattention": 0}, "two STABILIZE uses cost 2 Focus and reduce only dominant Corruption by 16")
	run.reset()
	_check(run.knowledge.current_state == "UNKNOWN", "new Run resets prototype knowledge")
	for failure in failures:
		push_error(failure)
	print("KNOWLEDGE_LOOP_SMOKE: %s" % ("PASS" if failures.is_empty() else "FAIL"))
	quit(0 if failures.is_empty() else 1)

func _check(condition: bool, message: String) -> void:
	if not condition:
		failures.append(message)
