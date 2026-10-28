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
const INK := Color(0.86, 0.89, 0.86)
const DIM := Color(0.56, 0.6, 0.62)
const HURT := Color(0.9, 0.45, 0.4)
const NATIVE := Vector2(960, 540)
const BAR_TOP := 432.0
const FONT := preload("res://art/ui/fonts/CormorantGaramond.ttf")
const VIGNETTE := preload("res://scripts/world/v3/combat_vignette.gdshader")
const IMPACT_AT := 0.42 # seconds from invoking to the word reaching the enemy
const CAST_TIME := 0.85 # the whole cast; clicks wait until it is over
const ENEMY_BODY := Vector2(0, -46) # from the feet to the middle of the body
const HERO_CHEST := Vector2(0, -50)

var combat: CombatState
var hero: Node2D
var enemy: Node2D # the skeleton's root
var enemy_name := "ENEMY"
var active := false
var busy := false
var selected_mulligan: Array[int] = []

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


func setup(viewport: SubViewport, language: CanvasLayer, world_screen: Control, model: CombatState) -> void:
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
	_words.add_theme_constant_override("separation", 10)
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
	for card in combat.deck.hand:
		_words.add_child(_word_button(card))
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


func _word_button(card: Dictionary) -> Button:
	var uid := int(card.instance_id)
	var word := str(card.name)
	var reason := combat.disabled_reason(word, uid)
	var button := _text_button(word, 18)
	button.custom_minimum_size = Vector2(84, 44)
	button.alignment = HORIZONTAL_ALIGNMENT_CENTER
	button.vertical_icon_alignment = VERTICAL_ALIGNMENT_TOP
	var usable := reason.is_empty() and not busy
	if combat.deck.mulligan_pending:
		usable = not busy
	button.set_meta("usable", usable)
	button.modulate.a = 1.0 if usable else 0.38
	button.mouse_filter = Control.MOUSE_FILTER_STOP
	button.draw.connect(_draw_word_frame.bind(button, card))
	button.gui_input.connect(func(event: InputEvent):
		if event is InputEventMouseButton and event.pressed:
			if event.button_index == MOUSE_BUTTON_LEFT:
				_press_word(card)
			elif event.button_index == MOUSE_BUTTON_RIGHT and not combat.deck.mulligan_pending:
				retain_requested.emit(uid))
	button.mouse_entered.connect(func():
		button.queue_redraw()
		_show_word_tip(card, button))
	button.mouse_exited.connect(func():
		button.queue_redraw()
		_hide_tip())
	return button


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


func _draw_word_frame(button: Button, card: Dictionary) -> void:
	var uid := int(card.instance_id)
	var r := Rect2(Vector2.ZERO, button.size).grow(-2)
	var hovered := button.is_hovered() and bool(button.get_meta("usable", false))
	var c := CYAN if hovered else Color(CYAN, 0.45)
	# Precise corner brackets; the whole frame closes while the word is under the mouse.
	var arm := r.size.x / 2.0 if hovered else 7.0
	for corner in [r.position, Vector2(r.end.x, r.position.y), r.end, Vector2(r.position.x, r.end.y)]:
		var sx := 1.0 if corner.x == r.position.x else -1.0
		var sy := 1.0 if corner.y == r.position.y else -1.0
		button.draw_line(corner, corner + Vector2(arm * sx, 0), c, 1.0)
		button.draw_line(corner, corner + Vector2(0, minf(arm, r.size.y / 2.0) * sy), c, 1.0)
	# Focus cost as small nodes under the word.
	var cost := combat.card_cost(card)
	var left := r.get_center().x - (cost - 1) * 4.5
	for i in cost:
		_diamond(button, Vector2(left + i * 9, r.end.y - 6), 2.5, Color(CYAN, 0.8), true)
	if uid in combat.deck.retained_cards:
		button.draw_line(Vector2(r.position.x + 10, r.end.y + 3), Vector2(r.end.x - 10, r.end.y + 3), CYAN, 1.0)
		button.draw_line(Vector2(r.position.x + 10, r.end.y + 5), Vector2(r.end.x - 10, r.end.y + 5), CYAN, 1.0)
	if uid in selected_mulligan:
		button.draw_line(Vector2(r.position.x + 6, r.get_center().y - 3), Vector2(r.end.x - 6, r.get_center().y - 3), HURT, 1.0)


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

func _build_tip() -> void:
	_tip = PanelContainer.new()
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.02, 0.03, 0.04, 0.93)
	style.border_color = Color(CYAN, 0.45)
	style.set_border_width_all(1)
	style.set_content_margin_all(8)
	_tip.add_theme_stylebox_override("panel", style)
	_tip.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_tip_rows = VBoxContainer.new()
	_tip_rows.add_theme_constant_override("separation", 1)
	_tip.add_child(_tip_rows)
	_tip.hide()
	_ui.add_child(_tip)


func _show_tip(rows: Array, anchor: Rect2, above := true) -> void:
	for child in _tip_rows.get_children():
		_tip_rows.remove_child(child)
		child.queue_free()
	for row in rows:
		var label := _label(str(row[0]), int(row[1]), row[2])
		label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		label.custom_minimum_size.x = 250
		_tip_rows.add_child(label)
	_tip.reset_size()
	_tip.show()
	await get_tree().process_frame # let the panel size itself
	var size := _tip.get_combined_minimum_size()
	var at := Vector2(anchor.get_center().x - size.x / 2.0, anchor.position.y - size.y - 6 if above else anchor.end.y + 6)
	_tip.position = at.clamp(Vector2(6, 6), NATIVE - size - Vector2(6, 6)).round()


func _hide_tip() -> void:
	_tip.hide()


func _show_word_tip(card: Dictionary, button: Control) -> void:
	var word := str(card.name)
	var rows: Array = [[word, 19, CYAN]]
	var skill: Dictionary = CombatContent.SKILLS.get(str(card.card_id), {})
	if skill.has("sense"):
		rows.append([str(skill.sense), 14, INK])
	for line in preview(card):
		rows.append([line, 14, INK])
	var reason := combat.disabled_reason(word, int(card.instance_id))
	if not reason.is_empty() and not combat.deck.mulligan_pending:
		rows.append([reason, 12, HURT])
	if int(card.instance_id) in combat.deck.retained_cards:
		rows.append(["RETAINED · kept for next turn", 12, CYAN])
	elif combat.retain_disabled_reason(card).is_empty():
		rows.append(["Right-click: retain for next turn", 12, DIM])
	_show_tip(rows, button.get_global_rect())


func _show_intent_tip() -> void:
	var text := combat.intent_description()
	if text.is_empty():
		return
	_show_tip([[str(intent_text()[0]), 16, CYAN], [text, 13, INK]], _tag.get_global_rect(), false)


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
				lines.append("POISONED 3 turns  ·  HP -3 each turn")
			"STABILIZE":
				var family := combat.dominant_corruption_family()
				if not family.is_empty():
					lines.append("%s %d → %d" % [family.to_upper(), int(combat.corruption[family]), maxi(0, int(combat.corruption[family]) - CombatState.STABILIZE_AMOUNT)])
			"RESTORE":
				lines.append("HP %d → %d" % [combat.hp, mini(CombatState.MAX_HP, combat.hp + (6 if combat.statuses.has("WITHERED") else 8))] if combat.hp < CombatState.MAX_HP else "ARMOR %d → %d" % [combat.armor, mini(CombatState.BASE_ARMOR, combat.armor + 4)])
			"DEFLECT":
				lines.append("Answers an attack as it comes")
	if word != "DEFLECT":
		lines.append("FOCUS %d → %d" % [combat.focus, combat.focus - cost])
	return lines


# --- Casting -------------------------------------------------------------------------------

## Call right before the rules resolve a word: the enemy's look waits until the word lands.
func hold_enemy() -> Dictionary:
	_holding = true
	if is_instance_valid(enemy):
		enemy.get_node("VisualRoot/Visual").hold_for(IMPACT_AT)
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
		_float("+%d" % (int(after.hero_hp) - int(before.hero_hp)), hero_at, CYAN, 15)
	if int(after.armor) > int(before.armor):
		_float("ARMOR +%d" % (int(after.armor) - int(before.armor)), hero_at, CYAN, 13)
	if word == "STABILIZE":
		_float("STABILIZED", hero_at, CYAN, 14)
	_last_hero_hp = combat.hp
	if shook:
		_shake(0.12)


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
