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
const BACKDROP := 32.0 # closer in, the region's own shape fills the left page this large
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


## How large each thing is drawn on `level`: fewer things, larger (a single one fills the middle
## of the page, its stars showing); on the whole sky each region has its own size.
func radius(level: int, path: Array, i: int) -> float:
	var items := children(level, path)
	if level == 1:
		return items[i].r
	return clampf(26.0 / sqrt(maxf(1.0, items.size())), 7.0, 22.0)


## Where each thing on `level` sits. The whole sky: where each region was placed by hand. Closer
## in: inside the region's own shape, drawn large behind them (going in, you are inside that
## nebula), spread out but not in rows; the same every time. A constellation: its figure.
func layout(level: int, path: Array) -> Array[Vector2]:
	var items := children(level, path)
	var points: Array[Vector2] = []
	if level == 1: # the whole sky spreads over both pages, each region where it was placed by hand
		for r in items:
			points.append(r.at)
		return points
	if level == 4:
		return figure(str(node(4, path).id), items.size(), PAGE.get_center(), 30.0)
	var here := node(level, path)
	var rng := RandomNumberGenerator.new()
	rng.seed = hash(str(here.get("name", here.get("id", ""))))
	var centre := PAGE.get_center()
	var turn := float(hash(str(here.kind)) % 100000 % 1000) / 1000.0
	if items.size() == 1:
		points.append(centre.round())
		return points
	for i in items.size():
		var r := radius(level, path, i)
		var room := PAGE.grow(-r * 0.6)
		var best := room.get_center()
		var best_score := -1.0
		for tries in 80: # best of many: the place furthest from the others, inside the shape
			var p := Vector2(rng.randf_range(room.position.x, room.end.x), rng.randf_range(room.position.y, room.end.y))
			var v: float = shape(str(here.kind), (p.x - centre.x) / BACKDROP, (p.y - centre.y) / BACKDROP, turn)[0]
			var score := 99.0
			for q in points:
				score = minf(score, p.distance_to(q))
			score -= maxf(0.0, v - 0.85) * 40.0 # outside the shape counts against it
			if score > best_score:
				best_score = score
				best = p
		points.append(best.round())
	return points


## The most known stage among a thing's words.
static func best_stage(item: Dictionary) -> String:
	var best := 0
	for w in words_in(item):
		best = maxi(best, STAGES.find(str(w.stage)))
	return STAGES[best]


## `count` places scattered inside a wash of `kind` round `centre`: the stars inside a cluster.
static func scatter(name: String, count: int, centre: Vector2, r: float, kind: String) -> Array[Vector2]:
	var rng := RandomNumberGenerator.new()
	rng.seed = hash(name)
	var turn := float(hash(kind) % 100000 % 1000) / 1000.0
	var points: Array[Vector2] = []
	for i in count:
		var p := centre
		for tries in 30:
			p = centre + Vector2(rng.randf_range(-r, r), rng.randf_range(-r, r) * 0.8)
			var s: Array = shape(kind, (p.x - centre.x) / r, (p.y - centre.y) / r, turn)
			if s[0] < 0.75 and not s[2] and points.all(func(q): return q.distance_to(p) >= 2.5):
				break
		points.append(p.round())
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


static func segment_distance(p: Vector2, a: Vector2, b: Vector2) -> float:
	var t := clampf((p - a).dot(b - a) / maxf((b - a).length_squared(), 0.0001), 0.0, 1.0)
	return p.distance_to(a + (b - a) * t)


const TREE := [[Vector2(0, 0.9), Vector2(0, -0.1)], [Vector2(0, 0.2), Vector2(-0.6, -0.5)], [Vector2(0, 0.0), Vector2(0.55, -0.6)],
		[Vector2(-0.35, -0.3), Vector2(-0.5, -0.9)], [Vector2(0.3, -0.35), Vector2(0.75, -0.2)], [Vector2(0, -0.1), Vector2(0.05, -0.85)]]

## A region's shape, by what it means (round 2 of D-088): [v, density, hole] for a point (dx, dy)
## in units of the radius; v < 1 is inside, a hole stays bare paper.
static func shape(kind: String, dx: float, dy: float, salt: float) -> Array:
	var d := Vector2(dx, dy).length()
	var a := atan2(dy, dx)
	match kind:
		"breaking": # jagged, splintered edges (the cracks are drawn after)
			var tri := absf(fposmod(a * 7.0 / TAU + salt, 1.0) - 0.5) * 2.0
			return [d / (0.72 + 0.38 * tri), 1.0, false]
		"holding": # a ring, not quite closed: a hand closing
			return [9.0 if a > -2.0 and a < -1.15 else absf(d - 0.66) / 0.3, 1.0, false]
		"seeing": # a wide eye, its white kept bare, a dark pupil
			if Vector2(dx / 0.6, dy / 0.46).length() < 1.0:
				return [0.0, 0.0, true]
			return [Vector2(dx / 1.7, dy / 0.72).length(), 1.0, false]
		"death": # a drop: narrow above, heavy and wide below
			var width := 0.45 + 0.8 * clampf((dy + 1.0) / 1.6, 0.0, 1.0)
			return [Vector2(dx / width, (dy - 0.1) / 1.05).length(), pow(clampf(0.25 + 0.8 * (dy + 1.0) / 2.0, 0.2, 1.0), 1.5), false]
		"feeling": # the softest: no edge at all
			var v := Vector2(dx / 1.35, dy).length() * 0.95
			return [v, pow(maxf(0.0, 1.0 - v), 0.5) * 1.3, false]
		"sound": # rings going out
			return [d * 0.95, 1.0, sin(d * 9.5) < -0.1]
		"light": # a bare core, long rays
			if d < 0.28:
				return [0.0, 0.0, true]
			var ray := 1.0 if cos(7.0 * a + salt * TAU) > 0.7 else 0.0
			return [d / (0.55 + 0.6 * ray), 1.0, false]
		"nature": # branching like a tree
			var near := 9.0
			for s in TREE:
				near = minf(near, segment_distance(Vector2(dx, dy), s[0], s[1]))
			return [near / 0.2, 1.1, false]
		"places": # laid flat, like a piece of ground
			return [9.0 if dy > 0.32 else Vector2(dx / 1.9, dy / 0.55).length(), 1.0, false]
		"time": # two lobes and a narrow waist
			return [minf(minf(Vector2(dx / 0.8, (dy + 0.55) / 0.5).length(), Vector2(dx / 0.8, (dy - 0.55) / 0.5).length()), Vector2(dx / 0.25, dy / 0.6).length()), 1.0, false]
		"thinking": # a few small thoughts, touching
			var t := 9.0
			for c in [Vector2(-0.6, 0.2), Vector2(0.1, -0.4), Vector2(0.6, 0.3)]:
				t = minf(t, Vector2(dx, dy).distance_to(c) / 0.42)
			return [t, 1.0, false]
		"people": # several, side by side
			var p := 9.0
			for c in [Vector2(-0.75, 0), Vector2(-0.25, 0.15), Vector2(0.25, -0.05), Vector2(0.75, 0.1)]:
				p = minf(p, Vector2(dx, dy).distance_to(c) / 0.3)
			return [p, 1.0, false]
	return [Vector2(dx / 1.3, dy).length(), 1.0, false]
