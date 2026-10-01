extends RefCounted

const STARTER := ["SHATTER", "SHATTER", "OBSERVE", "OBSERVE", "BIND", "BIND", "STABILIZE", "DEFLECT", "RESTORE", "ERODE"]

static func definition(card_id: String) -> Dictionary:
	var skill: Dictionary = CombatContent.SKILLS[card_id]
	return {
		"card_id": card_id, "name": card_id, "category": "REACTION" if card_id == "DEFLECT" else ("SEMANTIC MODIFIER" if card_id == "ERODE" else "CORE ACTION"),
		"focus_cost": int(skill["cost"]), "concept_family": skill["family"], "base_effect": skill["effect"],
		"time_properties": ["REACTION"] if card_id == "DEFLECT" else [], "word_id": "erode" if card_id == "ERODE" else "",
		"combo_tags": [card_id], "fleeting": false, "echo": false, "delayed": false, "prepared": false,
	}
