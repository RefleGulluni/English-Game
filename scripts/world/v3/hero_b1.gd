class_name HeroB1
extends CharacterBody2D
## The Wordbearer (B1) on the v3 pixel world. Drag scenes/player/hero_b1.tscn into any scene:
## it walks with WASD / arrows, idles, and plays the Lexicon book animation.
## Frames come from scenes/player/hero_b1_frames.tres (scripts/tools/bake_hero_b1.gd).
##
## Same player contract as the 0.9 slice (`scripts/world/player_movement.gd`), so the
## interaction system, reward controller and combat wiring keep working unchanged:
## set_input_locked(), can_world_interact(), face_direction().
## Animation rules: docs/HERO_DESIGN.md, docs/HERO_ANIMATION_REQUEST.md §7.

signal book_closed

const WALK_SPEED := 70.0 # native px per second, validated in graveyard_room

var input_locked := false
var facing := "front"
var book_phase := "" # "", "opening", "reading", "closing": busy with the Lexicon
@onready var sprite: AnimatedSprite2D = $Sprite


func _ready() -> void:
	add_to_group("world_player")
	# Dragged into a fresh scene, the hero still walks: movement actions are added if missing.
	preload("res://scripts/systems/slice_input.gd").install()
	sprite.animation_finished.connect(_on_animation_finished)
	sprite.play(facing)


func set_input_locked(value: bool) -> void:
	input_locked = value
	if value:
		velocity = Vector2.ZERO


func can_world_interact() -> bool:
	return not input_locked and book_phase == ""


## Turns to face a direction (diagonals show the side) and shows the standing pose.
func face_direction(direction: Vector2) -> void:
	_turn(direction)
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
	if dir != Vector2.ZERO:
		_turn(dir) # keep the facing when stopping
	var walk := "walk_" + facing
	# play() on the running animation keeps its frame; switching every tick would freeze it on frame 1.
	sprite.play(walk if dir != Vector2.ZERO and sprite.sprite_frames.has_animation(walk) else facing)


func _turn(direction: Vector2) -> void:
	if direction.length_squared() < 0.01:
		return
	if absf(direction.x) >= absf(direction.y):
		facing = "right" if direction.x > 0.0 else "left"
	else:
		facing = "front" if direction.y > 0.0 else "back"


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
