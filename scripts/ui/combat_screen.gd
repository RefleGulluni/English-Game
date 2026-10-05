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
var lesson_words: Array[String] = []
var lesson_is_combat := false
var lesson_source := ""
var dev_previous: Control
var dev_open := false
const CEMETERY_WORDS := preload("res://scripts/run/cemetery_words.gd")

func _ready() -> void:
	set_process_unhandled_key_input(true)
	_build_interface()
	state.changed.connect(_refresh)
	state.reaction_requested.connect(_show_reaction)
	state.battle_finished.connect(_on_battle_finished)
	state.inattention_tier_changed.connect(_pulse_status)
	state.combo_discovered.connect(_on_combo_discovered)
	if bool(get_meta("legacy_run", false)):
		run_manager.start_run()
	else:
		run_manager.start_cemetery_run()
	run_manager.state.knowledge.changed.connect(_on_knowledge_changed)
	run_manager.state.toxic_knowledge.changed.connect(_on_knowledge_changed)
	_connect_target_words()
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

	var subtitle := _make_label("MINI RUN PROTOTYPE 0.7", Vector2(28, 48), Vector2(280, 22), 12, MUTED)
	add_child(subtitle)

	stage_label = _make_label("", Vector2(360, 19), Vector2(560, 42), 15, INK)
	stage_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	add_child(stage_label)

	var reset := _make_button("RESTART RUN", Vector2(1098, 20), Vector2(150, 38), Color("7d8da1"))
	reset.pressed.connect(_restart_run)
	add_child(reset)
	if OS.has_feature("editor") or OS.is_debug_build():
		var dev_button := _make_button("DEV", Vector2(1028, 20), Vector2(60, 38), MUTED)
		dev_button.name = "DevButton"
		dev_button.z_index = 102
		dev_button.pressed.connect(_show_dev_panel)
		add_child(dev_button)

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
	var lexicon_button := get_node_or_null("LexiconButton") as Button
	if is_instance_valid(lexicon_button):
		lexicon_button.visible = not dev_open
	var dev_button := get_node_or_null("DevButton") as Button
	if is_instance_valid(dev_button):
		dev_button.disabled = lexicon_open
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
	if state.enemy.is_empty():
		end_turn_button.disabled = true
		return

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
	if state.bone_remains:
		enemy_armor_label.text = "BONE REMAINS · INTEGRITY %d/10" % state.remains_hp
		enemy_armor_bar.visible = true
		enemy_armor_bar.max_value = 10
		enemy_armor_bar.value = state.remains_hp
	intent_badge.text = state.clarity_name()
	intent_badge.add_theme_color_override("font_color", _clarity_color(state.intent_clarity))
	intent_title.text = state.intent_title()
	intent_text.text = state.intent_description()
	var known_word = state.toxic_knowledge if state.intent.has("poison") else state.knowledge
	var intent_lemma := CEMETERY_WORDS.lemma(str(state.intent.get("word", "")))
	if state.target_knowledge.has(intent_lemma):
		known_word = state.target_knowledge[intent_lemma]
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
			text += "\nCONTEXT CARD · Learn in world contexts"
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
			if state.bone_remains:
				var bonus := 2 if "ossuary_key" in state.relics else 0
				summaries["SHATTER"] = "REMAINS · Integrity -%d" % (8 + bonus)
				summaries["STRIKE"] = "REMAINS · Integrity -%d" % (3 + bonus)
				summaries["BIND"] = "REASSEMBLY · Countdown +1, once"
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
	if run_manager.cemetery:
		return "CEMETERY · LAYER %d / 6 · %s · TURN %d" % [mini(6, run_manager.state.current_layer + 1), state.enemy.get("name", "CHOOSE A PATH"), state.turn]
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
	if run_manager.cemetery:
		title = "BIOME CLEAR" if run.victory else "CONNECTION BROKEN"
		summary = "CEMETERY · Seed %d\nBoss Result: %s\nEcho: %d\nRelics: %s\nBuild tendencies: %s\n\nTarget Words:" % [run.seed_value, "DEFEATED" if run.victory else "NOT DEFEATED", run.echo, _relic_names(), _build_tendencies()]
		var usable: Array[String] = []
		for word in run.target_knowledge.values():
			summary += "\n%s · %s" % [word.lemma, word.current_state]
			if word.current_state == "USABLE":
				usable.append(word.lemma)
		for word in [run.knowledge, run.toxic_knowledge]:
			if word.current_state == "USABLE":
				usable.append(word.lemma)
		summary += "\nNew USABLE Words: " + (", ".join(usable) if not usable.is_empty() else "NONE")
		summary += "\nThe world forgets. You do not.\nPrototype Lexicon resets next run."
	_show_modal(title, summary, [{"text": "BEGIN ANOTHER RUN", "callback": _restart_run}])

func _restart_run() -> void:
	_clear_modal()
	knowledge_notice.text = "Knowledge = Tactical Advantage"
	state.metrics = {"observe_uses": 0, "bind_uses": 0, "stabilize_uses": 0, "deflect_uses": 0, "focus_reserved": 0, "intents_countered": 0}
	state.exposure.clear()
	run_manager.run_index += 1
	if bool(get_meta("legacy_run", false)):
		run_manager.start_run()
	else:
		run_manager.start_cemetery_run()
	state = _new_connected_combat()
	_sync_state_from_run()
	mulligan_selection.clear()
	toxic_training_in_combat = false
	_connect_target_words()
	pending_combat_result.clear()
	_show_run_entry()

func _show_run_entry() -> void:
	if run_manager.cemetery:
		_show_modal("CEMETERY ENTRY", "Seed %d\nSix layers. Ghosts conceal, Skeletons reassemble, Wraiths linger.\nGrave Pressure starts at zero each encounter and rises every round.\nTargets: %s\n\nThe world forgets. You do not." % [run_manager.state.seed_value, ", ".join(run_manager.state.target_knowledge.keys())], [{"text": "ENTER CEMETERY", "callback": _show_inscription}])
		return
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
	if not dev_open and not is_instance_valid(modal) and not state.finished and state.battle_index in [4, 7] and run_manager.state.toxic_knowledge.current_state == "UNDERSTOOD" and not run_manager.state.toxic_knowledge.transfer_offered:
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
	toxic_training_in_combat = state.battle_index in [4, 7] and not state.finished and not state.enemy.is_empty()
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
	if lexicon_open or dev_open:
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
	for target in run_manager.state.target_knowledge.values():
		body += "\n\n" + target.entry_text()
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
	if run_manager.cemetery:
		lines.push_front("CEMETERY · Seed %d\nTargets: %s" % [run.seed_value, ", ".join(run.target_knowledge.keys())])
	_show_modal(("CEMETERY MAP" if run_manager.cemetery else "FRACTURE MAP") + " · LAYER %d" % [run.current_layer + 1], "\n".join(lines), actions)

func _select_node(node_id: String) -> void:
	var node := run_manager.select_node(node_id)
	if node.is_empty():
		return
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
			if run_manager.cemetery:
				_begin_cemetery_lessons(node, true)
			else:
				_show_mulligan()
		"anomaly":
			_show_semantic_anomaly()
		"event":
			if run_manager.cemetery:
				_begin_cemetery_lessons(node, false)
			else:
				_show_event()
		"rest":
			_show_cemetery_rest()
		"relic":
			_show_relic_reward("You found a preserved Relic.")
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
	if bool(pending_combat_result.get("elite", false)) or (state.battle_index == 0 and not run_manager.cemetery):
		_show_relic_reward(str(result["description"]))
	else:
		_show_modal("BREATHER COMPLETE", "%s\n\n%s" % [result["description"], run_manager.state.condition_text()], [{"text": "RETURN TO MAP", "callback": _show_map}])

func _show_relic_reward(breather_result: String) -> void:
	var actions: Array = []
	var pool: Array = run_manager.offer_relics() if run_manager.cemetery else RunContent.RELICS.keys()
	for relic_id in pool:
		if run_manager.state.relics.has(relic_id):
			continue
		var relic: Dictionary = RunContent.RELICS[relic_id]
		actions.append({
			"text": "%s · %s · %s" % [relic["rarity"], relic["name"], relic["description"]],
			"accent": RunContent.RARITY_COLORS[relic["rarity"]],
			"callback": _claim_relic.bind(str(relic_id)),
		})
	if run_manager.cemetery:
		actions.append({"text": "SKIP RELIC", "callback": _claim_relic.bind("")})
	_show_modal("RELIC REWARD", "%s\n\nChoose one rule-changing Relic." % breather_result, actions)

func _claim_relic(relic_id: String) -> void:
	if run_manager.cemetery:
		run_manager.finish_relic_choice(relic_id)
		_sync_state_from_run()
		_show_map()
		return
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
	if event.pressed and not event.echo and event.keycode == KEY_F2 and (OS.has_feature("editor") or OS.is_debug_build()):
		_show_dev_panel()
		get_viewport().set_input_as_handled()
		return
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

func _connect_target_words() -> void:
	for word in run_manager.state.target_knowledge.values():
		if not word.changed.is_connected(_on_knowledge_changed):
			word.changed.connect(_on_knowledge_changed)

func _begin_cemetery_lessons(node: Dictionary, combat: bool) -> void:
	lesson_words.clear()
	lesson_source = str(node.id)
	lesson_is_combat = combat
	for id in node.get("words", []):
		if run_manager.state.target_knowledge.has(id):
			lesson_words.append(str(id))
	_show_cemetery_lesson_menu()

func _show_cemetery_lesson_menu() -> void:
	var actions: Array = []
	var body := "Read the scene, infer a meaning, connect its consequence, then use the word.\nWrong answers never remove resources. You may leave without learning."
	if lesson_is_combat:
		body = "Before the encounter, infer the word from the scene. Combat consequences provide separate context; this does not grant it automatically."
	for id in lesson_words:
		var word = run_manager.state.target_knowledge[id]
		word.encounter()
		if word.current_state == "USABLE" or (lesson_is_combat and word.is_recognized()):
			continue
		actions.append({"text": "%s · %s" % [id, word.current_state], "callback": _show_cemetery_exercise.bind(id)})
	if lesson_is_combat and actions.is_empty():
		_show_mulligan()
		return
	actions.append({"text": "CONTINUE TO COMBAT" if lesson_is_combat else "LEAVE THIS EVENT", "callback": _finish_cemetery_lesson})
	_show_modal(str(run_manager.selected_node.get("title", "CEMETERY CONTEXT")), body, actions)

func _show_cemetery_exercise(id: String) -> void:
	var word = run_manager.state.target_knowledge[id]
	var data: Array = CEMETERY_WORDS.DATA[id]
	var stage := "recognition" if not word.is_recognized() else ("context" if word.current_state == "RECOGNIZED" else "production")
	var prompt := str(data[1]) + "\nWhat does %s mean here?" % id
	var correct := str(data[0])
	var options: Array[String] = [correct, "restore physical health immediately", "tie a moving object in place"]
	if stage == "context":
		prompt = "%s\nA second context: %s\nWhich relationship fits the word?" % [data[1], data[2]]
		correct = str(data[2])
		options = [correct, "This word always causes direct HP damage.", "The effect has no relationship to the scene."]
	elif stage == "production":
		prompt = str(data[3]) + "\nChoose the word that completes this new use."
		correct = id
		options = [id, "STRIKE", "RESTORE"]
	var rng := RandomNumberGenerator.new()
	rng.seed = run_manager.state.seed_value + id.hash() + stage.hash() + lesson_source.hash()
	for index in range(options.size() - 1, 0, -1):
		var other := rng.randi_range(0, index)
		var value := options[index]
		options[index] = options[other]
		options[other] = value
	var actions: Array = []
	for option in options:
		actions.append({"text": option, "callback": _answer_cemetery_exercise.bind(id, stage, option == correct)})
	actions.append({"text": "SKIP THIS EXERCISE", "callback": _show_cemetery_lesson_menu})
	_show_modal("%s · %s" % [id, stage.to_upper()], prompt, actions)

func _answer_cemetery_exercise(id: String, stage: String, correct: bool) -> void:
	if not correct:
		_show_modal("TRY ANOTHER MEANING", "This choice does not fit the scene.\nNo resources or previous evidence were lost.", [{"text": "TRY AGAIN", "callback": _show_cemetery_exercise.bind(id)}, {"text": "RETURN TO SCENE", "callback": _show_cemetery_lesson_menu}])
		return
	var word = run_manager.state.target_knowledge[id]
	match stage:
		"recognition": word.recognize(lesson_source)
		"context": word.context(lesson_source)
		"production": word.produce(lesson_source, true)
	if lesson_is_combat or word.current_state == "USABLE":
		_show_cemetery_lesson_menu()
	else:
		_show_cemetery_exercise(id)

func _finish_cemetery_lesson() -> void:
	if lesson_is_combat:
		_show_mulligan()
	else:
		run_manager.finish_learning_event()
		_show_map()

func _show_cemetery_rest() -> void:
	_show_modal("SHELTERED GRAVE", "A quiet shelter, not a forced campfire.\nChoose recovery, stability, or keep moving.", [{"text": "RECOVER · +6 HP / +4 Armor if full", "callback": _resolve_cemetery_rest.bind("recover")}, {"text": "STABILIZE · Dominant Corruption -12", "callback": _resolve_cemetery_rest.bind("stabilize")}, {"text": "PRESS ON · Next reward ×1.25", "callback": _resolve_cemetery_rest.bind("press_on")}])

func _resolve_cemetery_rest(choice: String) -> void:
	run_manager.rest(choice)
	_sync_state_from_run()
	_show_map()

func _build_tendencies() -> String:
	var tags: Array[String] = []
	for id in run_manager.state.relics:
		var tag := str({"clear_lens": "INFORMATION", "mourner_thread": "INFORMATION", "iron_script": "BREAK", "venom_vessel": "TOXIC", "ossuary_key": "PERSISTENCE", "pale_candle": "CONTROL / SURVIVAL", "echo_chamber": "RULE-BENDING", "unfinished_sentence": "RETAIN"}.get(id, "CONTROL"))
		if tag not in tags:
			tags.append(tag)
	return ", ".join(tags) if not tags.is_empty() else "NO RELIC BUILD YET"

func _show_dev_panel() -> void:
	if lexicon_open or not (OS.has_feature("editor") or OS.is_debug_build()):
		return
	if not dev_open:
		dev_open = true
		dev_previous = modal
		if is_instance_valid(dev_previous):
			dev_previous.hide()
		modal = null
	var actions: Array = []
	for field in ["Seed", "Layer", "Targets", "Word State", "Relic", "HP", "Focus", "Corruption", "Grave Pressure"]:
		actions.append({"text": "SET " + field.to_upper(), "callback": _show_dev_input.bind(field)})
	for pair in [["Ghost", 5], ["Veil Ghost", 6], ["Grave Skeleton", 7], ["Neglect Wraith", 2], ["Mourning Wraith", 8], ["Boss", 9], ["Root Husk (0.6)", 0], ["Iron Shell (0.6)", 4]]:
		actions.append({"text": "ENTER " + str(pair[0]).to_upper() + " TEST", "callback": _dev_enter_enemy.bind(int(pair[1]))})
	actions.append({"text": "TRIGGER SPECIFIC EVENT", "callback": _show_dev_input.bind("Event")})
	actions.append({"text": "RESET MINIRUN LEXICON", "callback": _dev_reset_lexicon})
	actions.append({"text": "INSPECT CURRENT WEIGHTS", "callback": _show_weight_inspector})
	actions.append({"text": "CLOSE DEV PANEL", "callback": _close_dev_panel})
	_show_modal("DEV PANEL · QA ONLY", "Seed %d · Layer %d\nInputs change this test run only. Seed restarts the run.\nF2 opens this panel. Release exports hide it." % [run_manager.state.seed_value, run_manager.state.current_layer + 1], actions)

func _close_dev_panel() -> void:
	dev_open = false
	if is_instance_valid(dev_previous):
		modal = dev_previous
		modal.show()
	dev_previous = null
	_refresh()

func _dev_abandon_previous() -> void:
	if is_instance_valid(dev_previous):
		dev_previous.queue_free()
	dev_previous = null
	dev_open = false
	lexicon_open = false

func _show_dev_input(field: String) -> void:
	var hints := {"Seed": "Integer; starts a new reproducible run.", "Layer": "1–6; invalidates cached map choices.", "Targets": "MOURN,LINGER,CONCEAL,REASSEMBLE,REMAINS (choose any compatible fifth word).", "Word State": "MOURN,UNDERSTOOD (or RECOGNIZED / USABLE / UNKNOWN).", "Relic": "Relic ID: clear_lens / unfinished_sentence / iron_script / venom_vessel / mourner_thread / ossuary_key / pale_candle / echo_chamber.", "HP": "0–50; zero ends an active combat as defeat.", "Focus": "0–4; active combat only.", "Corruption": "Obscurity,40 (Decay / Inattention also supported).", "Grave Pressure": "0–100; active combat only.", "Event": "mourning_stone / hidden_epitaph / scattered_bones / lingering_bell / grave_inscription / caretaker_note / withered_flowers."}
	var input := LineEdit.new()
	input.name = "DevInput"
	input.placeholder_text = "Enter test value"
	input.custom_minimum_size.y = 36
	_show_modal("DEV · " + field.to_upper(), str(hints[field]), [{"text": "APPLY", "callback": func():
		var valid := _dev_apply(field, input.text)
		if not valid:
			_show_modal("INVALID DEV VALUE", "No change was applied. Check the range, word, or identifier.", [{"text": "TRY AGAIN", "callback": _show_dev_input.bind(field)}])
		elif field not in ["Seed", "Layer", "Targets", "Event"]:
			_show_dev_panel()
	}, {"text": "BACK", "callback": _show_dev_panel}])
	var card = modal.find_child("ModalCard", true, false)
	card.actions_box.add_child(input)
	card.actions_box.move_child(input, 0)
	input.minimum_size_changed.connect(card._queue_layout)
	card._queue_layout()
	input.grab_focus()

func _dev_apply(field: String, raw: String) -> bool:
	var value := raw.strip_edges()
	var parts := value.split(",", false)
	if field in ["Seed", "Layer", "HP", "Focus", "Grave Pressure"] and not value.is_valid_int():
		return false
	var number := int(value)
	match field:
		"Seed":
			if number < 0: return false
			_dev_abandon_previous()
			run_manager.start_cemetery_run(number)
			state = _new_connected_combat()
			_connect_target_words()
			_show_run_entry()
		"Layer":
			if number < 1 or number > 6: return false
			_dev_abandon_previous()
			run_manager.state.current_layer = number - 1
			run_manager.state.completed = false
			run_manager.state.victory = false
			run_manager.state.extracted = false
			run_manager.director.cache.clear()
			_show_map()
		"Targets":
			var ids: Array = []
			for part in parts: ids.append(part.strip_edges().to_upper())
			if not run_manager.set_targets(ids): return false
			_connect_target_words()
			state.target_knowledge = run_manager.state.target_knowledge
			_dev_abandon_previous()
			_show_map()
		"Word State":
			if parts.size() != 2: return false
			var id := CEMETERY_WORDS.lemma(parts[0].strip_edges())
			var target := parts[1].strip_edges().to_upper()
			if run_manager.state.target_knowledge.has(id):
				if not run_manager.state.target_knowledge[id].dev_set_state(target): return false
			elif id in ["ERODE", "TOXIC"]:
				if target not in ["UNKNOWN", "RECOGNIZED", "UNDERSTOOD", "USABLE"]: return false
				var word = run_manager.state.knowledge if id == "ERODE" else run_manager.state.toxic_knowledge
				word.reset()
				if target != "UNKNOWN": word.recognize("dev")
				if target in ["UNDERSTOOD", "USABLE"]: word.record_combat_context(true)
				if target == "USABLE":
					word.record_transfer(true)
					word.record_production(true)
			else: return false
		"Relic":
			if value not in RunContent.RELICS: return false
			run_manager.state.add_relic(value)
			state.relics.assign(run_manager.state.relics)
		"HP":
			if number < 0 or number > 50: return false
			run_manager.state.hp = number
			state.hp = number
			if number == 0 and not state.enemy.is_empty() and not state.finished: state._finish_battle(false)
		"Focus":
			if number < 0 or number > 4 or state.enemy.is_empty(): return false
			state.focus = number
		"Corruption":
			if parts.size() != 2 or parts[0] not in run_manager.state.corruption or not parts[1].is_valid_int(): return false
			var amount := int(parts[1])
			if amount < 0 or amount > 100: return false
			run_manager.state.corruption[parts[0]] = amount
			run_manager.state.refresh_lingering_statuses()
			state.corruption[parts[0]] = amount
			state._update_threshold_statuses()
		"Grave Pressure":
			if number < 0 or number > 100 or state.enemy.is_empty(): return false
			state.grave_pressure = number
		"Event":
			var node := preload("res://scripts/run/cemetery_content.gd").node(value)
			if node.get("type", "") != "event": return false
			_dev_abandon_previous()
			run_manager.selected_node = node
			run_manager.state.begin_node(value)
			_begin_cemetery_lessons(node, false)
		_: return false
	run_manager.state.history.append("DEV: %s = %s" % [field, value])
	_refresh()
	return true

func _new_connected_combat() -> CombatState:
	var combat := CombatState.new()
	combat.changed.connect(_refresh)
	combat.reaction_requested.connect(_show_reaction)
	combat.battle_finished.connect(_on_battle_finished)
	combat.inattention_tier_changed.connect(_pulse_status)
	combat.combo_discovered.connect(_on_combo_discovered)
	return combat

func _dev_enter_enemy(index: int) -> void:
	_dev_abandon_previous()
	run_manager.selected_node = {"id": "dev_test", "type": "encounter", "title": "DEV ENCOUNTER", "echo": 0, "detour": true}
	var snapshot := run_manager.state.combat_snapshot()
	snapshot.objective = "survive" if index == 2 else "kill"
	state.start_battle(index, snapshot)
	_show_mulligan()

func _dev_reset_lexicon() -> void:
	run_manager.state.knowledge.reset()
	run_manager.state.toxic_knowledge.reset()
	for word in run_manager.state.target_knowledge.values(): word.reset()
	_show_dev_panel()

func _show_weight_inspector() -> void:
	var choices := run_manager.available_nodes()
	var lines: Array[String] = ["Final = Base × Biome × Layer × Learning × Rhythm × Repetition", "Seed %d · Layer %d" % [run_manager.state.seed_value, run_manager.state.current_layer + 1], "Frozen generation weights; future layers use updated evidence.", "CURRENT CHOICES / CONSTRAINTS:"]
	for node in choices:
		lines.append("%s · %s" % [node.title, "LEARNING GUARANTEE" if bool(node.get("guarantee", false)) else ("FIXED BOSS" if node.type == "final" else "WEIGHTED / RHYTHM CONSTRAINT")])
	for row in run_manager.director.weights:
		lines.append("%s\nBase %.2f × Biome %.2f × Layer %.2f × Learning %.2f × Rhythm %.2f × Repetition %.2f = Final %.2f" % [row.id, row.base_weight, row.biome_modifier, row.layer_modifier, row.learning_modifier, row.rhythm_modifier, row.repetition_modifier, row.final_weight])
	_show_modal("WEIGHT INSPECTOR", "\n\n".join(lines), [{"text": "BACK TO DEV", "callback": _show_dev_panel}])
