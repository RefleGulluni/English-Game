extends SceneTree

const WORDS := preload("res://scripts/run/cemetery_words.gd")
const CONTENT := preload("res://scripts/run/cemetery_content.gd")
var failures: Array[String] = []
var checks := 0

func check(value: bool, message: String) -> void:
	checks += 1
	if not value and failures.size() < 20: failures.append(message)

func _initialize() -> void:
	var signatures: Dictionary = {}
	var elastic_seen: Dictionary = {}
	for seed_value in range(240):
		var first := RunManager.new()
		var second := RunManager.new()
		first.start_cemetery_run(seed_value)
		second.start_cemetery_run(seed_value)
		check(first.state.target_knowledge.keys() == second.state.target_knowledge.keys(), "same seed reproduces target words")
		check(first.state.target_knowledge.keys().slice(0, 4) == WORDS.CORE, "four core words fixed")
		var elastic: String = first.state.target_knowledge.keys()[4]
		elastic_seen[elastic] = true
		check(elastic in WORDS.ELASTIC and CONTENT.POOL.any(func(entry): return elastic in entry.words and not bool(entry.get("production", false))), "elastic word has a real native carrier")
		for layer in range(6):
			first.state.current_layer = layer
			second.state.current_layer = layer
			var nodes := first.available_nodes()
			check(nodes == second.available_nodes(), "same seed and decisions reproduce route")
			check(nodes == first.available_nodes(), "opening map twice does not reroll")
			var ids: Array[String] = []
			for node in nodes:
				check(str(node.id) not in ids, "map has no duplicate fake choices")
				ids.append(str(node.id))
				check(node.id not in ["root_husk", "iron_shell"], "old off-biome enemies excluded")
			if layer == 0:
				check(not nodes.any(func(n): return n.type == "elite"), "layer one has no elite")
				signatures[str(ids)] = true
			if layer < 5: check(nodes.size() in [2, 3], "two or three branches")
			if layer == 4:
				check(nodes.any(func(n): return n.type in ["event", "rest", "relic"]), "layer five has safe path")
				check(nodes.any(func(n): return bool(n.get("guarantee", false)) and n.words == WORDS.CORE), "missing learning receives explicit opportunity")
			if layer == 5: check(nodes.size() == 1 and nodes[0].id == "mourning_keeper", "sixth layer always boss")
			check(first.state.target_knowledge.MOURN.current_state == "UNKNOWN", "director does not grant evidence")
			if layer < 5:
				for manager in [first, second]:
					manager.state.recent_node_types.append(str(nodes[0].type))
					manager.state.recent_content.append(str(nodes[0].id))
		check(first.director.reward_choices(first.state) == second.director.reward_choices(second.state), "seed reproduces reward choices")
	check(signatures.size() > 30, "different seeds produce varied routes")
	check(elastic_seen.size() == 8, "all eight supported elastic words are reachable")
	for history in [["encounter", "elite"], ["event", "rest"]]:
		var manager := RunManager.new()
		manager.start_cemetery_run(731)
		manager.state.current_layer = 2
		manager.state.recent_node_types.assign(history)
		manager.state.recent_content.assign(["grave_skeleton", "hidden_epitaph"])
		var nodes := manager.available_nodes()
		if history[0] == "encounter":
			check(nodes.any(func(n): return n.type in ["event", "rest", "relic"]), "safe branch after sustained fighting")
		else:
			check(nodes.any(func(n): return n.type in ["encounter", "elite"]), "combat alternative after sustained noncombat")
		for row in manager.director.weights:
			var expected: float = row.base_weight * row.biome_modifier * row.layer_modifier * row.learning_modifier * row.rhythm_modifier * row.repetition_modifier
			check(is_equal_approx(expected, row.final_weight), "weight inspector exposes actual product")
			if row.id == "grave_skeleton": check(row.repetition_modifier < 1, "recent content repetition penalized")
	var manager := RunManager.new()
	manager.start_cemetery_run(123)
	for word in manager.state.target_knowledge.values():
		word.recognize("world")
		word.context("world")
	manager.state.current_layer = 4
	var guaranteed: Dictionary = manager.available_nodes()[0]
	check(guaranteed.type == "event" and guaranteed.words == WORDS.CORE, "all one-step-away core words offered production at layer five")
	for id in guaranteed.words:
		manager.state.target_knowledge[id].produce("wrong", false)
		check(manager.state.target_knowledge[id].current_state == "UNDERSTOOD", "wrong production never unlocks")
		manager.state.target_knowledge[id].produce("actual_use", true)
		check(manager.state.target_knowledge[id].current_state == "USABLE", "correct production completes loop")
	manager.start_cemetery_run(123)
	check(manager.state.target_knowledge.MOURN.current_state == "UNKNOWN", "new run resets Lexicon")
	check(WORDS.lemma("mourning") == "MOURN" and WORDS.lemma("reassembled") == "REASSEMBLE" and WORDS.lemma("eroded") == "ERODE", "ordinary inflections share lemma")
	check(WORDS.lemma("erosion") == "EROSION", "derivations are not silently merged")
	var seen: Dictionary = {}
	for value in range(80):
		manager.start_cemetery_run(value)
		var offer := manager.offer_relics()
		check(offer.size() == 3 and offer == manager.offer_relics(), "stable three-choice reward")
		for id in offer: seen[id] = true
		check(not manager.finish_relic_choice("not_a_relic"), "cannot claim an unoffered Relic")
		manager.finish_relic_choice("")
	check(seen.size() == 8, "all eight Relics in seeded reward pool")
	for message in failures: push_error(message)
	print("CEMETERY_DIRECTOR_SMOKE: %s · %d checks · %d route variants" % ["PASS" if failures.is_empty() else "FAIL", checks, signatures.size()])
	quit(0 if failures.is_empty() else 1)
