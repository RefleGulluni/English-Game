extends SceneTree

const AUTO := preload("res://tests/cemetery_auto_combat.gd")
var failures: Array[String] = []

func _initialize() -> void:
	var successful := 0
	for seed_value in [7, 70, 707, 1707, 42, 4303, 999, 12345]:
		var manager := RunManager.new()
		manager.start_cemetery_run(seed_value)
		manager.state.knowledge.recognize("inscription")
		manager.state.toxic_knowledge.recognize("cracked_vial")
		var route: Array[String] = []
		for layer in range(6):
			if manager.state.knowledge.current_state == "UNDERSTOOD":
				manager.state.knowledge.record_transfer(true)
				manager.state.knowledge.record_production(true)
			if manager.state.toxic_knowledge.current_state == "UNDERSTOOD":
				manager.state.toxic_knowledge.record_transfer(true)
				manager.state.toxic_knowledge.record_production(true)
			var choices := manager.available_nodes()
			var chosen: Dictionary = choices[0]
			if layer < 2:
				for node in choices:
					if node.type == "encounter": chosen = node; break
			elif layer < 5:
				for node in choices:
					if node.type == "event" and bool(node.get("guarantee", false)): chosen = node; break
				if manager.state.target_knowledge.values().all(func(word): return word.current_state == "USABLE"):
					for node in choices:
						if node.type in ["rest", "relic"]: chosen = node; break
			chosen = manager.select_node(str(chosen.id))
			route.append(str(chosen.id))
			match str(chosen.type):
				"event":
					for id in chosen.words:
						if not manager.state.target_knowledge.has(id): continue
						var word = manager.state.target_knowledge[id]
						word.recognize(str(chosen.id))
						word.context(str(chosen.id))
						word.produce(str(chosen.id), true)
					manager.finish_learning_event()
				"rest": manager.rest("recover")
				"relic": manager.finish_relic_choice(manager.offer_relics()[0])
				_:
					for id in chosen.words:
						if manager.state.target_knowledge.has(id): manager.state.target_knowledge[id].recognize("field:" + str(chosen.id))
					var snapshot := manager.state.combat_snapshot()
					snapshot.objective = chosen.get("objective", "kill")
					var c := CombatState.new()
					c.start_battle(int(chosen.battle), snapshot, bool(chosen.get("elite", false)))
					if not AUTO.fight(c):
						failures.append("Route policy failed · seed %d · %s · HP %d · rounds %d" % [seed_value, chosen.id, c.hp, c.completed_rounds])
						break
					manager.complete_combat(c)
					if layer == 5: manager.complete_final()
					else:
						manager.choose_breather("recover")
						if chosen.type == "elite": manager.finish_relic_choice(manager.offer_relics()[0])
		if manager.state.completed and manager.state.victory:
			successful += 1
			var usable := 0
			for word in manager.state.target_knowledge.values():
				if word.current_state == "USABLE": usable += 1
			if usable < 2: failures.append("Route lacked two complete learning opportunities")
		print("CEMETERY ROUTE · Seed %d · HP %d · %s" % [seed_value, manager.state.hp, " → ".join(route)])
	if successful != 8: failures.append("All eight legal route samples must reach Biome Clear")
	for message in failures: push_error(message)
	print("CEMETERY_PLAYTHROUGH_SMOKE: %s · %d/8 routes" % ["PASS" if failures.is_empty() else "FAIL", successful])
	quit(0 if failures.is_empty() else 1)
