extends RefCounted

# Same-name effects refresh; upgrades explicitly replace them. No implicit stacks.
var active: Dictionary = {}

func clear() -> void:
	active.clear()

func apply(effect_id: String, duration: int, potency: int = 0, source: String = "", rule: String = "REFRESH") -> void:
	var turns := duration
	if rule == "EXTEND" and active.has(effect_id):
		turns += int(active[effect_id]["duration"])
	active[effect_id] = {"status_id": effect_id, "name": effect_id, "duration": turns, "potency": potency, "stack_count": 1, "stack_rule": rule, "source": source}

func has(effect_id: String) -> bool:
	return active.has(effect_id)

func duration(effect_id: String) -> int:
	return int(active.get(effect_id, {}).get("duration", 0))

func potency(effect_id: String) -> int:
	return int(active.get(effect_id, {}).get("potency", 0))

func tick_durations(skip_ids: Array[String] = []) -> void:
	for effect_id in active.keys():
		if str(effect_id) in skip_ids:
			continue
		active[effect_id]["duration"] -= 1
		if int(active[effect_id]["duration"]) <= 0:
			active.erase(effect_id)

func rows() -> Array[String]:
	var result: Array[String] = []
	for effect_id in active:
		result.append("%s · %d turns" % [effect_id, duration(effect_id)])
	return result
