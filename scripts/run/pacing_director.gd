extends "res://scripts/run/cemetery_director.gd"

const CONFIG := preload("res://scripts/run/pacing_config.gd")
var learning
var history: Array = []
var safety := 0.0
var learning_weights: Dictionary = {}
var last_generated_layer := 0

func reset(value: int) -> void:
	super.reset(value)
	history.clear()
	learning_weights.clear()

func streak(tag: String) -> int:
	var count := 0
	for i in range(history.size() - 1, -1, -1):
		if tag not in history[i].get("tags", []): break
		count += 1
	return count

func nonrisk_tail() -> int:
	var count := 0
	for i in range(history.size() - 1, -1, -1):
		if "RISK" in history[i].get("tags", []): break
		count += 1
	return count

func annotate(raw: Dictionary) -> Dictionary:
	var n := raw.duplicate(true)
	n["biome"] = "cemetery"
	n["tags"] = []
	match str(n.type):
		"encounter", "final": n.tags = ["RISK", "COMBAT"]
		"elite": n.tags = ["RISK", "COMBAT", "ELITE", "HIGH_REWARD"]
		"event": n.tags = ["SAFE", "WORLD_EVENT"]
		"rest": n.tags = ["SAFE", "RECOVERY", "WORLD_EVENT"]
		"relic": n.tags = ["SAFE", "HIGH_REWARD", "WORLD_EVENT"]
		"mystery": n.tags = ["RISK", "DANGEROUS_MYSTERY", "HIGH_REWARD", "WORLD_EVENT"]
	# Legacy 0.7 content gets default tags; explicitly authored functional tags take precedence.
	if raw.has("tags"): n.tags = raw.tags.duplicate()
	# These contexts remain world-native; borrowed words are not injected into arbitrary scenes.
	if n.id == "grave_skeleton": n.words += ["ERODE", "TOXIC"]
	if n.id == "withered_flowers": n.words += ["ERODE"]
	if n.id == "hidden_epitaph": n.words += ["ERODE"]
	if n.id == "caretaker_note": n.words += ["ERODE", "TOXIC"]
	if n.id == "grave_inscription": n.words += ["ERODE"]
	return n

func generate(run) -> Array:
	var layer: int = run.current_layer + 1
	last_generated_layer = layer
	if cache.has(layer):
		weights.assign(weight_cache[layer])
		return cache[layer].duplicate(true)
	var rng := RandomNumberGenerator.new()
	rng.seed = seed_value + layer * 104729
	learning.refresh_pool()
	weights.clear()
	var pool: Array = CONTENT.POOL.duplicate(true)
	pool.append({"id": "black_mist_well", "type": "mystery", "title": "BLACK MIST WELL", "weight": CONFIG.QA.mystery_base, "words": ["CONCEAL", "LINGER", "TOXIC"], "echo": 12})
	pool.append({"id": "cracked_vial", "type": "event", "title": "THE CARETAKER'S VIAL", "weight": 6.0, "words": ["TOXIC", "WITHER"], "echo": 8})
	var risk_required := nonrisk_tail() >= 2 or (layer == 4 and nonrisk_tail() >= 1)
	var dominant: String = run.dominant_corruption_family()
	var corruption_pressure: float = float(run.corruption[dominant]) / 100.0 * float(CONFIG.QA.corruption_pressure) if not dominant.is_empty() else 0.0
	safety = clampf((1 - float(run.hp) / RunState.MAX_HP) * float(CONFIG.QA.hp_pressure) + (1 - float(run.armor) / RunState.MAX_ARMOR) * float(CONFIG.QA.armor_pressure) + corruption_pressure, 0, float(CONFIG.QA.safety_cap))
	safety += float(CONFIG.QA.risk_pressure) * streak("RISK") + (float(CONFIG.QA.elite_pressure) if streak("ELITE") > 0 else 0.0)
	var nodes: Array = []
	if layer == 6:
		var boss := annotate(CONTENT.boss())
		attach_learning(boss, rng)
		cache[layer] = [boss]
		weight_cache[layer] = []
		return cache[layer].duplicate(true)
	for raw in pool:
		var n := annotate(raw)
		var blocked: Array[String] = []
		if layer < int(n.get("min_layer", 1)): blocked.append("MIN LAYER")
		if layer == 1 and "ELITE" in n.tags: blocked.append("NO FIRST-LAYER ELITE")
		if risk_required and ("RISK" not in n.tags or "ELITE" in n.tags): blocked.append("RISK FLOOR / PRE-BOSS LOOKAHEAD")
		if "RECOVERY" in n.tags and streak("RECOVERY") >= CONFIG.RECOVERY_CAP and layer != 5: blocked.append("RECOVERY STREAK CAP")
		if "ELITE" in n.tags and streak("ELITE") >= CONFIG.ELITE_CAP: blocked.append("ELITE STREAK CAP")
		var adaptive := 1.0
		var rhythm := 1.0
		if "RECOVERY" in n.tags:
			adaptive = float(CONFIG.QA.recovery_safety_base) + safety
			if streak("RECOVERY") > 0: rhythm *= float(CONFIG.QA.recovery_repeat)
		if "ELITE" in n.tags and streak("ELITE") > 0: rhythm *= float(CONFIG.QA.elite_repeat)
		var repetition: float = float(CONFIG.QA.content_repetition) if n.id in run.recent_content.slice(-3) else 1.0
		var base: float = float(CONFIG.QA.recovery_base) if "RECOVERY" in n.tags else (float(CONFIG.QA.elite_base) if "ELITE" in n.tags else float(n.weight))
		n.merge({"base_weight": base, "adaptive_modifier": adaptive, "rhythm_modifier": rhythm, "repetition_modifier": repetition, "blocked": blocked, "final_weight": base * adaptive * rhythm * repetition if blocked.is_empty() else 0.0})
		weights.append(n)
	var candidates := weights.duplicate(true)
	# A genuinely selectable recovery is mandatory at layer five; earlier lookahead makes it legal.
	if layer == 5:
		var recovery := annotate(CONTENT.node("rest"))
		recovery["constraint"] = "PRE-BOSS RECOVERY GUARANTEE (overrides recovery streak)"
		nodes.append(recovery)
		candidates = candidates.filter(func(n): return n.id != recovery.id)
	for slot in range(3 - nodes.size()):
		var valid: Array = candidates.filter(func(n): return nodes.filter(func(chosen): return chosen.type == n.type).size() < 2)
		var chosen := pick(valid, rng)
		if chosen.is_empty(): break
		nodes.append(chosen.duplicate(true))
		candidates = candidates.filter(func(n): return n.id != chosen.id)
	# At a forced risk layer there must be normal combat alternatives, never elite-only access.
	for n in nodes:
		attach_learning(n, rng)
		n["constraint"] = n.get("constraint", "RISK FLOOR / PRE-BOSS LOOKAHEAD" if risk_required else "WEIGHTED CHOICE")
		n["detail"] = "Selective recovery: REST / CALM / REPAIR / PREPARE." if "RECOVERY" in n.tags else ("Risk sign: the mist burns. First probe costs 2 HP; deeper exploration offers higher rewards and danger." if n.type == "mystery" else ("A preserved relic. Choose one or leave it." if n.type == "relic" else ("A world encounter. You may examine the scene or continue." if n.type == "event" else "Combat risk · Reward %d Echo." % int(n.get("echo", 0)))))
	cache[layer] = nodes.duplicate(true)
	weight_cache[layer] = weights.duplicate(true)
	return nodes.duplicate(true)

func attach_learning(node: Dictionary, rng: RandomNumberGenerator) -> void:
	var id: String = learning.choose_target(node, rng, streak("MAJOR_LEARNING_OPPORTUNITY"))
	node["primary"] = id
	node["learning_mode"] = learning.weak_layer(id) if not id.is_empty() else "ambient"
	node["learning_offer_chance"] = 0.0 if streak("MAJOR_LEARNING_OPPORTUNITY") >= CONFIG.LEARNING_CAP else (float(CONFIG.QA.learning_repeat) if streak("MAJOR_LEARNING_OPPORTUNITY") == 1 else 1.0)
	node["word_weights"] = learning.selection_weights.duplicate(true)
	if not id.is_empty(): node.tags.append("MAJOR_LEARNING_OPPORTUNITY")

func complete(node: Dictionary, layer: int) -> void:
	history.append({"layer": layer, "id": node.id, "name": node.title, "tags": node.get("tags", []).duplicate(), "primary": node.get("primary", ""), "route": node.id})
	if history.size() > 40: history.pop_front()

func inspector() -> String:
	var lines: Array[String] = ["Learning streak %d · Recovery streak %d · Elite streak %d\nNon-risk tail %d · Safety Pressure %.2f\nLayer 4 lookahead prevents Layer 5 recovery/Risk Floor conflicts.\nElite never the only forced risk. Pre-Boss Recovery overrides recovery streak." % [streak("MAJOR_LEARNING_OPPORTUNITY"), streak("RECOVERY"), streak("ELITE"), nonrisk_tail(), safety], "RECENT DIRECTOR TIMELINE:"]
	lines.insert(1, "Pre-Boss Recovery Guarantee: " + ("ACTIVE" if last_generated_layer == 5 else "NOT THIS LAYER") + "\nRecent 3-Encounter Risk Window: " + str(history.slice(-3).map(func(row): return "RISK" if "RISK" in row.tags else "NON-RISK")))
	for row in history.slice(-8):
		lines.append("Layer %d · %s\nTags %s · Primary %s · Selected %s" % [row.layer, row.name, ", ".join(row.tags), row.primary, row.route])
	lines.append("PERSISTENT RECENT LEARNING TIMELINE (continues across Runs):")
	for row in learning.timeline.slice(-5):
		lines.append("Layer %d · %s\nTags %s · Primary %s · Selected %s" % [row.layer, row.name, ", ".join(row.tags), row.primary, row.id])
	return "\n\n".join(lines)
