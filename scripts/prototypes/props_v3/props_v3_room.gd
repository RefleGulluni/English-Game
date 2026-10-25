extends Node
## 墓园物件（角色设计组，art/cemetery_v3/props/）的实机验收房间。
## 物件按 A 残墙院落的样子摆放，地面暂用样板地面板，主角可走动，物件有碰撞、遮挡与半透明。
## 按键：WASD 走路 · T 开关游戏整体色调 · F 全屏
## 截图：Godot --path . res://scenes/prototypes/props_v3/props_v3_room.tscn -- --capture=<目录>
## 换地面试样：-- --plate=<PNG 路径>（960×540）

const HERO_SCENE := preload("res://scenes/player/hero_b1.tscn")
const PROPS := "res://art/cemetery_v3/props/"
const NATIVE := Vector2i(960, 540)
const SKELETON := "../../character_design/enemies/skeleton/" # relative to PROPS
# [物件, 原点]；碰撞留空，由房间按立体部分的脚自动生成。物件名可带子目录（例如 qc/backups/round1/ 里的旧版）
# 第 2 版拼接：完整墙每 148 px 接一段（画布内拼接列 x=21 / 168），残墙左拼接列 x=21；铁栏每 132 px（x=12 / 143）
const LAYOUT := {
	"id": "props_v3", "seed": 7, "dead_grass": 8, "prop_dir": PROPS,
	"props": [
		# A 乱石墙家族：完整墙 + 嵌柱 + 完整墙 + 断墙，间隔 148
		["low_wall_01", Vector2(120, 150), null],
		["low_wall_rubble_pillar_01", Vector2(268, 150), null],
		["low_wall_01", Vector2(416, 150), null],
		["low_wall_rubble_broken_01", Vector2(564, 150), null],
		# B 条石墙家族：门柱 + 铁栏 + 门柱
		["wall_pillar_01", Vector2(700, 151), null],
		["iron_fence_01", Vector2(781, 150), null],
		["wall_pillar_01", Vector2(852, 151), null],
		# B 条石墙家族：门柱 + 02 + 01 + 02 + 断墙（02 有效宽 240；接 01 或断墙间隔 187，01 接 02 间隔 181）
		["low_wall_ashlar_02", Vector2(184, 270), null],
		["low_wall_ashlar_01", Vector2(371, 270), null],
		["low_wall_ashlar_02", Vector2(552, 270), null],
		["low_wall_broken_01", Vector2(739, 270), null],
		["wall_pillar_01", Vector2(60, 271), null],
		# 墓碑家族（第一批 + 第二批），小物件不给碰撞（false）
		["tombstone_upright_01", Vector2(70, 375), null],
		["tombstone_upright_01_tilted", Vector2(165, 392), null],
		["tombstone_small_01", Vector2(115, 450), null],
		["grave_vase_01", Vector2(205, 405), false],
		["tombstone_pointed_01", Vector2(260, 432), null],
		["tombstone_cross_01", Vector2(60, 515), null],
		["candles_01", Vector2(110, 520), false],
		["tombstone_upright_02", Vector2(215, 520), null],
		["tombstone_flat_01", Vector2(335, 525), null],
		["rubble_pile_01", Vector2(375, 455), false],
		["tombstone_upright_02_broken", Vector2(545, 505), null],
		["grave_lantern_01", Vector2(590, 425), false],
		["open_grave_01", Vector2(670, 400), null],
		["grave_lid_01", Vector2(820, 415), null],
		["obelisk_01", Vector2(915, 345), null],
		["grave_slab_01", Vector2(745, 510), false],
		["tombstone_cross_01_broken", Vector2(900, 525), null],
		# 选定的骷髅 B「余裹者」（D-037）：四方向（正 / 背 / 左 / 右）+ 骨堆
		[SKELETON + "skeleton_B", Vector2(360, 365), null],
		[SKELETON + "skeleton_B_back", Vector2(440, 365), null],
		[SKELETON + "skeleton_B_left", Vector2(520, 365), null],
		[SKELETON + "skeleton_B_right", Vector2(600, 365), null],
		[SKELETON + "skeleton_B_remains", Vector2(560, 420), false],
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
	var layout := LAYOUT.duplicate()
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--plate="):
			layout.plate_file = arg.get_slice("=", 1)
	_room = CemeteryRoom.new(layout)
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
	_label.text = "墓园物件 · WASD 走路 · T 游戏色调：%s · F 全屏" % ("开" if _tint().visible else "关")


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
	var dir := ""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--capture="):
			dir = arg.get_slice("=", 1)
	DirAccess.make_dir_recursive_absolute(dir)
	var hero: Node2D = _room.player
	for shot in [["room", Vector2(445, 470)], ["by_grave", Vector2(600, 400)], ["behind_wall", Vector2(450, 255)]]:
		hero.position = shot[1]
		for i in 40:
			await get_tree().process_frame
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("%s/%s.png" % [dir, shot[0]])
	get_tree().quit()
