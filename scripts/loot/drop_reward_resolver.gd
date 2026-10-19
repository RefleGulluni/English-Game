extends RefCounted

var rng := RandomNumberGenerator.new()
var special_chance := 0.10
var roll_history: Array[Dictionary] = []

func setup(seed_value: int) -> void:
	rng.seed = seed_value ^ 9010123 # Separate stream from deck/learning randomness.
	roll_history.clear()

func roll(enemy_tags: Array, pool: Array, force_qa: bool = false, affinity: Dictionary = {}):
	var roll_value := rng.randf()
	var triggered := force_qa or roll_value < special_chance
	roll_history.append({"roll": roll_value, "chance": special_chance, "forced": force_qa, "triggered": triggered})
	if not triggered: return null
	var legal: Array = pool.filter(func(item): return item.ecology_tags.any(func(tag): return tag in enemy_tags))
	var total := 0.0
	for item in legal: total += float(item.weight) * clampf(float(affinity.get(item.id, 1.0)), 1.0, 1.15)
	if total <= 0: return null
	var selected := rng.randf() * total
	for item in legal:
		selected -= float(item.weight) * clampf(float(affinity.get(item.id, 1.0)), 1.0, 1.15)
		if selected < 0: return item
	return legal.back()
