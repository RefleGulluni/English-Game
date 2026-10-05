extends RefCounted

const CONTENT := preload("res://scripts/run/cemetery_content.gd")
const WORDS := preload("res://scripts/run/cemetery_words.gd")
var seed_value := 0
var cache: Dictionary = {}
var weights: Array[Dictionary] = []
var weight_cache: Dictionary = {}

func reset(value: int) -> void:
	seed_value = value
	cache.clear()
	weights.clear()
	weight_cache.clear()

func pick(entries: Array, rng: RandomNumberGenerator) -> Dictionary:
	var total := 0.0
	for entry in entries:
		total += float(entry.final_weight)
	if total <= 0:
		return {}
	var roll := rng.randf() * total
	for entry in entries:
		roll -= float(entry.final_weight)
		if roll < 0:
			return entry
	return entries.back()

func generate(run) -> Array:
	var layer: int = run.current_layer + 1
	if cache.has(layer):
		weights.assign(weight_cache.get(layer, []))
		return cache[layer].duplicate(true)
	if layer == 6:
		cache[layer] = [CONTENT.boss()]
		weights.clear()
		weight_cache[layer] = []
		return cache[layer].duplicate(true)
	var rng := RandomNumberGenerator.new()
	rng.seed = seed_value + layer * 104729
	weights.clear()
	for entry in CONTENT.POOL:
		var row: Dictionary = entry.duplicate(true)
		var layer_mod := 1.0 if layer >= int(entry.get("min_layer", 1)) else 0.0
		if layer == 1 and entry.type not in ["encounter", "event"]:
			layer_mod = 0.0
		if layer == 5:
			layer_mod *= 2.0 if entry.type in ["rest", "event", "elite"] else 0.4
		var learning := 1.0
		for id in entry.words:
			if run.target_knowledge.has(id):
				var word = run.target_knowledge[id]
				if not word.is_recognized():
					learning += 1.0 if layer >= 3 else 0.3
				elif word.current_state == "UNDERSTOOD" and bool(entry.get("production", false)):
					learning += 2.0 if layer >= 4 else 0.4
				elif word.current_state == "RECOGNIZED":
					learning += 0.8
		var rhythm := 1.0
		if run.recent_node_types.size() >= 2:
			var recent: Array = run.recent_node_types.slice(-2)
			var fights := int(recent[0] in ["encounter", "elite"]) + int(recent[1] in ["encounter", "elite"])
			if fights == 2:
				rhythm = 0.25 if entry.type in ["encounter", "elite"] else 2.5
			elif fights == 0:
				rhythm = 2.5 if entry.type in ["encounter", "elite"] else 0.4
		var repetition := 0.15 if entry.id in run.recent_content.slice(-3) else 1.0
		row.merge({"base_weight": entry.weight, "biome_modifier": 3.0, "layer_modifier": layer_mod, "learning_modifier": learning, "rhythm_modifier": rhythm, "repetition_modifier": repetition, "final_weight": float(entry.weight) * 3.0 * layer_mod * learning * rhythm * repetition})
		weights.append(row)
	var candidates: Array = weights.duplicate(true)
	var nodes: Array = []
	for slot in range(rng.randi_range(2, 3)):
		var chosen := pick(candidates, rng)
		if chosen.is_empty():
			break
		nodes.append(chosen.duplicate(true))
		candidates.erase(chosen)
	# Constraints guarantee opportunity, never evidence or a correct answer.
	if layer >= 3:
		var needs: Array[String] = []
		for id in WORDS.CORE:
			var word = run.target_knowledge[id]
			if not word.is_recognized() or word.current_state == "UNDERSTOOD" or (layer == 5 and word.current_state != "USABLE"):
				needs.append(id)
		if not needs.is_empty():
			var compensation := CONTENT.node("grave_inscription" if layer != 4 else "caretaker_note")
			compensation.words = needs
			compensation["guarantee"] = true
			compensation["safe"] = true
			nodes[0] = compensation
	if layer == 5 and not nodes.any(func(n): return n.type in ["event", "rest", "relic"]):
		nodes[0] = CONTENT.node("rest")
	# A real noncombat alternative after sustained fighting, and vice versa.
	if run.recent_node_types.size() >= 2:
		var recent: Array = run.recent_node_types.slice(-2)
		if recent.all(func(t): return t in ["encounter", "elite"]) and not nodes.any(func(n): return n.type in ["event", "rest", "relic"]):
			nodes[0] = CONTENT.node("rest")
		if recent.all(func(t): return t not in ["encounter", "elite"]) and not nodes.any(func(n): return n.type in ["encounter", "elite"]):
			nodes[-1] = CONTENT.node("grave_skeleton")
	# Constraint replacements must not create duplicate, fake branch choices.
	var unique: Array = []
	var ids: Array[String] = []
	for n in nodes:
		if str(n.id) not in ids:
			unique.append(n)
			ids.append(str(n.id))
	for candidate in candidates:
		if unique.size() >= nodes.size(): break
		if candidate.final_weight > 0 and str(candidate.id) not in ids:
			unique.append(candidate.duplicate(true))
			ids.append(str(candidate.id))
	nodes = unique
	for n in nodes:
		var offered: Array[String] = []
		for id in n.words:
			if run.target_knowledge.has(id): offered.append(str(id))
		n["detail"] = "Study: %s · Reward 8 Echo." % (", ".join(offered) if not offered.is_empty() else "a Cemetery scene") if n.type == "event" else ("Recover or reduce Corruption." if n.type == "rest" else ("Three Relics to choose from, or Skip." if n.type == "relic" else "Cemetery %s · Reward %d Echo." % [n.type, int(n.get("echo", 0))]))
	cache[layer] = nodes
	weight_cache[layer] = weights.duplicate(true)
	return nodes.duplicate(true)

func reward_choices(run) -> Array[String]:
	var rng := RandomNumberGenerator.new()
	rng.seed = seed_value + run.current_layer * 7919 + run.relics.size() * 107
	var candidates: Array = []
	for id in CONTENT.RELICS:
		if id not in run.relics:
			candidates.append({"id": id, "final_weight": 2.0 if id in ["mourner_thread", "ossuary_key", "pale_candle"] else 1.0})
	var result: Array[String] = []
	for slot in range(mini(3, candidates.size())):
		var chosen := pick(candidates, rng)
		result.append(chosen.id)
		candidates.erase(chosen)
	return result
