extends Node
## 墓园入口（Cemetery Entry）灰盒，按用户的草图搭（Decision Log D-036）：
## 下方小路弯弯曲曲走上来 → 中间铁栏 + 两根门柱夹着大门 → 门里正对喷泉，喷泉两侧小路是出口 →
## 最上方一条雾带，雾里隐约有礼拜堂尖顶。已有的积木直接用，还没有的东西用色块占位并标字。
## 房间两屏半高（960×1350；D-038 原为两屏，2026-10-26 用户要门里更长），镜头只上下跟着主角：开始只看得到路，大门随着往上走慢慢露出来。
## 按键：WASD 走路 · V 切换视角（原版 / 更低）· H 开关占位说明 · T 开关游戏整体色调 · F 全屏
## 顶部的天空、天际线和礼拜堂剪影（D-039）、更高的门柱（D-040）两版都有。“更低的视角”是一版试验：
## 地上平躺的东西压得更扁、路往远处收窄、前景更大。
## 截图：Godot --path . res://scenes/prototypes/cemetery_entry/cemetery_entry_greybox.tscn -- --capture=<目录>
## 换地面试样：-- --plate=<PNG 路径>（960×540）
## 正式地面（2026-10-28，docs/GROUND_TERRAIN_METHOD.md）：场景里的 Ground（Base 底子 / Grass 草地 / Path 路 / Decals 贴花）
## 由用户在编辑器里亲手刷；有了它就不再画旧的色块路和积水。Reference 是一张半透明的房间参考图（物件位置），
## 只在编辑器里看，运行时隐藏。Ground 由 scripts/tools/build_cemetery_entry_ground.gd 第一次生成，之后不再覆盖。
## 参考图：-- --reference=<PNG 路径>（整个房间 960×1350 一张，不含地面）

const HERO_SCENE := preload("res://scenes/player/hero_b1.tscn")
const PROPS := "res://art/cemetery_v3/props/"
const OLD := "../../cemetery_pixel_v1/" # relative to PROPS: old placeholder art (road slabs)
const NATIVE := Vector2i(960, 540)
const SIZE := Vector2i(960, 1350) # 2.5 屏：门里的墓园加长了约半屏（用户 2026-10-26）
const SPAWN := Vector2(485, 1336)

# 铁栏一段宽 160：门柱 → 铁栏 +81，铁栏 → 门柱 +71（props_manifest wall_families.B_ashlar）
const LAYOUT := {
	"id": "cemetery_entry", "seed": 3, "dead_grass": 26, "grass_top": 112, "prop_dir": PROPS, "size": SIZE,
	"props": [
		# 大门与铁栏：两根高门柱是角色组的正式素材（D-040），柱脚处门洞净空 92
		["gate_pillar_tall_01", Vector2(408, 546), null], ["gate_pillar_tall_01", Vector2(552, 546), null],
		["iron_fence_01", Vector2(337, 545), null], ["wall_pillar_01", Vector2(256, 546), null],
		["iron_fence_01", Vector2(185, 545), null], ["wall_pillar_01", Vector2(104, 546), null],
		["iron_fence_01", Vector2(33, 545), null],
		["iron_fence_01", Vector2(633, 545), null], ["wall_pillar_01", Vector2(704, 546), null],
		["iron_fence_01", Vector2(785, 545), null], ["wall_pillar_01", Vector2(856, 546), null],
		["iron_fence_01", Vector2(937, 545), null],
		["grave_lantern_01", Vector2(384, 562), null],
		# 门外靠近大门：路边孤坟、碎石、花瓶
		["tombstone_upright_01_tilted", Vector2(95, 615), null], ["tombstone_cross_01_broken", Vector2(205, 622), null],
		["tombstone_small_01", Vector2(150, 662), null], ["rubble_pile_01", Vector2(260, 665), null],
		["tombstone_small_01", Vector2(735, 622), null], ["grave_vase_01", Vector2(772, 630), null],
		["tombstone_upright_02_broken", Vector2(860, 680), null],
		# 路的中段：墓园外圈的旧乱石墙，塌得只剩几段（以前的墓园比现在大）
		["low_wall_01", Vector2(120, 860), null], ["low_wall_rubble_broken_01", Vector2(268, 860), null],
		["low_wall_rubble_broken_01", Vector2(830, 910), null], ["rubble_pile_01", Vector2(700, 920), null],
		["tombstone_small_01", Vector2(640, 830), null],
		# 路的下段：更孤零零的坟
		["tombstone_cross_01_broken", Vector2(160, 1130), null], ["candles_01", Vector2(196, 1138), null],
		["tombstone_small_01", Vector2(800, 1170), null],
		# 枯树（角色组第 2 步，两种形状交替）；离开路中间，免得挡住视线
		["dead_tree_02", Vector2(318, 750), null], ["dead_tree_03", Vector2(720, 1070), null],
		["dead_tree_03", Vector2(300, 1280), null], ["dead_tree_02", Vector2(880, 1320), null],
		# 大门：左边一扇半开（门轴在左门柱），另一扇倒在门里的地上（位置照角色组的拼装图）
		["iron_gate_leaf_open_01", Vector2(433, 546), null], ["iron_gate_leaf_fallen_01", Vector2(512, 518), null],
		# 门里正中：干涸的喷泉和哀悼天使
		["fountain_dry_01", Vector2(480, 334), null], # = FOUNTAIN,
		# 门外路边：歪倒的路牌、倒下的路灯、穷人坟的木十字架
		["signpost_01", Vector2(560, 1030), null], ["fallen_lamp_post_01", Vector2(642, 1272), null],
		["wooden_cross_01", Vector2(56, 700), null], ["wooden_cross_02", Vector2(752, 1188), null],
	],
}

# 路的左边线，从下往上；右边线 = 左边线 + 路宽（近处宽、远处窄一点）
const ROAD_LEFT := [Vector2(444, 1350), Vector2(426, 1290), Vector2(450, 1230), Vector2(474, 1170), Vector2(452, 1110),
	Vector2(418, 1050), Vector2(426, 990), Vector2(462, 930), Vector2(476, 870), Vector2(448, 810),
	Vector2(428, 752), Vector2(452, 690), Vector2(470, 642), Vector2(440, 592), Vector2(452, 552)]
# 门里的路：从大门笔直走到喷泉前，再分成左右两条，穿过墓碑群通向出口
const FOUNTAIN := Vector2(480, 334) # 门里的正中间，从大门要走一段才到
const AVENUE := [Vector2(452, 540), Vector2(508, 540), Vector2(512, 344), Vector2(448, 344)]
const BRANCH := [Vector2(420, 326), Vector2(376, 266), Vector2(336, 196), Vector2(308, 140), Vector2(298, 100)] # 左边那条的中线，右边左右对称
# 门里两侧铺满墓碑（用现成的积木）：一排一排，避开路和喷泉
const YARD_GRAVES := ["tombstone_upright_01", "tombstone_upright_02", "tombstone_flat_01", "tombstone_pointed_01",
	"tombstone_cross_01", "tombstone_small_01", "tombstone_upright_01", "tombstone_upright_02", "tombstone_small_01",
	"tombstone_upright_01_tilted", "tombstone_cross_01_broken", "tombstone_upright_02_broken", "obelisk_01"]
# 出口在远景条（y 0～100）下沿：小路走进薄雾里
const EXITS := [
	{"zone": Rect2(262, 92, 72, 26), "kind": "combat", "target": "layer1_a", "side": "top", "glyph_at": Vector2(298, 80)},
	{"zone": Rect2(626, 92, 72, 26), "kind": "event", "target": "layer1_b", "side": "top", "glyph_at": Vector2(662, 80)},
]
const BACKDROP := "res://art/cemetery_v3/backdrop/" # 美术组的远景条和前景枯枝

const STONE := Color(0.45, 0.44, 0.42)
const STONE_DARK := Color(0.28, 0.27, 0.26)
const IRON := Color(0.16, 0.15, 0.15)
const MUD_PATH := Color(0.36, 0.30, 0.25)
const WATER := Color(0.34, 0.40, 0.46, 0.85)
const FOG := Color(0.62, 0.66, 0.72)
const HORIZON_FOG := Rect2(0, 24, 960, 210) # from inside the backdrop strip's flat bottom down over the far graves

var _viewport: SubViewport
var _room: CemeteryRoom
var _language: CanvasLayer
var _labels: Node2D
var _camera: Camera2D
var _high: Array[CanvasItem] = [] # placeholders drawn for the current camera angle
var _low: Array[CanvasItem] = [] # the same things drawn as if the camera sat lower (V)
var _low_angle := false
var _exits: Array[Node2D] = []
var _label: Label
var _note := ""
var _font := SystemFont.new() # the default font lacks some Chinese characters
var _painted := false # the user's painted Ground is in use: no colour-block road or puddles


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
	layout.props = LAYOUT.props + yard_graves()
	var placed: Node2D = get_node_or_null("Props") # the user's own arrangement of the blocks
	if placed:
		layout.props = []
		remove_child(placed)
	var reference := get_node_or_null("Reference")
	if reference:
		reference.free() # an editor-only guide to where the props stand
	var painted: Node2D = get_node_or_null("Ground")
	if painted and not "--reference" in str(OS.get_cmdline_user_args()):
		layout.plate_file = "" # the painted ground replaces the old sample plate
		remove_child(painted)
		_viewport.add_child(painted)
		_collect_stray_decals(painted)
	elif painted:
		painted.free()
		painted = null
	if "--reference" in str(OS.get_cmdline_user_args()):
		layout.plate_file = "" # props and placeholders only, on a see-through background
		_viewport.transparent_bg = true
	_painted = painted != null
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--plate="):
			layout.plate_file = arg.get_slice("=", 1)
			if painted:
				painted.visible = false
	_room = CemeteryRoom.new(layout)
	_viewport.add_child(_room)
	if placed:
		_take_placed_props(placed)
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
	elif "--reference" in str(OS.get_cmdline_user_args()):
		_save_reference()


func _process(_delta: float) -> void:
	_follow()
	for exit in _exits:
		exit.check(_room.player)
	var tint := _tint()
	_label.text = "墓园入口 · 灰盒 · WASD 走路 · V 视角：%s · H 占位说明：%s · T 色调：%s · F 全屏%s" % [
		"更低" if _low_angle else "原版", "开" if _labels.visible else "关", "开" if tint.visible else "关",
		("\n" + _note) if _note else ""]


## The hero sits a little below the screen centre, so more of the road ahead shows.
func _follow() -> void:
	_camera.position = Vector2(SIZE.x / 2, _room.player.position.y - 40)


## Everything without art yet: drawn as flat colour shapes, each with a short Chinese note.
func _build_placeholders() -> void:
	var ground := Node2D.new() # flat things: drawn with the bases, under everyone
	ground.z_index = CemeteryProp.BASE_Z
	_room.add_child(ground)
	_room.move_child(ground, 2)
	if not _painted:
		_keep(ground, _poly(road_polygon(), MUD_PATH), _high)
		ground.add_child(_poly(AVENUE, MUD_PATH))
		for side in [1, -1]:
			ground.add_child(_poly(branch_polygon(side), MUD_PATH))
	var slabs := [Vector2(482, 1310), Vector2(470, 1250), Vector2(502, 1200), Vector2(486, 1130), Vector2(458, 1060),
		Vector2(470, 1000), Vector2(500, 938), Vector2(484, 860), Vector2(470, 790), Vector2(492, 688),
		Vector2(505, 650), Vector2(482, 606), Vector2(478, 570), Vector2(480, 520)]
	for i in (0 if _painted else slabs.size()): # old flagstones scattered along the road
		var slab := Sprite2D.new()
		slab.texture = PixelArt.texture(PROPS + OLD + "path/old_slab_%02d.png" % (i % 8 + 1))
		slab.position = slabs[i]
		_keep(ground, slab, _high)
	for p in [] if _painted else [[Vector2(392, 605), Vector2(26, 7)], [Vector2(568, 712), Vector2(20, 6)], [Vector2(380, 970), Vector2(22, 6)],
			[Vector2(560, 1090), Vector2(28, 8)], [Vector2(540, 1280), Vector2(14, 5)], [Vector2(424, 470), Vector2(14, 4)]]:
		_keep(ground, _poly(_ellipse(p[0], p[1]), WATER), _high)
		_keep(ground, _poly(_ellipse(p[0], Vector2(p[1].x * 1.3, maxf(2, p[1].y * 0.45))), WATER), _low)
	# 远景：雾里的礼拜堂尖顶，在地面之上、雾之下
	var far := Node2D.new()
	far.z_index = 41 # just over the thickest fog, so it reads as a dark shape inside the mist
	far.modulate = Color(1, 1, 1, 0.55)
	_room.add_child(far)
	far.visible = false # replaced by the sky and skyline (D-039); kept for comparison
	far.add_child(_poly([Vector2(452, 62), Vector2(452, 34), Vector2(470, 24), Vector2(480, 2), Vector2(490, 24),
		Vector2(508, 34), Vector2(508, 62)], Color(0.20, 0.21, 0.24)))
	far.add_child(_poly([Vector2(420, 62), Vector2(420, 44), Vector2(452, 44), Vector2(452, 62)], Color(0.22, 0.23, 0.26)))
	far.add_child(_poly([Vector2(508, 62), Vector2(508, 46), Vector2(540, 46), Vector2(540, 62)], Color(0.22, 0.23, 0.26)))

	_build_low_angle(ground)
	_set_low_angle(false)

	# 雾带：最上方一条，盖在所有东西上面
	var fog := Node2D.new()
	fog.z_index = 40
	_room.add_child(fog)
	fog.visible = false # replaced by the sky and skyline (D-039)
	for band in [[0, 34, 0.75], [34, 52, 0.5], [52, 68, 0.28], [68, 80, 0.12]]:
		fog.add_child(_poly([Vector2(0, band[0]), Vector2(960, band[0]), Vector2(960, band[1]), Vector2(0, band[1])], Color(FOG, band[2])))

	# 前景：画面最下面两个角伸进来的枯枝
	var fore := Node2D.new()
	fore.z_index = 60
	_keep(_room, fore, _high)
	if FileAccess.file_exists(BACKDROP + "fg_branches_left_01.png"):
		fore.modulate.a = 0.0 # placeholder kept for the V comparison only
		for side in ["left", "right"]:
			var branches := Sprite2D.new()
			branches.texture = PixelArt.texture(BACKDROP + "fg_branches_%s_01.png" % side)
			branches.centered = false
			branches.z_index = 60
			var size := branches.texture.get_size()
			branches.position = Vector2(0 if side == "left" else SIZE.x - size.x, SIZE.y - size.y)
			_room.add_child(branches)
	var branch := Color(0.08, 0.07, 0.06)
	fore.position = Vector2(0, SIZE.y - NATIVE.y) # the branches hang over the start of the road
	fore.add_child(_poly([Vector2(0, 540), Vector2(0, 452), Vector2(22, 470), Vector2(70, 478), Vector2(44, 488), Vector2(118, 512),
		Vector2(66, 510), Vector2(92, 540)], branch))
	fore.add_child(_poly([Vector2(960, 540), Vector2(960, 470), Vector2(930, 492), Vector2(880, 500), Vector2(910, 508), Vector2(850, 530),
		Vector2(900, 528), Vector2(886, 540)], branch))

	# 雾带和出口之外不让走出画面上方
	var top := StaticBody2D.new()
	_room.add_child(top)
	for r in [Rect2(0, 0, 262, 100), Rect2(334, 0, 292, 100), Rect2(698, 0, 262, 100), Rect2(262, 0, 72, 92), Rect2(626, 0, 72, 92)]:
		var block := CollisionShape2D.new()
		var rect := RectangleShape2D.new()
		rect.size = r.size
		block.shape = rect
		block.position = r.get_center()
		top.add_child(block)

	_labels = Node2D.new()
	_labels.z_index = 80
	_room.add_child(_labels)
	for note in [["天空 + 天际线 + 礼拜堂轮廓", Vector2(392, 86)], ["干涸的喷泉 + 哀悼天使", Vector2(372, 340)],
			["出口 → 第 1 层", Vector2(262, 122)], ["出口 → 第 1 层", Vector2(626, 122)],
			["门里两侧：一排排墓碑", Vector2(60, 300)], ["半开的铁门", Vector2(330, 516)],
			["倒下的铁门", Vector2(540, 500)], ["路边孤坟", Vector2(120, 570)],
			["倒下的路灯", Vector2(600, 1276)], ["枯树", Vector2(740, 890)],
			["前景枯枝（占位）", Vector2(8, 1250)], ["泥路（色块占位，正式地面在 Ground 里刷）", Vector2(540, 1170)],
			["外圈旧乱石墙（塌了）", Vector2(110, 870)], ["歪倒的路牌", Vector2(576, 1000)]]:
		var label := Label.new()
		label.text = note[0]
		label.add_theme_font_override("font", _font)
		label.position = note[1]
		label.add_theme_font_size_override("font_size", 9)
		label.add_theme_constant_override("outline_size", 3)
		label.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.8))
		label.add_theme_color_override("font_color", Color(1, 0.92, 0.7))
		_labels.add_child(label)


## The low-angle trial (V): flat things squashed harder, the road narrowing into the distance,
## sky and a skyline at the top, taller gate pillars, bigger foreground. Only placeholders change.
func _build_low_angle(ground: Node2D) -> void:
	var road := PackedVector2Array()
	var right := PackedVector2Array()
	for p: Vector2 in ROAD_LEFT:
		var centre := p.x + lerpf(56, 80, p.y / SIZE.y) / 2.0
		var half := lerpf(16, 50, pow(p.y / SIZE.y, 1.4)) # much narrower far away
		road.append(Vector2(roundf(centre - half), p.y))
		right.append(Vector2(roundf(centre + half), p.y))
	for i in range(right.size() - 1, -1, -1):
		road.append(right[i])
	_keep(ground, _poly(road, MUD_PATH), _low)
	for p in [Vector2(482, 1310), Vector2(470, 1250), Vector2(502, 1200), Vector2(486, 1130), Vector2(458, 1060),
			Vector2(470, 1000), Vector2(500, 938), Vector2(484, 860), Vector2(470, 790), Vector2(492, 688),
			Vector2(505, 650), Vector2(482, 606), Vector2(478, 570)]: # flagstones as thin slivers
		var w := roundf(lerpf(8, 22, p.y / SIZE.y))
		_keep(ground, _poly([p + Vector2(-w, -2), p + Vector2(w, -3), p + Vector2(w + 2, 2), p + Vector2(-w + 2, 3)], STONE), _low)

	# 天空 + 天际线 + 礼拜堂剪影：用户喜欢这一部分的神秘感，两种视角都保留（D-039）
	var sky := Node2D.new()
	sky.z_index = 39
	_room.add_child(sky)
	var backdrop := ""
	for v in ["03", "02", "01"]: # 最新的一版：02 放大礼拜堂，03 修好雾里的底部和屋顶
		if backdrop == "" and FileAccess.file_exists(BACKDROP + "entry_backdrop_%s.png" % v):
			backdrop = BACKDROP + "entry_backdrop_%s.png" % v
	if backdrop != "":
		sky.visible = false # the art group's backdrop strip replaces this placeholder
		var strip := Sprite2D.new()
		strip.texture = PixelArt.texture(backdrop)
		strip.centered = false
		strip.z_index = -9 # behind every prop, just over the ground
		_room.add_child(strip)
	sky.add_child(_poly([Vector2(0, 0), Vector2(960, 0), Vector2(960, 46), Vector2(0, 46)], Color(0.66, 0.68, 0.72)))
	var line := PackedVector2Array([Vector2(0, 70)])
	for x in range(0, 961, 24):
		line.append(Vector2(x, 38 + (x * 7 % 13) - (6 if x % 72 == 0 else 0)))
	line.append(Vector2(960, 70))
	sky.add_child(_poly(line, Color(0.34, 0.36, 0.40)))
	sky.add_child(_poly([Vector2(440, 62), Vector2(440, 26), Vector2(462, 26), Vector2(462, 12), Vector2(472, 12),
		Vector2(480, -0), Vector2(488, 12), Vector2(498, 12), Vector2(498, 26), Vector2(520, 26), Vector2(520, 62)], Color(0.26, 0.27, 0.31)))
	# 地平线的雾：盖住远景条底部平平的一块和地面开始的那条直线，往下慢慢变淡，
	# 罩住最后几排墓碑（越远越朦胧）；下沿起伏、缓慢飘动，不出现直线
	var mist := ColorRect.new()
	mist.position = HORIZON_FOG.position
	mist.size = HORIZON_FOG.size
	mist.z_index = 40
	mist.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var mat := ShaderMaterial.new()
	mat.shader = load("res://scripts/world/v3/horizon_fog.gdshader")
	mat.set_shader_parameter("size", HORIZON_FOG.size)
	mat.set_shader_parameter("fog_color", Color8(76, 82, 90)) # the backdrop strip's own bottom colour
	mist.material = mat
	_room.add_child(mist)

	# 更高的门柱占位：正式素材到了就不用（D-040）
	for x in ([] if ResourceLoader.exists(PROPS + "gate_pillar_tall_01.png") else [408, 552]):
		var pillar := Node2D.new()
		pillar.position = Vector2(x, 542)
		_room.sorted.add_child(pillar)
		pillar.add_child(_poly([Vector2(-20, 0), Vector2(-20, -132), Vector2(20, -132), Vector2(20, 0)], STONE))
		pillar.add_child(_poly([Vector2(8, 0), Vector2(8, -132), Vector2(20, -132), Vector2(20, 0)], STONE_DARK))
		pillar.add_child(_poly([Vector2(-24, -132), Vector2(-24, -142), Vector2(0, -160), Vector2(24, -142), Vector2(24, -132)], STONE_DARK))

	# 更大的前景：枯枝 + 一排高草，压在画面最下面
	var fore := Node2D.new()
	fore.z_index = 60
	fore.position = Vector2(0, SIZE.y - NATIVE.y)
	_keep(_room, fore, _low)
	var dark := Color(0.06, 0.05, 0.05)
	fore.add_child(_poly([Vector2(0, 540), Vector2(0, 400), Vector2(40, 430), Vector2(120, 440), Vector2(70, 458), Vector2(190, 500),
		Vector2(100, 498), Vector2(150, 540)], dark))
	fore.add_child(_poly([Vector2(960, 540), Vector2(960, 420), Vector2(910, 452), Vector2(820, 462), Vector2(870, 476), Vector2(760, 520),
		Vector2(850, 518), Vector2(820, 540)], dark))
	for x in range(0, 960, 9):
		if x > 380 and x < 590:
			continue # keep the road clear
		var h := 14 + (x * 13 % 23)
		fore.add_child(_poly([Vector2(x, 540), Vector2(x + 3, 540 - h), Vector2(x + 6, 540)], dark))


## Rows of graves filling both sides of the yard, kept off the avenue, the fountain and the two paths.
## Only the first arrangement: once the scene has a Props node, the user's blocks are used instead.
static func yard_graves() -> Array:
	var rng := RandomNumberGenerator.new()
	rng.seed = 7
	var graves := []
	var row := 0
	for y in range(150, 520, 58):
		for x in range(36 + (row % 2) * 31, 940, 62):
			var p := Vector2(x + rng.randi_range(-8, 8), y + rng.randi_range(-6, 6))
			var name: String = YARD_GRAVES[rng.randi() % YARD_GRAVES.size()]
			if rng.randf() < 0.14 or near_paths(p):
				continue # a few gaps, like graves that were never dug
			graves.append([name, p, null])
		row += 1
	return graves


static func near_paths(p: Vector2) -> bool:
	if absf(p.x - FOUNTAIN.x) < 120 and p.y > FOUNTAIN.y - 130 and p.y < FOUNTAIN.y + 40:
		return true
	if absf(p.x - FOUNTAIN.x) < 74 and p.y > FOUNTAIN.y:
		return true
	if absf(p.x - FOUNTAIN.x) < 96 and p.y < 236:
		return true # 从大门望过去，礼拜堂不被墓碑挡住
	for side in [1, -1]:
		for i in BRANCH.size() - 1:
			var a := _mirror(BRANCH[i], side)
			var b := _mirror(BRANCH[i + 1], side)
			if p.distance_to(Geometry2D.get_closest_point_to_segment(p, a, b)) < 46:
				return true
	return false


static func _mirror(p: Vector2, side: int) -> Vector2:
	return p if side == 1 else Vector2(SIZE.x - p.x, p.y)


## The road from the bottom of the room up to the gate: wider near the viewer, a little narrower far away.
static func road_polygon() -> PackedVector2Array:
	var road := PackedVector2Array(ROAD_LEFT)
	for i in range(ROAD_LEFT.size() - 1, -1, -1):
		var p: Vector2 = ROAD_LEFT[i]
		road.append(p + Vector2(roundf(lerpf(56, 80, p.y / SIZE.y)), 0))
	return road


## The path along BRANCH, 40 px wide.
static func branch_polygon(side: int) -> PackedVector2Array:
	var left := PackedVector2Array()
	var right := PackedVector2Array()
	for p: Vector2 in BRANCH:
		left.append(_mirror(p + Vector2(-20, 0), side))
		right.append(_mirror(p + Vector2(20, 0), side))
	right.reverse()
	return left + right


func _keep(parent: Node, item: CanvasItem, variant: Array[CanvasItem]) -> CanvasItem:
	parent.add_child(item)
	variant.append(item)
	return item


func _set_low_angle(low: bool) -> void:
	_low_angle = low
	for item in _high:
		item.visible = not low
	for item in _low:
		item.visible = low


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
	if event.physical_keycode == KEY_V:
		_set_low_angle(not _low_angle)
	elif event.physical_keycode == KEY_H:
		_labels.visible = not _labels.visible
	elif event.physical_keycode == KEY_T:
		_tint().visible = not _tint().visible
	elif event.physical_keycode == KEY_F:
		var win := get_window()
		win.mode = Window.MODE_WINDOWED if win.mode == Window.MODE_FULLSCREEN else Window.MODE_FULLSCREEN


## Decals dragged onto the scene root instead of Ground/Decals would never be drawn (the root is
## not in the viewport); move them where they belong, keeping their place.
## The blocks the user placed under Props (and any dropped on the scene root by mistake) join the
## room's Y-sorted layer, so they sort, fade and collide like the props the layout builds.
func _take_placed_props(placed: Node2D) -> void:
	for child in get_children():
		if child is CemeteryProp:
			child.reparent(placed)
	for prop in placed.get_children():
		prop.reparent(_room.sorted)
	placed.free()


func _collect_stray_decals(ground: Node2D) -> void:
	var decals: Node2D = ground.get_node_or_null("Decals")
	if decals == null:
		return
	for child in get_children():
		if child is Sprite2D:
			child.reparent(decals)


## The whole room in one picture, without the painted ground: the editor guide for painting.
func _save_reference() -> void:
	var path := ""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--reference="):
			path = arg.get_slice("=", 1)
	_labels.visible = true
	_tint().visible = false
	_room.player.visible = false
	_viewport.size = SIZE
	_camera.position = Vector2(SIZE) / 2
	_camera.reset_smoothing()
	set_process(false)
	for i in 30:
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	_viewport.get_texture().get_image().save_png(path)
	get_tree().quit()


func _capture() -> void:
	var dir := ""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--capture="):
			dir = arg.get_slice("=", 1)
	DirAccess.make_dir_recursive_absolute(dir)
	var hero: Node2D = _room.player
	_labels.visible = "--labels" in str(OS.get_cmdline_user_args())
	for shot in [["01_arrive", SPAWN, false], ["02_gate", Vector2(480, 600), false],
			["03_arrive_low", SPAWN, true], ["04_gate_low", Vector2(480, 600), true],
			["05_fountain", Vector2(480, 470), false], ["06_yard_top", Vector2(330, 200), false]]:
		_set_low_angle(shot[2])
		hero.position = shot[1]
		_follow()
		_camera.reset_smoothing()
		for i in 40:
			await get_tree().process_frame
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("%s/%s.png" % [dir, shot[0]])
	get_tree().quit()
