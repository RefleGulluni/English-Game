extends Control
## Language layer for the pixel validation room.
##
## Precise geometry with a soft glow plus the English word. pixel_room.gd draws it either
## anti-aliased in the main viewport or, with antialias off, into a low-resolution viewport
## at the world's pixel size (the style chosen on 2026-10-22).
## "The world is pixel and broken. Language is precise and luminous."

const LINE := Color(0.62, 0.9, 1.0, 0.95)
const GLOW := Color(0.35, 0.75, 1.0, 0.12)

var word := "OBSERVE"
var anchor := Vector2.ZERO # screen position of the sigil centre, set every frame
var radius := 40.0
var antialias := true # false when drawn into a low-resolution pixel viewport
var _t := 0.0


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_preset(Control.PRESET_FULL_RECT)


func _process(delta: float) -> void:
	_t += delta
	queue_redraw()


func _draw() -> void:
	var r := radius * (1.0 + 0.02 * sin(_t * 1.6))
	var spin := _t * 0.25
	for i in 4: # soft glow: wide, faint strokes under the precise line
		draw_arc(anchor, r, 0.0, TAU, 128, GLOW, (10.0 - i * 2.0) * _w(), antialias)
	draw_arc(anchor, r, 0.0, TAU, 128, LINE, 1.6 * _w(), antialias)
	draw_arc(anchor, r * 0.86, 0.0, TAU, 128, Color(LINE, 0.45), 1.0 * _w(), antialias)

	var tri := PackedVector2Array()
	for k in 4:
		var a := spin - PI / 2.0 + TAU * (k % 3) / 3.0
		tri.append(anchor + Vector2(cos(a), sin(a)) * r * 0.86)
	draw_polyline(tri, LINE, 1.4 * _w(), antialias)
	for k in 3:
		_diamond(tri[k], r * 0.06)

	draw_arc(anchor, r * 0.28, 0.0, TAU, 64, LINE, 1.4 * _w(), antialias)
	draw_arc(anchor, r * 0.12, 0.0, TAU, 48, Color(LINE, 0.7), 1.0 * _w(), antialias)
	draw_circle(anchor, r * 0.035, LINE)

	var font := ThemeDB.fallback_font
	var size := int(clampf(r * 0.38, 12.0, 28.0))
	var text_w := font.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x
	draw_string(font, anchor + Vector2(-text_w / 2.0, r + size * 1.4), word, HORIZONTAL_ALIGNMENT_LEFT, -1, size, LINE)


# Pixel modes draw at low resolution: thin lines would vanish, so keep them at least one pixel.
func _w() -> float:
	return 1.0 if antialias else 0.7


func _diamond(c: Vector2, s: float) -> void:
	draw_colored_polygon(PackedVector2Array([c + Vector2(0, -s), c + Vector2(s, 0), c + Vector2(0, s), c + Vector2(-s, 0)]), LINE)
