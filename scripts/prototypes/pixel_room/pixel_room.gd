extends Node
## Pixel Art Direction Validation Room (Art Direction Bible v3).
##
## The world renders into a SubViewport at native pixel resolution and is shown at an
## integer scale with nearest filtering, so every world pixel stays a clean square.
## The Smooth Language layer (sigil + word) is drawn in the full-resolution main viewport.
##
## Keys: WASD / arrows move · 1/2/3 player size 64/96/128 · R native resolution
##       G grounding (contact shadows + light) · L language layer · P language style · F fullscreen · H help
## Language styles: smooth (anti-aliased) · fine pixel (one step finer than the world) · world pixel.
## The window's content scaling is disabled here so the integer scale is computed in real
## screen pixels (a 1280x720 window on a Retina screen is 2560x1440 pixels).
## Capture mode: Godot --path . res://scenes/prototypes/pixel_room/pixel_room.tscn -- --capture=<abs dir>

const PixelGround := preload("res://scripts/prototypes/pixel_room/pixel_ground.gd")
const LanguageSigil := preload("res://scripts/prototypes/pixel_room/language_sigil.gd")

const SIZES := [64, 96, 128]
const NATIVE_PRESETS := [Vector2i(640, 360), Vector2i(960, 540), Vector2i(1280, 720)]
const ROOM := Vector2i(1600, 1040)
const ASSET_DIR := "res://art/pixel_test/size_%d/"
const SHADOW_COLOR := Color(0.04, 0.03, 0.05, 0.45)
const PLAYER_START := Vector2(760, 610)
# Rows of graves: the cemetery once had order; gaps show it failing.
const GRAVES := [
	Vector2(260, 300), Vector2(380, 300), Vector2(500, 300), Vector2(740, 300), Vector2(860, 300), Vector2(980, 300), Vector2(1220, 300),
	Vector2(260, 440), Vector2(500, 440), Vector2(740, 440), Vector2(860, 440), Vector2(1100, 440), Vector2(1220, 440), Vector2(1340, 440),
	Vector2(380, 580), Vector2(500, 580), Vector2(620, 580), Vector2(860, 580), Vector2(980, 580), Vector2(1340, 580),
	Vector2(260, 720), Vector2(620, 720), Vector2(740, 720), Vector2(980, 720), Vector2(1100, 720), Vector2(1220, 720),
	Vector2(380, 860), Vector2(500, 860), Vector2(860, 860), Vector2(1100, 860), Vector2(1340, 860),
]
const SIGIL_GRAVE := 17
const CAPTURE_GRAVE := 16

var size_index := 1
var native_index := 1
var grounding := true
var show_language := true
var lang_mode := 2 # 0 smooth, 1 fine pixel, 2 world pixel (chosen 2026-10-22)

var _viewport: SubViewport
var _screen: TextureRect
var _world: Node2D
var _player: CharacterBody2D
var _player_sprite: Sprite2D
var _player_shadow: Sprite2D
var _player_shape: RectangleShape2D
var _light: PointLight2D
var _modulate: CanvasModulate
var _camera: Camera2D
var _graves: Array[Node2D] = []
var _sigil: Control
var _lang_vp: SubViewport
var _lang_screen: TextureRect
var _lang_px := 1 # screen pixels per language pixel
var _hud: Label
var _scale := 2
var _textures := {}


func _ready() -> void:
	get_window().content_scale_mode = Window.CONTENT_SCALE_MODE_DISABLED
	get_window().size_changed.connect(_apply)
	_viewport = SubViewport.new()
	_viewport.canvas_item_default_texture_filter = Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_NEAREST
	_viewport.snap_2d_transforms_to_pixel = true
	_viewport.snap_2d_vertices_to_pixel = true
	_viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(_viewport)

	_world = Node2D.new()
	_viewport.add_child(_world)
	var ground := Sprite2D.new()
	ground.centered = false
	ground.texture = PixelGround.generate(ROOM)
	_world.add_child(ground)

	var sorted := Node2D.new()
	sorted.y_sort_enabled = true # feet origins: whoever stands lower on screen draws in front
	_world.add_child(sorted)
	for pos in GRAVES:
		var grave := _make_grave()
		grave.position = pos
		sorted.add_child(grave)
		_graves.append(grave)
	_player = _make_player()
	_player.position = PLAYER_START
	sorted.add_child(_player)

	_modulate = CanvasModulate.new()
	_modulate.color = Color(0.74, 0.79, 0.88) # cold, wet ambient shared by everything
	_world.add_child(_modulate)

	_camera = Camera2D.new()
	_camera.limit_left = 0
	_camera.limit_top = 0
	_camera.limit_right = ROOM.x
	_camera.limit_bottom = ROOM.y
	_world.add_child(_camera)
	_camera.make_current()

	_screen = TextureRect.new()
	_screen.texture = _viewport.get_texture()
	_screen.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_screen.stretch_mode = TextureRect.STRETCH_SCALE
	add_child(_screen)

	_lang_vp = SubViewport.new()
	_lang_vp.transparent_bg = true
	_lang_vp.canvas_item_default_texture_filter = Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_NEAREST
	_lang_vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(_lang_vp)
	_lang_screen = TextureRect.new()
	_lang_screen.texture = _lang_vp.get_texture()
	_lang_screen.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_lang_screen.stretch_mode = TextureRect.STRETCH_SCALE
	_lang_screen.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_lang_screen)
	_sigil = LanguageSigil.new()
	add_child(_sigil)

	_hud = Label.new()
	_hud.position = Vector2(12, 8)
	_hud.add_theme_color_override("font_color", Color(0.85, 0.85, 0.82))
	_hud.add_theme_color_override("font_outline_color", Color.BLACK)
	_hud.add_theme_constant_override("outline_size", 4)
	add_child(_hud)

	_apply()
	if "--capture" in str(OS.get_cmdline_user_args()):
		_capture()


func _physics_process(_delta: float) -> void:
	var dir := Vector2(
		float(Input.is_key_pressed(KEY_D) or Input.is_key_pressed(KEY_RIGHT)) - float(Input.is_key_pressed(KEY_A) or Input.is_key_pressed(KEY_LEFT)),
		float(Input.is_key_pressed(KEY_S) or Input.is_key_pressed(KEY_DOWN)) - float(Input.is_key_pressed(KEY_W) or Input.is_key_pressed(KEY_UP)))
	_player.velocity = dir.normalized() * SIZES[size_index] * 1.4
	_player.move_and_slide()
	if dir.x != 0.0:
		_player_sprite.flip_h = dir.x < 0.0


func _process(_delta: float) -> void:
	_camera.position = _player.position + Vector2(0, -SIZES[size_index] * 0.5)
	var grave := _graves[SIGIL_GRAVE]
	var world_anchor := grave.position + Vector2(0, -SIZES[size_index] * 1.45)
	_sigil.anchor = (_screen.position + (_viewport.canvas_transform * world_anchor) * _scale) / _lang_px
	_sigil.radius = SIZES[size_index] * 0.42 * _scale / _lang_px


func _unhandled_input(event: InputEvent) -> void:
	if not (event is InputEventKey and event.pressed and not event.echo):
		return
	match event.keycode:
		KEY_1, KEY_2, KEY_3:
			size_index = event.keycode - KEY_1
		KEY_R:
			native_index = (native_index + 1) % NATIVE_PRESETS.size()
		KEY_G:
			grounding = not grounding
		KEY_L:
			show_language = not show_language
		KEY_P:
			lang_mode = (lang_mode + 1) % 3
		KEY_H:
			_hud.visible = not _hud.visible
		KEY_F:
			var win := get_window()
			win.mode = Window.MODE_WINDOWED if win.mode == Window.MODE_FULLSCREEN else Window.MODE_FULLSCREEN
		_:
			return
	_apply()


func _apply() -> void:
	var size: int = SIZES[size_index]
	var native: Vector2i = NATIVE_PRESETS[native_index]
	_viewport.size = native
	var window := get_viewport().get_visible_rect().size
	_scale = maxi(1, floori(minf(window.x / native.x, window.y / native.y)))
	_screen.size = Vector2(native * _scale)
	_screen.position = ((window - _screen.size) / 2.0).floor()
	var ui := window.y / 720.0
	_hud.position = Vector2(12, 8) * ui
	_hud.add_theme_font_size_override("font_size", int(16 * ui))
	_hud.add_theme_constant_override("outline_size", int(4 * ui))

	var player_tex := _texture(size, "player_idle_01")
	_player_sprite.texture = player_tex
	_player_sprite.offset = Vector2(0, -player_tex.get_height() / 2)
	_player_shadow.texture = _shadow(int(player_tex.get_width() * 0.8))
	_player_shape.size = Vector2(player_tex.get_width() * 0.45, 6)
	_light.texture_scale = size * 2.6 / 128.0

	var grave_tex := _texture(size, "tombstone_01")
	for grave in _graves:
		var sprite: Sprite2D = grave.get_node("Sprite")
		sprite.texture = grave_tex
		sprite.offset = Vector2(0, -grave_tex.get_height() / 2)
		var shadow: Sprite2D = grave.get_node("Shadow")
		shadow.texture = _shadow(int(grave_tex.get_width() * 0.9))
		(grave.get_node("Body/Shape").shape as RectangleShape2D).size = Vector2(grave_tex.get_width() * 0.8, 6)

	_modulate.visible = grounding
	_light.enabled = grounding
	_player_shadow.visible = grounding
	for grave in _graves:
		grave.get_node("Shadow").visible = grounding
	_sigil.visible = show_language
	# Language pixels: smooth = 1 screen px, fine = one step finer than the world, world = same as the world.
	_lang_px = [1, maxi(1, _scale - 1), _scale][lang_mode]
	_sigil.antialias = lang_mode == 0
	var target: Node = self if lang_mode == 0 else _lang_vp
	if _sigil.get_parent() != target:
		_sigil.reparent(target)
	_lang_vp.size = Vector2i((window / _lang_px).ceil())
	_lang_screen.size = Vector2(_lang_vp.size * _lang_px)
	_lang_screen.visible = lang_mode != 0
	_hud.text = "Player %d px   Native %dx%d  (x%d)   Player = %d%% of screen height   Grounding %s   Language %s (%s)\nWASD move · 1/2/3 size · R resolution · G grounding · L language · P language style · F fullscreen · H hide" % [
		size, native.x, native.y, _scale, roundi(100.0 * size / native.y), "ON" if grounding else "OFF", "ON" if show_language else "OFF", ["smooth", "fine pixel", "world pixel"][lang_mode]]


func _make_player() -> CharacterBody2D:
	var body := CharacterBody2D.new()
	_player_shadow = Sprite2D.new()
	body.add_child(_player_shadow)
	_player_sprite = Sprite2D.new()
	body.add_child(_player_sprite)
	var shape := CollisionShape2D.new()
	_player_shape = RectangleShape2D.new()
	shape.shape = _player_shape
	shape.position = Vector2(0, -3)
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
	_light.color = Color(1.0, 0.9, 0.78)
	_light.energy = 0.7
	_light.position = Vector2(0, -20)
	body.add_child(_light)
	return body


func _make_grave() -> Node2D:
	var grave := Node2D.new()
	var shadow := Sprite2D.new()
	shadow.name = "Shadow"
	shadow.position = Vector2(2, 0) # light from the upper left
	grave.add_child(shadow)
	var sprite := Sprite2D.new()
	sprite.name = "Sprite"
	grave.add_child(sprite)
	var body := StaticBody2D.new()
	body.name = "Body"
	var shape := CollisionShape2D.new()
	shape.name = "Shape"
	shape.shape = RectangleShape2D.new()
	shape.position = Vector2(0, -3)
	body.add_child(shape)
	grave.add_child(body)
	return grave


func _texture(size: int, file: String) -> Texture2D:
	var key := "%d/%s" % [size, file]
	if not _textures.has(key):
		# Loaded straight from the PNG so the prototype does not depend on editor import.
		var img := Image.load_from_file(ProjectSettings.globalize_path(ASSET_DIR % size + file + ".png"))
		_textures[key] = ImageTexture.create_from_image(img)
	return _textures[key]


func _shadow(width: int) -> Texture2D:
	var key := "shadow/%d" % width
	if not _textures.has(key):
		var h := maxi(3, int(width * 0.28))
		var img := Image.create_empty(width, h, false, Image.FORMAT_RGBA8)
		for y in h:
			for x in width:
				var d := Vector2((x + 0.5) / width * 2.0 - 1.0, (y + 0.5) / h * 2.0 - 1.0)
				if d.length_squared() <= 1.0:
					img.set_pixel(x, y, SHADOW_COLOR)
		_textures[key] = ImageTexture.create_from_image(img)
	return _textures[key]


func _capture() -> void:
	var dir := ""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--capture="):
			dir = arg.trim_prefix("--capture=")
	DirAccess.make_dir_recursive_absolute(dir)
	# Stand just behind a grave so Y-Sort occlusion is visible in every shot.
	_player.position = GRAVES[CAPTURE_GRAVE] + Vector2(10, -18)
	for n in NATIVE_PRESETS.size():
		for s in SIZES.size():
			native_index = n
			size_index = s
			grounding = true
			_apply()
			await _shot("%s/native%d_player%d.png" % [dir, NATIVE_PRESETS[n].x, SIZES[s]])
	size_index = 1
	native_index = 0
	grounding = false
	_apply()
	await _shot("%s/native640_player96_no_grounding.png" % dir)
	get_tree().quit()


func _shot(path: String) -> void:
	for i in 4:
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(path)
	print("captured ", path)
