extends Node
## 墓园物件第一批（角色设计组，art/cemetery_v3/props/）的实机验收房间。
## 物件按 A 残墙院落的样子摆放，地面暂用样板地面板，主角可走动，物件有碰撞、遮挡与半透明。
## 按键：WASD 走路 · T 开关游戏整体色调 · F 全屏
## 截图：Godot --path . res://scenes/prototypes/props_v3/props_v3_room.tscn -- --capture=<目录>

const HERO_SCENE := preload("res://scenes/player/hero_b1.tscn")
const PROPS := "res://art/cemetery_v3/props/"
const NATIVE := Vector2i(960, 540)
# [物件, 原点]；碰撞留空，由房间按立体部分的脚自动生成。物件名可带子目录（返修试样）
const TRIAL := "qc/revision1_tombstone_trial/tombstone_upright_01"
const LAYOUT := {
	"id": "props_v3", "seed": 7, "dead_grass": 8, "prop_dir": PROPS,
	"props": [
		["low_wall_01", Vector2(150, 150), null],
		["low_wall_01", Vector2(246, 150), null],
		["wall_pillar_01", Vector2(198, 154), null],
		["wall_pillar_01", Vector2(294, 154), null],
		["low_wall_broken_01", Vector2(390, 150), null],
		["wall_pillar_01", Vector2(552, 154), null],
		["iron_fence_01", Vector2(600, 150), null],
		["iron_fence_01", Vector2(696, 150), null],
		["wall_pillar_01", Vector2(744, 154), null],
		[TRIAL, Vector2(110, 320), null],
		[TRIAL, Vector2(380, 480), null], # 返修试样和第 1 版并排，主角站在中间
		["tombstone_upright_01", Vector2(510, 480), null],
		["tombstone_upright_02", Vector2(220, 400), null],
		["tombstone_cross_01", Vector2(80, 470), null],
		["open_grave_01", Vector2(640, 350), null],
		["grave_lid_01", Vector2(738, 352), null],
		[TRIAL, Vector2(840, 290), null],
		["tombstone_cross_01", Vector2(890, 430), null],
		["tombstone_upright_02", Vector2(780, 500), null],
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
	_room = CemeteryRoom.new(LAYOUT)
	_viewport.add_child(_room)
	var hero := HERO_SCENE.instantiate()
	hero.position = Vector2(445, 470)
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
	add_child(_label)
	_update_label()
	if "--capture" in str(OS.get_cmdline_user_args()):
		_capture()


func _tint() -> CanvasModulate:
	for child in _room.get_children():
		if child is CanvasModulate:
			return child
	return null


func _update_label() -> void:
	_label.text = "墓园物件第一批 · WASD 走路 · T 游戏色调：%s · F 全屏" % ("开" if _tint().visible else "关")


func _unhandled_key_input(event: InputEvent) -> void:
	if not event.is_pressed() or event.is_echo():
		return
	if event.physical_keycode == KEY_T:
		_tint().visible = not _tint().visible
		_update_label()
	elif event.physical_keycode == KEY_F:
		var win := get_window()
		win.mode = Window.MODE_WINDOWED if win.mode == Window.MODE_FULLSCREEN else Window.MODE_FULLSCREEN


func _capture() -> void:
	var dir := str(OS.get_cmdline_user_args()[0]).get_slice("=", 1)
	DirAccess.make_dir_recursive_absolute(dir)
	var hero: Node2D = _room.player
	for shot in [["room", Vector2(445, 470)], ["by_grave", Vector2(600, 400)], ["behind_wall", Vector2(250, 140)]]:
		hero.position = shot[1]
		for i in 40:
			await get_tree().process_frame
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("%s/%s.png" % [dir, shot[0]])
	get_tree().quit()
