extends CanvasLayer
## Room and area transitions (Decision Log D-022). One black cover for both:
##   room -> room in the same area: quick fade, about 0.4 s in total;
##   entering a new area: slow fade, the area name written in language-layer cyan, slow reveal.
## Only a clean fade: no glitch, tearing or pixel displacement (the Fracture never breaks the grid).
## Lives inside the 960x540 world viewport, so the title sits on the native pixel grid.

const ROOM_SECONDS := 0.2 # each way
const AREA_SECONDS := 0.8 # each way
const TITLE_SECONDS := 1.4 # writing the name, then a short hold
const CYAN := Color(0.42, 0.86, 0.95)
const FONT := preload("res://art/ui/fonts/CormorantGaramond.ttf")

var _cover: ColorRect
var _title: Label


func _init() -> void:
	layer = 20
	_cover = ColorRect.new()
	_cover.color = Color.BLACK
	_cover.size = Vector2(960, 540)
	_cover.modulate.a = 0.0
	_cover.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_cover)
	_title = Label.new()
	_title.size = Vector2(960, 540)
	_title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_title.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_title.add_theme_font_override("font", FONT)
	_title.add_theme_font_size_override("font_size", 32)
	_title.add_theme_color_override("font_color", CYAN)
	_title.add_theme_color_override("font_shadow_color", Color(CYAN, 0.25))
	_title.add_theme_constant_override("shadow_offset_x", 0)
	_title.add_theme_constant_override("shadow_offset_y", 1)
	_title.visible_ratio = 0.0
	add_child(_title)


func is_covered() -> bool:
	return _cover.modulate.a > 0.0


func cover(seconds: float) -> void:
	var t := create_tween()
	t.tween_property(_cover, "modulate:a", 1.0, seconds)
	await t.finished


func reveal(seconds: float) -> void:
	var t := create_tween()
	t.tween_property(_cover, "modulate:a", 0.0, seconds)
	await t.finished


## Writes the area name letter by letter on the black cover, holds, then clears it.
func write_title(text: String) -> void:
	_title.text = text
	_title.visible_ratio = 0.0
	_title.modulate.a = 1.0
	var t := create_tween()
	t.tween_property(_title, "visible_ratio", 1.0, TITLE_SECONDS * 0.6)
	t.tween_interval(TITLE_SECONDS * 0.4)
	t.tween_property(_title, "modulate:a", 0.0, 0.3)
	await t.finished
	_title.visible_ratio = 0.0
