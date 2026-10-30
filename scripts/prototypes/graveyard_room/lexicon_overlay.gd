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
##
## Turning a page (A / D) is computed, not a drawn strip (user 2026-10-29: smoother, and the words
## must turn with the paper, like a real book). Both spreads are painted into hidden viewports;
## the leaf is then drawn one book-pixel column at a time, each column projected round the spine
## on a bending curve, so the motion runs at the frame rate yet stays on the book's pixel grid.
## Past upright the leaf shows its back, which is the next spread's facing page. V switches back
## to the character group's six drawn frames, to compare.
##
## What the pages show is the sky (D-080, D-088; lexicon_sky.gd holds it as data): five levels,
## the whole sky -> a region -> a cluster -> a constellation -> one word's spread. The left page is
## the picture, drawn in the book's own pixels and materials (pale ink washes, pencil, ink, and
## cyan only for what is usable); the right page says what it is. E / Q (or a click, a right
## click) go closer and back, and going closer is not a camera zoom: the page is redrawn, the old
## washes fading as the next level's wash seeps in and its stars and lines are drawn one by one.
## W / S choose; A / D turn the page to the next thing on the same level (D-073: a page turn stays
## inside one level).

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
# Seconds for the book appearing / disappearing (the rise stage) and for everything after it.
# User 2026-10-29: 0.7 s, 1.3 s, 2 s to open and 0.4 s .. 1.5 s to close each felt too fast; then
# 0.3 s more for the book appearing and for it disappearing.
const OPEN_RISE := 0.6
const OPEN_REST := 2.2 # +0.5 s for the sigil ring drawing itself (user 2026-10-29)
const CLOSE_RISE := OPEN_RISE # user 2026-10-29: closing as slow as opening
const CLOSE_REST := OPEN_REST
const TURN_TIME := 0.6 # one page turn (user: 0.15 s slower than 0.45)
const LIVE_TURN_TIME := 0.8 # the computed turn: nothing to count frames on, so a touch more leisurely
const LEAF_LIFT := 0.06 # book pixels the leaf rises on screen per book pixel of height above the page
const LEAF_LAG := 0.18 # how far the spine side of the leaf trails its free edge (share of the turn)
const LEAF_SHADE := 0.3 # how much the leaf darkens as it stands up, away from the light
const PAPER_MIN_LUMA := 0.43 # brighter than this is paper (leather and binding are darker)
const WORDS_DIR := "res://data/words/"
const WORDS := preload("res://scripts/run/word_library.gd")
const PAGE_STAGES := ["USABLE", "UNDERSTOOD", "RECOGNIZED", "ENCOUNTERED"] # grey box: no progress yet
const SKY := preload("res://scripts/prototypes/graveyard_room/lexicon_sky.gd")
const WIPE := 0.4 # seconds the old level takes to fade when the page is redrawn
const WASH_IN := 0.7 # the new level's washes seeping into the paper
const STAR_GAP := 0.09 # between one star appearing and the next
const STAR_FLASH := 0.35 # a new star flares, then settles
const LINE_TIME := 0.3 # one line drawing itself from star to star
const WASH_SHADE := 0.89 # how much darker than the paper a wash pixel is
const STAGE_NAMES := {"ENCOUNTERED": "seen", "RECOGNIZED": "recognized", "UNDERSTOOD": "understood", "USABLE": "usable"}
const TABS := [["find", Color8(120, 46, 40)], ["recent", Color8(58, 74, 62)], ["review", Color8(150, 118, 60)], ["stage", Color8(64, 70, 96)]]
const PACE := [0.7, 1.0, 1.4] # keys 1 / 2 / 3: quicker, as designed, slower (to judge the timing)
# Where each stage ends, as a share of the opening.
const P_RISE := 0.15
const P_SIGIL := 0.48 # the sigil wakes: triangle and dot, then the ring drawn clockwise
const P_TIP := 0.60
const P_FALL := 0.83
const RISE := 24 # native pixels the book travels up while rising
# A word becoming USABLE (2026-10-30): once the book lies open at its page, its letters light
# one by one, the meaning settles, the word leaves the book as a card for the word bar, and the
# book closes by itself. Seconds, counted from the book lying open.
const RITE_START := 0.5
const RITE_LETTER := 0.2
const RITE_CARD := 1.1 # the card's flight
const RITE_HOLD := 0.7 # after the card, before the book closes
# It can't be interrupted, only skipped on purpose (user 2026-10-30): holding Space (or Esc) fills a
# small ring; other keys do nothing. The hint waits a second, and the very first ceremony in a
# player's game has none: it is where they learn the book answers them.
const SKIP_HOLD := 0.6
const SKIP_HINT_AFTER := 1.0
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
var _turn_frames: Texture2D # one page turning right to left; null until delivered
var _turn := -1.0 # 0..1 while a page turns
var _turn_back := false # A: the page comes back from the left (the strip played backwards)
var live_turn := true # V: false plays the six drawn frames instead
var _page := 0 # which spread is open
var _turn_from := 0 # the spread a turn started from
var _warm := 0 # frames left for the viewports to paint before a turn starts moving
var _spreads: Array[SubViewport] = [] # [the spread turned from, the spread turned to]
var _spread_page := [0, 0]
var _spread_unit := 1.0 # screen pixels per book pixel inside the hidden spreads
var _leaf_len := 0 # columns of paper from the spine to a page's outer edge
var _paper_rows := {} # book x -> Vector2i(top, bottom) of the paper in that column of the open book
var sky: SKY = SKY.new()
var progress # lexicon_progress.gd, for the sentences on a word's page (optional)
var _level := 1 # 1 the sky ... 5 a word's spread
var _path := [0, 0, 0, 0] # what is looked at: region, cluster, constellation, word (lexicon_sky.gd)
var _prev := {} # the level being wiped off while the next is drawn in: {level, path, selected}
var _washes := {} # the ink washes of a view, one texture each, made once
var _open_img: Image
var _hits: Array = [] # [Rect2 on screen, index]: what a click on the left page picks
var _rite_from := Vector2.ZERO # where the ceremony's card lifts off (the big word)
var _sounds := SystemFont.new() # the phonetic line: the book's font has no IPA letters
var _ci: CanvasItem = self # where the helpers draw: this overlay, or one of the hidden spreads
var _sigil: Array[Vector2i] = [] # cyan pixels of the cover, in closed-book pixels
var _sigil_core: Array[Vector2i] = [] # the triangle and the dot inside it
var _sigil_ring: Array[Vector2i] = [] # the circle, clockwise from its top
# The constellation, split into stars (the dense knots) and the lines between them. The stars
# light one by one from the spine outwards, then each line draws itself from star to star.
var _seam_x := OPEN_SPINE # the gap between the pages of the standing book
var _seam_y := Vector2i(BOOK_TOP + 3, BOOK_BOTTOM - 3) # its lit stretch, inside the page block
var _glow: Texture2D # soft elliptical halo for the seam light
var _sky := 0.0 # seconds since the book lay fully open (the constellation's own clock)
var _time := 0.0
var _rite_lemma := "" # the word whose ceremony is running
var _rite := -1.0 # seconds of ceremony since the book lay open; -1: none
var _rite_clock := 0.0 # seconds since the ceremony began (the book still opening included)
var _skippable := true
var _hold := 0.0 # seconds Space / Esc has been held towards a skip


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	var sheet := Image.load_from_file(ProjectSettings.globalize_path(SHEET))
	var closed := sheet.get_region(CLOSED_BOOK)
	var open := sheet.get_region(OPEN_BOOK)
	_sigil.assign(_lift_cyan(closed, ENGRAVED).map(func(p): return p[0]))
	_lift_cyan(open, PAPER) # the design sheet's constellation: the sky is drawn from data now
	_closed = _clean("lexicon_closed_clean.png", closed)
	_open = _clean("lexicon_open_clean.png", open)
	_tip_frames = _strip("lexicon_tip_up.png")
	_fall_frames = _strip("lexicon_covers_fall.png")
	_turn_frames = _strip("lexicon_page_turn.png")
	_find_seam()
	var halo := GradientTexture2D.new()
	halo.fill = GradientTexture2D.FILL_RADIAL
	halo.fill_from = Vector2(0.5, 0.5)
	halo.fill_to = Vector2(1.0, 0.5)
	halo.gradient = Gradient.new()
	halo.gradient.set_color(0, Color(CYAN, 0.7))
	halo.gradient.set_color(1, Color(CYAN, 0.0))
	halo.gradient.add_point(0.3, Color(CYAN, 0.3))
	_glow = halo
	var mask := ProjectSettings.globalize_path(CLEAN_DIR + "lexicon_sigil_mask.png")
	if FileAccess.file_exists(mask):
		var img := Image.load_from_file(mask)
		_sigil.clear()
		for y in img.get_height():
			for x in img.get_width():
				if img.get_pixel(x, y).a > 0.5:
					_sigil.append(Vector2i(x, y))
	_split_sigil()
	_open_img = _open.get_image()
	_find_paper(_open_img)
	_load_pages()
	for i in 2:
		var spread := SubViewport.new()
		spread.transparent_bg = true
		spread.canvas_item_default_texture_filter = Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_NEAREST
		spread.render_target_update_mode = SubViewport.UPDATE_DISABLED
		var canvas := Control.new()
		canvas.draw.connect(_paint_spread.bind(canvas, i))
		spread.add_child(canvas)
		add_child(spread)
		_spreads.append(spread)


## Where the paper is in each column of the open book: the rows a turning leaf is made of.
func _find_paper(img: Image) -> void:
	for x in img.get_width():
		var rows := Vector2i(-1, -1)
		for y in img.get_height():
			var c := img.get_pixel(x, y)
			if c.a > 0.5 and c.get_luminance() >= PAPER_MIN_LUMA:
				rows = Vector2i(y if rows.x < 0 else rows.x, y)
		if rows.y - rows.x > 60: # a page column, not a lit rivet or clasp
			_paper_rows[x] = rows
	while _paper_rows.has(OPEN_SPINE + _leaf_len + 1) or _leaf_len < 3: # the groove at the spine has no paper
		_leaf_len += 1


## Grey box when no player is attached (the old prototype room): the whole word library, each
## word shown at a stage in turn.
func _load_pages() -> void:
	var demo := []
	for lemma in WORDS.lemmas():
		demo.append({"lemma": lemma, "stage": PAGE_STAGES[demo.size() % PAGE_STAGES.size()]})
	sky.build(demo)


## The player's real words (D-078): `known` is lexicon_progress.known_words(), in library order.
## Only met words appear (D-073 rule 2). The view stays where it was if it still exists.
func set_progress(known: Array) -> void:
	sky.build(known)
	_washes.clear()
	if sky.regions.is_empty() or (_level > 1 and sky.node(_level, _path).is_empty()):
		_go(1, [0, 0, 0, 0], 0)
	for level in range(2, _level + 1): # an index may now point past the end
		_path[level - 2] = clampi(_path[level - 2], 0, maxi(0, sky.siblings(level, _path) - 1))
	selected = clampi(selected, 0, maxi(0, sky.children(_level, _path).size() - 1))
	_page = _path[_level - 2] if _level >= 2 else 0
	queue_redraw()


## Opens at `lemma`'s own spread (the book opens there when a word is learned).
func show_word(lemma: String) -> void:
	var path := sky.find(lemma)
	if not path.is_empty():
		_go(SKY.WORD_PAGE, path, 0, false)


## Moves the view. `redraw`: the page is redrawn in front of the player (going closer or back);
## otherwise it is simply there (opening the book at a word).
func _go(level: int, path: Array, choose: int, redraw := true) -> void:
	_prev = {"level": _level, "path": _path.duplicate(), "selected": selected} if redraw else {}
	_level = level
	_path = path.duplicate()
	selected = choose
	_page = _path[_level - 2] if _level >= 2 else 0
	if redraw:
		_sky = 0.0
	queue_redraw()


func zoom_in(choice := -1) -> void:
	if not (is_open and _t >= 1.0 and _turn < 0.0) or _level >= SKY.WORD_PAGE:
		return
	var items := sky.children(_level, _path)
	if items.is_empty():
		return
	var path := _path.duplicate()
	path[_level - 1] = clampi(selected if choice < 0 else choice, 0, items.size() - 1)
	for k in range(_level, 4):
		path[k] = 0
	_go(_level + 1, path, 0)


func zoom_out() -> void:
	if not (is_open and _t >= 1.0 and _turn < 0.0) or _level <= 1:
		return
	_go(_level - 1, _path, _path[_level - 2])


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


## Where the standing book's pages part: the darkest column near the spine in the last tip
## frame, lit over the rows where pages are (a few rows in from their ends).
func _find_seam() -> void:
	if _tip_frames == null:
		return
	var img := _tip_frames.get_image()
	var cell := img.get_width() / OPEN_BOOK.size.x - 1
	var darkest := INF
	for x in range(OPEN_SPINE - 3, OPEN_SPINE + 4):
		var sum := 0.0
		for y in range(40, 90):
			sum += img.get_pixel(cell * OPEN_BOOK.size.x + x, y).get_luminance()
		if sum < darkest:
			darkest = sum
			_seam_x = x
	var top := -1
	var bottom := -1
	for y in OPEN_BOOK.size.y:
		var c := img.get_pixel(cell * OPEN_BOOK.size.x + _seam_x - 2, y)
		if c.a > 0.5 and c.get_luminance() > 0.35: # page paper, not the cover's dark edge
			if top < 0:
				top = y
			bottom = y
	if top >= 0:
		_seam_y = Vector2i(top + 2, bottom - 2)


## Splits the sigil into its ring and what is inside it (triangle and dot). The ring is the
## outermost stroke in every direction from the centre: a pixel within 3 px of the farthest lit
## pixel at its angle belongs to it. (A plain distance cut fails: the hand-drawn ring is thicker
## at the top than the triangle's corners are far from the centre, and the corners touch the
## ring, so it is not a separate stroke either.) The ring is ordered clockwise from the top.
func _split_sigil() -> void:
	var lo := Vector2(INF, INF)
	var hi := -lo
	for p in _sigil:
		lo = lo.min(Vector2(p))
		hi = hi.max(Vector2(p))
	var centre := (lo + hi) / 2.0
	const BINS := 48
	var turn := func(p: Vector2i) -> float: # 0 at the top, growing clockwise on screen
		var d := Vector2(p) - centre
		return fposmod(atan2(d.x, -d.y), TAU)
	var bin := func(p: Vector2i) -> int:
		return int(turn.call(p) / TAU * BINS) % BINS
	var farthest := []
	farthest.resize(BINS)
	farthest.fill(0.0)
	for p in _sigil:
		farthest[bin.call(p)] = maxf(farthest[bin.call(p)], (Vector2(p) - centre).length())
	_sigil_core.clear()
	_sigil_ring.clear()
	for p in _sigil:
		var b: int = bin.call(p)
		var edge := maxf(farthest[b], maxf(farthest[(b + BINS - 1) % BINS], farthest[(b + 1) % BINS]))
		if (Vector2(p) - centre).length() >= edge - 3.0:
			_sigil_ring.append(p)
		else:
			_sigil_core.append(p)
	_sigil_ring.sort_custom(func(a, b): return turn.call(a) < turn.call(b))


## Splits the constellation's pixels into stars and lines. Stars are the knots: pixels with four
## or more lit neighbours, grown by two pixels to take in their points. What is left falls into
## lines; each is ordered outwards from the star nearer the spine.
func _clean(file: String, derived: Image) -> Texture2D:
	var path := ProjectSettings.globalize_path(CLEAN_DIR + file)
	return ImageTexture.create_from_image(Image.load_from_file(path) if FileAccess.file_exists(path) else derived)


func toggle() -> void:
	is_open = not is_open
	if not is_open:
		_rite = -1.0
		_rite_lemma = ""
	open_changed.emit(is_open)


## A word just became USABLE: open at its page and play its ceremony (see RITE_START).
func ceremony(lemma: String, skippable := true) -> void:
	show_word(lemma)
	_rite_lemma = lemma
	_rite = 0.0
	_rite_clock = 0.0
	_hold = 0.0
	_skippable = skippable
	if not is_open:
		toggle()


func in_ceremony() -> bool:
	return _rite >= 0.0


func skip_ceremony() -> void:
	if is_open:
		toggle()


func _rite_letters() -> float:
	return RITE_START + _rite_lemma.length() * RITE_LETTER + 0.4


func _rite_end() -> float:
	return _rite_letters() + RITE_CARD + RITE_HOLD


## A / D: turn to the next or the previous spread (none before the first).
func turn_page(forward: bool) -> void:
	if not (is_open and _t >= 1.0 and _turn < 0.0) or _level < 2 or (not forward and _page == 0) \
			or (forward and _page >= sky.siblings(_level, _path) - 1):
		return
	_turn_from = _page
	_page += 1 if forward else -1
	_turn_back = not forward
	_turn = 0.0
	if live_turn:
		_spread_page = [_turn_from, _page]
		# Painted at the window's real resolution, not the game's 960x540: text drawn small and
		# then enlarged would blur next to the sharp text of the open book.
		var stretch := maxf(1.0, get_viewport().get_final_transform().get_scale().x)
		_spread_unit = pixel * book_scale * stretch
		for spread in _spreads:
			spread.size = Vector2i((Vector2(OPEN_BOOK.size) * _spread_unit).round())
			spread.render_target_update_mode = SubViewport.UPDATE_ALWAYS
			spread.get_child(0).queue_redraw()
		_warm = 2
	queue_redraw()


## The path shown on spread `page` of the current level: the same, with the last step turned.
func _path_at(page: int) -> Array:
	var path := _path.duplicate()
	if _level >= 2:
		path[_level - 2] = page
	return path


func set_open_now(open: bool) -> void:
	is_open = open
	_t = 1.0 if open else 0.0
	queue_redraw()


func _process(delta: float) -> void:
	_time += delta
	if _rite >= 0.0:
		_rite_clock += delta
		var holding := _skippable and _rite_clock > SKIP_HINT_AFTER \
				and (Input.is_physical_key_pressed(KEY_SPACE) or Input.is_physical_key_pressed(KEY_ESCAPE))
		_hold = _hold + delta if holding else maxf(0.0, _hold - delta * 2.0)
		if _hold >= SKIP_HOLD:
			skip_ceremony()
	# The rise stage and the rest run at their own speeds, so either can be tuned alone.
	var in_rise := _t < P_RISE or (_t == P_RISE and not is_open)
	var seconds: float = ((OPEN_RISE if is_open else CLOSE_RISE) if in_rise else (OPEN_REST if is_open else CLOSE_REST)) * PACE[speed]
	var share := P_RISE if in_rise else 1.0 - P_RISE
	if _turn >= 0.0:
		if _warm > 0:
			_warm -= 1 # the hidden spreads paint first, so the leaf never shows an empty frame
		else:
			_turn += delta / ((LIVE_TURN_TIME * PACE[speed]) if live_turn else TURN_TIME)
		if _turn >= 1.0:
			_turn = -1.0
			_path = _path_at(_page) # the page has landed: it is what is looked at now
			selected = 0
			_prev = {}
			for spread in _spreads:
				spread.render_target_update_mode = SubViewport.UPDATE_DISABLED
		else:
			for spread in _spreads:
				spread.get_child(0).queue_redraw()
		queue_redraw()
	if is_open and _t >= 1.0 and _turn < 0.0:
		_sky += delta
		if _rite >= 0.0:
			_rite += delta
			if _rite >= _rite_end():
				toggle() # the word is in the bar: the book closes by itself
	elif _t < P_FALL:
		_sky = 0.0
	var was := _t
	_t = move_toward(_t, 1.0 if is_open else 0.0, delta * share / seconds)
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
	elif event.keycode == KEY_V:
		live_turn = not live_turn
	elif is_open and event.keycode in [KEY_W, KEY_UP, KEY_S, KEY_DOWN]:
		var count := maxi(1, sky.children(_level, _path).size())
		selected = (selected + (count - 1 if event.keycode in [KEY_W, KEY_UP] else 1)) % count
	elif is_open and event.keycode in [KEY_E, KEY_ENTER, KEY_KP_ENTER]:
		zoom_in()
	elif is_open and event.keycode in [KEY_Q, KEY_BACKSPACE]:
		zoom_out()
	elif is_open and event.keycode in [KEY_A, KEY_D, KEY_LEFT, KEY_RIGHT]:
		turn_page(event.keycode in [KEY_D, KEY_RIGHT])
	else:
		return
	get_viewport().set_input_as_handled()
	queue_redraw()


## The mouse: a click on something on the left page goes closer to it, a right click goes back.
func _input(event: InputEvent) -> void:
	if not (event is InputEventMouseButton and event.pressed and is_open and _t >= 1.0 and _rite < 0.0):
		return
	if event.button_index == MOUSE_BUTTON_RIGHT:
		zoom_out()
	elif event.button_index == MOUSE_BUTTON_LEFT:
		var at := get_local_mouse_position()
		for hit in _hits:
			if hit[0].has_point(at):
				selected = hit[1]
				zoom_in(hit[1])
				break
	else:
		return
	get_viewport().set_input_as_handled()


## 0..1 progress through the stage that runs from a to b.
func _stage(a: float, b: float) -> float:
	return clampf((_t - a) / (b - a), 0.0, 1.0)


func _draw() -> void:
	_ci = self
	if _t <= 0.0:
		return
	var rise_t := ease(_stage(0.0, P_RISE), -2.0)
	_ci.draw_rect(screen_rect, Color(0.02, 0.02, 0.04, 0.62 * ease(_stage(0.0, P_SIGIL), -2.0)))
	if _rite >= 0.0 and _skippable:
		_draw_skip_hint()

	var unit := pixel * book_scale # window pixels per book pixel
	var size := Vector2(OPEN_BOOK.size) * unit
	var lift := roundi((1.0 - rise_t) * RISE) * pixel # moves on the native grid
	# Every stage shares one 256x128 frame whose centre line is the spine.
	var origin := (screen_rect.position + (screen_rect.size - size) / 2.0).snapped(Vector2(pixel, pixel)) + Vector2(0, lift)
	var tip := _stage(P_SIGIL, P_TIP)
	var fall := _stage(P_TIP, P_FALL)

	if tip <= 0.0:
		var at := origin + Vector2(OPEN_SPINE - CLOSED_BOOK.size.x / 2, 0) * unit
		_ci.draw_texture_rect(_closed, Rect2(at, Vector2(CLOSED_BOOK.size) * unit), false, Color(1, 1, 1, minf(1.0, rise_t * 2.0)))
		# The sigil wakes: a flash that settles into a steady glow.
		# The sigil wakes: the triangle and its dot light together, then the ring draws itself
		# clockwise from the top like a pen going round, and the whole sigil flares as it closes.
		var wake := _stage(P_RISE, P_SIGIL)
		if wake > 0.0:
			var core := clampf(wake / 0.22, 0.0, 1.0)
			var ring := clampf((wake - 0.25) / 0.6, 0.0, 1.0)
			var close_flash := clampf(1.0 - absf(wake - 0.9) / 0.08, 0.0, 1.0)
			_draw_pixels(_sigil_core, at, unit, CYAN.lerp(Color.WHITE, 0.4 * sin(core * PI)), core, 0.22 + 0.3 * sin(core * PI) + 0.3 * close_flash)
			var drawn: Array[Vector2i] = []
			drawn.assign(_sigil_ring.slice(0, ceili(ring * _sigil_ring.size())))
			_draw_pixels(drawn, at, unit, CYAN, 1.0, 0.22 + 0.3 * close_flash)
			if ring > 0.0 and ring < 1.0: # the pen's tip
				var tip_px: Array[Vector2i] = []
				tip_px.assign(drawn.slice(maxi(0, drawn.size() - 4)))
				_draw_pixels(tip_px, at, unit, Color.WHITE, 1.0, 0.5)
	elif fall <= 0.0:
		if _tip_frames:
			_draw_frame(_tip_frames, tip, origin, size)
			if tip * (_tip_frames.get_width() / OPEN_BOOK.size.x) < 1.0: # still the cover: keep it lit
				_draw_pixels(_sigil, origin + Vector2(OPEN_SPINE - CLOSED_BOOK.size.x / 2, 0) * unit, unit, CYAN, 1.0, 0.22)
		else: # grey box: the cover turns away about the spine, narrowing to the standing book
			var w := maxi(14, roundi(COVER_W * cos(tip * PI / 2.0)))
			_box(origin, unit, OPEN_SPINE - w / 2, w, LEATHER)
			if w < 40:
				_box(origin, unit, OPEN_SPINE - w / 2 + 3, w - 6, PAPER.darkened(0.25))
		# The seam only exists once the book stands: before that x 128 is the middle of the cover.
		_seam(origin, unit, (tip - 0.67) / 0.33)
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
		_seam(origin, unit, 1.0 - fall, fall)
	elif _turn >= 0.0 and live_turn and _warm == 0:
		_draw_leaf(origin, unit)
		_draw_tabs(origin, unit, 1.0)
		_draw_caption(origin, unit, 1.0)
		return
	elif _turn >= 0.0 and not live_turn and _turn_frames:
		_draw_frame(_turn_frames, 1.0 - _turn if _turn_back else _turn, origin, size)
		return
	else:
		_ci.draw_texture_rect(_open, Rect2(origin, size), false)

	if fall < 1.0:
		return
	var page := _turn_from if _turn >= 0.0 else _page # still warming up: the old spread
	_paint_pages(origin, unit, page, _sky, _stage(P_FALL, 1.0), _stage(0.88, 1.0))
	_draw_tabs(origin, unit, _stage(0.88, 1.0))
	if _rite >= 0.0:
		_draw_rite_card(origin, unit)
	else:
		_draw_caption(origin, unit, _stage(0.88, 1.0))


## Everything printed on a spread: the right page's paper, then the view of `page` (a sibling on
## the current level). While the page is being redrawn the old view fades first.
func _paint_pages(origin: Vector2, unit: float, page: int, sky_clock: float, sky_fade: float, e: float) -> void:
	_ci.draw_rect(Rect2(origin + Vector2(RIGHT_PAGE.position) * unit, Vector2(RIGHT_PAGE.size) * unit), PAPER)
	if _ci == self:
		_hits.clear()
	var wiping: bool = not _prev.is_empty() and sky_clock < WIPE * PACE[speed]
	if wiping:
		_draw_view(origin, unit, _prev.level, _prev.path, _prev.selected, 99.0, e * (1.0 - sky_clock / (WIPE * PACE[speed])))
	var clock: float = sky_clock - (WIPE * 0.6 * PACE[speed] if not _prev.is_empty() else 0.0)
	_draw_view(origin, unit, _level, _path_at(page), selected, clock / PACE[speed], e * sky_fade)


## One hidden spread, painted at the size it shows on screen: [0] the spread turned from, [1] the
## one turned to.
func _paint_spread(canvas: Control, which: int) -> void:
	_ci = canvas
	var unit := _spread_unit
	_ci.draw_texture_rect(_open, Rect2(Vector2.ZERO, Vector2(OPEN_BOOK.size) * unit), false)
	_paint_pages(Vector2.ZERO, unit, _spread_page[which], 99.0, 1.0, 1.0) # a turned page is already written
	_ci = self


## The leaf turning, from the spread turned from (A) to the spread turned to (B). On the side it
## leaves, B already shows underneath; on the side it heads for, A shows until the leaf covers it.
## The leaf is the paper columns of A's page on its front and of B's facing page on its back.
## Each column turns about the spine by its own angle: the free edge leads, the spine side trails,
## so the paper bends. Columns are placed on whole book pixels and drawn nearest the eye last.
func _draw_leaf(origin: Vector2, unit: float) -> void:
	var a := _spreads[0].get_texture()
	var b := _spreads[1].get_texture()
	var from := -1 if _turn_back else 1 # the side the leaf leaves: +1 right (D), -1 left (A)
	var pivot := OPEN_SPINE + 0.5
	var split := OPEN_SPINE if from > 0 else OPEN_SPINE + 1
	var w := OPEN_BOOK.size.x
	var h := OPEN_BOOK.size.y
	var b_part := Rect2i(split, 0, w - split, h) if from > 0 else Rect2i(0, 0, split, h)
	var a_part := Rect2i(0, 0, split, h) if from > 0 else Rect2i(split, 0, w - split, h)
	for part in [[b, b_part], [a, a_part]]:
		var r: Rect2i = part[1]
		_ci.draw_texture_rect_region(part[0], Rect2(origin + Vector2(r.position) * unit, Vector2(r.size) * unit), Rect2(Vector2(r.position) * _spread_unit, Vector2(r.size) * _spread_unit))

	var edge := PI * smoothstep(0.0, 1.0 - LEAF_LAG, _turn) # angle of the free edge
	var root := PI * smoothstep(LEAF_LAG, 1.0, _turn) # angle at the spine
	var angle := func(u: float) -> float: return lerpf(root, edge, pow(u / _leaf_len, 1.3))
	# Where each column boundary lands (distance from the spine along the book) and how high it is.
	var along: Array[float] = [0.5 * cos(angle.call(0.25))]
	var height: Array[float] = [0.5 * sin(angle.call(0.25))]
	for d in range(1, _leaf_len + 1):
		along.append(along[d - 1] + cos(angle.call(d)))
		height.append(height[d - 1] + sin(angle.call(d)))
	var columns := []
	for d in range(1, _leaf_len + 1):
		var x0 := roundi(pivot + from * along[d - 1])
		var x1 := roundi(pivot + from * along[d])
		if x0 == x1:
			continue
		var front := (x1 - x0) * from > 0
		var source := OPEN_SPINE + from * d if front else OPEN_SPINE - from * d
		if not _paper_rows.has(source):
			continue
		var rows: Vector2i = _paper_rows[source]
		var shade := 1.0 - LEAF_SHADE * absf(sin(angle.call(d)))
		columns.append([(height[d - 1] + height[d]) / 2.0, mini(x0, x1), absi(x1 - x0), source, rows, a if front else b, shade])
	columns.sort_custom(func(p, q): return p[0] < q[0])

	# The leaf's shadow on the page beyond its free edge, deepest while it stands highest.
	var edge_x := roundi(pivot + from * along[_leaf_len])
	var side := signi(edge_x - OPEN_SPINE) if edge_x != OPEN_SPINE else from
	var depth := sin(edge)
	for band in 3:
		var reach := roundi((2.0 + 7.0 * depth) * (band + 1) / 3.0)
		for x in range(edge_x, edge_x + side * reach, side):
			if _paper_rows.has(x):
				var rows: Vector2i = _paper_rows[x]
				_ci.draw_rect(Rect2(origin + Vector2(x, rows.x) * unit, Vector2(1, rows.y - rows.x + 1) * unit), Color(0.12, 0.07, 0.04, 0.12 * depth))

	for c in columns:
		var rows: Vector2i = c[4]
		var lift := roundi(c[0] * LEAF_LIFT)
		var src := Rect2(Vector2(c[3], rows.x) * _spread_unit, Vector2(1, rows.y - rows.x + 1) * _spread_unit)
		var dst := Rect2(origin + Vector2(c[1], rows.x - lift) * unit, Vector2(c[2], rows.y - rows.x + 1) * unit)
		# Old paper in shade goes brown, not grey: blue falls off fastest, green a little faster than red.
		_ci.draw_texture_rect_region(c[5], dst, src, Color(c[6], pow(c[6], 1.25), pow(c[6], 1.7)))


# --- The sky on the pages (D-088) -----------------------------------------------------------------

## One level of the sky, `clock` seconds into being drawn: the washes seep in, the stars appear
## one by one, the lines draw themselves, the words come with the washes. `e`: opacity.
func _draw_view(origin: Vector2, unit: float, level: int, path: Array, choice: int, clock: float, e: float) -> void:
	if e <= 0.0:
		return
	var shown := clampf((clock - 0.15) / 0.5, 0.0, 1.0) * e
	var right := Vector2(RIGHT_PAGE.position.x + 6, 24)
	if sky.regions.is_empty():
		_text(origin, unit, right, "The sky", 7.5, INK, shown)
		_text(origin, unit, right + Vector2(0, 9), "No words yet.", 4.2, PENCIL, shown)
		return
	_draw_crumbs(origin, unit, level, path, shown)
	if level == SKY.WORD_PAGE:
		_draw_word_page(origin, unit, path, clock, e, shown)
		return
	var items := sky.children(level, path)
	var points := sky.layout(level, path)
	_ci.draw_texture_rect(_wash(level, path, points), Rect2(origin, Vector2(OPEN_BOOK.size) * unit), false, Color(1, 1, 1, clampf(clock / WASH_IN, 0.0, 1.0) * e))
	var lines_from := 0.3 + items.size() * STAR_GAP
	if level == 4: # the constellation itself: a star for each word, joined in order
		for i in items.size():
			if i > 0:
				_link(origin, unit, points[i - 1], points[i], items[i - 1].stage, items[i].stage, (clock - lines_from - (i - 1) * LINE_TIME * 0.6) / LINE_TIME, e)
		for i in items.size():
			_star(origin, unit, points[i], str(items[i].stage), clock - 0.3 - i * STAR_GAP, e)
			_word_label(origin, unit, points[i] + Vector2(3, 2), str(items[i].lemma), str(items[i].stage), 4.6, shown, i == choice)
	else: # each thing as a small figure (its best-known constellation) with its name under it
		for i in items.size():
			var best := SKY.brightest(items[i])
			var words: Array = best.words.slice(0, 5)
			var figure := SKY.figure(str(best.id), words.size(), points[i] + Vector2(0, -2), 6.0)
			var born := 0.3 + i * STAR_GAP * 2.0
			for k in range(1, words.size()):
				_link(origin, unit, figure[k - 1], figure[k], words[k - 1].stage, words[k].stage, (clock - born - 0.2 - k * 0.1) / LINE_TIME, e)
			for k in words.size():
				_star(origin, unit, figure[k], str(words[k].stage), clock - born - k * 0.05, e)
			var name := str(items[i].get("name", items[i].get("id", "")))
			_text(origin, unit, points[i] + Vector2(0, 9), name, 4.2, INK if i == choice else PENCIL, shown * (1.0 if i == choice else 0.85), true, i == choice)
	if _ci == self:
		for i in points.size():
			var box := Rect2(points[i] - Vector2(10, 8), Vector2(20, 20)) if level < 4 else Rect2(points[i] - Vector2(3, 5), Vector2(30, 9))
			_hits.append([Rect2(origin + box.position * unit, box.size * unit), i])
	_draw_about(origin, unit, level, path, items, choice, right, shown)


## The right page: what is being looked at, and what is in it.
func _draw_about(origin: Vector2, unit: float, level: int, path: Array, items: Array, choice: int, at: Vector2, a: float) -> void:
	var here := sky.node(level, path)
	match level:
		1:
			_text(origin, unit, at, "The sky", 7.5, INK, a)
			_text(origin, unit, at + Vector2(0, 8), "%d of %d regions found" % [items.size(), sky.total_regions()], 4.2, PENCIL, a)
		2, 3:
			_text(origin, unit, at, str(here.name), 7.5, INK, a)
			var kind := "clusters" if level == 2 else "constellations"
			_text(origin, unit, at + Vector2(0, 8), "%d of %d %s found" % [items.size(), here.total, kind], 4.2, PENCIL, a)
		4:
			_text(origin, unit, at, str(here.id), 7.5, INK, a)
			_text(origin, unit, at + Vector2(0, 8), _count(items.size(), "star"), 4.2, PENCIL, a)
			_draw_preview(origin, unit, items[clampi(choice, 0, items.size() - 1)], at + Vector2(0, 20), a)
			return
	var y := at.y + 18
	for i in items.size():
		if y > 96:
			break
		var item: Dictionary = items[i]
		var count := ""
		match level:
			1: count = _count(SKY.words_in(item).size(), "word")
			2: count = _count(item.constellations.size(), "constellation")
			3:
				var usable := SKY.words_in(item).filter(func(w): return w.stage == "USABLE").size()
				count = _count(item.words.size(), "star") + (", %d usable" % usable if usable > 0 else "")
		_text(origin, unit, Vector2(at.x, y), "%s  ·  %s" % [item.get("name", item.get("id", "")), count], 4.4, INK if i == choice else PENCIL, a, false, i == choice)
		y += 6.5
	if y < 92:
		_text(origin, unit, Vector2(at.x, 99), "the ink is darker where you know more", 3.6, PENCIL, a * 0.8)


## A constellation's chosen word, on the right page: as far as the player knows it.
func _draw_preview(origin: Vector2, unit: float, word: Dictionary, at: Vector2, a: float) -> void:
	var lemma := str(word.lemma)
	var stage := str(word.stage)
	_word_label(origin, unit, at + Vector2(0, 6), lemma, stage, 8.0, a)
	_text(origin, unit, at + Vector2(0, 12), STAGE_NAMES.get(stage, ""), 3.8, PENCIL, a)
	var y := at.y + 20
	if stage in ["UNDERSTOOD", "USABLE"]:
		for row in _wrap(WORDS.sense(lemma), 4.6, unit, 84):
			_text(origin, unit, Vector2(at.x, y), row, 4.6, INK, a)
			y += 6
	var met: Dictionary = progress.met_at(lemma, stage) if progress else {}
	if not met.is_empty():
		y += 2
		for row in _wrap("“%s”" % str(met.line).replace("[", "").replace("]", ""), 4.2, unit, 84):
			_text(origin, unit, Vector2(at.x, y), row, 4.2, PENCIL, a)
			y += 5.5
	_text(origin, unit, Vector2(at.x, 99), "E  open the page", 3.8, PENCIL, a * 0.8)


## One word, its own spread: the word as far as it is known, how it sounds, what it means, how far
## along it is; on the right, every sentence it was met in (the page slips, D-086) and its neighbours.
func _draw_word_page(origin: Vector2, unit: float, path: Array, clock: float, e: float, a: float) -> void:
	var word := sky.node(SKY.WORD_PAGE, path)
	var lemma := str(word.lemma)
	var stage := str(word.stage)
	var known := stage in ["UNDERSTOOD", "USABLE"]
	var size := 13.0
	var at := Vector2(34, 46)
	if _rite >= 0.0 and lemma == _rite_lemma:
		var px := _font_px(size, unit)
		_draw_lighting(origin + at * unit, {"word": lemma, "note": ""}, px, px, 0.0, unit, a)
		if _ci == self:
			_rite_from = origin + (at + Vector2(FONT.get_string_size(lemma, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x / unit / 2.0, -4)) * unit
	else:
		_word_label(origin, unit, at, lemma, stage, size, a)
	var dictionary := WORDS.dictionary(lemma)
	var sound := str(dictionary.get("phonetic", {}).get("uk", ""))
	var pos := str(WORDS.main_sense(lemma).get("pos", ""))
	var px := _font_px(4.0, unit)
	var line := ("/%s/   " % sound if sound else "") + pos
	if stage != "ENCOUNTERED": # only seen: nothing about it is known yet, not even how it sounds
		_ci.draw_string(_sounds, origin + (at + Vector2(0, 8)) * unit, line, HORIZONTAL_ALIGNMENT_LEFT, -1, px, Color(PENCIL, a))
	var y := at.y + 16
	if known:
		for row in _wrap(WORDS.sense(lemma), 5.0, unit, 80):
			_text(origin, unit, Vector2(at.x, y), row, 5.0, INK, a)
			y += 6.5
	var track := SKY.STAGES.find(stage)
	var x := at.x
	for k in range(1, 5): # seen · recognized · understood · usable, the reached ones in ink
		var name: String = STAGE_NAMES[SKY.STAGES[k]]
		_text(origin, unit, Vector2(x, 82), name, 3.6, INK if k <= track else PENCIL, a * (1.0 if k <= track else 0.45))
		x += FONT.get_string_size(name + "  ·  ", HORIZONTAL_ALIGNMENT_LEFT, -1, _font_px(3.6, unit)).x / unit
	if known:
		y = 90
		for row in _wrap(WORDS.page_line(lemma), 4.2, unit, 80):
			_text(origin, unit, Vector2(at.x, y), row, 4.2, INK, a * 0.9)
			y += 5.5
	# Its star, small, in the corner: where it is in the sky. In a ceremony it is the last to light.
	var star_stage := stage
	var star_age := clock - 0.4
	if _rite >= 0.0 and lemma == _rite_lemma:
		star_age = _rite - _rite_letters() - RITE_CARD * 0.6
		star_stage = "USABLE" if star_age >= 0.0 else "UNDERSTOOD"
	_star(origin, unit, Vector2(110, 25), star_stage, star_age, e)

	var right := Vector2(RIGHT_PAGE.position.x + 6, 24)
	_text(origin, unit, right, "Where you met it", 6.0, INK, a)
	y = right.y + 8
	var met: Dictionary = progress.meetings.get(lemma, {}) if progress else {}
	if met.is_empty():
		_text(origin, unit, Vector2(right.x, y), "Not written down yet.", 4.2, PENCIL, a)
		y += 7
	for s in SKY.STAGES:
		if not met.has(s) or y > 72:
			continue
		for row in _wrap("“%s”" % str(met[s].line).replace("[", "").replace("]", ""), 4.2, unit, 84):
			_text(origin, unit, Vector2(right.x, y), row, 4.2, INK, a * 0.9)
			y += 5.5
		_text(origin, unit, Vector2(right.x, y), "— " + str(met[s].where), 3.4, PENCIL, a)
		y += 7.5
	var near: Array = sky.node(4, path).words.filter(func(w): return w.lemma != lemma).map(func(w): return str(w.lemma))
	if not near.is_empty():
		_text(origin, unit, Vector2(right.x, 84), "Near it", 5.0, INK, a)
		_text(origin, unit, Vector2(right.x, 91), _fit("  ·  ".join(near), _font_px(4.0, unit), 84 * unit), 4.0, PENCIL, a)
	var confused: Array = WORDS.main_sense(lemma).get("confusable", [])
	if known and not confused.is_empty():
		var names: Array = confused.map(func(c): return str(c).get_slice("（", 0).strip_edges())
		_text(origin, unit, Vector2(right.x, 99), "easily confused: " + ", ".join(names), 3.4, PENCIL, a * 0.85)


## Top left of the left page: where in the sky you are.
func _draw_crumbs(origin: Vector2, unit: float, level: int, path: Array, a: float) -> void:
	var parts := ["sky"]
	for l in range(2, level + 1):
		var item := sky.node(l, path)
		parts.append(str(item.get("name", item.get("id", item.get("lemma", "")))))
	_text(origin, unit, Vector2(32, 19), "  ›  ".join(parts), 3.4, PENCIL, a * 0.9)


## The ink washes of a view: one pale stain of ink per thing on the page, darker the better it is
## known, in the book's own pixels and only on paper. Made once per view.
func _wash(level: int, path: Array, points: Array[Vector2]) -> Texture2D:
	var key := "%d %s" % [level, str(path.slice(0, level - 1))]
	if _washes.has(key):
		return _washes[key]
	var img := Image.create(OPEN_BOOK.size.x, OPEN_BOOK.size.y, false, Image.FORMAT_RGBA8)
	var spots := [] # [centre, radius, density, seed]
	var items := sky.children(level, path)
	if level == 4:
		var here := sky.node(4, path)
		spots.append([SKY.PAGE.get_center(), 34.0, 0.12 + 0.3 * SKY.light(here), hash(str(here.id))])
	else:
		for i in items.size():
			spots.append([points[i] + Vector2(0, -2), 11.0 if level == 1 else 10.0, 0.12 + 0.55 * SKY.light(items[i]), hash(str(items[i].get("name", ""))) % 100000])
	for spot in spots:
		var c: Vector2 = spot[0]
		var r: float = spot[1]
		var rng := RandomNumberGenerator.new()
		rng.seed = spot[3]
		var k := [rng.randf() * TAU, rng.randf() * TAU]
		for y in range(int(c.y - r * 1.3), int(c.y + r * 1.3) + 1):
			for x in range(int(c.x - r * 1.5), int(c.x + r * 1.5) + 1):
				if x < 1 or y < 1 or x >= OPEN_SPINE - 2 or y >= img.get_height():
					continue
				var paper := _open_img.get_pixel(x, y)
				if paper.a < 0.5 or paper.get_luminance() < PAPER_MIN_LUMA:
					continue
				var angle := atan2(y - c.y, x - c.x)
				var d := Vector2((x - c.x) / 1.3, y - c.y).length()
				var edge: float = r * (1.0 + 0.18 * sin(3.0 * angle + k[0]) + 0.1 * sin(5.0 * angle + k[1]))
				if d > edge:
					continue
				var density: float = spot[2] * minf(1.0, (1.0 - d / edge) * 2.2)
				if float(hash(x * 7919 + y * 104729 + spot[3]) & 0xffff) / 65535.0 < density * 0.9:
					img.set_pixel(x, y, Color(paper.r * WASH_SHADE, paper.g * WASH_SHADE, paper.b * WASH_SHADE * 0.98))
	_washes[key] = ImageTexture.create_from_image(img)
	return _washes[key]


## A star: one book pixel, as far as its word is known (seen faint pencil, recognized pencil,
## understood ink, usable cyan with a glow). `age`: seconds since it appeared (it flares, cyan).
func _star(origin: Vector2, unit: float, at: Vector2, stage: String, age: float, e: float) -> void:
	if age < 0.0:
		return
	var a := e * clampf(age / 0.15, 0.0, 1.0)
	var p := Vector2i(at)
	match stage:
		"USABLE":
			var flare := clampf(1.0 - age / STAR_FLASH, 0.0, 1.0)
			_draw_pixels([p], origin, unit, CYAN.lerp(Color.WHITE, 0.5 * flare), a, 0.22 + 0.4 * flare)
		"UNDERSTOOD":
			_ci.draw_rect(Rect2(origin + Vector2(p) * unit, Vector2(unit, unit)), Color(INK, a))
		"RECOGNIZED":
			_ci.draw_rect(Rect2(origin + Vector2(p) * unit, Vector2(unit, unit)), Color(PENCIL, a))
		_:
			_ci.draw_rect(Rect2(origin + Vector2(p) * unit, Vector2(unit, unit)), Color(PENCIL, 0.45 * a))


## A line between two stars, drawn as far as the less known of the two: a seen word is not joined
## yet, pencil dashes, ink, cyan. `progress` 0..1: how far it has drawn itself.
func _link(origin: Vector2, unit: float, from: Vector2, to: Vector2, stage_a: String, stage_b: String, progress: float, e: float) -> void:
	var low := mini(SKY.STAGES.find(stage_a), SKY.STAGES.find(stage_b))
	if low <= 1 or progress <= 0.0:
		return
	var n := maxi(absi(int(to.x - from.x)), absi(int(to.y - from.y)))
	var points: Array[Vector2i] = []
	for k in range(1, n):
		if k > progress * n:
			break
		if low == 2 and (k / 2) % 2 == 1:
			continue
		points.append(Vector2i(from.lerp(to, k / float(n)).round()))
	if low == 4:
		_draw_pixels(points, origin, unit, CYAN.darkened(0.15), 0.9 * e, 0.1)
		return
	for p in points:
		_ci.draw_rect(Rect2(origin + Vector2(p) * unit, Vector2(unit, unit)), Color(INK if low == 3 else PENCIL, e))


## A word written as far as it is known (the book's own hands: rubbed out, pencil, ink, cyan).
func _word_label(origin: Vector2, unit: float, at: Vector2, lemma: String, stage: String, size: float, a: float, chosen := false) -> void:
	var px := _font_px(size, unit)
	var spot := origin + at * unit
	match stage:
		"ENCOUNTERED": _rubbed_out(spot, lemma, px, a, unit)
		"RECOGNIZED": _pencil(spot, lemma, px, a, unit)
		"UNDERSTOOD": _ci.draw_string(FONT, spot, lemma, HORIZONTAL_ALIGNMENT_LEFT, -1, px, Color(INK, a))
		_:
			var glow := 0.18 + 0.06 * sin(_time * 1.6)
			for o in [Vector2(-1, 0), Vector2(1, 0), Vector2(0, -1), Vector2(0, 1)]:
				_ci.draw_string(FONT, spot + o * unit * 0.6, lemma, HORIZONTAL_ALIGNMENT_LEFT, -1, px, Color(CYAN, glow * a))
			_ci.draw_string(FONT, spot, lemma, HORIZONTAL_ALIGNMENT_LEFT, -1, px, Color(CYAN.darkened(0.25), a))
	if chosen:
		var w := FONT.get_string_size(lemma, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
		_ci.draw_rect(Rect2(spot + Vector2(0, unit), Vector2(w, unit * 0.5)), Color(INK, 0.7 * a))


## Text at a place in book pixels, its size in book pixels; `centred` on x; `chosen` underlined.
func _text(origin: Vector2, unit: float, at: Vector2, text: String, size: float, color: Color, a: float, centred := false, chosen := false) -> void:
	if a <= 0.0 or text.is_empty():
		return
	var px := _font_px(size, unit)
	var w := FONT.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
	var spot := origin + at * unit - Vector2(w / 2.0 if centred else 0.0, 0)
	_ci.draw_string(FONT, spot, text, HORIZONTAL_ALIGNMENT_LEFT, -1, px, Color(color, color.a * a))
	if chosen:
		_ci.draw_rect(Rect2(spot + Vector2(0, unit), Vector2(w, unit * 0.5)), Color(INK, 0.7 * a))


static func _count(n: int, thing: String) -> String:
	return "%d %s%s" % [n, thing, "" if n == 1 else "s"]


## Lines of `text` no wider than `width` book pixels.
func _wrap(text: String, size: float, unit: float, width: float) -> Array[String]:
	var px := _font_px(size, unit)
	var rows: Array[String] = []
	var row := ""
	for word in text.split(" "):
		var trial := word if row.is_empty() else row + " " + word
		if not row.is_empty() and FONT.get_string_size(trial, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x > width * unit:
			rows.append(row)
			row = word
		else:
			row = trial
	if not row.is_empty():
		rows.append(row)
	return rows


## Cloth bookmarks tucked in at the top of the right page: find, recent, review, stage
## (D-073 quick ways in; drawn, not working yet).
func _draw_tabs(origin: Vector2, unit: float, e: float) -> void:
	if e <= 0.0:
		return
	for i in TABS.size():
		var x := 146 + i * 17
		var color: Color = TABS[i][1]
		_ci.draw_rect(Rect2(origin + Vector2(x, -5) * unit, Vector2(14, 20) * unit), Color(color, e))
		for side in [0, 13]:
			_ci.draw_rect(Rect2(origin + Vector2(x + side, -5) * unit, Vector2(1, 20) * unit), Color(color.darkened(0.25), e))
		_ci.draw_rect(Rect2(origin + Vector2(x + 6, -5) * unit, Vector2(2, 1) * unit), Color(0, 0, 0, 0.35 * e)) # the notch
		_text(origin, unit, Vector2(x + 7, 3), TABS[i][0], 3.2, Color8(235, 224, 206), e * 0.9, true)


## One cell of a 256x128 strip, picked by 0..1 progress.
func _draw_frame(strip: Texture2D, progress: float, origin: Vector2, size: Vector2) -> void:
	var count := strip.get_width() / OPEN_BOOK.size.x
	var frame := mini(int(progress * count), count - 1)
	_ci.draw_texture_rect_region(strip, Rect2(origin, size), Rect2(frame * OPEN_BOOK.size.x, 0, OPEN_BOOK.size.x, OPEN_BOOK.size.y))


## Grey box: a full-height band of the book, x and width in book pixels.
func _box(origin: Vector2, unit: float, x: int, w: int, color: Color) -> void:
	_ci.draw_rect(Rect2(origin + Vector2(x, BOOK_TOP) * unit, Vector2(w, BOOK_BOTTOM - BOOK_TOP) * unit), color)


## Light from inside the standing book, leaking through the seam between its pages: language
## waking inside it. Not a flat bar: brightest at the middle and dying out towards the ends,
## a slow shimmer running up it, the page edges either side catching some of it, a soft halo
## (lighting may be smooth; the seam itself stays whole pixels) and a few motes drifting up out
## of it. `spread` widens the halo as the covers fall open.
func _seam(origin: Vector2, unit: float, strength: float, spread := 0.0) -> void:
	strength = clampf(strength, 0.0, 1.0)
	if strength <= 0.0:
		return
	var length := float(_seam_y.y - _seam_y.x)
	var mid := origin + Vector2(_seam_x + 0.5, (_seam_y.x + _seam_y.y) / 2.0) * unit
	var halo := Vector2(lerpf(18.0, 70.0, spread), length * lerpf(1.15, 1.0, spread)) * unit
	_ci.draw_texture_rect(_glow, Rect2(mid - halo / 2.0, halo), false, Color(1, 1, 1, strength * (0.9 + 0.1 * sin(_time * 2.1)) * (1.0 - 0.6 * spread)))
	for y in range(_seam_y.x, _seam_y.y + 1):
		var along := (y - _seam_y.x) / maxf(1.0, length)
		var shape := pow(sin(along * PI), 0.6) # bright middle, ends fading out
		var shimmer := 0.8 + 0.2 * sin(_time * 3.2 - y * 0.22)
		var i := strength * (0.25 + 0.75 * shape) * shimmer
		if i < 0.05:
			continue
		var at := origin + Vector2(_seam_x, y) * unit
		_ci.draw_rect(Rect2(at, Vector2(unit, unit)), Color(CYAN.lerp(Color.WHITE, 0.45 * i), minf(1.0, i * 1.2)))
		for side in [-1, 1]: # the page edges either side catch the light
			_ci.draw_rect(Rect2(at + Vector2(side * unit, 0), Vector2(unit, unit)), Color(CYAN, 0.5 * i))
	for k in 7: # motes rising out of the seam
		var life := fposmod(_time * 0.45 + k * 0.143, 1.0)
		var y := roundf(lerpf(_seam_y.y - length * (0.2 + 0.1 * (k % 3)), _seam_y.x - 4.0, life))
		var x := _seam_x + roundf(sin(_time * 1.3 + k * 2.1) * (1.0 + 2.0 * life + 8.0 * spread))
		var fade := strength * sin(life * PI)
		_ci.draw_rect(Rect2(origin + Vector2(x, y) * unit, Vector2(unit, unit)), Color(CYAN.lerp(Color.WHITE, 0.5), fade))


## Language pixels: a soft one-pixel glow around each, then the pixel itself.
func _draw_pixels(points: Array[Vector2i], at: Vector2, unit: float, color: Color, alpha: float, glow: float) -> void:
	for p in points:
		for o in [Vector2(-1, 0), Vector2(1, 0), Vector2(0, -1), Vector2(0, 1)]:
			_ci.draw_rect(Rect2(at + (Vector2(p) + o) * unit, Vector2(unit, unit)), Color(CYAN, glow * alpha))
	for p in points:
		_ci.draw_rect(Rect2(at + Vector2(p) * unit, Vector2(unit, unit)), Color(color, alpha))


## The ceremony's word: written in ink, its letters catch one by one (each flares white, then
## settles to cyan), the meaning comes once the whole word is lit, and the word leaves as a card.
func _draw_lighting(at: Vector2, entry: Dictionary, word_size: int, note_size: int, note_width: float, unit: float, e: float) -> void:
	var word := str(entry.word)
	var x := at.x
	for i in word.length():
		var since := _rite - (RITE_START + i * RITE_LETTER)
		var letter := word[i]
		if since < 0.0:
			_ci.draw_string(FONT, Vector2(x, at.y), letter, HORIZONTAL_ALIGNMENT_LEFT, -1, word_size, Color(INK, e))
		else:
			var flare := clampf(1.0 - since / 0.35, 0.0, 1.0)
			var halo := 0.18 + 0.4 * flare
			for o in [Vector2(-1, 0), Vector2(1, 0), Vector2(0, -1), Vector2(0, 1)]:
				_ci.draw_string(FONT, Vector2(x, at.y) + o * unit * (0.6 + flare), letter, HORIZONTAL_ALIGNMENT_LEFT, -1, word_size, Color(CYAN, halo * e))
			_ci.draw_string(FONT, Vector2(x, at.y), letter, HORIZONTAL_ALIGNMENT_LEFT, -1, word_size, Color(CYAN.darkened(0.25).lerp(Color.WHITE, flare * 0.8), e))
		x += FONT.get_string_size(letter, HORIZONTAL_ALIGNMENT_LEFT, -1, word_size).x
	var meaning := clampf((_rite - _rite_letters() + 0.3) / 0.5, 0.0, 1.0)
	_ci.draw_string(FONT, at + Vector2(0, 6 * unit), _fit(entry.note, note_size, note_width), HORIZONTAL_ALIGNMENT_LEFT, -1, note_size, Color(INK, 0.8 * e * meaning))


## Bottom right, after a second: "HOLD SPACE · SKIP" and a ring that fills while it is held.
func _draw_skip_hint() -> void:
	var a := clampf((_rite_clock - SKIP_HINT_AFTER) / 0.5, 0.0, 1.0) * 0.7
	if a <= 0.0:
		return
	var hint := "HOLD SPACE  ·  SKIP"
	var hint_size := int(8 * pixel)
	var hw := FONT.get_string_size(hint, HORIZONTAL_ALIGNMENT_LEFT, -1, hint_size).x
	var at := screen_rect.end - Vector2(hw + 16 * pixel, 12 * pixel)
	var color := Color(INK.lightened(0.6), a)
	_ci.draw_string(FONT, at, hint, HORIZONTAL_ALIGNMENT_LEFT, -1, hint_size, color)
	var ring := at + Vector2(-10, -3) * pixel
	_ci.draw_arc(ring, 5 * pixel, 0, TAU, 24, Color(color, a * 0.4), pixel)
	if _hold > 0.0:
		_ci.draw_arc(ring, 5 * pixel, -PI / 2.0, -PI / 2.0 + TAU * _hold / SKIP_HOLD, 24, Color(CYAN, 0.9), pixel)
	queue_redraw()


## The ceremony's card: it lifts off the word and flies down to where the word bar sits in a fight.
func _draw_rite_card(origin: Vector2, unit: float) -> void:
	var k := clampf((_rite - _rite_letters()) / RITE_CARD, 0.0, 1.0)
	if _rite < _rite_letters() or k >= 1.0:
		return
	var from := _rite_from
	var to := screen_rect.position + Vector2(screen_rect.size.x / 2.0, screen_rect.size.y - 34 * pixel)
	var fly := ease(k, 2.2)
	var at := Vector2(lerpf(from.x, to.x, fly), lerpf(from.y, to.y, fly) - sin(k * PI) * 30 * pixel)
	var a := clampf((1.0 - k) / 0.3, 0.0, 1.0) * clampf(k / 0.1, 0.0, 1.0)
	var size := Vector2(64, 24) * pixel
	var r := Rect2((at - size / 2.0).round(), size)
	for i in 4: # a short trail of cyan behind it
		var back := clampf(k - (i + 1) * 0.04, 0.0, 1.0)
		var tb := Vector2(lerpf(from.x, to.x, ease(back, 2.2)), lerpf(from.y, to.y, ease(back, 2.2)) - sin(back * PI) * 30 * pixel)
		_ci.draw_rect(Rect2(tb.round(), Vector2(2, 2) * pixel), Color(CYAN, a * (0.5 - i * 0.1)))
	_ci.draw_rect(r, Color(0.04, 0.07, 0.09, 0.92 * a))
	_ci.draw_rect(r, Color(CYAN, a), false, pixel)
	var word := _rite_lemma.to_upper()
	var font_size := int(11 * pixel)
	var w := FONT.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size).x
	_ci.draw_string(FONT, Vector2(r.get_center().x - w / 2.0, r.get_center().y + 4 * pixel).round(), word, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size, Color(CYAN, a))


## ENCOUNTERED on the page: the whole word, faint, its strokes thinning out after the first three
## letters (the paper shows through more and more towards the end). Seeded by the word: it holds still.
func _rubbed_out(at: Vector2, word: String, size: int, e: float, unit: float) -> void:
	_ci.draw_string(FONT, at, word, HORIZONTAL_ALIGNMENT_LEFT, -1, size, Color(PENCIL, 0.55 * e))
	var from := at.x + FONT.get_string_size(word.left(3), HORIZONTAL_ALIGNMENT_LEFT, -1, size).x
	var to := at.x + FONT.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x
	var cell := maxf(1.0, roundf(unit * 0.5))
	var top := at.y - size * 0.8
	var salt := word.hash()
	var x := from
	while x < to:
		var k := (x - from) / maxf(1.0, to - from)
		var y := top
		while y < at.y + size * 0.15:
			var clump := float(hash(salt + int(x / (cell * 3)) * 31 + int(y / (cell * 3)) * 977) & 0xffff) / 65535.0
			var grain := float(hash(salt + int(x / cell) * 131 + int(y / cell) * 7919) & 0xffff) / 65535.0
			if lerpf(grain, clump, 0.65) < 0.2 + 0.62 * k:
				_ci.draw_rect(Rect2(Vector2(x, y), Vector2(cell, cell)), Color(PAPER, e))
			y += cell
		x += cell


## A word written in pencil by someone not yet sure of it. Nothing moves: the doubt is in the
## drawing. Each letter takes the pencil a little differently (lighter, darker), a faint second
## pass sits just off the first as if the word were gone over again, and the grain of the paper
## breaks a few strokes. All of it is seeded by the word, so it looks the same every time.
func _pencil(at: Vector2, word: String, size: int, e: float, unit: float) -> void:
	var salt := word.hash()
	var pick := func(i: int) -> float: return float(hash(salt + i * 7919) & 0xffff) / 65535.0
	var x := at.x
	for i in word.length():
		var letter := word[i]
		var pressure := lerpf(0.5, 0.85, pick.call(i))
		_ci.draw_string(FONT, Vector2(x, at.y), letter, HORIZONTAL_ALIGNMENT_LEFT, -1, size, Color(PENCIL, pressure * e))
		if pick.call(i + 100) > 0.45: # gone over again, not quite on the first line
			var drift := Vector2(pick.call(i + 500) - 0.5, (pick.call(i + 600) - 0.5) * 0.5) * unit * 0.7
			_ci.draw_string(FONT, Vector2(x, at.y) + drift, letter, HORIZONTAL_ALIGNMENT_LEFT, -1, size, Color(PENCIL, 0.16 * e))
		x += FONT.get_string_size(letter, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x
	var width := x - at.x
	var cap := size * 0.62 # roughly the height of a capital
	for k in 14: # the paper's grain skipping under the pencil: short breaks in the strokes
		var gap := Vector2(at.x + pick.call(200 + k) * width, at.y - pick.call(300 + k) * cap)
		_ci.draw_rect(Rect2(gap, Vector2(lerpf(1.0, 2.5, pick.call(400 + k)), 0.55) * unit), Color(PAPER, 0.95 * e))

## The line under the book: where you are and the keys.
func _draw_caption(origin: Vector2, unit: float, e: float) -> void:
	var where: String = ["THE SKY", "A REGION", "A CLUSTER", "A CONSTELLATION", "A WORD"][_level - 1]
	var keys := "W/S choose   E closer   " if _level < SKY.WORD_PAGE else ""
	keys += "Q back   " if _level > 1 else ""
	keys += "A/D turn   " if _level > 1 else ""
	var caption := "%s   ·   %sTab close   1/2/3 speed" % [where, keys]
	var caption_size := int(8 * pixel)
	var w := FONT.get_string_size(caption, HORIZONTAL_ALIGNMENT_LEFT, -1, caption_size).x
	_ci.draw_string(FONT, Vector2(screen_rect.get_center().x - w / 2.0, origin.y + OPEN_BOOK.size.y * unit + 18 * pixel), caption, HORIZONTAL_ALIGNMENT_LEFT, -1, caption_size, Color(0.85, 0.82, 0.76, e))


## A font size in book pixels, sized on the game's grid and then scaled whole, so text painted
## into a hidden spread at the window's resolution is exactly the open book's text, only sharper.
func _font_px(book_px: float, unit: float) -> int:
	var base := pixel * book_scale
	return int(book_px * base) * maxi(1, roundi(unit / base))

## Shortens a line, a word at a time, until it fits `width`.
func _fit(text: String, font_size: int, width: float) -> String:
	var words := text.split(" ")
	while words.size() > 1 and FONT.get_string_size(" ".join(words), HORIZONTAL_ALIGNMENT_LEFT, -1, font_size).x > width:
		words.resize(words.size() - 1)
		words[-1] = words[-1].trim_suffix(",") + "…"
	return " ".join(words)


func _brackets(r: Rect2, color: Color, unit: float) -> void:
	var l := 4 * unit
	var w := unit
	for corner in [r.position, Vector2(r.end.x, r.position.y), Vector2(r.position.x, r.end.y), r.end]:
		var sx := 1.0 if corner.x == r.position.x else -1.0
		var sy := 1.0 if corner.y == r.position.y else -1.0
		_ci.draw_rect(Rect2(corner + Vector2(minf(0, sx * l), minf(0, sy * w)), Vector2(l, w)), color)
		_ci.draw_rect(Rect2(corner + Vector2(minf(0, sx * w), minf(0, sy * l)), Vector2(w, l)), color)
