extends SceneTree
## Bakes the hero B1 animation strips into a SpriteFrames resource, plus the contact shadow,
## so scenes/player/hero_b1.tscn shows the full hero in the editor and can be dragged into
## any scene. Re-run after the character design group delivers new strips:
##   Godot --headless --path . --import
##   Godot --headless --path . --script res://scripts/tools/bake_hero_b1.gd

const ANIM := "res://art/character_design/anim/"
const OUT := "res://scenes/player/"
const FRAME := 96
const SHADOW_COLOR := Color(0.03, 0.03, 0.05, 0.45)
# [animation, strip file, frames per second, loops]
const STRIPS := [
	["front", "hero_B1_idle_front.png", 2.0, true], # 4 x 500 ms
	["back", "hero_B1_idle_back.png", 2.0, true],
	["left", "hero_B1_idle_left.png", 2.0, true],
	["right", "hero_B1_idle_right.png", 2.0, true],
	["walk_front", "hero_B1_walk_front.png", 10.0, true], # 8 x 100 ms
	["walk_back", "hero_B1_walk_back.png", 10.0, true],
	["walk_left", "hero_B1_walk_left.png", 10.0, true],
	["walk_right", "hero_B1_walk_right.png", 10.0, true],
	["book_open", "hero_B1_book_open_front.png", 1000.0 / 70.0, false], # 6 x 70 ms; closing plays it backwards
	["book_read", "hero_B1_book_read_front.png", 2.0, true],
]


func _init() -> void:
	var frames := SpriteFrames.new()
	frames.remove_animation("default")
	for s in STRIPS:
		var strip: Texture2D = load(ANIM + s[1])
		if strip == null:
			push_error("Missing strip (run --import first): " + s[1])
			quit(1)
			return
		frames.add_animation(s[0])
		frames.set_animation_speed(s[0], s[2])
		frames.set_animation_loop(s[0], s[3])
		for i in strip.get_width() / FRAME:
			var atlas := AtlasTexture.new()
			atlas.atlas = strip
			atlas.region = Rect2(i * FRAME, 0, FRAME, FRAME)
			frames.add_frame(s[0], atlas)
	var err := ResourceSaver.save(frames, OUT + "hero_b1_frames.tres")
	# Contact shadow 36x14 (user-approved 2026-10-24); the scene raises it 3 px.
	var img := Image.create_empty(36, 14, false, Image.FORMAT_RGBA8)
	for y in 14:
		for x in 36:
			if Vector2((x + 0.5) / 36.0 * 2.0 - 1.0, (y + 0.5) / 14.0 * 2.0 - 1.0).length_squared() <= 1.0:
				img.set_pixel(x, y, SHADOW_COLOR)
	img.save_png(ProjectSettings.globalize_path(OUT + "hero_b1_shadow.png"))
	print("BAKE_HERO_B1: ", "OK" if err == OK else "FAILED %d" % err)
	quit()
