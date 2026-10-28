extends SceneTree
## Lengthens the yard inside the cemetery entry's gate upwards by -TOP px (user 2026-10-28: after
## the gate the angel should come first and the chapel only a walk later). Everything already in
## the scene keeps its coordinates; the new strip above y 0 gets:
##   - Ground/Base tiles (the same two base tiles, random);
##   - Ground/Path: the two side paths carried straight up to the exits, which moved to the new top
##     (only cells that were empty are added, so the user's painting stays as it is);
##   - Props: more rows of graves like the user's, kept off the paths, the fountain and the view
##     up to the chapel, and off every prop already there;
##   - the fountain moved up into the middle of the longer yard (FOUNTAIN).
## Runs once: if Base already has tiles above y 0 nothing is changed.
##
##   Godot --headless --path . --script res://scripts/tools/extend_cemetery_entry_top.gd

const ROOM := "res://scenes/prototypes/cemetery_entry/cemetery_entry_greybox.tscn"
const ENTRY := preload("res://scripts/prototypes/cemetery_entry/cemetery_entry_greybox.gd")
const BLOCKS := "res://scenes/props/cemetery/"
const CELL := 32
const BASE := Vector2i(224, 128)
const NEW_ROWS := [92, 34, -24, -82] # grave rows (feet), 58 apart like the yard below
const PATH_X := 298 # the left side path's centre in the new strip; the right one is mirrored


func _init() -> void:
	var root: Node = load(ROOM).instantiate()
	var base: TileMapLayer = root.get_node("Ground/Base")
	for c in base.get_used_cells():
		if c.y < 0:
			print("the entry is already lengthened; nothing changed")
			root.free()
			quit()
			return
	var rng := RandomNumberGenerator.new()
	rng.seed = 6
	for y in range(floori(float(ENTRY.TOP) / BASE.y), 0):
		for x in ceili(float(ENTRY.SIZE.x) / BASE.x):
			base.set_cell(Vector2i(x, y), 0 if rng.randf() < 0.65 else 1, Vector2i.ZERO)

	var path: TileMapLayer = root.get_node("Ground/Path")
	var cells: Array[Vector2i] = []
	for y in range(floori((ENTRY.TOP + 92.0) / CELL), 4):
		for x in ceili(float(ENTRY.SIZE.x) / CELL):
			var cx := (x + 0.5) * CELL
			if (absf(cx - PATH_X) < 34 or absf(cx - (ENTRY.SIZE.x - PATH_X)) < 34) and path.get_cell_source_id(Vector2i(x, y)) == -1:
				cells.append(Vector2i(x, y))
	path.set_cells_terrain_connect(cells, 0, 0)

	var props: Node2D = root.get_node("Props")
	var fountain_moved := false
	for prop: Node2D in props.get_children():
		if prop.scene_file_path.ends_with("fountain_dry_01.tscn"):
			prop.position = ENTRY.FOUNTAIN - Vector2(0, prop.get("ground_gap"))
			fountain_moved = true
	var taken: Array[Vector2] = []
	for prop: Node2D in props.get_children():
		taken.append(prop.position + Vector2(0, prop.get("ground_gap")))
	var added := 0
	var row := 0
	for gy in NEW_ROWS:
		for x in range(36 + (row % 2) * 31, 940, 62):
			var p := Vector2(x + rng.randi_range(-8, 8), gy + rng.randi_range(-6, 6))
			var name: String = ENTRY.YARD_GRAVES[rng.randi() % ENTRY.YARD_GRAVES.size()]
			if rng.randf() < 0.14 or _keep_clear(p) or _crowded(p, taken):
				continue
			var block: Node2D = load(BLOCKS + name + ".tscn").instantiate()
			block.position = p - Vector2(0, block.get("ground_gap"))
			props.add_child(block, true)
			block.owner = root
			taken.append(p)
			added += 1
		row += 1

	var scene := PackedScene.new()
	scene.pack(root)
	ResourceSaver.save(scene, ROOM)
	root.free()
	print("entry lengthened by %d px: base + %d path cells + %d graves, fountain moved: %s" % [-ENTRY.TOP, cells.size(), added, fountain_moved])
	quit()


## The two paths up to the exits, the fountain, and the view from the gate to the chapel.
static func _keep_clear(p: Vector2) -> bool:
	if absf(p.x - PATH_X) < 46 or absf(p.x - (ENTRY.SIZE.x - PATH_X)) < 46:
		return true
	if absf(p.x - ENTRY.FOUNTAIN.x) < 110 and p.y > ENTRY.FOUNTAIN.y - 140:
		return true
	return absf(p.x - ENTRY.FOUNTAIN.x) < 96


static func _crowded(p: Vector2, taken: Array[Vector2]) -> bool:
	for q in taken:
		if absf(q.x - p.x) < 44 and absf(q.y - p.y) < 40:
			return true
	return false
