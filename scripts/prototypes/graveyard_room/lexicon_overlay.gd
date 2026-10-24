extends Control
## Grey-box Lexicon: Tab opens the hero's book over the graveyard room (2026-10-24).
##
## Only for finding the feel of "opening the book": timing, dimming, size, and how the four
## learning stages read on a page. The open book is the existing Lexicon sheet art; the right
## page is blanked and the entries are drawn on top. Long readable text uses a clear font
## (the v3 exception for text meant to be read).

signal open_changed(is_open: bool)

const SHEET := "res://art/character_design/lexicon_book_sheet.png"
const OPEN_BOOK := Rect2i(168, 48, 256, 128) # open spread inside the sheet
const RIGHT_PAGE := Rect2i(140, 14, 92, 88) # blanked area of the right page, in book pixels
const PAPER := Color8(205, 189, 172)
const FONT := preload("res://art/ui/fonts/CormorantGaramond.ttf")
const CYAN := Color(0.42, 0.86, 0.95)
const INK := Color8(44, 31, 24)
const PENCIL := Color8(128, 116, 104)
const SPEEDS := [0.25, 0.45, 0.8] # seconds to open or close; keys 1 / 2 / 3 (user picked 0.45)
const RISE := 24 # native pixels the book travels up while opening
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
var _t := 0.0 # 0 closed .. 1 open
var _book: Texture2D
var _time := 0.0


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	var sheet := Image.load_from_file(ProjectSettings.globalize_path(SHEET))
	_book = ImageTexture.create_from_image(sheet.get_region(OPEN_BOOK))


func toggle() -> void:
	is_open = not is_open
	open_changed.emit(is_open)


func set_open_now(open: bool) -> void:
	is_open = open
	_t = 1.0 if open else 0.0
	queue_redraw()


func _process(delta: float) -> void:
	_time += delta
	_t = move_toward(_t, 1.0 if is_open else 0.0, delta / SPEEDS[speed])
	if _t > 0.0:
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


func _draw() -> void:
	if _t <= 0.0:
		return
	var e := ease(_t, -2.0) # ease in-out
	draw_rect(screen_rect, Color(0.02, 0.02, 0.04, 0.62 * e))

	var unit := pixel * book_scale # window pixels per book pixel
	var size := Vector2(OPEN_BOOK.size) * unit
	var rise := roundi((1.0 - e) * RISE) * pixel # moves on the native grid
	var origin := (screen_rect.position + (screen_rect.size - size) / 2.0).snapped(Vector2(pixel, pixel)) + Vector2(0, rise)
	var fade := Color(1, 1, 1, e)
	draw_texture_rect(_book, Rect2(origin, size), false, fade)
	draw_rect(Rect2(origin + Vector2(RIGHT_PAGE.position) * unit, Vector2(RIGHT_PAGE.size) * unit), Color(PAPER, e))

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
	draw_string(FONT, Vector2(screen_rect.get_center().x - w / 2.0, origin.y + size.y + 18 * pixel), caption, HORIZONTAL_ALIGNMENT_LEFT, -1, caption_size, Color(0.85, 0.82, 0.76, e))


func _brackets(r: Rect2, color: Color, unit: float) -> void:
	var l := 4 * unit
	var w := unit
	for corner in [r.position, Vector2(r.end.x, r.position.y), Vector2(r.position.x, r.end.y), r.end]:
		var sx := 1.0 if corner.x == r.position.x else -1.0
		var sy := 1.0 if corner.y == r.position.y else -1.0
		draw_rect(Rect2(corner + Vector2(minf(0, sx * l), minf(0, sy * w)), Vector2(l, w)), color)
		draw_rect(Rect2(corner + Vector2(minf(0, sx * w), minf(0, sy * l)), Vector2(w, l)), color)
