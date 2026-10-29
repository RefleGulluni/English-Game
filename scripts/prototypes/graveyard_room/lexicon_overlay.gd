extends Control
## The Lexicon: Tab opens the hero's book over the room (grey box 2026-10-24; opening and closing
## per Decision Log D-068, revised with the user 2026-10-29).
##
## Opening (about 1.3 s), the spine at the centre of the screen throughout: the closed book rises
## with its cover to the player while the world dims -> the sigil engraved on the cover wakes in
## cyan -> the book tips back and stands on its spine, light showing in the seam between the
## covers -> both covers fall open at once, left and right -> the constellation lights up from the
## spine outwards and the entries appear. Closing plays it backwards and faster (about 0.5 s), so
## the cover faces the player again as it goes; Tab at any moment turns it around.
##
## Book and language are separate layers: the book is world pixels with no cyan on it; the sigil,
## the seam light, the constellation and the words are drawn here. Until the character group
## delivers the clean book and its frames (docs/LEXICON_BOOK_ANIMATION_REQUEST.md) the clean
## versions are lifted off the design sheet, and tipping and falling are flat grey-box shapes.

signal open_changed(is_open: bool)

const SHEET := "res://art/character_design/lexicon_book_sheet.png"
const CLOSED_BOOK := Rect2i(16, 48, 128, 128) # closed book inside the sheet, its cover centred
const OPEN_BOOK := Rect2i(168, 48, 256, 128) # open spread inside the sheet (its spine at x 128)
const OPEN_SPINE := 128
const BOOK_TOP := 4 # rows the book covers inside both cells
const BOOK_BOTTOM := 124
const COVER_W := 98 # width of the closed cover
# The character group's clean book and frames (all 256x128 cells, spine at x 128); used as soon
# as they exist.
const CLEAN_DIR := "res://art/character_design/lexicon/"
const RIGHT_PAGE := Rect2i(140, 14, 92, 88) # blanked area of the right page, in book pixels
const PAPER := Color8(205, 189, 172)
const ENGRAVED := Color8(38, 29, 24) # the sigil pressed into the leather while it sleeps
const LEATHER := Color8(70, 50, 36) # grey-box covers until the frames arrive
const FONT := preload("res://art/ui/fonts/CormorantGaramond.ttf")
const CYAN := Color(0.42, 0.86, 0.95)
const INK := Color8(44, 31, 24)
const PENCIL := Color8(128, 116, 104)
const OPEN_TIME := 1.3 # user 2026-10-29: 0.7 felt too fast; tipping the book up adds a beat
const CLOSE_TIME := 0.5
const PACE := [0.6, 1.0, 1.6] # keys 1 / 2 / 3: quicker, as designed, slower (to judge the timing)
# Where each stage ends, as a share of the opening.
const P_RISE := 0.15
const P_SIGIL := 0.32
const P_TIP := 0.48
const P_FALL := 0.78
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
var _tip_frames: Texture2D # cover to the player -> standing on its spine; null until delivered
var _fall_frames: Texture2D # standing -> both covers fallen open; null until delivered
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
	_tip_frames = _strip("lexicon_tip_up.png")
	_fall_frames = _strip("lexicon_covers_fall.png")
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


static func _strip(file: String) -> Texture2D:
	var path := ProjectSettings.globalize_path(CLEAN_DIR + file)
	return ImageTexture.create_from_image(Image.load_from_file(path)) if FileAccess.file_exists(path) else null


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
	# Every stage shares one 256x128 frame whose centre line is the spine.
	var origin := (screen_rect.position + (screen_rect.size - size) / 2.0).snapped(Vector2(pixel, pixel)) + Vector2(0, lift)
	var tip := _stage(P_SIGIL, P_TIP)
	var fall := _stage(P_TIP, P_FALL)

	if tip <= 0.0:
		var at := origin + Vector2(OPEN_SPINE - CLOSED_BOOK.size.x / 2, 0) * unit
		draw_texture_rect(_closed, Rect2(at, Vector2(CLOSED_BOOK.size) * unit), false, Color(1, 1, 1, minf(1.0, rise_t * 2.0)))
		# The sigil wakes: a flash that settles into a steady glow.
		var wake := _stage(P_RISE, P_SIGIL)
		if wake > 0.0:
			_draw_pixels(_sigil, at, unit, CYAN, wake, 0.22 * (1.0 + 0.8 * sin(wake * PI)))
	elif fall <= 0.0:
		if _tip_frames:
			_draw_frame(_tip_frames, tip, origin, size)
		else: # grey box: the cover turns away about the spine, narrowing to the standing book
			var w := maxi(14, roundi(COVER_W * cos(tip * PI / 2.0)))
			_box(origin, unit, OPEN_SPINE - w / 2, w, LEATHER)
			if w < 40:
				_box(origin, unit, OPEN_SPINE - w / 2 + 3, w - 6, PAPER.darkened(0.25))
		_seam(origin, unit, tip)
	elif fall < 1.0:
		if _fall_frames:
			_draw_frame(_fall_frames, fall, origin, size)
		else: # grey box: both covers fall outwards together, the pages fanning after them
			var w := maxi(7, roundi(OPEN_SPINE * cos((1.0 - ease(fall, 1.6)) * PI / 2.0)))
			_box(origin, unit, OPEN_SPINE - w, w, LEATHER)
			_box(origin, unit, OPEN_SPINE, w, LEATHER)
			if w > 8:
				_box(origin, unit, OPEN_SPINE - w + 4, w - 4, PAPER)
				_box(origin, unit, OPEN_SPINE, w - 4, PAPER)
		_seam(origin, unit, 1.0 - fall)
	else:
		draw_texture_rect(_open, Rect2(origin, size), false)

	if fall < 1.0:
		return
	draw_rect(Rect2(origin + Vector2(RIGHT_PAGE.position) * unit, Vector2(RIGHT_PAGE.size) * unit), PAPER)
	# The constellation lights up from the spine outwards.
	var lit := int(round(_stage(P_FALL, 1.0) * _stars.size()))
	var stars: Array[Vector2i] = []
	for i in lit:
		stars.append(_stars[i][0])
	_draw_pixels(stars, origin, unit, CYAN.darkened(0.15), 1.0, 0.18 + 0.05 * sin(_time * 1.6))
	_draw_entries(origin, unit, _stage(0.88, 1.0))


## One cell of a 256x128 strip, picked by 0..1 progress.
func _draw_frame(strip: Texture2D, progress: float, origin: Vector2, size: Vector2) -> void:
	var count := strip.get_width() / OPEN_BOOK.size.x
	var frame := mini(int(progress * count), count - 1)
	draw_texture_rect_region(strip, Rect2(origin, size), Rect2(frame * OPEN_BOOK.size.x, 0, OPEN_BOOK.size.x, OPEN_BOOK.size.y))


## Grey box: a full-height band of the book, x and width in book pixels.
func _box(origin: Vector2, unit: float, x: int, w: int, color: Color) -> void:
	draw_rect(Rect2(origin + Vector2(x, BOOK_TOP) * unit, Vector2(w, BOOK_BOTTOM - BOOK_TOP) * unit), color)


## Light in the seam between the covers while the book stands: language waking inside it.
func _seam(origin: Vector2, unit: float, strength: float) -> void:
	var points: Array[Vector2i] = []
	for y in range(BOOK_TOP + 3, BOOK_BOTTOM - 3):
		points.append(Vector2i(OPEN_SPINE, y))
	_draw_pixels(points, origin, unit, CYAN, clampf(strength * 1.5, 0.0, 1.0), 0.3)


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
