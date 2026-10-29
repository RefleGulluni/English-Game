extends SceneTree

# D-078: a word moves through the four stages one step at a time, from evidence found in the
# world, and one encounter moves it at most one stage. The SHATTER route's event cards are valid.
const PROGRESS := preload("res://scripts/run/lexicon_progress.gd")
var failures: Array[String] = []

func _initialize() -> void:
	var progress = PROGRESS.new()
	progress.save_path = ""
	progress.load_or_start()
	_check(progress.stage("shatter") == "UNKNOWN", "SHATTER starts unknown")
	_check(progress.advance("shatter", "context", "a").is_empty(), "no skipping: context does nothing to an unknown word")
	_check(progress.advance("shatter", "ambient") == "ENCOUNTERED", "seeing it: ENCOUNTERED")
	_check(progress.advance("shatter", "recognition", "event:broken_wing") == "RECOGNIZED", "the broken wing: RECOGNIZED")
	_check(progress.advance("shatter", "context", "event:broken_wing").is_empty(), "the same encounter cannot move it twice")
	_check(progress.advance("shatter", "context", "fight:bg_3") == "UNDERSTOOD", "the lent word on the remains: UNDERSTOOD")
	_check(not "shatter" in progress.usable_abilities(), "understood is not yet in hand")
	_check(progress.advance("shatter", "production", "event:cracked_slab") == "USABLE", "the slab: USABLE")
	_check(progress.deck_cards().count("SHATTER") == 1, "a word made usable joins the deck")
	_check(progress.advance("shatter", "recognition", "x").is_empty() and progress.stage("shatter") == "USABLE", "never moves back")
	_check(progress.known_words().any(func(w): return w.lemma == "shatter" and w.stage == "USABLE"), "the book lists it")
	var fresh = PROGRESS.new()
	fresh.save_path = ""
	fresh.load_or_start()
	_check(fresh.advance("shatter", "recognition", "e") == "RECOGNIZED", "recognising a word never seen counts too")

	for file in ["broken_wing", "cracked_slab"]:
		var card = JSON.parse_string(FileAccess.get_file_as_string("res://data/events/cemetery/%s.json" % file))
		_check(card is Dictionary and card.word == "shatter" and card.evidence in PROGRESS.EVIDENCE, "%s card reads" % file)
		if card is Dictionary and card.has("options"):
			_check(card.options.filter(func(o): return bool(o.get("correct", false))).size() == 1, "%s has exactly one right answer" % file)
		if card is Dictionary and card.has("replies"):
			_check(card.replies.has("shatter") and card.replies.shatter.correct and card.replies.has("_default"), "%s answers SHATTER and any other word" % file)
	_finish()

func _check(ok: bool, label: String) -> void:
	if not ok: failures.append(label)

func _finish() -> void:
	if failures.is_empty():
		print("WORD_ROUTE_SMOKE: PASS")
		quit(0)
	else:
		for f in failures: printerr("FAIL: " + f)
		quit(1)
