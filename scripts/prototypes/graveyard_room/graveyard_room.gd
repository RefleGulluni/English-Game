extends Node
## Broken Graveyard validation room — batch 2 pixel assets (art/cemetery_pixel_v1).
##
## Native 960x540 world in a SubViewport, shown at an integer scale with nearest filtering.
## Three ground modes share the same props, player and language layer:
##   Tiles  — dual-grid terrain (mud/grass, mud/puddle) + decals + loose path slabs
##   Plate  — the AI ground decoration plate (flat only)
##   Target — the whole-scene visual target (reference; props hidden because they are baked in)
##
## Keys: WASD / arrows move · T ground mode · G grounding · L language · O player outline · F fullscreen · H help
## Capture mode: Godot --path . res://scenes/prototypes/graveyard_room/graveyard_room.tscn -- --capture=<abs dir>

const LanguageSigil := preload("res://scripts/prototypes/pixel_room/language_sigil.gd")

const ART := "res://art/cemetery_pixel_v1/"
const HERO := "res://art/character_design/" # B1 four-direction still poses
const NATIVE := Vector2i(960, 540)
const CELL := 32
const GRID := Vector2i(30, 17) # logic cells; display cells sit half a cell offset
const MODES := ["Tiles (dual-grid + decals)", "Plate (AI ground plate)", "Target (visual target, reference)"]
const SHADOW_COLOR := Color(0.03, 0.03, 0.05, 0.45)
const WALK_SPEED := 70.0
const PLAYER_START := Vector2(340, 400)

# Prop layout follows the visual target so all three modes line up.
# [file, origin, collision rect (x, y, w, h) relative to origin — from props/NOTES.md, optional: ellipse]
const PROPS := [
	["dead_tree_01", Vector2(185, 222), Rect2(-52, -48, 104, 46), true], # ellipse over the roots; rects are relative to the PNG origin
	["tombstone_upright_01", Vector2(322, 170), Rect2(-32, -15, 44, 15)],
	["tombstone_upright_01", Vector2(578, 92), Rect2(-32, -15, 44, 15)],
	["tombstone_fragment_01", Vector2(645, 124), Rect2(-24, -28, 48, 28)],
	["tombstone_upright_01", Vector2(892, 272), Rect2(-32, -15, 44, 15)],
	["open_grave_01", Vector2(815, 328), Rect2(-40, -64, 96, 64)],
	["tombstone_upright_01", Vector2(82, 444), Rect2(-32, -15, 44, 15)],
	["tombstone_tilted_01", Vector2(205, 492), Rect2(-32, -18, 48, 18)],
]
const SIGIL_PROP := 5 # hovers over the open grave
# 1 px dark outline around the player, so they read clearly against props of similar colour.
const OUTLINE_SHADER := """
shader_type canvas_item;
uniform bool enabled = true;
uniform vec4 outline_color : source_color = vec4(0.06, 0.05, 0.07, 1.0);
void fragment() {
	vec4 c = texture(TEXTURE, UV);
	if (enabled && c.a < 0.5) {
		vec2 px = TEXTURE_PIXEL_SIZE;
		float n = texture(TEXTURE, UV + vec2(px.x, 0.0)).a + texture(TEXTURE, UV - vec2(px.x, 0.0)).a
			+ texture(TEXTURE, UV + vec2(0.0, px.y)).a + texture(TEXTURE, UV - vec2(0.0, px.y)).a;
		if (n > 0.5) {
			c = outline_color;
		}
	}
	COLOR = c;
}
"""
const FADE_ALPHA := 0.45 # whole tall prop (upright part + its ground base) when the player is behind it
# Old path, following the plate's path: once laid in a line, now with gaps.
const PATH := [Vector2(10, 528), Vector2(150, 452), Vector2(300, 345), Vector2(380, 232),
	Vector2(470, 140), Vector2(620, 72), Vector2(760, 58), Vector2(880, 12)]

var mode := 1 # ground plate: the chosen production approach
var grounding := true
var show_language := true
var outline := false # user preferred no outline (2026-10-22); O toggles it for comparison

var _viewport: SubViewport
var _screen: TextureRect
var _world: Node2D
var _ground: Sprite2D
var _ground_textures: Array[Texture2D] = []
var _tile_extras: Node2D # decals + path slabs, only shown with tiles
var _bases: Node2D # ground bases + dead grass: flat, always under every actor
var _props: Array[Node2D] = []
var _player: CharacterBody2D
var _player_sprite: AnimatedSprite2D
var _facing := "front"
var _shadows: Array[Sprite2D] = []
var _modulate: CanvasModulate
var _light: PointLight2D
var _lang_vp: SubViewport
var _lang_screen: TextureRect
var _sigil: Control
var _hud: Label
var _scale := 2
var _rng := RandomNumberGenerator.new()


func _ready() -> void:
	get_window().content_scale_mode = Window.CONTENT_SCALE_MODE_DISABLED
	get_window().size_changed.connect(_apply)
	_rng.seed = 11

	_viewport = SubViewport.new()
	_viewport.size = NATIVE
	_viewport.canvas_item_default_texture_filter = Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_NEAREST
	_viewport.snap_2d_transforms_to_pixel = true
	_viewport.snap_2d_vertices_to_pixel = true
	add_child(_viewport)
	_world = Node2D.new()
	_viewport.add_child(_world)

	_ground_textures = [_build_tile_ground(), _tex("plates/ground_plate_960x540"), _tex("source/visual_target_960x540")]
	_ground = Sprite2D.new()
	_ground.centered = false
	_world.add_child(_ground)
	_tile_extras = Node2D.new()
	_world.add_child(_tile_extras)
	_scatter_decals()
	_lay_path()
	_bases = Node2D.new()
	_world.add_child(_bases)
	_scatter_dead_grass()

	var sorted := Node2D.new()
	sorted.y_sort_enabled = true # every node's origin is its ground contact point
	_world.add_child(sorted)
	for p in PROPS:
		var base: Sprite2D = null
		if FileAccess.file_exists(ART + "props/" + p[0] + "_base.png"):
			base = Sprite2D.new()
			base.texture = _tex("props/" + p[0] + "_base")
			base.offset = Vector2(0, -base.texture.get_height() / 2)
			base.position = p[1] # same world origin as its prop
			_bases.add_child(base)
		var prop := _make_prop(p[0], p[2], p.size() > 3 and p[3], base)
		prop.position += p[1] # _make_prop may already lift the node to the trunk base
		sorted.add_child(prop)
		_props.append(prop)
	_player = _make_player()
	_player.position = PLAYER_START
	sorted.add_child(_player)
	_add_room_bounds()

	_modulate = CanvasModulate.new()
	_modulate.color = Color(0.8, 0.84, 0.92)
	_world.add_child(_modulate)

	_screen = TextureRect.new()
	_screen.texture = _viewport.get_texture()
	_screen.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_screen.stretch_mode = TextureRect.STRETCH_SCALE
	add_child(_screen)

	# Language layer: same pixel size as the world (chosen 2026-10-22), unaffected by world lighting.
	_lang_vp = SubViewport.new()
	_lang_vp.transparent_bg = true
	_lang_vp.canvas_item_default_texture_filter = Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_NEAREST
	add_child(_lang_vp)
	_lang_screen = TextureRect.new()
	_lang_screen.texture = _lang_vp.get_texture()
	_lang_screen.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_lang_screen.stretch_mode = TextureRect.STRETCH_SCALE
	_lang_screen.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_lang_screen)
	_sigil = LanguageSigil.new()
	_sigil.antialias = false
	_sigil.radius = 30.0
	_lang_vp.add_child(_sigil)

	_hud = Label.new()
	_hud.add_theme_color_override("font_color", Color(0.85, 0.85, 0.82))
	_hud.add_theme_color_override("font_outline_color", Color.BLACK)
	add_child(_hud)

	_apply()
	if "--capture" in str(OS.get_cmdline_user_args()):
		_capture()


func _physics_process(_delta: float) -> void:
	var dir := Vector2(
		float(Input.is_key_pressed(KEY_D) or Input.is_key_pressed(KEY_RIGHT)) - float(Input.is_key_pressed(KEY_A) or Input.is_key_pressed(KEY_LEFT)),
		float(Input.is_key_pressed(KEY_S) or Input.is_key_pressed(KEY_DOWN)) - float(Input.is_key_pressed(KEY_W) or Input.is_key_pressed(KEY_UP)))
	_player.velocity = dir.normalized() * WALK_SPEED
	_player.move_and_slide()
	# Face the dominant direction and keep it when stopping. Walk where a strip exists, else the still pose.
	if dir.x != 0.0 and (dir.y == 0.0 or absf(dir.x) >= absf(dir.y)):
		_facing = "right" if dir.x > 0.0 else "left"
	elif dir.y != 0.0:
		_facing = "front" if dir.y > 0.0 else "back"
	var walk := "walk_" + _facing
	if dir != Vector2.ZERO and _player_sprite.sprite_frames.has_animation(walk):
		_player_sprite.play(walk)
	else:
		_player_sprite.play(_facing)


func _process(delta: float) -> void:
	# When the player is behind a tall prop, the whole prop (upright part + ground base) turns
	# see-through as one material, so the player is never lost and the prop never splits in two.
	var body := _player.position + Vector2(0, -44)
	for prop in _props:
		var sprite: Sprite2D = prop.get_node("Sprite")
		var rect := Rect2(prop.position + sprite.offset - sprite.texture.get_size() / 2.0, sprite.texture.get_size())
		var behind := _player.position.y < prop.position.y and rect.grow(-4).has_point(body)
		var a := move_toward(sprite.modulate.a, FADE_ALPHA if behind else 1.0, delta * 4.0)
		sprite.modulate.a = a
		var base: Sprite2D = prop.get_meta("base")
		if base:
			base.modulate.a = a
	var anchor: Vector2 = PROPS[SIGIL_PROP][1] + Vector2(8, -96)
	_sigil.anchor = anchor # world pixels == language pixels


func _unhandled_input(event: InputEvent) -> void:
	if not (event is InputEventKey and event.pressed and not event.echo):
		return
	match event.keycode:
		KEY_T:
			mode = (mode + 1) % MODES.size()
		KEY_G:
			grounding = not grounding
		KEY_L:
			show_language = not show_language
		KEY_O:
			outline = not outline
		KEY_H:
			_hud.visible = not _hud.visible
		KEY_F:
			var win := get_window()
			win.mode = Window.MODE_WINDOWED if win.mode == Window.MODE_FULLSCREEN else Window.MODE_FULLSCREEN
		_:
			return
	_apply()


func _apply() -> void:
	var window := get_viewport().get_visible_rect().size
	_scale = maxi(1, floori(minf(window.x / NATIVE.x, window.y / NATIVE.y)))
	_screen.size = Vector2(NATIVE * _scale)
	_screen.position = ((window - _screen.size) / 2.0).floor()
	_lang_vp.size = NATIVE
	_lang_screen.size = _screen.size
	_lang_screen.position = _screen.position

	_ground.texture = _ground_textures[mode]
	_tile_extras.visible = mode == 0
	_bases.visible = mode != 2
	for prop in _props:
		prop.visible = mode != 2 # the target image already contains its props
	_modulate.visible = grounding
	_light.enabled = grounding
	for s in _shadows:
		s.visible = grounding
	_sigil.visible = show_language
	(_player_sprite.material as ShaderMaterial).set_shader_parameter("enabled", outline)

	var ui := window.y / 720.0
	_hud.position = Vector2(12, 8) * ui
	_hud.add_theme_font_size_override("font_size", int(16 * ui))
	_hud.add_theme_constant_override("outline_size", int(4 * ui))
	_hud.text = "Ground: %s   (x%d)   Grounding %s   Language %s   Outline %s\nWASD move · T ground mode · G grounding · L language · O outline · F fullscreen · H hide" % [
		MODES[mode], _scale, "ON" if grounding else "OFF", "ON" if show_language else "OFF", "ON" if outline else "OFF"]


# --- Ground: dual-grid tiles -------------------------------------------------------------

## Terrain per logic cell: 0 mud, 1 grass, 2 puddle. Grass and puddle never touch, because
## the batch only has mud<->grass and mud<->puddle transitions.
func _terrain_map() -> Array:
	var grass := FastNoiseLite.new()
	grass.seed = 3
	grass.frequency = 0.11
	var water := FastNoiseLite.new()
	water.seed = 9
	water.frequency = 0.09
	var map := []
	for y in GRID.y + 2:
		var row := []
		for x in GRID.x + 2:
			var t := 0
			if water.get_noise_2d(x, y) > 0.42:
				t = 2
			elif grass.get_noise_2d(x, y) > 0.05:
				t = 1
			row.append(t)
		map.append(row)
	for y in map.size(): # keep a ring of mud between grass and puddles
		for x in map[y].size():
			if map[y][x] != 2:
				continue
			for dy in [-1, 0, 1]:
				for dx in [-1, 0, 1]:
					var yy: int = y + dy
					var xx: int = x + dx
					if yy >= 0 and yy < map.size() and xx >= 0 and xx < map[y].size() and map[yy][xx] == 1:
						map[yy][xx] = 0
	return map


func _build_tile_ground() -> Texture2D:
	var map := _terrain_map()
	var atlases := {1: _img("terrain/mud_grass_dualgrid"), 2: _img("terrain/mud_puddle_dualgrid")}
	var bases := {0: [], 1: [], 2: []}
	for i in range(1, 5):
		bases[0].append(_img("terrain/mud_base_%02d" % i))
		bases[1].append(_img("terrain/grass_base_%02d" % i))
		bases[2].append(_img("terrain/puddle_base_%02d" % i))
	var img := Image.create_empty(NATIVE.x, NATIVE.y, false, Image.FORMAT_RGBA8)
	# Display cell (i, j) covers the four logic cells (i..i+1, j..j+1) and is drawn
	# half a cell up-left, so its centre sits on their shared corner.
	for j in GRID.y + 1:
		for i in GRID.x + 1:
			var corners := [map[j][i], map[j][i + 1], map[j + 1][i], map[j + 1][i + 1]] # TL, TR, BL, BR
			var kind := 2 if 2 in corners else (1 if 1 in corners else 0)
			var dst := Vector2i(i * CELL - CELL / 2, j * CELL - CELL / 2)
			var index := 0
			for k in 4:
				index = index * 2 + int(corners[k] == kind)
			var src: Image
			var region := Rect2i(0, 0, CELL, CELL)
			if kind == 0 or index == 15: # uniform cell: use a random seamless base variant
				var pool: Array = bases[kind]
				src = pool[_rng.randi_range(0, pool.size() - 1)]
			else: # index = 8*TL + 4*TR + 2*BL + BR, atlas (index % 4, index / 4)
				src = atlases[kind]
				region.position = Vector2i(index % 4, index / 4) * CELL
			img.blit_rect(src, region, dst)
	return ImageTexture.create_from_image(img)


func _scatter_decals() -> void:
	var names := ["gravel_01", "gravel_02", "gravel_03", "leaves_01", "leaves_02", "moss_01", "moss_02", "ground_crack_01"]
	for i in 46:
		var s := Sprite2D.new()
		s.texture = _tex("decals/" + names[_rng.randi_range(0, names.size() - 1)])
		s.position = Vector2(_rng.randi_range(16, NATIVE.x - 16), _rng.randi_range(16, NATIVE.y - 16))
		_tile_extras.add_child(s)


func _lay_path() -> void:
	for seg in PATH.size() - 1:
		var a: Vector2 = PATH[seg]
		var b: Vector2 = PATH[seg + 1]
		var steps := int(a.distance_to(b) / 20.0)
		for k in steps:
			if _rng.randf() < 0.25:
				continue # missing slabs: the order is failing
			var s := Sprite2D.new()
			s.texture = _tex("path/old_slab_%02d" % _rng.randi_range(1, 8))
			s.position = (a.lerp(b, float(k) / steps) + Vector2(_rng.randi_range(-4, 4), _rng.randi_range(-3, 3))).round()
			_tile_extras.add_child(s)


# --- Props, player, bounds ---------------------------------------------------------------

func _make_prop(file: String, collision: Rect2, ellipse: bool, base: Sprite2D) -> Node2D:
	var root := Node2D.new()
	root.set_meta("base", base)
	var tex := _tex("props/" + file)
	# Props whose ground part moved into a *_base decal end above the PNG's bottom edge.
	# Lift the node to where the upright part really meets the ground, so Y-Sort, the
	# contact shadow and collision follow the trunk instead of the canvas bottom.
	var gap := tex.get_height() - 1 - _lowest_opaque_row(tex.get_image())
	if base:
		tex = _without_overlap(tex, base.texture)
	root.position = Vector2(0, -gap)
	if not base: # a ground base already gives the prop its contact with the ground
		root.add_child(_footprint_shadow(tex))
	var sprite := Sprite2D.new()
	sprite.name = "Sprite"
	sprite.texture = tex
	sprite.offset = Vector2(0, -tex.get_height() / 2 + gap)
	root.add_child(sprite)
	var body := StaticBody2D.new()
	body.position = Vector2(0, gap) # collision data is relative to the PNG origin, not the lifted node
	if ellipse:
		var poly := CollisionPolygon2D.new()
		var pts := PackedVector2Array()
		var c := collision.get_center()
		for k in 20:
			var t := TAU * k / 20.0
			pts.append(c + Vector2(cos(t), sin(t)) * collision.size / 2.0)
		poly.polygon = pts
		body.add_child(poly)
	else:
		var shape := CollisionShape2D.new()
		var rect := RectangleShape2D.new()
		rect.size = collision.size
		shape.shape = rect
		shape.position = collision.get_center()
		body.add_child(shape)
	root.add_child(body)
	return root


## Drops the upright part's pixels that its ground base already draws identically (both share
## the same bottom-centre origin). Without this, the overlapping rows get doubled when both fade.
## Pixels that differ (a plinth over soil) stay on the upright part.
func _without_overlap(upright: Texture2D, base: Texture2D) -> Texture2D:
	var img := upright.get_image()
	var b := base.get_image()
	var dx := (b.get_width() - img.get_width()) / 2
	var dy := b.get_height() - img.get_height()
	for y in img.get_height():
		for x in img.get_width():
			var bx := x + dx
			var by := y + dy
			if bx >= 0 and by >= 0 and bx < b.get_width() and by < b.get_height() and b.get_pixel(bx, by).a > 0.5 and img.get_pixel(x, y).a > 0.5 \
					and _rgb_distance(b.get_pixel(bx, by), img.get_pixel(x, y)) < 0.06:
				img.set_pixel(x, y, Color(0, 0, 0, 0))
	return ImageTexture.create_from_image(img)


func _rgb_distance(a: Color, b: Color) -> float:
	return absf(a.r - b.r) + absf(a.g - b.g) + absf(a.b - b.b)


func _make_player() -> CharacterBody2D:
	var body := CharacterBody2D.new()
	# Taller and raised 3 px so the far foot of a side pose still lands on it (side poses stand in slight depth).
	body.add_child(_shadow(36, Vector2(0, -3), 14))
	var frames := SpriteFrames.new()
	# Strips (96x96 frames in a row) are picked up as they get delivered. Standing uses the
	# idle strip (500 ms a frame: a calm 2 s breath) when there is one, else the still pose; walking is 100 ms a frame.
	# Front uses the straight-on pose (the original B1 is a 3/4 view and looked twisted walking down).
	var still := {"front": "hero_B1_front_straight.png"}
	for facing in ["front", "back", "left", "right"]:
		frames.add_animation(facing)
		if not _add_strip(frames, facing, "anim/hero_B1_idle_%s.png" % facing, 2.0):
			var pose: String = still.get(facing, "hero_B1_%s.png" % facing)
			frames.add_frame(facing, ImageTexture.create_from_image(_img_at(HERO + pose)))
		var walk: String = "walk_" + facing
		frames.add_animation(walk)
		if not _add_strip(frames, walk, "anim/hero_B1_walk_%s.png" % facing, 10.0):
			frames.remove_animation(walk)
	_player_sprite = AnimatedSprite2D.new()
	_player_sprite.sprite_frames = frames
	_player_sprite.animation = "front"
	_player_sprite.offset = Vector2(0, -48) # 96x96 frames, feet at bottom centre
	var outline_mat := ShaderMaterial.new()
	outline_mat.shader = Shader.new()
	outline_mat.shader.code = OUTLINE_SHADER
	_player_sprite.material = outline_mat
	body.add_child(_player_sprite)
	var shape := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(22, 8)
	shape.shape = rect
	shape.position = Vector2(0, -4)
	body.add_child(shape)

	_light = PointLight2D.new()
	var gradient := Gradient.new()
	gradient.set_color(0, Color(1, 1, 1, 1))
	gradient.set_color(1, Color(1, 1, 1, 0))
	var tex := GradientTexture2D.new()
	tex.gradient = gradient
	tex.fill = GradientTexture2D.FILL_RADIAL
	tex.fill_from = Vector2(0.5, 0.5)
	tex.fill_to = Vector2(1.0, 0.5)
	tex.width = 256
	tex.height = 256
	_light.texture = tex
	_light.texture_scale = 1.6
	_light.color = Color(1.0, 0.92, 0.8)
	_light.energy = 0.55
	_light.position = Vector2(0, -30)
	body.add_child(_light)
	return body


func _add_strip(frames: SpriteFrames, anim: String, file: String, fps: float) -> bool:
	if not FileAccess.file_exists(HERO + file):
		return false
	var strip := _img_at(HERO + file)
	frames.set_animation_speed(anim, fps)
	for i in strip.get_width() / 96:
		frames.add_frame(anim, ImageTexture.create_from_image(strip.get_region(Rect2i(i * 96, 0, 96, 96))))
	return true


func _add_room_bounds() -> void:
	var walls := StaticBody2D.new()
	for r in [Rect2(-20, -20, NATIVE.x + 40, 20), Rect2(-20, NATIVE.y, NATIVE.x + 40, 20),
			Rect2(-20, 0, 20, NATIVE.y), Rect2(NATIVE.x, 0, 20, NATIVE.y)]:
		var shape := CollisionShape2D.new()
		var rect := RectangleShape2D.new()
		rect.size = r.size
		shape.shape = rect
		shape.position = r.position + r.size / 2.0
		walls.add_child(shape)
	_world.add_child(walls)


## Contact shadow shaped like the prop's own base: the bottom rows of its silhouette are
## squashed flat and nudged down-right (light from the upper left), so roots and plinths sit
## in their shadow instead of floating above a generic ellipse.
func _footprint_shadow(tex: Texture2D) -> Sprite2D:
	var src := tex.get_image()
	var w := src.get_width()
	var h := _lowest_opaque_row(src) + 1
	var band := mini(24, h)
	var out_h := band / 2 + 3
	var img := Image.create_empty(w + 4, out_h, false, Image.FORMAT_RGBA8)
	for r in band:
		for x in w:
			if src.get_pixel(x, h - band + r).a > 0.5:
				var y := r / 2
				for k in 3: # thicken downwards so thin roots still leave a shadow
					img.set_pixel(x + 2, mini(y + k, out_h - 1), SHADOW_COLOR)
	var s := Sprite2D.new()
	s.texture = ImageTexture.create_from_image(img)
	s.centered = false
	s.position = Vector2(-w / 2, -band / 2 + 1)
	_shadows.append(s)
	return s


func _lowest_opaque_row(img: Image) -> int:
	for y in range(img.get_height() - 1, -1, -1):
		for x in img.get_width():
			if img.get_pixel(x, y).a > 0.5:
				return y
	return img.get_height() - 1


func _scatter_dead_grass() -> void:
	for i in 14:
		var s := Sprite2D.new()
		s.texture = _tex("decals/dead_grass_%02d" % _rng.randi_range(1, 4))
		s.offset = Vector2(0, -s.texture.get_height() / 2)
		s.position = Vector2(_rng.randi_range(20, NATIVE.x - 20), _rng.randi_range(30, NATIVE.y - 6))
		_bases.add_child(s)


func _shadow(width: int, offset: Vector2, height := 0) -> Sprite2D:
	var h := height if height > 0 else maxi(3, int(width * 0.3))
	var img := Image.create_empty(width, h, false, Image.FORMAT_RGBA8)
	for y in h:
		for x in width:
			var d := Vector2((x + 0.5) / width * 2.0 - 1.0, (y + 0.5) / h * 2.0 - 1.0)
			if d.length_squared() <= 1.0:
				img.set_pixel(x, y, SHADOW_COLOR)
	var s := Sprite2D.new()
	s.texture = ImageTexture.create_from_image(img)
	s.position = offset.round()
	_shadows.append(s)
	return s


# --- Loading & capture -------------------------------------------------------------------

func _img(path: String) -> Image:
	return _img_at(ART + path + ".png")


func _img_at(res_path: String) -> Image:
	# Loaded straight from the PNG so the prototype does not depend on editor import.
	var img := Image.load_from_file(ProjectSettings.globalize_path(res_path))
	img.convert(Image.FORMAT_RGBA8)
	return img


func _tex(path: String) -> Texture2D:
	return ImageTexture.create_from_image(_img(path))


func _capture() -> void:
	var dir := ""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--capture="):
			dir = arg.trim_prefix("--capture=")
	DirAccess.make_dir_recursive_absolute(dir)
	_player.position = PROPS[0][1] + Vector2(-4, -64) # behind the tree trunk: occlusion check
	for m in MODES.size():
		mode = m
		grounding = true
		_apply()
		await _shot("%s/mode%d.png" % [dir, m])
	mode = 0
	grounding = false
	_apply()
	await _shot("%s/mode0_no_grounding.png" % dir)
	# Hero B1 in open ground on the chosen plate, one shot per facing.
	mode = 1
	grounding = true
	_apply()
	set_physics_process(false) # keyboard handling would reset the pose
	_player.position = PLAYER_START
	for facing in ["front", "back", "left", "right"]:
		_player_sprite.animation = facing
		await _shot("%s/hero_%s.png" % [dir, facing])
	# Walk cycles stepped by hand at game speed (70 px/s x 100 ms = 7 px per frame): a planted
	# foot should stay on the same ground pixel while the body moves past it.
	for facing in ["front", "back", "left", "right"]:
		var walk: String = "walk_" + facing
		if not _player_sprite.sprite_frames.has_animation(walk):
			continue
		var step: Vector2 = {"front": Vector2.DOWN, "back": Vector2.UP, "left": Vector2.LEFT, "right": Vector2.RIGHT}[facing] * WALK_SPEED * 0.1
		_player.position = PLAYER_START
		_player_sprite.animation = walk
		for i in _player_sprite.sprite_frames.get_frame_count(walk) * 2:
			_player_sprite.frame = i % _player_sprite.sprite_frames.get_frame_count(walk)
			await _shot("%s/%s_%02d.png" % [dir, walk, i])
			_player.position += step
	get_tree().quit()


func _shot(path: String) -> void:
	for i in 4:
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	# Crop the composed window (world + language layer) back to the game screen.
	var frame := get_viewport().get_texture().get_image()
	frame.get_region(Rect2i(_screen.position, _screen.size)).save_png(path)
	print("captured ", path)
