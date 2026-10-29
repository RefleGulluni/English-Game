extends RefCounted

const CONFIG := preload("res://scripts/run/pacing_config.gd")
const WORDS := preload("res://scripts/run/cemetery_words.gd")
const KNOWLEDGE_FIELDS := ["current_state", "known_meaning", "recognition_evidence", "context_evidence", "production_evidence", "gameplay_unlocks", "unlocked_cards", "discovered_combos", "enemy_records", "evidence_sources", "transfer_correct"]
const LIBRARY := preload("res://scripts/run/word_library.gd")
# 0.8 families, kept as the fallback; a word's family is now its first tag in the library (D-070).
const FAMILIES := {"MOURN": "GRIEF", "LINGER": "CONTINUITY", "CONCEAL": "HIDDEN", "REASSEMBLE": "PARTS", "REMAINS": "PARTS", "HOLLOW": "SPACE", "BURY": "BURIAL", "HAUNT": "CONTINUITY", "WITHER": "DECAY", "SCATTER": "PARTS", "GRAVE": "BURIAL", "ECHO": "SOUND", "ERODE": "DECAY", "TOXIC": "HARM"}
var words: Dictionary = {}
var records: Dictionary = {}
var active_pool: Array[String] = []
var pool_override: Array[String] = [] # DEV only, never persisted.
var pending: Array = []
var timeline: Array = []
var clock := 0
var pace := "Balanced"
var new_ratio := 0.6
var player_level := 1 # Prototype learner level; no new RPG leveling subsystem.
var encounter: Dictionary = {}
var selection_weights: Array = []
var save_path := "user://learning_schedule_0_8.json"
var save_error := ""
var load_notice := ""
var read_only := false

func setup() -> void:
	for id in WORDS.CORE + WORDS.ELASTIC + ["ERODE", "TOXIC"]:
		var word = WORDS.word(id) if id in WORDS.DATA else preload("res://scripts/run/word_knowledge.gd").new(id.to_lower())
		words[id] = word
		word.schedule = self
		records[id] = {"sense_id": id.to_lower() + ":cemetery:v1", "familiarity": 0.0, "difficulty": 0.0, "stability": 0.0, "last_major": -1, "last_appearance": -1, "errors": {"recognition": 0, "context": 0, "production": 0}, "weakness": {"recognition": 0, "context": 0, "production": 0}, "successes": 0, "failures": 0, "success_streak": 0, "failure_streak": 0, "stage_encounters": 0, "stages_needed": {}, "corrective_history": [], "hints": 0, "active": false}
	refresh_pool()

func age(id: String) -> int:
	return 100 if int(records[id].last_major) < 0 else maxi(0, clock - int(records[id].last_major))

func cooldown(id: String) -> int:
	return maxi(0, CONFIG.MIN_MAJOR_GAP - age(id))

func priority(id: String) -> float:
	var r: Dictionary = records[id]
	var elapsed := 0.0 if int(r.last_major) < 0 else minf(float(CONFIG.QA.revisit_max_bonus), float(age(id)) / float(CONFIG.QA.revisit_high_after))
	return 1.0 + elapsed + float(r.difficulty) * float(CONFIG.QA.personal_difficulty_weight) + (1.0 - float(r.stability)) * float(CONFIG.QA.stability_priority) + (1.0 - float(r.familiarity) / 100.0) * float(CONFIG.QA.familiarity_priority) + (float(CONFIG.QA.pending_priority) if pending.any(func(p): return p.word == id) else 0.0)

func weak_layer(id: String) -> String:
	var r: Dictionary = records[id]
	var weakest := ""
	var highest := 0
	for key in ["recognition", "context", "production"]:
		if int(r.weakness[key]) > highest:
			weakest = key
			highest = int(r.weakness[key])
	if not weakest.is_empty() and float(r.stability) < float(CONFIG.QA.stable_confidence):
		return weakest
	var stage: String = words[id].current_state
	if stage in ["UNDERSTOOD", "USABLE"] and float(r.familiarity) < float(CONFIG.QA.familiarity_recognition_below) and float(r.stability) >= float(CONFIG.QA.stable_confidence): return "recognition"
	return "recognition" if stage in ["UNKNOWN", "ENCOUNTERED"] else ("context" if stage == "RECOGNIZED" else "production")

func stable(id: String) -> bool:
	var r: Dictionary = records[id]
	return words[id].current_state == "USABLE" and float(r.stability) >= float(CONFIG.QA.stable_confidence) and float(r.familiarity) >= float(CONFIG.QA.stable_familiarity) and int(r.success_streak) >= int(CONFIG.QA.stable_success_streak)

func refresh_pool() -> void:
	var ranked: Array = words.keys()
	ranked.sort_custom(func(a, b):
		var pa := priority(a) + (0.0 if stable(a) else float(CONFIG.QA.pool_unstable_bonus))
		var pb := priority(b) + (0.0 if stable(b) else float(CONFIG.QA.pool_unstable_bonus))
		return a < b if is_equal_approx(pa, pb) else pa > pb)
	active_pool.clear()
	for id in ranked.slice(0, clampi(int(CONFIG.QA.active_pool_size), 5, 8)):
		active_pool.append(str(id))
	# Reserve discoverable senses while they exist; old difficult words must not starve all discovery.
	var new_words: Array = ranked.filter(func(id): return words[id].current_state in ["UNKNOWN", "ENCOUNTERED"])
	var required_new := mini(2, new_words.size())
	for id in new_words:
		if active_pool.filter(func(key): return words[key].current_state in ["UNKNOWN", "ENCOUNTERED"]).size() >= required_new: break
		if id not in active_pool:
			for index in range(active_pool.size() - 1, -1, -1):
				if words[active_pool[index]].current_state not in ["UNKNOWN", "ENCOUNTERED"]:
					active_pool[index] = str(id)
					break
	if not pool_override.is_empty(): active_pool.assign(pool_override)
	for id in records:
		records[id].active = id in active_pool
	var successes := 0
	var failures := 0
	for r in records.values():
		successes += int(r.success_streak)
		failures += int(r.failure_streak)
	new_ratio = clampf(float(CONFIG.QA.mode_new.get(pace, 0.6)) + clampf(float(successes - failures) * float(CONFIG.QA.ratio_per_streak), -float(CONFIG.QA.ratio_adjust_limit), float(CONFIG.QA.ratio_adjust_limit)), float(CONFIG.QA.ratio_min), float(CONFIG.QA.ratio_max))

func eligible(id: String, node: Dictionary) -> bool:
	# Finite authored senses, not an unrestricted dictionary draw. Each needs a native carrier.
	if not words.has(id) or id not in node.get("words", []) or node.get("biome", "cemetery") != "cemetery" or id not in active_pool or stable(id) or cooldown(id) > 0: return false
	# Combat carries observed context, not recognition quizzes or post-combat production popups.
	if "COMBAT" in node.get("tags", []) and (not words[id].is_recognized() or weak_layer(id) != "context"): return false
	if "DANGEROUS_MYSTERY" in node.get("tags", []): return false
	if words[id].current_state in ["UNKNOWN", "ENCOUNTERED"]:
		var profile := catalog_profile(id)
		if player_level < int(profile.min_level) or float(profile.usefulness) < float(CONFIG.QA.new_min_usefulness) or float(profile.difficulty) > float(CONFIG.QA.new_max_difficulty): return false
	return true

func catalog_profile(id: String) -> Dictionary:
	return {"biome": "cemetery", "min_level": 1, "usefulness": 0.7, "difficulty": 0.7 if id == "REASSEMBLE" else 0.4, "family": family(id)}

## The family a word is paced by: two words from one family in a row are less likely.
func family(id: String) -> String:
	return LIBRARY.primary_tag(id, FAMILIES.get(id, "UNSUPPORTED"))

func variety(id: String) -> float:
	var recent: Array = timeline.filter(func(row): return not str(row.primary).is_empty())
	if not recent.is_empty() and family(str(recent.back().primary)) == family(id):
		return float(CONFIG.QA.semantic_repeat)
	return 1.0

func choose_target(node: Dictionary, rng: RandomNumberGenerator, learning_streak: int) -> String:
	selection_weights.clear()
	var total := 0.0
	var category_totals := {"new": 0.0, "review": 0.0}
	for id in words:
		if eligible(id, node):
			var group := "new" if words[id].current_state in ["UNKNOWN", "ENCOUNTERED"] else "review"
			category_totals[group] += priority(id) * variety(id)
	for id in words:
		var allowed := eligible(id, node) and learning_streak < CONFIG.LEARNING_CAP
		var is_new: bool = words[id].current_state in ["UNKNOWN", "ENCOUNTERED"]
		var balance := new_ratio if is_new else 1.0 - new_ratio
		var repeat: float = CONFIG.QA.learning_repeat if learning_streak == 1 else 1.0
		var group_total: float = category_totals["new" if is_new else "review"]
		var weight := priority(id) * variety(id) * balance * repeat / maxf(0.001, group_total) if allowed else 0.0
		selection_weights.append({"id": id, "eligible": allowed, "biome": 1.0, "scene": 1.0 if id in node.get("words", []) else 0.0, "pool": id in active_pool, "cooldown": cooldown(id), "revisit": priority(id), "difficulty": records[id].difficulty, "variety": variety(id), "catalog": catalog_profile(id), "new_review": balance, "group_total": group_total, "streak": repeat, "final": weight, "weak": weak_layer(id)})
		total += weight
	if total <= 0: return ""
	# A uniform multiplier alone cancels out during sampling. Gate the opportunity itself,
	# so the second consecutive encounter is actually less likely to contain a major focus.
	if learning_streak == 1 and rng.randf() >= float(CONFIG.QA.learning_repeat): return ""
	var roll := rng.randf() * total
	for row in selection_weights:
		roll -= float(row.final)
		if roll < 0: return str(row.id)
	return ""

func begin(node: Dictionary, layer: int) -> void:
	var id := str(node.get("primary", ""))
	encounter = {"layer": layer, "name": node.title, "id": node.id, "tags": node.get("tags", []).duplicate(), "primary": id, "answered": false, "stage_before": words[id].current_state if words.has(id) else "", "source": "%s:%d:%s" % [str(node.id), clock, id]}
	for word_id in node.get("words", []):
		if words.has(word_id): ambient(str(word_id))

func ambient(id: String) -> void:
	if not records.has(id): return
	var r: Dictionary = records[id]
	# One gain per complete Encounter, not per frame/intent/lexicon opening.
	if int(r.last_appearance) != clock:
		r.familiarity = minf(100, float(r.familiarity) + float(CONFIG.QA.ambient_gain))
		r.last_appearance = clock
	var word = words[id]
	if word.current_state == "UNKNOWN":
		word.current_state = "ENCOUNTERED"
		word.changed.emit("NEW WORD ENCOUNTERED — " + id)

func evidence(id: String, kind: String, correct: bool, source: String = "") -> bool:
	if not words.has(id): return false
	ambient(id)
	# Combat effects for other words stay diagnostic pending evidence, never major progression.
	if encounter.is_empty() or encounter.primary != id or bool(encounter.answered):
		if kind == "context" and correct:
			queue_pending(id, source)
		return false
	var r: Dictionary = records[id]
	var word = words[id]
	var desired := weak_layer(id)
	if kind != desired:
		if kind == "context" and correct: queue_pending(id, source)
		return false
	encounter.answered = true
	r.last_major = clock
	if not correct:
		r.errors[kind] = int(r.errors[kind]) + 1
		r.weakness[kind] = int(r.weakness[kind]) + 1
		r.failures = int(r.failures) + 1
		r.failure_streak = int(r.failure_streak) + 1
		r.success_streak = 0
		r.stability = maxf(0, float(r.stability) - float(CONFIG.QA.error_stability))
		r.difficulty = minf(1, float(r.difficulty) + float(CONFIG.QA.error_difficulty))
		word.changed.emit(id + " — The scene offers another context.")
		save()
		return false
	r.successes = int(r.successes) + 1
	r.success_streak = int(r.success_streak) + 1
	r.failure_streak = 0
	r.stability = minf(1, float(r.stability) + float(CONFIG.QA.success_stability) * (float(CONFIG.QA.hint_stability_factor) if bool(encounter.get("hint_used", false)) else 1.0))
	r.difficulty = maxf(0, float(r.difficulty) - float(CONFIG.QA.success_difficulty))
	r.familiarity = minf(100, float(r.familiarity) + float(CONFIG.QA.correct_gain))
	# Repair the weakest layer first. Correct review does not erase a higher earned stage.
	r.weakness[kind] = maxi(0, int(r.weakness[kind]) - 1)
	word._add_source(kind + ":" + str(encounter.source))
	if kind == "recognition":
		word.recognition_evidence += 1
		word.known_meaning = WORDS.meaning(id) if id in WORDS.DATA else LIBRARY.sense(id, "harmful / poisonous" if id == "TOXIC" else "gradual wearing away / weakening")
	elif kind == "context": word.context_evidence += 1
	else:
		word.production_evidence += 1
		word.transfer_correct = true
	var before: int = word.STATES.find(word.current_state)
	var next := before
	if kind == "recognition" and before < 2: next = 2
	if kind == "context" and before == 2: next = 3
	if kind == "production" and before == 3: next = 4
	word.current_state = word.STATES[next]
	if next >= 3 and not word.has_insight(): word.gameplay_unlocks.append(word.word_id + "_insight")
	if next == 4 and id in ["ERODE", "TOXIC"] and id not in word.unlocked_cards: word.unlocked_cards.append(id)
	if next > before:
		r.stages_needed[word.current_state] = int(r.stage_encounters) + 1
		r.stage_encounters = 0
	word.changed.emit(id + " — " + word.current_state)
	save()
	return true

func queue_pending(id: String, source: String) -> void:
	var marker := {"word": id, "source": source, "clock": clock}
	if not pending.any(func(p): return p.word == id and p.source == source): pending.append(marker)
	if pending.size() > 64: pending.pop_front()

func complete() -> void:
	if encounter.is_empty(): return
	clock += 1
	var id: String = encounter.primary
	if words.has(id):
		records[id].last_major = clock
		records[id].stage_encounters = int(records[id].stage_encounters) + 1
		pending = pending.filter(func(p): return p.word != id)
	timeline.append(encounter.duplicate(true))
	if timeline.size() > 40: timeline.pop_front()
	for key in records:
		if clock - int(records[key].last_appearance) > int(CONFIG.QA.decay_after):
			records[key].familiarity = maxf(0, float(records[key].familiarity) - float(CONFIG.QA.familiarity_decay))
	encounter.clear()
	refresh_pool()
	save()

func set_pace(value: String) -> bool:
	if value not in CONFIG.QA.mode_new: return false
	pace = value
	refresh_pool()
	save()
	return true

func snapshot() -> Dictionary:
	var saved_words := {}
	for id in words:
		var fields := {}
		for field in KNOWLEDGE_FIELDS: fields[field] = words[id].get(field)
		saved_words[id] = fields
	return {"version": 1, "clock": clock, "pace": pace, "player_level": player_level, "words": saved_words, "records": records, "pool": active_pool, "pending": pending, "timeline": timeline}

func save() -> bool:
	if read_only:
		save_error = load_notice
		return false
	if save_path.is_empty(): return true
	# Atomic staging + recoverable previous save. Never silently discard an invalid file.
	var file := FileAccess.open(save_path + ".tmp", FileAccess.WRITE)
	if file == null:
		save_error = "Cannot save learning schedule: " + str(FileAccess.get_open_error())
		push_warning(save_error)
		return false
	file.store_string(JSON.stringify(snapshot()))
	file.close()
	if FileAccess.file_exists(save_path):
		var old := FileAccess.get_file_as_bytes(save_path)
		var backup_path := save_path + ".previous"
		if FileAccess.file_exists(backup_path): backup_path = save_path + ".backup.%d.%d" % [int(Time.get_unix_time_from_system() * 1000000), Time.get_ticks_usec()]
		var backup := FileAccess.open(backup_path, FileAccess.WRITE)
		if backup == null:
			save_error = "Cannot preserve previous learning save; original was not replaced."
			return false
		backup.store_buffer(old)
		backup.close()
	var result := DirAccess.rename_absolute(save_path + ".tmp", save_path)
	save_error = "" if result == OK else "Learning save rename failed: " + str(result)
	return result == OK

func restore(data: Dictionary) -> bool:
	if data.get("version", 0) != 1 or not data.get("records", null) is Dictionary or not data.get("words", null) is Dictionary: return false
	if not numeric(data.get("clock", null)) or not data.get("pending", null) is Array or not data.get("timeline", null) is Array: return false
	if data.words.is_empty() or not numeric(data.get("player_level", 1)): return false
	# Validate into a fresh model, so malformed saves cannot partially mutate the live schedule.
	for id in data.words:
		if not words.has(id): continue
		var fields = data.words[id]
		var r = data.records.get(id, {})
		if not fields is Dictionary or not r is Dictionary: return false
		if fields.get("current_state", "") not in words[id].STATES or not r.get("errors", null) is Dictionary: return false
		for key in records[id]:
			if not r.has(key): return false
		for key in ["familiarity", "difficulty", "stability", "last_major", "last_appearance", "successes", "failures", "success_streak", "failure_streak", "stage_encounters", "hints"]:
			if not numeric(r[key]): return false
		if float(r.familiarity) < 0 or float(r.familiarity) > 100 or float(r.stability) < 0 or float(r.stability) > 1 or float(r.difficulty) < 0 or float(r.difficulty) > 1: return false
		if not r.weakness is Dictionary or not r.stages_needed is Dictionary or not r.corrective_history is Array: return false
		for key in ["recognition", "context", "production"]:
			if not numeric(r.errors.get(key, null)) or not numeric(r.weakness.get(key, null)): return false
		for row in r.corrective_history:
			if not row is Dictionary or not numeric(row.get("variant", null)) or not numeric(row.get("clock", null)): return false
		for field in KNOWLEDGE_FIELDS:
			if not fields.has(field): return false
			var original = words[id].get(field)
			var value = fields[field]
			if original is Array:
				if not value is Array or not value.all(func(item): return item is String): return false
			elif original is Dictionary:
				if not value is Dictionary: return false
			elif original is String:
				if not value is String: return false
			elif original is bool:
				if not value is bool: return false
			elif not numeric(value) or float(value) < 0: return false
	for row in data.pending:
		if not row is Dictionary or not words.has(row.get("word", "")) or not row.get("source", null) is String or not numeric(row.get("clock", null)): return false
	for row in data.timeline:
		if not row is Dictionary or not numeric(row.get("layer", null)) or not row.get("tags", null) is Array or not row.get("primary", null) is String: return false
	clock = maxi(0, int(data.get("clock", 0)))
	player_level = maxi(1, int(data.get("player_level", 1)))
	pace = str(data.get("pace", "Balanced"))
	if pace not in CONFIG.QA.mode_new: pace = "Balanced"
	for id in data.words:
		if not words.has(id): continue
		records[id] = data.records[id].duplicate(true)
		for field in KNOWLEDGE_FIELDS:
			if not data.words[id].has(field): continue
			var value = data.words[id][field]
			if value is Array: words[id].get(field).assign(value)
			else: words[id].set(field, value)
	pending = data.get("pending", []).duplicate(true)
	timeline = data.get("timeline", []).duplicate(true)
	refresh_pool()
	return true

func numeric(value) -> bool:
	return (value is int or value is float) and is_finite(float(value))

func load_saved() -> void:
	if save_path.is_empty() or not FileAccess.file_exists(save_path): return
	var parser := JSON.new()
	var result := parser.parse(FileAccess.get_file_as_string(save_path))
	var data = parser.data if result == OK else null
	if data is Dictionary and restore(data): return
	read_only = true
	load_notice = "Learning save could not be read. Original preserved; saving is disabled until resolved."
	push_warning(load_notice)

func inspector() -> String:
	var lines: Array[String] = ["PACE: %s · New %.0f%% / Review %.0f%% · Clock %d" % [pace, new_ratio * 100, (1 - new_ratio) * 100, clock], "Active pool: " + ", ".join(active_pool), "Pending context (not earned stages): %d" % pending.size(), "QA numbers are provisional, not difficulty penalties."]
	for id in words:
		var r: Dictionary = records[id]
		lines.append("%s · %s · %s\nFamiliarity %.1f · Difficulty %.2f · Stability %.2f\nWeak %s · Cooldown %d · Age %d · Revisit %.2f\nErrors R/C/P %d/%d/%d · Hints %d · Stage encounters %s" % [id, words[id].current_state, "ACTIVE" if id in active_pool else "BACKGROUND", r.familiarity, r.difficulty, r.stability, weak_layer(id), cooldown(id), age(id), priority(id), r.errors.recognition, r.errors.context, r.errors.production, r.hints, str(r.stages_needed)])
	return "\n\n".join(lines)
