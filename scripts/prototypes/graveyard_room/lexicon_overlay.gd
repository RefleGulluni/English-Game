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
const PAGE_STAGES := ["USABLE", "UNDERSTOOD", "RECOGNIZED", "ENCOUNTERED"] # grey box: no progress yet
const STAR_GAP := 0.14 # seconds between one star lighting and the next
const STAR_FLASH := 0.35 # a new star flares, then settles
const LINE_PAUSE := 0.15 # after the last star, before the first line
const LINE_TIME := 0.35 # one line drawing itself from star to star
const LINE_GAP := 0.16 # between the starts of two lines
const PACE := [0.7, 1.0, 1.4] # keys 1 / 2 / 3: quicker, as designed, slower (to judge the timing)
# Where each stage ends, as a share of the opening.
const P_RISE := 0.15
const P_SIGIL := 0.48 # the sigil wakes: triangle and dot, then the ring drawn clockwise
const P_TIP := 0.60
const P_FALL := 0.83
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
var _pages: Array = [] # four entries per right page, from the word library
var _ci: CanvasItem = self # where the helpers draw: this overlay, or one of the hidden spreads
var _sigil: Array[Vector2i] = [] # cyan pixels of the cover, in closed-book pixels
var _sigil_core: Array[Vector2i] = [] # the triangle and the dot inside it
var _sigil_ring: Array[Vector2i] = [] # the circle, clockwise from its top
# The constellation, split into stars (the dense knots) and the lines between them. The stars
# light one by one from the spine outwards, then each line draws itself from star to star.
var _star_points: Array = [] # one Array[Vector2i] per star, nearest the spine first
var _line_points: Array = [] # one Array[Vector2i] per line, in drawing order from its first star
var _seam_x := OPEN_SPINE # the gap between the pages of the standing book
var _seam_y := Vector2i(BOOK_TOP + 3, BOOK_BOTTOM - 3) # its lit stretch, inside the page block
var _glow: Texture2D # soft elliptical halo for the seam light
var _sky := 0.0 # seconds since the book lay fully open (the constellation's own clock)
var _time := 0.0


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	var sheet := Image.load_from_file(ProjectSettings.globalize_path(SHEET))
	var closed := sheet.get_region(CLOSED_BOOK)
	var open := sheet.get_region(OPEN_BOOK)
	_sigil.assign(_lift_cyan(closed, ENGRAVED).map(func(p): return p[0]))
	var sky: Array[Vector2i] = []
	for p in _lift_cyan(open, PAPER):
		if not RIGHT_PAGE.has_point(p[0]):
			sky.append(p[0])
	_split_sky(sky)
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
	_find_paper(_open.get_image())
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


## Grey box until the Lexicon interface: the word library in list order, four to a page, each
## shown at a stage in turn (there is no player progress yet).
func _load_pages() -> void:
	var list := FileAccess.get_file_as_string(WORDS_DIR + "word_list.txt")
	var page: Array = []
	for line in list.split("\n"):
		var lemma := line.get_slice("#", 0).strip_edges().get_slice(" ", 0)
		var data = JSON.parse_string(FileAccess.get_file_as_string(WORDS_DIR + "entries/%s.json" % lemma)) if lemma else null
		if not data is Dictionary:
			continue
		var stage: String = PAGE_STAGES[(page.size() + _pages.size()) % PAGE_STAGES.size()]
		page.append({"word": lemma.to_upper() if stage != "ENCOUNTERED" else "", "stage": stage, "note": data.senses[0].sense})
		if page.size() == 4:
			_pages.append(page)
			page = []
	if not page.is_empty():
		_pages.append(page)
	if _pages.is_empty():
		_pages.append(ENTRIES)


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
func _split_sky(sky: Array[Vector2i]) -> void:
	var lit := {}
	for p in sky:
		lit[p] = true
	var around := func(p: Vector2i, reach: int) -> Array[Vector2i]:
		var out: Array[Vector2i] = []
		for dy in range(-reach, reach + 1):
			for dx in range(-reach, reach + 1):
				if (dx != 0 or dy != 0) and lit.has(p + Vector2i(dx, dy)):
					out.append(p + Vector2i(dx, dy))
		return out
	var dense := {}
	for p in sky:
		if around.call(p, 1).size() >= 4:
			dense[p] = true
	var taken := {}
	for p in dense:
		if taken.has(p):
			continue
		var knot := _flood(p, dense, 1)
		var star: Array[Vector2i] = []
		for q in knot:
			for r in around.call(q, 2) + [q]:
				if not taken.has(r):
					taken[r] = true
					star.append(r)
		_star_points.append(star)
	var centre := func(points: Array) -> Vector2:
		var c := Vector2.ZERO
		for q in points:
			c += Vector2(q)
		return c / maxf(1.0, points.size())
	_star_points.sort_custom(func(a, b): return absf(centre.call(a).x - OPEN_SPINE) < absf(centre.call(b).x - OPEN_SPINE))
	var rest := {}
	for p in sky:
		if not taken.has(p):
			rest[p] = true
	var lines := []
	for p in rest:
		if taken.has(p):
			continue
		var line := _flood(p, rest, 3) # lines may be drawn with small gaps
		for q in line:
			taken[q] = true
		# Start at the end touching the earliest star (or any end), then walk the line outwards.
		var start: Vector2i = line[0]
		var first := _star_points.size()
		for q in line:
			for i in _star_points.size():
				if i < first and _star_points[i].any(func(s): return absi(s.x - q.x) <= 2 and absi(s.y - q.y) <= 2):
					first = i
					start = q
		var inside := {}
		for q in line:
			inside[q] = true
		lines.append([first, _flood(start, inside, 3)])
	lines.sort_custom(func(a, b): return a[0] < b[0])
	for l in lines:
		_line_points.append(l[1])


## Pixels of `pool` connected to `from` (8-way within `reach`), in breadth-first order.
static func _flood(from: Vector2i, pool: Dictionary, reach: int) -> Array[Vector2i]:
	var order: Array[Vector2i] = [from]
	var seen := {from: true}
	var i := 0
	while i < order.size():
		var p := order[i]
		i += 1
		for dy in range(-reach, reach + 1):
			for dx in range(-reach, reach + 1):
				var q := p + Vector2i(dx, dy)
				if pool.has(q) and not seen.has(q):
					seen[q] = true
					order.append(q)
	return order


func _clean(file: String, derived: Image) -> Texture2D:
	var path := ProjectSettings.globalize_path(CLEAN_DIR + file)
	return ImageTexture.create_from_image(Image.load_from_file(path) if FileAccess.file_exists(path) else derived)


func toggle() -> void:
	is_open = not is_open
	open_changed.emit(is_open)


## A / D: turn to the next or the previous spread (none before the first).
func turn_page(forward: bool) -> void:
	if not (is_open and _t >= 1.0 and _turn < 0.0) or (not forward and _page == 0):
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


func _entries(page: int) -> Array:
	return _pages[page % _pages.size()]


func set_open_now(open: bool) -> void:
	is_open = open
	_t = 1.0 if open else 0.0
	queue_redraw()


func _process(delta: float) -> void:
	_time += delta
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
			_sky = 0.0 # a new page: its constellation draws itself again
			for spread in _spreads:
				spread.render_target_update_mode = SubViewport.UPDATE_DISABLED
		else:
			for spread in _spreads:
				spread.get_child(0).queue_redraw()
		queue_redraw()
	if is_open and _t >= 1.0 and _turn < 0.0:
		_sky += delta
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
	elif is_open and event.keycode in [KEY_W, KEY_UP]:
		selected = (selected + _entries(_page).size() - 1) % _entries(_page).size()
	elif is_open and event.keycode in [KEY_S, KEY_DOWN]:
		selected = (selected + 1) % _entries(_page).size()
	elif is_open and event.keycode in [KEY_A, KEY_D, KEY_LEFT, KEY_RIGHT]:
		turn_page(event.keycode in [KEY_D, KEY_RIGHT])
	else:
		return
	get_viewport().set_input_as_handled()
	queue_redraw()


## 0..1 progress through the stage that runs from a to b.
func _stage(a: float, b: float) -> float:
	return clampf((_t - a) / (b - a), 0.0, 1.0)


func _draw() -> void:
	_ci = self
	if _t <= 0.0:
		return
	var rise_t := ease(_stage(0.0, P_RISE), -2.0)
	_ci.draw_rect(screen_rect, Color(0.02, 0.02, 0.04, 0.62 * ease(_stage(0.0, P_SIGIL), -2.0)))

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
	_draw_caption(origin, unit, _stage(0.88, 1.0))


## Everything printed on a spread: the right page's paper, the constellation (on its own clock),
## the entries and the page numbers.
func _paint_pages(origin: Vector2, unit: float, page: int, sky_clock: float, sky_fade: float, e: float) -> void:
	_ci.draw_rect(Rect2(origin + Vector2(RIGHT_PAGE.position) * unit, Vector2(RIGHT_PAGE.size) * unit), PAPER)
	_draw_sky(origin, unit, sky_fade, sky_clock)
	_draw_entries(origin, unit, e, page)
	var size := _font_px(4.6, unit)
	for side in 2: # page numbers, small and centred at the foot of each page
		var number := str(page * 2 + side + 1)
		var w := FONT.get_string_size(number, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x
		var centre := 75.0 if side == 0 else 185.0
		_ci.draw_string(FONT, origin + Vector2(centre * unit - w / 2.0, 104 * unit), number, HORIZONTAL_ALIGNMENT_LEFT, -1, size, Color(INK, 0.7 * e))


## One hidden spread, painted at the size it shows on screen: [0] the spread turned from, [1] the
## one turned to. The new spread's constellation is still dark: it lights once the page lands.
func _paint_spread(canvas: Control, which: int) -> void:
	_ci = canvas
	var unit := _spread_unit
	_ci.draw_texture_rect(_open, Rect2(Vector2.ZERO, Vector2(OPEN_BOOK.size) * unit), false)
	_paint_pages(Vector2.ZERO, unit, _spread_page[which], _sky if which == 0 else 0.0, 1.0, 1.0)
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


## The constellation on its own clock: stars light one by one (each flares, then settles), then
## each line draws itself from its first star to the next. `fade` dims it all while closing.
func _draw_sky(origin: Vector2, unit: float, fade: float, clock: float) -> void:
	var calm := 0.18 + 0.05 * sin(_time * 1.6)
	for i in _star_points.size():
		var age := clock - i * STAR_GAP
		if age <= 0.0:
			continue
		var flare := clampf(1.0 - age / STAR_FLASH, 0.0, 1.0)
		var star: Array[Vector2i] = []
		star.assign(_star_points[i])
		_draw_pixels(star, origin, unit, CYAN.lerp(Color.WHITE, 0.5 * flare), fade * minf(1.0, age / 0.08), calm + 0.45 * flare)
	var start := _star_points.size() * STAR_GAP + LINE_PAUSE
	for j in _line_points.size():
		var progress := clampf((clock - start - j * LINE_GAP) / LINE_TIME, 0.0, 1.0)
		if progress <= 0.0:
			continue
		var line: Array = _line_points[j]
		var drawn: Array[Vector2i] = []
		drawn.assign(line.slice(0, ceili(progress * line.size())))
		_draw_pixels(drawn, origin, unit, CYAN.darkened(0.15), fade * 0.9, calm)


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


func _draw_entries(origin: Vector2, unit: float, e: float, page: int) -> void:
	if e <= 0.0:
		return
	# Entries on the right page: one line per word, its meaning underneath once understood.
	var left := origin.x + (RIGHT_PAGE.position.x + 8) * unit
	var top := origin.y + (RIGHT_PAGE.position.y + 6) * unit
	var row := 20.0 * unit
	var word_size := _font_px(7.5, unit)
	var note_size := _font_px(4.6, unit)
	var entries := _entries(page)
	var note_width := (RIGHT_PAGE.size.x - 10) * unit
	for i in entries.size():
		var entry: Dictionary = entries[i]
		var y := top + i * row
		if i == selected:
			_ci.draw_rect(Rect2(Vector2(left - 5 * unit, y + 2 * unit), Vector2(2, 2) * unit), Color(INK, e))
		match entry.stage:
			"ENCOUNTERED": # only a reserved place: corner brackets around an empty line
				_brackets(Rect2(Vector2(left, y + unit), Vector2(56, 9) * unit), Color(PENCIL, 0.8 * e), unit)
			"RECOGNIZED": # pencil: still, but not yet sure of itself (user 2026-10-29: no wobbling)
				_pencil(Vector2(left, y + 8 * unit), entry.word, word_size, e, unit)
			"UNDERSTOOD": # ink, settled
				_ci.draw_string(FONT, Vector2(left, y + 8 * unit), entry.word, HORIZONTAL_ALIGNMENT_LEFT, -1, word_size, Color(INK, e))
				_ci.draw_string(FONT, Vector2(left, y + 14 * unit), _fit(entry.note, note_size, note_width), HORIZONTAL_ALIGNMENT_LEFT, -1, note_size, Color(INK, 0.8 * e))
			"USABLE": # cyan, steady glow: language
				var glow := 0.18 + 0.06 * sin(_time * 1.6)
				for o in [Vector2(-1, 0), Vector2(1, 0), Vector2(0, -1), Vector2(0, 1)]:
					_ci.draw_string(FONT, Vector2(left, y + 8 * unit) + o * unit * 0.6, entry.word, HORIZONTAL_ALIGNMENT_LEFT, -1, word_size, Color(CYAN, glow * e))
				_ci.draw_string(FONT, Vector2(left, y + 8 * unit), entry.word, HORIZONTAL_ALIGNMENT_LEFT, -1, word_size, Color(CYAN.darkened(0.25), e))
				_ci.draw_string(FONT, Vector2(left, y + 14 * unit), _fit(entry.note, note_size, note_width), HORIZONTAL_ALIGNMENT_LEFT, -1, note_size, Color(INK, 0.8 * e))




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

## The line under the book: the selected entry's stage and the keys.
func _draw_caption(origin: Vector2, unit: float, e: float) -> void:
	var stage: String = _entries(_page)[mini(selected, _entries(_page).size() - 1)].stage
	var caption := "%s   ·   W/S choose   A/D turn   V %s   Tab close   1/2/3 speed" % [stage, "live turn" if live_turn else "6 frames"]
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
