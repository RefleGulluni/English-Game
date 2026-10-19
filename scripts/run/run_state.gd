class_name RunState
extends RefCounted

const MAX_HP := 50
const MAX_ARMOR := 12
const BASE_FOCUS := 3
const ARMOR_REBUILD_RATIO := 0.30
const NATURAL_DISSIPATION := 5
const RECOVER_HP := 6
const RECOVER_ARMOR := 4
const STABILIZE_AMOUNT := 12
const PRESS_ON_MULTIPLIER := 1.25

const TRANSIENT_STATUSES := ["WITHERED", "EXPOSED", "STAGGERED", "BLINDED"]
const LINGERING_THRESHOLDS := {
	"FRAGILE": {"family": "Decay", "apply": 60, "clear": 60},
}
const INATTENTION := preload("res://scripts/combat/inattention_rules.gd")
var inattention_tier := 0
var knowledge := preload("res://scripts/run/word_knowledge.gd").new()
var toxic_knowledge := preload("res://scripts/run/word_knowledge.gd").new("toxic")
var completed_detours: Array[String] = []
var biome_id := ""
var seed_value := 0
var target_knowledge: Dictionary = {}
var recent_node_types: Array[String] = []
var recent_content: Array[String] = []
var temporary_cards: Array[String] = []
var deck_seed := 5050
var anomaly_resolved := false
var learning_schedule
var pacing := false
var prepared_armor := 0
var initial_usable_words: Array[String] = []

var hp := MAX_HP
var armor := MAX_ARMOR
var corruption := {"Decay": 0, "Obscurity": 0, "Inattention": 0}
var statuses: Dictionary = {}
var echo := 0
var current_layer := 0
var current_node_id := "entry"
var next_reward_multiplier := 1.0
var active_reward_multiplier := 1.0
var relics: Array[String] = []
var completed := false
var extracted := false
var victory := false
var history: Array[String] = []
var world_inventory: Dictionary = {}
var collected_loot_ids: Dictionary = {}
var world_reward_ledger: Dictionary = {}

func reset() -> void:
	learning_schedule = null
	pacing = false
	prepared_armor = 0
	initial_usable_words.clear()
	knowledge.reset()
	toxic_knowledge.reset()
	for word in target_knowledge.values():
		word.reset()
	target_knowledge.clear()
	recent_node_types.clear()
	recent_content.clear()
	biome_id = ""
	completed_detours.clear()
	temporary_cards.clear()
	anomaly_resolved = false
	hp = MAX_HP
	armor = MAX_ARMOR
	corruption = {"Decay": 0, "Obscurity": 0, "Inattention": 0}
	statuses.clear()
	inattention_tier = 0
	echo = 0
	current_layer = 0
	current_node_id = "entry"
	next_reward_multiplier = 1.0
	active_reward_multiplier = 1.0
	relics.clear()
	completed = false
	extracted = false
	victory = false
	history.clear()
	world_inventory.clear()
	collected_loot_ids.clear()
	world_reward_ledger.clear()
	history.append("Entered the Fracture.")

func begin_node(node_id: String) -> void:
	current_node_id = node_id
	active_reward_multiplier = next_reward_multiplier
	next_reward_multiplier = 1.0
	history.append("Entered %s." % node_id)

func grant_world_echo_once(reward_id: String, amount: int) -> bool:
	if amount <= 0 or world_reward_ledger.has(reward_id): return false
	world_reward_ledger[reward_id] = amount
	echo += amount
	history.append("World Echo +%d · %s" % [amount, reward_id])
	return true

func claim_world_loot(instance_id: String, item_id: String) -> bool:
	if instance_id.is_empty() or item_id.is_empty() or collected_loot_ids.has(instance_id): return false
	collected_loot_ids[instance_id] = item_id
	world_inventory[item_id] = int(world_inventory.get(item_id, 0)) + 1
	if item_id.begins_with("relic.") and item_id not in relics: relics.append(item_id)
	history.append("PICK UP · " + item_id)
	return true

func finish_node() -> void:
	current_layer += 1
	active_reward_multiplier = 1.0

func combat_snapshot() -> Dictionary:
	return {
		"hp": hp,
		"armor": armor,
		"corruption": corruption.duplicate(true),
		"statuses": statuses.duplicate(true),
		"inattention_tier": inattention_tier,
		"knowledge": knowledge,
		"toxic_knowledge": toxic_knowledge,
		"temporary_cards": temporary_cards.duplicate(),
		"deck_seed": deck_seed + (current_layer * 15485863 if biome_id == "cemetery" else 0),
		"relics": relics.duplicate(),
		"biome_id": biome_id, "target_knowledge": target_knowledge,
		"pacing": pacing, "prepared_armor": prepared_armor,
	}

func capture_combat(combat: CombatState) -> void:
	hp = combat.hp
	armor = combat.armor
	corruption = combat.corruption.duplicate(true)
	statuses = combat.statuses.duplicate(true)
	inattention_tier = combat.inattention_tier
	knowledge = combat.knowledge
	toxic_knowledge = combat.toxic_knowledge

func apply_post_combat() -> Dictionary:
	var report := {
		"armor_before": armor,
		"armor_after": 0,
		"corruption_before": corruption.duplicate(true),
		"corruption_after": {},
		"cleared_statuses": [],
	}
	var rebuilt := int(ceil(float(MAX_ARMOR) * ARMOR_REBUILD_RATIO))
	armor = mini(MAX_ARMOR, armor + rebuilt)
	report["armor_after"] = armor
	for family in corruption:
		corruption[family] = maxi(0, int(corruption[family]) - NATURAL_DISSIPATION)
	for status in TRANSIENT_STATUSES:
		if statuses.has(status):
			statuses.erase(status)
			report["cleared_statuses"].append(status)
	_update_lingering_statuses()
	report["corruption_after"] = corruption.duplicate(true)
	history.append("Breathing room: Armor rebuilt and Corruption dissipated.")
	return report

func choose_breather(choice: String) -> Dictionary:
	var result := {"choice": choice, "description": ""}
	match choice:
		"recover":
			if hp < MAX_HP:
				var before := hp
				hp = mini(MAX_HP, hp + RECOVER_HP)
				result["description"] = "HP %d → %d" % [before, hp]
			else:
				var before := armor
				armor = mini(MAX_ARMOR, armor + RECOVER_ARMOR)
				result["description"] = "Armor %d → %d" % [before, armor]
		"stabilize":
			var family := dominant_corruption_family()
			if family.is_empty():
				result["description"] = "No active Corruption."
			else:
				var before := int(corruption[family])
				corruption[family] = maxi(0, before - STABILIZE_AMOUNT)
				result["description"] = "%s %d → %d" % [family, before, int(corruption[family])]
				_update_lingering_statuses()
		"press_on":
			next_reward_multiplier = PRESS_ON_MULTIPLIER
			result["description"] = "Next node reward ×1.25"
		_:
			push_error("Unknown Breather choice: %s" % choice)
	history.append("Breather: %s · %s" % [choice, result["description"]])
	return result

func grant_echo(base_amount: int, source: String) -> int:
	var awarded := preview_echo(base_amount)
	echo += awarded
	history.append("Gained %d Echo from %s." % [awarded, source])
	return awarded

func preview_echo(base_amount: int, use_next_multiplier: bool = false) -> int:
	var multiplier := next_reward_multiplier if use_next_multiplier else active_reward_multiplier
	return int(round(float(base_amount) * multiplier))

func add_relic(relic_id: String) -> bool:
	if relic_id in relics:
		return false
	relics.append(relic_id)
	history.append("Claimed relic: %s." % relic_id)
	return true

func dominant_corruption_family() -> String:
	var family := ""
	var highest := 0
	for key in corruption:
		if int(corruption[key]) > highest:
			highest = int(corruption[key])
			family = str(key)
	return family

func refresh_lingering_statuses() -> void:
	_update_lingering_statuses()

func condition_text() -> String:
	return "HP %d/%d   ·   Armor %d/%d\nDecay %d   ·   Obscurity %d   ·   Inattention %d\nEcho %d   ·   Relics %d" % [
		hp, MAX_HP, armor, MAX_ARMOR,
		int(corruption["Decay"]), int(corruption["Obscurity"]), int(corruption["Inattention"]),
		echo, relics.size(),
	]

func _update_lingering_statuses() -> void:
	inattention_tier = INATTENTION.update_tier(maxi(inattention_tier, INATTENTION.tier_from_statuses(statuses)), int(corruption["Inattention"]))
	INATTENTION.sync_statuses(statuses, inattention_tier)
	for status in LINGERING_THRESHOLDS:
		var rule: Dictionary = LINGERING_THRESHOLDS[status]
		var value := int(corruption[str(rule["family"])])
		if value >= int(rule["apply"]):
			statuses[status] = 99
		elif statuses.has(status) and value < int(rule["clear"]):
			statuses.erase(status)
