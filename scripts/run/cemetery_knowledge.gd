extends "res://scripts/run/word_knowledge.gd"

const WORDS := preload("res://scripts/run/cemetery_words.gd")
var current_run_target := true
var is_elastic_slot := false
var semantic_tags := ["DEATH", "MEMORY", "CEMETERY"]

func _init(id: String = "MOURN") -> void:
	word_id = id.to_lower()
	lemma = id.to_upper()
	concept_family = "CEMETERY"
	var library_tags: Array = preload("res://scripts/run/word_library.gd").tags(id)
	if not library_tags.is_empty():
		semantic_tags = library_tags.duplicate()

func recognize(source: String) -> void:
	if schedule != null:
		schedule.evidence(lemma, "recognition", true, source)
		return
	encounter()
	if _add_source("recognition:" + source):
		recognition_evidence += 1
		known_meaning = WORDS.meaning(lemma)
		_advance()

func context(source: String, correct: bool = true) -> void:
	if schedule != null:
		schedule.evidence(lemma, "context", correct, source)
		return
	encounter()
	if correct and is_recognized() and _add_source("context:" + source):
		context_evidence += 1
		_advance()

func produce(source: String, correct: bool) -> void:
	if schedule != null:
		schedule.evidence(lemma, "production", correct, source)
		return
	if correct and current_state in ["UNDERSTOOD", "USABLE"] and _add_source("production:" + source):
		production_evidence += 1
		transfer_correct = true
		_advance()

func _advance() -> void:
	if recognition_evidence > 0:
		current_state = "RECOGNIZED"
	if recognition_evidence > 0 and context_evidence > 0:
		current_state = "UNDERSTOOD"
		if not has_insight():
			gameplay_unlocks.append(word_id + "_insight")
	if recognition_evidence > 0 and context_evidence > 0 and production_evidence > 0:
		current_state = "USABLE"
	changed.emit("%s — %s" % [lemma, current_state])

func dev_set_state(value: String) -> bool:
	if value not in STATES:
		return false
	var previous_schedule = schedule
	schedule = null
	reset()
	if value == "UNKNOWN":
		schedule = previous_schedule
		return true
	encounter()
	if STATES.find(value) >= 2:
		recognize("dev")
	if STATES.find(value) >= 3:
		context("dev")
	if value == "USABLE":
		produce("dev", true)
	schedule = previous_schedule
	return true

func entry_text() -> String:
	var info := "Observe this word in the world."
	if is_recognized():
		info = "Known meaning: " + known_meaning
	if has_insight():
		info += "\nKnowledge: " + str(WORDS.DATA[lemma][4])
	var focus := "ELASTIC" if is_elastic_slot else "CORE"
	if schedule != null: focus = "ACTIVE" if lemma in schedule.active_pool else "BACKGROUND"
	return "Word: %s\nCurrent State: %s\nRecognition Evidence: %d\nContext Evidence: %d\nProduction Evidence: %d\nTarget: %s\n%s" % [lemma, current_state, recognition_evidence, context_evidence, production_evidence, focus, info]
