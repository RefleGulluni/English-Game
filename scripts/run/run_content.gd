class_name RunContent
extends RefCounted

const LAYERS := [
	[
		{"id": "root_husk", "type": "encounter", "title": "ROOT HUSK", "detail": "Known physical and Decay pressure.", "battle": 0, "echo": 20},
		{"id": "fracture_event", "type": "event", "title": "FRACTURE EVENT", "detail": "An uncertain opportunity inside the ruins."},
		{"id": "iron_shell", "type": "encounter", "title": "IRON SHELL · ECOLOGY TEST", "detail": "Optional fixed test branch: plating and poisonous leakage. Does not consume a layer.", "battle": 4, "echo": 15, "detour": true},
	],
	[
		{"id": "semantic_anomaly", "type": "anomaly", "title": "SEMANTIC ANOMALY", "detail": "A repeating phrase loses one word each time. Optional; does not consume a layer."},
		{"id": "ghost", "type": "encounter", "title": "GHOST · ECOLOGY TEST", "detail": "Optional fixed test branch: no Structure, shifting phase, high Toxic Resistance. Does not consume a layer.", "battle": 5, "echo": 15, "detour": true},
		{"id": "veil_moth", "type": "encounter", "title": "VEIL MOTH", "detail": "Obscurity pressure. Reward: 20 Echo.", "battle": 1, "echo": 20},
		{"id": "supply_cache", "type": "cache", "title": "SUPPLY CACHE", "detail": "Choose recovery, stability, or Echo."},
	],
	[
		{"id": "neglect_wraith", "type": "encounter", "title": "NEGLECT WRAITH · SURVIVE", "detail": "Survive 5 turns. Killing is not required.", "battle": 2, "echo": 25, "objective": "survive"},
		{"id": "neglect_wraith_elite", "type": "elite", "title": "NEGLECT WRAITH · ELITE", "detail": "High pressure. Reward: 50 Echo + Prototype Relic.", "battle": 2, "echo": 50, "elite": true},
	],
	[
		{"id": "extract", "type": "extract", "title": "EXTRACT", "detail": "Leave safely with the Echo already earned."},
		{"id": "final_encounter", "type": "final", "title": "ENTER DEEPER", "detail": "Fight the Fractured Husk. Final reward: 90 Echo.", "battle": 3, "echo": 60, "reward_multiplier": 1.5},
	],
]

const EVENTS := [
	{
		"id": "polluted_well",
		"title": "POLLUTED WELL",
		"body": "A dark residue floats on the surface.",
		"choices": [
			{"id": "drink", "title": "DRINK", "effect": "Restore 10 HP · Gain 12 Decay"},
			{"id": "examine", "title": "EXAMINE", "effect": "Read the residue · Gain 10 Echo"},
			{"id": "leave", "title": "LEAVE", "effect": "Nothing happens"},
		],
	},
	{
		"id": "broken_relay",
		"title": "BROKEN RELAY",
		"body": "A fractured signal repeats beneath the static.",
		"choices": [
			{"id": "search", "title": "SEARCH", "effect": "50%: +25 Echo · 50%: +10 Obscurity"},
			{"id": "leave", "title": "LEAVE", "effect": "Preserve your current condition"},
		],
	},
	{
		"id": "injured_wanderer",
		"title": "INJURED WANDERER",
		"body": "A stranger reaches toward the path, too weak to stand.",
		"choices": [
			{"id": "help", "title": "HELP", "effect": "Lose 5 HP · Gain 30 Echo"},
			{"id": "ignore", "title": "IGNORE", "effect": "Nothing happens"},
		],
	},
]

const CACHE_CHOICES := [
	{"id": "medical", "title": "MEDICAL SUPPLY", "effect": "+8 HP"},
	{"id": "stabilizer", "title": "STABILIZER", "effect": "Dominant Corruption -15"},
	{"id": "echo", "title": "ECHO FRAGMENT", "effect": "+30 Echo"},
]

const RELICS := {
	"unfinished_sentence": {"name": "UNFINISHED SENTENCE", "rarity": "EPIC", "rule_type": "retain", "trigger": "each_turn", "description": "Retain Slot +1. Keep up to two unused cards; never retain the same instance consecutively."},
	"echo_chamber": {"name": "ECHO CHAMBER", "rarity": "LEGENDARY", "rule_type": "word_copy", "trigger": "first_usable_word_each_turn", "description": "First USABLE Word played each turn creates an Echo copy: cost +1; Exhaust after use."},
	"clear_lens": {
		"rarity": "RARE", "rule_type": "cost", "trigger": "first_observe_per_combat",
		"name": "CLEAR LENS",
		"description": "The first OBSERVE each combat costs 0 Focus.",
	},
	"iron_script": {
		"rarity": "REFINED", "rule_type": "collapse", "trigger": "structure_collapse",
		"name": "IRON SCRIPT",
		"description": "Structure Collapse applies EXPOSED for one additional turn. No Collapse HP damage.",
	},
	"quiet_mind": {
		"rarity": "RARE", "rule_type": "corruption", "trigger": "first_inattention_gain_per_combat",
		"name": "QUIET MIND",
		"description": "The first Inattention gain each combat is reduced by 5.",
	},
}

const RARITY_COLORS := {"COMMON": Color("d8dce2"), "RARE": Color("68c99b"), "REFINED": Color("68a8ed"), "EPIC": Color("b697e8"), "LEGENDARY": Color("ee8b5b"), "MYTHIC": Color("d76565")}

static func layer_nodes(layer: int) -> Array:
	if layer < 0 or layer >= LAYERS.size():
		return []
	return LAYERS[layer].duplicate(true)

static func node_by_id(node_id: String) -> Dictionary:
	for layer in LAYERS:
		for node in layer:
			if str(node["id"]) == node_id:
				return node.duplicate(true)
	return {}

static func event_for_run(run_index: int) -> Dictionary:
	return EVENTS[run_index % EVENTS.size()].duplicate(true)
