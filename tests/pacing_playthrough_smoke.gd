extends SceneTree

const AUTO := preload("res://tests/cemetery_auto_combat.gd")
var failures: Array[String] = []
var successes := 0

func _initialize() -> void:
	for seed_value in [7, 70, 707, 1707, 42, 4303, 999, 12345]:
		var m := RunManager.new()
		m.persistence_path = ""
		m.start_cemetery_run(seed_value)
		var route: Array[String] = []
		for layer in range(6):
			var nodes := m.available_nodes()
			var chosen: Dictionary = nodes[0]
			for n in nodes:
				if n.type == "rest" or n.type == "event": chosen = n; break
			if layer == 4:
				for n in nodes:
					if n.type == "rest": chosen = n; break
			if "RISK" in chosen.tags:
				for n in nodes:
					if n.type == "encounter" and not bool(n.get("elite", false)): chosen = n; break
			chosen = m.select_node(str(chosen.id))
			route.append(str(chosen.id))
			match str(chosen.type):
				"event":
					if not str(chosen.primary).is_empty():
						var id: String = chosen.primary
						m.learning.evidence(id, m.learning.weak_layer(id), true)
					m.finish_world()
				"rest": m.rest("rest")
				"relic": m.finish_relic_choice(m.offer_relics()[0])
				"mystery":
					m.mystery_probe(1)
					m.leave_mystery()
				_:
					var snapshot := m.state.combat_snapshot()
					snapshot.objective = chosen.get("objective", "kill")
					var c := CombatState.new()
					c.start_battle(int(chosen.battle), snapshot, bool(chosen.get("elite", false)))
					m.state.prepared_armor = 0
					if not AUTO.fight(c):
						failures.append("Seed %d · failed %s · HP %d · rounds %d" % [seed_value, chosen.id, c.hp, c.completed_rounds])
						break
					m.complete_combat(c)
					if layer == 5: m.complete_final()
					elif chosen.type == "elite": m.finish_relic_choice(m.offer_relics()[0])
		if m.state.completed and m.state.victory: successes += 1
		print("PACING ROUTE · Seed %d · HP %d · %s" % [seed_value, m.state.hp, " → ".join(route)])
	for message in failures: push_error(message)
	print("PACING_PLAYTHROUGH_SMOKE: %s · %d/8 legal complete runs" % ["PASS" if failures.is_empty() and successes == 8 else "FAIL", successes])
	quit(0 if failures.is_empty() and successes == 8 else 1)
