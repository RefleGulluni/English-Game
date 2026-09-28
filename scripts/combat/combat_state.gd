class_name CombatState
extends RefCounted

signal changed
signal battle_finished(victory: bool)
signal reaction_requested(action: Dictionary, cost: int)

const MAX_HP := 50
const BASE_ARMOR := 12
const BASE_FOCUS := 3
const MAX_CARRY := 1

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
	hp = int(run_snapshot.get("hp", MAX_HP))
	armor = int(run_snapshot.get("armor", BASE_ARMOR))
	focus = BASE_FOCUS
	corruption = run_snapshot.get("corruption", {"Decay": 0, "Obscurity": 0, "Inattention": 0}).duplicate(true)
	statuses = run_snapshot.get("statuses", {}).duplicate(true)
	relics.clear()
	for relic in run_snapshot.get("relics", []):
		relics.append(str(relic))
	is_elite = elite
	observe_used_this_battle = false
	quiet_mind_used_this_battle = false
	log_lines.clear()
	action_cursor = 0
	next_intent_penalty = 0
	enemy = CombatContent.BATTLES[index].duplicate(true)
	if is_elite:
		enemy["name"] = "%s · ELITE" % enemy["name"]
		enemy["hp"] = int(ceil(float(enemy["hp"]) * 1.25))
		enemy["armor"] = int(ceil(float(enemy["armor"]) * 1.25))
	enemy["max_hp"] = int(enemy["hp"])
	enemy["max_armor"] = int(enemy["armor"])
	if is_elite:
		_add_corruption("Inattention", 10)
		_update_threshold_statuses()
	_add_log("ENCOUNTER %d · %s" % [index + 1, enemy["name"]])
	_add_log(str(enemy["tutorial"]))
	_begin_player_turn(0, false)

func can_use(skill_name: String) -> bool:
	if enemy.is_empty() or int(enemy["hp"]) <= 0:
		return false
	if skill_name == "DEFLECT":
		return false
	return focus >= skill_cost(skill_name)

func skill_cost(skill_name: String) -> int:
	var cost := int(CombatContent.SKILLS[skill_name]["cost"])
	if skill_name == "OBSERVE":
		if "clear_lens" in relics and not observe_used_this_battle:
			return 0
		if is_elite and int(corruption["Inattention"]) >= 50:
			cost += 1
	return cost

func use_skill(skill_name: String, restore_target: String = "") -> bool:
	if skill_name == "DEFLECT":
		_add_log("DEFLECT is a Reaction. Reserve Focus, then end the turn.")
		changed.emit()
		return false
	if not can_use(skill_name):
		_add_log("Not enough Focus for %s." % skill_name)
		changed.emit()
		return false

	var cost := skill_cost(skill_name)
	match skill_name:
		"OBSERVE":
			focus -= cost
			observe_used_this_battle = true
			intent_clarity = mini(2, intent_clarity + 1)
			metrics["observe_uses"] += 1
			_add_log("OBSERVE · Intent is now %s." % clarity_name())
		"SHATTER":
			focus -= cost
			if int(enemy["armor"]) > 0:
				var before := int(enemy["armor"])
				enemy["armor"] = maxi(0, before - 8)
				_add_log("SHATTER · %d Armor broken." % [before - int(enemy["armor"])])
			if int(enemy["armor"]) == 0:
				var collapse_damage := 10 if "iron_script" in relics else 6
				enemy["hp"] = maxi(0, int(enemy["hp"]) - collapse_damage)
				_add_log("STRUCTURE COLLAPSE · EXPOSED. The collapse deals %d HP." % collapse_damage)
			else:
				enemy["hp"] = maxi(0, int(enemy["hp"]) - 10)
				_add_log("SHATTER · The exposed target loses 10 HP.")
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
			corruption[family] = maxi(0, before - 16)
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

	if int(enemy["hp"]) <= 0:
		_add_log("%s collapses. Understanding created the opening." % enemy["name"])
		changed.emit()
		battle_finished.emit(true)
		return true
	changed.emit()
	return true

func end_player_turn() -> void:
	if enemy.is_empty() or int(enemy["hp"]) <= 0:
		return
	if delayed_this_turn:
		delayed_this_turn = false
		var carry := mini(MAX_CARRY, focus)
		if carry > 0:
			metrics["focus_reserved"] += 1
		_add_log("BIND holds. %s cannot resolve this turn." % intent["word"])
		_tick_statuses()
		_begin_player_turn(carry, true)
		return

	var reaction_cost := 2 if int(corruption["Inattention"]) >= 60 else 1
	if intent["kind"] == "physical" and focus >= reaction_cost:
		reaction_requested.emit(intent, reaction_cost)
		return
	resolve_enemy_action(false)

func resolve_enemy_action(use_deflect: bool) -> void:
	var action := intent
	if action["kind"] == "physical":
		var incoming := int(action["damage"])
		if use_deflect:
			var reaction_cost := 2 if int(corruption["Inattention"]) >= 60 else 1
			focus -= reaction_cost
			incoming = maxi(1, int(ceil(float(incoming) * 0.25)))
			metrics["deflect_uses"] += 1
			metrics["intents_countered"] += 1
			_add_log("DEFLECT · The strike changes course. Damage reduced to %d." % incoming)
		_apply_physical_damage(incoming)
	else:
		var family := str(action["family"])
		_add_corruption(family, int(action["corruption"]))
		if action.has("secondary_family"):
			var secondary := str(action["secondary_family"])
			_add_corruption(secondary, int(action["secondary_corruption"]))
		if action.has("armor_damage"):
			armor = maxi(0, armor - int(action["armor_damage"]))
		if action.has("guard"):
			enemy["armor"] = mini(int(enemy["max_armor"]), int(enemy["armor"]) + int(action["guard"]))
		if action.has("obscure"):
			next_intent_penalty += int(action["obscure"])
		if action.has("status"):
			statuses[str(action["status"])] = int(action["duration"])
		_add_log(_enemy_resolution_text(action))

	exposure[str(action["word"])] = int(exposure.get(str(action["word"]), 0)) + 1
	_update_threshold_statuses()
	if hp <= 0:
		_add_log("Your connection breaks. Read the pattern differently and try again.")
		changed.emit()
		battle_finished.emit(false)
		return
	var carry := mini(MAX_CARRY, focus)
	if carry > 0:
		metrics["focus_reserved"] += 1
	_tick_statuses()
	_begin_player_turn(carry, false)

func _begin_player_turn(carry: int, keep_intent: bool) -> void:
	turn += 1
	focus = BASE_FOCUS + carry
	if not keep_intent:
		intent = _choose_intent()
		intent_bound_once = false
		intent_clarity = _base_intent_clarity(intent)
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
	if "OBSCURITY" in enemy["families"]:
		clarity -= 1
	if int(corruption["Obscurity"]) >= 30:
		clarity -= 1
	if int(corruption["Inattention"]) >= 40:
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
	_set_threshold_status("CARELESS", int(corruption["Inattention"]) >= 80)
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
	return ["OBSCURED", "PARTIAL", "CLEAR"][intent_clarity]

func intent_title() -> String:
	if intent.is_empty():
		return "—"
	return "Something is coming…" if intent_clarity == 0 else str(intent["word"])

func intent_description() -> String:
	if intent.is_empty():
		return ""
	if intent_clarity == 0:
		return "The pattern is present, but its meaning is not yet readable."
	if intent_clarity == 1:
		return str(intent["partial"])
	return "%s\n\nWord sense · %s" % [intent["clear"], intent["sense"]]

func dominant_corruption_family() -> String:
	var family := ""
	var highest := 0
	for key in corruption:
		if int(corruption[key]) > highest:
			highest = int(corruption[key])
			family = str(key)
	return family

func active_status_text() -> String:
	if statuses.is_empty():
		return "STABLE"
	var names: Array[String] = []
	for status in statuses:
		names.append(str(status))
	return ", ".join(names)

func _add_log(text: String) -> void:
	log_lines.append(text)
	if log_lines.size() > 12:
		log_lines.pop_front()
