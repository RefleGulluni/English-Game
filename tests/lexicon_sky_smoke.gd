extends SceneTree
## The Lexicon sky's data (D-088, scripts/prototypes/graveyard_room/lexicon_sky.gd): every
## constellation in the word library has a place in data/words/sky.json, only met words show,
## paths find words, and everything sits on the left page.

const SKY := preload("res://scripts/prototypes/graveyard_room/lexicon_sky.gd")

var failures: Array[String] = []


func check(value: bool, message: String) -> void:
	if not value: failures.append(message)


func _initialize() -> void:
	check(SKY.unplaced().is_empty(), "constellations without a place in sky.json: %s" % [SKY.unplaced()])
	var sky := SKY.new()
	sky.build([])
	check(sky.regions.is_empty(), "no words, no sky")
	sky.build([{"lemma": "shatter", "stage": "USABLE"}, {"lemma": "scatter", "stage": "RECOGNIZED"}, {"lemma": "decay", "stage": "ENCOUNTERED"}, {"lemma": "grave", "stage": "UNDERSTOOD"}])
	check(sky.regions.size() == 2, "two regions found (Breaking, Death): %d" % sky.regions.size())
	var path := sky.find("shatter")
	check(path.size() == 4 and sky.node(5, path).lemma == "shatter", "a path leads to its word")
	check(sky.find("bind").is_empty(), "an unmet word is not in the sky")
	check(sky.children(2, path).size() == 2, "Breaking shows the two clusters met in")
	for level in range(1, 5):
		for p in sky.layout(level, path):
			check((SKY.SPREAD if level == 1 else SKY.PAGE).grow(12).has_point(p), "level %d: %s is on its page" % [level, p])
	check(SKY.light(sky.node(5, path)) == 1.0 and SKY.light(sky.regions[1]) == 0.75, "light follows the stages")
	check(SKY.figure("BREAK", 5, Vector2(70, 60), 30) == SKY.figure("BREAK", 5, Vector2(70, 60), 30), "a figure is the same every time")
	# Recent / review (the quick ways in) read when each word last moved on.
	var progress = preload("res://scripts/run/lexicon_progress.gd").new()
	progress.save_path = ""
	progress.load_or_start()
	progress.set_stage("decay", "ENCOUNTERED")
	progress.set_stage("grave", "RECOGNIZED")
	check(progress.touched["grave"] > progress.touched["decay"] and progress.touched["decay"] > progress.touched["strike"], "touched counts up as words move on")
	progress.set_stage("grave", "ENCOUNTERED")
	check(progress.touched["grave"] == progress.clock, "a word never goes back, and that is not a move")
	progress.reset_to_start()
	check(not progress.touched.has("decay") and progress.touched.size() == 5, "a reset forgets when words moved")
	progress.remember("decay", "ENCOUNTERED", "", "In passing · Broken Graveyard")
	check(progress.meetings["decay"]["ENCOUNTERED"].where == "In passing · Broken Graveyard", "a word seen in passing keeps where")
	progress.remember("decay", "RECOGNIZED", "", "")
	check(not progress.meetings["decay"].has("RECOGNIZED"), "nothing is kept without a sentence or a place")
	var overlay := preload("res://scripts/prototypes/graveyard_room/lexicon_overlay.gd")
	for lemma in ["strike", "shatter", "observe", "bind", "anchor", "stabilize", "restore", "deflect", "toxic"]:
		check(not overlay.invocation(lemma).is_empty(), "%s says what it does in a fight" % lemma)
	check("8 structure" in overlay.invocation("shatter"), "shatter's invocation reads its effect: %s" % overlay.invocation("shatter"))
	if failures.is_empty():
		print("LEXICON_SKY_SMOKE: PASS")
	else:
		for f in failures: print("FAIL: ", f)
	quit(0 if failures.is_empty() else 1)
