extends Control

func _ready() -> void:
	var title := Label.new()
	title.text = "ENGLISH GAME"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 52)
	title.add_theme_color_override("font_color", Color("d7c49e"))
	title.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(title)

	var subtitle := Label.new()
	subtitle.text = "Combat Prototype 0.1 · Project connected"
	subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	subtitle.position = Vector2(0, 410)
	subtitle.size = Vector2(1280, 40)
	subtitle.add_theme_font_size_override("font_size", 20)
	subtitle.add_theme_color_override("font_color", Color("8293a8"))
	add_child(subtitle)
