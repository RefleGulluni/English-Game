extends RefCounted
## The Lexicon's sky as data (D-080, D-088): five levels, each a picture on the left page.
##
##   1 the whole sky: about 12 regions, placed by hand (data/words/sky.json)
##   2 a region: its clusters          3 a cluster: its constellations
##   4 a constellation: its words      5 a word: its own spread
##
## A constellation is a word's `constellation` in the word library; sky.json files each one in a
## cluster. Only what the player has met is here (D-073 rule 2): a region, cluster or
## constellation with no met word is left out, so the sky fills as they learn.
## `path` names what is being looked at: [region, cluster, constellation, word], indexes into
## these met-only lists. Positions are in book pixels of the open book (256x128).

const WORDS := preload("res://scripts/run/word_library.gd")
const FILE := "res://data/words/sky.json"
const STAGES := ["UNKNOWN", "ENCOUNTERED", "RECOGNIZED", "UNDERSTOOD", "USABLE"]
const PAGE := Rect2(32, 24, 80, 70) # where the picture goes on the left page (levels 2 to 4)
const SPREAD := Rect2(30, 16, 200, 86) # the whole sky: both pages
const WORD_PAGE := 5

static var _definition := {}

var regions: Array = [] # [{id, name, at, r, total, clusters: [{name, kind, total, constellations: [{id, kind, words: [{lemma, stage}]}]}]}]
## `kind`: the region a cluster or constellation belongs to; its ink wash takes that region's shape.


static func definition() -> Dictionary:
	if _definition.is_empty():
		var data = JSON.parse_string(FileAccess.get_file_as_string(FILE))
		_definition = data if data is Dictionary else {"regions": []}
	return _definition


## Constellations in the word library that no cluster in sky.json takes (they would never show).
static func unplaced() -> Array[String]:
	var placed := {}
	for r in definition().regions:
		for c in r.clusters:
			for id in c.constellations:
				placed[id] = true
	var missing: Array[String] = []
	for lemma in WORDS.lemmas():
		var id := constellation_of(lemma)
		if not placed.has(id) and id not in missing:
			missing.append(id)
	return missing


static func constellation_of(lemma: String) -> String:
	return str(WORDS.main_sense(lemma).get("constellation", WORDS.primary_tag(lemma)))


## `known`: lexicon_progress.known_words() ([{lemma, stage}], library order).
func build(known: Array) -> void:
	var by_constellation := {}
	for item in known:
		var id := constellation_of(str(item.lemma))
		if not by_constellation.has(id):
			by_constellation[id] = []
		by_constellation[id].append({"lemma": str(item.lemma), "stage": str(item.stage)})
	regions.clear()
	for r in definition().regions:
		var clusters := []
		for c in r.clusters:
			var constellations := []
			for id in c.constellations:
				if by_constellation.has(id):
					constellations.append({"id": str(id), "kind": str(r.id), "words": by_constellation[id]})
			if not constellations.is_empty():
				clusters.append({"name": str(c.name), "kind": str(r.id), "total": c.constellations.size(), "constellations": constellations})
		if not clusters.is_empty():
			regions.append({"id": str(r.id), "kind": str(r.id), "name": str(r.name), "at": Vector2(r.at[0], r.at[1]),
				"r": float(r.get("r", 8)), "total": r.clusters.size(), "clusters": clusters})


func total_regions() -> int:
	return definition().regions.size()


## What is looked at on `level`: the sky (an empty dictionary), a region, a cluster, a
## constellation or a word.
func node(level: int, path: Array) -> Dictionary:
	if level <= 1 or regions.is_empty():
		return {}
	var region: Dictionary = regions[clampi(path[0], 0, regions.size() - 1)]
	if level == 2:
		return region
	var cluster: Dictionary = region.clusters[clampi(path[1], 0, region.clusters.size() - 1)]
	if level == 3:
		return cluster
	var constellation: Dictionary = cluster.constellations[clampi(path[2], 0, cluster.constellations.size() - 1)]
	if level == 4:
		return constellation
	return constellation.words[clampi(path[3], 0, constellation.words.size() - 1)]


## The things shown on `level`, to choose from: regions, clusters, constellations or words.
func children(level: int, path: Array) -> Array:
	match level:
		1: return regions
		2: return node(2, path).get("clusters", [])
		3: return node(3, path).get("constellations", [])
		4: return node(4, path).get("words", [])
	return []


## How many siblings the thing on `level` has (what A / D turn through).
func siblings(level: int, path: Array) -> int:
	return children(level - 1, path).size() if level >= 2 else 1


## Every met word under a region, cluster or constellation (or the word itself).
static func words_in(item: Dictionary) -> Array:
	if item.has("lemma"):
		return [item]
	if item.has("words"):
		return item.words
	var result := []
	for child in item.get("clusters", item.get("constellations", [])):
		result.append_array(words_in(child))
	return result


## 0..1: how well the player knows what is under `item` (seen 0.25 ... usable 1).
static func light(item: Dictionary) -> float:
	var words := words_in(item)
	if words.is_empty():
		return 0.0
	var sum := 0.0
	for w in words:
		sum += STAGES.find(str(w.stage)) / 4.0
	return sum / words.size()


## How far a region, cluster or constellation's picture has been painted (round 2 of D-088):
## 0 just found (one faint layer), 1 some (the ink settles at the edge), 2 many (more of its stars,
## a few pen strokes), 3 every word in it usable (a thin cyan rim).
static func state(item: Dictionary) -> int:
	var words := words_in(item)
	var known := light(item)
	if words.size() >= 3 and known >= 1.0:
		return 3
	if words.size() >= 8 or (words.size() >= 4 and known >= 0.7):
		return 2
	if words.size() >= 3 or known >= 0.5:
		return 1
	return 0


## The constellation that stands for a region or cluster in its small picture: the best known.
static func brightest(item: Dictionary) -> Dictionary:
	if item.has("words"):
		return item
	var best := {}
	for child in item.get("clusters", item.get("constellations", [])):
		var b := brightest(child)
		if best.is_empty() or light(b) > light(best):
			best = b
	return best


## The path to a word, or [] if the player has not met it.
func find(lemma: String) -> Array:
	for r in regions.size():
		for c in regions[r].clusters.size():
			var cluster: Dictionary = regions[r].clusters[c]
			for k in cluster.constellations.size():
				var words: Array = cluster.constellations[k].words
				for w in words.size():
					if words[w].lemma == lemma:
						return [r, c, k, w]
	return []


## Where each thing on `level` sits on the left page.
func layout(level: int, path: Array) -> Array[Vector2]:
	var items := children(level, path)
	var points: Array[Vector2] = []
	if level == 1: # the whole sky spreads over both pages, each region where it was placed by hand
		for r in items:
			points.append(r.at)
	elif level == 4:
		points = figure(str(node(4, path).id), items.size(), PAGE.get_center(), 30.0)
	else:
		var cols := ceili(sqrt(items.size()))
		var rows := ceili(items.size() / float(maxi(cols, 1)))
		var cell := PAGE.size / Vector2(cols, maxi(rows, 1))
		for i in items.size():
			var rng := RandomNumberGenerator.new()
			rng.seed = hash(str(items[i].get("name", items[i].get("id", ""))))
			var at := PAGE.position + cell * (Vector2(i % cols, i / cols) + Vector2(0.5, 0.42))
			points.append((at + cell * Vector2(rng.randf_range(-0.12, 0.12), rng.randf_range(-0.1, 0.1))).round())
	return points


## A constellation's figure: `count` stars on a loose, curving line round `centre`, the same
## every time for the same name.
static func figure(name: String, count: int, centre: Vector2, reach: float) -> Array[Vector2]:
	var rng := RandomNumberGenerator.new()
	rng.seed = hash(name)
	var points: Array[Vector2] = []
	if count == 1:
		points.append(centre.round())
		return points
	var start := rng.randf() * TAU
	var sweep := TAU * lerpf(0.55, 0.85, rng.randf())
	for i in count:
		var a := start + sweep * i / float(count - 1)
		var r := reach * lerpf(0.6, 1.0, rng.randf())
		points.append((centre + Vector2(cos(a), sin(a) * 0.72) * r).round())
	return points
