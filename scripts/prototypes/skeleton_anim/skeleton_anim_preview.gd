extends Node
## 骷髅 B「余裹者」动画试看（docs/SKELETON_ANIMATION_REQUEST.md）：在墓地地面上按游戏大小播放角色组交来的动画。
## 左上一只按 50 px/秒 绕着一圈走（右 → 下 → 左 → 上，四个方向的行走都会出现，到拐角站一下待机）；
## 中间一排四只站着待机（正 / 背 / 左 / 右），按 H 一起受击；
## 右下一只按空格散架 → 骨堆待机 → 重组 → 站回待机。主角站在旁边作比例参照。
## 有返修版（`_v3` / `_v2`）的动画默认播最新一版，V 切回最初版对比；待机各自从随机位置开始，几只不会一起动。
## 按键：空格 散架 / 重组 · H 受击 · V 新版 / 最初版 · T 开关游戏整体色调 · F 全屏
## 截图：Godot --path . res://scenes/prototypes/skeleton_anim/skeleton_anim_preview.tscn -- --capture=<目录>

const HERO_SCENE := preload("res://scenes/player/hero_b1.tscn")
const PROPS := "res://art/cemetery_v3/props/"
const ANIM := "res://art/character_design/enemies/skeleton/anim/"
const NATIVE := Vector2i(960, 540)
const WALK_SPEED := 50.0
const LOOP := [Vector2(80, 170), Vector2(360, 170), Vector2(360, 300), Vector2(80, 300)] # 绕圈的四个拐角
const PAUSE := 1.0 # 每个拐角站一下，看待机和走 / 停的衔接
const DIRS := ["front", "back", "left", "right"]
const REMAINS_TIME := 3.0
const SHADOW := Color(0.03, 0.03, 0.05, 0.45)
const LAYOUT := {
	"id": "skeleton_anim", "seed": 11, "dead_grass": 10, "prop_dir": PROPS,
	"props": [
		["tombstone_upright_01", Vector2(220, 250), null], ["tombstone_cross_01", Vector2(520, 150), null],
		["obelisk_01", Vector2(900, 200), null], ["tombstone_small_01", Vector2(60, 470), null],
		["tombstone_pointed_01", Vector2(880, 520), null], ["tombstone_flat_01", Vector2(300, 520), null],
	],
}

var _viewport: SubViewport
var _room: CemeteryRoom
var _walker: Node2D
var _walk_strip: SpriteStrip
var _leg := 0
var _pause := 0.0
var _standing: Array[SpriteStrip] = []
var _faller: SpriteStrip
var _label: Label
var _use_v2 := true
var _keys := {} # every animation name in timing.json


func _ready() -> void:
	_keys = JSON.parse_string(FileAccess.get_file_as_string(ANIM + "timing.json")).animations
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
	hero.position = Vector2(620, 470)
	_room.sorted.add_child(hero)
	hero.face_direction(Vector2.RIGHT)
	_room.player = hero

	_walker = _actor(LOOP[0], "skeleton_B_walk_right")
	_walk_strip = _walker.get_node("Strip")
	for i in DIRS.size():
		var strip: SpriteStrip = _actor(Vector2(520 + i * 100, 330), "skeleton_B_idle_" + DIRS[i]).get_node("Strip")
		strip.finished.connect(func(): _play(strip, "skeleton_B_idle_" + DIRS[i]))
		strip.random_phase()
		_standing.append(strip)
	_faller = _actor(Vector2(760, 470), "skeleton_B_idle_front").get_node("Strip")
	_faller.finished.connect(_faller_next)

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
	_update_label()
	add_child(_label)
	if "--capture" in str(OS.get_cmdline_user_args()):
		_capture()


## A Y-sorted actor: contact shadow + the strip, feet on the origin.
func _actor(at: Vector2, anim: String) -> Node2D:
	var root := Node2D.new()
	root.position = at
	_room.sorted.add_child(root)
	root.add_child(PixelArt.ellipse_sprite(34, 12, SHADOW, Vector2(0, -3)))
	var strip := SpriteStrip.new()
	strip.name = "Strip"
	root.add_child(strip)
	_play(strip, anim)
	return root


## Plays the newest returned version of anim (_v3, then _v2) unless V has switched back to the first set.
func _play(strip: SpriteStrip, anim: String) -> void:
	if _use_v2:
		for suffix in ["_v3", "_v2"]:
			if _keys.has(anim + suffix):
				strip.load_strip(ANIM, anim + suffix)
				return
	strip.load_strip(ANIM, anim)


func _base(anim: String) -> String:
	return anim.trim_suffix("_v2").trim_suffix("_v3")


func _update_label() -> void:
	_label.text = "骷髅动画试看（%s）· 左上：绕圈走 · 中间：四方向待机，H 受击 · 右下：空格 散架 / 重组 · V 新版 / 最初版 · T 色调 · F 全屏" % ("最新返修版" if _use_v2 else "最初版")


func _process(delta: float) -> void:
	var target: Vector2 = LOOP[(_leg + 1) % LOOP.size()]
	var dir := _dir_name(target - _walker.position)
	if _pause > 0.0:
		_pause -= delta
		return
	if _base(_walk_strip.current) != "skeleton_B_walk_" + dir:
		_play(_walk_strip, "skeleton_B_walk_" + dir)
	_walker.position = _walker.position.move_toward(target, WALK_SPEED * delta)
	if _walker.position == target:
		_leg = (_leg + 1) % LOOP.size()
		_pause = PAUSE
		_play(_walk_strip, "skeleton_B_idle_" + dir)


func _dir_name(v: Vector2) -> String:
	if absf(v.x) >= absf(v.y):
		return "right" if v.x > 0 else "left"
	return "front" if v.y > 0 else "back"


## collapse → remains idle (a few seconds) → reassemble → idle again.
func _faller_next() -> void:
	match _base(_faller.current):
		"skeleton_B_collapse_front":
			_play(_faller, "skeleton_B_remains_idle")
			await get_tree().create_timer(REMAINS_TIME).timeout
			_play(_faller, "skeleton_B_reassemble_front")
		"skeleton_B_reassemble_front":
			_play(_faller, "skeleton_B_idle_front")


func _collapse() -> void:
	if _base(_faller.current) == "skeleton_B_idle_front":
		_play(_faller, "skeleton_B_collapse_front")


func _hit() -> void:
	for i in DIRS.size():
		_play(_standing[i], "skeleton_B_hit_" + DIRS[i])


func _tint() -> CanvasModulate:
	for child in _room.get_children():
		if child is CanvasModulate:
			return child
	return null


func _unhandled_key_input(event: InputEvent) -> void:
	if not event.is_pressed() or event.is_echo():
		return
	if event.physical_keycode == KEY_SPACE:
		_collapse()
	elif event.physical_keycode == KEY_H:
		_hit()
	elif event.physical_keycode == KEY_V:
		_use_v2 = not _use_v2
		var strips: Array = [_walk_strip, _faller]
		strips.append_array(_standing)
		for strip in strips:
			_play(strip, _base(strip.current))
		_update_label()
	elif event.physical_keycode == KEY_T:
		_tint().visible = not _tint().visible
	elif event.physical_keycode == KEY_F:
		var win := get_window()
		win.mode = Window.MODE_WINDOWED if win.mode == Window.MODE_FULLSCREEN else Window.MODE_FULLSCREEN


## Saves a few moments: the four hits at their peak, the collapse, and the reassembly.
func _capture() -> void:
	var dir := ""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--capture="):
			dir = arg.get_slice("=", 1)
	DirAccess.make_dir_recursive_absolute(dir)
	for i in 20:
		await get_tree().process_frame
	_hit()
	_collapse()
	var shots := [["01_hit_peak", 0.12], ["02_collapsing", 0.45], ["03_remains", 1.0],
		["04_rising", 4.18], ["05_skull_flying", 0.75]]
	for shot in shots:
		await get_tree().create_timer(shot[1]).timeout
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("%s/%s.png" % [dir, shot[0]])
	get_tree().quit()
