extends SceneTree
## Turns every prop in art/cemetery_v3/props/props_manifest.json into a placeable scene
## (scenes/props/cemetery/<name>.tscn, script CemeteryProp) with a first-guess collision.
##
## Run after importing new art:
##   Godot --headless --path . --import
##   Godot --headless --path . --script res://scripts/tools/bake_cemetery_props.gd
## Existing scenes are skipped, because their collision may have been adjusted by hand;
## pass `-- --force=<name>` to rebuild one of them.

const ART := "res://art/cemetery_v3/props/"
const OUT := "res://scenes/props/cemetery/"
const PROP_SCRIPT := "res://scripts/world/v3/cemetery_prop.gd"

## Wall pieces join end to end, so their strip spans the whole foot (no gaps at the joins).
const WALLS := ["low_wall_01", "low_wall_broken_01", "low_wall_rubble_broken_01",
		"low_wall_rubble_pillar_01", "low_wall_ashlar_01", "low_wall_ashlar_02", "iron_fence_01"]
## Lying boxes and pits: block their whole footprint.
const FOOTPRINT := ["open_grave_01", "grave_lid_01"]
## On the ground; walked over.
const FLAT := ["grave_slab_01", "iron_gate_leaf_fallen_01", "fallen_lamp_post_01"]
## Wide things whose bottom rows are narrower than what stands on the ground (the fountain's front
## corner): an ellipse inside this box, relative to the foot, measured from the pool's widest rows.
const POOLS := {"fountain_dry_01": Rect2(-92, -92, 186, 84)}
## Too small to block the way; the shape is there but switched off.
const WALK_OVER := ["rubble_pile_01", "grave_vase_01", "candles_01", "grave_lantern_01"]


func _init() -> void:
	var force := ""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--force="):
			force = arg.get_slice("=", 1)
	var manifest: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(ART + "props_manifest.json"))
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	var made := 0
	for prop_name: String in manifest.items:
		var path := OUT + prop_name + ".tscn"
		if FileAccess.file_exists(path) and force != prop_name:
			continue
		var err := ResourceSaver.save(_bake(prop_name), path)
		print("%s %s" % ["saved" if err == OK else "FAILED", path])
		made += 1
	print("bake_cemetery_props: %d scene(s) written" % made)
	quit()


func _bake(prop_name: String) -> PackedScene:
	var tex: Texture2D = load(ART + prop_name + ".png")
	var img := Image.load_from_file(ProjectSettings.globalize_path(ART + prop_name + ".png"))
	img.convert(Image.FORMAT_RGBA8)
	var w := img.get_width()
	var h := img.get_height()
	var gap := h - 1 - PixelArt.lowest_opaque_row(img)
	var root := Node2D.new()
	root.name = prop_name.to_pascal_case()
	root.set_script(load(PROP_SCRIPT))
	root.set("ground_gap", gap)
	root.set("flat", prop_name in FLAT)
	if FileAccess.file_exists(ART + prop_name + "_base.png"):
		var base_tex: Texture2D = load(ART + prop_name + "_base.png")
		var base := _sprite("Base", base_tex, gap)
		root.add_child(base)
		base.owner = root
	var sprite := _sprite("Sprite", tex, gap)
	root.add_child(sprite)
	sprite.owner = root
	var body := StaticBody2D.new()
	body.name = "Body"
	root.add_child(body)
	body.owner = root
	if prop_name in FOOTPRINT:
		var poly := CollisionPolygon2D.new()
		poly.name = "Shape"
		poly.polygon = _footprint(img, gap)
		body.add_child(poly)
		poly.owner = root
	elif prop_name in POOLS:
		var box: Rect2 = POOLS[prop_name]
		var poly := CollisionPolygon2D.new()
		poly.name = "Shape"
		var pts := PackedVector2Array()
		for i in 12:
			var a := TAU * i / 12.0
			pts.append((box.get_center() + Vector2(cos(a), sin(a)) * box.size / 2.0).round())
		poly.polygon = pts
		body.add_child(poly)
		poly.owner = root
	else:
		var foot := _foot_rect(img, gap, 1.0 if prop_name in WALLS else 0.85, 12 if prop_name in WALLS else 10)
		var shape := CollisionShape2D.new()
		shape.name = "Shape"
		var rect := RectangleShape2D.new()
		rect.size = foot.size
		shape.shape = rect
		shape.position = foot.get_center()
		shape.disabled = prop_name in WALK_OVER or prop_name in FLAT
		body.add_child(shape)
		shape.owner = root
	var scene := PackedScene.new()
	scene.pack(root)
	root.free()
	return scene


## Top-left anchored so every pixel lands on a whole native pixel; the origin is the foot.
func _sprite(sprite_name: String, tex: Texture2D, gap: int) -> Sprite2D:
	var s := Sprite2D.new()
	s.name = sprite_name
	s.texture = tex
	s.centered = false
	s.offset = Vector2(-tex.get_width() / 2, -tex.get_height() + gap)
	return s


## A strip across the bottom of the upright part, relative to the foot point.
func _foot_rect(img: Image, gap: int, width_share: float, depth: int) -> Rect2:
	var bottom := img.get_height() - 1 - gap
	var left := img.get_width()
	var right := -1
	for y in range(maxi(0, bottom - 7), bottom + 1):
		for x in img.get_width():
			if img.get_pixel(x, y).a > 0.5:
				left = mini(left, x)
				right = maxi(right, x)
	var w := roundf(maxf(8.0, (right - left + 1) * width_share))
	var cx := roundf((left + right + 1) / 2.0 - img.get_width() / 2.0)
	return Rect2(cx - w / 2.0, 1 - depth, w, depth)


## The outline of everything the prop covers, cut down to a handful of corners for editing.
func _footprint(img: Image, gap: int) -> PackedVector2Array:
	var pts := PackedVector2Array()
	var origin := Vector2(img.get_width() / 2, img.get_height() - gap)
	for y in img.get_height():
		for x in img.get_width():
			if img.get_pixel(x, y).a > 0.5:
				pts.append(Vector2(x, y) - origin)
				pts.append(Vector2(x + 1, y + 1) - origin)
	var hull := Geometry2D.convex_hull(pts)
	hull.remove_at(hull.size() - 1) # convex_hull repeats the first point at the end
	while hull.size() > 6:
		var best := 0
		var least := INF
		for i in hull.size():
			var a := hull[i - 1]
			var b := hull[i]
			var c := hull[(i + 1) % hull.size()]
			var area := absf((b - a).cross(c - a))
			if area < least:
				least = area
				best = i
		if least > 300.0:
			break
		hull.remove_at(best)
	return hull
