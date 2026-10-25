class_name CemeteryRoom
extends Node2D
## One room of the v3 pixel world: a 960x540 ground plate, flat ground bases, tall props with
## collision and see-through fading, room bounds, and the world tint. Built from a layout
## dictionary so rooms are data (see broken_graveyard_v3.gd ROOMS).
##
## Layer order (Art Bible v3): ground plate -> bases / dead grass -> Y-sorted actors and props.
## Rules validated in graveyard_room: the whole prop (upright + base) fades together; props with
## a base get no procedural shadow; the Y-sort point is where the upright part meets the ground.

const ART := "res://art/cemetery_pixel_v1/"
const NATIVE := Vector2i(960, 540)
const SHADOW_COLOR := Color(0.03, 0.03, 0.05, 0.45)
const FADE_ALPHA := 0.45

var layout: Dictionary
var sorted: Node2D # Y-sorted: props, actors and world loot; every origin is a ground contact point
var player: Node2D
var _props: Array[Node2D] = []
var _rng := RandomNumberGenerator.new()


func _init(room_layout: Dictionary) -> void:
	layout = room_layout
	name = "Room_" + str(layout.id)
	_rng.seed = int(layout.get("seed", 1))
	var ground := Sprite2D.new()
	ground.centered = false
	ground.texture = PixelArt.texture(ART + str(layout.get("plate", "plates/ground_plate_960x540")) + ".png")
	add_child(ground)
	var bases := Node2D.new()
	add_child(bases)
	for i in int(layout.get("dead_grass", 14)):
		var s := Sprite2D.new()
		s.texture = PixelArt.texture(ART + "decals/dead_grass_%02d.png" % _rng.randi_range(1, 4))
		s.offset = Vector2(0, -s.texture.get_height() / 2)
		s.position = Vector2(_rng.randi_range(20, NATIVE.x - 20), _rng.randi_range(30, NATIVE.y - 6))
		bases.add_child(s)
	sorted = Node2D.new()
	sorted.name = "Sorted"
	sorted.y_sort_enabled = true
	add_child(sorted)
	for p in layout.get("props", []):
		var base: Sprite2D = null
		if FileAccess.file_exists(ART + "props/" + p[0] + "_base.png"):
			base = Sprite2D.new()
			base.texture = PixelArt.texture(ART + "props/" + p[0] + "_base.png")
			base.offset = Vector2(0, -base.texture.get_height() / 2)
			base.position = p[1]
			bases.add_child(base)
		var prop := _make_prop(p[0], p[2], p.size() > 3 and p[3], base)
		prop.position += p[1]
		sorted.add_child(prop)
		_props.append(prop)
	_add_bounds()
	var tint := CanvasModulate.new()
	tint.color = layout.get("tint", Color(0.8, 0.84, 0.92))
	add_child(tint)


func _process(delta: float) -> void:
	if not is_instance_valid(player):
		return
	# Behind a tall prop, the whole prop turns see-through as one material.
	var body := player.position + Vector2(0, -44)
	for prop in _props:
		var sprite: Sprite2D = prop.get_node("Sprite")
		var rect := Rect2(prop.position + sprite.offset - sprite.texture.get_size() / 2.0, sprite.texture.get_size())
		var behind := player.position.y < prop.position.y and rect.grow(-4).has_point(body)
		var a := move_toward(sprite.modulate.a, FADE_ALPHA if behind else 1.0, delta * 4.0)
		sprite.modulate.a = a
		var base: Sprite2D = prop.get_meta("base")
		if base:
			base.modulate.a = a


func _make_prop(file: String, collision: Rect2, ellipse: bool, base: Sprite2D) -> Node2D:
	var root := Node2D.new()
	root.set_meta("base", base)
	var tex := PixelArt.texture(ART + "props/" + file + ".png")
	# Lift the node to where the upright part really meets the ground (Y-sort point).
	var gap := tex.get_height() - 1 - PixelArt.lowest_opaque_row(tex.get_image())
	if base:
		tex = PixelArt.without_overlap(tex, base.texture)
	root.position = Vector2(0, -gap)
	if not base:
		root.add_child(PixelArt.footprint_shadow(tex, SHADOW_COLOR))
	var sprite := Sprite2D.new()
	sprite.name = "Sprite"
	sprite.texture = tex
	sprite.offset = Vector2(0, -tex.get_height() / 2 + gap)
	root.add_child(sprite)
	var body := StaticBody2D.new()
	body.position = Vector2(0, gap) # collision data is relative to the PNG origin
	if ellipse:
		var poly := CollisionPolygon2D.new()
		var pts := PackedVector2Array()
		var c := collision.get_center()
		for k in 20:
			var t := TAU * k / 20.0
			pts.append(c + Vector2(cos(t), sin(t)) * collision.size / 2.0)
		poly.polygon = pts
		body.add_child(poly)
	else:
		var shape := CollisionShape2D.new()
		var rect := RectangleShape2D.new()
		rect.size = collision.size
		shape.shape = rect
		shape.position = collision.get_center()
		body.add_child(shape)
	root.add_child(body)
	return root


func _add_bounds() -> void:
	var walls := StaticBody2D.new()
	walls.name = "Bounds"
	for r in [Rect2(-20, -20, NATIVE.x + 40, 20), Rect2(-20, NATIVE.y, NATIVE.x + 40, 20),
			Rect2(-20, 0, 20, NATIVE.y), Rect2(NATIVE.x, 0, 20, NATIVE.y)]:
		var shape := CollisionShape2D.new()
		var rect := RectangleShape2D.new()
		rect.size = r.size
		shape.shape = rect
		shape.position = r.position + r.size / 2.0
		walls.add_child(shape)
	add_child(walls)
