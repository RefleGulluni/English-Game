extends Panel

# The two scroll regions isolate text minimum sizes from the card width.
var title_label: Label
var body_label: Label
var body_scroll: ScrollContainer
var actions_scroll: ScrollContainer
var actions_box: VBoxContainer
var layout_box: VBoxContainer
var available_size := Vector2(1280, 720)
var layout_pending := false

func configure(title: Label, body: Label, buttons: Array[Button]) -> void:
	name = "ModalCard"
	var margins := MarginContainer.new()
	margins.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	for edge in ["left", "right", "top", "bottom"]:
		margins.add_theme_constant_override("margin_" + edge, 24)
	add_child(margins)
	layout_box = VBoxContainer.new()
	layout_box.add_theme_constant_override("separation", 20)
	margins.add_child(layout_box)
	title_label = title
	title_label.name = "Title"
	layout_box.add_child(title_label)
	body_scroll = _scroll_region("BodyScroll")
	layout_box.add_child(body_scroll)
	body_label = body
	body_label.name = "Body"
	body_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	body_scroll.add_child(body_label)
	actions_scroll = _scroll_region("ActionsScroll")
	layout_box.add_child(actions_scroll)
	actions_box = VBoxContainer.new()
	actions_box.name = "Actions"
	actions_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	actions_box.add_theme_constant_override("separation", 10)
	actions_scroll.add_child(actions_box)
	for button in buttons:
		actions_box.add_child(button)
		button.minimum_size_changed.connect(_queue_layout)
	title_label.minimum_size_changed.connect(_queue_layout)
	body_label.minimum_size_changed.connect(_queue_layout)
	layout_box.resized.connect(_queue_layout)
	fit_to_area(available_size)

func _scroll_region(region_name: String) -> ScrollContainer:
	var region := ScrollContainer.new()
	region.name = region_name
	region.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	region.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_AUTO
	region.follow_focus = true
	return region

func fit_to_area(area: Vector2) -> void:
	available_size = area
	size.x = minf(550.0, maxf(1.0, area.x - 48.0))
	_queue_layout()

func _queue_layout() -> void:
	if not layout_pending:
		layout_pending = true
		_reflow.call_deferred()

func _reflow() -> void:
	layout_pending = false
	if not is_inside_tree():
		return
	var max_height := maxf(1.0, available_size.y - 48.0)
	var fixed_height := 48.0 + 40.0 + title_label.get_combined_minimum_size().y
	var region_budget := maxf(1.0, max_height - fixed_height)
	# Short prose gives unused space to choices without per-dialogue sizing.
	var body_height := minf(body_label.get_combined_minimum_size().y, region_budget * 0.55)
	var actions_height := minf(actions_box.get_combined_minimum_size().y, region_budget - body_height)
	body_height = minf(body_label.get_combined_minimum_size().y, region_budget - actions_height)
	body_scroll.custom_minimum_size.y = maxf(1.0, body_height)
	actions_scroll.custom_minimum_size.y = maxf(1.0, actions_height)
	size.y = minf(max_height, fixed_height + body_height + actions_height)
	position = (available_size - size) * 0.5
