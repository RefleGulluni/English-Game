extends Control

const INK := Color("e8edf2")
const MUTED := Color("8997a8")
const GOLD := Color("d7b86c")
const BG := Color("0d1522")
const PANEL := Color("141f2e")
const PANEL_DARK := Color("101925")
const BORDER := Color("2a3b50")

var state := CombatState.new()
var run_manager := RunManager.new()
var pending_combat_result: Dictionary = {}
var modal: Control
var knowledge_notice: Label
var lexicon_open := false

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
var knowledge_indicator: Label
var tutorial_label: RichTextLabel
var log_text: RichTextLabel
var detail_label: RichTextLabel
var end_turn_button: Button
var skill_buttons: Dictionary = {}
var hand_row: HBoxContainer
var pile_label: Label
var mulligan_selection: Array[int] = []
var toxic_training_in_combat := false

func _ready() -> void:
	set_process_unhandled_key_input(true)
	_build_interface()
	state.changed.connect(_refresh)
	state.reaction_requested.connect(_show_reaction)
	state.battle_finished.connect(_on_battle_finished)
	state.inattention_tier_changed.connect(_pulse_status)
	state.combo_discovered.connect(_on_combo_discovered)
	run_manager.start_run()
	run_manager.state.knowledge.changed.connect(_on_knowledge_changed)
	run_manager.state.toxic_knowledge.changed.connect(_on_knowledge_changed)
	_show_run_entry()

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

	var subtitle := _make_label("MINI RUN PROTOTYPE 0.6", Vector2(28, 48), Vector2(280, 22), 12, MUTED)
	add_child(subtitle)

	stage_label = _make_label("", Vector2(360, 19), Vector2(560, 42), 15, INK)
	stage_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	add_child(stage_label)

	var reset := _make_button("RESTART RUN", Vector2(1098, 20), Vector2(150, 38), Color("7d8da1"))
	reset.pressed.connect(_restart_run)
	add_child(reset)

	_build_player_panel()
	_build_enemy_panel()
	_build_log_panel()
	_build_skill_panel()

	end_turn_button = _make_button("END TURN   [SPACE]", Vector2(1038, 670), Vector2(210, 38), GOLD)
	end_turn_button.pressed.connect(_on_end_turn)
	add_child(end_turn_button)

	knowledge_notice = _make_label("Knowledge = Tactical Advantage", Vector2(28, 676), Vector2(780, 28), 14, Color("708197"))
	add_child(knowledge_notice)
	var lexicon_button := _make_button("LEXICON", Vector2(824, 670), Vector2(200, 38), GOLD)
	lexicon_button.name = "LexiconButton"
	lexicon_button.z_index = 101
	lexicon_button.pressed.connect(_show_lexicon)
	add_child(lexicon_button)

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
	panel.add_child(_make_label("STATUS", Vector2(18, 164), Vector2(232, 18), 11, MUTED))
	var status_scroll := ScrollContainer.new()
	status_scroll.position = Vector2(18, 184)
	status_scroll.size = Vector2(232, 70)
	status_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	panel.add_child(status_scroll)
	status_label = _make_label("", Vector2.ZERO, Vector2.ZERO, 11, MUTED)
	status_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	status_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	status_scroll.add_child(status_label)

	var rule := HSeparator.new()
	rule.position = Vector2(18, 258)
	rule.size = Vector2(232, 2)
	panel.add_child(rule)
	panel.add_child(_make_label("CORRUPTION", Vector2(18, 270), Vector2(220, 20), 12, MUTED))

	var families := ["Decay", "Obscurity", "Inattention"]
	var colors := [Color("a98a5d"), Color("7e79bd"), Color("bd7087")]
	for index in range(families.size()):
		var family: String = families[index]
		var y := 294.0 + index * 17.0
		var label := _make_label("", Vector2(18, y), Vector2(150, 18), 12, INK)
		panel.add_child(label)
		corruption_labels[family] = label
		var bar := _make_progress(Vector2(142, y + 3), Vector2(108, 8), colors[index])
		# Keep the visible bar 8px tall despite the engine's theme minimum height.
		bar.size = Vector2(108, 32)
		bar.scale.y = 0.25
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
	knowledge_indicator = _make_label("", Vector2(132, 16), Vector2(390, 23), 11, GOLD)
	intent_panel.add_child(knowledge_indicator)
	intent_title = _make_label("", Vector2(16, 45), Vector2(510, 28), 20, INK)
	intent_title.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	intent_title.add_theme_font_size_override("font_size", 14)
	intent_panel.add_child(intent_title)
	intent_text = RichTextLabel.new()
	intent_text.position = Vector2(16, 77)
	intent_text.size = Vector2(510, 58)
	intent_text.bbcode_enabled = true
	intent_text.fit_content = false
	intent_text.scroll_active = true
	intent_text.add_theme_font_size_override("normal_font_size", 13)
	intent_text.add_theme_color_override("default_color", Color("b9c5d2"))
	intent_panel.add_child(intent_text)

	tutorial_label = RichTextLabel.new()
	tutorial_label.position = Vector2(22, 290)
	tutorial_label.size = Vector2(545, 52)
	tutorial_label.scroll_active = true
	tutorial_label.add_theme_font_size_override("normal_font_size", 10)
	tutorial_label.add_theme_color_override("default_color", Color("a8b9c8"))
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
	panel.add_child(_make_label("SEMANTIC HAND", Vector2(16, 10), Vector2(220, 20), 12, MUTED))
	pile_label = _make_label("", Vector2(350, 10), Vector2(850, 20), 11, MUTED)
	pile_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	panel.add_child(pile_label)
	var hand_scroll := ScrollContainer.new()
	hand_scroll.position = Vector2(16, 36)
	hand_scroll.size = Vector2(1200, 112)
	hand_scroll.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	panel.add_child(hand_scroll)
	hand_row = HBoxContainer.new()
	hand_row.add_theme_constant_override("separation", 10)
	hand_scroll.add_child(hand_row)

	detail_label = RichTextLabel.new()
	detail_label.position = Vector2(16, 155)
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
	status_label.text = state.active_status_text()
	for family in corruption_labels:
		corruption_labels[family].text = "%s  %d" % [family.to_upper(), int(state.corruption[family])]
		corruption_bars[family].value = int(state.corruption[family])

	enemy_name.text = str(state.enemy["name"])
	enemy_subtitle.text = str(state.enemy["subtitle"])
	enemy_family.text = " + ".join(state.enemy["families"])
	enemy_hp_label.text = "HP   %d / %d" % [int(state.enemy["hp"]), int(state.enemy["max_hp"])]
	enemy_hp_bar.max_value = int(state.enemy["max_hp"])
	enemy_hp_bar.value = int(state.enemy["hp"])
	enemy_armor_label.text = ("STRUCTURE %d/%d" % [int(state.enemy["structure"]), int(state.enemy["max_structure"])] if bool(state.enemy["has_structure"]) else "STRUCTURE NONE") + " · ARMOR %d/%d" % [int(state.enemy["armor"]), int(state.enemy["max_armor"])]
	enemy_armor_label.add_theme_font_size_override("font_size", 11)
	# A zero-width range renders as full in Godot; no-Structure targets have no bar.
	enemy_armor_bar.visible = bool(state.enemy["has_structure"])
	enemy_armor_bar.max_value = maxi(1, int(state.enemy["max_structure"]))
	enemy_armor_bar.value = int(state.enemy["structure"])
	intent_badge.text = state.clarity_name()
	intent_badge.add_theme_color_override("font_color", _clarity_color(state.intent_clarity))
	intent_title.text = state.intent_title()
	intent_text.text = state.intent_description()
	var known_word = state.toxic_knowledge if state.intent.has("poison") else state.knowledge
	knowledge_indicator.text = "KNOWN WORD · %s · %s" % [known_word.lemma, known_word.current_state] if not state.knowledge_intent_hint().is_empty() else ""
	tutorial_label.text = state.trait_text()
	log_text.text = "\n\n".join(state.log_lines)
	log_text.scroll_to_line(maxi(0, state.log_lines.size() - 1))

	var modal_open := is_instance_valid(modal)
	_refresh_hand(modal_open)
	end_turn_button.disabled = modal_open or state.deck.mulligan_pending or state.turn_ending or state.pending_counter or state.finished

func _refresh_hand(modal_open: bool) -> void:
	for child in hand_row.get_children():
		hand_row.remove_child(child)
		child.queue_free()
	pile_label.text = "DRAW %d · DISCARD %d · EXHAUST %d · RETAIN %d/%d" % [state.deck.draw_pile.size(), state.deck.discard_pile.size(), state.deck.exhaust_pile.size(), state.deck.retained_cards.size(), state.retain_slots()]
	for index in range(state.deck.hand.size()):
		var card: Dictionary = state.deck.hand[index]
		var uid := int(card["instance_id"])
		var card_name := str(card["name"])
		var column := VBoxContainer.new()
		column.custom_minimum_size.x = 230
		hand_row.add_child(column)
		var text := "%d · %s · %d FOCUS\n%s" % [index + 1, card_name, state.card_cost(card), card["category"]]
		if card_name in ["ERODE", "TOXIC"] and state.word_for(card_name).current_state != "USABLE":
			text += "\nCONTEXT CARD · Study in Lexicon"
		else:
			var summaries := {
				"SHATTER": "BREAK · Structure -8 / low direct 3",
				"STRIKE": "KILL · Direct 8 / Structure -2",
				"TOXIC": "BYPASS · Poison HP -3 × 3 turns",
				"OBSERVE": "Intent clarity +1",
				"BIND": "Delay the current intent 1 turn",
				"DEFLECT": "Reaction · physical damage -75%",
				"STABILIZE": "Dominant Corruption -8",
				"RESTORE": "Choose +8 HP or +4 Armor",
				"ERODE": "Erosion 3 turns · Structure -2 / Armor -1",
			}
			text += "\n" + str(summaries.get(card_name, card["base_effect"]))
			if "EXHAUST" in card["time_properties"]:
				text += "\nECHO · EXHAUST" if bool(card.get("echo", false)) else "\nTEMPORARY · EXHAUST"
		var reason := "DIALOG OPEN" if modal_open else state.disabled_reason(card_name, uid)
		if not reason.is_empty():
			text += "\n" + reason
		var button := _make_button(text, Vector2.ZERO, Vector2.ZERO, CombatContent.SKILLS[card_name]["accent"])
		button.name = "Card%d" % uid
		button.custom_minimum_size = Vector2(230, 72)
		button.size_flags_vertical = Control.SIZE_EXPAND_FILL
		button.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		button.add_theme_font_size_override("font_size", 11)
		button.add_theme_color_override("font_disabled_color", Color("97a6b8"))
		button.tooltip_text = str(card["base_effect"]) + ("\n" + reason if not reason.is_empty() else "")
		button.disabled = not reason.is_empty()
		button.pressed.connect(_on_card_pressed.bind(uid))
		button.mouse_entered.connect(_show_skill_detail.bind(card_name))
		column.add_child(button)
		var retained := state.deck.retained_cards.has(uid)
		var retain_reason := "DIALOG OPEN" if modal_open else state.retain_disabled_reason(card)
		var retain := _make_button(retain_reason if not retain_reason.is_empty() else ("RETAIN ✓" if retained else "RETAIN"), Vector2.ZERO, Vector2.ZERO, GOLD if retained else MUTED)
		retain.custom_minimum_size.y = 24
		retain.add_theme_font_size_override("font_size", 9)
		retain.add_theme_color_override("font_disabled_color", Color("97a6b8"))
		retain.tooltip_text = retain_reason
		retain.disabled = not retain_reason.is_empty()
		retain.pressed.connect(func():
			state.deck.toggle_retain(uid, state.retain_slots())
			_refresh()
		)
		column.add_child(retain)

func _on_card_pressed(uid: int) -> void:
	for card in state.deck.hand:
		if int(card["instance_id"]) == uid:
			if not state.can_use(str(card["name"]), uid):
				return
			if str(card["name"]) == "RESTORE":
				_show_restore_choice(uid)
			else:
				state.use_card(uid)
			return

func _show_mulligan() -> void:
	var actions: Array = [{"text": "CONFIRM · REPLACE %d CARDS" % mulligan_selection.size(), "callback": _confirm_mulligan}]
	for card in state.deck.hand:
		var uid := int(card["instance_id"])
		actions.append({"text": "%s %s · %d FOCUS" % ["✓" if mulligan_selection.has(uid) else "□", card["name"], state.card_cost(card)], "callback": _toggle_mulligan.bind(uid)})
	_show_modal("OPENING HAND", "Replace up to two cards, once per combat.\nReturned cards are shuffled back after replacements are drawn.\nRetain keeps one card for the next turn without a Focus cost.\nThe same instance cannot be retained on consecutive turns.", actions)

func _toggle_mulligan(uid: int) -> void:
	if mulligan_selection.has(uid):
		mulligan_selection.erase(uid)
	elif mulligan_selection.size() < 2:
		mulligan_selection.append(uid)
	_show_mulligan()

func _confirm_mulligan() -> void:
	state.finish_mulligan(mulligan_selection)
	mulligan_selection.clear()
	_refresh()

func _on_combo_discovered() -> void:
	knowledge_notice.text = "COMBO DISCOVERED · %s · Recorded in Lexicon" % state.latest_combo.replace("_", " ").to_upper()
	# Defer until the card and any counter-Reaction have finished resolving.
	_show_combo_notice.call_deferred()

func _show_combo_notice() -> void:
	if not is_instance_valid(modal) and not state.finished and not state.pending_counter:
		var descriptions := {"fractured_erosion": "ERODE × SHATTER.\nErosion ticks become 3 Structure damage and last one additional turn.", "weakened_opening": "ERODE × STRIKE.\nThis STRIKE ignores up to 3 Armor without adding damage.", "venomous_strike": "TOXIC × STRIKE.\nNormal Strike also refreshes POISONED for 3 turns."}
		_show_modal("SEMANTIC RESONANCE DISCOVERED", str(descriptions.get(state.latest_combo, state.latest_combo)) + "\nRecorded in your Lexicon.", [{"text": "CONTINUE", "callback": _refresh}])

func _stage_text() -> String:
	return "FRACTURE · LAYER %d / 4     ·     %s     ·     TURN %d" % [
		mini(4, run_manager.state.current_layer + 1), str(state.enemy.get("name", "ENCOUNTER")), state.turn
	]

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

func _show_restore_choice(uid: int = -1) -> void:
	_show_modal("RESTORE", "Return one part of the Wordbearer to an earlier, better condition.", [
		{"text": "RESTORE 8 HP", "callback": func(): state.use_skill("RESTORE", "hp", uid)},
		{"text": "RESTORE 4 ARMOR", "callback": func(): state.use_skill("RESTORE", "armor", uid)},
		{"text": "CANCEL", "callback": _refresh},
	])

func _show_reaction(action: Dictionary, cost: int) -> void:
	var body := "%s is moving toward you.\nSpend %d reserved Focus to change its direction?" % [action["word"], cost]
	if state.battle_index == 2:
		if state.inattention_tier == 2:
			body = "%s incoming.\nUse DEFLECT?" % action["word"]
		elif state.inattention_tier == 3:
			body = "Reaction Available.\nDetails are obscured by Inattention."
		elif state.inattention_tier >= 4:
			body = "Reaction Available"
	_show_modal(
		"REACTION WINDOW",
		body,
		[
			{"text": "DEFLECT  ·  %d FOCUS" % cost, "callback": func(): state.resolve_enemy_action(true)},
			{"text": "TAKE THE HIT", "callback": func(): state.resolve_enemy_action(false)},
		]
	)

func _on_battle_finished(victory: bool) -> void:
	if victory:
		pending_combat_result = run_manager.complete_combat(state)
		_sync_state_from_run()
		if bool(pending_combat_result.get("final", false)):
			run_manager.complete_final()
			_show_run_summary()
		else:
			_show_breather()
	else:
		run_manager.fail_run(state)
		_sync_state_from_run()
		_show_run_summary()

func _show_run_summary() -> void:
	var run := run_manager.state
	var title := "RUN COMPLETE" if run.victory else "CONNECTION BROKEN"
	var outcome := "Extracted safely." if run.extracted else ("The deepest pattern was understood." if run.victory else "The Fracture claimed this attempt.")
	var summary := "%s\n\nEcho secured: %d\nNodes crossed: %d\nRelics: %s\n\nOBSERVE %d · DEFLECT %d · BIND %d · STABILIZE %d" % [
		outcome, run.echo, run.current_layer, _relic_names(),
		state.metrics["observe_uses"], state.metrics["deflect_uses"], state.metrics["bind_uses"], state.metrics["stabilize_uses"]
	]
	_show_modal(title, summary, [{"text": "BEGIN ANOTHER RUN", "callback": _restart_run}])

func _restart_run() -> void:
	_clear_modal()
	knowledge_notice.text = "Knowledge = Tactical Advantage"
	state.metrics = {"observe_uses": 0, "bind_uses": 0, "stabilize_uses": 0, "deflect_uses": 0, "focus_reserved": 0, "intents_countered": 0}
	state.exposure.clear()
	run_manager.run_index += 1
	run_manager.start_run()
	pending_combat_result.clear()
	_show_run_entry()

func _show_run_entry() -> void:
	_show_modal(
		"FRACTURE ENTRY",
		"A short route opens through unstable language. HP and Corruption will persist until you extract or the connection breaks.",
		[{"text": "ENTER THE FRACTURE", "callback": _show_inscription}]
	)

func _on_knowledge_changed(message: String) -> void:
	knowledge_notice.text = message
	state._add_log(message)
	if not state.enemy.is_empty():
		_refresh()
	if message.begins_with("TOXIC") and run_manager.state.toxic_knowledge.current_state == "UNDERSTOOD" and not run_manager.state.toxic_knowledge.transfer_offered:
		_offer_toxic_training.call_deferred()

func _offer_toxic_training() -> void:
	if not is_instance_valid(modal) and not state.finished and state.battle_index == 4:
		_show_toxic_transfer()

func _show_inscription() -> void:
	var word := run_manager.state.knowledge
	word.encounter()
	_show_modal("ERODED INSCRIPTION", "The inscription has been eroded by years of rain.\n\nThe stone is worn smooth. Only fragments of the old letters remain.", [
		{"text": "INFER FROM CONTEXT", "callback": _show_recognition_question},
		{"text": "EXAMINE", "callback": _examine_inscription},
		{"text": "IGNORE", "callback": _finish_inscription},
	])

func _examine_inscription() -> void:
	_show_modal("EXAMINE THE INSCRIPTION", "Rain has passed over this stone for many years.\nIts edges and letters have slowly worn away.", [
		{"text": "INFER FROM CONTEXT", "callback": _show_recognition_question},
		{"text": "CONTINUE WITHOUT GUESSING", "callback": _finish_inscription},
	])

func _show_recognition_question() -> void:
	_show_modal("ERODE · INFER FROM CONTEXT", "The inscription has been eroded by years of rain.\n\nWhat does eroded mean here?", [
		{"text": "gradually wear away", "callback": _answer_recognition.bind("wear")},
		{"text": "suddenly explode", "callback": _answer_recognition.bind("explode")},
		{"text": "tightly connect", "callback": _answer_recognition.bind("connect")},
	])

func _answer_recognition(answer: String) -> void:
	var correct := answer == "wear"
	if correct:
		run_manager.state.knowledge.recognize("inscription")
	_show_modal("ERODE · RECOGNIZED" if correct else "ERODE · KEEP EXPLORING", "Recognition Evidence +1.\nThe stone has gradually worn away.\nLook for ERODE when you meet ROOT HUSK." if correct else "That meaning does not match the slow wear on the stone.\nNo resources are lost. You may find more evidence in combat.", [
		{"text": "CONTINUE", "callback": _finish_inscription},
	])

func _finish_inscription() -> void:
	run_manager.state.knowledge.inscription_completed = true
	if not run_manager.state.toxic_knowledge.inscription_completed:
		_show_toxic_exposure()
	else:
		_show_map()

func _show_toxic_exposure() -> void:
	run_manager.state.toxic_knowledge.encounter()
	_show_modal("TOXIC · FIRST EXPOSURE", "A cracked vial carries a warning: TOXIC.\nA drop touches a leaf, which slowly sickens.\nWhat does toxic mean in this context?", [
		{"text": "harmful or poisonous", "callback": _answer_toxic_recognition.bind("harmful")},
		{"text": "protective and healing", "callback": _answer_toxic_recognition.bind("healing")},
		{"text": "tightly tied together", "callback": _answer_toxic_recognition.bind("tied")},
		{"text": "LEAVE AND KEEP EXPLORING", "callback": _finish_toxic_exposure},
	])

func _answer_toxic_recognition(answer: String) -> void:
	var correct := answer == "harmful"
	if correct:
		run_manager.state.toxic_knowledge.recognize("cracked_vial")
	_show_modal("TOXIC · RECOGNIZED" if correct else "TOXIC · KEEP EXPLORING", "Recognition Evidence +1.\nThe substance is harmful or poisonous.\nThe Iron Shell test branch contains a real TOXIC consequence to observe." if correct else "That meaning does not explain the sick leaf.\nNo resources are lost.", [
		{"text": "CONTINUE" if correct else "TRY AGAIN", "callback": _finish_toxic_exposure if correct else _show_toxic_exposure},
		{"text": "LEAVE", "callback": _finish_toxic_exposure},
	])

func _finish_toxic_exposure() -> void:
	run_manager.state.toxic_knowledge.inscription_completed = true
	_show_map()

func _show_toxic_transfer() -> void:
	toxic_training_in_combat = state.battle_index == 4 and not state.finished and not "iron_shell" in run_manager.state.completed_detours
	run_manager.state.toxic_knowledge.transfer_offered = true
	_show_modal("TOXIC · A NEW CONTEXT", "The contaminated water is toxic to fish.\nWhat does toxic describe here?", [
		{"text": "It is harmful or poisonous to the fish.", "callback": _answer_toxic_transfer.bind("harmful")},
		{"text": "It makes the fish stronger.", "callback": _answer_toxic_transfer.bind("stronger")},
		{"text": "SKIP AND CONTINUE", "callback": _resume_toxic_training},
	])

func _answer_toxic_transfer(answer: String) -> void:
	var correct := answer == "harmful"
	run_manager.state.toxic_knowledge.record_transfer(correct)
	if correct:
		_show_toxic_production()
	else:
		_show_modal("TOXIC · KEEP EXPLORING", "The water causes harm rather than strengthening the fish.\nYour evidence is preserved.", [{"text": "TRY AGAIN", "callback": _show_toxic_transfer}, {"text": "CONTINUE", "callback": _resume_toxic_training}])

func _show_toxic_production() -> void:
	_show_modal("TOXIC · USE THE WORD", "The fumes are _____ and can poison living things.", [
		{"text": "toxic", "callback": _answer_toxic_production.bind("toxic")},
		{"text": "stable", "callback": _answer_toxic_production.bind("stable")},
		{"text": "restored", "callback": _answer_toxic_production.bind("restored")},
		{"text": "SKIP AND CONTINUE", "callback": _resume_toxic_training},
	])

func _answer_toxic_production(answer: String) -> void:
	var correct := answer == "toxic"
	run_manager.state.toxic_knowledge.record_production(correct)
	_show_modal("TOXIC · USABLE" if correct else "TOXIC · TRY AGAIN", "Production Evidence +1.\nTOXIC is now a usable Semantic Modifier.\nPOISONED bypasses Structure and Armor, but some enemies resist it." if correct else "Choose the word for something harmful or poisonous.", [{"text": "CONTINUE" if correct else "TRY AGAIN", "callback": _resume_toxic_training if correct else _show_toxic_production}])

func _resume_toxic_training() -> void:
	if toxic_training_in_combat:
		toxic_training_in_combat = false
		_refresh()
	else:
		_show_map()

func _show_semantic_anomaly() -> void:
	var word := run_manager.state.knowledge
	var body := "A phrase repeats in the Fracture.\nRain will _____ the stone over many winters.\nAgain: Rain will _____ the stone over many winters.\nWhich concept is disappearing from the phrase?"
	if word.is_recognized():
		body += "\nKnown concept: gradual weakening."
	if word.has_insight():
		body += "\nKnown mechanism: repeated exposure wears away material, rather than binding or restoring it."
	var actions: Array = [
		{"text": "ERODE", "callback": _resolve_anomaly.bind("erode")},
		{"text": "BIND", "callback": _resolve_anomaly.bind("bind")},
		{"text": "RESTORE", "callback": _resolve_anomaly.bind("restore")},
	]
	if word.current_state == "USABLE":
		actions.append({"text": "ANCHOR THE MISSING CONCEPT", "callback": _resolve_anomaly.bind("anchor")})
	actions.append({"text": "LEAVE SAFELY", "callback": _resolve_anomaly.bind("leave")})
	body += "\nCorrect meaning: a temporary card. Wrong meaning: Obscurity +8. Leave: no cost."
	_show_modal("REPEATING PHRASE ANOMALY", body, actions)

func _show_lexicon() -> void:
	if lexicon_open:
		return
	lexicon_open = true
	var previous := modal
	if is_instance_valid(previous):
		previous.hide()
	modal = null
	var word := run_manager.state.knowledge
	var body := "No words recorded yet.\nExplore the Fracture to discover a word." if word.current_state == "UNKNOWN" else word.entry_text()
	var toxic := run_manager.state.toxic_knowledge
	if toxic.current_state != "UNKNOWN":
		body += "\n\n" + toxic.entry_text()
	for monster in word.enemy_records:
		body += "\n\nCOMBAT CODEX · %s\n%s" % [monster, word.enemy_records[monster]]
	if not run_manager.state.relics.is_empty():
		body += "\n\nRELICS · " + _relic_names()
	_show_modal("LEXICON · WORDS & COMBAT CODEX", body, [
		{"text": "CLOSE LEXICON", "callback": _close_lexicon.bind(previous)},
	])

func _close_lexicon(previous: Control) -> void:
	lexicon_open = false
	if is_instance_valid(previous):
		modal = previous
		previous.show()
	_refresh()

func _show_transfer_context() -> void:
	run_manager.state.knowledge.transfer_offered = true
	_show_modal("ERODE · A NEW CONTEXT", "Water erodes the stone slowly.\n\nWhat is happening?", [
		{"text": "The stone is slowly being worn away.", "callback": _answer_transfer.bind("wear")},
		{"text": "The stone is suddenly exploding.", "callback": _answer_transfer.bind("explode")},
		{"text": "The stone is becoming stronger.", "callback": _answer_transfer.bind("stronger")},
		{"text": "SKIP AND CONTINUE", "callback": _show_map},
	])

func _answer_transfer(answer: String) -> void:
	var correct := answer == "wear"
	run_manager.state.knowledge.record_transfer(correct)
	if correct:
		_show_modal("ERODE · CONTEXT EVIDENCE", "Context Evidence gained.\nThe same gradual weakening appears in a new setting.\nERODE Insight predicts structural weakening in combat.", [
			{"text": "TRY USING THE WORD", "callback": _show_production_question},
			{"text": "CONTINUE TO MAP", "callback": _show_map},
		])
	else:
		_show_modal("ERODE · KEEP EXPLORING", "This sentence describes slow wear, not an explosion or strengthening.\nYour existing knowledge is preserved. No resources are lost.", [
			{"text": "TRY THE CONTEXT AGAIN", "callback": _show_transfer_context},
			{"text": "CONTINUE TO MAP", "callback": _show_map},
		])

func _show_production_question() -> void:
	_show_modal("ERODE · USE THE WORD", "The river slowly ______ the cliff.", [
		{"text": "erodes", "callback": _answer_production.bind("erodes")},
		{"text": "binds", "callback": _answer_production.bind("binds")},
		{"text": "restores", "callback": _answer_production.bind("restores")},
		{"text": "SKIP AND CONTINUE", "callback": _show_map},
	])

func _answer_production(answer: String) -> void:
	var correct := answer == "erodes"
	run_manager.state.knowledge.record_production(correct)
	_show_modal("ERODE · USABLE" if correct else "ERODE · TRY ANOTHER MEANING", "Production Evidence +1.\nThe river slowly erodes the cliff.\nERODE INSIGHT and the ERODE Semantic Modifier card are unlocked." if correct else "The river wears the cliff away gradually.\nYour existing evidence is preserved.", [
		{"text": "CONTINUE TO MAP" if correct else "TRY AGAIN", "callback": _show_map if correct else _show_production_question},
	])

func _show_map() -> void:
	var run := run_manager.state
	if run.toxic_knowledge.current_state == "UNDERSTOOD" and not run.toxic_knowledge.transfer_offered:
		_show_toxic_transfer()
		return
	if run.knowledge.root_combat_seen and run.current_layer >= 2 and not run.knowledge.transfer_offered:
		_show_transfer_context()
		return
	var lines: Array[String] = [run.condition_text(), "", "Choose the next path:"]
	if run.next_reward_multiplier > 1.0:
		lines.append("PRESS ON ACTIVE · Next Echo reward ×%.2f" % run.next_reward_multiplier)
	var actions: Array = []
	for node in run_manager.available_nodes():
		lines.append("%s · %s" % [node["title"], node["detail"]])
		var action_text := str(node["title"])
		var base_echo := int(node.get("echo", 0))
		if node.has("reward_multiplier"):
			base_echo = int(round(float(base_echo) * float(node["reward_multiplier"])))
		if base_echo > 0 and run.next_reward_multiplier > 1.0:
			action_text += " · %d → %d ECHO" % [base_echo, run.preview_echo(base_echo, true)]
		actions.append({"text": action_text, "callback": _select_node.bind(str(node["id"]))})
	_show_modal("FRACTURE MAP · LAYER %d" % [run.current_layer + 1], "\n".join(lines), actions)

func _select_node(node_id: String) -> void:
	var node := run_manager.select_node(node_id)
	match str(node.get("type", "")):
		"encounter", "elite", "final":
			var snapshot := run_manager.state.combat_snapshot()
			snapshot["objective"] = str(node.get("objective", "kill"))
			state.start_battle(int(node["battle"]), snapshot, bool(node.get("elite", false)))
			if state.battle_index == 0:
				if not run_manager.state.knowledge.enemy_records.has("ROOT HUSK"):
					run_manager.state.knowledge.enemy_records["ROOT HUSK"] = "REGROWTH: after 2 turns without Structure damage, restore 6 Structure.\nA second trait is not discovered yet."
			elif state.battle_index == 1:
				run_manager.state.knowledge.enemy_records["VEIL MOTH"] = "FALSE INTENT: two possible actions; OBSERVE removes the false possibility.\nObscurity still reduces clarity."
			elif state.battle_index == 2:
				run_manager.state.knowledge.enemy_records["NEGLECT WRAITH"] = "MISSED WINDOW: Inattention makes warnings less reliable, but never removes a DEFLECT opportunity."
			elif state.battle_index in [4, 5]:
				run_manager.state.knowledge.enemy_records[str(state.enemy["name"])] = str(state.enemy["tutorial"])
			run_manager.state.temporary_cards.clear()
			mulligan_selection.clear()
			_refresh()
			_show_mulligan()
		"anomaly":
			_show_semantic_anomaly()
		"event":
			_show_event()
		"cache":
			_show_cache()
		"extract":
			run_manager.extract()
			_show_run_summary()

func _resolve_anomaly(choice: String) -> void:
	var result := run_manager.resolve_anomaly(choice)
	_sync_state_from_run()
	_show_modal("ANOMALY RESOLVED", result, [{"text": "RETURN TO MAP", "callback": _show_map}])

func _show_event() -> void:
	var event := run_manager.current_event
	var actions: Array = []
	for choice in event["choices"]:
		actions.append({
			"text": "%s · %s" % [choice["title"], choice["effect"]],
			"callback": _resolve_event_choice.bind(str(choice["id"])),
		})
	_show_modal(str(event["title"]), "%s\n\n%s" % [event["body"], run_manager.state.condition_text()], actions)

func _resolve_event_choice(choice_id: String) -> void:
	var result := run_manager.resolve_event(choice_id)
	_sync_state_from_run()
	_show_modal("EVENT RESOLVED", "%s\n\n%s" % [result, run_manager.state.condition_text()], [{"text": "RETURN TO MAP", "callback": _show_map}])

func _show_cache() -> void:
	var actions: Array = []
	for choice in RunContent.CACHE_CHOICES:
		var effect := str(choice["effect"])
		if str(choice["id"]) == "echo" and run_manager.state.active_reward_multiplier > 1.0:
			effect = "+30 → +%d Echo · PRESS ON" % run_manager.state.preview_echo(30)
		actions.append({
			"text": "%s · %s" % [choice["title"], effect],
			"callback": _resolve_cache_choice.bind(str(choice["id"])),
		})
	_show_modal("SUPPLY CACHE", "Only one resource can be carried forward.\n\n%s" % run_manager.state.condition_text(), actions)

func _resolve_cache_choice(choice_id: String) -> void:
	var result := run_manager.resolve_cache(choice_id)
	_sync_state_from_run()
	_show_modal("CACHE CLAIMED", "%s\n\n%s" % [result, run_manager.state.condition_text()], [{"text": "RETURN TO MAP", "callback": _show_map}])

func _show_breather() -> void:
	var settlement: Dictionary = pending_combat_result["settlement"]
	var before: Dictionary = settlement["corruption_before"]
	var after: Dictionary = settlement["corruption_after"]
	var body := "Victory reward: +%d Echo\nAutomatic rebuild: Armor %d → %d\nNatural dissipation: D %d→%d · O %d→%d · I %d→%d\n\n%s" % [
		int(pending_combat_result["echo"]), int(settlement["armor_before"]), int(settlement["armor_after"]),
		int(before["Decay"]), int(after["Decay"]), int(before["Obscurity"]), int(after["Obscurity"]),
		int(before["Inattention"]), int(after["Inattention"]), run_manager.state.condition_text(),
	]
	_show_modal("BREATHER", body, [
		{"text": "RECOVER · +6 HP (or +4 Armor at full HP)", "callback": _choose_breather.bind("recover")},
		{"text": "STABILIZE · Dominant Corruption -12", "callback": _choose_breather.bind("stabilize")},
		{"text": "PRESS ON · Next node reward ×1.25", "callback": _choose_breather.bind("press_on")},
	])

func _choose_breather(choice: String) -> void:
	var result := run_manager.choose_breather(choice)
	_sync_state_from_run()
	if bool(pending_combat_result.get("elite", false)) or state.battle_index == 0:
		_show_relic_reward(str(result["description"]))
	else:
		_show_modal("BREATHER COMPLETE", "%s\n\n%s" % [result["description"], run_manager.state.condition_text()], [{"text": "RETURN TO MAP", "callback": _show_map}])

func _show_relic_reward(breather_result: String) -> void:
	var actions: Array = []
	for relic_id in RunContent.RELICS:
		if run_manager.state.relics.has(relic_id):
			continue
		var relic: Dictionary = RunContent.RELICS[relic_id]
		actions.append({
			"text": "%s · %s · %s" % [relic["rarity"], relic["name"], relic["description"]],
			"accent": RunContent.RARITY_COLORS[relic["rarity"]],
			"callback": _claim_relic.bind(str(relic_id)),
		})
	_show_modal("RELIC REWARD", "%s\n\nChoose one rule-changing Relic." % breather_result, actions)

func _claim_relic(relic_id: String) -> void:
	run_manager.claim_relic(relic_id)
	_sync_state_from_run()
	var relic: Dictionary = RunContent.RELICS[relic_id]
	_show_modal("%s CLAIMED" % relic["name"], "%s\n\n%s" % [relic["description"], run_manager.state.condition_text()], [{"text": "RETURN TO MAP", "callback": _show_map}])

func _relic_names() -> String:
	if run_manager.state.relics.is_empty():
		return "None"
	var names: Array[String] = []
	for relic_id in run_manager.state.relics:
		names.append(str(RunContent.RELICS[relic_id]["name"]))
	return ", ".join(names)

func _format_modal_body(text_value: String) -> String:
	# Format prose only; preserve existing rows, paragraphs and decimal numbers.
	var english_end := RegEx.create_from_string("([.!?])[ \\t]+(?=[A-Z0-9])")
	var chinese_end := RegEx.create_from_string("([。！？])[ \\t]*(?=[^\\n\\r。！？])")
	return chinese_end.sub(english_end.sub(text_value, "$1\n", true), "$1\n", true)

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
	var card := preload("res://scripts/ui/adaptive_modal.gd").new()
	card.add_theme_stylebox_override("panel", _style(Color("162333"), Color("49647e"), 10, 0, 1))
	modal.add_child(card)
	var title := _make_label("", Vector2.ZERO, Vector2.ZERO, 22, GOLD)
	title.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	title.text = title_text
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	var body := _make_label("", Vector2.ZERO, Vector2.ZERO, 14, Color("c1ccd7"))
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	body.text = _format_modal_body(body_text)
	body.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	var buttons: Array[Button] = []
	for index in range(actions.size()):
		var action: Dictionary = actions[index]
		var button := _make_button("", Vector2.ZERO, Vector2.ZERO, action.get("accent", GOLD if index == 0 else Color("74869a")))
		button.name = "Action%d" % index
		button.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		button.text = str(action["text"])
		button.custom_minimum_size.y = 38
		var callback: Callable = action["callback"]
		button.pressed.connect(func():
			_clear_modal()
			callback.call()
			_refresh()
		)
		buttons.append(button)
	card.configure(title, body, buttons)
	modal.resized.connect(func(): card.fit_to_area(modal.size))
	card.fit_to_area(modal.size)
	_refresh()

func _sync_state_from_run() -> void:
	var run := run_manager.state
	state.hp = run.hp
	state.armor = run.armor
	state.corruption = run.corruption.duplicate(true)
	state.statuses = run.statuses.duplicate(true)
	state.inattention_tier = run.inattention_tier

func _pulse_status(_tier_name: String) -> void:
	var tween := create_tween()
	status_label.modulate = GOLD
	tween.tween_property(status_label, "modulate", Color.WHITE, 0.65)

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
	if event.keycode >= KEY_1 and event.keycode <= KEY_9:
		index = event.keycode - KEY_1
	if index >= 0 and index < state.deck.hand.size():
		_on_card_pressed(int(state.deck.hand[index]["instance_id"]))
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
