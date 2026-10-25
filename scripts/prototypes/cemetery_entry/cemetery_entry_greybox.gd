extends Node
## 墓园入口（Cemetery Entry）灰盒，按用户的草图搭（Decision Log D-036）：
## 下方小路弯弯曲曲走上来 → 中间铁栏 + 两根门柱夹着大门 → 门里正对喷泉，喷泉两侧小路是出口 →
## 最上方一条雾带，雾里隐约有礼拜堂尖顶。已有的积木直接用，还没有的东西用色块占位并标字。
## 房间两屏高（960×1080，D-038），镜头只上下跟着主角：开始只看得到路，大门随着往上走慢慢露出来。
## 按键：WASD 走路 · H 开关占位说明 · T 开关游戏整体色调 · F 全屏
## 截图：Godot --path . res://scenes/prototypes/cemetery_entry/cemetery_entry_greybox.tscn -- --capture=<目录>
## 换地面试样：-- --plate=<PNG 路径>（960×540）

const HERO_SCENE := preload("res://scenes/player/hero_b1.tscn")
const PROPS := "res://art/cemetery_v3/props/"
const OLD := "../../cemetery_pixel_v1/" # relative to PROPS: old placeholder art (dead tree, slabs)
const NATIVE := Vector2i(960, 540)
const SIZE := Vector2i(960, 1080)
const SPAWN := Vector2(485, 1066)

# 铁栏一段宽 160：门柱 → 铁栏 +81，铁栏 → 门柱 +71（props_manifest wall_families.B_ashlar）
const LAYOUT := {
	"id": "cemetery_entry", "seed": 3, "dead_grass": 26, "prop_dir": PROPS, "size": SIZE,
	"props": [
		# 大门与铁栏（门柱以后要换成更高的新素材）
		["wall_pillar_01", Vector2(428, 276), null], ["wall_pillar_01", Vector2(532, 276), null],
		["iron_fence_01", Vector2(357, 275), null], ["wall_pillar_01", Vector2(276, 276), null],
		["iron_fence_01", Vector2(205, 275), null], ["wall_pillar_01", Vector2(124, 276), null],
		["iron_fence_01", Vector2(53, 275), null],
		["iron_fence_01", Vector2(613, 275), null], ["wall_pillar_01", Vector2(684, 276), null],
		["iron_fence_01", Vector2(765, 275), null], ["wall_pillar_01", Vector2(836, 276), null],
		["iron_fence_01", Vector2(917, 275), null],
		["grave_lantern_01", Vector2(404, 292), null],
		# 门里：隔着铁栏看到的墓碑
		["tombstone_upright_01", Vector2(70, 150), null], ["tombstone_flat_01", Vector2(155, 132), null],
		["tombstone_pointed_01", Vector2(225, 168), null], ["tombstone_cross_01", Vector2(110, 228), null],
		["tombstone_upright_02", Vector2(200, 240), null], ["tombstone_small_01", Vector2(290, 236), null],
		["tombstone_cross_01", Vector2(760, 132), null], ["obelisk_01", Vector2(880, 168), null],
		["tombstone_upright_02", Vector2(700, 210), null], ["tombstone_upright_01_tilted", Vector2(830, 240), null],
		["tombstone_small_01", Vector2(760, 238), null], ["tombstone_flat_01", Vector2(905, 250), null],
		# 门外靠近大门：路边孤坟、碎石、花瓶
		["tombstone_upright_01_tilted", Vector2(95, 345), null], ["tombstone_cross_01_broken", Vector2(205, 352), null],
		["tombstone_small_01", Vector2(150, 392), null], ["rubble_pile_01", Vector2(260, 395), null],
		["tombstone_small_01", Vector2(735, 352), null], ["grave_vase_01", Vector2(772, 360), null],
		["tombstone_upright_02_broken", Vector2(860, 410), null],
		# 路的中段：墓园外圈的旧乱石墙，塌得只剩几段（以前的墓园比现在大）
		["low_wall_01", Vector2(120, 590), null], ["low_wall_rubble_broken_01", Vector2(268, 590), null],
		["low_wall_rubble_broken_01", Vector2(830, 640), null], ["rubble_pile_01", Vector2(700, 650), null],
		["tombstone_small_01", Vector2(640, 560), null],
		# 路的下段：更孤零零的坟
		["tombstone_cross_01_broken", Vector2(160, 860), null], ["candles_01", Vector2(196, 868), null],
		["tombstone_small_01", Vector2(800, 900), null],
		# 枯树（旧样板素材占位，比主角高一倍，以后要新画）；离开路中间，免得挡住视线
		[OLD + "props/dead_tree_01", Vector2(318, 480), null],
		[OLD + "props/dead_tree_01", Vector2(720, 800), null],
		[OLD + "props/dead_tree_01", Vector2(300, 1010), null],
		[OLD + "props/dead_tree_01", Vector2(880, 1050), null],
	],
}

# 路的左边线，从下往上；右边线 = 左边线 + 路宽（近处宽、远处窄一点）
const ROAD_LEFT := [Vector2(444, 1080), Vector2(426, 1020), Vector2(450, 960), Vector2(474, 900), Vector2(452, 840),
	Vector2(418, 780), Vector2(426, 720), Vector2(462, 660), Vector2(476, 600), Vector2(448, 540),
	Vector2(428, 482), Vector2(452, 420), Vector2(470, 372), Vector2(440, 322), Vector2(452, 282)]
# 门里的路：从大门到喷泉前，再分成左右两条通向出口
const INNER_PATHS := [
	[Vector2(452, 270), Vector2(508, 270), Vector2(512, 232), Vector2(448, 232)],
	[Vector2(420, 200), Vector2(400, 168), Vector2(330, 110), Vector2(318, 66), Vector2(278, 66), Vector2(290, 116), Vector2(372, 196), Vector2(410, 232)],
	[Vector2(540, 200), Vector2(560, 168), Vector2(630, 110), Vector2(642, 66), Vector2(682, 66), Vector2(670, 116), Vector2(588, 196), Vector2(550, 232)],
]
const EXITS := [
	{"zone": Rect2(262, 40, 72, 30), "kind": "combat", "target": "layer1_a", "side": "top", "glyph_at": Vector2(298, 26)},
	{"zone": Rect2(626, 40, 72, 30), "kind": "event", "target": "layer1_b", "side": "top", "glyph_at": Vector2(662, 26)},
]

const STONE := Color(0.45, 0.44, 0.42)
const STONE_DARK := Color(0.28, 0.27, 0.26)
const IRON := Color(0.16, 0.15, 0.15)
const MUD_PATH := Color(0.36, 0.30, 0.25)
const WATER := Color(0.34, 0.40, 0.46, 0.85)
const FOG := Color(0.62, 0.66, 0.72)

var _viewport: SubViewport
var _room: CemeteryRoom
var _language: CanvasLayer
var _labels: Node2D
var _camera: Camera2D
var _exits: Array[Node2D] = []
var _label: Label
var _note := ""
var _font := SystemFont.new() # the default font lacks some Chinese characters


func _ready() -> void:
	_font.font_names = PackedStringArray(["PingFang SC", "Hiragino Sans GB", "Heiti SC"])
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
	_build_placeholders()
	var hero := HERO_SCENE.instantiate()
	hero.position = SPAWN
	_room.sorted.add_child(hero)
	hero.face_direction(Vector2.UP)
	_room.player = hero
	# Vertical-only follow: the left and right edges never move, only the road scrolls (D-038).
	_camera = Camera2D.new()
	_camera.limit_left = 0
	_camera.limit_right = SIZE.x
	_camera.limit_top = 0
	_camera.limit_bottom = SIZE.y
	_camera.position_smoothing_enabled = true
	_camera.position_smoothing_speed = 4.0
	_room.add_child(_camera)
	_camera.make_current()
	_follow()
	_camera.reset_smoothing()
	_language = CanvasLayer.new()
	_language.layer = 5
	_language.follow_viewport_enabled = true # exit glyphs scroll with the world
	_viewport.add_child(_language)
	for data in EXITS:
		var exit: Node2D = load("res://scripts/world/v3/room_exit.gd").new()
		_room.add_child(exit)
		exit.setup(data, _language)
		exit.enabled = true
		exit.taken.connect(func(e): _note = "出口：%s（灰盒里不切换房间）" % ("去第 1 层 · 战斗" if e.kind == "combat" else "去第 1 层 · 事件"))
		_exits.append(exit)
	var screen := TextureRect.new()
	screen.texture = _viewport.get_texture()
	screen.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	screen.size = Vector2(NATIVE)
	add_child(screen)
	_label = Label.new()
	_label.add_theme_font_override("font", _font)
	_label.position = Vector2(8, NATIVE.y - 40) # bottom: the exit glyphs live at the top
	_label.add_theme_font_size_override("font_size", 11)
	_label.add_theme_constant_override("outline_size", 3)
	_label.add_theme_color_override("font_outline_color", Color.BLACK)
	add_child(_label)
	if "--capture" in str(OS.get_cmdline_user_args()):
		_capture()


func _process(_delta: float) -> void:
	_follow()
	for exit in _exits:
		exit.check(_room.player)
	var tint := _tint()
	_label.text = "墓园入口 · 灰盒 · WASD 走路 · H 占位说明：%s · T 色调：%s · F 全屏%s" % [
		"开" if _labels.visible else "关", "开" if tint.visible else "关", ("\n" + _note) if _note else ""]


## The hero sits a little below the screen centre, so more of the road ahead shows.
func _follow() -> void:
	_camera.position = Vector2(SIZE.x / 2, _room.player.position.y - 40)


## Everything without art yet: drawn as flat colour shapes, each with a short Chinese note.
func _build_placeholders() -> void:
	var ground := Node2D.new() # flat things: drawn with the bases, under everyone
	ground.z_index = CemeteryProp.BASE_Z
	_room.add_child(ground)
	_room.move_child(ground, 2)
	var road := ROAD_LEFT.duplicate()
	for i in range(ROAD_LEFT.size() - 1, -1, -1):
		var p: Vector2 = ROAD_LEFT[i]
		road.append(p + Vector2(roundf(lerpf(56, 80, p.y / SIZE.y)), 0))
	ground.add_child(_poly(road, MUD_PATH))
	for path in INNER_PATHS:
		ground.add_child(_poly(path, MUD_PATH))
	var slabs := [Vector2(482, 1040), Vector2(470, 980), Vector2(502, 930), Vector2(486, 860), Vector2(458, 790),
		Vector2(470, 730), Vector2(500, 668), Vector2(484, 590), Vector2(470, 520), Vector2(492, 418),
		Vector2(505, 380), Vector2(482, 336), Vector2(478, 300), Vector2(480, 250)]
	for i in slabs.size(): # old flagstones scattered along the road
		var slab := Sprite2D.new()
		slab.texture = PixelArt.texture(PROPS + OLD + "path/old_slab_%02d.png" % (i % 8 + 1))
		slab.position = slabs[i]
		ground.add_child(slab)
	for p in [[Vector2(392, 335), Vector2(26, 7)], [Vector2(568, 442), Vector2(20, 6)], [Vector2(380, 700), Vector2(22, 6)],
			[Vector2(560, 820), Vector2(28, 8)], [Vector2(540, 1010), Vector2(14, 5)], [Vector2(330, 150), Vector2(16, 5)]]:
		ground.add_child(_poly(_ellipse(p[0], p[1]), WATER))
	# 倒下的那扇铁门，平躺在门内地上
	ground.add_child(_poly([Vector2(500, 286), Vector2(552, 290), Vector2(546, 302), Vector2(494, 298)], IRON))
	# 倒下的路灯（只剩一截灯杆）
	ground.add_child(_poly([Vector2(600, 996), Vector2(682, 976), Vector2(684, 980), Vector2(602, 1000)], IRON))
	ground.add_child(_poly(_ellipse(Vector2(687, 977), Vector2(5, 4)), IRON))
	# 歪倒的路牌：一根木桩 + 一块牌子（立着的东西，参与前后遮挡）
	var sign_post := Node2D.new()
	sign_post.position = Vector2(560, 760)
	_room.sorted.add_child(sign_post)
	sign_post.add_child(_poly([Vector2(-2, 0), Vector2(-6, -44), Vector2(-2, -44), Vector2(2, 0)], Color(0.30, 0.22, 0.16)))
	sign_post.add_child(_poly([Vector2(-22, -42), Vector2(12, -36), Vector2(12, -26), Vector2(-22, -32)], Color(0.38, 0.29, 0.21)))

	# 远景：雾里的礼拜堂尖顶，在地面之上、雾之下
	var far := Node2D.new()
	far.z_index = 41 # just over the thickest fog, so it reads as a dark shape inside the mist
	far.modulate = Color(1, 1, 1, 0.55)
	_room.add_child(far)
	far.add_child(_poly([Vector2(452, 62), Vector2(452, 34), Vector2(470, 24), Vector2(480, 2), Vector2(490, 24),
		Vector2(508, 34), Vector2(508, 62)], Color(0.20, 0.21, 0.24)))
	far.add_child(_poly([Vector2(420, 62), Vector2(420, 44), Vector2(452, 44), Vector2(452, 62)], Color(0.22, 0.23, 0.26)))
	far.add_child(_poly([Vector2(508, 62), Vector2(508, 46), Vector2(540, 46), Vector2(540, 62)], Color(0.22, 0.23, 0.26)))

	# 喷泉：参与前后遮挡，有碰撞
	var fountain := StaticBody2D.new()
	fountain.position = Vector2(480, 222)
	_room.sorted.add_child(fountain)
	fountain.add_child(_poly(_ellipse(Vector2(0, -26), Vector2(70, 24)), STONE))
	fountain.add_child(_poly(_ellipse(Vector2(0, -30), Vector2(58, 17)), Color(0.22, 0.24, 0.26)))
	fountain.add_child(_poly([Vector2(-8, -34), Vector2(-8, -88), Vector2(0, -98), Vector2(8, -88), Vector2(8, -34)], STONE_DARK))
	var shape := CollisionPolygon2D.new()
	shape.polygon = _ellipse(Vector2(0, -24), Vector2(68, 20))
	fountain.add_child(shape)

	# 半开的那扇铁门：从左门柱斜着打开
	var leaf := Node2D.new()
	leaf.position = Vector2(470, 268)
	_room.sorted.add_child(leaf)
	leaf.add_child(_poly([Vector2(-22, 2), Vector2(-22, -48), Vector2(6, -60), Vector2(6, -10)], Color(IRON, 0.9)))

	# 雾带：最上方一条，盖在所有东西上面
	var fog := Node2D.new()
	fog.z_index = 40
	_room.add_child(fog)
	for band in [[0, 34, 0.75], [34, 52, 0.5], [52, 68, 0.28], [68, 80, 0.12]]:
		fog.add_child(_poly([Vector2(0, band[0]), Vector2(960, band[0]), Vector2(960, band[1]), Vector2(0, band[1])], Color(FOG, band[2])))

	# 前景：画面最下面两个角伸进来的枯枝
	var fore := Node2D.new()
	fore.z_index = 60
	_room.add_child(fore)
	var branch := Color(0.08, 0.07, 0.06)
	fore.position = Vector2(0, SIZE.y - NATIVE.y) # the branches hang over the start of the road
	fore.add_child(_poly([Vector2(0, 540), Vector2(0, 452), Vector2(22, 470), Vector2(70, 478), Vector2(44, 488), Vector2(118, 512),
		Vector2(66, 510), Vector2(92, 540)], branch))
	fore.add_child(_poly([Vector2(960, 540), Vector2(960, 470), Vector2(930, 492), Vector2(880, 500), Vector2(910, 508), Vector2(850, 530),
		Vector2(900, 528), Vector2(886, 540)], branch))

	# 雾带和出口之外不让走出画面上方
	var top := StaticBody2D.new()
	_room.add_child(top)
	for r in [Rect2(0, 0, 262, 70), Rect2(334, 0, 292, 70), Rect2(698, 0, 262, 70)]:
		var block := CollisionShape2D.new()
		var rect := RectangleShape2D.new()
		rect.size = r.size
		block.shape = rect
		block.position = r.get_center()
		top.add_child(block)

	_labels = Node2D.new()
	_labels.z_index = 80
	_room.add_child(_labels)
	for note in [["雾带 + 礼拜堂的影子（以后做）", Vector2(516, 64)], ["喷泉（占位，建议干涸 + 残缺天使像）", Vector2(372, 228)],
			["出口 → 第 1 层", Vector2(262, 72)], ["出口 → 第 1 层", Vector2(626, 72)],
			["门柱（要更高的新素材）", Vector2(540, 196)], ["半开的铁门（占位）", Vector2(330, 246)],
			["倒下的铁门（占位）", Vector2(556, 292)], ["路边孤坟", Vector2(120, 300)],
			["倒下的路灯（占位）", Vector2(600, 1006)], ["枯树（旧素材占位）", Vector2(740, 620)],
			["前景枯枝（占位）", Vector2(8, 980)], ["泥路（以后换地面贴花）", Vector2(540, 900)],
			["外圈旧乱石墙（塌了）", Vector2(110, 600)], ["歪倒的路牌（占位）", Vector2(576, 730)]]:
		var label := Label.new()
		label.text = note[0]
		label.add_theme_font_override("font", _font)
		label.position = note[1]
		label.add_theme_font_size_override("font_size", 9)
		label.add_theme_constant_override("outline_size", 3)
		label.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.8))
		label.add_theme_color_override("font_color", Color(1, 0.92, 0.7))
		_labels.add_child(label)


func _poly(points: Array, color: Color) -> Polygon2D:
	var poly := Polygon2D.new()
	poly.polygon = PackedVector2Array(points)
	poly.color = color
	return poly


func _ellipse(center: Vector2, radius: Vector2) -> PackedVector2Array:
	var pts := PackedVector2Array()
	for k in 24:
		var t := TAU * k / 24.0
		pts.append((center + Vector2(cos(t), sin(t)) * radius).round())
	return pts


func _tint() -> CanvasModulate:
	for child in _room.get_children():
		if child is CanvasModulate:
			return child
	return null


func _unhandled_key_input(event: InputEvent) -> void:
	if not event.is_pressed() or event.is_echo():
		return
	if event.physical_keycode == KEY_H:
		_labels.visible = not _labels.visible
	elif event.physical_keycode == KEY_T:
		_tint().visible = not _tint().visible
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
	for shot in [["01_arrive", SPAWN], ["02_halfway", Vector2(470, 720)], ["03_gate", Vector2(480, 330)],
			["04_fountain", Vector2(380, 214)], ["05_no_labels", Vector2(480, 330)]]:
		if shot[0] == "05_no_labels":
			_labels.visible = false
		hero.position = shot[1]
		_follow()
		_camera.reset_smoothing()
		for i in 40:
			await get_tree().process_frame
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("%s/%s.png" % [dir, shot[0]])
	get_tree().quit()
