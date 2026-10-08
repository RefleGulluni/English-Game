extends SceneTree

const FIXTURE := preload("res://tests/mechanics_fixture.gd")
var failures: Array[String] = []
var checks := 0

func check(value: bool, message: String) -> void:
	checks += 1
	if not value: failures.append(message)

func model(index: int, primary: String) -> Dictionary:
	var m := RunManager.new()
	m.persistence_path = ""
	m.start_cemetery_run(123)
	if primary in preload("res://scripts/run/cemetery_words.gd").DATA:
		m.learning.words[primary].dev_set_state("RECOGNIZED")
	else:
		m.learning.words[primary].current_state = "RECOGNIZED"
		m.learning.words[primary].recognition_evidence = 1
	m.learning.begin({"id": "unit_combat", "title": "Unit Combat", "words": [primary], "tags": ["RISK", "COMBAT"], "primary": primary}, 1)
	var c := CombatState.new()
	c.start_battle(index, m.state.combat_snapshot())
	c.finish_mulligan()
	return {"manager": m, "combat": c}

func _initialize() -> void:
	var pair := model(6, "CONCEAL")
	pair.combat._finish_battle(true)
	check(pair.manager.learning.words.CONCEAL.current_state == "RECOGNIZED", "Victory alone does not turn appearance into knowledge")
	pair = model(6, "CONCEAL")
	FIXTURE.play(pair.combat, "OBSERVE")
	check(pair.manager.learning.words.CONCEAL.current_state == "UNDERSTOOD", "actual hidden reveal supplies context")
	check(pair.manager.learning.words.HOLLOW.current_state != "RECOGNIZED", "other native word stays ambient/pending")
	pair.combat._record_target_context("LINGER", "second_word")
	check(pair.manager.learning.pending.any(func(p): return p.word == "LINGER"), "secondary context retained diagnostically, not awarded")
	pair = model(7, "REASSEMBLE")
	pair.combat.enemy.hp = 0
	pair.combat._enemy_defeated()
	check(pair.combat.bone_remains and pair.manager.learning.words.REASSEMBLE.current_state == "UNDERSTOOD", "actual Remains scene supplies reassembly context")
	pair = model(5, "HOLLOW")
	FIXTURE.play(pair.combat, "OBSERVE")
	check(pair.manager.learning.words.HOLLOW.current_state == "UNDERSTOOD", "observing incorporeal no-structure enemy supplies HOLLOW context")
	pair = model(7, "ERODE")
	pair.combat._record_target_context("ERODE", "actual_decay")
	check(pair.manager.learning.words.ERODE.current_state == "UNDERSTOOD", "legacy modifier supports new context interface without invalid method calls")
	pair.combat.knowledge.record_production(true)
	check(pair.manager.learning.words.ERODE.current_state == "UNDERSTOOD", "combat context cannot chain into production")
	for message in failures: push_error(message)
	print("PACING_COMBAT_SMOKE: %s · %d checks" % ["PASS" if failures.is_empty() else "FAIL", checks])
	quit(0 if failures.is_empty() else 1)
