extends SceneTree
## Gives the cemetery entry greybox (scenes/prototypes/cemetery_entry/) the paintable ground of
## docs/GROUND_TERRAIN_METHOD.md: Ground/Base (the two big base tiles over the whole 960×1350
## room), Ground/Grass, Ground/Path, Ground/Decals, plus Reference, a see-through picture of the
## room's props that only shows in the editor, so the user can see where the gate and graves are
## while painting.
##
## The path starts out painted along the greybox's old colour-block road (the user's sketch), so
## the user adjusts it rather than starting from nothing. Once the scene has a Ground it is
## the user's work: later runs only add the terrain layers it lacks (old paving), never repaint.
##
##   Godot --path . res://scenes/prototypes/cemetery_entry/cemetery_entry_greybox.tscn -- --reference=<abs>/art/cemetery_v3/ground/rooms/cemetery_entry_reference.png
##   Godot --headless --path . --import
##   Godot --headless --path . --script res://scripts/tools/build_cemetery_entry_ground.gd

const ROOM := "res://scenes/prototypes/cemetery_entry/cemetery_entry_greybox.tscn"
const ENTRY := preload("res://scripts/prototypes/cemetery_entry/cemetery_entry_greybox.gd")
const GROUND := "res://art/cemetery_v3/ground/"
const MASKS := GROUND + "transitions/masks/"
const REFERENCE := GROUND + "rooms/cemetery_entry_reference.png"
const DECALS := "res://scenes/props/cemetery/decals/"
const PATH_SHADER := "res://scripts/world/v3/ground_path.gdshader"
const CELL := 32
const TERRAINS := [
	{"layer": "Grass", "tileset": "ground_grass_tileset.tres", "texture": GROUND + "transitions/grass_texture_01.png"},
	{"layer": "Path", "tileset": "ground_path_tileset.tres", "texture": GROUND + "transitions/path_texture_01.png"},
	{"layer": "Paving", "tileset": "ground_paving_tileset.tres", "texture": GROUND + "transitions/paving_texture_01.png"},
]
## The old paving inside the gate (D-059): the avenue and a square round the fountain.
const PAVED_SQUARE := Rect2(360, 236, 240, 136)
## Grass to start with (cell rectangles): the verges outside the gate and the corners by the fence.
const SAMPLE_GRASS := [Rect2i(1, 20, 7, 4), Rect2i(22, 23, 7, 5), Rect2i(2, 33, 6, 5), Rect2i(23, 37, 6, 4),
	Rect2i(0, 14, 5, 2), Rect2i(25, 14, 5, 2)]
## Decals where the greybox had its colour-block puddles, plus a few leaves under the trees.
const SAMPLE_DECALS := [["decal_puddle_02", Vector2(392, 605)], ["decal_puddle_01", Vector2(568, 712)],
	["decal_puddle_03", Vector2(380, 970)], ["decal_wet_mud_02", Vector2(560, 1090)],
	["decal_leaves_02", Vector2(318, 770)], ["decal_leaves_01", Vector2(720, 1090)],
	["decal_bone_bits_01", Vector2(196, 1150)], ["decal_roots_01", Vector2(300, 1296)]]


func _init() -> void:
	var root: Node = load(ROOM).instantiate()
	if root.has_node("Ground"):
		_add_missing_layers(root)
		root.free()
		quit()
		return
	var ground := Node2D.new()
	ground.name = "Ground"
	ground.z_index = -10
	root.add_child(ground)
	ground.owner = root

	var base := TileMapLayer.new()
	base.name = "Base"
	base.tile_set = load(GROUND + "ground_base_tileset.tres")
	ground.add_child(base)
	base.owner = root
	var rng := RandomNumberGenerator.new()
	rng.seed = 5
	for y in ceili(ENTRY.SIZE.y / 128.0):
		for x in ceili(ENTRY.SIZE.x / 224.0):
			base.set_cell(Vector2i(x, y), 0 if rng.randf() < 0.65 else 1, Vector2i.ZERO)

	for t in TERRAINS:
		ground.add_child(_terrain_layer(t))
		ground.get_node(NodePath(t.layer)).owner = root

	var grass: Array[Vector2i] = []
	for r in SAMPLE_GRASS:
		for y in range(r.position.y, r.end.y):
			for x in range(r.position.x, r.end.x):
				grass.append(Vector2i(x, y))
	(ground.get_node("Grass") as TileMapLayer).set_cells_terrain_connect(grass, 0, 0)
	(ground.get_node("Path") as TileMapLayer).set_cells_terrain_connect(_road_cells(), 0, 0)
	(ground.get_node("Paving") as TileMapLayer).set_cells_terrain_connect(_paved_cells(), 0, 0)

	var decals := Node2D.new()
	decals.name = "Decals"
	ground.add_child(decals)
	decals.owner = root
	for d in SAMPLE_DECALS:
		var decal: Node2D = load(DECALS + d[0] + ".tscn").instantiate()
		decal.position = d[1]
		decals.add_child(decal, true)
		decal.owner = root

	if ResourceLoader.exists(REFERENCE):
		var reference := Sprite2D.new()
		reference.name = "Reference"
		reference.texture = load(REFERENCE)
		reference.centered = false
		reference.modulate = Color(1, 1, 1, 0.5)
		root.add_child(reference)
		reference.owner = root

	var scene := PackedScene.new()
	scene.pack(root)
	ResourceSaver.save(scene, ROOM)
	root.free()
	print("entry ground saved: ", ROOM)
	quit()


## A Ground the user has painted is kept as it is; only terrain layers added to the method since
## (old paving) are slotted in at their place, pre-painted where the sketch has them.
func _add_missing_layers(root: Node) -> void:
	var ground: Node2D = root.get_node("Ground")
	var added := false
	for i in TERRAINS.size():
		var t: Dictionary = TERRAINS[i]
		if ground.has_node(NodePath(t.layer)):
			continue
		var layer := _terrain_layer(t)
		ground.add_child(layer)
		layer.owner = root
		ground.move_child(layer, 1 + i) # after Base
		if t.layer == "Paving":
			layer.set_cells_terrain_connect(_paved_cells(), 0, 0)
		added = true
		print("added layer ", t.layer)
	if not added:
		print("the entry already has every ground layer (the user's painting); nothing changed")
		return
	var scene := PackedScene.new()
	scene.pack(root)
	ResourceSaver.save(scene, ROOM)
	print("entry ground saved: ", ROOM)


func _terrain_layer(t: Dictionary) -> TileMapLayer:
	var layer := TileMapLayer.new()
	layer.name = t.layer
	layer.tile_set = load(MASKS + t.tileset)
	var mat := ShaderMaterial.new()
	mat.shader = load(PATH_SHADER)
	mat.set_shader_parameter("path_texture", load(t.texture))
	layer.material = mat
	return layer


## The avenue from the gate to the fountain, and the square round the fountain.
func _paved_cells() -> Array[Vector2i]:
	var avenue := PackedVector2Array(ENTRY.AVENUE)
	var cells: Array[Vector2i] = []
	for y in ceili(ENTRY.SIZE.y / float(CELL)):
		for x in ceili(ENTRY.SIZE.x / float(CELL)):
			var centre := Vector2(x + 0.5, y + 0.5) * CELL
			if Geometry2D.is_point_in_polygon(centre, avenue) or PAVED_SQUARE.has_point(centre):
				cells.append(Vector2i(x, y))
	return cells


## Every cell the old road, avenue or side paths touch (a cell counts when its centre or a point
## 10 px around it is inside), so the painted path is about as wide as the colour blocks were.
func _road_cells() -> Array[Vector2i]:
	var shapes := [ENTRY.road_polygon(), PackedVector2Array(ENTRY.AVENUE), ENTRY.branch_polygon(1), ENTRY.branch_polygon(-1)]
	var cells: Array[Vector2i] = []
	for y in ceili(ENTRY.SIZE.y / float(CELL)):
		for x in ceili(ENTRY.SIZE.x / float(CELL)):
			var centre := Vector2(x + 0.5, y + 0.5) * CELL
			for shape in shapes:
				var hit := false
				for d in [Vector2.ZERO, Vector2(10, 0), Vector2(-10, 0), Vector2(0, 10), Vector2(0, -10)]:
					if Geometry2D.is_point_in_polygon(centre + d, shape):
						hit = true
						break
				if hit:
					cells.append(Vector2i(x, y))
					break
	return cells
