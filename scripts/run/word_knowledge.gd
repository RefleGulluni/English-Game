extends RefCounted

signal changed(message: String)

const STATES := ["UNKNOWN", "ENCOUNTERED", "RECOGNIZED", "UNDERSTOOD", "USABLE"]
var word_id := "erode"
var lemma := "ERODE"
var concept_family := "DECAY"
var current_state := "UNKNOWN"
var known_meaning := "Not yet inferred"
var recognition_evidence := 0
var context_evidence := 0
var production_evidence := 0
var gameplay_unlocks: Array[String] = []
var evidence_sources: Array[String] = []
var inscription_completed := false
var root_combat_seen := false
var transfer_offered := false
var transfer_correct := false

func reset() -> void:
	current_state = "UNKNOWN"
	known_meaning = "Not yet inferred"
	recognition_evidence = 0
	context_evidence = 0
	production_evidence = 0
	gameplay_unlocks.clear()
	evidence_sources.clear()
	inscription_completed = false
	root_combat_seen = false
	transfer_offered = false
	transfer_correct = false

func encounter() -> void:
	if current_state == "UNKNOWN":
		current_state = "ENCOUNTERED"
		changed.emit("NEW WORD ENCOUNTERED — ERODE")

func recognize(source: String) -> void:
	encounter()
	if not _add_source("recognition:" + source):
		return
	recognition_evidence += 1
	known_meaning = "gradual wearing away / weakening"
	_advance()

func record_combat_context(observed_exact_effects: bool) -> void:
	root_combat_seen = true
	encounter()
	if not is_recognized() or not observed_exact_effects or not _add_source("context:combat"):
		return
	context_evidence += 1
	_advance()

func record_transfer(correct: bool) -> void:
	if not correct:
		return
	recognize("water_stone")
	transfer_correct = true
	if _add_source("context:water_stone"):
		context_evidence += 1
	_advance()

func record_production(correct: bool) -> void:
	if not correct or not transfer_correct or STATES.find(current_state) < 3:
		return
	if _add_source("production:river_cliff"):
		production_evidence += 1
	_advance()

func is_recognized() -> bool:
	return STATES.find(current_state) >= 2

func has_insight() -> bool:
	return "erode_insight" in gameplay_unlocks

func _add_source(source: String) -> bool:
	if source in evidence_sources:
		return false
	evidence_sources.append(source)
	return true

func _advance() -> void:
	var before := current_state
	if recognition_evidence > 0:
		current_state = "RECOGNIZED"
	if recognition_evidence > 0 and context_evidence > 0:
		current_state = "UNDERSTOOD"
		if not has_insight():
			gameplay_unlocks.append("erode_insight")
	if production_evidence > 0 and transfer_correct:
		current_state = "USABLE"
	changed.emit("ERODE — %s" % current_state if before != current_state else "ERODE — Evidence recorded")

func entry_text() -> String:
	var advantage := "More understanding may reveal how ERODE behaves in combat."
	if is_recognized():
		advantage = "Recognition: ERODE Intent gains +1 clarity before Corruption penalties."
	if has_insight():
		advantage += "\nERODE INSIGHT: gradual structural weakening.\nLikely effect: Armor loss + Decay gain."
	return "Word: %s\nCurrent State: %s\nKnown Meaning: %s\nConcept Family: %s\n\nRecognition Evidence: %d\nContext Evidence: %d\nProduction Evidence: %d\n\nGameplay Knowledge:\n%s" % [lemma, current_state, known_meaning, concept_family, recognition_evidence, context_evidence, production_evidence, advantage]
