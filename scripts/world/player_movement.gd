extends CharacterBody2D

@export var speed := 180.0 # Placeholder world scale; not a combat stat.
var input_locked := false
var facing := Vector2.RIGHT

func set_input_locked(value: bool) -> void:
	input_locked = value
	if value: velocity = Vector2.ZERO

func can_world_interact() -> bool:
	return not input_locked

func face_direction(direction: Vector2) -> void:
	if direction.length_squared() > 0.01: facing = direction.normalized()

func _physics_process(_delta: float) -> void:
	velocity = Vector2.ZERO if input_locked else Input.get_vector("world_left", "world_right", "world_up", "world_down") * speed
	move_and_slide()
	if velocity.length_squared() > 1.0: facing = velocity.normalized()
	# A read-only motion contract; visual animation never owns movement or lock state.
	for visual in $VisualRoot.get_children():
		if visual.has_method("present_motion"): visual.present_motion(get_real_velocity(), facing)
