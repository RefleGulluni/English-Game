extends Node2D
## An exit at the edge of a room (Decision Log D-023: the route is chosen by walking out of a
## chosen exit). Above it floats a small language-layer glyph telling what lies beyond.
## The glyph lives on the language CanvasLayer, so world tint and fog never touch it:
## same pixel size as the world, the one saturated cyan, precise geometry, steady motion.

signal taken(exit: Node2D)

const CYAN := Color(0.42, 0.86, 0.95)
# 11x11 glyphs, one per node type. Placeholders until the exit symbols are designed (KB: Scene
# Structure §4, open question).
const GLYPHS := {
	"combat": ["X.........X", ".X.......X.", "..X.....X..", "...X...X...", "....X.X....", ".....X.....",
		"....X.X....", "...X...X...", "..X.....X..", ".X.......X.", "X.........X"],
	"event": ["...XXXXX...", "..X.....X..", ".X.......X.", ".........X.", "........X..", "......XX...",
		".....X.....", ".....X.....", "...........", ".....X.....", ".....X....."],
	"rest": [".....X.....", "....X.X....", "....X.X....", "...X...X...", "...X...X...", "..X..X..X..",
		"..X.X.X.X..", ".X...X...X.", ".X.......X.", "X.........X", "XXXXXXXXXXX"],
	"elite": ["X....X....X", "XX..XXX..XX", "X.X.X.X.X.X", "X..X...X..X", "X.........X", "XXXXXXXXXXX",
		"...........", "XXXXXXXXXXX", ".X.......X.", "..X.....X..", "...XXXXX..."],
	"area": ["XXXXXXXXXXX", "X.........X", "X.........X", "X....X....X", "X.....X...X", "XXXXXXXX..X",
		"X.....X...X", "X....X....X", "X.........X", "X.........X", "XXXXXXXXXXX"],
}

var zone := Rect2() # world rect the player's feet must enter
var kind := "combat"
var target := "" # room id or area id this exit leads to
var side := "right" # edge of the room, so the next room is entered from the opposite side
var enabled := false:
	set(value):
		enabled = value
		if is_instance_valid(glyph):
			glyph.visible = value
var glyph: Node2D
var _time := 0.0


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
	var rows: Array = GLYPHS.get(kind, GLYPHS.combat)
	# Steady breathing glow, whole pixels only: a 1 px bob every second.
	var bob := Vector2(0, -1 if fmod(_time, 2.0) < 1.0 else 0)
	var glow := 0.22 + 0.08 * sin(_time * 1.6)
	var origin := Vector2(-5, -5) + bob
	for y in rows.size():
		for x in rows[y].length():
			if rows[y][x] == "X":
				for o in [Vector2(-1, 0), Vector2(1, 0), Vector2(0, -1), Vector2(0, 1)]:
					glyph.draw_rect(Rect2(origin + Vector2(x, y) + o, Vector2.ONE), Color(CYAN, glow))
	for y in rows.size():
		for x in rows[y].length():
			if rows[y][x] == "X":
				glyph.draw_rect(Rect2(origin + Vector2(x, y), Vector2.ONE), CYAN)
