extends Node2D
## An exit at the edge of a room (Decision Log D-023: the route is chosen by walking out of a
## chosen exit). Above it floats a small language-layer glyph telling what lies beyond.
## The glyph lives on the language CanvasLayer, so world tint and fog never touch it:
## same pixel size as the world, the one saturated cyan, precise geometry, steady motion.

signal taken(exit: Node2D)

const CYAN := Color(0.42, 0.86, 0.95)
# 15x15 glyphs from the art group (art/ui/exit_glyphs_v3/, approved 2026-10-28), one per node
# type. All stand on the same threshold line, which tells "a place" apart from the word-family
# marks in the combat bar. "unknown" is how a node shows while the player has not understood it.
const GLYPH_DIR := "res://art/ui/exit_glyphs_v3/exit_%s.png"
const KINDS := ["combat", "elite", "event", "mystery", "relic", "rest", "final", "area", "unknown"]
const ALIASES := {"encounter": "combat", "boss": "final"} # rule-layer node names
static var GLYPHS := {}

var zone := Rect2() # world rect the player's feet must enter
var kind := "combat"
var target := "" # room id or area id this exit leads to
var side := "right" # edge of the room, so the next room is entered from the opposite side
var enabled := false:
	set(value):
		enabled = value
		if is_instance_valid(glyph):
			glyph.visible = value
var understood := true # false shows the "unknown" glyph (not wired to the rules yet)
var glyph: Node2D
var _time := 0.0


static func glyph_rows(node_kind: String) -> Array:
	if GLYPHS.is_empty():
		for k in KINDS:
			var path := ProjectSettings.globalize_path(GLYPH_DIR % k)
			if not FileAccess.file_exists(path):
				continue
			var img := Image.load_from_file(path)
			var rows: Array[String] = []
			for y in img.get_height():
				var row := ""
				for x in img.get_width():
					row += "X" if img.get_pixel(x, y).a > 0.5 else "."
				rows.append(row)
			GLYPHS[k] = rows
	var key: String = ALIASES.get(node_kind, node_kind)
	return GLYPHS.get(key, GLYPHS.get("unknown", []))


func setup(data: Dictionary, language_layer: CanvasLayer) -> void:
	zone = data.zone
	kind = data.kind
	target = data.target
	side = data.side
	glyph = Node2D.new()
	glyph.position = (data.get("glyph_at", zone.get_center() + Vector2(0, -60)) as Vector2).round()
	glyph.draw.connect(_draw_glyph)
	language_layer.add_child(glyph)
	glyph.visible = enabled


func check(player: Node2D) -> void:
	if enabled and zone.has_point(player.position):
		taken.emit(self)


func _exit_tree() -> void:
	if is_instance_valid(glyph):
		glyph.queue_free()


func _process(delta: float) -> void:
	_time += delta
	if is_instance_valid(glyph) and glyph.visible:
		glyph.queue_redraw()


func _draw_glyph() -> void:
	var rows: Array = glyph_rows(kind if understood else "unknown")
	# Steady breathing glow, whole pixels only: a 1 px bob every second.
	var bob := Vector2(0, -1 if fmod(_time, 2.0) < 1.0 else 0)
	var glow := 0.22 + 0.08 * sin(_time * 1.6)
	var origin := Vector2(-7, -7) + bob
	for y in rows.size():
		for x in rows[y].length():
			if rows[y][x] == "X":
				for o in [Vector2(-1, 0), Vector2(1, 0), Vector2(0, -1), Vector2(0, 1)]:
					glyph.draw_rect(Rect2(origin + Vector2(x, y) + o, Vector2.ONE), Color(CYAN, glow))
	for y in rows.size():
		for x in rows[y].length():
			if rows[y][x] == "X":
				glyph.draw_rect(Rect2(origin + Vector2(x, y), Vector2.ONE), CYAN)
