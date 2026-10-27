extends SceneTree
## Builds the cemetery ground TileSets and the paint test room from the art in
## art/cemetery_v3/ground/: the big base (224×128, two variants) and the path corner masks
## (scripts/tools/build_ground_path_masks.py). Re-run after either changes; the room scene is
## only written when it doesn't exist yet, so paths the user painted are kept.
##   Godot --headless --path . --import
##   Godot --headless --path . --script res://scripts/tools/build_ground_paint_room.gd

const GROUND := "res://art/cemetery_v3/ground/"
const MASKS := GROUND + "transitions/masks/"
const BASE_TILESET := GROUND + "ground_base_tileset.tres"
const PATH_TILESET := MASKS + "ground_path_tileset.tres"
const ROOM := "res://scenes/prototypes/ground_paint/ground_paint_room.tscn"
const ROOM_SCRIPT := "res://scripts/prototypes/ground_paint/ground_paint_room.gd"
const PATH_SHADER := "res://scripts/world/v3/ground_path.gdshader"
const PATH_TEXTURE := GROUND + "transitions/path_texture_01.png" # the art group's seamless path surface
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


func _init() -> void:
	var base_set := _base_tileset()
	var path_set := _path_tileset()
	ResourceSaver.save(base_set, BASE_TILESET)
	ResourceSaver.save(path_set, PATH_TILESET)
	print("tilesets saved")
	if not ResourceLoader.exists(ROOM):
		_save_room(load(BASE_TILESET), load(PATH_TILESET))
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


func _path_tileset() -> TileSet:
	var ts := TileSet.new()
	ts.tile_size = Vector2i(32, 32)
	ts.add_terrain_set()
	ts.set_terrain_set_mode(0, TileSet.TERRAIN_MODE_MATCH_CORNERS)
	ts.add_terrain(0)
	ts.set_terrain_name(0, 0, "碎石泥路")
	ts.set_terrain_color(0, 0, Color(0.85, 0.72, 0.5))
	var src := TileSetAtlasSource.new()
	src.texture = load(MASKS + "ground_path_masks_01.png")
	src.texture_region_size = Vector2i(32, 32)
	ts.add_source(src, 0)
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(MASKS + "ground_path_masks_01.json"))
	for cell in data.cells:
		var coords := Vector2i(int(cell.x), int(cell.y))
		src.create_tile(coords)
		var td := src.get_tile_data(coords, 0)
		td.terrain_set = 0
		td.terrain = 0
		for key in BITS:
			td.set_terrain_peering_bit(BITS[key], 0 if int(cell[key]) == 1 else -1)
	return ts


func _save_room(base_set: TileSet, path_set: TileSet) -> void:
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
	base.tile_set = base_set
	ground.add_child(base)
	base.owner = root
	var rng := RandomNumberGenerator.new()
	rng.seed = 5
	for y in 5:
		for x in 5:
			base.set_cell(Vector2i(x, y), 0 if rng.randf() < 0.65 else 1, Vector2i.ZERO)

	var path := TileMapLayer.new()
	path.name = "Path"
	path.tile_set = path_set
	var mat := ShaderMaterial.new()
	mat.shader = load(PATH_SHADER)
	mat.set_shader_parameter("path_texture", load(PATH_TEXTURE))
	path.material = mat
	ground.add_child(path)
	path.owner = root
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

	var scene := PackedScene.new()
	scene.pack(root)
	DirAccess.make_dir_recursive_absolute(ROOM.get_base_dir())
	ResourceSaver.save(scene, ROOM)
	print("room saved: ", ROOM)
