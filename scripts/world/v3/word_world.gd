class_name WordWorld
extends CanvasLayer
## Words met in the world (D-078, docs/FIRST_WORD_ROUTE_SHATTER.md): the language the player
## walks past and answers to, outside fights.
##
## - Floating words: walking near a thing that carries a word shows it over the thing, drawn as far
##   as the player knows it (first letters and a crack → pencil → ink → cyan). Coming close the
##   first time is the word's first sighting (ambient evidence: UNKNOWN → ENCOUNTERED): the
##   letters write themselves in, lit, then cool to pencil. A word never seen glints faintly over
##   its thing from anywhere in the room, so the player has a reason to walk over (user
##   2026-10-29: a pale word that only shows up close went unnoticed).
## - Event box: an event room's script card (data/events/<biome>/<id>.json) in a framed box low
##   on the screen: a few lines, a question, numbered answers (keys 1-9 or the mouse), then the
##   scene's reply. Correct answers are evidence for the card's word.
## - Learning moments, lighter for early stages, heavier later (2026-10-30): a first sighting is a
##   glint at the hero's book and one faint line; RECOGNIZED and UNDERSTOOD slide a corner of a
##   page up from the bottom right, where the word is pencilled in (and, understood, gone over in
##   ink with its meaning), without stopping the player. Slips wait for the event box to close and
##   for a fight to end (`holding`). USABLE is the book's own ceremony (lexicon_overlay.ceremony).
## - Page slips (D-086): a page torn from the hero's book, with the sentence the word was met in
##   copied out; a pen tip writes (a pencil for RECOGNIZED: it underlines the word in the sentence,
##   then writes it; a dip pen for UNDERSTOOD: it goes over the pencil, then writes the meaning).
##   Done, the page folds and flies into the book at the hero's hip, which glints. The first few
##   are played in full, later RECOGNIZED ones only write the word (UNDERSTOOD stays in full).
##   Several at once come up as a pile and peel off one by one, each played, a little faster.
##
## Lives at window resolution above the world (text stays sharp), in native 960x540 units.

signal advanced(lemma: String, stage: String)

const FONT := preload("res://art/ui/fonts/CormorantGaramond.ttf")
const CYAN := Color(0.42, 0.86, 0.95)
const INK := Color8(222, 206, 176)
const DIM := Color8(150, 136, 116)
const PENCIL := Color8(176, 166, 152)
const PANEL := Color(0.055, 0.045, 0.035, 0.94)
const EDGE := Color8(150, 128, 92, 150)
const SEE := 120.0 # native pixels: the floating word starts to show
const MEET := 80.0 # and counts as seen
const WRITE_IN := 0.9 # seconds for a first-seen word to write itself in and cool
const BOX_W := 520.0
const NATIVE := Vector2(960, 540)
const WORDS := preload("res://scripts/run/word_library.gd")
const ERASED := preload("res://scripts/world/v3/word_erased.gdshader")
const SLIP_PAPER := Color8(205, 189, 172) # the book's paper and writing (lexicon_overlay)
const SLIP_PENCIL := Color8(128, 116, 104)
const SLIP_INK := Color8(44, 31, 24)
const SLIP_WIDTH := 250.0
const SLIP_SLIDE := 0.35 # seconds the pile takes to come up, and to go back down
const SLIP_FLY := 0.5 # seconds a page takes to fold and fly into the book
const SLIP_FULL := 5 # page slips played in full before RECOGNIZED ones only write the word
const SLIP_PILE_SPEED := 1.5 # a pile plays each page this much faster
const SLIP_READ := 2.5 # seconds a page stays once written, to be read (user: it went too fast)
const SLIP_READ_SHORT := 1.2 # a page with the word only
const QUILL := Color8(206, 110, 76) # the quill's outline (user 2026-10-30: like Claude's feather)
const QUILL_FILL := Color8(232, 214, 196)
const PENCIL_LEAD := Color8(80, 74, 70)

var progress # lexicon_progress.gd
var hero: Node2D
var _floats: Array[Dictionary] = [] # {lemma, at (where it hangs), near (where to stand), alpha, control}
var _note: Control
var _note_text := ""
var _note_color := CYAN
var _note_t := 99.0
## Where the note line sits: low in the room while exploring (the top is where tall things and
## their words are), high during a fight (the bottom belongs to the word bar).
var note_y := 400.0
var holding := false # in a fight: page slips wait until it is over
var place := "" # the area the hero is in: where a word was first seen (the book's "how you learned it")
var _slips: Array[Dictionary] = [] # {lemma, stage} waiting their turn
var _slip := {} # the page on show, laid out (_lay_out)
var _slip_t := 0.0
var _pile_up := 0.0 # 0..1: the pile at the bottom right, down or up
var _slip_c: Control
var _book_t := 99.0 # seconds since the hero's book last glinted (a first sighting)
var _clock := 0.0
var _box: PanelContainer
var _box_rows: VBoxContainer
var _answers: Array = [] # the options on show: {text, label, reply, correct}
var _reply_open := false
var _result := {}
var _on_done: Callable


func _init() -> void:
	layer = 6


func _ready() -> void:
	_note = Control.new()
	_note.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_note.size = NATIVE
	_note.draw.connect(_draw_note)
	add_child(_note)
	_slip_c = Control.new()
	_slip_c.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_slip_c.size = NATIVE
	_slip_c.draw.connect(_draw_slip)
	add_child(_slip_c)
	_box = PanelContainer.new()
	var style := StyleBoxFlat.new()
	style.draw_center = false
	style.set_content_margin_all(16)
	style.content_margin_top = 13
	_box.add_theme_stylebox_override("panel", style)
	_box.draw.connect(_draw_box)
	_box_rows = VBoxContainer.new()
	_box_rows.add_theme_constant_override("separation", 5)
	_box.add_child(_box_rows)
	_box.hide()
	add_child(_box)


# --- Floating words ------------------------------------------------------------------------

## words: [{lemma, at, near}] for the room just entered (positions in the room, native pixels).
func set_room_words(words: Array) -> void:
	for f in _floats:
		f.control.queue_free()
	_floats.clear()
	for w in words:
		var c := Control.new()
		c.mouse_filter = Control.MOUSE_FILTER_IGNORE
		c.size = Vector2(160, 28)
		var erased := ShaderMaterial.new() # ENCOUNTERED: the letters after the first few half rubbed out
		erased.shader = ERASED
		erased.set_shader_parameter("seed", float(hash(str(w.lemma)) % 997))
		c.material = erased
		var f := {"lemma": str(w.lemma), "at": w.at, "near": w.get("near", w.at), "alpha": 0.0, "control": c, "born": -99.0}
		c.draw.connect(_draw_float.bind(f))
		add_child(c)
		move_child(c, 0)
		_floats.append(f)


## A thing that carried a word is gone (the slab shattered): its word goes with it.
func remove_near(at: Vector2, radius := 60.0) -> void:
	for f in _floats.duplicate():
		if Vector2(f.near).distance_to(at) <= radius:
			f.control.queue_free()
			_floats.erase(f)


func _process(delta: float) -> void:
	_clock += delta
	_note_t += delta
	_book_t += delta
	_note.queue_redraw()
	if _slip.is_empty() and not _slips.is_empty() and not holding and not _box.visible:
		_start_slip(_slips.pop_front())
	elif not _slip.is_empty():
		_slip_t += delta
		if _slip_t >= _slip.lead + _slip.end / _slip.speed:
			_slip = {}
			_book_t = 0.0 # it has gone into the book
	_pile_up = move_toward(_pile_up, 1.0 if not _slip.is_empty() else 0.0, delta / SLIP_SLIDE)
	_slip_c.queue_redraw()
	for f in _floats:
		var near := is_instance_valid(hero) and hero.visible and _box.visible == false
		var d: float = hero.global_position.distance_to(f.near) if near else 9999.0
		if d <= MEET and progress.stage(f.lemma) == "UNKNOWN":
			f.born = _clock
			_moved(f.lemma, progress.advance(f.lemma, "ambient"), "", "In passing · " + place if place else "")
		# Never seen: the glint, from anywhere in the room. Known: the word, once close enough.
		var target := 1.0 if near else 0.0
		if progress.stage(f.lemma) != "UNKNOWN":
			target = clampf((SEE - d) / (SEE - MEET), 0.0, 1.0)
		f.alpha = move_toward(f.alpha, target, delta * 2.5)
		var c: Control = f.control
		c.position = (Vector2(f.at) + Vector2(-80, -14)).round()
		c.visible = f.alpha > 0.0
		c.queue_redraw()


func _draw_float(f: Dictionary) -> void:
	var c: Control = f.control
	var a: float = f.alpha
	var word := str(f.lemma).to_upper()
	var stage: String = progress.stage(f.lemma)
	# The rubbing out is only for a word seen once; a word unknown again (dev reset) must not keep
	# it, or the glint loses its right half (user 2026-10-30).
	(c.material as ShaderMaterial).set_shader_parameter("strength", 1.0 if stage == "ENCOUNTERED" else 0.0)
	if stage == "UNKNOWN":
		draw_glint(c, Vector2(79, 13), a, _clock)
		return
	var since: float = _clock - float(f.born)
	var writing := clampf(since / (WRITE_IN * 0.6), 0.0, 1.0) # letters appear one by one
	var cooling := clampf((since - WRITE_IN * 0.5) / (WRITE_IN * 0.5), 0.0, 1.0) # then cool from lit to pencil
	var size := 17
	var shown := word
	var color := CYAN
	match stage:
		"ENCOUNTERED": # the whole word, its strokes thinning out after the first letters: seen, not yet read
			color = Color(PENCIL, 0.9)
		"RECOGNIZED":
			color = PENCIL
		"UNDERSTOOD":
			color = INK
	var w := FONT.get_string_size(shown, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x
	var at := Vector2(roundf(80 - w / 2.0), 16)
	var erased := c.material as ShaderMaterial
	erased.set_shader_parameter("erase_from", at.x + FONT.get_string_size(word.left(3), HORIZONTAL_ALIGNMENT_LEFT, -1, size).x)
	erased.set_shader_parameter("erase_to", at.x + w)
	if since < WRITE_IN: # just seen: lit like language, written in as you watch
		shown = shown.left(ceili(writing * shown.length()))
		color = Color(CYAN.lerp(color, cooling), lerpf(1.0, color.a, cooling))
		c.draw_string_outline(FONT, at, shown, HORIZONTAL_ALIGNMENT_LEFT, -1, size, 8, Color(CYAN, 0.18 * a * (1.0 - cooling)))
	# a soft dark edge so a pale word still reads on pale stone
	c.draw_string_outline(FONT, at, shown, HORIZONTAL_ALIGNMENT_LEFT, -1, size, 4, Color(0.03, 0.03, 0.05, 0.55 * a))
	if stage == "USABLE": # language: a steady glow
		c.draw_string_outline(FONT, at, shown, HORIZONTAL_ALIGNMENT_LEFT, -1, size, 8, Color(CYAN, 0.12 * a))
	c.draw_string(FONT, at, shown, HORIZONTAL_ALIGNMENT_LEFT, -1, size, Color(color, color.a * a))
	# a hairline down to the thing it belongs to
	c.draw_line(Vector2(80, 21), Vector2(80, 26), Color(color, 0.35 * a), 1.0)


## The glint (user's favourite, 2026-10-29): a four-pointed star breathing, flaring every few
## seconds. Marks a word never seen, and a thing that can be looked into (event_spot).
static func draw_glint(c: CanvasItem, mid: Vector2, a: float, clock: float) -> void:
	var breath := 0.6 + 0.4 * sin(clock * 2.2)
	var flare := clampf(1.0 - fmod(clock, 3.2) / 0.5, 0.0, 1.0) # a quick flare, then 2.7 s of calm
	var px := 2.0 # one glint pixel: two world pixels, so it reads from across the room
	var reach := 3 + int(round(3.0 * flare))
	for r in range(16, 0, -2): # soft halo
		c.draw_circle(mid + Vector2(px, px) / 2.0, r, Color(CYAN, 0.03 * a * (breath + flare)))
	for i in range(1, reach + 1): # the four arms, fading out along their length
		var arm_a := a * (breath * 0.8 + flare * 0.6) * (1.0 - float(i - 1) / reach)
		for dir in [Vector2.UP, Vector2.DOWN, Vector2.LEFT, Vector2.RIGHT]:
			c.draw_rect(Rect2(mid + dir * i * px, Vector2(px, px)), Color(CYAN, clampf(arm_a, 0.0, 1.0)))
	c.draw_rect(Rect2(mid, Vector2(px, px)), Color(Color.WHITE.lerp(CYAN, 0.3), a))


# --- Notes -----------------------------------------------------------------------------------

func _moved(lemma: String, stage: String, line := "", where := "") -> void:
	if stage.is_empty():
		return
	progress.remember(lemma, stage, line, where)
	var word := lemma.to_upper()
	match stage:
		"ENCOUNTERED":
			note("A NEW WORD  ·  %s…" % word.left(3).to_lower(), PENCIL)
			_book_t = 0.0
		"RECOGNIZED", "UNDERSTOOD": _slips.append({"lemma": lemma, "stage": stage})
		"USABLE": note("%s  ·  USABLE  ·  it is yours now" % word, CYAN)
	advanced.emit(lemma, stage)


## Evidence from outside this layer (a fight, an event); same notes, same rules. `line` is the
## sentence it happened in, the word in [brackets]; `where`, a few words on the place (D-086).
func evidence(lemma: String, kind: String, encounter: String, line := "", where := "") -> String:
	var stage: String = progress.advance(lemma, kind, encounter)
	_moved(lemma, stage, line, where)
	return stage


func note(text: String, color := CYAN) -> void:
	_note_text = text
	_note_color = color
	_note_t = 0.0


func _draw_note() -> void:
	if _book_t < 0.8 and is_instance_valid(hero) and hero.visible: # the book at the hero's hip glints once
		var k := 1.0 - _book_t / 0.8
		var at := (hero.global_position + Vector2(9, -40)).round()
		for i in range(1, 2 + roundi(3.0 * k)):
			for dir in [Vector2.UP, Vector2.DOWN, Vector2.LEFT, Vector2.RIGHT]:
				_note.draw_rect(Rect2(at + dir * i, Vector2.ONE), Color(CYAN, k * (1.0 - float(i - 1) / 4.0)))
		_note.draw_rect(Rect2(at, Vector2.ONE), Color(Color.WHITE, k))
	if _note_text.is_empty() or _note_t > 4.0:
		return
	var a := clampf(_note_t / 0.4, 0.0, 1.0) * clampf((4.0 - _note_t) / 0.8, 0.0, 1.0)
	var size := 16
	var w := FONT.get_string_size(_note_text, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x
	var at := Vector2(roundf((NATIVE.x - w) / 2.0), note_y - 4.0 * (1.0 - a))
	# a soft dark band behind, so a pencil-grey line still reads over pale ground
	_note.draw_rect(Rect2(Vector2(at.x - 18, at.y - 17), Vector2(w + 36, 30)), Color(0.02, 0.02, 0.03, 0.5 * a))
	_note.draw_string_outline(FONT, at, _note_text, HORIZONTAL_ALIGNMENT_LEFT, -1, size, 8, Color(_note_color, 0.08 * a))
	_note.draw_string_outline(FONT, at, _note_text, HORIZONTAL_ALIGNMENT_LEFT, -1, size, 3, Color(0, 0, 0, 0.5 * a))
	_note.draw_string(FONT, at, _note_text, HORIZONTAL_ALIGNMENT_LEFT, -1, size, Color(_note_color, a))
	var mid := NATIVE.x / 2.0
	for side in [-1.0, 1.0]: # a short rule either side of a node, under the line
		_note.draw_line(Vector2(mid + side * 6, at.y + 8), Vector2(mid + side * minf(w / 2.0, 90.0), at.y + 8), Color(_note_color, 0.35 * a), 1.0)
	_note.draw_rect(Rect2(Vector2(mid - 1, at.y + 7), Vector2(3, 3)), Color(_note_color, a))


# --- Page slips (RECOGNIZED, UNDERSTOOD) ------------------------------------------------------

const SLIP_SENTENCE := 12 # font sizes on the page
const SLIP_WHERE := 10
const SLIP_WORD := 24
const SLIP_MEANING := 12


## Dev and capture: puts a page in the queue as if the word had just moved.
func show_slip(lemma: String, stage: String) -> void:
	_slips.append({"lemma": lemma, "stage": stage})


func _start_slip(entry: Dictionary) -> void:
	var lemma := str(entry.lemma)
	var understood: bool = entry.stage == "UNDERSTOOD"
	var met: Dictionary = progress.met_at(lemma, str(entry.stage))
	var full: bool = not met.is_empty() and (understood or progress.slips_seen < SLIP_FULL)
	progress.slips_seen += 1
	progress.save()
	_slip = _lay_out(lemma, understood, str(met.get("line", "")) if full else "", str(met.get("where", "")))
	var pile_up := _pile_up >= 0.5 # the page before has just gone: this one was under it
	_slip.lead = 0.15 if pile_up else SLIP_SLIDE
	_slip.speed = SLIP_PILE_SPEED if pile_up or not _slips.is_empty() else 1.0
	_slip_t = 0.0


## Where everything on the page goes, and when it is written (seconds, before `speed`).
func _lay_out(lemma: String, understood: bool, line: String, where: String) -> Dictionary:
	var inner := SLIP_WIDTH - 28.0
	var page := {"lemma": lemma, "understood": understood, "sentence": [], "mark": {}, "meaning": []}
	var y := 10.0 # below the torn edge
	if not line.is_empty():
		var start_mark := line.find("[")
		var end_mark := line.find("]") - 1 # in the sentence without its brackets
		var plain := line.replace("[", "").replace("]", "")
		var rows := [] # [text, index of its first letter]
		var row := ""
		var row_start := 0
		var index := 0
		for word in plain.split(" "):
			var trial: String = word if row.is_empty() else row + " " + word
			if not row.is_empty() and FONT.get_string_size(trial, HORIZONTAL_ALIGNMENT_LEFT, -1, SLIP_SENTENCE).x > inner:
				rows.append([row, row_start])
				row = word
				row_start = index
			else:
				row = trial
			index += word.length() + 1
		rows.append([row, row_start])
		for r in rows:
			y += 15.0
			page.sentence.append({"text": r[0], "y": y})
			var from: int = start_mark - r[1]
			if start_mark >= 0 and from >= 0 and from < str(r[0]).length():
				page.mark = {"x0": _width(str(r[0]).left(from), SLIP_SENTENCE),
					"x1": _width(str(r[0]).left(end_mark - r[1]), SLIP_SENTENCE), "y": y + 3.0}
		y += 13.0
		page.where = {"text": "— " + where, "y": y}
		y += 30.0
	else:
		y += 24.0
	page.word_y = y
	page.word_w = _width(lemma, SLIP_WORD)
	if understood:
		var meaning := str(WORDS.sense(lemma))
		var row := ""
		for word in meaning.split(" "):
			var trial: String = word if row.is_empty() else row + " " + word
			if not row.is_empty() and _width(trial, SLIP_MEANING) > inner:
				y += 15.0
				page.meaning.append({"text": row, "y": y})
				row = word
			else:
				row = trial
		y += 15.0
		page.meaning.append({"text": row, "y": y})
	page.size = Vector2(SLIP_WIDTH, y + 12.0)
	# When: the sentence comes, the pen underlines the word in it, then writes the word (in ink
	# over the pencil, if understood), then the meaning; it lifts, the page waits, then flies.
	var t := 0.0
	if not line.is_empty():
		page.under = [0.35, 0.65 if understood else 0.75]
		t = page.under[1] + 0.05
	page.write = [t + 0.05, t + 0.65]
	t = page.write[1]
	if understood:
		var letters := 0
		for r in page.meaning:
			letters += str(r.text).length()
		page.mean = [t + 0.1, t + 0.1 + letters / 60.0]
		t = page.mean[1]
	page.fly = t + (SLIP_READ + (0.5 if understood else 0.0) if not line.is_empty() or understood else SLIP_READ_SHORT)
	page.end = page.fly + SLIP_FLY
	# The torn top edge: ragged in whole pixels, the same for the same word.
	var rng := RandomNumberGenerator.new()
	rng.seed = hash(lemma)
	var edge := PackedVector2Array()
	var x := 0.0
	while x < SLIP_WIDTH:
		edge.append(Vector2(x, rng.randi_range(0, 3)))
		x += rng.randi_range(4, 8)
	edge.append(Vector2(SLIP_WIDTH, rng.randi_range(0, 3)))
	page.edge = edge
	return page


func _width(text: String, size: int) -> float:
	return FONT.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x


func _draw_slip() -> void:
	if _slip.is_empty():
		return
	var c := _slip_c
	var size: Vector2 = _slip.size
	var rest := Vector2(NATIVE.x - SLIP_WIDTH - 24, NATIVE.y - size.y - 18)
	var at := (rest + Vector2(0, (1.0 - ease(_pile_up, 0.4)) * (size.y + 30))).round()
	for k in range(mini(_slips.size(), 2), 0, -1): # the rest of the pile, under this page
		c.draw_set_transform(at + Vector2(3 * k, -4 * k))
		_draw_paper(c, Vector2.ZERO, size, 1.0, SLIP_PAPER.darkened(0.08 * k))
	c.draw_set_transform(Vector2.ZERO)
	if not _slips.is_empty():
		var more := "%d more page%s" % [_slips.size(), "" if _slips.size() == 1 else "s"]
		var spot := at + Vector2(SLIP_WIDTH - _width(more, 11), -8 - 4 * mini(_slips.size(), 2))
		c.draw_string_outline(FONT, spot, more, HORIZONTAL_ALIGNMENT_LEFT, -1, 11, 3, Color(0, 0, 0, 0.5))
		c.draw_string(FONT, spot, more, HORIZONTAL_ALIGNMENT_LEFT, -1, 11, PENCIL)
	var u: float = maxf(_slip_t - _slip.lead, 0.0) * _slip.speed
	var f: float = clampf((u - _slip.fly) / SLIP_FLY, 0.0, 1.0)
	if f <= 0.0:
		c.draw_set_transform(at)
		_draw_page(c, u, Vector2.ZERO, 1.0)
	else: # folds in half the long way, then flies on an arc into the book at the hero's hip
		var pivot := size / 2.0
		var from := at + pivot
		var to := Vector2(at.x, NATIVE.y + 40)
		if is_instance_valid(hero) and hero.visible:
			to = hero.global_position + Vector2(9, -40)
		var bend := (from + to) / 2.0 + Vector2(0, -90)
		var e := ease(f, -1.8)
		var p := from.lerp(bend, e).lerp(bend.lerp(to, e), e)
		var fold := Vector2(lerpf(1.0, 0.05, ease(f, 0.7)), lerpf(1.0, 0.1, clampf(f * 2.0, 0.0, 1.0)))
		c.draw_set_transform(p, -0.35 * e, fold)
		_draw_page(c, u, -pivot, 1.0 - clampf((f - 0.8) / 0.2, 0.0, 1.0))
	c.draw_set_transform(Vector2.ZERO)


func _draw_paper(c: Control, o: Vector2, size: Vector2, a: float, paper := SLIP_PAPER) -> void:
	var outline := PackedVector2Array()
	for point in _slip.edge:
		outline.append(o + point)
	outline.append(o + size)
	outline.append(o + Vector2(0, size.y))
	var shadow := PackedVector2Array()
	for point in outline:
		shadow.append(point + Vector2(3, 3))
	c.draw_colored_polygon(shadow, Color(0, 0, 0, 0.35 * a))
	c.draw_colored_polygon(outline, Color(paper, a))
	var torn := outline.slice(0, _slip.edge.size())
	c.draw_polyline(torn, Color(paper.lightened(0.25), a), 1.0) # torn fibres catch the light
	c.draw_polyline(PackedVector2Array([o + Vector2(size.x, _slip.edge[-1].y), o + size, o + Vector2(0, size.y), o + Vector2(0, _slip.edge[0].y)]),
		Color(paper.darkened(0.3), a), 1.0)


func _draw_page(c: Control, u: float, o: Vector2, a: float) -> void:
	var page := _slip
	_draw_paper(c, o, page.size, a)
	var left := o.x + 14.0
	var ink := Color(SLIP_INK, 0.9 * a)
	var pencil := Color(SLIP_PENCIL, 0.9 * a)
	var shown := clampf(u / 0.3, 0.0, 1.0)
	for row in page.sentence:
		c.draw_string(FONT, Vector2(left, o.y + row.y), row.text, HORIZONTAL_ALIGNMENT_LEFT, -1, SLIP_SENTENCE, Color(pencil, pencil.a * shown))
	if page.has("where"):
		c.draw_string(FONT, Vector2(left, o.y + page.where.y), page.where.text, HORIZONTAL_ALIGNMENT_LEFT, -1, SLIP_WHERE, Color(pencil, 0.7 * a * shown))
	var tips := [] # [start, end, from, to]: where the pen goes, and when
	if not page.mark.is_empty():
		var y: float = o.y + page.mark.y
		var x0: float = left + page.mark.x0
		var x1: float = left + page.mark.x1
		var p := _progress(u, page.under)
		if page.understood: # pencil underneath, ink drawn over it
			c.draw_line(Vector2(x0, y), Vector2(x1, y), pencil, 1.0)
			if p > 0.0:
				c.draw_line(Vector2(x0, y), Vector2(lerpf(x0, x1, p), y), ink, 1.0)
		elif p > 0.0:
			c.draw_line(Vector2(x0, y), Vector2(lerpf(x0, x1, p), y), pencil, 1.0)
		tips.append([page.under[0], page.under[1], Vector2(x0, y), Vector2(x1, y)])
	var word := str(page.lemma)
	var w := _progress(u, page.write)
	var x := left
	for i in word.length():
		var letter := word[i]
		if page.understood:
			c.draw_string(FONT, Vector2(x, o.y + page.word_y), letter, HORIZONTAL_ALIGNMENT_LEFT, -1, SLIP_WORD, pencil.lerp(ink, clampf(w * word.length() - i, 0.0, 1.0)))
		elif i < ceili(w * word.length()):
			c.draw_string(FONT, Vector2(x, o.y + page.word_y), letter, HORIZONTAL_ALIGNMENT_LEFT, -1, SLIP_WORD, pencil)
		x += _width(letter, SLIP_WORD)
	tips.append([page.write[0], page.write[1], Vector2(left, o.y + page.word_y - 5), Vector2(left + page.word_w, o.y + page.word_y - 5)])
	if page.understood:
		var letters := ceili(_progress(u, page.mean) * _meaning_letters(page))
		for row in page.meaning:
			var text := str(row.text).left(letters)
			letters -= str(row.text).length()
			if not text.is_empty():
				c.draw_string(FONT, Vector2(left, o.y + row.y), text, HORIZONTAL_ALIGNMENT_LEFT, -1, SLIP_MEANING, ink)
			tips.append([0.0, 0.0, Vector2(left, o.y + row.y - 4), Vector2(left + _width(row.text, SLIP_MEANING), o.y + row.y - 4)])
		_split_meaning_tips(tips, page)
	_draw_pen_on(c, u, tips, page.understood, a)


func _meaning_letters(page: Dictionary) -> int:
	var n := 0
	for row in page.meaning:
		n += str(row.text).length()
	return n


## The meaning's rows share its time, by how many letters each has.
func _split_meaning_tips(tips: Array, page: Dictionary) -> void:
	var total := float(maxi(_meaning_letters(page), 1))
	var t: float = page.mean[0]
	var rows: int = page.meaning.size()
	for i in rows:
		var tip: Array = tips[tips.size() - rows + i]
		var span: float = (page.mean[1] - page.mean[0]) * str(page.meaning[i].text).length() / total
		tip[0] = t
		tip[1] = t + span
		t += span


func _progress(u: float, span) -> float:
	if span == null:
		return 0.0
	return clampf((u - span[0]) / maxf(span[1] - span[0], 0.01), 0.0, 1.0)


## The pen tip follows the writing: it comes down just before, moves along while it writes, and
## lifts away after the last stroke.
func _draw_pen_on(c: Control, u: float, tips: Array, dip_pen: bool, a: float) -> void:
	if tips.is_empty():
		return
	var first: float = tips[0][0]
	var last: float = tips[-1][1]
	var down := clampf((u - first + 0.25) / 0.15, 0.0, 1.0)
	var lift := clampf((u - last) / 0.3, 0.0, 1.0)
	if down <= 0.0 or lift >= 1.0:
		return
	var tip: Vector2 = tips[0][2]
	for t in tips:
		if u >= t[0] - 0.05:
			tip = Vector2(t[2]).lerp(t[3], clampf((u - t[0]) / maxf(t[1] - t[0], 0.01), 0.0, 1.0))
			if u <= t[1]:
				tip.y += roundf(sin(u * 38.0)) # the small up-and-down of a hand writing
	tip += Vector2(4, -10) * (1.0 - down) + Vector2(5, -12) * lift
	_draw_pen(c, tip.round(), dip_pen, a * down * (1.0 - lift))


## A quill: an outlined feather (after Claude's own, user 2026-10-30), the vane wide on one side
## of the shaft; its nib leaves pencil grey for RECOGNIZED, ink for UNDERSTOOD.
func _draw_pen(c: Control, tip: Vector2, dip_pen: bool, a: float) -> void:
	var d := Vector2(0.5, -1.0).normalized()
	var n := Vector2(-d.y, d.x)
	var outer := PackedVector2Array() # one side of the vane up, the other side back down
	var inner := PackedVector2Array()
	for i in 9:
		var k := i / 8.0
		var along := d * lerpf(9.0, 32.0, k)
		var swell := sin(PI * pow(k, 0.7))
		outer.append(tip + along + n * 6.0 * swell)
		inner.append(tip + along - n * 2.5 * swell)
	inner.reverse()
	var vane := outer + inner
	var shadow := PackedVector2Array()
	for point in vane:
		shadow.append(point + Vector2(2, 2))
	c.draw_colored_polygon(shadow, Color(0, 0, 0, 0.2 * a))
	c.draw_colored_polygon(vane, Color(QUILL_FILL, a))
	vane.append(vane[0])
	c.draw_polyline(vane, Color(QUILL, a), 1.0)
	c.draw_line(tip + d * 3, tip + d * 30, Color(QUILL, a), 1.0) # the shaft
	for k in [0.45, 0.7]: # two splits in the vane, as on a real feather
		var at := tip + d * lerpf(9.0, 32.0, k)
		c.draw_line(at + n * 6.0 * sin(PI * pow(k, 0.7)), at + n * 2.0 + d * -2.0, Color(QUILL, a), 1.0)
	c.draw_line(tip, tip + d * 3, Color(SLIP_INK if dip_pen else PENCIL_LEAD, a), 1.5) # the nib


# --- Event box -------------------------------------------------------------------------------

func is_busy() -> bool:
	return _box.visible


## Shows a script card. options: [{text, label?, reply, correct}] (label: a word drawn in cyan).
## done(result) gets {"index", "correct"} once the reply has been read.
func open_event(card: Dictionary, options: Array, done: Callable) -> void:
	_answers = options
	_on_done = done
	_reply_open = false
	_result = {}
	_clear_rows()
	_add_label(str(card.get("title", "")), 12, DIM)
	for line in card.get("text", []):
		_add_rich(str(line))
	_add_spacer(4)
	_add_label(str(card.get("question", "")), 14, INK)
	for i in options.size():
		_box_rows.add_child(_option_row(i, options[i]))
	_show_box()


func _show_box() -> void:
	_box.reset_size()
	_box.custom_minimum_size = Vector2(BOX_W, 0)
	_box.modulate.a = 0.0
	_box.show()
	await get_tree().process_frame
	var size := _box.get_combined_minimum_size()
	_box.size = size
	_box.position = Vector2(roundf((NATIVE.x - size.x) / 2.0), roundf(NATIVE.y - size.y - 28))
	create_tween().tween_property(_box, "modulate:a", 1.0, 0.2)
	_box.queue_redraw()


func _choose(i: int) -> void:
	if _reply_open or i < 0 or i >= _answers.size():
		return
	var option: Dictionary = _answers[i]
	_result = {"index": i, "correct": bool(option.get("correct", false))}
	_reply_open = true
	_clear_rows()
	_add_label(str(option.get("label", "")) if option.has("label") else str(option.get("text", "")), 14, CYAN if option.has("label") else DIM)
	_add_rich(str(option.get("reply", "")))
	_add_spacer(2)
	_add_label("E  ·  continue", 11, DIM)
	_show_box()


func _close() -> void:
	_box.hide()
	_clear_rows()
	var done := _on_done
	_on_done = Callable()
	if done.is_valid():
		done.call(_result)


func _unhandled_key_input(event: InputEvent) -> void:
	if not _box.visible or not event.is_pressed() or event.is_echo():
		return
	var key: Key = event.physical_keycode
	if _reply_open and key in [KEY_E, KEY_SPACE, KEY_ENTER, KEY_ESCAPE]:
		_close()
	elif not _reply_open and key >= KEY_1 and key <= KEY_9:
		_choose(key - KEY_1)
	elif not _reply_open and key == KEY_ESCAPE: # walk away: nothing chosen, nothing lost
		_result = {}
		_close()
	get_viewport().set_input_as_handled()


func _clear_rows() -> void:
	for child in _box_rows.get_children():
		_box_rows.remove_child(child)
		child.queue_free()


func _add_label(text: String, size: int, color: Color) -> void:
	var label := Label.new()
	label.text = text
	label.add_theme_font_override("font", FONT)
	label.add_theme_font_size_override("font_size", size)
	label.add_theme_color_override("font_color", color)
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.custom_minimum_size.x = BOX_W - 32
	_box_rows.add_child(label)


## A line of the scene; [word] marks the word in question, drawn in the language colour.
func _add_rich(text: String) -> void:
	var rich := RichTextLabel.new()
	rich.bbcode_enabled = true
	rich.fit_content = true
	rich.scroll_active = false
	rich.mouse_filter = Control.MOUSE_FILTER_IGNORE
	rich.custom_minimum_size.x = BOX_W - 32
	rich.add_theme_font_override("normal_font", FONT)
	rich.add_theme_font_size_override("normal_font_size", 15)
	rich.add_theme_color_override("default_color", INK)
	var marked := RegEx.create_from_string("\\[([^\\]]+)\\]")
	rich.text = marked.sub(text, "[color=#%s]$1[/color]" % CYAN.to_html(false), true)
	_box_rows.add_child(rich)


func _add_spacer(h: float) -> void:
	var gap := Control.new()
	gap.custom_minimum_size.y = h
	_box_rows.add_child(gap)


func _option_row(i: int, option: Dictionary) -> Control:
	var row := Control.new()
	row.custom_minimum_size = Vector2(BOX_W - 32, 22)
	row.mouse_filter = Control.MOUSE_FILTER_STOP
	row.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	row.set_meta("hover", false)
	row.mouse_entered.connect(func(): row.set_meta("hover", true); row.queue_redraw())
	row.mouse_exited.connect(func(): row.set_meta("hover", false); row.queue_redraw())
	row.gui_input.connect(func(event: InputEvent):
		if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
			_choose(i))
	row.draw.connect(func():
		var hover := bool(row.get_meta("hover"))
		if hover:
			row.draw_rect(Rect2(Vector2(0, 1), row.size - Vector2(0, 2)), Color(EDGE, 0.12))
		row.draw_string(FONT, Vector2(6, 16), str(i + 1), HORIZONTAL_ALIGNMENT_LEFT, -1, 13, DIM)
		if option.has("label") and bool(option.get("understood", false)): # understood, not yet in hand: ink
			row.draw_string(FONT, Vector2(26, 16), str(option.label), HORIZONTAL_ALIGNMENT_LEFT, -1, 15, INK if hover else Color(INK, 0.85))
		elif option.has("label"): # one of the player's words: language colour
			row.draw_string_outline(FONT, Vector2(26, 16), str(option.label), HORIZONTAL_ALIGNMENT_LEFT, -1, 15, 5, Color(CYAN, 0.1))
			row.draw_string(FONT, Vector2(26, 16), str(option.label), HORIZONTAL_ALIGNMENT_LEFT, -1, 15, Color(CYAN, 1.0 if hover else 0.85))
		else:
			row.draw_string(FONT, Vector2(26, 16), str(option.text), HORIZONTAL_ALIGNMENT_LEFT, BOX_W - 60, 14, INK if hover else Color(INK, 0.82)))
	return row


func _draw_box() -> void:
	var r := Rect2(Vector2.ZERO, _box.size)
	_box.draw_rect(r, PANEL)
	_box.draw_rect(r.grow(-0.5), EDGE, false, 1.0)
	_box.draw_rect(r.grow(-3.5), Color(EDGE, EDGE.a * 0.35), false, 1.0)
	for corner in [r.position, Vector2(r.end.x, r.position.y), r.end, Vector2(r.position.x, r.end.y)]:
		var sx := 1.0 if corner.x == r.position.x else -1.0
		var sy := 1.0 if corner.y == r.position.y else -1.0
		var c: Vector2 = corner + Vector2(sx * 0.5, sy * 0.5)
		_box.draw_line(c, c + Vector2(sx * 9, 0), Color(EDGE, 1.0), 2.0)
		_box.draw_line(c, c + Vector2(0, sy * 9), Color(EDGE, 1.0), 2.0)
