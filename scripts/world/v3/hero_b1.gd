class_name HeroB1
extends CharacterBody2D
## The Wordbearer (B1) on the v3 pixel world: four directions, idle / walk strips, Lexicon book.
##
## Same player contract as the 0.9 slice (`scripts/world/player_movement.gd`), so the
## interaction system, reward controller and combat wiring keep working unchanged:
## set_input_locked(), can_world_interact(), face_direction().
## Animation rules: docs/HERO_DESIGN.md, docs/HERO_ANIMATION_REQUEST.md §7.

signal book_closed

const HERO := "res://art/character_design/"
const FRAME := 96
const WALK_SPEED := 70.0 # native px per second, validated in graveyard_room
const SHADOW_COLOR := Color(0.03, 0.03, 0.05, 0.45)

var input_locked := false
var facing := "front"
var book_phase := "" # "", "opening", "reading", "closing": busy with the Lexicon
var sprite: AnimatedSprite2D
var light: PointLight2D


func _init() -> void:
	add_to_group("world_player")
	collision_layer = 2
	collision_mask = 1
	# Contact shadow 36x14, raised 3 px: side poses stand in slight depth (2026-10-24).
	add_child(PixelArt.ellipse_sprite(36, 14, SHADOW_COLOR, Vector2(0, -3)))
	sprite = AnimatedSprite2D.new()
	sprite.sprite_frames = _build_frames()
	sprite.offset = Vector2(0, -FRAME / 2) # feet at the node origin
	sprite.play("front")
	sprite.animation_finished.connect(_on_animation_finished)
	add_child(sprite)
	var shape := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(22, 8)
	shape.shape = rect
	shape.position = Vector2(0, -4)
	add_child(shape)
	light = PointLight2D.new() # the lantern
	light.texture = PixelArt.radial_light(256)
	light.texture_scale = 1.6
	light.color = Color(1.0, 0.92, 0.8)
	light.energy = 0.55
	light.position = Vector2(0, -30)
	add_child(light)


func set_input_locked(value: bool) -> void:
	input_locked = value
	if value:
		velocity = Vector2.ZERO


func can_world_interact() -> bool:
	return not input_locked and book_phase == ""


func face_direction(direction: Vector2) -> void:
	if direction.length_squared() < 0.01:
		return
	if absf(direction.x) >= absf(direction.y):
		facing = "right" if direction.x > 0.0 else "left"
	else:
		facing = "front" if direction.y > 0.0 else "back"
	if book_phase == "":
		sprite.play(facing)


func _physics_process(_delta: float) -> void:
	if input_locked or book_phase != "":
		velocity = Vector2.ZERO
		if book_phase == "" and sprite.animation.begins_with("walk_"):
			sprite.play(facing)
		return
	var dir := Input.get_vector("world_left", "world_right", "world_up", "world_down")
	velocity = dir * WALK_SPEED
	move_and_slide()
	# Face the dominant direction (diagonals show the side) and keep it when stopping.
	if dir != Vector2.ZERO:
		face_direction(dir)
	var walk := "walk_" + facing
	if dir != Vector2.ZERO and sprite.sprite_frames.has_animation(walk):
		sprite.play(walk)
	else:
		sprite.play(facing)


## Opening turns the hero to the camera and plays the book strip; closing plays it backwards.
func set_book_open(open: bool) -> void:
	facing = "front"
	if not sprite.sprite_frames.has_animation("book_open"):
		book_phase = "reading" if open else ""
		sprite.play("front")
		if not open:
			book_closed.emit()
	elif open:
		book_phase = "opening"
		sprite.play("book_open")
	else:
		book_phase = "closing"
		sprite.play_backwards("book_open")


func _on_animation_finished() -> void:
	if sprite.animation != "book_open":
		return
	if book_phase == "opening":
		book_phase = "reading"
		sprite.play("book_read")
	elif book_phase == "closing":
		book_phase = ""
		sprite.play("front")
		book_closed.emit()


func _build_frames() -> SpriteFrames:
	var frames := SpriteFrames.new()
	frames.remove_animation("default")
	# Front uses the straight-on pose; the original B1 is a 3/4 design sheet (D-011).
	var still := {"front": "hero_B1_front_straight.png"}
	for dir in ["front", "back", "left", "right"]:
		frames.add_animation(dir)
		if not _add_strip(frames, dir, "anim/hero_B1_idle_%s.png" % dir, 2.0):
			frames.add_frame(dir, PixelArt.texture(HERO + still.get(dir, "hero_B1_%s.png" % dir)))
		var walk: String = "walk_" + dir
		frames.add_animation(walk)
		if not _add_strip(frames, walk, "anim/hero_B1_walk_%s.png" % dir, 10.0):
			frames.remove_animation(walk)
	frames.add_animation("book_open")
	frames.set_animation_loop("book_open", false)
	if not _add_strip(frames, "book_open", "anim/hero_B1_book_open_front.png", 1000.0 / 70.0):
		frames.remove_animation("book_open")
	frames.add_animation("book_read")
	if not _add_strip(frames, "book_read", "anim/hero_B1_book_read_front.png", 2.0):
		frames.remove_animation("book_read")
	return frames


func _add_strip(frames: SpriteFrames, anim: String, file: String, fps: float) -> bool:
	if not FileAccess.file_exists(HERO + file):
		return false
	var strip := PixelArt.image(HERO + file)
	frames.set_animation_speed(anim, fps)
	for i in strip.get_width() / FRAME:
		frames.add_frame(anim, ImageTexture.create_from_image(strip.get_region(Rect2i(i * FRAME, 0, FRAME, FRAME))))
	return true
