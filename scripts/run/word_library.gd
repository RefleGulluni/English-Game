extends RefCounted
## The word library (D-070, D-071): every word the game knows, read from data/words/ the first
## time anything asks, then kept in memory, so asking costs nothing. Combat, learning and the
## Lexicon all ask here instead of keeping their own lists. Content only: what a player has
## learned lives in their save, not here.
##
## Use through preload: `const WORDS := preload("res://scripts/run/word_library.gd")`, then
## `WORDS.sense("bind")`, `WORDS.effect("strike")`, `WORDS.tags("grave")` ... Lemmas are matched
## without case, so "BIND" and "bind" are the same word.

const DIR := "res://data/words/"

static var _entries := {} # lemma -> the whole entry: {"lemma", "dictionary", "senses"}
static var _order: Array[String] = [] # word_list.txt order
static var _tags := {} # tag -> what it means
static var _regions := {} # region -> the tags it likes
static var _loaded := false
static var _related := {} # lemma -> its page's neighbours, both ways (related())


static func _load() -> void:
	if _loaded:
		return
	_loaded = true
	var table = JSON.parse_string(FileAccess.get_file_as_string(DIR + "tags.json"))
	if table is Dictionary:
		_tags = table.get("tags", {})
		_regions = table.get("regions", {})
	for line in FileAccess.get_file_as_string(DIR + "word_list.txt").split("\n"):
		var lemma := line.get_slice("#", 0).strip_edges().get_slice(" ", 0)
		if lemma.is_empty():
			continue
		var entry = JSON.parse_string(FileAccess.get_file_as_string(DIR + "entries/%s.json" % lemma))
		if entry is Dictionary and not entry.get("senses", []).is_empty():
			_entries[lemma] = entry
			_order.append(lemma)


static func has(lemma: String) -> bool:
	_load()
	return _entries.has(lemma.to_lower())


## Every lemma in the library, in list order.
static func lemmas() -> Array[String]:
	_load()
	return _order.duplicate()


## The game's sense of a word (its first sense; one sense per word for now). Empty if unknown.
static func main_sense(lemma: String) -> Dictionary:
	_load()
	var entry: Dictionary = _entries.get(lemma.to_lower(), {})
	return entry.senses[0] if entry else {}


## The short English meaning shown in game, or `fallback`.
static func sense(lemma: String, fallback := "") -> String:
	return str(main_sense(lemma).get("sense", fallback))


static func role(lemma: String) -> String:
	return str(main_sense(lemma).get("role", ""))


static func tags(lemma: String) -> Array:
	return main_sense(lemma).get("tags", [])


## The tag a word is filed under first: its constellation, and its family for pacing.
static func primary_tag(lemma: String, fallback := "") -> String:
	var t := tags(lemma)
	return str(t[0]) if not t.is_empty() else fallback


## An ability word's effect: {"type", "cost", ...numbers}; empty for other words.
static func effect(lemma: String) -> Dictionary:
	return main_sense(lemma).get("effect", {})


static func sigil(lemma: String) -> String:
	return str(main_sense(lemma).get("sigil", ""))


static func page_line(lemma: String) -> String:
	return str(main_sense(lemma).get("page_line", ""))


## The dictionary half: exam lists, phonetic, forms ... (filled from ECDICT and WordNet).
static func dictionary(lemma: String) -> Dictionary:
	_load()
	return _entries.get(lemma.to_lower(), {}).get("dictionary", {})


static func region_tags(region: String) -> Array:
	_load()
	return _regions.get(region, [])


## How many tags a word shares with what a region likes: 0 keeps it out of that region (D-069,
## D-070) unless the entry asks for the region by hand (`region_override`).
static func region_overlap(lemma: String, region: String) -> int:
	var liked := region_tags(region)
	var shared := 0
	for tag in tags(lemma):
		if tag in liked:
			shared += 1
	if shared == 0 and main_sense(lemma).get("region_override", {}).has(region):
		shared = 1
	return shared


## A word's neighbours on its page (D-092): {"close": [{word, note}], "opposite": [{word}],
## "mixup": [{word, why}], "family": [{word}], "also": [{pos, sense}]}. Every relation but "also"
## runs both ways: an entry names the other word once and the other word's page shows it too,
## its own entry's items first, then the ones mirrored from other entries.
static func related(lemma: String) -> Dictionary:
	_load()
	if _related.is_empty():
		_build_related()
	return _related.get(lemma.to_lower(), {"close": [], "opposite": [], "mixup": [], "family": [], "also": []})



static func _build_related() -> void:
	for lemma in _order:
		var own: Dictionary = main_sense(lemma).get("related", {})
		var page := {"close": [], "opposite": [], "mixup": [], "family": [], "also": own.get("also", []).duplicate()}
		for kind in ["close", "opposite", "mixup", "family"]:
			for item in own.get(kind, []):
				page[kind].append(item.duplicate() if item is Dictionary else {"word": str(item)})
		_related[lemma] = page
	for lemma in _order:
		for kind in ["close", "opposite", "mixup", "family"]:
			for item in _related[lemma][kind]:
				var other := str(item.word)
				if not _related.has(other) or _related[other][kind].any(func(i): return i.word == lemma):
					continue
				var back := {"word": lemma}
				if item.has("why"):
					back.why = item.why
				_related[other][kind].append(back) # no note: a note says how *that* word differs
