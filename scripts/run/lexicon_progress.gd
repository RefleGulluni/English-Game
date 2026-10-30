extends RefCounted
## What this player has learned of the ability words (D-075): one stage per word, kept in their
## save and never lost between runs ("The world forgets. You do not."). Only USABLE ability words
## go into the word bar. Content lives in the word library; this is progress only.
##
## The learning words of the 0.8 schedule (MOURN, ERODE, TOXIC ...) keep their own records in
## learning_schedule.gd; ERODE and TOXIC join the word bar when that schedule makes them USABLE.

const LIBRARY := preload("res://scripts/run/word_library.gd")
const STAGES := ["UNKNOWN", "ENCOUNTERED", "RECOGNIZED", "UNDERSTOOD", "USABLE"]
## Learned in the prologue, one per stop (D-075). Until the prologue exists every new save starts
## with them; the prologue will grant them one at a time instead.
const STARTING_WORDS := ["observe", "stabilize", "bind", "anchor", "strike"]
## Cards each USABLE word adds to the deck; a word not listed adds one.
const COPIES := {"strike": 3, "observe": 2, "bind": 2}
## Ability words that only work through the 0.8 learning schedule.
const SCHEDULED := ["erode", "toxic"]

var save_path := "user://lexicon_progress.json" # empty: nothing is saved (QA and tests)
var stages := {} # lemma -> stage
var ceremonies_seen := 0 # how many times a word became USABLE in play (the first can't be skipped)
var slips_seen := 0 # page slips shown so far: the first few are played in full (D-086)
## Where each stage was learned (D-086): lemma -> {stage: {"line", "where"}}. `line` is the
## sentence the word was met in, the word itself in [brackets]; the page slip copies it out and
## the word's page in the book keeps it.
var meetings := {}


## Reads the save; a player with no save starts as if they had just come through the prologue.
func load_or_start() -> void:
	stages.clear()
	if not save_path.is_empty() and FileAccess.file_exists(save_path):
		var data = JSON.parse_string(FileAccess.get_file_as_string(save_path))
		if data is Dictionary:
			stages = data.get("stages", {})
			ceremonies_seen = int(data.get("ceremonies_seen", 0))
			slips_seen = int(data.get("slips_seen", 0))
			meetings = data.get("meetings", {})
	if stages.is_empty():
		grant_starting_words()


func grant_starting_words() -> void:
	for lemma in STARTING_WORDS:
		set_stage(lemma, "USABLE")


func stage(lemma: String) -> String:
	return str(stages.get(lemma.to_lower(), "UNKNOWN"))


## Moves a word to `value`. Learning only goes forward (a word is never unlearned) unless `force`.
func set_stage(lemma: String, value: String, force := false) -> void:
	var id := lemma.to_lower()
	if force or STAGES.find(value) > STAGES.find(stage(id)):
		stages[id] = value
		save()


func save() -> void:
	if save_path.is_empty():
		return
	var file := FileAccess.open(save_path, FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify({"version": 1, "stages": stages, "ceremonies_seen": ceremonies_seen,
			"slips_seen": slips_seen, "meetings": meetings}, "\t"))


## The ability words this player can use, in library order.
func usable_abilities(schedule = null) -> Array[String]:
	var result: Array[String] = []
	for lemma in LIBRARY.lemmas():
		if LIBRARY.role(lemma) != "ability" and lemma not in SCHEDULED:
			continue
		var learned := stage(lemma) == "USABLE"
		if lemma in SCHEDULED and schedule != null and schedule.words.has(lemma.to_upper()):
			learned = schedule.words[lemma.to_upper()].current_state == "USABLE"
		if learned:
			result.append(lemma)
	return result


## The deck for the next fight: each usable word that combat knows how to play, in copies.
func deck_cards(schedule = null) -> Array[String]:
	var cards: Array[String] = []
	for lemma in usable_abilities(schedule):
		var id := lemma.to_upper()
		if not CombatContent.SKILLS.has(id):
			continue # learned, but its combat effect is not built yet (REVEAL, SEAL, MEND ...)
		for i in int(COPIES.get(lemma, 1)):
			cards.append(id)
	return cards


## Evidence of understanding, from the world (D-078, KB Learning Reference §3.1 / §4): each kind
## moves a word one stage, and only from the stage just below it (0.8 learning_schedule.evidence):
## ambient UNKNOWN → ENCOUNTERED; recognition (from UNKNOWN or ENCOUNTERED) → RECOGNIZED;
## context RECOGNIZED → UNDERSTOOD; production UNDERSTOOD → USABLE.
## One encounter (a room's event, a fight) moves a word at most one stage: `encounter` names it.
## Returns the new stage, or "" when nothing moved.
const EVIDENCE := {"ambient": ["UNKNOWN", "ENCOUNTERED"], "recognition": ["ENCOUNTERED", "RECOGNIZED"],
	"context": ["RECOGNIZED", "UNDERSTOOD"], "production": ["UNDERSTOOD", "USABLE"]}
var _moved_in := {} # lemma -> the encounter that last moved it (this session only)

func advance(lemma: String, kind: String, encounter := "") -> String:
	var id := lemma.to_lower()
	var step: Array = EVIDENCE.get(kind, [])
	if step.is_empty():
		return ""
	var now := stage(id)
	var allowed: bool = now == step[0] or (kind == "recognition" and now == "UNKNOWN")
	if not allowed or (not encounter.is_empty() and kind != "ambient" and _moved_in.get(id, "") == encounter):
		return ""
	set_stage(id, step[1])
	if kind != "ambient":
		_moved_in[id] = encounter
	return step[1]


## Keeps the sentence a word reached `stage` in (D-086); nothing without a sentence.
func remember(lemma: String, stage_reached: String, line: String, where: String) -> void:
	if line.is_empty() or stage_reached.is_empty():
		return
	var id := lemma.to_lower()
	var met: Dictionary = meetings.get(id, {})
	met[stage_reached] = {"line": line, "where": where}
	meetings[id] = met
	save()


## The sentence a word reached `stage_reached` in, or the nearest earlier one; {} if none.
func met_at(lemma: String, stage_reached: String) -> Dictionary:
	var met: Dictionary = meetings.get(lemma.to_lower(), {})
	for i in range(STAGES.find(stage_reached), 0, -1):
		if met.has(STAGES[i]):
			return met[STAGES[i]]
	return {}


## Every word the player has met, in library order, with its stage (for the Lexicon pages).
func known_words() -> Array:
	var result := []
	for lemma in LIBRARY.lemmas():
		if stage(lemma) != "UNKNOWN":
			result.append({"lemma": lemma, "stage": stage(lemma)})
	return result


## Dev: back to the five starting words.
func reset_to_start() -> void:
	stages.clear()
	meetings.clear()
	ceremonies_seen = 0
	slips_seen = 0
	grant_starting_words()


## Dev: every ability word usable at once.
func learn_all_abilities() -> void:
	for lemma in LIBRARY.lemmas():
		if LIBRARY.role(lemma) == "ability":
			set_stage(lemma, "USABLE")
