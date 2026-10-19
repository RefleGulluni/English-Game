extends SceneTree

const ROLLER := preload("res://scripts/loot/drop_reward_resolver.gd")
const CHISEL := preload("res://data/loot/loot_weathered_chisel.tres")
var failures: Array[String] = []

func check(value: bool, message: String) -> void:
	if not value: failures.append(message)

func _initialize() -> void:
	var count := 0
	var affinity_count := 0
	for seed_value in range(10000):
		var first := ROLLER.new()
		var second := ROLLER.new()
		first.setup(seed_value)
		second.setup(seed_value)
		var item = first.roll(["BONE", "BURIAL"], [CHISEL])
		var repeated = second.roll(["BONE", "BURIAL"], [CHISEL], false, {"relic.weathered_chisel": 1.15})
		if item != null: count += 1
		if repeated != null: affinity_count += 1
		check((item == null) == (repeated == null), "affinity must never alter special trigger")
	check(count > 800 and count < 1200 and affinity_count == count, "normal rate near ten percent over 10000 Seeds")
	var r := ROLLER.new()
	r.setup(9019)
	check(r.roll(["BONE"], [CHISEL], true) == CHISEL, "first-acceptance QA force drops real legal Chisel data")
	check(r.roll(["MEMORY", "VEIL"], [CHISEL], true) == null, "even forced roll cannot violate ecology")
	for message in failures: push_error(message)
	print("SLICE_LOOT_SMOKE: %s · %d/10000 ordinary triggers" % ["PASS" if failures.is_empty() else "FAIL", count])
	quit(0 if failures.is_empty() else 1)
