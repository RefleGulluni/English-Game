extends SceneTree
## Builds the cemetery ground TileSets and the paint test room from the art in
## art/cemetery_v3/ground/: the big base (224×128, two variants) and one painted terrain per
## entry in TERRAINS (corner masks from scripts/tools/build_ground_path_masks.py + the art group's
## 224×128 texture). Re-run after either changes. The room scene is only created when missing;
## an existing room only gains the layers it lacks (and the Decals node), so everything the user
## painted is kept.
## Method: docs/GROUND_TERRAIN_METHOD.md.
##   Godot --headless --path . --import
##   Godot --headless --path . --script res://scripts/tools/build_ground_paint_room.gd

const GROUND := "res://art/cemetery_v3/ground/"
const MASKS := GROUND + "transitions/masks/"
const BASE_TILESET := GROUND + "ground_base_tileset.tres"
const ROOM := "res://scenes/prototypes/ground_paint/ground_paint_room.tscn"
const ROOM_SCRIPT := "res://scripts/prototypes/ground_paint/ground_paint_room.gd"
const PATH_SHADER := "res://scripts/world/v3/ground_path.gdshader"
## Painted terrains, bottom to top: grass under paths, so a path can cross a meadow.
const TERRAINS := [
	{"layer": "Grass", "name": "枯草苔藓地", "masks": "ground_grass_masks_01", "tileset": "ground_grass_tileset.tres",
		"texture": GROUND + "transitions/grass_texture_01.png", "color": Color(0.5, 0.62, 0.38)},
	{"layer": "Path", "name": "碎石泥路", "masks": "ground_path_masks_01", "tileset": "ground_path_tileset.tres",
		"texture": GROUND + "transitions/path_texture_01.png", "color": Color(0.85, 0.72, 0.5)},
]
const BITS := {
	"tl": TileSet.CELL_NEIGHBOR_TOP_LEFT_CORNER, "tr": TileSet.CELL_NEIGHBOR_TOP_RIGHT_CORNER,
	"bl": TileSet.CELL_NEIGHBOR_BOTTOM_LEFT_CORNER, "br": TileSet.CELL_NEIGHBOR_BOTTOM_RIGHT_CORNER,
}
## A sample path in 32 px cells: a winding avenue from the bottom, a branch to the right, and a
## loose patch, so the room opens with something to look at.
const SAMPLE_PATH := [
	[Vector2(14, 17), Vector2(14, 12), Vector2(12, 8), Vector2(9, 5), Vector2(8, 1)],
	[Vector2(13, 10), Vector2(18, 8), Vector2(23, 7), Vector2(27, 4)],
]
const SAMPLE_PATCH := [Vector2(23, 13), Vector2(24, 13), Vector2(23, 14)]
## Sample meadows (cell rectangles) painted when the Grass layer is first added.
const SAMPLE_GRASS := [Rect2i(1, 9, 6, 5), Rect2i(19, 11, 7, 5), Rect2i(17, 1, 5, 4)]
## Ground decals (scenes from scripts/tools/bake_ground_decals.gd) dropped in when the Decals node
## is first added, so the user sees how they sit on the painted ground.
const DECALS := "res://scenes/props/cemetery/decals/"
const SAMPLE_DECALS := [["decal_puddle_02", Vector2(420, 300)], ["decal_leaves_01", Vector2(330, 262)],
	["decal_moss_02", Vector2(700, 250)], ["decal_pebbles_01", Vector2(520, 450)],
	["decal_dead_flowers_01", Vector2(650, 398)], ["decal_roots_01", Vector2(150, 150)]]


func _init() -> void:
	ResourceSaver.save(_base_tileset(), BASE_TILESET)
	for t in TERRAINS:
		ResourceSaver.save(_terrain_tileset(t), MASKS + t.tileset)
	print("tilesets saved")
	if not ResourceLoader.exists(ROOM):
		_save_room()
	else:
		_add_missing_layers()
	quit()


func _base_tileset() -> TileSet:
	var ts := TileSet.new()
	ts.tile_size = Vector2i(224, 128)
	for i in 2:
		var src := TileSetAtlasSource.new()
		src.texture = load(GROUND + "base/ground_base_%02d.png" % (i + 1))
		src.texture_region_size = Vector2i(224, 128)
		ts.add_source(src, i)
		src.create_tile(Vector2i.ZERO)
	return ts


func _terrain_tileset(t: Dictionary) -> TileSet:
	var ts := TileSet.new()
	ts.tile_size = Vector2i(32, 32)
	ts.add_terrain_set()
	ts.set_terrain_set_mode(0, TileSet.TERRAIN_MODE_MATCH_CORNERS)
	ts.add_terrain(0)
	ts.set_terrain_name(0, 0, t.name)
	ts.set_terrain_color(0, 0, t.color)
	var src := TileSetAtlasSource.new()
	src.texture = load(MASKS + t.masks + ".png")
	src.texture_region_size = Vector2i(32, 32)
	ts.add_source(src, 0)
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(MASKS + t.masks + ".json"))
	for cell in data.cells:
		var coords := Vector2i(int(cell.x), int(cell.y))
		src.create_tile(coords)
		var td := src.get_tile_data(coords, 0)
		td.terrain_set = 0
		td.terrain = 0
		for key in BITS:
			td.set_terrain_peering_bit(BITS[key], 0 if int(cell[key]) == 1 else -1)
	return ts


func _terrain_layer(t: Dictionary) -> TileMapLayer:
	var layer := TileMapLayer.new()
	layer.name = t.layer
	layer.tile_set = load(MASKS + t.tileset)
	var mat := ShaderMaterial.new()
	mat.shader = load(PATH_SHADER)
	mat.set_shader_parameter("path_texture", load(t.texture))
	layer.material = mat
	return layer


func _save_room() -> void:
	var root := Node.new()
	root.name = "GroundPaintRoom"
	root.set_script(load(ROOM_SCRIPT))
	var ground := Node2D.new()
	ground.name = "Ground"
	ground.z_index = -10
	root.add_child(ground)
	ground.owner = root

	var base := TileMapLayer.new()
	base.name = "Base"
	base.tile_set = load(BASE_TILESET)
	ground.add_child(base)
	base.owner = root
	var rng := RandomNumberGenerator.new()
	rng.seed = 5
	for y in 5:
		for x in 5:
			base.set_cell(Vector2i(x, y), 0 if rng.randf() < 0.65 else 1, Vector2i.ZERO)

	for t in TERRAINS:
		var layer := _terrain_layer(t)
		ground.add_child(layer)
		layer.owner = root
	_paint_sample_grass(ground.get_node("Grass"))
	_add_decals(ground, root)
	var path: TileMapLayer = ground.get_node("Path")
	var cells: Array[Vector2i] = []
	for line in SAMPLE_PATH:
		for i in line.size() - 1:
			var a: Vector2 = line[i]
			var b: Vector2 = line[i + 1]
			for k in int(a.distance_to(b) * 3.0) + 1:
				var p := a.lerp(b, k / (a.distance_to(b) * 3.0))
				for d in [Vector2i(0, 0), Vector2i(1, 0), Vector2i(0, 1), Vector2i(1, 1)]:
					var c: Vector2i = Vector2i(p.floor()) + d
					if not cells.has(c):
						cells.append(c)
	for p in SAMPLE_PATCH:
		cells.append(Vector2i(p))
	path.set_cells_terrain_connect(cells, 0, 0)

	_pack(root)


## An older room keeps all its painting and only gains the terrain layers it doesn't have yet,
## each slotted in at its place in TERRAINS (grass under paths).
func _add_missing_layers() -> void:
	var root: Node = load(ROOM).instantiate()
	var ground: Node2D = root.get_node("Ground")
	var added := false
	for i in TERRAINS.size():
		var t: Dictionary = TERRAINS[i]
		if ground.has_node(t.layer):
			continue
		var layer := _terrain_layer(t)
		ground.add_child(layer)
		layer.owner = root
		ground.move_child(layer, 1 + i) # after Base
		if t.layer == "Grass":
			_paint_sample_grass(layer)
		added = true
		print("added layer ", t.layer)
	if not ground.has_node("Decals"):
		_add_decals(ground, root)
		added = true
		print("added Decals")
	if added:
		_pack(root)


## The Decals node goes last under Ground: above every painted layer, below props and actors.
func _add_decals(ground: Node2D, root: Node) -> void:
	var decals := Node2D.new()
	decals.name = "Decals"
	ground.add_child(decals)
	decals.owner = root
	for d in SAMPLE_DECALS:
		var decal: Node2D = load(DECALS + d[0] + ".tscn").instantiate()
		decal.position = d[1]
		decals.add_child(decal, true)
		decal.owner = root


func _paint_sample_grass(layer: TileMapLayer) -> void:
	var cells: Array[Vector2i] = []
	for r in SAMPLE_GRASS:
		for y in range(r.position.y, r.end.y):
			for x in range(r.position.x, r.end.x):
				cells.append(Vector2i(x, y))
	layer.set_cells_terrain_connect(cells, 0, 0)


func _pack(root: Node) -> void:
	var scene := PackedScene.new()
	scene.pack(root)
	DirAccess.make_dir_recursive_absolute(ROOM.get_base_dir())
	ResourceSaver.save(scene, ROOM)
	print("room saved: ", ROOM)
