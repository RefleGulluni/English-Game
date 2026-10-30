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
const SLIP_PAPER := Color8(205, 189, 172) # the book's paper and writing (lexicon_overlay)
const SLIP_PENCIL := Color8(128, 116, 104)
const SLIP_INK := Color8(44, 31, 24)
const SLIP_TIME := {"RECOGNIZED": 2.2, "UNDERSTOOD": 3.2}
const SLIP_SIZE := Vector2(230, 90)
const SLIP_SLIDE := 0.35 # seconds the slip takes to come up, and to go back down

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
var _slips: Array[Dictionary] = [] # {lemma, stage} waiting their turn
var _slip := {} # the one on show
var _slip_t := 0.0
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
		_slip = _slips.pop_front()
		_slip_t = 0.0
	elif not _slip.is_empty():
		_slip_t += delta
		if _slip_t >= SLIP_TIME[_slip.stage]:
			_slip = {}
	_slip_c.queue_redraw()
	for f in _floats:
		var near := is_instance_valid(hero) and hero.visible and _box.visible == false
		var d: float = hero.global_position.distance_to(f.near) if near else 9999.0
		if d <= MEET and progress.stage(f.lemma) == "UNKNOWN":
			f.born = _clock
			_moved(f.lemma, progress.advance(f.lemma, "ambient"))
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
	if stage == "UNKNOWN": # a four-pointed glint, breathing, flaring every few seconds
		var breath := 0.6 + 0.4 * sin(_clock * 2.2)
		var flare := clampf(1.0 - fmod(_clock, 3.2) / 0.5, 0.0, 1.0) # a quick flare, then 2.7 s of calm
		var mid := Vector2(79, 13)
		var px := 2.0 # one glint pixel: two world pixels, so it reads from across the room
		var reach := 3 + int(round(3.0 * flare))
		for r in range(16, 0, -2): # soft halo
			c.draw_circle(mid + Vector2(px, px) / 2.0, r, Color(CYAN, 0.03 * a * (breath + flare)))
		for i in range(1, reach + 1): # the four arms, fading out along their length
			var arm_a := a * (breath * 0.8 + flare * 0.6) * (1.0 - float(i - 1) / reach)
			for dir in [Vector2.UP, Vector2.DOWN, Vector2.LEFT, Vector2.RIGHT]:
				c.draw_rect(Rect2(mid + dir * i * px, Vector2(px, px)), Color(CYAN, clampf(arm_a, 0.0, 1.0)))
		c.draw_rect(Rect2(mid, Vector2(px, px)), Color(Color.WHITE.lerp(CYAN, 0.3), a))
		return
	var since: float = _clock - float(f.born)
	var writing := clampf(since / (WRITE_IN * 0.6), 0.0, 1.0) # letters appear one by one
	var cooling := clampf((since - WRITE_IN * 0.5) / (WRITE_IN * 0.5), 0.0, 1.0) # then cool from lit to pencil
	var size := 17
	var shown := word
	var color := CYAN
	match stage:
		"ENCOUNTERED": # its first letters and a gap, and a crack through it: seen, not yet read
			shown = word.left(3).to_lower() + "_".repeat(maxi(2, word.length() - 3))
			color = Color(PENCIL, 0.9)
		"RECOGNIZED":
			color = PENCIL
		"UNDERSTOOD":
			color = INK
	var w := FONT.get_string_size(shown, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x
	var at := Vector2(roundf(80 - w / 2.0), 16)
	if since < WRITE_IN: # just seen: lit like language, written in as you watch
		shown = shown.left(ceili(writing * shown.length()))
		color = Color(CYAN.lerp(color, cooling), lerpf(1.0, color.a, cooling))
		c.draw_string_outline(FONT, at, shown, HORIZONTAL_ALIGNMENT_LEFT, -1, size, 8, Color(CYAN, 0.18 * a * (1.0 - cooling)))
	# a soft dark edge so a pale word still reads on pale stone
	c.draw_string_outline(FONT, at, shown, HORIZONTAL_ALIGNMENT_LEFT, -1, size, 4, Color(0.03, 0.03, 0.05, 0.55 * a))
	if stage == "USABLE": # language: a steady glow
		c.draw_string_outline(FONT, at, shown, HORIZONTAL_ALIGNMENT_LEFT, -1, size, 8, Color(CYAN, 0.12 * a))
	c.draw_string(FONT, at, shown, HORIZONTAL_ALIGNMENT_LEFT, -1, size, Color(color, color.a * a))
	if stage == "ENCOUNTERED" and since >= WRITE_IN * 0.6:
		var crack := PackedVector2Array([at + Vector2(-3, -12), at + Vector2(w * 0.3, -7), at + Vector2(w * 0.45, -10), at + Vector2(w * 0.7, -3), at + Vector2(w + 4, -6)])
		c.draw_polyline(crack, Color(PENCIL, 0.55 * a), 1.0)
	# a hairline down to the thing it belongs to
	c.draw_line(Vector2(80, 21), Vector2(80, 26), Color(color, 0.35 * a), 1.0)


# --- Notes -----------------------------------------------------------------------------------

func _moved(lemma: String, stage: String) -> void:
	if stage.is_empty():
		return
	var word := lemma.to_upper()
	match stage:
		"ENCOUNTERED":
			note("A NEW WORD  ·  %s" % (word.left(3).to_lower() + "_".repeat(word.length() - 3)), PENCIL)
			_book_t = 0.0
		"RECOGNIZED", "UNDERSTOOD": _slips.append({"lemma": lemma, "stage": stage})
		"USABLE": note("%s  ·  USABLE  ·  it is yours now" % word, CYAN)
	advanced.emit(lemma, stage)


## Evidence from outside this layer (a fight); same notes, same rules.
func evidence(lemma: String, kind: String, encounter: String) -> String:
	var stage: String = progress.advance(lemma, kind, encounter)
	_moved(lemma, stage)
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

## A corner of a page comes up from the bottom right: the word is pencilled in letter by letter;
## understood, ink goes over the pencil from left to right and the meaning appears underneath.
func _draw_slip() -> void:
	if _slip.is_empty():
		return
	var t := _slip_t
	var total: float = SLIP_TIME[_slip.stage]
	var up := ease(clampf(t / SLIP_SLIDE, 0.0, 1.0), 0.4) * ease(clampf((total - t) / SLIP_SLIDE, 0.0, 1.0), 0.4)
	var rest := NATIVE - SLIP_SIZE - Vector2(24, 18)
	var at := Vector2(rest.x, roundf(lerpf(NATIVE.y + 4, rest.y, up)))
	var c := _slip_c
	c.draw_rect(Rect2(at + Vector2(3, 3), SLIP_SIZE), Color(0, 0, 0, 0.35))
	c.draw_rect(Rect2(at, SLIP_SIZE), SLIP_PAPER)
	c.draw_rect(Rect2(at, SLIP_SIZE), SLIP_PAPER.darkened(0.3), false, 1.0)
	var fold := PackedVector2Array([at + Vector2(SLIP_SIZE.x - 14, 0), at + Vector2(SLIP_SIZE.x, 14), at + Vector2(SLIP_SIZE.x - 14, 14)])
	c.draw_colored_polygon(fold, SLIP_PAPER.darkened(0.18)) # a dog-eared corner: it is a page of the book
	c.draw_line(at + Vector2(SLIP_SIZE.x - 14, 0), at + Vector2(SLIP_SIZE.x, 14), SLIP_PAPER.darkened(0.35), 1.0)
	var word := str(_slip.lemma).to_upper()
	var size := 26
	var pen := clampf((t - SLIP_SLIDE) / 0.8, 0.0, 1.0) # the pencil writes the letters in
	var ink := clampf((t - SLIP_SLIDE - 0.4) / 1.0, 0.0, 1.0) * word.length() if _slip.stage == "UNDERSTOOD" else 0.0
	var x := at.x + 16
	for i in ceili(pen * word.length()):
		var color := Color(SLIP_PENCIL, 0.85).lerp(SLIP_INK, clampf(ink - i, 0.0, 1.0))
		c.draw_string(FONT, Vector2(x, at.y + 38), word[i], HORIZONTAL_ALIGNMENT_LEFT, -1, size, color)
		x += FONT.get_string_size(word[i], HORIZONTAL_ALIGNMENT_LEFT, -1, size).x
	var small := 12
	if _slip.stage == "RECOGNIZED":
		c.draw_string(FONT, at + Vector2(16, 62), "recognized  ·  pencilled in", HORIZONTAL_ALIGNMENT_LEFT, -1, small, Color(SLIP_PENCIL, clampf((t - 1.2) / 0.4, 0.0, 1.0)))
	else:
		var meaning := str(WORDS.sense(str(_slip.lemma)))
		c.draw_multiline_string(FONT, at + Vector2(16, 60), meaning, HORIZONTAL_ALIGNMENT_LEFT, SLIP_SIZE.x - 28, small, 2, Color(SLIP_INK, 0.85 * clampf((t - 1.7) / 0.5, 0.0, 1.0)))
		c.draw_string(FONT, at + Vector2(SLIP_SIZE.x - 82, 16), "understood", HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Color(SLIP_INK, 0.6 * clampf((t - 1.9) / 0.4, 0.0, 1.0)))


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
