extends SceneTree

var failures: Array[String] = []

func _initialize() -> void:
	_run.call_deferred()

func _settle() -> void:
	for frame in range(16):
		await process_frame

func _run() -> void:
	var screen := (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(screen)
	await _settle()
	var entry_card: Control = screen.modal.get_node("ModalCard")
	var entry_body: Label = entry_card.find_child("Body", true, false)
	_check(entry_body.get_line_count() > 1, "entry description wraps")
	_check_bounds(screen)
	screen._show_reaction({"word": "DUST CUT"}, 1)
	await _settle()
	var reaction_body: Label = screen.modal.get_node("ModalCard").find_child("Body", true, false)
	_check(reaction_body.text == "DUST CUT is moving toward you.\nSpend 1 reserved Focus to change its direction?", "reaction explanation and question start on separate lines")
	_check(reaction_body.get_line_count() == 2, "reaction question fits on one line at default width")
	_check_bounds(screen)
	var long_text := "Long English description with rewards and conditions. ".repeat(100)
	screen._show_modal("AUTOMATIC LAYOUT TEST", long_text, [
		{"text": "A long option with a complete explanation and a reward description. ".repeat(8), "callback": screen._show_map},
		{"text": "RETURN TO MAP", "callback": screen._show_map},
	])
	await _settle()
	_check_bounds(screen)
	var card: Control = screen.modal.get_node("ModalCard")
	var body_scroll: ScrollContainer = card.find_child("BodyScroll", true, false)
	_check(body_scroll.get_v_scroll_bar().max_value > body_scroll.size.y, "very long body can scroll")
	var button: Button = card.find_child("Action0", true, false)
	_check(button.size.y > 38, "long option grows vertically")
	for area in [Vector2(800, 600), Vector2(480, 360), Vector2(1600, 900)]:
		screen.size = area
		await _settle()
		_check_bounds(screen)
	button.pressed.emit()
	await _settle()
	_check(is_instance_valid(screen.modal), "wrapped option callback still opens map")
	screen.queue_free()
	await process_frame
	for failure in failures:
		push_error(failure)
	print("MODAL_LAYOUT_SMOKE: %s" % ("PASS" if failures.is_empty() else "FAIL"))
	quit(0 if failures.is_empty() else 1)

func _check_bounds(screen: Control) -> void:
	var card: Control = screen.modal.get_node("ModalCard")
	var bounds := card.get_global_rect()
	_check(card.size.x <= screen.modal.size.x - 47 and card.size.y <= screen.modal.size.y - 47, "modal fits available area")
	_check(bounds.get_center().distance_to(screen.modal.get_global_rect().get_center()) < 1, "modal stays centered")
	for region_name in ["BodyScroll", "ActionsScroll"]:
		var region: Control = card.find_child(region_name, true, false)
		_check(bounds.encloses(region.get_global_rect()), "scroll region stays inside card")
		var content: Control = region.get_child(0)
		_check(content.size.x <= region.size.x + 1, "text and options cannot widen card")
		_check(absf(content.get_global_rect().get_center().x - bounds.get_center().x) < 12, "content stays centered allowing scrollbar gutter")

func _check(condition: bool, message: String) -> void:
	if not condition:
		failures.append(message)
