extends Control

const INK := Color("e8edf2")
const MUTED := Color("8997a8")
const GOLD := Color("d7b86c")
const BG := Color("0d1522")
const PANEL := Color("141f2e")
const PANEL_DARK := Color("101925")
const BORDER := Color("2a3b50")

var state := CombatState.new()
var modal: Control

var stage_label: Label
var hp_label: Label
var hp_bar: ProgressBar
var armor_label: Label
var focus_label: Label
var status_label: Label
var corruption_labels: Dictionary = {}
var corruption_bars: Dictionary = {}
var enemy_name: Label
var enemy_subtitle: Label
var enemy_family: Label
var enemy_hp_label: Label
var enemy_hp_bar: ProgressBar
var enemy_armor_label: Label
var enemy_armor_bar: ProgressBar
var intent_badge: Label
var intent_title: Label
var intent_text: RichTextLabel
var tutorial_label: Label
var log_text: RichTextLabel
var detail_label: RichTextLabel
var end_turn_button: Button
var skill_buttons: Dictionary = {}

func _ready() -> void:
	set_process_unhandled_key_input(true)
	_build_interface()
	state.changed.connect(_refresh)
	state.reaction_requested.connect(_show_reaction)
	state.battle_finished.connect(_on_battle_finished)
	state.start_battle(0)

func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, size), BG)
	for index in range(18):
		var y := 40.0 + float(index) * 43.0
		draw_line(Vector2(0, y), Vector2(size.x, y - 170), Color(0.12, 0.19, 0.27, 0.12), 1.0)
	draw_circle(Vector2(665, 250), 240, Color(0.08, 0.25, 0.29, 0.08))
	draw_circle(Vector2(665, 250), 165, Color(0.17, 0.36, 0.34, 0.045))

func _build_interface() -> void:
	var title := _make_label("ENGLISH GAME", Vector2(26, 16), Vector2(280, 32), 26, GOLD)
	title.add_theme_constant_override("outline_size", 5)
	title.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.4))
	add_child(title)

	var subtitle := _make_label("COMBAT PROTOTYPE 0.1", Vector2(28, 48), Vector2(280, 22), 12, MUTED)
	add_child(subtitle)

	stage_label = _make_label("", Vector2(360, 19), Vector2(560, 42), 15, INK)
	stage_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	add_child(stage_label)

	var reset := _make_button("RESTART DEMO", Vector2(1098, 20), Vector2(150, 38), Color("7d8da1"))
	reset.pressed.connect(_restart_demo)
	add_child(reset)

	_build_player_panel()
	_build_enemy_panel()
	_build_log_panel()
	_build_skill_panel()

	end_turn_button = _make_button("END TURN   [SPACE]", Vector2(1038, 670), Vector2(210, 38), GOLD)
	end_turn_button.pressed.connect(_on_end_turn)
	add_child(end_turn_button)

	var footer := _make_label("Understanding creates options. Knowledge removes helplessness, not danger.", Vector2(28, 676), Vector2(820, 28), 14, Color("708197"))
	add_child(footer)

func _build_player_panel() -> void:
	var panel := _make_panel(Vector2(24, 82), Vector2(268, 352), PANEL)
	add_child(panel)
	panel.add_child(_make_label("WORDBEARER", Vector2(18, 14), Vector2(220, 25), 13, GOLD))

	hp_label = _make_label("", Vector2(18, 52), Vector2(232, 22), 16, INK)
	panel.add_child(hp_label)
	hp_bar = _make_progress(Vector2(18, 78), Vector2(232, 10), Color("d76565"))
	panel.add_child(hp_bar)

	armor_label = _make_label("", Vector2(18, 102), Vector2(232, 22), 15, INK)
	panel.add_child(armor_label)
	focus_label = _make_label("", Vector2(18, 132), Vector2(232, 30), 20, Color("77c9e3"))
	panel.add_child(focus_label)
	status_label = _make_label("", Vector2(18, 164), Vector2(232, 24), 13, MUTED)
	panel.add_child(status_label)

	var rule := HSeparator.new()
	rule.position = Vector2(18, 198)
	rule.size = Vector2(232, 2)
	panel.add_child(rule)
	panel.add_child(_make_label("CORRUPTION", Vector2(18, 211), Vector2(220, 20), 12, MUTED))

	var families := ["Decay", "Obscurity", "Inattention"]
	var colors := [Color("a98a5d"), Color("7e79bd"), Color("bd7087")]
	for index in range(families.size()):
		var family: String = families[index]
		var y := 240.0 + index * 34.0
		var label := _make_label("", Vector2(18, y), Vector2(150, 18), 12, INK)
		panel.add_child(label)
		corruption_labels[family] = label
		var bar := _make_progress(Vector2(142, y + 3), Vector2(108, 8), colors[index])
		panel.add_child(bar)
		corruption_bars[family] = bar

func _build_enemy_panel() -> void:
	var panel := _make_panel(Vector2(308, 82), Vector2(590, 352), PANEL_DARK)
	add_child(panel)

	enemy_name = _make_label("", Vector2(22, 16), Vector2(330, 32), 25, INK)
	panel.add_child(enemy_name)
	enemy_family = _make_label("", Vector2(365, 20), Vector2(202, 24), 12, GOLD)
	enemy_family.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	panel.add_child(enemy_family)
	enemy_subtitle = _make_label("", Vector2(22, 50), Vector2(545, 24), 13, MUTED)
	panel.add_child(enemy_subtitle)

	enemy_hp_label = _make_label("", Vector2(22, 84), Vector2(260, 20), 13, INK)
	panel.add_child(enemy_hp_label)
	enemy_hp_bar = _make_progress(Vector2(22, 108), Vector2(260, 10), Color("cb5f61"))
	panel.add_child(enemy_hp_bar)
	enemy_armor_label = _make_label("", Vector2(307, 84), Vector2(260, 20), 13, INK)
	panel.add_child(enemy_armor_label)
	enemy_armor_bar = _make_progress(Vector2(307, 108), Vector2(260, 10), Color("b88955"))
	panel.add_child(enemy_armor_bar)

	var intent_panel := _make_panel(Vector2(22, 138), Vector2(545, 143), Color("182536"), Color("35516d"))
	panel.add_child(intent_panel)
	intent_badge = _make_label("", Vector2(16, 13), Vector2(100, 23), 11, INK)
	intent_badge.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	intent_badge.add_theme_stylebox_override("normal", _style(Color("26384c"), Color.TRANSPARENT, 6, 5))
	intent_panel.add_child(intent_badge)
	intent_title = _make_label("", Vector2(16, 45), Vector2(510, 28), 20, INK)
	intent_panel.add_child(intent_title)
	intent_text = RichTextLabel.new()
	intent_text.position = Vector2(16, 77)
	intent_text.size = Vector2(510, 58)
	intent_text.bbcode_enabled = true
	intent_text.fit_content = false
	intent_text.scroll_active = false
	intent_text.add_theme_font_size_override("normal_font_size", 13)
	intent_text.add_theme_color_override("default_color", Color("b9c5d2"))
	intent_panel.add_child(intent_text)

	tutorial_label = _make_label("", Vector2(22, 296), Vector2(545, 39), 12, Color("a8b9c8"))
	tutorial_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	panel.add_child(tutorial_label)

func _build_log_panel() -> void:
	var panel := _make_panel(Vector2(914, 82), Vector2(342, 352), PANEL)
	add_child(panel)
	panel.add_child(_make_label("COMBAT TRACE", Vector2(18, 14), Vector2(300, 22), 13, GOLD))
	log_text = RichTextLabel.new()
	log_text.position = Vector2(18, 48)
	log_text.size = Vector2(306, 286)
	log_text.bbcode_enabled = true
	log_text.scroll_active = true
	log_text.scroll_following = true
	log_text.add_theme_font_size_override("normal_font_size", 12)
	log_text.add_theme_color_override("default_color", Color("aab7c5"))
	panel.add_child(log_text)

func _build_skill_panel() -> void:
	var panel := _make_panel(Vector2(24, 450), Vector2(1232, 204), Color("111b29"))
	add_child(panel)
	panel.add_child(_make_label("CORE WORD SKILLS", Vector2(16, 10), Vector2(220, 20), 12, MUTED))
	panel.add_child(_make_label("Fixed knowledge · no draw pile", Vector2(900, 10), Vector2(300, 20), 11, Color("64758a")))

	var order := CombatContent.skill_order()
	for index in range(order.size()):
		var skill_name: String = order[index]
		var data: Dictionary = CombatContent.SKILLS[skill_name]
		var text := "%d  %s\n%s" % [int(data["cost"]), skill_name, data["family"]]
		if skill_name == "DEFLECT":
			text = "1  DEFLECT\nREACTION ONLY"
		var button := _make_button(text, Vector2(16 + index * 200, 38), Vector2(184, 98), data["accent"])
		button.add_theme_font_size_override("font_size", 13)
		button.tooltip_text = "%s\n\n%s" % [data["sense"], data["effect"]]
		button.pressed.connect(_on_skill_pressed.bind(skill_name))
		button.mouse_entered.connect(_show_skill_detail.bind(skill_name))
		panel.add_child(button)
		skill_buttons[skill_name] = button

	detail_label = RichTextLabel.new()
	detail_label.position = Vector2(16, 145)
	detail_label.size = Vector2(1188, 42)
	detail_label.bbcode_enabled = true
	detail_label.scroll_active = false
	detail_label.add_theme_font_size_override("normal_font_size", 12)
	detail_label.add_theme_color_override("default_color", Color("9eacbc"))
	panel.add_child(detail_label)
	_show_skill_detail("OBSERVE")

func _refresh() -> void:
	if state.enemy.is_empty():
		return
	stage_label.text = _stage_text()
	hp_label.text = "HP   %d / %d" % [state.hp, CombatState.MAX_HP]
	hp_bar.max_value = CombatState.MAX_HP
	hp_bar.value = state.hp
	armor_label.text = "ARMOR   %d / %d" % [state.armor, CombatState.BASE_ARMOR]
	focus_label.text = "FOCUS   %d" % state.focus
	status_label.text = "STATUS   %s" % state.active_status_text()
	for family in corruption_labels:
		corruption_labels[family].text = "%s  %d" % [family.to_upper(), int(state.corruption[family])]
		corruption_bars[family].value = int(state.corruption[family])

	enemy_name.text = str(state.enemy["name"])
	enemy_subtitle.text = str(state.enemy["subtitle"])
	enemy_family.text = " + ".join(state.enemy["families"])
	enemy_hp_label.text = "HP   %d / %d" % [int(state.enemy["hp"]), int(state.enemy["max_hp"])]
	enemy_hp_bar.max_value = int(state.enemy["max_hp"])
	enemy_hp_bar.value = int(state.enemy["hp"])
	enemy_armor_label.text = "STRUCTURE   %d / %d" % [int(state.enemy["armor"]), int(state.enemy["max_armor"])]
	enemy_armor_bar.max_value = int(state.enemy["max_armor"])
	enemy_armor_bar.value = int(state.enemy["armor"])
	intent_badge.text = state.clarity_name()
	intent_badge.add_theme_color_override("font_color", _clarity_color(state.intent_clarity))
	intent_title.text = state.intent_title()
	intent_text.text = state.intent_description()
	tutorial_label.text = "TACTICAL NOTE · %s" % state.enemy["tutorial"]
	log_text.text = "\n\n".join(state.log_lines)
	log_text.scroll_to_line(maxi(0, state.log_lines.size() - 1))

	var modal_open := is_instance_valid(modal)
	for skill_name in skill_buttons:
		var button: Button = skill_buttons[skill_name]
		button.disabled = modal_open or not state.can_use(skill_name)
	end_turn_button.disabled = modal_open

func _stage_text() -> String:
	var parts: Array[String] = []
	for index in range(CombatContent.BATTLES.size()):
		var marker := "●" if index == state.battle_index else "○"
		parts.append("%s %d" % [marker, index + 1])
	return "     ".join(parts) + "     ·     TURN %d" % state.turn

func _show_skill_detail(skill_name: String) -> void:
	var data: Dictionary = CombatContent.SKILLS[skill_name]
	detail_label.text = "[color=#d8b96c]%s[/color]  ·  %s\n%s" % [skill_name, data["sense"], data["effect"]]

func _on_skill_pressed(skill_name: String) -> void:
	if skill_name == "RESTORE":
		_show_restore_choice()
	else:
		state.use_skill(skill_name)

func _on_end_turn() -> void:
	state.end_player_turn()

func _show_restore_choice() -> void:
	_show_modal("RESTORE", "Return one part of the Wordbearer to an earlier, better condition.", [
		{"text": "RESTORE 8 HP", "callback": func(): state.use_skill("RESTORE", "hp")},
		{"text": "RESTORE 4 ARMOR", "callback": func(): state.use_skill("RESTORE", "armor")},
		{"text": "CANCEL", "callback": func(): pass},
	])

func _show_reaction(action: Dictionary, cost: int) -> void:
	_show_modal(
		"REACTION WINDOW",
		"%s is moving toward you. Spend %d reserved Focus to change its direction?" % [action["word"], cost],
		[
			{"text": "DEFLECT  ·  %d FOCUS" % cost, "callback": func(): state.resolve_enemy_action(true)},
			{"text": "TAKE THE HIT", "callback": func(): state.resolve_enemy_action(false)},
		]
	)

func _on_battle_finished(victory: bool) -> void:
	if victory:
		if state.battle_index < CombatContent.BATTLES.size() - 1:
			_show_modal(
				"PATTERN UNDERSTOOD",
				"%s is defeated. The next encounter will pressure a different kind of understanding." % state.enemy["name"],
				[{"text": "CONTINUE TO ENCOUNTER %d" % [state.battle_index + 2], "callback": _continue_run}]
			)
		else:
			_show_run_summary()
	else:
		_show_modal(
			"CONNECTION BROKEN",
			"The encounter remains dangerous, but its pattern is no longer completely unknown.",
			[{"text": "RETRY ENCOUNTER", "callback": _retry_battle}, {"text": "RESTART DEMO", "callback": _restart_demo}]
		)

func _show_run_summary() -> void:
	var summary := "The Combat Prototype loop is complete.\n\nOBSERVE used: %d\nFocus reserved: %d\nDEFLECT reactions: %d\nBIND windows: %d\nSTABILIZE uses: %d\nThreats countered: %d" % [
		state.metrics["observe_uses"], state.metrics["focus_reserved"], state.metrics["deflect_uses"],
		state.metrics["bind_uses"], state.metrics["stabilize_uses"], state.metrics["intents_countered"]
	]
	_show_modal("UNDERSTANDING CREATED OPTIONS", summary, [{"text": "PLAY AGAIN", "callback": _restart_demo}])

func _continue_run() -> void:
	state.start_battle(state.battle_index + 1)

func _retry_battle() -> void:
	state.start_battle(state.battle_index)

func _restart_demo() -> void:
	_clear_modal()
	state.metrics = {"observe_uses": 0, "bind_uses": 0, "stabilize_uses": 0, "deflect_uses": 0, "focus_reserved": 0, "intents_countered": 0}
	state.exposure.clear()
	state.start_battle(0)

func _show_modal(title_text: String, body_text: String, actions: Array) -> void:
	_clear_modal()
	modal = Control.new()
	modal.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	modal.z_index = 100
	add_child(modal)
	var shade := ColorRect.new()
	shade.color = Color(0.015, 0.025, 0.04, 0.84)
	shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	shade.mouse_filter = Control.MOUSE_FILTER_STOP
	modal.add_child(shade)
	var panel_height := 250.0 + maxf(0, actions.size() - 2) * 48.0
	var card := _make_panel(Vector2(390, 215 - (panel_height - 250) * 0.5), Vector2(500, panel_height), Color("162333"), Color("49647e"))
	modal.add_child(card)
	var title := _make_label(title_text, Vector2(28, 24), Vector2(444, 36), 22, GOLD)
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	card.add_child(title)
	var body := _make_label(body_text, Vector2(32, 72), Vector2(436, 82), 14, Color("c1ccd7"))
	body.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	body.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	card.add_child(body)
	for index in range(actions.size()):
		var action: Dictionary = actions[index]
		var button := _make_button(str(action["text"]), Vector2(85, 166 + index * 48), Vector2(330, 38), GOLD if index == 0 else Color("74869a"))
		var callback: Callable = action["callback"]
		button.pressed.connect(func():
			_clear_modal()
			callback.call()
		)
		card.add_child(button)
	_refresh()

func _clear_modal() -> void:
	if is_instance_valid(modal):
		modal.queue_free()
	modal = null

func _unhandled_key_input(event: InputEvent) -> void:
	if not event.pressed or event.echo or is_instance_valid(modal):
		return
	if event.keycode == KEY_SPACE:
		_on_end_turn()
		get_viewport().set_input_as_handled()
		return
	var index := -1
	if event.keycode >= KEY_1 and event.keycode <= KEY_6:
		index = event.keycode - KEY_1
	if index >= 0:
		_on_skill_pressed(CombatContent.skill_order()[index])
		get_viewport().set_input_as_handled()

func _clarity_color(level: int) -> Color:
	return [Color("db7b72"), Color("e2b968"), Color("6fd1ad")][level]

func _make_panel(pos: Vector2, panel_size: Vector2, color: Color, border: Color = BORDER) -> Panel:
	var panel := Panel.new()
	panel.position = pos
	panel.size = panel_size
	panel.add_theme_stylebox_override("panel", _style(color, border, 10, 0, 1))
	return panel

func _make_label(text_value: String, pos: Vector2, label_size: Vector2, font_size: int, color: Color) -> Label:
	var label := Label.new()
	label.text = text_value
	label.position = pos
	label.size = label_size
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	return label

func _make_button(text_value: String, pos: Vector2, button_size: Vector2, accent: Color) -> Button:
	var button := Button.new()
	button.text = text_value
	button.position = pos
	button.size = button_size
	button.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	button.add_theme_color_override("font_color", INK)
	button.add_theme_color_override("font_hover_color", Color.WHITE)
	button.add_theme_color_override("font_disabled_color", Color("596677"))
	button.add_theme_stylebox_override("normal", _style(Color("182638"), accent.darkened(0.38), 7, 7, 1))
	button.add_theme_stylebox_override("hover", _style(Color("223449"), accent, 7, 7, 2))
	button.add_theme_stylebox_override("pressed", _style(Color("0f1824"), accent.lightened(0.15), 7, 7, 2))
	button.add_theme_stylebox_override("disabled", _style(Color("111a27"), Color("263444"), 7, 7, 1))
	return button

func _make_progress(pos: Vector2, bar_size: Vector2, color: Color) -> ProgressBar:
	var bar := ProgressBar.new()
	bar.position = pos
	bar.size = bar_size
	bar.min_value = 0
	bar.max_value = 100
	bar.show_percentage = false
	bar.add_theme_stylebox_override("background", _style(Color("0b111b"), Color.TRANSPARENT, 4))
	bar.add_theme_stylebox_override("fill", _style(color, Color.TRANSPARENT, 4))
	return bar

func _style(color: Color, border: Color, radius: int, margin: int = 0, width: int = 0) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = color
	style.border_color = border
	style.set_border_width_all(width)
	style.corner_radius_top_left = radius
	style.corner_radius_top_right = radius
	style.corner_radius_bottom_left = radius
	style.corner_radius_bottom_right = radius
	style.content_margin_left = margin
	style.content_margin_right = margin
	style.content_margin_top = margin
	style.content_margin_bottom = margin
	return style
