@tool
extends Node2D
## Terrain Prototype v2 — dual-grid stone/mud ground.
##
## Logic cells live in a TileMapLayer (atlas (0,0) = mud, (1,0) = stone).
## The visible ground is a single mask sprite offset by half a cell: every display cell
## looks at its four corner logic cells (TL=1, TR=2, BL=4, BR=8) and gets one of the
## 16 edge masks composed from the hand-made edge brushes. terrain_blend.gdshader then
## blends the stone and mud textures in world space through that mask.

const BRUSH_DIR := "res://art/cemetery_kit_v2/terrain/edge_brushes/"
const STONE_TEX := "res://art/cemetery_kit_v2/terrain/stone_texture_src.png"
const MUD_TEX := "res://art/cemetery_kit_v2/terrain/mud_texture_src.png"
const BLEND_SHADER := preload("res://scripts/prototypes/terrain_v2/terrain_blend.gdshader")

const MASK_RES := 128 # mask pixels per display cell
const STONE_TILE := Vector2i(1, 0)
const MUD_TILE := Vector2i(0, 0)
const DAMP_PROBE_WORLD := 28.0 # world px radius for the wet band / joint bleed
const WARP_CELLS := 0.35 # edge wobble amplitude, in cells
const ROUND_CELLS := 0.3 # corner rounding radius, in cells

@export var cell_size := 64

var logic: TileMapLayer
var display: Sprite2D
var map_size := Vector2i.ZERO
var _masks := {} # mask index -> Array[Image]


func _init() -> void:
	logic = TileMapLayer.new()
	logic.name = "Logic"
	logic.visible = false
	add_child(logic)
	display = Sprite2D.new()
	display.name = "Ground"
	display.centered = false
	display.show_behind_parent = true
	add_child(display)


func _ready() -> void:
	logic.tile_set = _make_logic_tileset()
	_build_masks()
	var mat := ShaderMaterial.new()
	mat.shader = BLEND_SHADER
	mat.set_shader_parameter("stone_tex", _mipmapped(STONE_TEX))
	mat.set_shader_parameter("mud_tex", _mipmapped(MUD_TEX))
	var noise := NoiseTexture2D.new()
	noise.seamless = true
	noise.width = 256
	noise.height = 256
	noise.noise = FastNoiseLite.new()
	noise.noise.frequency = 0.02
	noise.noise.fractal_octaves = 3
	mat.set_shader_parameter("noise_tex", noise)
	display.material = mat


## Fills the logic layer from rows of text: "S" = stone, anything else = mud.
func paint_layout(rows: PackedStringArray) -> void:
	logic.clear()
	map_size = Vector2i(rows[0].length(), rows.size())
	for y in rows.size():
		if rows[y].length() != map_size.x:
			push_error("Layout row %d has length %d, expected %d" % [y, rows[y].length(), map_size.x])
		for x in rows[y].length():
			logic.set_cell(Vector2i(x, y), 0, STONE_TILE if rows[y][x] == "S" else MUD_TILE)
	rebuild()


func rebuild() -> void:
	var w := map_size.x
	var h := map_size.y
	var img := Image.create_empty((w + 1) * MASK_RES, (h + 1) * MASK_RES, false, Image.FORMAT_L8)
	for j in range(-1, h):
		for i in range(-1, w):
			var idx := _stone(i, j) * 1 + _stone(i + 1, j) * 2 + _stone(i, j + 1) * 4 + _stone(i + 1, j + 1) * 8
			var variants: Array = _masks[idx]
			var pick: Image = variants[_cell_hash(i, j) % variants.size()]
			img.blit_rect(pick, Rect2i(0, 0, MASK_RES, MASK_RES), Vector2i((i + 1) * MASK_RES, (j + 1) * MASK_RES))
	display.texture = ImageTexture.create_from_image(img)
	# Display cell (i, j) spans from the centre of logic cell (i, j) to the centre of (i+1, j+1).
	display.position = Vector2(-0.5, -0.5) * cell_size
	display.scale = Vector2.ONE * float(cell_size) / MASK_RES
	var world_size := Vector2(w + 1, h + 1) * cell_size
	var mat := display.material as ShaderMaterial
	mat.set_shader_parameter("probe_uv", Vector2.ONE * DAMP_PROBE_WORLD / world_size)
	mat.set_shader_parameter("warp_uv", Vector2.ONE * WARP_CELLS * cell_size / world_size)
	mat.set_shader_parameter("round_uv", Vector2.ONE * ROUND_CELLS * cell_size / world_size)


func cell_to_world(cell: Vector2i) -> Vector2:
	return (Vector2(cell) + Vector2(0.5, 0.5)) * cell_size


func _stone(x: int, y: int) -> int:
	return 1 if logic.get_cell_atlas_coords(Vector2i(x, y)) == STONE_TILE else 0


func _cell_hash(x: int, y: int) -> int:
	return absi((x * 73856093) ^ (y * 19349663))


func _build_masks() -> void:
	var straight := _load_brushes(["edge_straight_01", "edge_straight_02", "edge_straight_03"])
	var outer := _load_brushes(["edge_outer_corner_01", "edge_outer_corner_02"])
	var inner := _load_brushes(["edge_inner_corner_01", "edge_inner_corner_02"])
	_masks.clear()
	_masks[0] = [_solid(0.0)]
	_masks[15] = [_solid(1.0)]
	# Base brushes: outer = stone at TL, straight = stone on top, inner = mud at BR.
	# Each clockwise quarter turn moves those corners TL -> TR -> BR -> BL.
	var outer_idx := [1, 2, 8, 4]
	var straight_idx := [3, 10, 12, 5]
	var inner_idx := [7, 11, 14, 13]
	for r in 4:
		_masks[outer_idx[r]] = outer.map(func(b: Image) -> Image: return _rotated(b, r))
		_masks[straight_idx[r]] = straight.map(func(b: Image) -> Image: return _rotated(b, r))
		_masks[inner_idx[r]] = inner.map(func(b: Image) -> Image: return _rotated(b, r))
	# Diagonal pairs have no brush of their own: union of the two outer corners.
	_masks[9] = [_union(_masks[1][0], _masks[8][1]), _union(_masks[1][1], _masks[8][0])]
	_masks[6] = [_union(_masks[2][0], _masks[4][1]), _union(_masks[2][1], _masks[4][0])]


func _load_brushes(names: Array) -> Array:
	var out := []
	for n in names:
		var img := Image.load_from_file(ProjectSettings.globalize_path(BRUSH_DIR + n + ".png"))
		img.convert(Image.FORMAT_L8)
		img.resize(MASK_RES, MASK_RES, Image.INTERPOLATE_LANCZOS)
		out.append(img)
	return out


func _rotated(src: Image, quarter_turns: int) -> Image:
	var img := src.duplicate() as Image
	for i in quarter_turns:
		img.rotate_90(CLOCKWISE)
	return img


func _union(a: Image, b: Image) -> Image:
	var img := a.duplicate() as Image
	for y in MASK_RES:
		for x in MASK_RES:
			var v := maxf(a.get_pixel(x, y).r, b.get_pixel(x, y).r)
			img.set_pixel(x, y, Color(v, v, v))
	return img


func _solid(v: float) -> Image:
	var img := Image.create_empty(MASK_RES, MASK_RES, false, Image.FORMAT_L8)
	img.fill(Color(v, v, v))
	return img


func _mipmapped(path: String) -> ImageTexture:
	# Loaded straight from the PNG so the prototype does not depend on import settings;
	# mipmaps keep the downscaled textures from shimmering.
	var img := Image.load_from_file(ProjectSettings.globalize_path(path))
	img.convert(Image.FORMAT_RGBA8)
	img.generate_mipmaps()
	return ImageTexture.create_from_image(img)


func _make_logic_tileset() -> TileSet:
	var ts := TileSet.new()
	ts.tile_size = Vector2i(cell_size, cell_size)
	var img := Image.create_empty(cell_size * 2, cell_size, false, Image.FORMAT_RGBA8)
	img.fill_rect(Rect2i(0, 0, cell_size, cell_size), Color(0.45, 0.33, 0.22, 0.5))
	img.fill_rect(Rect2i(cell_size, 0, cell_size, cell_size), Color(0.6, 0.66, 0.62, 0.5))
	var src := TileSetAtlasSource.new()
	src.texture = ImageTexture.create_from_image(img)
	src.texture_region_size = ts.tile_size
	src.create_tile(MUD_TILE)
	src.create_tile(STONE_TILE)
	ts.add_source(src, 0)
	return ts
