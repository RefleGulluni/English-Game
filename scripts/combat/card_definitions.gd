extends RefCounted

const STARTER := ["SHATTER", "STRIKE", "STRIKE", "OBSERVE", "OBSERVE", "BIND", "BIND", "STABILIZE", "DEFLECT", "RESTORE", "ERODE", "TOXIC"]

static func definition(card_id: String) -> Dictionary:
	var skill: Dictionary = CombatContent.SKILLS[card_id]
	return {
		"card_type": "MODIFIER" if card_id in ["ERODE", "TOXIC"] else "ACTION",
		"action_family": {"SHATTER": "BREAK", "STRIKE": "KILL", "ERODE": "WEAKEN", "TOXIC": "BYPASS"}.get(card_id, skill["family"]),
		"semantic_family": skill["family"], "reaction_only": card_id == "DEFLECT", "temporary": false, "exhaust_on_use": false, "disabled_reason": "",
		"card_id": card_id, "name": card_id, "category": "REACTION" if card_id == "DEFLECT" else ("SEMANTIC MODIFIER" if card_id in ["ERODE", "TOXIC"] else "CORE ACTION"),
		"focus_cost": int(skill["cost"]), "concept_family": skill["family"], "base_effect": skill["effect"],
		"time_properties": ["REACTION"] if card_id == "DEFLECT" else [], "word_id": card_id.to_lower() if card_id in ["ERODE", "TOXIC"] else "",
		"base_structure_damage": 8 if card_id == "SHATTER" else (2 if card_id == "STRIKE" else 0),
		"base_hp_damage": 3 if card_id == "SHATTER" else (8 if card_id == "STRIKE" else 0),
		"base_armor_damage": 2 if card_id == "SHATTER" else 0,
		"retained_last_turn": false, "requires_word_state": "USABLE" if card_id in ["ERODE", "TOXIC"] else "",
		"combo_tags": [card_id], "fleeting": false, "echo": false, "delayed": false, "prepared": false,
	}
