class_name CombatContent
extends RefCounted

const SKILLS := {
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
		"effect": "Break 8 Armor. Strike an exposed target for 10 HP.",
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
		"effect": "Reduce the dominant Corruption family by 16.",
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
		"tutorial": "Read its intent. Break Bark Armor with SHATTER, and reserve Focus when LASH is coming.",
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
			{"word": "OVERLOOK", "kind": "concept", "family": "Inattention", "corruption": 14, "sense": "to fail to notice something", "partial": "A warning may be missed.", "clear": "Inattention +14. Intent clarity worsens at 40."},
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
]

static func skill_order() -> Array[String]:
	return ["OBSERVE", "SHATTER", "BIND", "DEFLECT", "STABILIZE", "RESTORE"]
