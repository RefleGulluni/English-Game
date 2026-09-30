extends RefCounted

const NAMES := ["STABLE", "DISTRACTED", "PRESSURED", "CARELESS", "NEGLIGENT"]
const ENTER := [0, 20, 40, 60, 80]
const CLEAR := [0, 10, 30, 50, 70]

static func tier_from_statuses(statuses: Dictionary) -> int:
	var tier := 0
	for index in range(1, NAMES.size()):
		if statuses.has(NAMES[index]):
			tier = index
	return tier

static func update_tier(current: int, value: int) -> int:
	var tier := clampi(current, 0, 4)
	while tier < 4 and value >= ENTER[tier + 1]:
		tier += 1
	while tier > 0 and value < CLEAR[tier]:
		tier -= 1
	return tier

static func sync_statuses(statuses: Dictionary, tier: int) -> void:
	for index in range(1, NAMES.size()):
		statuses.erase(NAMES[index])
	if tier > 0:
		statuses[NAMES[tier]] = 99
