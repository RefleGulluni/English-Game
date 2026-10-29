class_name CombatView
extends Node
## How a fight looks in the v3 world (KB 02_SYSTEMS/01_Combat/English_Game_Combat_Presentation_Proposal.md,
## first playable pass 2026-10-28, "Seamless In-World Semantic Combat"): the fight happens in the
## room where it starts. Presentation only: it reads CombatState and asks the scene to act, never
## changes the rules.
##
## - Start: the room's edges sink into cold mist (no zoom: pixel art only scales by whole numbers),
##   the bar fades in, a faint language ring lies under the hero.
## - Bottom: one thin word bar. Left HP, Armor, Focus nodes and only the corruption that is active;
##   centre the words of this turn as luminous text (no cards); right END TURN.
## - Hovering a word previews exactly what it will do (Structure 12 → 4, Focus 3 → 1, EXPOSED).
## - Over the enemy: its intent in English, as complete as the hero understands it (? → STRIKE ? →
##   STRIKE · 6), name, HP and Structure. Hover it for the long description.
## - Invoking: the word appears by the hero first, then its geometry reaches the enemy, and only then
##   does the enemy react (the skeleton holds its hit until the word lands). Each word has its own
##   shape, drawn here in pixels on the language layer. Breaking Structure stops time for a moment.
## - In the fight only short words appear (EXPOSED, BOUND, -8); nothing pops up over the middle.

signal invoke_requested(uid: int, restore_target: String)
signal retain_requested(uid: int)
signal end_turn_requested
signal mulligan_confirmed(ids: Array[int])
signal reaction_answered(deflect: bool)

const CYAN := Color(0.42, 0.86, 0.95)
const PENCIL := Color8(176, 166, 152) # a word only half known: lent for one use (D-078)
## Cyan belongs to language only (Art Bible v3 §8): the words, their shapes, the intent, Focus.
## Everything else (numbers, labels, frames, hints) uses a palette of its own. Two to compare
## (user 2026-10-28: "all one cyan is a little monotonous"); P switches them in a fight.
const PALETTES := {
	"warm": {"ink": Color8(222, 206, 176), "dim": Color8(150, 136, 116), "hurt": Color8(206, 98, 76), "panel": Color(0.055, 0.045, 0.035, 0.94), "edge": Color8(150, 128, 92, 150), "button": Color8(222, 206, 176)},
	"cold": {"ink": Color(0.86, 0.89, 0.86), "dim": Color(0.56, 0.6, 0.62), "hurt": Color(0.9, 0.45, 0.4), "panel": Color(0.02, 0.03, 0.04, 0.93), "edge": Color(0.42, 0.86, 0.95, 0.45), "button": Color(0.42, 0.86, 0.95)},
}
var INK := Color8(222, 206, 176)
var DIM := Color8(150, 136, 116)
var HURT := Color8(206, 98, 76)
var palette := "warm"
var FAMILY_MARKS := {} # family → rows of "X." read from the glyph files
const NATIVE := Vector2(960, 540)
const BAR_TOP := 432.0
const FONT := preload("res://art/ui/fonts/CormorantGaramond.ttf")
const VIGNETTE := preload("res://scripts/world/v3/combat_vignette.gdshader")
const IMPACT_AT := 0.42 # seconds from invoking to the word reaching the enemy
const CAST_TIME := 0.85 # the whole cast; clicks wait until it is over
const ENEMY_BODY := Vector2(0, -46) # from the feet to the middle of the body
const HERO_CHEST := Vector2(0, -50)
const SIGIL_FONT := 18
const SIGIL_H := 40.0
const DISSOLVE_TIME := 0.55
const LEAD := 0.45 # the word leaves the bar and reaches the hero before the hero speaks it
## The nine family marks from the art group (art/ui/word_sigil_v3/glyphs/, 11x11 white on
## transparent, tinted cyan here). Keys are CombatContent.SKILLS families.
const MARK_FILES := {"FORCE": "force", "DIRECT HP": "direct", "DECAY": "decay", "TOXICITY": "toxicity",
	"PERCEPTION": "perception", "CONTROL": "control", "REACTION": "reaction", "SEMANTIC PROTECTION": "protection",
	"RESTORATION": "restoration"}
const MARK_DIR := "res://art/ui/word_sigil_v3/glyphs/family_%s.png"
## Claude's earlier placeholders: only used when a file is missing.
const PLACEHOLDER_MARKS := {
	"FORCE": [".....X.....", "..X..X..X..", "...X...X...", "....X.X....", ".XX.....XX.", "....X.X....", "...X...X...", "..X..X..X..", ".....X.....", "...........", "..........."],
	"DIRECT HP": ["...........", "...........", "........X..", ".........X.", "XXXXXXXXXXX", ".........X.", "........X..", "...........", "...........", "...........", "..........."],
	"PERCEPTION": [".....X.....", "....X.X....", "...X...X...", "..X.....X..", ".X...X...X.", "X...XXX...X", ".X...X...X.", "..X.....X..", "...X...X...", "....X.X....", ".....X....."],
	"CONTROL": ["....XXX....", "..XX...XX..", ".X.......X.", ".X..XXX..X.", "X..X...X..X", "X..X...X..X", ".X..XXX..X.", ".X.......X.", "..XX...XX..", "....XXX....", "..........."],
	"DECAY": [".....X.....", "...........", "....X.X....", "...........", "...X.X.X...", "...........", "..X.X.X.X..", "...........", ".X.X.X.X.X.", "...........", "X.X.X.X.X.X"],
	"TOXICITY": [".....X.....", ".....X.....", "....X.X....", "....X.X....", "...X...X...", "...X...X...", "..X.....X..", "..X..X..X..", "...X...X...", "....XXX....", "..........."],
	"REACTION": ["X..........", ".X.........", "..X........", "...X.......", "....X......", "....X......", "...X.X.....", "..X...X....", ".X.....XX..", "X.......XXX", "..........."],
	"SEMANTIC PROTECTION": ["...XXXXX...", "..X.....X..", ".X.......X.", "X....X....X", "X...XXX...X", "X....X....X", ".X.......X.", "..X.....X..", "...XXXXX...", "...........", "..........."],
	"RESTORATION": [".....X.....", ".....X.....", ".....X.....", "...........", "XXX.....XXX", "...........", ".....X.....", ".....X.....", ".....X.....", "...........", "..........."],
	"": ["...........", "...........", "...........", ".....X.....", "....X.X....", "...X...X...", "....X.X....", ".....X.....", "...........", "...........", "..........."],
}

var combat: CombatState
var hero: Node2D
var enemy: Node2D # the skeleton's root
var enemy_name := "ENEMY"
var active := false
var busy := false
var selected_mulligan: Array[int] = []
var forced_hover := -1 # capture mode: show this word as if the mouse were on it

var _viewport: SubViewport
var _world_screen: Control
var _vignette: ColorRect
var _fx_node: Node2D
var _fx: Array[Dictionary] = []
var _ui: Control
var _bar: Control
var _vitals: Control
var _words: HBoxContainer
var _note: Label
var _end_button: Button
var _deflect_button: Button
var _tag: Control
var _tip: PanelContainer
var _tip_rows: VBoxContainer
var _floats: Control
var _shown := {} # enemy values the tag shows; they wait for the word to land
var _holding := false
var _reaction := {}
var _last_hero_hp := -1
var _strength := 0.0
var _clock := 0.0
var _leaving := {} # the used word's place in the bar, for its dissolve
var _gap_index := -1 # the bar keeps the used word's place open while it dissolves, then closes it
var _gap_w := 0.0
var _gap: Control


func setup(viewport: SubViewport, language: CanvasLayer, world_screen: Control, model: CombatState) -> void:
	_load_marks()
	_viewport = viewport
	_world_screen = world_screen
	combat = model
	combat.changed.connect(_on_changed)
	combat.reaction_requested.connect(func(action, cost):
		_reaction = {"action": action, "cost": cost}
		refresh())

	var mist_layer := CanvasLayer.new()
	mist_layer.layer = 4 # over the world, under the language layer
	viewport.add_child(mist_layer)
	_vignette = ColorRect.new()
	_vignette.size = NATIVE
	_vignette.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var material := ShaderMaterial.new()
	material.shader = VIGNETTE
	_vignette.material = material
	mist_layer.add_child(_vignette)
	_fx_node = Node2D.new()
	_fx_node.draw.connect(_draw_fx)
	language.add_child(_fx_node)

	# Text lives outside the pixel viewport so it stays sharp at any window size (Art Bible §8.2).
	var layer := CanvasLayer.new()
	layer.layer = 8
	add_child(layer)
	_ui = Control.new()
	_ui.size = NATIVE
	_ui.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_ui.modulate.a = 0.0
	_ui.hide()
	layer.add_child(_ui)
	_build_bar()
	_tag = Control.new()
	_tag.size = Vector2(116, 56)
	_tag.mouse_filter = Control.MOUSE_FILTER_STOP
	_tag.draw.connect(_draw_tag)
	_tag.mouse_entered.connect(_show_intent_tip)
	_tag.mouse_exited.connect(_hide_tip)
	_ui.add_child(_tag)
	_floats = Control.new()
	_floats.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_ui.add_child(_floats)
	_build_tip()
	set_palette(palette)


func _load_marks() -> void:
	FAMILY_MARKS = PLACEHOLDER_MARKS.duplicate()
	for family in MARK_FILES:
		var path := ProjectSettings.globalize_path(MARK_DIR % MARK_FILES[family])
		if not FileAccess.file_exists(path):
			continue
		var img := Image.load_from_file(path)
		var rows: Array[String] = []
		for y in img.get_height():
			var row := ""
			for x in img.get_width():
				row += "X" if img.get_pixel(x, y).a > 0.5 else "."
			rows.append(row)
		FAMILY_MARKS[family] = rows


func set_palette(name: String) -> void:
	palette = name
	var p: Dictionary = PALETTES[name]
	INK = p.ink
	DIM = p.dim
	HURT = p.hurt
	_tip.queue_redraw()
	for button in [_end_button, _deflect_button]:
		button.add_theme_color_override("font_color", p.button)
		button.add_theme_color_override("font_disabled_color", Color(p.button, 0.35))
	refresh()


func _unhandled_key_input(event: InputEvent) -> void:
	if active and event.is_pressed() and not event.is_echo() and event.physical_keycode == KEY_P:
		set_palette("cold" if palette == "warm" else "warm")
		_float("PALETTE · " + palette.to_upper(), Vector2(480, 60), INK, 14)


# --- Opening and closing -----------------------------------------------------------------

func open(fighter: Node2D, foe: Node2D, foe_name: String) -> void:
	hero = fighter
	enemy = foe
	enemy_name = foe_name
	active = true
	_last_hero_hp = combat.hp
	_shown = _enemy_values()
	_ui.show()
	var tween := create_tween().set_parallel()
	tween.tween_property(_ui, "modulate:a", 1.0, 0.5)
	tween.tween_property(self, "_strength", 1.0, 0.9).set_trans(Tween.TRANS_SINE)
	refresh()


func close() -> void:
	active = false
	_hide_tip()
	var tween := create_tween().set_parallel()
	tween.tween_property(_ui, "modulate:a", 0.0, 0.6)
	tween.tween_property(self, "_strength", 0.0, 1.2).set_trans(Tween.TRANS_SINE)
	tween.chain().tween_callback(_ui.hide)


# --- The bar -----------------------------------------------------------------------------

func _build_bar() -> void:
	_bar = Control.new()
	_bar.position = Vector2(0, BAR_TOP)
	_bar.size = Vector2(NATIVE.x, NATIVE.y - BAR_TOP)
	_bar.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_ui.add_child(_bar)
	var shade := TextureRect.new()
	var gradient := Gradient.new()
	gradient.set_color(0, Color(0.02, 0.03, 0.04, 0.0))
	gradient.set_color(1, Color(0.02, 0.03, 0.04, 0.88))
	gradient.add_point(0.45, Color(0.02, 0.03, 0.04, 0.72))
	var texture := GradientTexture2D.new()
	texture.gradient = gradient
	texture.fill_from = Vector2(0, 0)
	texture.fill_to = Vector2(0, 1)
	texture.width = 8
	texture.height = 64
	shade.texture = texture
	shade.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	shade.stretch_mode = TextureRect.STRETCH_SCALE
	shade.size = _bar.size
	shade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_bar.add_child(shade)

	_vitals = Control.new()
	_vitals.position = Vector2(24, 34)
	_vitals.size = Vector2(190, 70)
	_vitals.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_vitals.draw.connect(_draw_vitals)
	_bar.add_child(_vitals)

	_note = _label("", 13, DIM)
	_note.position = Vector2(230, 22)
	_note.size = Vector2(500, 18)
	_note.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_bar.add_child(_note)
	_words = HBoxContainer.new()
	_words.position = Vector2(230, 44)
	_words.size = Vector2(500, 48)
	_words.alignment = BoxContainer.ALIGNMENT_CENTER
	_words.add_theme_constant_override("separation", 12)
	_bar.add_child(_words)

	_deflect_button = _text_button("DEFLECT", 16)
	_deflect_button.position = Vector2(790, 26)
	_deflect_button.size = Vector2(150, 30)
	_deflect_button.pressed.connect(func():
		if not _reaction.is_empty():
			_reaction = {}
			reaction_answered.emit(true))
	_bar.add_child(_deflect_button)
	_end_button = _text_button("END TURN", 16)
	_end_button.position = Vector2(790, 60)
	_end_button.size = Vector2(150, 30)
	_end_button.pressed.connect(_press_end)
	_bar.add_child(_end_button)


func _press_end() -> void:
	if busy:
		return
	if not _reaction.is_empty():
		_reaction = {}
		reaction_answered.emit(false)
	elif combat.deck.mulligan_pending:
		mulligan_confirmed.emit(selected_mulligan.duplicate())
		selected_mulligan.clear()
	else:
		end_turn_requested.emit()


func refresh() -> void:
	if not active or combat.enemy.is_empty():
		return
	if not _holding:
		_shown = _enemy_values()
	for child in _words.get_children():
		_words.remove_child(child)
		child.queue_free()
	var widths := 0.0
	for card in combat.deck.hand:
		var button := _word_button(card, combat.deck.hand.size() > 5)
		widths += button.custom_minimum_size.x
		_words.add_child(button)
	# A sixth word (one lent, D-078) would push into END TURN: close the gaps, then spill left
	# over the empty space beside the vitals rather than right.
	var count := combat.deck.hand.size()
	var gap := 12.0 if count < 2 else clampf((500.0 - widths) / (count - 1), 4.0, 12.0)
	var total := widths + gap * maxf(0, count - 1)
	_words.add_theme_constant_override("separation", int(gap))
	_words.size.x = maxf(500.0, total)
	# past 500 px it grows left, but never further than the vitals' edge (x 222)
	_words.position.x = roundf(maxf(222.0, 730.0 - total) if total > 500.0 else 230.0)
	_gap = null
	if _gap_index >= 0:
		_gap = Control.new()
		_gap.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_words.add_child(_gap)
		_words.move_child(_gap, mini(_gap_index, _words.get_child_count() - 1))
	if not _reaction.is_empty():
		var action: Dictionary = _reaction.action
		_note.text = "%s comes at you%s" % [str(action.word), "  ·  %d damage" % int(action.get("damage", 0)) if combat.inattention_tier < 4 else ""]
		_note.add_theme_color_override("font_color", HURT)
		_deflect_button.text = "DEFLECT · %d FOCUS" % int(_reaction.cost)
		_deflect_button.disabled = not combat.can_react()
		_deflect_button.show()
		_end_button.text = "TAKE THE HIT"
	elif combat.deck.mulligan_pending:
		_note.text = "OPENING HAND  ·  click up to two words to replace"
		_note.add_theme_color_override("font_color", DIM)
		_deflect_button.hide()
		_end_button.text = "REPLACE %d" % selected_mulligan.size() if not selected_mulligan.is_empty() else "KEEP HAND"
	else:
		_note.text = ""
		_deflect_button.hide()
		_end_button.text = "END TURN"
	_end_button.disabled = busy or combat.finished or (combat.turn_ending and _reaction.is_empty())
	_vitals.queue_redraw()
	_tag.queue_redraw()


## compact: a crowded hand (six words) draws each word a little tighter.
func _word_button(card: Dictionary, compact := false) -> Control:
	var uid := int(card.instance_id)
	var word := str(card.name)
	var reason := combat.disabled_reason(word, uid)
	var sigil := Control.new()
	var text_w := FONT.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, SIGIL_FONT).x
	sigil.custom_minimum_size = Vector2(maxf(56.0, ceilf(text_w) + (30.0 if compact else 36.0)), SIGIL_H)
	sigil.mouse_filter = Control.MOUSE_FILTER_STOP
	sigil.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	var usable := (reason.is_empty() or combat.deck.mulligan_pending) and not busy
	sigil.set_meta("uid", uid)
	sigil.set_meta("usable", usable)
	sigil.set_meta("blocked", not reason.is_empty() and not combat.deck.mulligan_pending) # its own reason, not just "a word is flying"
	sigil.set_meta("hover", false)
	sigil.draw.connect(_draw_sigil.bind(sigil, card))
	sigil.gui_input.connect(func(event: InputEvent):
		if event is InputEventMouseButton and event.pressed:
			if event.button_index == MOUSE_BUTTON_LEFT:
				_press_word(card)
			elif event.button_index == MOUSE_BUTTON_RIGHT and not combat.deck.mulligan_pending:
				retain_requested.emit(uid))
	sigil.mouse_entered.connect(func():
		sigil.set_meta("hover", true)
		sigil.set_meta("hover_since", _clock)
		_show_word_tip(card, sigil))
	sigil.mouse_exited.connect(func():
		sigil.set_meta("hover", false)
		_hide_tip())
	return sigil


func _press_word(card: Dictionary) -> void:
	if busy:
		return
	var uid := int(card.instance_id)
	if combat.deck.mulligan_pending:
		if uid in selected_mulligan:
			selected_mulligan.erase(uid)
		elif selected_mulligan.size() < 2:
			selected_mulligan.append(uid)
		refresh()
		return
	if not combat.disabled_reason(str(card.name), uid).is_empty():
		return
	_hide_tip()
	# RESTORE mends HP, or Armor when HP is already full (no choice box in the middle of the screen).
	invoke_requested.emit(uid, "hp" if combat.hp < CombatState.MAX_HP else "armor")


## The Word Sigil, level 3 of docs/reference/word_sigil_refinement_levels.png on the art group's
## direction B (art/ui/word_sigil_v3/): the word stands on a precise baseline with a node at each
## end, a dotted ruler between them, a faint echo line below, and its Focus cost as nodes set into
## the middle of the line. Light: a soft halo around every stroke (glow may be smooth). Motion: the
## cost nodes breathe; under the mouse the line closes, light runs in from both ends and a crown of
## nodes rises over the word. Family marks are Claude's placeholders until the art group's arrive.
func _draw_sigil(sigil: Control, card: Dictionary) -> void:
	var uid := int(card.instance_id)
	var word := str(card.name)
	# A borrowed word (D-078: lent once, in pencil, before it is truly yours) is drawn in pencil grey.
	var ink := PENCIL if bool(card.get("borrowed", false)) else CYAN
	var usable := bool(sigil.get_meta("usable", false))
	var hover := usable and (bool(sigil.get_meta("hover", false)) or uid == forced_hover)
	var retained := uid in combat.deck.retained_cards
	var blocked := bool(sigil.get_meta("blocked", false))
	var a := 1.0 if hover else (0.42 if blocked else (0.86 if usable else 0.7))
	var w := sigil.size.x
	var base := 28.0
	var mid := roundf(w / 2.0)
	var cost := combat.card_cost(card)
	var breathe := 0.78 + 0.22 * sin(_clock * 2.2 + uid)
	# Family mark and the word.
	var family := str(CombatContent.SKILLS.get(str(card.card_id), {}).get("family", ""))
	_glyph(sigil, Vector2(6, 9), FAMILY_MARKS.get(family, FAMILY_MARKS[""]), Color(ink, a * 0.9))
	_glow_text(sigil, Vector2(23, 20), word, SIGIL_FONT, Color(ink, a))
	# The baseline: two ends and a dotted ruler, or one closed line under the mouse.
	var c := Color(ink, a * 0.85)
	var gap := cost * 4.0 + 3.0
	if hover:
		_glow_line(sigil, Vector2(1, base), Vector2(w - 2, base), Color(ink, a))
		# Light running in from both ends to the centre.
		var run := fmod((_clock - float(sigil.get_meta("hover_since", _clock))) * 0.9, 1.0)
		var reach := (mid - 2.0) * run
		for x in [1.0 + reach, w - 2.0 - reach]:
			sigil.draw_rect(Rect2(Vector2(roundf(x) - 1, base - 1), Vector2(3, 3)), Color(1, 1, 1, 0.75 * (1.0 - run)))
		# A crown of nodes over the word.
		for dx in [-12, -6, 6, 12]:
			sigil.draw_rect(Rect2(Vector2(mid + dx, -1 + absi(dx) / 6), Vector2(1, 1)), Color(ink, 0.6))
		_diamond(sigil, Vector2(mid, -3), 1.5, Color(ink, 0.95), true)
	else:
		_glow_line(sigil, Vector2(1, base), Vector2(10, base), c)
		_glow_line(sigil, Vector2(w - 11, base), Vector2(w - 2, base), c)
		for x in range(12, int(mid - gap), 2):
			sigil.draw_rect(Rect2(Vector2(x, base), Vector2(1, 1)), Color(ink, a * 0.3))
		for x in range(int(mid + gap) + 1, int(w - 12), 2):
			sigil.draw_rect(Rect2(Vector2(x, base), Vector2(1, 1)), Color(ink, a * 0.3))
	sigil.draw_line(Vector2(1, base - 3), Vector2(1, base), c, 1.0)
	sigil.draw_line(Vector2(w - 2, base - 3), Vector2(w - 2, base), c, 1.0)
	_diamond(sigil, Vector2(1, base), 1.5, Color(ink, a), true)
	_diamond(sigil, Vector2(w - 2, base), 1.5, Color(ink, a), true)
	sigil.draw_line(Vector2(5, base + 2.5), Vector2(w - 6, base + 2.5), Color(ink, a * 0.2), 1.0)
	# Focus cost: nodes set into the middle of the line, breathing while the word can be used.
	var left := mid - (cost - 1) * 4.0
	for i in cost:
		var node_a := a * (breathe if usable and not hover else 1.0)
		_halo(sigil, Vector2(left + i * 8, base), 4.0, Color(ink, node_a * 0.35))
		_diamond(sigil, Vector2(left + i * 8, base), 2.5, Color(ink, node_a), true)
	# Marks at the top right: kept for next turn, cannot be used, chosen to replace.
	var corner := Vector2(w - 9, 1)
	if retained:
		sigil.draw_polyline(PackedVector2Array([corner + Vector2(0, 6), corner, corner + Vector2(6, 0), corner + Vector2(6, 6)]), ink, 1.0)
		sigil.draw_line(corner + Vector2(0, 6), corner + Vector2(3, 4), ink, 1.0)
		sigil.draw_line(corner + Vector2(6, 6), corner + Vector2(3, 4), ink, 1.0)
	if blocked:
		sigil.draw_line(corner + Vector2(2, 1), corner + Vector2(6, 5), Color(ink, 0.55), 1.0)
		sigil.draw_line(corner + Vector2(6, 1), corner + Vector2(2, 5), Color(ink, 0.55), 1.0)
	if uid in selected_mulligan:
		sigil.draw_polyline(PackedVector2Array([corner + Vector2(6, 0), corner + Vector2(6, 5), corner + Vector2(0, 5)]), ink, 1.0)
		sigil.draw_line(corner + Vector2(0, 5), corner + Vector2(2, 3), ink, 1.0)
		sigil.draw_line(corner + Vector2(0, 5), corner + Vector2(2, 7), ink, 1.0)


## A used word leaves the bar (about half a second): the line draws in to its centre, the letters
## flare one by one and drift up as cyan pixels, and the centre node flies off to the hero, who
## then speaks the word. Drawn on a ghost at the word's old place, since the bar rebuilds at once.
func _dissolve(word: String, rect: Rect2) -> void:
	var ghost := Control.new()
	ghost.position = rect.position - _ui.global_position
	ghost.size = rect.size
	ghost.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ghost.set_meta("t0", _clock)
	ghost.set_meta("word", word)
	ghost.set_meta("to", _to_screen(hero.global_position + HERO_CHEST) - ghost.position if is_instance_valid(hero) else Vector2.ZERO)
	ghost.draw.connect(_draw_dissolve.bind(ghost))
	_floats.add_child(ghost)
	get_tree().create_timer(DISSOLVE_TIME + 0.1).timeout.connect(ghost.queue_free)


func _draw_dissolve(ghost: Control) -> void:
	var t := (_clock - float(ghost.get_meta("t0"))) / DISSOLVE_TIME # 0 → 1
	var word := str(ghost.get_meta("word"))
	var w := ghost.size.x
	var base := 28.0
	var mid := roundf(w / 2.0)
	# 1. The line draws in to its centre (first 40 %).
	var close := clampf(t / 0.4, 0.0, 1.0)
	if close < 1.0:
		var half := (mid - 1.0) * (1.0 - close)
		_glow_line(ghost, Vector2(mid - half, base), Vector2(mid + half, base), Color(CYAN, 1.0 - close * 0.3))
	# 2. Each letter flares, then breaks into a few pixels drifting up and fading.
	var x := 23.0
	for i in word.length():
		var ch := word[i]
		var local := clampf((t - 0.05 - i * 0.04) / 0.5, 0.0, 1.0)
		var adv := FONT.get_string_size(ch, HORIZONTAL_ALIGNMENT_LEFT, -1, SIGIL_FONT).x
		if local < 0.25:
			var flare := Color(CYAN.lerp(Color.WHITE, local * 3.0), 1.0)
			ghost.draw_char(FONT, Vector2(x, 20), ch, SIGIL_FONT, flare)
		else:
			var e := (local - 0.25) / 0.75
			for k in 3:
				var seed := float(i * 7 + k * 13)
				var drift := Vector2(sin(seed) * 6.0 * e, -18.0 * e - k * 3.0 * e)
				var at := (Vector2(x + adv * (0.25 + 0.25 * k), 12 + k * 3) + drift).round()
				ghost.draw_rect(Rect2(at, Vector2(1, 1)), Color(CYAN, 1.0 - e))
		x += adv
	# 3. The centre node flies to the hero (last 45 %).
	var fly := clampf((t - 0.55) / 0.45, 0.0, 1.0)
	if fly > 0.0 and fly < 1.0:
		var to: Vector2 = ghost.get_meta("to")
		var at := Vector2(mid, base).lerp(to, fly * fly)
		_halo(ghost, at, 5.0, Color(CYAN, 0.5))
		_diamond(ghost, at.round(), 2.5, CYAN, true)
	elif close >= 1.0 and fly <= 0.0:
		_halo(ghost, Vector2(mid, base), 5.0, Color(CYAN, 0.6))
		_diamond(ghost, Vector2(mid, base), 2.5, Color.WHITE, true)


# Soft light (smooth is allowed for light, Art Bible v3 §7) under crisp 1-pixel strokes.
func _glow_line(ci: CanvasItem, from: Vector2, to: Vector2, color: Color) -> void:
	ci.draw_line(from, to, Color(color, color.a * 0.07), 7.0, true)
	ci.draw_line(from, to, Color(color, color.a * 0.16), 3.0, true)
	ci.draw_line(from, to, color, 1.0)


func _glow_text(ci: CanvasItem, at: Vector2, text: String, size: int, color: Color) -> void:
	ci.draw_string_outline(FONT, at, text, HORIZONTAL_ALIGNMENT_LEFT, -1, size, 9, Color(color, color.a * 0.06))
	ci.draw_string_outline(FONT, at, text, HORIZONTAL_ALIGNMENT_LEFT, -1, size, 4, Color(color, color.a * 0.14))
	ci.draw_string(FONT, at, text, HORIZONTAL_ALIGNMENT_LEFT, -1, size, color)


func _halo(ci: CanvasItem, at: Vector2, r: float, color: Color) -> void:
	for i in 3:
		ci.draw_circle(at, r * (1.0 + i * 0.6), Color(color, color.a * (0.35 - i * 0.1)))


func _glyph(ci: CanvasItem, at: Vector2, rows: Array, color: Color) -> void:
	for j in rows.size():
		var row: String = rows[j]
		for i in row.length():
			if row[i] == "X":
				ci.draw_rect(Rect2(at + Vector2(i, j), Vector2(1, 1)), color)


func _draw_vitals() -> void:
	var font: Font = FONT
	_vitals.draw_string(font, Vector2(0, 12), "HP", HORIZONTAL_ALIGNMENT_LEFT, -1, 13, DIM)
	_vitals.draw_string(font, Vector2(24, 12), "%d / %d" % [combat.hp, CombatState.MAX_HP], HORIZONTAL_ALIGNMENT_LEFT, -1, 15, INK)
	_bar_line(_vitals, Vector2(0, 18), 150, float(combat.hp) / CombatState.MAX_HP, INK)
	_vitals.draw_string(font, Vector2(98, 12), "ARMOR %d" % combat.armor, HORIZONTAL_ALIGNMENT_LEFT, -1, 12, DIM)
	# Focus: language nodes, not a blue bar.
	for i in CombatState.BASE_FOCUS:
		_diamond(_vitals, Vector2(6 + i * 18, 34), 5.0, CYAN, i < combat.focus)
	# Corruption shows only when it is there.
	var parts: Array[String] = []
	for family in ["Decay", "Obscurity", "Inattention"]:
		if int(combat.corruption[family]) > 0:
			parts.append("%s %d" % [family.to_upper(), int(combat.corruption[family])])
	_vitals.draw_string(font, Vector2(0, 58), "   ".join(parts), HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color(0.72, 0.64, 0.82))


# --- Over the enemy ----------------------------------------------------------------------

func _enemy_values() -> Dictionary:
	if combat.enemy.is_empty():
		return {}
	return {"hp": int(combat.enemy.hp), "max_hp": int(combat.enemy.max_hp), "structure": int(combat.enemy.structure),
		"max_structure": int(combat.enemy.max_structure), "remains": combat.bone_remains, "integrity": combat.remains_hp,
		"max_integrity": combat.remains_integrity}


## The intent as far as the hero understands it, and how complete its sign is (0, 1, 2).
func intent_text() -> Array:
	var intent := combat.intent
	if intent.is_empty() or combat.finished:
		return ["", 2]
	if combat.bone_remains:
		return ["REASSEMBLE · %d" % combat.reassembly_countdown, 2]
	if not combat.false_intent.is_empty() and not combat.false_removed:
		return ["%s / %s ?" % [combat.intent_options[0], combat.intent_options[1]], 1]
	if bool(intent.get("hidden", false)) and not combat.hidden_revealed:
		return ["?", 0]
	var word := str(intent.word)
	if combat.inattention_tier == 4:
		return [word + " ?", 1]
	var bound := "  · BOUND" if combat.delayed_this_turn else ""
	match combat.intent_clarity:
		0: return ["?" + bound, 0]
		1: return [word + " ?" + bound, 1]
	var amount := str(int(intent.damage)) if str(intent.kind) == "physical" else "%s +%d" % [str(intent.family).to_upper(), int(intent.get("corruption", 0))]
	return ["%s · %s%s" % [word, amount, bound], 2]


func _draw_tag() -> void:
	if _shown.is_empty():
		return
	var font: Font = FONT
	var w := _tag.size.x
	var intent := intent_text()
	if not str(intent[0]).is_empty():
		var sign_at := Vector2(6, 8)
		match int(intent[1]):
			2: _tag.draw_arc(sign_at, 5, 0, TAU, 16, CYAN, 1.0)
			1: _tag.draw_arc(sign_at, 5, PI * 0.5, PI * 1.5, 9, CYAN, 1.0)
			0:
				for i in 6:
					_tag.draw_arc(sign_at, 5, i * TAU / 6, i * TAU / 6 + 0.5, 3, Color(CYAN, 0.7), 1.0)
		_tag.draw_string(font, Vector2(16, 13), str(intent[0]), HORIZONTAL_ALIGNMENT_LEFT, w - 16, 15, CYAN)
	_tag.draw_string(font, Vector2(0, 29), enemy_name, HORIZONTAL_ALIGNMENT_LEFT, w, 11, DIM)
	if bool(_shown.remains):
		_tag.draw_string(font, Vector2(0, 43), "REMAINS %d" % int(_shown.integrity), HORIZONTAL_ALIGNMENT_LEFT, -1, 11, INK)
		_bar_line(_tag, Vector2(0, 49), w, float(_shown.integrity) / maxi(1, int(_shown.max_integrity)), INK)
		return
	_tag.draw_string(font, Vector2(0, 43), "HP %d" % int(_shown.hp), HORIZONTAL_ALIGNMENT_LEFT, -1, 11, INK)
	_tag.draw_string(font, Vector2(52, 43), "STRUCT %d" % int(_shown.structure), HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Color(0.7, 0.78, 0.8))
	_bar_line(_tag, Vector2(0, 49), w, float(_shown.hp) / maxi(1, int(_shown.max_hp)), INK)
	_bar_line(_tag, Vector2(0, 53), w, float(_shown.structure) / maxi(1, int(_shown.max_structure)), Color(0.7, 0.78, 0.8))
	var effects := combat.enemy_effects.rows()
	if not effects.is_empty():
		_tag.draw_string(font, Vector2(0, 66), "  ".join(effects).to_upper(), HORIZONTAL_ALIGNMENT_LEFT, w + 60, 10, CYAN)


# --- Tips ----------------------------------------------------------------------------------
# The hover card, drawn like the sigils (level 3): a precise instrument, not a plain box. Header
# with the family mark, the word in cyan and its family in small letters; a rule with a node at its
# centre; effects as label → value columns (keywords stay cyan, the language colour); a double
# hairline frame with corner ticks and nodes, and a short stem down to the word it belongs to.

const TIP_W := 236.0

func _build_tip() -> void:
	_tip = PanelContainer.new()
	var style := StyleBoxFlat.new() # only holds the palette colours and the margins; _draw_tip paints
	style.draw_center = false
	style.set_content_margin_all(10)
	style.content_margin_top = 9
	style.content_margin_bottom = 9
	_tip.add_theme_stylebox_override("panel", style)
	_tip.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_tip.draw.connect(_draw_tip)
	_tip_rows = VBoxContainer.new()
	_tip_rows.add_theme_constant_override("separation", 2)
	_tip.add_child(_tip_rows)
	_tip.hide()
	_ui.add_child(_tip)


func _draw_tip() -> void:
	var p: Dictionary = PALETTES[palette]
	var r := Rect2(Vector2.ZERO, _tip.size)
	var edge: Color = p.edge
	_tip.draw_rect(r, p.panel)
	_tip.draw_rect(Rect2(r.position, Vector2(r.size.x, 30)), Color(edge, 0.06)) # header band
	_tip.draw_rect(r.grow(-0.5), edge, false, 1.0)
	_tip.draw_rect(r.grow(-3.5), Color(edge, edge.a * 0.35), false, 1.0)
	for corner in [r.position, Vector2(r.end.x, r.position.y), r.end, Vector2(r.position.x, r.end.y)]:
		var sx := 1.0 if corner.x == r.position.x else -1.0
		var sy := 1.0 if corner.y == r.position.y else -1.0
		var c: Vector2 = corner + Vector2(sx * 0.5, sy * 0.5)
		_tip.draw_line(c, c + Vector2(sx * 9, 0), Color(edge, 1.0), 2.0)
		_tip.draw_line(c, c + Vector2(0, sy * 9), Color(edge, 1.0), 2.0)
		_diamond(_tip, c + Vector2(sx * 6, sy * 6), 1.5, Color(edge, 1.0), true)
	# The stem to the word: a node on the edge and a short tick beyond it.
	var stem_y := r.end.y if _tip_above else 0.0
	var dir := 1.0 if _tip_above else -1.0
	var mid := roundf(_tip_anchor_x - _tip.position.x)
	_tip.draw_line(Vector2(mid, stem_y), Vector2(mid, stem_y + dir * 5), edge, 1.0)
	_diamond(_tip, Vector2(mid, stem_y), 2.5, p.panel, true)
	_diamond(_tip, Vector2(mid, stem_y), 2.5, Color(edge, 1.0), false)


var _tip_above := true
var _tip_anchor_x := 0.0


## rows: {kind: "title", word, family, mark} · {kind: "rule"} · {kind: "sense", text} ·
## {kind: "stat", key, value, extra} · {kind: "text", text} · {kind: "hint", text, color}
func _show_tip(rows: Array, anchor: Rect2, above := true) -> void:
	for child in _tip_rows.get_children():
		_tip_rows.remove_child(child)
		child.queue_free()
	for row in rows:
		_tip_rows.add_child(_tip_row(row))
	_tip.reset_size()
	_tip.modulate.a = 0.0
	_tip.show()
	await get_tree().process_frame # let the panel size itself
	var size := _tip.get_combined_minimum_size()
	_tip_above = above
	_tip_anchor_x = anchor.get_center().x
	var at := Vector2(anchor.get_center().x - size.x / 2.0, anchor.position.y - size.y - 9 if above else anchor.end.y + 9)
	# Over the bar it keeps clear of the HP and Focus corner.
	var left := 222.0 if anchor.position.y >= BAR_TOP else 6.0
	_tip.position = at.clamp(Vector2(left, 6), NATIVE - size - Vector2(6, 6)).round()
	_tip_anchor_x = clampf(_tip_anchor_x, _tip.position.x + 14, _tip.position.x + size.x - 14)
	var rest := _tip.position
	_tip.position.y += 4.0 if above else -4.0
	var tween := _tip.create_tween().set_parallel()
	tween.tween_property(_tip, "modulate:a", 1.0, 0.12)
	tween.tween_property(_tip, "position", rest, 0.12).set_trans(Tween.TRANS_SINE)
	_tip.queue_redraw()


func _tip_row(row: Dictionary) -> Control:
	match str(row.kind):
		"title":
			var line := HBoxContainer.new()
			line.add_theme_constant_override("separation", 7)
			var mark := Control.new()
			mark.custom_minimum_size = Vector2(11, 22)
			var rows: Array = row.get("mark", [])
			mark.draw.connect(func(): _glyph(mark, Vector2(0, 6), rows, CYAN))
			line.add_child(mark)
			var word := Label.new()
			word.text = str(row.word)
			word.add_theme_font_override("font", FONT)
			word.add_theme_font_size_override("font_size", 20)
			word.add_theme_color_override("font_color", CYAN)
			word.add_theme_color_override("font_outline_color", Color(CYAN, 0.16))
			word.add_theme_constant_override("outline_size", 4)
			word.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			line.add_child(word)
			var family := _label(str(row.get("family", "")), 10, DIM)
			family.size_flags_vertical = Control.SIZE_SHRINK_CENTER
			line.add_child(family)
			return line
		"rule":
			var rule := Control.new()
			rule.custom_minimum_size = Vector2(TIP_W, 9)
			rule.draw.connect(func():
				var edge: Color = PALETTES[palette].edge
				var y := 4.5
				var w := rule.size.x
				rule.draw_line(Vector2(0, y), Vector2(w / 2 - 6, y), Color(edge, 0.9), 1.0)
				rule.draw_line(Vector2(w / 2 + 6, y), Vector2(w, y), Color(edge, 0.9), 1.0)
				for x in [w / 2 - 10, w / 2 + 10]:
					rule.draw_rect(Rect2(Vector2(x, y - 0.5), Vector2(1, 1)), edge)
				_diamond(rule, Vector2(w / 2, y), 2.5, Color(CYAN, 0.85), true))
			return rule
		"sense":
			var sense := _label("“%s”" % str(row.text), 14, INK)
			sense.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			sense.custom_minimum_size.x = TIP_W
			return sense
		"stat":
			var line := HBoxContainer.new()
			line.custom_minimum_size.x = TIP_W
			var key := _label(str(row.key), 12, DIM)
			key.custom_minimum_size.x = 84
			key.size_flags_vertical = Control.SIZE_SHRINK_CENTER
			line.add_child(key)
			var value := _label(str(row.value), 15, INK)
			value.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			line.add_child(value)
			if not str(row.get("extra", "")).is_empty():
				var extra := _label(str(row.extra), 13, CYAN)
				extra.size_flags_vertical = Control.SIZE_SHRINK_CENTER
				line.add_child(extra)
			return line
		"hint":
			var hint := _label(str(row.text), 11, row.get("color", DIM))
			hint.custom_minimum_size.x = TIP_W
			hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
			return hint
	var text := _label(str(row.get("text", "")), 13, INK)
	text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	text.custom_minimum_size.x = TIP_W
	return text


func _hide_tip() -> void:
	_tip.hide()


func _show_word_tip(card: Dictionary, button: Control) -> void:
	var word := str(card.name)
	var skill: Dictionary = CombatContent.SKILLS.get(str(card.card_id), {})
	var family := str(skill.get("family", ""))
	var rows: Array = [{"kind": "title", "word": word, "family": family.replace("SEMANTIC ", "").replace("DIRECT HP", "DIRECT"), "mark": FAMILY_MARKS.get(family, FAMILY_MARKS[""])}]
	rows.append({"kind": "rule"})
	if skill.has("sense"):
		rows.append({"kind": "sense", "text": str(skill.sense)})
	for line in preview(card):
		rows.append(_stat_row(line))
	var reason := combat.disabled_reason(word, int(card.instance_id))
	if not reason.is_empty() and not combat.deck.mulligan_pending:
		rows.append({"kind": "hint", "text": reason, "color": HURT})
	if bool(card.get("borrowed", false)):
		rows.append({"kind": "hint", "text": "BORROWED · half known, lent for one use. Try it on the remains."})
	if int(card.instance_id) in combat.deck.retained_cards:
		rows.append({"kind": "hint", "text": "RETAINED · kept for next turn", "color": CYAN})
	elif combat.retain_disabled_reason(card).is_empty():
		rows.append({"kind": "hint", "text": "right-click · retain for next turn"})
	_show_tip(rows, button.get_global_rect())


## "STRUCTURE 12 → 4  ·  EXPOSED" → label STRUCTURE, value 12 → 4, keyword EXPOSED.
func _stat_row(line: String) -> Dictionary:
	var parts := line.split("  ·  ")
	var head := parts[0]
	var cut := -1
	for i in head.length():
		if head[i] in "0123456789-+" and i > 0 and head[i - 1] == " ":
			cut = i
			break
	var extra := " · ".join(parts.slice(1)) if parts.size() > 1 else ""
	if cut < 0:
		return {"kind": "text", "text": line}
	return {"kind": "stat", "key": head.substr(0, cut).strip_edges(), "value": head.substr(cut), "extra": extra}


func _show_intent_tip() -> void:
	var text := combat.intent_description()
	if text.is_empty():
		return
	_show_tip([{"kind": "title", "word": str(intent_text()[0]), "family": "INTENT · " + combat.clarity_name(), "mark": []}, {"kind": "rule"}, {"kind": "text", "text": text}], _tag.get_global_rect(), false)


## What a word will do right now, in numbers (KB: knowledge removes helplessness, not danger).
func preview(card: Dictionary) -> Array[String]:
	var word := str(card.card_id)
	var lines: Array[String] = []
	var cost := combat.card_cost(card)
	var e := combat.enemy
	if combat.bone_remains and word in ["SHATTER", "STRIKE"]:
		var hit := 8 if word == "SHATTER" else 3
		lines.append("REMAINS %d → %d%s" % [combat.remains_hp, maxi(0, combat.remains_hp - hit), "  ·  they stay down" if combat.remains_hp <= hit else ""])
	elif combat.bone_remains and word == "BIND":
		lines.append("REASSEMBLE %d → %d rounds" % [combat.reassembly_countdown, combat.reassembly_countdown + 1])
	else:
		match word:
			"SHATTER":
				if int(e.structure) > 0:
					lines.append("STRUCTURE %d → %d%s" % [int(e.structure), maxi(0, int(e.structure) - 8), "  ·  EXPOSED" if int(e.structure) <= 8 else ""])
				else:
					lines.append("ARMOR -2  ·  HP -3")
			"STRIKE":
				var damage := 8 + (2 if combat.enemy_effects.has("EXPOSED") else 0)
				if str(e.phase_state) == "FADED":
					damage = int(damage / 2)
				var through := mini(int(e.armor), 3 if combat.erode_played_this_turn else 0)
				var absorbed := mini(maxi(0, int(e.armor) - through), damage)
				lines.append("HP %d → %d" % [int(e.hp), maxi(0, int(e.hp) - damage + absorbed)])
				if int(e.structure) > 0:
					lines.append("STRUCTURE %d → %d%s" % [int(e.structure), maxi(0, int(e.structure) - 2), "  ·  EXPOSED" if int(e.structure) <= 2 else ""])
			"BIND":
				lines.append("%s waits one turn" % (str(combat.intent.word) if combat.intent_clarity > 0 else "Its next action"))
			"OBSERVE":
				lines.append("INTENT %s → %s" % [combat.clarity_name(), ["OBSERVED", "PARTIAL", "CLEAR"][mini(2, combat.intent_clarity + 1)]])
			"ERODE":
				lines.append("EROSION 3 turns  ·  STRUCTURE -2 each turn")
			"TOXIC":
				lines.append("POISONED %d turns  ·  HP -%d each turn" % [CombatState.POISON_TURNS, CombatState.POISON_TICK])
			"STABILIZE":
				var family := combat.dominant_corruption_family()
				if not family.is_empty():
					lines.append("%s %d → %d" % [family.to_upper(), int(combat.corruption[family]), maxi(0, int(combat.corruption[family]) - CombatState.STABILIZE_AMOUNT)])
			"RESTORE":
				lines.append("HP %d → %d" % [combat.hp, mini(CombatState.MAX_HP, combat.hp + (int(CombatState.RESTORE_HP * 0.75) if combat.statuses.has("WITHERED") else CombatState.RESTORE_HP))] if combat.hp < CombatState.MAX_HP else "ARMOR %d → %d" % [combat.armor, mini(CombatState.BASE_ARMOR, combat.armor + CombatState.RESTORE_ARMOR)])
			"ANCHOR":
				lines.append("Next wearing-away (Decay, Armor loss) prevented")
			"DEFLECT":
				lines.append("Answers an attack as it comes")
	if word != "DEFLECT":
		lines.append("FOCUS %d → %d" % [combat.focus, combat.focus - cost])
	return lines


# --- Casting -------------------------------------------------------------------------------

## Call right before the rules resolve a word: the enemy's look waits until the word lands.
func hold_enemy(uid := -1) -> Dictionary:
	_holding = true
	_leaving = {}
	for sigil in _words.get_children():
		if int(sigil.get_meta("uid", -2)) == uid:
			_leaving = {"rect": sigil.get_global_rect(), "index": sigil.get_index()}
	if is_instance_valid(enemy):
		enemy.get_node("VisualRoot/Visual").hold_for(LEAD + IMPACT_AT)
	return _snapshot()


func release_enemy() -> void:
	_holding = false
	refresh()


func _snapshot() -> Dictionary:
	return {"enemy": _enemy_values(), "hero_hp": combat.hp, "armor": combat.armor, "clarity": combat.intent_clarity,
		"bound": combat.delayed_this_turn, "phase": str(combat.enemy.get("phase_state", "")), "corruption": combat.corruption.duplicate()}


## The rules have resolved card; now show it: word by the hero, its shape flies, the enemy reacts.
func play_cast(card: Dictionary, before: Dictionary) -> void:
	busy = true
	refresh()
	var word := str(card.card_id)
	if not _leaving.is_empty():
		_dissolve(str(card.name), _leaving.rect)
		_gap_index = int(_leaving.index)
		_gap_w = _leaving.rect.size.x
		_leaving = {}
		refresh()
		var close := create_tween()
		close.tween_interval(DISSOLVE_TIME)
		close.tween_property(self, "_gap_w", 0.0, 0.3).set_trans(Tween.TRANS_SINE)
		close.tween_callback(func():
			_gap_index = -1
			refresh())
	# The hero lifts a hand as the word arrives; its shape leaves on the release frame.
	var release := 0.0
	if is_instance_valid(hero) and hero.has_method("cast"):
		await get_tree().create_timer(maxf(0.0, LEAD - 0.29)).timeout
		release = hero.cast()
		await get_tree().create_timer(release if release > 0.0 else 0.29).timeout
	else:
		await get_tree().create_timer(LEAD).timeout
	var to_enemy := signf(enemy.global_position.x - hero.global_position.x) if is_instance_valid(enemy) else 1.0
	var origin := hero.global_position + HERO_CHEST + Vector2(to_enemy * 22, 0)
	var target := enemy.global_position + ENEMY_BODY if is_instance_valid(enemy) else origin
	_fx.append({"word": word, "t0": _clock, "from": origin.round(), "to": target.round(), "hero": hero.global_position.round()})
	_cast_word(word, hero.global_position + Vector2(0, -112))
	await get_tree().create_timer(IMPACT_AT).timeout
	_impact(word, before)
	await get_tree().create_timer(CAST_TIME - IMPACT_AT).timeout
	busy = false
	refresh()


func _impact(word: String, before: Dictionary) -> void:
	var after := _snapshot()
	_holding = false
	_shown = _enemy_values()
	_tag.queue_redraw()
	# Beside the enemy, clear of its tag above: numbers at its shoulder, words a little higher.
	var at := (enemy.global_position + Vector2(signf(enemy.global_position.x - hero.global_position.x) * 44, -70)) if is_instance_valid(enemy) else Vector2(480, 200)
	var b: Dictionary = before.enemy
	var a: Dictionary = after.enemy
	var shook := false
	if int(a.hp) < int(b.hp):
		_float("-%d" % (int(b.hp) - int(a.hp)), at + Vector2(-14, 0), INK, 15)
		shook = true
	if int(a.structure) < int(b.structure):
		_float("-%d" % (int(b.structure) - int(a.structure)), at + Vector2(16, 6), Color(0.7, 0.78, 0.8), 13)
		shook = true
	if int(b.structure) > 0 and int(a.structure) == 0:
		_hit_stop(0.14)
		_float("EXPOSED", at + Vector2(0, -18), CYAN, 17, 0.14)
	if bool(a.remains) and not bool(b.remains):
		_hit_stop(0.18)
		_float("COLLAPSED", at + Vector2(0, -18), CYAN, 17, 0.18)
	if bool(a.remains) and bool(b.remains) and int(a.integrity) < int(b.integrity):
		_float("-%d" % (int(b.integrity) - int(a.integrity)), at, INK, 15)
		shook = true
	if combat.finished and combat.hp > 0:
		_hit_stop(0.2)
	if after.clarity > before.clarity:
		_float(combat.clarity_name(), at + Vector2(0, -18), CYAN, 15)
	if after.phase != before.phase and after.phase == "REVEALED":
		_float("REVEALED", at + Vector2(0, -34), CYAN, 15)
	if after.bound and not before.bound:
		_float("BOUND", at + Vector2(0, -18), CYAN, 15)
	var hero_at := hero.global_position + Vector2(0, -108)
	if int(after.hero_hp) > int(before.hero_hp):
		_float("+%d" % (int(after.hero_hp) - int(before.hero_hp)), hero_at, INK, 15)
	if int(after.armor) > int(before.armor):
		_float("ARMOR +%d" % (int(after.armor) - int(before.armor)), hero_at, CYAN, 13)
	if word == "STABILIZE":
		_float("STABILIZED", hero_at, CYAN, 14)
	_last_hero_hp = combat.hp
	if shook:
		_shake(0.12)
	_reality(word, shook, bool(a.remains) and not bool(b.remains))


## The world answers the word (§7 of the combat animation request): bone chips fly off away from
## the hero, a puff of bone ash rises; words that cut (SHATTER, STRIKE) also tear shroud threads;
## a collapse throws more bone and raises the ash from the ground.
func _reality(word: String, hurt: bool, collapsed: bool) -> void:
	if not is_instance_valid(enemy) or not (hurt or collapsed):
		return
	var ground := enemy.global_position
	var away := signf(enemy.global_position.x - hero.global_position.x) if is_instance_valid(hero) else 1.0
	var parent := enemy.get_parent()
	if collapsed:
		RealityFx.chips(parent, ground, 30.0, away, 4)
		RealityFx.dust(parent, ground + Vector2(0, 2))
		return
	# Knocked out of the far side of the body, over the ground: drawn over the skeleton itself the
	# ash and threads vanish into the bone and shroud of the same colours.
	RealityFx.chips(parent, ground, 46.0, away, randi_range(2, 3))
	RealityFx.dust(parent, ground + Vector2(away * 22, 2), 26.0)
	if word in ["SHATTER", "STRIKE"]:
		RealityFx.threads(parent, ground + Vector2(away * 24, 3), 50.0)


## The enemy's attack is under way: hold the hero's hit until its hit frame, and keep the bar
## quiet until the attack has finished playing.
func enemy_attack(hit_in: float, total: float) -> void:
	busy = true
	refresh()
	await get_tree().create_timer(hit_in).timeout
	if is_instance_valid(hero):
		if combat.hp < _last_hero_hp:
			_float("-%d" % (_last_hero_hp - combat.hp), hero.global_position + Vector2(0, -108), HURT, 16)
			_shake(0.14)
		if hero.has_method("take_hit"):
			hero.take_hit()
		if is_instance_valid(enemy): # BONE CUT: splinters off the bone blade where it meets the hero
			var toward := signf(hero.global_position.x - enemy.global_position.x)
			RealityFx.chips(enemy.get_parent(), hero.global_position + Vector2(-toward * 14, 2), 52.0, toward, 2)
	_last_hero_hp = combat.hp
	await get_tree().create_timer(maxf(0.0, total - hit_in)).timeout
	busy = false
	refresh()


func _on_changed() -> void:
	if not active:
		return
	# Hits taken on the enemy's turn (casting covers the hero's own changes).
	if not busy and _last_hero_hp >= 0 and combat.hp < _last_hero_hp and is_instance_valid(hero):
		_float("-%d" % (_last_hero_hp - combat.hp), hero.global_position + Vector2(0, -108), HURT, 16)
		_shake(0.14)
	if not busy:
		_last_hero_hp = combat.hp
	if combat.deck.mulligan_pending == false:
		selected_mulligan.clear()
	if not combat.turn_ending:
		_reaction = {}
	refresh()


## The word appears by the hero first (KB: Language → Reality), sharp and steady.
func _cast_word(word: String, world_at: Vector2) -> void:
	var label := _label(word, 18, CYAN)
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.size = Vector2(160, 24)
	label.position = (_to_screen(world_at) - Vector2(80, 12)).round()
	label.modulate.a = 0.0
	_floats.add_child(label)
	var tween := label.create_tween()
	tween.tween_property(label, "modulate:a", 1.0, 0.1)
	tween.tween_interval(IMPACT_AT + 0.1)
	tween.tween_property(label, "modulate:a", 0.0, 0.3)
	tween.tween_callback(label.queue_free)


func _float(text: String, world_at: Vector2, color: Color, size: int, delay := 0.0) -> void:
	var label := _label(text, size, color)
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.size = Vector2(140, 22)
	label.position = (_to_screen(world_at) - Vector2(70, 11)).round()
	label.modulate.a = 0.0
	_floats.add_child(label)
	var tween := label.create_tween()
	tween.tween_interval(delay)
	tween.tween_property(label, "modulate:a", 1.0, 0.08)
	tween.parallel().tween_property(label, "position:y", label.position.y - 10, 0.9).set_trans(Tween.TRANS_SINE)
	tween.tween_property(label, "modulate:a", 0.0, 0.35)
	tween.tween_callback(label.queue_free)


## A breath of stillness when something breaks (0.1 – 0.2 s), so it lands with weight.
func _hit_stop(seconds: float) -> void:
	Engine.time_scale = 0.02
	await get_tree().create_timer(seconds, true, false, true).timeout
	Engine.time_scale = 1.0


## A whole-pixel tremor of the world picture (never a sub-pixel one).
func _shake(seconds: float) -> void:
	var end := Time.get_ticks_msec() + int(seconds * 1000)
	while Time.get_ticks_msec() < end:
		_world_screen.position = Vector2(randi_range(-1, 1), randi_range(-1, 1))
		await get_tree().process_frame
	_world_screen.position = Vector2.ZERO


# --- Per frame -----------------------------------------------------------------------------

func _process(delta: float) -> void:
	_clock += delta
	var material := _vignette.material as ShaderMaterial
	material.set_shader_parameter("strength", _strength)
	if is_instance_valid(hero) and is_instance_valid(enemy):
		var mid := _to_screen((hero.global_position + enemy.global_position) / 2.0 + Vector2(0, -40))
		material.set_shader_parameter("center", mid / NATIVE)
	if active and is_instance_valid(enemy):
		var feet := _to_screen(enemy.global_position)
		_tag.position = (feet + Vector2(-_tag.size.x / 2.0, -170)).clamp(Vector2(6, 6), Vector2(NATIVE.x - _tag.size.x - 6, BAR_TOP - 80)).round()
		_tag.modulate.a = 1.0 if Rect2(_tag.position, _tag.size).has_point(_ui.get_local_mouse_position()) else 0.82
	if is_instance_valid(_gap):
		_gap.custom_minimum_size.x = maxf(0.0, _gap_w - 12.0)
	for sigil in _words.get_children():
		sigil.queue_redraw()
	for ghost in _floats.get_children():
		if ghost.has_meta("t0"):
			ghost.queue_redraw()
	_fx = _fx.filter(func(f): return _clock - float(f.t0) < CAST_TIME + 0.2)
	_fx_node.queue_redraw()


func _to_screen(world: Vector2) -> Vector2:
	return _viewport.canvas_transform * world


# --- Word shapes (pixel geometry on the language layer) -------------------------------------

func _draw_fx() -> void:
	if _strength > 0.01 and is_instance_valid(hero):
		# A faint language ring under the hero while the fight lasts.
		_ellipse(_fx_node, hero.global_position.round() + Vector2(0, -2), 22, 7, Color(CYAN, 0.3 * _strength))
	for f in _fx:
		var t: float = (_clock - float(f.t0)) / IMPACT_AT # 0 → 1 until it lands, then above 1
		var from: Vector2 = f.from
		var to: Vector2 = f.to
		var fade := clampf(1.0 - (t - 1.0) / ((CAST_TIME - IMPACT_AT) / IMPACT_AT), 0.0, 1.0)
		var form := clampf(t / 0.4, 0.0, 1.0) # the sigil forms at the hero in the first part
		var c := Color(CYAN, fade if t > 1.0 else 1.0)
		match str(f.word):
			"SHATTER":
				_diamond(_fx_node, from, roundf(6 * form), c, false)
				if t > 0.4:
					var reach := clampf((t - 0.4) / 0.6, 0.0, 1.0)
					_fx_node.draw_line(from, from.lerp(to, reach).round(), Color(c, c.a * 0.8), -1.0)
				if t > 1.0:
					var grow := clampf((t - 1.0) * 3.0, 0.0, 1.0)
					for i in 8:
						var dir := Vector2.from_angle(i * TAU / 8 + 0.2)
						var kink := to + (dir * 9 * grow).round()
						_fx_node.draw_line(to, kink, c, -1.0)
						_fx_node.draw_line(kink, kink + (dir.rotated(0.5 if i % 2 == 0 else -0.5) * 14 * grow).round(), c, -1.0)
			"STRIKE":
				_fx_node.draw_line(from + Vector2(0, -4), from + Vector2(0, 4), c, -1.0)
				if t > 0.6:
					_fx_node.draw_line(from, to, c, -1.0)
				if t > 1.0:
					_fx_node.draw_line(to + Vector2(-6, -6), to + Vector2(6, 6), c, -1.0)
					_fx_node.draw_line(to + Vector2(-6, 6), to + Vector2(6, -6), c, -1.0)
			"BIND":
				_diamond(_fx_node, from, roundf(5 * form), c, false)
				if t > 0.4:
					var r := roundf(lerpf(40, 18, clampf((t - 0.4) / 1.2, 0.0, 1.0)))
					_ellipse(_fx_node, to, r, roundf(r * 0.9), c)
					var nodes: Array[Vector2] = []
					for i in 3:
						nodes.append((to + Vector2.from_angle(-PI / 2 + i * TAU / 3) * r).round())
					for i in 3:
						_fx_node.draw_rect(Rect2(nodes[i] - Vector2(1, 1), Vector2(3, 3)), c)
						_fx_node.draw_line(nodes[i], nodes[(i + 1) % 3], Color(c, c.a * 0.6), -1.0)
			"OBSERVE":
				# No beam: the lens settles on the enemy and what was blurred becomes clear.
				if t > 0.3:
					var sweep := clampf((t - 0.3) / 0.9, 0.0, 1.0)
					var at := to + Vector2(roundf(lerpf(-16, 0, sweep)), 0)
					_ellipse(_fx_node, at, 18, 8, c)
					_fx_node.draw_rect(Rect2(at - Vector2(1, 1), Vector2(3, 3)), c)
			"ERODE":
				_diamond(_fx_node, from, roundf(5 * form), c, false)
				if t > 0.6:
					var gone := clampf((t - 0.6) / 1.4, 0.0, 1.0) * 8 # rows already worn away, top down
					for row in 8:
						if row < int(gone):
							continue
						for col in 6:
							if (row + col) % 2 == 0:
								_fx_node.draw_rect(Rect2(to + Vector2(-15 + col * 6, -28 + row * 7), Vector2(1, 1)), c)
			"STABILIZE", "RESTORE":
				# The shaking around the hero settles into a steady hexagon.
				var centre: Vector2 = f.hero + Vector2(0, -44)
				var settle := clampf(t / 1.2, 0.0, 1.0)
				var points := PackedVector2Array()
				for i in 7:
					var jitter := Vector2(((i * 7 + int(_clock * 30)) % 5) - 2, ((i * 3 + int(_clock * 30)) % 5) - 2) * (1.0 - settle)
					points.append((centre + Vector2.from_angle(i * TAU / 6) * 30 + jitter).round())
				_fx_node.draw_polyline(points, c, -1.0)
			_:
				_diamond(_fx_node, from, roundf(5 * form), c, false)
				if t > 0.5:
					_fx_node.draw_line(from, to, c, -1.0)


# --- Small drawing and widget helpers --------------------------------------------------------

## In the pixel viewport a line must be a true 1-pixel primitive (-1): a 1-wide polygon line slips
## between pixels and drops out in places. On the sharp UI layer it is one native pixel wide.
func _width(ci: CanvasItem) -> float:
	return -1.0 if ci == _fx_node else 1.0


func _diamond(ci: CanvasItem, at: Vector2, r: float, color: Color, filled: bool) -> void:
	if r <= 0:
		return
	var points := PackedVector2Array([at + Vector2(0, -r), at + Vector2(r, 0), at + Vector2(0, r), at + Vector2(-r, 0)])
	if filled:
		ci.draw_colored_polygon(points, color)
	else:
		points.append(points[0])
		ci.draw_polyline(points, color, _width(ci))


func _ellipse(ci: CanvasItem, at: Vector2, rx: float, ry: float, color: Color) -> void:
	var points := PackedVector2Array()
	for i in 33:
		points.append((at + Vector2(cos(i * TAU / 32) * rx, sin(i * TAU / 32) * ry)).round())
	ci.draw_polyline(points, color, _width(ci))


func _bar_line(ci: CanvasItem, at: Vector2, width: float, share: float, color: Color) -> void:
	ci.draw_line(at, at + Vector2(width, 0), Color(color, 0.18), 2.0)
	ci.draw_line(at, at + Vector2(roundf(width * clampf(share, 0.0, 1.0)), 0), color, 2.0)


func _label(text: String, size: int, color: Color) -> Label:
	var label := Label.new()
	label.text = text
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	label.add_theme_font_override("font", FONT)
	label.add_theme_font_size_override("font_size", size)
	label.add_theme_color_override("font_color", color)
	label.add_theme_color_override("font_outline_color", Color(0.01, 0.02, 0.03, 0.85))
	label.add_theme_constant_override("outline_size", 3)
	return label


func _text_button(text: String, size: int) -> Button:
	var button := Button.new()
	button.text = text
	button.focus_mode = Control.FOCUS_NONE
	button.add_theme_font_override("font", FONT)
	button.add_theme_font_size_override("font_size", size)
	button.add_theme_color_override("font_color", CYAN)
	button.add_theme_color_override("font_hover_color", Color(0.75, 0.97, 1.0))
	button.add_theme_color_override("font_pressed_color", Color.WHITE)
	button.add_theme_color_override("font_disabled_color", Color(CYAN, 0.35))
	button.add_theme_color_override("font_outline_color", Color(0.01, 0.02, 0.03, 0.85))
	button.add_theme_constant_override("outline_size", 3)
	for state in ["normal", "hover", "pressed", "disabled", "focus"]:
		button.add_theme_stylebox_override(state, StyleBoxEmpty.new())
	return button
