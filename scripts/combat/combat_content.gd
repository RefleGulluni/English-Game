class_name CombatContent
extends RefCounted

const SKILLS := {
	"STRIKE": {"cost": 2, "family": "DIRECT HP", "sense": "to hit a target directly", "effect": "Kill: 8 direct damage (Armor absorbs), plus 2 Structure damage. EXPOSED adds 2 direct damage.", "accent": Color("dd7777")},
	"TOXIC": {"cost": 1, "family": "TOXICITY", "sense": "harmful or poisonous", "effect": "Bypass: POISONED for 3 turns; delayed HP -3, bypassing Structure and Armor. Refresh, not Stack.", "accent": Color("92bc62")},
	"ERODE": {"cost": 1, "family": "DECAY", "sense": "to gradually wear away or weaken something", "effect": "USABLE: Erosion for 3 turns; -2 Structure per tick, or -1 Armor without Structure. No direct HP damage.", "accent": Color("b98c60")},
	"OBSERVE": {
		"cost": 1,
		"family": "PERCEPTION",
		"sense": "to watch or examine something carefully",
		"effect": "Reveal one level of the enemy's intent.",
		"accent": Color("63c5da"),
	},
	"SHATTER": {
		"cost": 2,
		"family": "FORCE",
		"sense": "to break something violently into pieces",
		"effect": "Break: 8 Structure damage. Without Structure: Armor -2, then 3 direct damage (remaining Armor absorbs).",
		"accent": Color("ee8b5b"),
	},
	"BIND": {
		"cost": 2,
		"family": "CONTROL",
		"sense": "to tie, restrain, or restrict movement or action",
		"effect": "Delay the current intent by one turn.",
		"accent": Color("b697e8"),
	},
	"DEFLECT": {
		"cost": 1,
		"family": "REACTION",
		"sense": "to cause something moving toward you to change direction",
		"effect": "Reaction: reduce incoming physical damage by 75%.",
		"accent": Color("68a8ed"),
	},
	"STABILIZE": {
		"cost": 1,
		"family": "SEMANTIC PROTECTION",
		"sense": "to make something steady or less likely to change",
		"effect": "Reduce the dominant Corruption family by 8.",
		"accent": Color("68c99b"),
	},
	"RESTORE": {
		"cost": 2,
		"family": "RESTORATION",
		"sense": "to return something to an earlier or better condition",
		"effect": "Choose: recover 8 HP or restore 4 Armor.",
		"accent": Color("e8c867"),
	},
}

const BATTLES := [
	{
		"name": "ROOT HUSK",
		"subtitle": "A body rebuilt by roots and gradual decay.",
		"families": ["DECAY"],
		"hp": 40,
		"armor": 18,
		"tutorial": "Read its intent. Pressure Structure before REGROWTH, and keep DEFLECT plus Focus when LASH is coming.",
		"sequence": ["ERODE", "LASH", "WITHER", "LASH"],
		"actions": [
			{"word": "LASH", "kind": "physical", "damage": 8, "sense": "to strike suddenly and forcefully", "partial": "A sudden physical strike.", "clear": "8 Physical Damage. DEFLECT can react."},
			{"word": "ERODE", "kind": "concept", "family": "Decay", "corruption": 12, "armor_damage": 4, "sense": "to gradually wear away or weaken something", "partial": "Gradual structural weakening detected.", "clear": "Armor -4 and Decay Corruption +12. Counter: STABILIZE."},
			{"word": "WITHER", "kind": "concept", "family": "Decay", "corruption": 8, "status": "WITHERED", "duration": 2, "sense": "to become weak, dry, or lifeless", "partial": "Living strength is fading.", "clear": "Decay +8. Healing received -25% for 2 turns."},
		],
	},
	{
		"name": "VEIL MOTH",
		"subtitle": "Its wings make existing information harder to read.",
		"families": ["OBSCURITY"],
		"hp": 34,
		"armor": 10,
		"tutorial": "Its intents begin Obscured. OBSERVE is how you take information back.",
		"sequence": ["BLUR", "DUST CUT", "CONCEAL", "DUST CUT"],
		"actions": [
			{"word": "DUST CUT", "kind": "physical", "damage": 6, "sense": "a cutting sweep of abrasive wing dust", "partial": "A light physical strike.", "clear": "6 Physical Damage. DEFLECT can react."},
			{"word": "BLUR", "kind": "concept", "family": "Obscurity", "corruption": 12, "obscure": 1, "sense": "to make something difficult to see or understand clearly", "partial": "Information clarity will decrease.", "clear": "Obscurity +12. The next Intent begins one level less clear."},
			{"word": "CONCEAL", "kind": "concept", "family": "Obscurity", "corruption": 8, "guard": 6, "sense": "to hide something from sight or knowledge", "partial": "Something is being hidden.", "clear": "Obscurity +8. The moth gains 6 Veil Armor."},
		],
	},
	{
		"name": "NEGLECT WRAITH",
		"subtitle": "The warning exists. It attacks your ability to notice it.",
		"families": ["INATTENTION"],
		"hp": 38,
		"armor": 8,
		"tutorial": "Watch the thresholds. STABILIZE before warnings and Reactions become unreliable.",
		"sequence": ["OVERLOOK", "RAP", "NEGLIGENCE", "RAP"],
		"actions": [
			{"word": "RAP", "kind": "physical", "damage": 7, "sense": "a quick, sharp blow", "partial": "A quick physical strike.", "clear": "7 Physical Damage. DEFLECT can react."},
			{"word": "OVERLOOK", "kind": "concept", "family": "Inattention", "corruption": 14, "sense": "to fail to notice something", "partial": "A warning may be missed.", "clear": "Inattention +14. DISTRACTED begins at 20: Intent clarity -1."},
			{"word": "NEGLIGENCE", "kind": "concept", "family": "Inattention", "corruption": 18, "sense": "failure to give something enough care or attention", "partial": "Your response is becoming careless.", "clear": "Inattention +18. Reactions cost 2 Focus at 60."},
		],
	},
	{
		"name": "FRACTURED HUSK",
		"subtitle": "Decay moves beneath a veil. Two pressures, one pattern.",
		"families": ["DECAY", "OBSCURITY"],
		"hp": 58,
		"armor": 22,
		"tutorial": "Reveal the threat, then choose: STABILIZE it, BIND it, or break the Husk first.",
		"sequence": ["OBSCURED EROSION", "SPLINTER LASH", "WITHER VEIL", "SPLINTER LASH"],
		"actions": [
			{"word": "SPLINTER LASH", "kind": "physical", "damage": 10, "sense": "a violent strike of broken wood", "partial": "A heavy physical strike.", "clear": "10 Physical Damage. DEFLECT can react."},
			{"word": "OBSCURED EROSION", "kind": "concept", "family": "Decay", "secondary_family": "Obscurity", "corruption": 14, "secondary_corruption": 8, "armor_damage": 5, "obscure": 1, "sense": "gradual weakening hidden from clear perception", "partial": "A hidden process is weakening structure.", "clear": "Armor -5, Decay +14, Obscurity +8. Next Intent loses clarity."},
			{"word": "WITHER VEIL", "kind": "concept", "family": "Decay", "secondary_family": "Obscurity", "corruption": 10, "secondary_corruption": 10, "status": "WITHERED", "duration": 2, "sense": "a shroud that drains living strength", "partial": "The veil carries decay.", "clear": "Decay +10, Obscurity +10. Healing -25% for 2 turns."},
		],
	},
	{
		"name": "IRON SHELL", "enemy_id": "iron_shell", "subtitle": "Break the structure. The plating still protects what is inside.",
		"families": ["MATERIAL"], "hp": 32, "structure": 8, "armor": 18, "max_armor": 18, "has_structure": true,
		"toxic_resistance": 0.0, "toxic_immune": false, "traits": ["SEALED PLATING", "REINFORCE"],
		"tutorial": "SEALED PLATING: Collapse does not remove Armor. REINFORCE every third turn restores up to 4 Armor. TOXIC bypasses plating.",
		"sequence": ["TOXIC LEAK", "SHELL BASH", "REINFORCE"],
		"actions": [
			{"word": "TOXIC LEAK", "kind": "concept", "family": "Decay", "corruption": 0, "poison": 3, "sense": "a harmful substance escaping from the shell", "partial": "A poisonous substance leaks toward you.", "clear": "POISONED for 3 turns: 3 HP damage each round, bypassing Armor."},
			{"word": "SHELL BASH", "kind": "physical", "damage": 5, "sense": "a blow from a heavy shell", "partial": "A plated physical strike.", "clear": "5 Physical Damage. DEFLECT can react."},
			{"word": "REINFORCE", "kind": "concept", "family": "Decay", "corruption": 0, "guard": 4, "sense": "to make a protective layer stronger", "partial": "The plating will be repaired.", "clear": "Armor +4, capped at 18. Structure is not restored."},
		],
	},
	{
		"name": "GHOST", "enemy_id": "ghost", "subtitle": "There is no material structure to break. Watch its phase.",
		"families": ["OBSCURITY"], "hp": 28, "structure": 0, "armor": 0, "max_armor": 0, "has_structure": false,
		"toxic_resistance": 0.75, "toxic_immune": false, "traits": ["INCORPOREAL", "PHASE SHIFT"],
		"tutorial": "INCORPOREAL: Structure NONE. Even turns: FADED, Direct Actions -50%. OBSERVE reveals it for this turn. HIGH TOXIC RESISTANCE.",
		"sequence": ["WHISPER", "PHANTOM TOUCH"],
		"actions": [
			{"word": "WHISPER", "kind": "concept", "family": "Obscurity", "corruption": 12, "obscure": 1, "sense": "a quiet voice that is difficult to locate", "partial": "The voice clouds your perception.", "clear": "Obscurity +12. Next Intent begins one clarity level lower."},
			{"word": "PHANTOM TOUCH", "kind": "physical", "damage": 5, "physical_corruption": 8, "family": "Obscurity", "sense": "a touch from an incorporeal presence", "partial": "A spectral physical strike.", "clear": "5 Physical Damage and Obscurity +8. DEFLECT reduces the physical damage."},
		],
	},
]

static func skill_order() -> Array[String]:
	return ["OBSERVE", "SHATTER", "BIND", "DEFLECT", "STABILIZE", "RESTORE"]
