extends Control
## The Lexicon: Tab opens the hero's book over the room (grey box 2026-10-24; opening and closing
## per Decision Log D-068, 2026-10-29).
##
## Opening (about 0.7 s): the closed book rises to the centre while the world dims -> the sigil
## engraved on the cover wakes in cyan -> the cover swings open about the spine -> the
## constellation lights up from the spine outwards -> the entries appear. Closing plays it
## backwards and faster (about 0.4 s); Tab at any moment turns it around from where it is.
##
## Book and language are separate layers: the book is world pixels with no cyan on it; the sigil,
## the constellation and the words are drawn here. Until the character group delivers the clean
## book (docs/LEXICON_BOOK_ANIMATION_REQUEST.md) the clean versions are derived from the design
## sheet by lifting its cyan pixels off, and the cover swing is a plain cut.

signal open_changed(is_open: bool)

const SHEET := "res://art/character_design/lexicon_book_sheet.png"
const CLOSED_BOOK := Rect2i(16, 48, 128, 128) # closed book inside the sheet (its spine at x 15)
const OPEN_BOOK := Rect2i(168, 48, 256, 128) # open spread inside the sheet (its spine at x 128)
const CLOSED_SPINE := 15
const OPEN_SPINE := 128
# The character group's clean book and cover frames; used as soon as they exist.
const CLEAN_DIR := "res://art/character_design/lexicon/"
const RIGHT_PAGE := Rect2i(140, 14, 92, 88) # blanked area of the right page, in book pixels
const PAPER := Color8(205, 189, 172)
const ENGRAVED := Color8(38, 29, 24) # the sigil pressed into the leather while it sleeps
const FONT := preload("res://art/ui/fonts/CormorantGaramond.ttf")
const CYAN := Color(0.42, 0.86, 0.95)
const INK := Color8(44, 31, 24)
const PENCIL := Color8(128, 116, 104)
const OPEN_TIME := 0.7
const CLOSE_TIME := 0.4
const PACE := [0.6, 1.0, 1.6] # keys 1 / 2 / 3: quicker, as designed, slower (to judge the timing)
# Where each stage ends, as a share of the opening.
const P_RISE := 0.22
const P_SIGIL := 0.42
const P_COVER := 0.78
const RISE := 24 # native pixels the book travels up while rising
# One entry per learning stage (World Bible §10). Encountered and recognized words never show
# their meaning: the book must not leak answers that have not been learned.
const ENTRIES := [
	{"word": "OBSERVE", "stage": "USABLE", "note": "to watch closely and notice"},
	{"word": "GRAVE", "stage": "UNDERSTOOD", "note": "a place in the ground for the dead"},
	{"word": "LANTERN", "stage": "RECOGNIZED", "note": ""},
	{"word": "", "stage": "ENCOUNTERED", "note": ""},
]

var screen_rect := Rect2() # the game screen inside the window
var pixel := 2 # window pixels per native pixel
var book_scale := 3 # native pixels per book pixel; Z switches 2 / 3 (user picked 3, 2026-10-24)
var speed := 1
var is_open := false
var selected := 0
var _t := 0.0 # 0 closed .. 1 open, along the whole opening
var _closed: Texture2D
var _open: Texture2D
var _cover_frames: Texture2D # the swing, 256x128 cells; null until delivered
var _cover_count := 0
var _sigil: Array[Vector2i] = [] # cyan pixels of the cover, in closed-book pixels
var _stars: Array = [] # [Vector2i, Color] of the constellation, nearest the spine first
var _time := 0.0


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	var sheet := Image.load_from_file(ProjectSettings.globalize_path(SHEET))
	var closed := sheet.get_region(CLOSED_BOOK)
	var open := sheet.get_region(OPEN_BOOK)
	_sigil.assign(_lift_cyan(closed, ENGRAVED).map(func(p): return p[0]))
	_stars = _lift_cyan(open, PAPER).filter(func(p): return not RIGHT_PAGE.has_point(p[0]))
	_stars.sort_custom(func(a, b): return absi(a[0].x - OPEN_SPINE) < absi(b[0].x - OPEN_SPINE))
	_closed = _clean("lexicon_closed_clean.png", closed)
	_open = _clean("lexicon_open_clean.png", open)
	var swing := ProjectSettings.globalize_path(CLEAN_DIR + "lexicon_cover_open.png")
	if FileAccess.file_exists(swing):
		_cover_frames = ImageTexture.create_from_image(Image.load_from_file(swing))
		_cover_count = _cover_frames.get_width() / OPEN_BOOK.size.x
	var mask := ProjectSettings.globalize_path(CLEAN_DIR + "lexicon_sigil_mask.png")
	if FileAccess.file_exists(mask):
		var img := Image.load_from_file(mask)
		_sigil.clear()
		for y in img.get_height():
			for x in img.get_width():
				if img.get_pixel(x, y).a > 0.5:
					_sigil.append(Vector2i(x, y))


## Takes the cyan (language) pixels off a piece of the sheet, filling them with `fill`; returns
## them as [position, colour].
static func _lift_cyan(img: Image, fill: Color) -> Array:
	var lifted := []
	for y in img.get_height():
		for x in img.get_width():
			var c := img.get_pixel(x, y)
			if c.a > 0.5 and c.b8 > 110 and c.g8 > 100 and c.b8 > c.r8 + 40:
				lifted.append([Vector2i(x, y), c])
				img.set_pixel(x, y, fill)
	return lifted


func _clean(file: String, derived: Image) -> Texture2D:
	var path := ProjectSettings.globalize_path(CLEAN_DIR + file)
	return ImageTexture.create_from_image(Image.load_from_file(path) if FileAccess.file_exists(path) else derived)


func toggle() -> void:
	is_open = not is_open
	open_changed.emit(is_open)


func set_open_now(open: bool) -> void:
	is_open = open
	_t = 1.0 if open else 0.0
	queue_redraw()


func _process(delta: float) -> void:
	_time += delta
	var duration: float = (OPEN_TIME if is_open else CLOSE_TIME) * PACE[speed]
	var was := _t
	_t = move_toward(_t, 1.0 if is_open else 0.0, delta / duration)
	if _t > 0.0 or was > 0.0: # one more redraw once fully closed, to clear the last frame
		queue_redraw()


func _unhandled_input(event: InputEvent) -> void:
	if not (event is InputEventKey and event.pressed and not event.echo):
		return
	if event.keycode == KEY_TAB or (is_open and event.keycode == KEY_ESCAPE):
		toggle()
	elif event.keycode in [KEY_1, KEY_2, KEY_3]:
		speed = event.keycode - KEY_1
	elif event.keycode == KEY_Z:
		book_scale = 5 - book_scale
	elif is_open and event.keycode in [KEY_W, KEY_UP]:
		selected = (selected + ENTRIES.size() - 1) % ENTRIES.size()
	elif is_open and event.keycode in [KEY_S, KEY_DOWN]:
		selected = (selected + 1) % ENTRIES.size()
	else:
		return
	get_viewport().set_input_as_handled()
	queue_redraw()


## 0..1 progress through the stage that runs from a to b.
func _stage(a: float, b: float) -> float:
	return clampf((_t - a) / (b - a), 0.0, 1.0)


func _draw() -> void:
	if _t <= 0.0:
		return
	var rise_t := ease(_stage(0.0, P_RISE), -2.0)
	draw_rect(screen_rect, Color(0.02, 0.02, 0.04, 0.62 * ease(_stage(0.0, P_SIGIL), -2.0)))

	var unit := pixel * book_scale # window pixels per book pixel
	var size := Vector2(OPEN_BOOK.size) * unit
	var lift := roundi((1.0 - rise_t) * RISE) * pixel # moves on the native grid
	# The spine stays put the whole way: the closed book waits where the right page will be.
	var origin := (screen_rect.position + (screen_rect.size - size) / 2.0).snapped(Vector2(pixel, pixel)) + Vector2(0, lift)
	var shade := Color(1, 1, 1, minf(1.0, rise_t * 2.0))
	var swing := _stage(P_SIGIL, P_COVER)

	if swing <= 0.0 or (_cover_frames == null and swing < 0.5):
		var at := origin + Vector2(OPEN_SPINE - CLOSED_SPINE, 0) * unit
		draw_texture_rect(_closed, Rect2(at, Vector2(CLOSED_BOOK.size) * unit), false, shade)
		# The sigil wakes: a flash that settles into a steady glow.
		var wake := _stage(P_RISE, P_SIGIL)
		if wake > 0.0:
			var flash := 1.0 + 0.8 * sin(wake * PI)
			_draw_pixels(_sigil, at, unit, CYAN, wake, 0.22 * flash)
	elif _cover_frames != null and swing < 1.0:
		var frame := mini(int(swing * _cover_count), _cover_count - 1)
		draw_texture_rect_region(_cover_frames, Rect2(origin, size), Rect2(frame * OPEN_BOOK.size.x, 0, OPEN_BOOK.size.x, OPEN_BOOK.size.y))
	else:
		draw_texture_rect(_open, Rect2(origin, size), false)

	if swing < 1.0:
		return
	draw_rect(Rect2(origin + Vector2(RIGHT_PAGE.position) * unit, Vector2(RIGHT_PAGE.size) * unit), PAPER)
	# The constellation lights up from the spine outwards.
	var lit := int(round(_stage(P_COVER, 1.0) * _stars.size()))
	var stars: Array[Vector2i] = []
	for i in lit:
		stars.append(_stars[i][0])
	_draw_pixels(stars, origin, unit, CYAN.darkened(0.15), 1.0, 0.18 + 0.05 * sin(_time * 1.6))
	_draw_entries(origin, unit, _stage(0.88, 1.0))


## Language pixels: a soft one-pixel glow around each, then the pixel itself.
func _draw_pixels(points: Array[Vector2i], at: Vector2, unit: float, color: Color, alpha: float, glow: float) -> void:
	for p in points:
		for o in [Vector2(-1, 0), Vector2(1, 0), Vector2(0, -1), Vector2(0, 1)]:
			draw_rect(Rect2(at + (Vector2(p) + o) * unit, Vector2(unit, unit)), Color(CYAN, glow * alpha))
	for p in points:
		draw_rect(Rect2(at + Vector2(p) * unit, Vector2(unit, unit)), Color(color, alpha))


func _draw_entries(origin: Vector2, unit: float, e: float) -> void:
	if e <= 0.0:
		return
	# Entries on the right page: one line per word, its meaning underneath once understood.
	var left := origin.x + (RIGHT_PAGE.position.x + 8) * unit
	var top := origin.y + (RIGHT_PAGE.position.y + 6) * unit
	var row := 20.0 * unit
	var word_size := int(7.5 * unit)
	var note_size := int(4.6 * unit)
	for i in ENTRIES.size():
		var entry: Dictionary = ENTRIES[i]
		var y := top + i * row
		if i == selected:
			draw_rect(Rect2(Vector2(left - 5 * unit, y + 2 * unit), Vector2(2, 2) * unit), Color(INK, e))
		match entry.stage:
			"ENCOUNTERED": # only a reserved place: corner brackets around an empty line
				_brackets(Rect2(Vector2(left, y + unit), Vector2(56, 9) * unit), Color(PENCIL, 0.8 * e), unit)
			"RECOGNIZED": # pencil sketch, slightly unsteady
				var jitter := Vector2(0, roundf(sin(_time * 2.0)) * 0.5 * unit)
				draw_string(FONT, Vector2(left, y + 8 * unit) + jitter, entry.word, HORIZONTAL_ALIGNMENT_LEFT, -1, word_size, Color(PENCIL, 0.75 * e))
			"UNDERSTOOD": # ink, settled
				draw_string(FONT, Vector2(left, y + 8 * unit), entry.word, HORIZONTAL_ALIGNMENT_LEFT, -1, word_size, Color(INK, e))
				draw_string(FONT, Vector2(left, y + 14 * unit), entry.note, HORIZONTAL_ALIGNMENT_LEFT, -1, note_size, Color(INK, 0.8 * e))
			"USABLE": # cyan, steady glow: language
				var glow := 0.18 + 0.06 * sin(_time * 1.6)
				for o in [Vector2(-1, 0), Vector2(1, 0), Vector2(0, -1), Vector2(0, 1)]:
					draw_string(FONT, Vector2(left, y + 8 * unit) + o * unit * 0.6, entry.word, HORIZONTAL_ALIGNMENT_LEFT, -1, word_size, Color(CYAN, glow * e))
				draw_string(FONT, Vector2(left, y + 8 * unit), entry.word, HORIZONTAL_ALIGNMENT_LEFT, -1, word_size, Color(CYAN.darkened(0.25), e))
				draw_string(FONT, Vector2(left, y + 14 * unit), entry.note, HORIZONTAL_ALIGNMENT_LEFT, -1, note_size, Color(INK, 0.8 * e))

	var stage: String = ENTRIES[selected].stage
	var caption := "%s   ·   W/S choose   Tab close   1/2/3 speed   Z size" % stage
	var caption_size := int(8 * pixel)
	var w := FONT.get_string_size(caption, HORIZONTAL_ALIGNMENT_LEFT, -1, caption_size).x
	draw_string(FONT, Vector2(screen_rect.get_center().x - w / 2.0, origin.y + OPEN_BOOK.size.y * unit + 18 * pixel), caption, HORIZONTAL_ALIGNMENT_LEFT, -1, caption_size, Color(0.85, 0.82, 0.76, e))


func _brackets(r: Rect2, color: Color, unit: float) -> void:
	var l := 4 * unit
	var w := unit
	for corner in [r.position, Vector2(r.end.x, r.position.y), Vector2(r.position.x, r.end.y), r.end]:
		var sx := 1.0 if corner.x == r.position.x else -1.0
		var sy := 1.0 if corner.y == r.position.y else -1.0
		draw_rect(Rect2(corner + Vector2(minf(0, sx * l), minf(0, sy * w)), Vector2(l, w)), color)
		draw_rect(Rect2(corner + Vector2(minf(0, sx * w), minf(0, sy * l)), Vector2(w, l)), color)
