extends Node
## 骷髅 B「余裹者」动画试看（docs/SKELETON_ANIMATION_REQUEST.md）：在墓地地面上按游戏大小播放角色组交来的动画。
## 上面一只按 50 px/秒 来回走过墓碑之间（目前只有右侧行走，走到头直接回到左边）；
## 下面一只站着，按空格散架，落成骨堆后停 2 秒再站回来（重组还没做，直接跳回站姿）。
## 主角站在旁边作比例参照。按键：空格 散架 · T 开关游戏整体色调 · F 全屏
## 截图：Godot --path . res://scenes/prototypes/skeleton_anim/skeleton_anim_preview.tscn -- --capture=<目录>

const HERO_SCENE := preload("res://scenes/player/hero_b1.tscn")
const PROPS := "res://art/cemetery_v3/props/"
const SKELETON := "res://art/character_design/enemies/skeleton/"
const ANIM := SKELETON + "anim/"
const NATIVE := Vector2i(960, 540)
const WALK_SPEED := 50.0
const WALK_Y := 250.0
const SHADOW := Color(0.03, 0.03, 0.05, 0.45)
const LAYOUT := {
	"id": "skeleton_anim", "seed": 11, "dead_grass": 10, "prop_dir": PROPS,
	"props": [
		["tombstone_upright_01", Vector2(150, 200), null], ["tombstone_cross_01", Vector2(330, 196), null],
		["tombstone_pointed_01", Vector2(560, 204), null], ["obelisk_01", Vector2(780, 198), null],
		["tombstone_small_01", Vector2(250, 330), null], ["tombstone_upright_02", Vector2(690, 336), null],
		["open_grave_01", Vector2(820, 500), null], ["tombstone_flat_01", Vector2(160, 480), null],
	],
}

var _viewport: SubViewport
var _room: CemeteryRoom
var _walker: Node2D
var _faller: SpriteStrip
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
	hero.position = Vector2(400, 420)
	_room.sorted.add_child(hero)
	hero.face_direction(Vector2.RIGHT)
	_room.player = hero

	_walker = _actor(Vector2(60, WALK_Y), "skeleton_B_walk_right")
	_faller = _actor(Vector2(520, 430), "skeleton_B_collapse_front").get_node("Strip")
	_faller.playing = false
	_faller.finished.connect(_stand_up_later)

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
	_label.text = "骷髅动画试看 · 上：右侧行走 50 px/秒 · 下：空格 散架 · T 色调 · F 全屏"
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
	strip.load_strip(ANIM, anim)
	return root


func _process(delta: float) -> void:
	_walker.position.x += WALK_SPEED * delta
	if _walker.position.x > NATIVE.x + 40:
		_walker.position.x = -40.0


func _collapse() -> void:
	if not _faller.playing:
		_faller.restart()


func _stand_up_later() -> void:
	await get_tree().create_timer(2.0).timeout
	_faller.frame = 0


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
	elif event.physical_keycode == KEY_T:
		_tint().visible = not _tint().visible
	elif event.physical_keycode == KEY_F:
		var win := get_window()
		win.mode = Window.MODE_WINDOWED if win.mode == Window.MODE_FULLSCREEN else Window.MODE_FULLSCREEN


## Saves a few moments: the walker mid-stride and the collapse at its start, middle and end.
func _capture() -> void:
	var dir := ""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--capture="):
			dir = arg.get_slice("=", 1)
	DirAccess.make_dir_recursive_absolute(dir)
	_walker.position.x = 420.0
	for i in 20:
		await get_tree().process_frame
	_collapse()
	for shot in [["01_start", 0.05], ["02_falling", 0.4], ["03_down", 0.7]]:
		await get_tree().create_timer(shot[1]).timeout
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("%s/%s.png" % [dir, shot[0]])
	get_tree().quit()
