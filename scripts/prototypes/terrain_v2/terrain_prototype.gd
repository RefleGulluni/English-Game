@tool
extends Node2D
## Terrain Prototype v2 test map.
##
## Covers every dual-grid case: large plaza, outer/inner corners, single-cell hole,
## single-cell island, 1- and 2-wide corridors and diagonal-only contacts.
## The player and a v1 grave are placed only as scale / contrast references.
##
## Capture mode (screenshots for review, then quits):
##   Godot --path . res://scenes/prototypes/terrain_v2/terrain_prototype.tscn -- --capture=<abs dir>

const DualGridTerrain := preload("res://scripts/prototypes/terrain_v2/dual_grid_terrain.gd")
const PLAYER_TEX := preload("res://art/characters/textures/wordbearer_base.png")
const GRAVE := preload("res://art/cemetery_kit_v1/props/grave_01.tscn")

const PLAYER_HEIGHT := 128.0
const CAPTURE_GRIDS := [64, 96]
const CAPTURE_ZOOMS := [1.0, 1.5, 2.0]

const LAYOUT := [
	"..............................",
	"..SSSSSSSS..........SSSS......",
	"..SSSSSSSS..........SSSS..S...",
	"..SSS.SSSS..........SSSS......",
	"..SSSSSSSSSSSSSSSSSSSSSS......",
	"..SSSSSSSSSSSSSSSSSSSSSS......",
	"..SSSSSSSS......SS..SSSS..S...",
	".....SSS........SS........S...",
	".....SSS........SSSSSSSS..S...",
	".....SSS........SSSSSSSS..S...",
	"...SSSSSSSS.....SS....SS......",
	"...SSSSSSSS..S..SS.S..SS......",
	"...SSSSSSSS...S.SS..S.SS......",
	"...SSSSSSSS....SSSSSSSSS......",
	"..........SS..................",
	"..........SSSSSSSSSSSS........",
	"..............................",
	"..............................",
]

@export var cell_size := 64:
	set(value):
		cell_size = value
		if is_inside_tree():
			_build()
@export var camera_zoom := 1.0:
	set(value):
		camera_zoom = value
		if _camera:
			_camera.zoom = Vector2.ONE * value

var _terrain: Node2D
var _player: Sprite2D
var _camera: Camera2D


func _ready() -> void:
	_build()
	if not Engine.is_editor_hint():
		_capture_if_requested()


func _build() -> void:
	for child in get_children():
		remove_child(child)
		child.queue_free()

	_terrain = DualGridTerrain.new()
	_terrain.cell_size = cell_size
	add_child(_terrain)
	_terrain.paint_layout(PackedStringArray(LAYOUT))

	_player = Sprite2D.new()
	_player.texture = PLAYER_TEX
	_player.scale = Vector2.ONE * PLAYER_HEIGHT / PLAYER_TEX.get_height()
	_player.offset = Vector2(0, -PLAYER_TEX.get_height() * 0.5) # feet at the node origin
	_player.position = _terrain.cell_to_world(Vector2i(6, 5))
	add_child(_player)

	var grave_on_stone := GRAVE.instantiate()
	grave_on_stone.position = _terrain.cell_to_world(Vector2i(4, 2))
	add_child(grave_on_stone)
	var grave_on_mud := GRAVE.instantiate()
	grave_on_mud.position = _terrain.cell_to_world(Vector2i(12, 8))
	add_child(grave_on_mud)

	_camera = Camera2D.new()
	_camera.position = _player.position + Vector2(0, -PLAYER_HEIGHT * 0.5)
	_camera.zoom = Vector2.ONE * camera_zoom
	add_child(_camera)
	if not Engine.is_editor_hint():
		_camera.make_current()


func _capture_if_requested() -> void:
	var dir := ""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--capture="):
			dir = arg.trim_prefix("--capture=")
	if dir.is_empty():
		return
	DirAccess.make_dir_recursive_absolute(dir)
	for grid in CAPTURE_GRIDS:
		cell_size = grid
		await _frames(20) # NoiseTexture2D generates on a thread
		_terrain.display.texture.get_image().save_png("%s/grid%d_mask.png" % [dir, grid])
		var map_px: Vector2 = Vector2((LAYOUT[0] as String).length(), LAYOUT.size()) * grid
		_camera.position = map_px * 0.5
		_camera.zoom = Vector2.ONE * minf(1280.0 / map_px.x, 720.0 / map_px.y)
		await _shot("%s/grid%d_overview.png" % [dir, grid])
		for z in CAPTURE_ZOOMS:
			_camera.position = _player.position + Vector2(0, -PLAYER_HEIGHT * 0.5)
			_camera.zoom = Vector2.ONE * z
			await _shot("%s/grid%d_zoom%.1f.png" % [dir, grid, z])
	get_tree().quit()


func _shot(path: String) -> void:
	await _frames(3)
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(path)
	print("captured ", path)


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame
