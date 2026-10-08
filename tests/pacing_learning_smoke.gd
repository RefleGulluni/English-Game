extends SceneTree

const SCHEDULE := preload("res://scripts/run/learning_schedule.gd")
const ENCOUNTERS := preload("res://scripts/run/learning_encounters.gd")
var failures: Array[String] = []
var checks := 0

func check(value: bool, message: String) -> void:
	checks += 1
	if not value: failures.append(message)

func fresh():
	var s := SCHEDULE.new()
	s.save_path = ""
	s.setup()
	return s

func begin(s, id: String = "MOURN") -> void:
	s.begin({"id": "mourning_stone", "title": "Mourning Stone", "primary": id, "words": [id], "tags": ["SAFE", "WORLD_EVENT", "MAJOR_LEARNING_OPPORTUNITY"]}, 1)

func gap(s) -> void:
	for i in range(2):
		s.begin({"id": "rest", "title": "Shelter", "primary": "", "words": [], "tags": ["RECOVERY"]}, 1)
		s.complete()

func _initialize() -> void:
	var s = fresh()
	begin(s)
	check(s.words.MOURN.current_state == "ENCOUNTERED", "Ambient only encounters; no recognition")
	check(s.evidence("MOURN", "recognition", true), "Correct recognition is evidence")
	s.words.MOURN.context("same event")
	s.words.MOURN.produce("same event", true)
	check(s.words.MOURN.current_state == "RECOGNIZED", "QA04: one encounter cannot chain stages")
	s.complete()
	check(s.cooldown("MOURN") == 2, "QA01: two encounters of cooldown start after complete")
	begin(s, "LINGER")
	s.complete()
	check(s.cooldown("MOURN") == 1, "QA01: first complete encounter still blocked")
	begin(s, "CONCEAL")
	s.complete()
	check(s.cooldown("MOURN") == 0, "QA01: third encounter eligible")
	var rng := RandomNumberGenerator.new()
	rng.seed = 123
	s.active_pool.assign(["MOURN", "LINGER", "CONCEAL", "REASSEMBLE", "ERODE", "TOXIC"])
	var eligible_node := {"words": ["MOURN", "REASSEMBLE"], "biome": "cemetery"}
	var draws := {}
	for i in range(200): draws[s.choose_target(eligible_node, rng, 0)] = true
	check(draws.size() > 1, "QA02: cooldown does not force immediate revisit")
	check(s.choose_target(eligible_node, rng, 2).is_empty(), "QA07: third major is blocked")
	var offered := 0
	for i in range(1000):
		if not s.choose_target(eligible_node, rng, 1).is_empty(): offered += 1
	check(offered > 150 and offered < 350, "QA07: second opportunity ACTUALLY reduced, not just a canceled weight multiplier")
	begin(s)
	s.evidence("MOURN", "context", true)
	s.complete()
	check(s.words.MOURN.current_state == "UNDERSTOOD", "Context advances one stage")
	gap(s)
	begin(s)
	s.evidence("MOURN", "production", true)
	s.complete()
	check(s.words.MOURN.current_state == "USABLE", "Production earns mastery on separate encounter")
	var before: Dictionary = s.snapshot().duplicate(true)
	var restored = fresh()
	check(restored.restore(JSON.parse_string(JSON.stringify(before))), "QA03: serialized schedule restores")
	check(restored.clock == s.clock and restored.cooldown("MOURN") == 2 and restored.words.MOURN.current_state == "USABLE", "QA03: clock/cooldown/knowledge survive reload")
	var malformed := before.duplicate(true)
	malformed.records.MOURN.familiarity = "bad data"
	check(not restored.restore(malformed) and restored.words.MOURN.current_state == "USABLE", "invalid save rejected without partially mutating earned knowledge")
	var manager := RunManager.new()
	manager.persistence_path = ""
	manager.start_cemetery_run(1)
	manager.learning.restore(before)
	manager.start_cemetery_run(2)
	check(manager.state.target_knowledge.MOURN.current_state == "USABLE" and manager.learning.cooldown("MOURN") == 2, "QA03: restart preserves schedule, not only disk load")
	for i in range(30):
		begin(s, "LINGER")
		s.complete()
	check(s.words.MOURN.current_state == "USABLE" and s.records.MOURN.familiarity < before.records.MOURN.familiarity, "Familiarity decay never downgrades knowledge")
	s = fresh()
	for pair in [["UNKNOWN", "recognition"], ["RECOGNIZED", "context"], ["UNDERSTOOD", "production"]]:
		s.words.MOURN.dev_set_state(pair[0])
		begin(s)
		var exercise := ENCOUNTERS.exercise("MOURN", {"id": "mourning_stone", "words": ["MOURN"]}, s)
		check(not exercise.correctiveLine.is_empty() and exercise.wordSenseId == "mourn:cemetery:v1", "QA06: corrective context and sense metadata authored")
		s.evidence("MOURN", pair[1], false)
		check(s.words.MOURN.current_state in [pair[0], "ENCOUNTERED"], "Wrong answer preserves earned knowledge")
		check(s.weak_layer("MOURN") == pair[1], "QA05: error changes weak layer")
		check(not s.evidence("MOURN", pair[1], true), "QA06: no forced immediate retry in same encounter")
		s.complete()
		# Reset weakness only to independently verify each diagnostic category.
		s.records.MOURN.weakness = {"recognition": 0, "context": 0, "production": 0}
	check(s.records.MOURN.errors == {"recognition": 1, "context": 1, "production": 1}, "QA05: three errors independently accumulated")
	check(s.records.MOURN.difficulty > 0 and s.new_ratio < 0.6, "QA18: struggling shifts toward review, not punishment")
	for mode in ["Adaptive", "More Discovery", "Balanced", "More Review"]:
		check(s.set_pace(mode) and s.new_ratio >= 0.25 and s.new_ratio <= 0.85, "QA19: pace controls dynamic bounded preference")
	s = fresh()
	var stable_id: String = s.active_pool[0]
	s.words[stable_id].dev_set_state("USABLE") if stable_id in preload("res://scripts/run/cemetery_words.gd").DATA else null
	if stable_id not in preload("res://scripts/run/cemetery_words.gd").DATA: s.words[stable_id].current_state = "USABLE"
	s.records[stable_id].stability = 1.0
	s.records[stable_id].familiarity = 90.0
	s.records[stable_id].success_streak = 5
	s.refresh_pool()
	check(stable_id not in s.active_pool and s.active_pool.size() in [5, 6, 7, 8], "QA17: stable word exits active focus, pool stays bounded")
	s.records[stable_id].stability = 0.1
	s.records[stable_id].difficulty = 1.0
	s.records[stable_id].last_major = 0
	s.clock = 20
	s.refresh_pool()
	check(stable_id in s.active_pool, "QA17: difficult old word reactivates")
	check(not s.eligible("MICROWAVE", {"words": ["MICROWAVE"]}) and not s.eligible("MOURN", {"words": ["WATER"]}), "QA20: unrelated/incompatible words never enter candidate pool")
	s.active_pool.assign(["MOURN", "LINGER", "CONCEAL", "REASSEMBLE", "ERODE", "TOXIC"])
	s.player_level = 0
	check(not s.eligible("REASSEMBLE", {"words": ["REASSEMBLE"]}), "QA20: learner level checked before new-word weighting")
	s.player_level = 1
	begin(s)
	s.words.LINGER.recognize("ambient secondary")
	check(s.words.LINGER.current_state != "RECOGNIZED", "QA15: secondary word cannot advance major knowledge")
	var familiarity: float = s.records.LINGER.familiarity
	for i in range(20): s.words.LINGER.encounter()
	check(s.records.LINGER.familiarity == familiarity, "Ambient gains deduplicate within encounter")
	# Disk test isolated by caller-provided QA directory; never touches player's save.
	var qa_dir := OS.get_environment("PACING_QA_DIR")
	if not qa_dir.is_empty():
		s.save_path = qa_dir.path_join("schedule.json")
		check(s.save(), "atomic save succeeds")
		s.clock += 1
		check(s.save() and FileAccess.file_exists(s.save_path + ".previous"), "previous disk save retained")
		var disk = fresh()
		disk.save_path = s.save_path
		disk.load_saved()
		check(disk.clock == s.clock and disk.words.MOURN.current_state == s.words.MOURN.current_state, "cross process disk schema roundtrips")
		var corrupted := FileAccess.open(qa_dir.path_join("corrupted.json"), FileAccess.WRITE)
		corrupted.store_string("not valid JSON")
		corrupted.close()
		var bad = fresh()
		bad.save_path = qa_dir.path_join("corrupted.json")
		bad.load_saved()
		check(bad.read_only and not bad.load_notice.is_empty(), "invalid disk save enters read-only protection")
		bad.save()
		check(FileAccess.get_file_as_string(bad.save_path) == "not valid JSON", "invalid original never overwritten with empty progress")
	for message in failures: push_error(message)
	print("PACING_LEARNING_SMOKE: %s · %d checks" % ["PASS" if failures.is_empty() else "FAIL", checks])
	quit(0 if failures.is_empty() else 1)
