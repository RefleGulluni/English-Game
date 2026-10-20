extends SceneTree
## Deterministic editor build step, never called by gameplay. Saves real editable cells/nodes.
const OUTPUT := "res://scenes/world/cemetery_modular_environment.tscn"
const TILESET := "res://art/cemetery_kit_v1/terrain/cemetery_tileset.tres"
const PROP := preload("res://scripts/world/cemetery_prop.gd")

func _initialize() -> void:
	build.call_deferred()

func build() -> void:
	if not ResourceLoader.exists(TILESET):
		push_error("Cemetery Kit TileSet has not arrived; leave source scene untouched.")
		quit(1)
		return
	var map := load(OUTPUT).instantiate() as Node2D
	root.add_child(map)
	var ground := map.get_node("GroundTileMap") as TileMapLayer
	ground.tile_set = load(TILESET)
	ground.scale = Vector2.ONE * (128.0 / ground.tile_set.tile_size.x)
	ground.position = Vector2(64, 64)
	ground.clear()
	var edges := map.get_node("GroundBlendLayer") as TileMapLayer
	edges.tile_set = ground.tile_set
	edges.scale = ground.scale
	edges.position = ground.position
	edges.clear()
	ground.modulate = Color(0.78, 0.81, 0.83)
	edges.modulate = ground.modulate
	var layout: Dictionary = {}
	# Source 0 is opaque mud. Source 1 supplies hand-painted terrain with alpha edges.
	# Keep phase variant 0 coherent: never butt-join unrelated offset texture variants.
	for y in range(9):
		for x in range(15):
			var material_index := 2
			if y in [3, 4]: material_index = 1 if x in [6, 7, 8] else 0
			elif y in [2, 5] and x > 3: material_index = 3
			if x in [7, 8, 9] and y == 4: material_index = 4
			if x in [5, 6, 10, 11] and y == 5: material_index = 5
			var cell := Vector2i(x, y)
			layout[cell] = material_index
			ground.set_cell(cell, 0, Vector2i(2, 0))
	var edge_rows := {0: 0, 1: 1, 3: 2, 4: 3, 5: 4}
	var neighbors := [Vector2i.UP, Vector2i.RIGHT, Vector2i.DOWN, Vector2i.LEFT]
	for cell in layout:
		var material_index: int = layout[cell]
		if material_index == 2: continue
		var mask := 0
		for direction in range(4):
			if int(layout.get(cell + neighbors[direction], 2)) != material_index: mask |= 1 << direction
		edges.set_cell(cell, 1, Vector2i(mask, edge_rows[material_index]))
	for layer_name in ["StructureLayer", "PropLayer", "ForegroundLayer"]:
		for child in map.get_node(layer_name).get_children(): child.free()
	# All visible objects are independently replaceable Kit scenes, never baked into terrain.
	for i in range(7):
		for row in [370, 680]:
			var variant := (i * 2 + (1 if row == 680 else 0)) % 8 + 1
			place_kit(map, "PropLayer", "Headstone_%d_%d" % [i, row], "props", "grave_%02d" % variant, Vector2(631 + i * 170, row))
	for edge_y in [90, 1100]:
		var x := 0.0
		var index := 0
		while x < 1900:
			var wall := place_kit(map, "StructureLayer", "Wall_%d_%d" % [edge_y, index], "structures", "wall_straight", Vector2.ZERO)
			var dimensions: Vector2 = wall.visual.get_meta("display_size")
			wall.position = Vector2(x + dimensions.x * 0.5, edge_y)
			x += dimensions.x - 3.0
			index += 1
	var footprints := StaticBody2D.new()
	footprints.name = "StructureFootprints"
	footprints.collision_mask = 2
	map.get_node("StructureLayer").add_child(footprints)
	footprints.owner = map
	for north in [true, false]:
		var point := Vector2(480, 440 if north else 560)
		var index := 0
		while point.y > -70 if north else point.y < 1170:
			var fence := place_kit(map, "StructureLayer", "Fence_%s_%d" % ["N" if north else "S", index], "structures", "fence_y", Vector2.ZERO)
			var a: Vector2 = fence.visual.get_node("SocketA").position
			var b: Vector2 = fence.visual.get_node("SocketB").position
			fence.position = point - (a if north else b)
			var next: Vector2 = fence.position + (b if north else a)
			var segment := SegmentShape2D.new()
			segment.a = point
			segment.b = next
			var shape := CollisionShape2D.new()
			shape.name = "Fence_%s_%d" % ["N" if north else "S", index]
			shape.shape = segment
			footprints.add_child(shape)
			shape.owner = map
			point = next
			index += 1
			assert(index < 40, "Fence sockets must advance along world Y")
	for y in [440, 560]: place_kit(map, "StructureLayer", "GatePost%d" % y, "structures", "fence_post", Vector2(480, y))
	# An actual traversable foreground rail overlaps the approach path. No hidden blocker.
	place_kit(map, "ForegroundLayer", "ApproachRail", "foreground", "fence_foreground", Vector2(700, 535), true)
	place_kit(map, "ForegroundLayer", "OverhangingBranch", "foreground", "branch_left", Vector2(800, 510), true)
	place_kit(map, "PropLayer", "TreeWest", "props", "tree_a", Vector2(750, 820))
	place_kit(map, "PropLayer", "TreeEast", "props", "tree_b", Vector2(1510, 230))
	place_kit(map, "StructureLayer", "BrokenLowWall", "structures", "wall_low", Vector2(1360, 910))
	place_kit(map, "StructureLayer", "CollapsedWall", "structures", "wall_collapsed", Vector2(1600, 940))
	for item in [["stone_chips", Vector2(1230, 790)], ["bone_cluster", Vector2(980, 810)], ["long_bones", Vector2(1170, 780)], ["funeral_cloth", Vector2(1640, 840)], ["dead_weeds", Vector2(600, 850)]]:
		place_kit(map, "PropLayer", str(item[0]).to_pascal_case(), "props", item[0], item[1])
	for item in [[Vector2(750, 820), Vector2(28, 18)], [Vector2(1510, 230), Vector2(30, 20)], [Vector2(1360, 910), Vector2(125, 20)], [Vector2(1600, 940), Vector2(110, 20)]]:
		var shape := CollisionShape2D.new()
		var footprint := RectangleShape2D.new()
		footprint.size = item[1]
		shape.shape = footprint
		shape.position = item[0]
		footprints.add_child(shape)
		shape.owner = map
	var packed := PackedScene.new()
	packed.pack(map)
	var error := ResourceSaver.save(packed, OUTPUT)
	print("MODULAR_MAP_BUILD: ", error_string(error), " · ", ground.get_used_cells().size(), " editable cells")
	map.queue_free()
	quit(0 if error == OK else 1)

func place_kit(map: Node, layer: String, label: String, folder: String, module: String, at: Vector2, front := false) -> Node2D:
	var object := Node2D.new()
	object.name = label
	object.set_script(PROP)
	object.visual_scene = load("res://art/cemetery_kit_v1/%s/%s.tscn" % [folder, module])
	assert(object.visual_scene != null, "Cemetery module must be approved and imported before rebuilding: " + module)
	object.foreground = front
	object.position = at
	object.set_meta("kit_module", module)
	map.get_node(layer).add_child(object)
	object.owner = map
	return object
