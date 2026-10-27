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
const PROP_SCENES := "res://scenes/props/cemetery/" # building blocks (D-034) win over bare PNGs

var layout: Dictionary
var size := NATIVE # most rooms are one screen; the Cemetery Entry is two screens tall (D-038)
var prop_dir: String # where this room's props live; layouts may point at a newer prop set
var sorted: Node2D # Y-sorted: props, actors and world loot; every origin is a ground contact point
var player: Node2D
var _props: Array[Node2D] = []
var _rng := RandomNumberGenerator.new()


func _init(room_layout: Dictionary) -> void:
	layout = room_layout
	name = "Room_" + str(layout.id)
	_rng.seed = int(layout.get("seed", 1))
	prop_dir = str(layout.get("prop_dir", ART + "props/"))
	size = layout.get("size", NATIVE)
	# plate_file: any PNG path (res:// or on disk), for trying ground candidates before they land;
	# "" means the scene draws its own ground (tile layers) underneath the room.
	var plate_file := str(layout.get("plate_file", ART + str(layout.get("plate", "plates/ground_plate_960x540")) + ".png"))
	if plate_file != "":
		var plate := PixelArt.texture(plate_file)
		for y in range(0, size.y, plate.get_height()): # a taller room stacks the plate until real ground exists
			var ground := Sprite2D.new()
			ground.centered = false
			ground.texture = plate
			ground.position.y = y
			ground.z_index = -10
			add_child(ground)
	var bases := Node2D.new()
	bases.z_index = CemeteryProp.BASE_Z
	add_child(bases)
	for i in int(layout.get("dead_grass", 14)):
		var s := Sprite2D.new()
		s.texture = PixelArt.texture(ART + "decals/dead_grass_%02d.png" % _rng.randi_range(1, 4))
		s.offset = Vector2(0, -s.texture.get_height() / 2)
		s.position = Vector2(_rng.randi_range(20, size.x - 20), _rng.randi_range(int(layout.get("grass_top", 30)), size.y - 6)) # grass_top: keep it off a backdrop strip
		bases.add_child(s)
	sorted = Node2D.new()
	sorted.name = "Sorted"
	sorted.y_sort_enabled = true
	add_child(sorted)
	for p in layout.get("props", []):
		if ResourceLoader.exists(PROP_SCENES + str(p[0]) + ".tscn"):
			# The block brings its own base, collision and fading; the layout point is the PNG origin.
			var block: CemeteryProp = load(PROP_SCENES + str(p[0]) + ".tscn").instantiate()
			block.position = p[1] - Vector2(0, block.ground_gap)
			sorted.add_child(block)
			continue
		var base: Sprite2D = null
		if FileAccess.file_exists(prop_dir + p[0] + "_base.png"):
			base = Sprite2D.new()
			base.texture = PixelArt.texture(prop_dir + p[0] + "_base.png")
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
		var base: Sprite2D = prop.get_meta("base") if prop.has_meta("base") else null
		if base:
			base.modulate.a = a


## collision: rect relative to the PNG origin, null for a strip along the upright part's foot,
## or false for none (small props the player walks over).
func _make_prop(file: String, collision: Variant, ellipse: bool, base: Sprite2D) -> Node2D:
	var root := Node2D.new()
	if base:
		root.set_meta("base", base) # setting null would try to remove a missing key
	var tex := PixelArt.texture(prop_dir + file + ".png")
	# Lift the node to where the upright part really meets the ground (Y-sort point).
	var gap := tex.get_height() - 1 - PixelArt.lowest_opaque_row(tex.get_image())
	if collision == null:
		collision = _foot_rect(tex.get_image(), gap)
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
	if collision is bool:
		return root
	var body := StaticBody2D.new()
	body.position = Vector2(0, gap) # collision data is relative to the PNG origin
	if ellipse:
		var poly := CollisionPolygon2D.new()
		var pts := PackedVector2Array()
		var c: Vector2 = collision.get_center()
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


## A 10 px strip across the bottom of the upright part, 85% of its width.
func _foot_rect(img: Image, gap: int) -> Rect2:
	var bottom := img.get_height() - 1 - gap
	var left := img.get_width()
	var right := -1
	for y in range(maxi(0, bottom - 7), bottom + 1):
		for x in img.get_width():
			if img.get_pixel(x, y).a > 0.5:
				left = mini(left, x)
				right = maxi(right, x)
	var w := maxf(8.0, (right - left + 1) * 0.85)
	var cx := (left + right + 1) / 2.0 - img.get_width() / 2.0
	return Rect2(cx - w / 2.0, -gap - 10, w, 10)


func _add_bounds() -> void:
	var walls := StaticBody2D.new()
	walls.name = "Bounds"
	for r in [Rect2(-20, -20, size.x + 40, 20), Rect2(-20, size.y, size.x + 40, 20),
			Rect2(-20, 0, 20, size.y), Rect2(size.x, 0, 20, size.y)]:
		var shape := CollisionShape2D.new()
		var rect := RectangleShape2D.new()
		rect.size = r.size
		shape.shape = rect
		shape.position = r.position + r.size / 2.0
		walls.add_child(shape)
	add_child(walls)
