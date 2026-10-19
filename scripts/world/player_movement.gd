extends CharacterBody2D

@export var speed := 180.0 # Placeholder world scale; not a combat stat.
var input_locked := false

func set_input_locked(value: bool) -> void:
	input_locked = value
	if value: velocity = Vector2.ZERO

func can_world_interact() -> bool:
	return not input_locked

func _physics_process(_delta: float) -> void:
	velocity = Vector2.ZERO if input_locked else Input.get_vector("world_left", "world_right", "world_up", "world_down") * speed
	move_and_slide()
