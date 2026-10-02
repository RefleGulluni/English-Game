class_name CombatState
extends RefCounted

signal changed
signal battle_finished(victory: bool)
signal reaction_requested(action: Dictionary, cost: int)
signal inattention_tier_changed(tier_name: String)
signal combo_discovered

const MAX_HP := 50
const BASE_ARMOR := 12
const BASE_FOCUS := 3
const MAX_CARRY := 1
const STABILIZE_AMOUNT := 8
const INATTENTION := preload("res://scripts/combat/inattention_rules.gd")
var inattention_tier := 0
var knowledge := preload("res://scripts/run/word_knowledge.gd").new()
var toxic_knowledge := preload("res://scripts/run/word_knowledge.gd").new("toxic")
var enemy_effects := preload("res://scripts/combat/semantic_effects.gd").new()
var player_effects := preload("res://scripts/combat/semantic_effects.gd").new()
var toxic_played_this_turn := false
var fractured_this_turn := false
var dispersed := false
var latest_combo := ""
var resolving_end_effects := false
var end_applied_effects: Array[String] = []
var deck := preload("res://scripts/combat/deck_state.gd").new()
var erosion_turns: int:
	get:
		return enemy_effects.duration("EROSION")
	set(value):
		if value <= 0:
			enemy_effects.active.erase("EROSION")
		else:
			enemy_effects.apply("EROSION", value, erosion_tick, "ERODE")
var erosion_tick: int:
	get:
		return enemy_effects.potency("EROSION") if enemy_effects.has("EROSION") else 2
	set(value):
		if enemy_effects.has("EROSION"):
			enemy_effects.active["EROSION"]["potency"] = value
var erode_played_this_turn := false
var echo_used_this_turn := false
var structure_damaged_this_turn := false
var shatter_played_this_turn := false
var no_structure_damage_turns := 0
var consecutive_shatter_turns := 0
var splinter_revealed := false
var pending_counter := false
var turn_ending := false
var finished := false
var completed_rounds := 0
var objective := "kill"
var false_intent: Dictionary = {}
var intent_options: Array[String] = []
var false_removed := false

var battle_index := 0
var turn := 0
var hp := MAX_HP
var armor := BASE_ARMOR
var focus := BASE_FOCUS
var enemy: Dictionary = {}
var intent: Dictionary = {}
var intent_clarity := 0
var intent_bound_once := false
var delayed_this_turn := false
var next_intent_penalty := 0
var action_cursor := 0
var corruption := {"Decay": 0, "Obscurity": 0, "Inattention": 0}
var statuses: Dictionary = {}
var exposure: Dictionary = {}
var relics: Array[String] = []
var is_elite := false
var structure_collapsed := false
var observe_used_this_battle := false
var quiet_mind_used_this_battle := false
var log_lines: Array[String] = []
var metrics := {
	"observe_uses": 0,
	"bind_uses": 0,
	"stabilize_uses": 0,
	"deflect_uses": 0,
	"focus_reserved": 0,
	"intents_countered": 0,
}

func start_battle(index: int, run_snapshot: Dictionary = {}, elite: bool = false) -> void:
	battle_index = index
	turn = 0
	finished = false
	turn_ending = false
	pending_counter = false
	completed_rounds = 0
	objective = str(run_snapshot.get("objective", "kill"))
	erosion_turns = 0
	erosion_tick = 2
	enemy_effects.clear()
	player_effects.clear()
	dispersed = false
	latest_combo = ""
	resolving_end_effects = false
	end_applied_effects.clear()
	consecutive_shatter_turns = 0
	no_structure_damage_turns = 0
	splinter_revealed = false
	hp = int(run_snapshot.get("hp", MAX_HP))
	armor = int(run_snapshot.get("armor", BASE_ARMOR))
	focus = BASE_FOCUS
	corruption = run_snapshot.get("corruption", {"Decay": 0, "Obscurity": 0, "Inattention": 0}).duplicate(true)
	statuses = run_snapshot.get("statuses", {}).duplicate(true)
	inattention_tier = int(run_snapshot.get("inattention_tier", INATTENTION.tier_from_statuses(statuses)))
	intent = {}
	knowledge = run_snapshot.get("knowledge", preload("res://scripts/run/word_knowledge.gd").new())
	toxic_knowledge = run_snapshot.get("toxic_knowledge", preload("res://scripts/run/word_knowledge.gd").new("toxic"))
	relics.clear()
	for relic in run_snapshot.get("relics", []):
		relics.append(str(relic))
	is_elite = elite
	structure_collapsed = false
	observe_used_this_battle = false
	quiet_mind_used_this_battle = false
	log_lines.clear()
	action_cursor = 0
	next_intent_penalty = 0
	enemy = CombatContent.BATTLES[index].duplicate(true)
	# Migrate the original material profiles; new ecology profiles are explicit.
	if not enemy.has("structure"):
		enemy["structure"] = int(enemy["armor"])
		enemy["armor"] = 0
		enemy["max_armor"] = 12
	enemy["has_structure"] = bool(enemy.get("has_structure", true))
	enemy["toxic_resistance"] = float(enemy.get("toxic_resistance", 0.0))
	enemy["toxic_immune"] = bool(enemy.get("toxic_immune", false))
	enemy["phase_state"] = "NORMAL"
	enemy["enemy_id"] = str(enemy.get("enemy_id", str(enemy["name"]).to_lower().replace(" ", "_")))
	if is_elite:
		enemy["name"] = "%s · ELITE" % enemy["name"]
		enemy["hp"] = int(ceil(float(enemy["hp"]) * 1.25))
		enemy["structure"] = int(ceil(float(enemy["structure"]) * 1.25))
		if index == 5:
			enemy["toxic_immune"] = true
	enemy["max_hp"] = int(enemy["hp"])
	enemy["max_structure"] = int(enemy["structure"])
	deck.reset(int(run_snapshot.get("deck_seed", 5050)) + index * 97, run_snapshot.get("temporary_cards", []))
	if is_elite:
		_add_corruption("Inattention", 10)
	_update_threshold_statuses()
	_add_log("ENCOUNTER %d · %s" % [index + 1, enemy["name"]])
	_add_log(str(enemy["tutorial"]))
	_begin_player_turn(0, false)

func can_use(skill_name: String, instance_id: int = -1) -> bool:
	return disabled_reason(skill_name, instance_id).is_empty()

func disabled_reason(skill_name: String, instance_id: int = -1) -> String:
	if enemy.is_empty() or finished or turn_ending or pending_counter or deck.mulligan_pending:
		return "CONFIRM OPENING HAND" if deck.mulligan_pending else ("ENCOUNTER COMPLETE" if finished else "RESOLVE CURRENT DECISION")
	if skill_name == "DEFLECT":
		return "REACTION ONLY"
	if skill_name in ["ERODE", "TOXIC"] and word_for(skill_name).current_state != "USABLE":
		return "REQUIRES USABLE"
	if dispersed and skill_name not in ["RESTORE", "STABILIZE"]:
		return "TARGET DISPERSED"
	if skill_name == "BIND" and intent_bound_once:
		return "CURRENT INTENT ALREADY BOUND"
	if skill_name == "STABILIZE" and dominant_corruption_family().is_empty():
		return "NO ACTIVE CORRUPTION"
	if skill_name == "TOXIC" and (bool(enemy["toxic_immune"]) or float(enemy["toxic_resistance"]) >= 1.0):
		return "TARGET IMMUNE"
	if skill_name == "ERODE" and int(enemy["structure"]) <= 0 and int(enemy["armor"]) <= 0:
		return "NO VALID STRUCTURE TARGET"
	var card := deck.find_card(skill_name, instance_id)
	if card.is_empty():
		return "NOT IN HAND"
	return "NOT ENOUGH FOCUS" if focus < card_cost(card) else ""

func word_for(card_name: String):
	return toxic_knowledge if card_name == "TOXIC" else knowledge

func card_cost(card: Dictionary) -> int:
	var base := reaction_cost() if str(card["card_id"]) == "DEFLECT" else skill_cost(str(card["card_id"]))
	return base + int(card.get("cost_bonus", 0))

func retain_slots() -> int:
	return 2 if "unfinished_sentence" in relics else 1

func finish_mulligan(ids: Array[int] = []) -> bool:
	var valid := deck.mulligan(ids)
	if valid:
		_add_log("OPENING HAND · %d cards replaced." % ids.size())
		changed.emit()
	return valid

func use_card(instance_id: int, restore_target: String = "") -> bool:
	for card in deck.hand:
		if int(card["instance_id"]) == instance_id:
			return use_skill(str(card["card_id"]), restore_target, instance_id)
	return false

func skill_cost(skill_name: String) -> int:
	var cost := int(CombatContent.SKILLS[skill_name]["cost"])
	if skill_name == "OBSERVE":
		if "clear_lens" in relics and not observe_used_this_battle:
			return 0
		if inattention_tier >= 2:
			cost += 1
	return cost

func use_skill(skill_name: String, restore_target: String = "", instance_id: int = -1) -> bool:
	if skill_name == "DEFLECT":
		_add_log("DEFLECT is a Reaction. Reserve Focus, then end the turn.")
		changed.emit()
		return false
	if not can_use(skill_name, instance_id):
		_add_log("%s is unavailable in this hand or Focus is insufficient." % skill_name)
		changed.emit()
		return false

	var card := deck.find_card(skill_name, instance_id)
	var cost := card_cost(card)
	match skill_name:
		"OBSERVE":
			focus -= cost
			observe_used_this_battle = true
			intent_clarity = mini(2, intent_clarity + 1)
			if str(enemy["phase_state"]) == "FADED":
				enemy_effects.apply("REVEALED", 1, 0, "OBSERVE")
				enemy["phase_state"] = "REVEALED"
				_add_log("REVEALED · 1 turn. Direct Action effectiveness restored; Toxic Resistance remains.")
			if not false_intent.is_empty() and not false_removed:
				false_removed = true
				_add_log("OBSERVE · False possibility removed.")
			if str(intent.get("word", "")) == "ERODE":
				knowledge.record_combat_context(intent_clarity == 2 and inattention_tier < 4)
			metrics["observe_uses"] += 1
			_add_log("OBSERVE · Intent is now %s." % clarity_name())
		"SHATTER":
			focus -= cost
			shatter_played_this_turn = true
			if int(enemy["structure"]) > 0:
				_damage_structure(8, true)
			else:
				var before_armor := int(enemy["armor"])
				var armor_chip := mini(2, before_armor)
				enemy["armor"] = maxi(0, before_armor - 2)
				_damage_enemy_hp(3)
				_add_log("%s · Armor chipped %d; direct damage 3 (remaining Armor absorbs)." % ["INCORPOREAL · SHATTER finds no structure" if not bool(enemy["has_structure"]) else "SHATTER", armor_chip])
			if erode_played_this_turn and erosion_turns > 0 and not fractured_this_turn:
				enemy_effects.apply("EROSION", erosion_turns + 1, 3, "FRACTURED EROSION", "REPLACE")
				fractured_this_turn = true
				_add_log("SEMANTIC RESONANCE — FRACTURED EROSION · Duration +1; Structure tick -3.")
				_discover_combo("fractured_erosion", knowledge)
		"STRIKE":
			focus -= cost
			var damage := 8 + (2 if enemy_effects.has("EXPOSED") else 0)
			if str(enemy["phase_state"]) == "FADED":
				damage = int(damage / 2)
				_add_log("FADED · STRIKE effectiveness -50%.")
			var penetration := 3 if erode_played_this_turn else 0
			var ignored := mini(penetration, int(enemy["armor"]))
			_damage_enemy_hp(damage, penetration)
			_add_log("STRIKE · %d direct damage; %d Armor ignored." % [damage, ignored])
			# The hit reads EXPOSED before its own structural side effect.
			if int(enemy["structure"]) > 0:
				_damage_structure(2, false)
			if erode_played_this_turn:
				_discover_combo("weakened_opening", knowledge)
				_add_log("WEAKENED OPENING · Armor penetration, not extra damage.")
			if toxic_played_this_turn:
				_apply_poison()
				_discover_combo("venomous_strike", toxic_knowledge)
				_add_log("VENOMOUS STRIKE · Normal Strike plus POISONED refresh.")
		"ERODE":
			focus -= cost
			enemy_effects.apply("EROSION", 3, 2, "ERODE")
			erode_played_this_turn = true
			_add_log("ERODE · Gradual weakening applied for %d turns." % erosion_turns)
		"TOXIC":
			focus -= cost
			toxic_played_this_turn = true
			_apply_poison()
		"BIND":
			if intent_bound_once:
				_add_log("This intent has already been bound. Restriction cannot become a permanent stun.")
				changed.emit()
				return false
			focus -= cost
			intent_bound_once = true
			delayed_this_turn = true
			metrics["bind_uses"] += 1
			metrics["intents_countered"] += 1
			_add_log("BIND · %s is delayed by one turn." % intent["word"])
		"STABILIZE":
			var family := dominant_corruption_family()
			if family.is_empty():
				_add_log("No active Corruption to stabilize.")
				changed.emit()
				return false
			focus -= cost
			var before := int(corruption[family])
			corruption[family] = maxi(0, before - STABILIZE_AMOUNT)
			metrics["stabilize_uses"] += 1
			metrics["intents_countered"] += 1
			_add_log("STABILIZE · %s %d → %d." % [family, before, int(corruption[family])])
			_update_threshold_statuses()
		"RESTORE":
			if restore_target.is_empty():
				return false
			focus -= cost
			if restore_target == "hp":
				var amount := 6 if statuses.has("WITHERED") else 8
				hp = mini(MAX_HP, hp + amount)
				_add_log("RESTORE · Recovered %d HP%s." % [amount, " (WITHERED)" if amount < 8 else ""])
			else:
				armor = mini(BASE_ARMOR, armor + 4)
				_add_log("RESTORE · Rebuilt 4 Armor.")

	deck.consume(card)
	if skill_name in ["ERODE", "TOXIC"] and "echo_chamber" in relics and not echo_used_this_turn and not bool(card["echo"]):
		echo_used_this_turn = true
		deck.hand.append(deck.make_card(skill_name, 1, true))
		_add_log("ECHO CHAMBER · Temporary %s copy (+1 Focus, EXHAUST)." % skill_name)
	if skill_name == "SHATTER" and battle_index == 0 and consecutive_shatter_turns >= 2:
		consecutive_shatter_turns = 0
		splinter_revealed = true
		knowledge.enemy_records["ROOT HUSK"] = "REGROWTH: after 2 turns without Structure damage, restore 6 Structure.\nSPLINTER RESPONSE: after 2 consecutive SHATTER turns, the next SHATTER causes 4 Physical Damage; DEFLECT can answer."
		pending_counter = true
		_add_log("SPLINTER RESPONSE — 4 Physical Damage.")
		changed.emit()
		if can_react():
			reaction_requested.emit({"word": "SPLINTER RESPONSE", "kind": "physical", "damage": 4}, reaction_cost())
		else:
			resolve_enemy_action(false)
		return true
	if int(enemy["hp"]) <= 0:
		_enemy_defeated()
	changed.emit()
	return true

func end_player_turn() -> void:
	if enemy.is_empty() or finished or turn_ending or pending_counter or deck.mulligan_pending:
		return
	turn_ending = true
	deck.end_turn(true)
	if objective == "survive" and int(enemy["hp"]) <= 0:
		_enemy_defeated()
		_add_log("DISPERSED · Enemy action cancelled. Objective continues.")
		_finish_round(false)
		return
	if delayed_this_turn:
		delayed_this_turn = false
		_add_log("BIND holds. %s cannot resolve this turn." % intent["word"])
		_finish_round(true)
		return

	var reaction_cost := reaction_cost()
	if intent["kind"] == "physical" and can_react():
		reaction_requested.emit(intent, reaction_cost)
		return
	resolve_enemy_action(false)

func resolve_enemy_action(use_deflect: bool) -> void:
	if finished:
		return
	if use_deflect and not can_react():
		return
	if use_deflect:
		deck.consume(deck.find_card("DEFLECT"))
	if pending_counter:
		pending_counter = false
		var damage := 4
		if use_deflect:
			focus -= reaction_cost()
			damage = 1
			metrics["deflect_uses"] += 1
			metrics["intents_countered"] += 1
		var absorbed := mini(armor, damage)
		armor -= absorbed
		hp = maxi(0, hp - (damage - absorbed))
		_add_log("SPLINTER RESPONSE · Damage %d; Armor absorbs %d." % [damage, absorbed])
		if hp <= 0:
			_finish_battle(false)
		elif int(enemy["hp"]) <= 0 and objective == "kill":
			_finish_battle(true)
		else:
			changed.emit()
		return
	var action := intent
	if action["kind"] == "physical":
		var incoming := int(action["damage"])
		if use_deflect:
			focus -= reaction_cost()
			incoming = maxi(1, int(ceil(float(incoming) * 0.25)))
			metrics["deflect_uses"] += 1
			metrics["intents_countered"] += 1
			_add_log("DEFLECT · The strike changes course. Damage reduced to %d." % incoming)
		_apply_physical_damage(incoming)
		if action.has("physical_corruption"):
			_add_corruption(str(action["family"]), int(action["physical_corruption"]))
			_add_log("%s · %s +%d." % [action["word"], action["family"], action["physical_corruption"]])
	else:
		var family := str(action["family"])
		_add_corruption(family, int(action["corruption"]))
		if action.has("secondary_family"):
			var secondary := str(action["secondary_family"])
			_add_corruption(secondary, int(action["secondary_corruption"]))
		if action.has("armor_damage"):
			armor = maxi(0, armor - int(action["armor_damage"]))
		if action.has("guard"):
			var guard_before := int(enemy["armor"])
			enemy["armor"] = mini(int(enemy["max_armor"]), int(enemy["armor"]) + int(action["guard"]))
			_add_log("%s · Armor %d → %d." % [action["word"], guard_before, enemy["armor"]])
		if action.has("poison"):
			player_effects.apply("POISONED", int(action["poison"]), 3, "TOXIC LEAK")
		if action.has("obscure"):
			next_intent_penalty += int(action["obscure"])
		if action.has("status"):
			statuses[str(action["status"])] = int(action["duration"])
		_add_log(_enemy_resolution_text(action))
		if str(action["word"]) == "ERODE":
			knowledge.record_combat_context(true)

	exposure[str(action["word"])] = int(exposure.get(str(action["word"]), 0)) + 1
	_update_threshold_statuses()
	_finish_round(false)

func can_react() -> bool:
	return not deck.find_card("DEFLECT").is_empty() and focus >= reaction_cost()

func _finish_round(keep_intent: bool) -> void:
	deck.end_turn(false)
	resolving_end_effects = true
	end_applied_effects.clear()
	if erosion_turns > 0:
		if int(enemy["structure"]) > 0:
			_damage_structure(erosion_tick, false)
		else:
			enemy["armor"] = maxi(0, int(enemy["armor"]) - 1)
			_add_log("EROSION · Armor -1; no HP damage.")
	if enemy_effects.has("POISONED") and not dispersed:
		var poison_damage := poison_tick_damage()
		enemy["hp"] = maxi(0, int(enemy["hp"]) - poison_damage)
		_add_log("%s · HP -%d; Structure / Armor bypassed." % ["TOXIC RESISTED" if poison_damage < 3 else "POISONED", poison_damage])
		if int(enemy["hp"]) <= 0 and objective == "survive":
			_enemy_defeated()
	if player_effects.has("POISONED"):
		hp = maxi(0, hp - player_effects.potency("POISONED"))
		_add_log("TOXIC CONSEQUENCE · POISONED bypasses your Armor. HP -3.")
		toxic_knowledge.record_combat_context(true)
	if battle_index == 0:
		consecutive_shatter_turns = consecutive_shatter_turns + 1 if shatter_played_this_turn else 0
		no_structure_damage_turns = 0 if structure_damaged_this_turn else no_structure_damage_turns + 1
		if no_structure_damage_turns >= 2:
			var before := int(enemy["structure"])
			enemy["structure"] = mini(int(enemy["max_structure"]), before + 6)
			no_structure_damage_turns = 0
			_add_log("REGROWTH — Structure restored +%d." % (int(enemy["structure"]) - before))
	completed_rounds += 1
	resolving_end_effects = false
	if hp <= 0:
		_finish_battle(false)
		return
	if finished:
		return
	if int(enemy["hp"]) <= 0 and objective == "kill":
		_finish_battle(true)
		return
	if objective == "survive" and completed_rounds >= 5:
		_add_log("SURVIVE 5 TURNS — Objective complete.")
		_finish_battle(true)
		return
	var carry := mini(MAX_CARRY, focus)
	if carry > 0:
		metrics["focus_reserved"] += 1
	_tick_statuses()
	enemy_effects.tick_durations(end_applied_effects)
	player_effects.tick_durations()
	_begin_player_turn(carry, keep_intent)

func _finish_battle(victory: bool) -> void:
	if finished:
		return
	finished = true
	turn_ending = false
	_add_log("%s · %s" % [enemy.get("name", "ENCOUNTER"), "Victory" if victory else "Connection broken"])
	changed.emit()
	battle_finished.emit(victory)

func _damage_enemy_hp(amount: int, penetration: int = 0) -> void:
	var ignored := mini(int(enemy["armor"]), penetration)
	var absorbed := mini(maxi(0, int(enemy["armor"]) - ignored), amount)
	enemy["armor"] = int(enemy["armor"]) - absorbed
	enemy["hp"] = maxi(0, int(enemy["hp"]) - (amount - absorbed))

func poison_tick_damage() -> int:
	if bool(enemy["toxic_immune"]):
		return 0
	return maxi(0, int(ceil(3.0 * (1.0 - float(enemy["toxic_resistance"])))))

func _apply_poison() -> void:
	if bool(enemy["toxic_immune"]) or float(enemy["toxic_resistance"]) >= 1.0:
		_add_log("TARGET IMMUNE · TOXIC has no effect.")
		return
	enemy_effects.apply("POISONED", 3, 3, "TOXIC")
	_add_log("POISONED · 3 turns, REFRESH not STACK; no immediate HP damage.")
	if poison_tick_damage() < 3:
		_add_log("TOXIC RESISTED · Poison damage reduced to %d." % poison_tick_damage())

func _discover_combo(combo_id: String, word) -> void:
	if combo_id in word.discovered_combos:
		return
	word.discovered_combos.append(combo_id)
	latest_combo = combo_id
	combo_discovered.emit()

func _enemy_defeated() -> void:
	if objective == "survive":
		if not dispersed:
			dispersed = true
			enemy["phase_state"] = "DISPERSED"
			_add_log("NEGLECT WRAITH — DISPERSED. Reforms next turn. Objective continues.")
	else:
		_finish_battle(true)

func retain_disabled_reason(card: Dictionary) -> String:
	if finished or turn_ending or pending_counter:
		return "RESOLVE CURRENT DECISION"
	if deck.mulligan_pending:
		return "CONFIRM OPENING HAND"
	if bool(card.get("retained_last_turn", false)):
		return "CANNOT RETAIN CONSECUTIVELY"
	if not int(card["instance_id"]) in deck.retained_cards and deck.retained_cards.size() >= retain_slots():
		return "RETAIN LIMIT REACHED"
	return ""

func _damage_structure(amount: int, _collapse_damage: bool) -> void:
	var before := int(enemy["structure"])
	enemy["structure"] = maxi(0, before - amount)
	structure_damaged_this_turn = structure_damaged_this_turn or before > int(enemy["structure"])
	_add_log("STRUCTURE PRESSURE · -%d Structure." % (before - int(enemy["structure"])))
	if before > 0 and int(enemy["structure"]) == 0:
		structure_collapsed = true
		enemy_effects.apply("EXPOSED", 3 if "iron_script" in relics else 2, 0, "STRUCTURE COLLAPSE")
		if resolving_end_effects:
			end_applied_effects.append("EXPOSED")
		_add_log("STRUCTURE COLLAPSE · EXPOSED %d turns. No HP damage; Armor remains." % enemy_effects.duration("EXPOSED"))

func _begin_player_turn(carry: int, keep_intent: bool) -> void:
	turn += 1
	turn_ending = false
	erode_played_this_turn = false
	toxic_played_this_turn = false
	fractured_this_turn = false
	echo_used_this_turn = false
	shatter_played_this_turn = false
	structure_damaged_this_turn = false
	deck.begin_turn()
	if dispersed:
		enemy["hp"] = int(enemy["max_hp"])
		dispersed = false
		_add_log("NEGLECT WRAITH — REFORMED · HP restored to full. Objective continues.")
	if battle_index == 5:
		enemy["phase_state"] = "FADED" if turn % 2 == 0 else "NORMAL"
		_add_log("PHASE SHIFT · %s." % enemy["phase_state"])
	else:
		enemy["phase_state"] = "NORMAL"
	focus = BASE_FOCUS + carry
	if not keep_intent:
		intent = _choose_intent()
		if str(intent["word"]) == "ERODE":
			knowledge.encounter()
			knowledge.root_combat_seen = true
		intent_bound_once = false
		intent_clarity = _base_intent_clarity(intent)
		false_intent = {}
		false_removed = false
		intent_options.clear()
		if battle_index == 1 and turn % 2 == 1:
			for action in enemy["actions"]:
				if action["word"] != intent["word"]:
					false_intent = action.duplicate(true)
					break
			intent_options.assign([str(intent["word"]), str(false_intent["word"])])
			if deck.rng.randi_range(0, 1) == 1:
				intent_options.reverse()
	_add_log("TURN %d · Focus %d." % [turn, focus])
	changed.emit()

func _choose_intent() -> Dictionary:
	var sequence: Array = enemy["sequence"]
	var word := str(sequence[action_cursor % sequence.size()])
	action_cursor += 1
	for action in enemy["actions"]:
		if action["word"] == word:
			return action.duplicate(true)
	return enemy["actions"][0].duplicate(true)

func _base_intent_clarity(action: Dictionary) -> int:
	var known := int(exposure.get(str(action["word"]), 0))
	var clarity := 1 if known > 0 else 0
	if battle_index == 0 and action["kind"] == "physical":
		clarity = 2
	if str(action["word"]) == "ERODE" and knowledge.is_recognized():
		clarity += 1
	if action.has("poison") and toxic_knowledge.is_recognized():
		clarity += 1
	if "OBSCURITY" in enemy["families"]:
		clarity -= 1
	if int(corruption["Obscurity"]) >= 30:
		clarity -= 1
	if inattention_tier >= 1:
		clarity -= 1
	clarity -= next_intent_penalty
	next_intent_penalty = 0
	return clampi(clarity, 0, 2)

func _apply_physical_damage(amount: int) -> void:
	var absorbed := mini(armor, amount)
	armor -= absorbed
	var health_damage := amount - absorbed
	hp = maxi(0, hp - health_damage)
	_add_log("%s · Armor absorbs %d; HP loses %d." % [intent["word"], absorbed, health_damage])

func _add_corruption(family: String, amount: int) -> void:
	var applied := amount
	if family == "Inattention" and "quiet_mind" in relics and not quiet_mind_used_this_battle:
		applied = maxi(0, amount - 5)
		quiet_mind_used_this_battle = true
		_add_log("QUIET MIND · Inattention gain reduced by 5.")
	corruption[family] = mini(100, int(corruption[family]) + applied)

func _enemy_resolution_text(action: Dictionary) -> String:
	var result := "%s resolves" % action["word"]
	if action.has("armor_damage"):
		result += " · Armor -%d" % int(action["armor_damage"])
	result += " · %s +%d" % [action["family"], int(action["corruption"])]
	if action.has("secondary_family"):
		result += " · %s +%d" % [action["secondary_family"], int(action["secondary_corruption"])]
	if action.has("status"):
		result += " · %s" % action["status"]
	return result + "."

func _update_threshold_statuses() -> void:
	var previous := inattention_tier
	inattention_tier = INATTENTION.update_tier(previous, int(corruption["Inattention"]))
	INATTENTION.sync_statuses(statuses, inattention_tier)
	if previous != inattention_tier:
		var tier_name: String = INATTENTION.NAMES[inattention_tier]
		_add_log("INATTENTION %s — %s" % ["THRESHOLD CROSSED" if inattention_tier > previous else "RECOVERED", tier_name])
		if previous == 0 and inattention_tier > 0 and not intent.is_empty():
			intent_clarity = maxi(0, intent_clarity - 1)
		inattention_tier_changed.emit(tier_name)
	_set_threshold_status("FRAGILE", int(corruption["Decay"]) >= 60)

func _set_threshold_status(status: String, active: bool) -> void:
	if active:
		statuses[status] = 99
	elif statuses.has(status) and int(statuses[status]) >= 90:
		statuses.erase(status)

func _tick_statuses() -> void:
	var expired: Array[String] = []
	for status in statuses:
		if int(statuses[status]) < 90:
			statuses[status] = int(statuses[status]) - 1
			if int(statuses[status]) <= 0:
				expired.append(status)
	for status in expired:
		statuses.erase(status)
		_add_log("%s fades." % status)

func clarity_name() -> String:
	if inattention_tier == 4:
		return "DEGRADED"
	return ["OBSCURED", "PARTIAL", "CLEAR"][intent_clarity]

func intent_title() -> String:
	if intent.is_empty():
		return "—"
	if not false_intent.is_empty() and not false_removed:
		return "Intent A: %s   /   Intent B: %s" % [intent_options[0], intent_options[1]]
	if inattention_tier == 4:
		return str(intent["word"])
	return "Something is coming…" if intent_clarity == 0 else str(intent["word"])

func intent_description() -> String:
	if intent.is_empty():
		return ""
	if not false_intent.is_empty() and not false_removed:
		return "FALSE INTENT · One possibility is real.\nOBSERVE removes the false possibility.\n%s" % ("High Obscurity further reduces reliable detail." if int(corruption["Obscurity"]) >= 30 else "The moth conceals which one will resolve.")
	if inattention_tier == 4:
		return "%s\n\nWARNING DEGRADED · Exact damage and effects are unavailable.\nWord sense · %s" % [intent["partial"], intent["sense"]]
	var extra := knowledge_intent_hint()
	if intent_clarity == 0:
		return "The pattern is present, but its meaning is not yet readable." + extra
	if intent_clarity == 1:
		return str(intent["partial"]) + extra
	return "%s\n\nWord sense · %s%s" % [intent["clear"], intent["sense"], extra]

func knowledge_intent_hint() -> String:
	if intent.has("poison") and toxic_knowledge.is_recognized():
		var toxic_hint := "\n\nKNOWN WORD · TOXIC · %s\nRecognized Concept: harmful / poisonous" % toxic_knowledge.current_state
		if toxic_knowledge.has_insight():
			toxic_hint += "\nKnown Mechanism: delayed HP damage bypasses Armor."
		return toxic_hint
	if intent.is_empty() or not knowledge.is_recognized():
		return ""
	var is_erode := str(intent["word"]) == "ERODE"
	var structural_decay := str(intent.get("family", "")) == "Decay" and intent.has("armor_damage")
	if not is_erode and not (structural_decay and knowledge.has_insight()):
		return ""
	var hint := "\n\nKNOWN WORD · ERODE · %s" % knowledge.current_state
	if is_erode:
		hint += "\nRecognized Concept: gradual weakening\nConcept Family: DECAY"
	if knowledge.has_insight():
		hint += "\nKnown Mechanism: gradual structural weakening\nLikely effect: Armor loss + Decay gain"
	return hint

func dominant_corruption_family() -> String:
	var family := ""
	var highest := 0
	for key in corruption:
		if int(corruption[key]) > highest:
			highest = int(corruption[key])
			family = str(key)
	return family

func active_status_text() -> String:
	var names: Array[String] = [INATTENTION.NAMES[inattention_tier]]
	for status in statuses:
		if not str(status) in INATTENTION.NAMES:
			names.append(str(status))
	var pressure: Array[String] = []
	if inattention_tier >= 1:
		pressure.append("INTENT DEGRADED" if inattention_tier == 4 else "INTENT -1")
	if inattention_tier >= 2:
		pressure.append("OBSERVE +1 FOCUS")
	if inattention_tier >= 3:
		pressure.append("DEFLECT +1 FOCUS")
	if inattention_tier == 4:
		pressure.append("WARNING RELIABILITY REDUCED")
	names.append_array(pressure)
	names.append_array(player_effects.rows())
	return "\n".join(names)

func reaction_cost() -> int:
	return 2 if inattention_tier >= 3 else 1

func _add_log(text: String) -> void:
	log_lines.append(text)
	if log_lines.size() > 12:
		log_lines.pop_front()

func trait_text() -> String:
	var text := ""
	match battle_index:
		0:
			text = "TRAIT — REGROWTH: after 2 turns without Structure damage, restore up to 6."
			text += "\nSPLINTER RESPONSE: 4 physical retaliation after repeated SHATTER turns." if splinter_revealed else "\nTRAIT — SPLINTER RESPONSE: repeated force may provoke retaliation."
		1:
			text = "TRAIT — FALSE INTENT: odd turns show two possibilities. OBSERVE eliminates the false one."
		2:
			text = "TRAIT — MISSED WINDOW: Inattention degrades Reaction information, not the opportunity itself."
		4:
			text = "TRAIT — SEALED PLATING: Collapse leaves Armor intact.\nTRAIT — REINFORCE: every third action, Armor +4 (max 18).\nTOXIC RESISTANCE · 0%"
		5:
			text = "TRAIT — INCORPOREAL: Structure NONE; SHATTER only 3 damage.\nTRAIT — PHASE SHIFT: even turns FADED; OBSERVE reveals."
		_:
			text = str(enemy.get("tutorial", ""))
	if objective == "survive":
		text += "\nOBJECTIVE — SURVIVE 5 TURNS: %d / 5 complete." % completed_rounds
	if erosion_turns > 0:
		text += "\nEROSION · %d turns; -%d Structure / -1 Armor." % [erosion_turns, erosion_tick]
	if enemy_effects.has("EXPOSED"):
		text += "\nEXPOSED · %d turns · STRIKE +2 direct damage." % enemy_effects.duration("EXPOSED")
	if enemy_effects.has("POISONED"):
		text += "\nPOISONED · %d turns · HP -%d per tick." % [enemy_effects.duration("POISONED"), poison_tick_damage()]
	if battle_index == 5:
		text += "\n%s%s" % [enemy["phase_state"], " · 1 turn" if enemy_effects.has("REVEALED") else ""]
		text += "\nTOXIC IMMUNE" if bool(enemy["toxic_immune"]) else "\nHIGH TOXIC RESISTANCE · 75%"
	if dispersed:
		text += "\nDISPERSED · Reforms next turn. Objective continues."
	return text
