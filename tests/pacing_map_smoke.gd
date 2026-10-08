extends SceneTree

var failures: Array[String] = []
var checks := 0

func check(value: bool, message: String) -> void:
	checks += 1
	if not value and failures.size() < 20: failures.append(message)

func manager(seed_value: int) -> RunManager:
	var result := RunManager.new()
	result.persistence_path = ""
	result.start_cemetery_run(seed_value)
	return result

func traverse(m: RunManager, history: Array, layer: int, route: String) -> void:
	m.state.current_layer = layer
	m.director.history = history.duplicate(true)
	m.state.recent_content.clear()
	for row in history: m.state.recent_content.append(str(row.id))
	m.director.cache.clear()
	var nodes := m.available_nodes()
	check(nodes == m.available_nodes(), "same map reopen does not reroll")
	if layer == 5:
		check(nodes.size() == 1 and nodes[0].id == "mourning_keeper", "fixed final boss")
		return
	check(nodes.size() == 3, "QA09: three real ordinary choices")
	var types := {}
	var ids := {}
	for node in nodes:
		types[node.type] = int(types.get(node.type, 0)) + 1
		check(not ids.has(node.id), "no duplicate fake choices")
		ids[node.id] = true
		check(not node.title.contains("Study") and not node.title.contains("Learning Event"), "world names, not lessons")
		if layer == 0: check("ELITE" not in node.tags, "no first-layer elite")
		if history.size() >= 2:
			var window: Array = history.slice(-2) + [node]
			check(window.any(func(row): return "RISK" in row.tags), "QA08: every offered branch preserves risk floor: " + route)
		if m.director.streak("ELITE") >= 2: check("ELITE" not in node.tags, "QA13: third elite blocked")
		if m.director.streak("RECOVERY") >= 2 and layer != 4: check("RECOVERY" not in node.tags, "QA12: third recovery blocked")
		if m.director.streak("MAJOR_LEARNING_OPPORTUNITY") >= 2: check(str(node.primary).is_empty(), "QA07: third major blocked")
	for count in types.values(): check(count <= 2, "QA09: never three same-type candidates")
	if layer == 4: check(nodes.any(func(n): return "RECOVERY" in n.tags), "QA10: pre-Boss Recovery always available")
	if m.director.nonrisk_tail() >= 2:
		check(nodes.any(func(n): return "COMBAT" in n.tags and "ELITE" not in n.tags), "Elite never sole Risk Floor route")
	for node in nodes:
		var row := {"id": node.id, "tags": node.tags, "name": node.title, "primary": node.primary, "layer": layer + 1, "route": node.id}
		traverse(m, history + [row], layer + 1, route + "/" + str(node.id))

func _initialize() -> void:
	var signatures := {}
	for seed_value in range(240):
		var m := manager(seed_value)
		var other := manager(seed_value)
		check(m.available_nodes() == other.available_nodes(), "same seed and knowledge reproduces choices")
		signatures[str(m.available_nodes().map(func(n): return n.id))] = true
		# Each seed tries adversarial safe-first choices instead of merely checking risk exists somewhere.
		for layer in range(6):
			var nodes := m.available_nodes()
			if layer < 5:
				check(nodes.size() == 3, "ordinary three-choice generation")
				if layer == 4: check(nodes.any(func(n): return "RECOVERY" in n.tags), "Recovery regardless of health")
			var chosen: Dictionary = nodes[0]
			for node in nodes:
				if "RISK" not in node.tags: chosen = node; break
			m.select_node(str(chosen.id))
			m.cemetery_finish_node()
			if layer >= 2:
				check(m.director.history.slice(-3).any(func(row): return "RISK" in row.tags), "actual safe-first route still meets Risk Floor")
	check(signatures.size() > 30, "seed variability retained")
	# Exhaustively validate EVERY selectable route for representative seeds (3^5 leaves each).
	for seed_value in [1, 7, 42, 707, 4303, 12345]: traverse(manager(seed_value), [], 0, str(seed_value))
	var m := manager(8)
	var multi: Dictionary = m.director.annotate({"id": "qa_recovery", "type": "event", "title": "QA Recovery", "words": [], "tags": ["LOW_RISK", "RECOVERY", "WORLD_EVENT"]})
	check("RECOVERY" in multi.tags and "SAFE" not in multi.tags, "functional tags can override single legacy node type")
	m.state.hp = 10
	m.state.armor = 1
	m.state.corruption = {"Decay": 60, "Obscurity": 45, "Inattention": 20}
	var before_corruption := m.state.corruption.duplicate()
	var result := m.selective_recovery("rest")
	check(not result.is_empty() and m.state.hp == 20 and m.state.armor == 1 and m.state.corruption == before_corruption, "QA11: REST only repairs HP")
	m.selective_recovery("repair")
	check(m.state.armor == 7 and m.state.hp == 20 and m.state.corruption == before_corruption, "QA11: REPAIR only repairs Armor")
	m.selective_recovery("calm")
	check(m.state.corruption.Decay == 45 and m.state.corruption.Obscurity == 45 and m.state.hp == 20, "QA11: CALM only repairs dominant Corruption")
	m.selective_recovery("prepare")
	check(m.state.hp == 23 and m.state.prepared_armor == 2 and m.state.armor == 7, "QA11: prepare grants one next-battle buff, not full heal")
	var c := CombatState.new()
	c.start_battle(5, m.state.combat_snapshot())
	check(c.armor == 9, "Preparation has executable combat effect")
	var poor := manager(8)
	poor.state.hp = 10
	poor.available_nodes()
	var healthy := manager(8)
	healthy.available_nodes()
	check(poor.director.safety > healthy.director.safety, "Adaptive safety increases as health worsens")
	m = manager(99)
	m.selected_node = m.director.annotate({"id": "black_mist_well", "title": "Black Mist Well", "type": "mystery", "words": ["TOXIC"], "primary": ""})
	m.state.begin_node("black_mist_well")
	m.learning.begin(m.selected_node, 1)
	check("RISK" in m.selected_node.tags, "QA14: actual Dangerous Mystery has risk tag")
	check(not m.mystery_probe(1).is_empty() and m.state.hp == 48 and m.state.echo == 12, "QA14: even shallow probe executes real HP loss, not fake Risk")
	check(m.mystery_probe(1).is_empty() and m.state.hp == 48, "probe cannot be repeated for free rewards")
	m.mystery_probe(2)
	check(m.state.corruption.Obscurity == 8 and m.state.echo == 32, "deeper probe higher reward and corruption")
	m.mystery_probe(3)
	check(m.selected_node.type == "encounter" and m.selected_node.battle == 8, "deepest probe triggers executable combat")
	check(m.director.inspector().contains("TIMELINE") and m.learning.inspector().contains("Cooldown"), "QA DEV exposes timeline and learning diagnostics")
	for message in failures: push_error(message)
	print("PACING_MAP_SMOKE: %s · %d checks · %d seed variants" % ["PASS" if failures.is_empty() else "FAIL", checks, signatures.size()])
	quit(0 if failures.is_empty() else 1)
