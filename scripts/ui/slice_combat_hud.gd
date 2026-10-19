extends CanvasLayer

signal action_requested(uid: int, restore_target: String)
signal retain_requested(uid: int)
signal mulligan_confirmed(ids: Array[int])
signal end_turn_requested
signal reaction_answered(deflect: bool)
signal overlay_changed(open: bool)
signal restart_requested
signal force_drop_changed(value: bool)
@export var hud_theme: Theme

var ui_root: Control
var survival: Label
var place_label: Label
var prompt: Label
var toast: Label
var combat_panel: PanelContainer
var combat_info: Label
var statuses_label: Label
var intent_label: Label
var cards: HBoxContainer
var detail: Label
var end_button: Button
var confirm_button: Button
var reaction_box: HBoxContainer
var reaction_label: Label
var deflect_button: Button
var overlay: Control
var combat: CombatState
var run: RunState
var selected_mulligan: Array[int] = []
var active := false
var overlay_open := false
var toast_lifetime := 0.0

func _ready() -> void:
	ui_root = Control.new()
	ui_root.name = "UI"
	if hud_theme != null: ui_root.theme = hud_theme
	ui_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ui_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(ui_root)
	var top := VBoxContainer.new()
	top.position = Vector2(24, 16)
	top.size = Vector2(1160, 100)
	top.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ui_root.add_child(top)
	place_label = label("ENGLISH GAME 0.9 · BROKEN GRAVEYARD · MILESTONE 01", 20)
	top.add_child(place_label)
	survival = label("", 16)
	top.add_child(survival)
	top.add_child(label("WASD / ARROWS move · E interact · L Lexicon · TAB Run Bag · F2 QA", 14))
	prompt = label("", 20)
	prompt.name = "InteractionPrompt"
	prompt.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	ui_root.add_child(prompt)
	prompt.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	prompt.offset_top = -94
	prompt.offset_bottom = -58
	toast = label("", 16)
	toast.name = "RewardToast"
	toast.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	ui_root.add_child(toast)
	toast.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	toast.offset_top = 118
	toast.offset_bottom = 174
	combat_panel = PanelContainer.new()
	combat_panel.name = "CombatPanel"
	ui_root.add_child(combat_panel)
	combat_panel.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	combat_panel.offset_left = 16
	combat_panel.offset_right = -16
	combat_panel.offset_top = -368
	combat_panel.offset_bottom = -16
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.045, 0.075, 0.09, 0.96)
	for edge in [SIDE_LEFT, SIDE_RIGHT, SIDE_TOP, SIDE_BOTTOM]: style.set_content_margin(edge, 12)
	if hud_theme == null: combat_panel.add_theme_stylebox_override("panel", style)
	var box := VBoxContainer.new()
	combat_panel.add_child(box)
	combat_info = label("", 15)
	combat_info.name = "CombatInfo"
	box.add_child(combat_info)
	var statuses_scroll := ScrollContainer.new()
	statuses_scroll.custom_minimum_size.y = 30
	statuses_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	statuses_label = label("", 13)
	statuses_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	statuses_scroll.add_child(statuses_label)
	box.add_child(statuses_scroll)
	intent_label = label("", 14)
	intent_label.name = "Intent"
	intent_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var intent_scroll := ScrollContainer.new()
	intent_scroll.name = "IntentScroll"
	intent_scroll.custom_minimum_size.y = 58
	intent_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	intent_scroll.add_child(intent_label)
	box.add_child(intent_scroll)
	cards = HBoxContainer.new()
	cards.name = "WordActions"
	box.add_child(cards)
	detail = label("Hover a Word Action for details. Click RETAIN to reserve that instance.", 13)
	detail.name = "ActionDetails"
	box.add_child(detail)
	reaction_box = HBoxContainer.new()
	reaction_label = label("", 14)
	reaction_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	reaction_box.add_child(reaction_label)
	deflect_button = button("DEFLECT", func(): reaction_answered.emit(true))
	reaction_box.add_child(deflect_button)
	reaction_box.add_child(button("TAKE THE HIT", func(): reaction_answered.emit(false)))
	box.add_child(reaction_box)
	var controls := HBoxContainer.new()
	confirm_button = button("CONFIRM OPENING HAND", func(): mulligan_confirmed.emit(selected_mulligan.duplicate()))
	controls.add_child(confirm_button)
	end_button = button("END TURN [SPACE]", func(): end_turn_requested.emit())
	controls.add_child(end_button)
	controls.add_child(button("LEXICON [L]", func(): show_lexicon()))
	controls.add_child(button("RUN BAG [TAB]", func(): show_bag()))
	box.add_child(controls)
	combat_panel.hide()
	reaction_box.hide()

func label(value: String, font_size: int = 14) -> Label:
	var result := Label.new()
	result.text = value
	result.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	result.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	result.add_theme_font_size_override("font_size", font_size)
	if hud_theme == null: result.add_theme_color_override("font_color", Color("e2e7dd"))
	return result

func button(value: String, callback: Callable) -> Button:
	var result := Button.new()
	result.text = value
	result.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	result.custom_minimum_size.y = 32
	result.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	result.pressed.connect(callback)
	return result

func bind(state: RunState, model: CombatState) -> void:
	run = state
	combat = model
	model.changed.connect(refresh)
	model.reaction_requested.connect(show_reaction)

func set_combat_active(value: bool) -> void:
	active = value
	combat_panel.visible = value
	prompt.visible = not value
	refresh()

func refresh() -> void:
	if run == null: return
	survival.text = "HP %d/50 · ARMOR %d/12 · ECHO %d" % [combat.hp if active else run.hp, combat.armor if active else run.armor, run.echo]
	if combat == null or combat.enemy.is_empty(): return
	combat_info.text = "FOCUS %d · %s · HP %d/%d · %s" % [combat.focus, combat.enemy.name, combat.enemy.hp, combat.enemy.max_hp, "BONE REMAINS %d/%d · REASSEMBLE in %d completed rounds" % [combat.remains_hp, combat.remains_integrity, combat.reassembly_countdown] if combat.bone_remains else "STRUCTURE %d/%d · ARMOR %d" % [combat.enemy.structure, combat.enemy.max_structure, combat.enemy.armor]]
	statuses_label.text = combat.active_status_text()
	intent_label.text = "%s · %s" % [combat.clarity_name(), combat.intent_description()]
	for child in cards.get_children():
		cards.remove_child(child)
		child.queue_free()
	for card in combat.deck.hand:
		var column := VBoxContainer.new()
		column.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		cards.add_child(column)
		var uid := int(card.instance_id)
		var reason := combat.disabled_reason(str(card.name), uid)
		var use_button := button("%s · %d FOCUS\n%s" % [card.name, combat.card_cost(card), "REPLACE" if combat.deck.mulligan_pending and uid in selected_mulligan else ("CLICK TO REPLACE (MAX 2)" if combat.deck.mulligan_pending else reason)], func(): _press_card(uid))
		use_button.name = "Sigil_%d" % uid
		use_button.custom_minimum_size.y = 56
		use_button.disabled = overlay_open or (not reason.is_empty() and not combat.deck.mulligan_pending)
		use_button.mouse_entered.connect(func(): show_card_detail(card))
		column.add_child(use_button)
		var retain := button("RETAINED" if uid in combat.deck.retained_cards else "RETAIN", func(): retain_requested.emit(uid))
		retain.name = "Retain_%d" % uid
		retain.disabled = overlay_open or not combat.retain_disabled_reason(card).is_empty()
		column.add_child(retain)
	confirm_button.visible = combat.deck.mulligan_pending
	confirm_button.disabled = overlay_open
	end_button.disabled = overlay_open or combat.finished or combat.turn_ending or combat.deck.mulligan_pending
	if not combat.turn_ending: reaction_box.hide()

func _press_card(uid: int) -> void:
	if combat.deck.mulligan_pending:
		if uid in selected_mulligan: selected_mulligan.erase(uid)
		elif selected_mulligan.size() < 2: selected_mulligan.append(uid)
		refresh()
		return
	for card in combat.deck.hand:
		if int(card.instance_id) != uid: continue
		if card.name == "RESTORE":
			show_overlay("RESTORE", "Choose one repair direction.", [{"text": "RESTORE HP", "callback": func(): close_overlay(); action_requested.emit(uid, "hp")}, {"text": "RESTORE ARMOR", "callback": func(): close_overlay(); action_requested.emit(uid, "armor")}])
		else: action_requested.emit(uid, "")
		return

func show_card_detail(card: Dictionary) -> void:
	if combat.bone_remains:
		var amounts := {"SHATTER": "Integrity -8", "STRIKE": "Integrity -3", "BIND": "Countdown +1, once per Remains phase"}
		detail.text = "%s · %s" % [card.name, amounts.get(card.name, card.base_effect)]
	else: detail.text = "%s · %s" % [card.name, card.base_effect]

func show_reaction(action: Dictionary, cost: int) -> void:
	reaction_label.text = "%s approaches. Use DEFLECT?" % action.word
	if combat.inattention_tier < 4: reaction_label.text += "  %d physical damage." % int(action.get("damage", 0))
	deflect_button.text = "DEFLECT · %d FOCUS" % cost
	deflect_button.disabled = not combat.can_react()
	reaction_box.show()

func announce(value: String) -> void:
	toast.text = value
	toast_lifetime = 3.0
	refresh()

func _process(delta: float) -> void:
	if toast_lifetime > 0:
		toast_lifetime -= delta
		if toast_lifetime <= 0: toast.text = ""

func show_lexicon() -> void:
	if overlay_open or run == null: return
	var lines: Array[String] = []
	for word in run.target_knowledge.values():
		if word.current_state == "UNKNOWN": continue
		var line := "%s · %s" % [word.lemma, word.current_state]
		# Permission-safe: unknown meanings, enemy codex and pending answers are not revealed.
		if word.is_recognized(): line += "\n" + word.known_meaning
		lines.append(line)
	show_overlay("LEXICON", "\n\n".join(lines) if not lines.is_empty() else "No words encountered yet.", [])

func show_bag() -> void:
	if overlay_open or run == null: return
	var lines: Array[String] = ["Echo: %d" % run.echo]
	for id in run.world_inventory: lines.append("%s × %d" % [str(id).replace("relic.", "").replace("_", " ").capitalize(), run.world_inventory[id]])
	if run.world_inventory.is_empty(): lines.append("No special loot picked up yet.")
	lines.append("Weathered Chisel's combat effect is not specified in this milestone.")
	show_overlay("RUN BAG", "\n".join(lines), [])

func show_overlay(title_text: String, body_text: String, actions: Array) -> void:
	if is_instance_valid(overlay): overlay.queue_free()
	overlay_open = true
	overlay_changed.emit(true)
	overlay = Control.new()
	overlay.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	ui_root.add_child(overlay)
	var shade := ColorRect.new()
	shade.color = Color(0.02, 0.04, 0.04, 0.92)
	shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	overlay.add_child(shade)
	var card := preload("res://scripts/ui/adaptive_modal.gd").new()
	overlay.add_child(card)
	var title := label(title_text, 22)
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	var body := label(body_text, 15)
	body.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	var buttons: Array[Button] = []
	for action in actions: buttons.append(button(str(action.text), action.callback))
	buttons.append(button("CLOSE", close_overlay))
	card.configure(title, body, buttons)
	card.fit_to_area(get_viewport().get_visible_rect().size)
	refresh()

func close_overlay() -> void:
	if is_instance_valid(overlay): overlay.queue_free()
	overlay = null
	overlay_open = false
	overlay_changed.emit(false)
	refresh()
