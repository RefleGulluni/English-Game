extends Node
## 地面刷路试验（方法：docs/GROUND_TERRAIN_METHOD.md）：大块底子 + 可以用画笔刷的草地和碎石泥路。
## 在编辑器里打开本场景 → 选中 Ground/Path（或 Ground/Grass）→ 底部 TileMap 面板的 Terrains 页 → 选“碎石泥路”（或“枯草苔藓地”）→ 在画面上拖着刷；
## 右键擦掉。Ground/Base 是两块底子随机铺的，一般不用动。运行（F6）后 WASD 走路看效果。
## 瓦片集和本场景由 scripts/tools/build_ground_paint_room.gd 生成；本场景已存在时不会被覆盖。
## 截图：Godot --path . res://scenes/prototypes/ground_paint/ground_paint_room.tscn -- --capture=<目录>

const HERO_SCENE := preload("res://scenes/player/hero_b1.tscn")
const NATIVE := Vector2i(960, 540)
const LAYOUT := {
	"id": "ground_paint", "seed": 3, "dead_grass": 0, "plate_file": "",
	"props": [
		["tombstone_upright_01", Vector2(300, 250), null], ["tombstone_cross_01", Vector2(640, 380), null],
		["tombstone_pointed_01", Vector2(180, 430), null], ["tombstone_small_01", Vector2(560, 160), null],
		["obelisk_01", Vector2(860, 470), null],
	],
}

var _viewport: SubViewport
var _room: CemeteryRoom
var _label: Label


func _ready() -> void:
	var win := get_window()
	win.content_scale_size = NATIVE
	win.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	win.content_scale_stretch = Window.CONTENT_SCALE_STRETCH_INTEGER
	if DisplayServer.get_name() != "headless" and win.mode == Window.MODE_WINDOWED:
		var usable := DisplayServer.screen_get_usable_rect(win.current_screen)
		var k := maxi(1, mini(usable.size.x / NATIVE.x, (usable.size.y - 40) / NATIVE.y))
		win.size = NATIVE * k
		win.position = usable.position + (usable.size - win.size) / 2
	_viewport = SubViewport.new()
	_viewport.size = NATIVE
	_viewport.canvas_item_default_texture_filter = Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_NEAREST
	_viewport.snap_2d_transforms_to_pixel = true
	_viewport.snap_2d_vertices_to_pixel = true
	add_child(_viewport)
	var ground: Node2D = $Ground # painted in the editor; drawn under the room
	remove_child(ground)
	_viewport.add_child(ground)
	_room = CemeteryRoom.new(LAYOUT)
	_viewport.add_child(_room)
	var hero := HERO_SCENE.instantiate()
	hero.position = Vector2(470, 500)
	_room.sorted.add_child(hero)
	_room.player = hero
	var screen := TextureRect.new()
	screen.texture = _viewport.get_texture()
	screen.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	screen.size = Vector2(NATIVE)
	add_child(screen)
	_label = Label.new()
	_label.position = Vector2(8, 6)
	_label.add_theme_font_size_override("font_size", 11)
	_label.add_theme_constant_override("outline_size", 3)
	_label.add_theme_color_override("font_outline_color", Color.BLACK)
	_label.text = "地面刷路试验 · WASD 走路 · T 游戏色调 · F 全屏 · 在编辑器里刷：Ground/Path 碎石泥路 · Ground/Grass 枯草苔藓地"
	add_child(_label)
	if "--capture" in str(OS.get_cmdline_user_args()):
		_capture()


func _unhandled_key_input(event: InputEvent) -> void:
	if not event.is_pressed() or event.is_echo():
		return
	if event.physical_keycode == KEY_T:
		for child in _room.get_children():
			if child is CanvasModulate:
				child.visible = not child.visible
	elif event.physical_keycode == KEY_F:
		var win := get_window()
		win.mode = Window.MODE_WINDOWED if win.mode == Window.MODE_FULLSCREEN else Window.MODE_FULLSCREEN


func _capture() -> void:
	var dir := ""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--capture="):
			dir = arg.get_slice("=", 1)
	DirAccess.make_dir_recursive_absolute(dir)
	for i in 30:
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(dir + "/room.png")
	get_tree().quit()
