@tool
extends Node2D
## Reusable placement wrapper. The foot pivot drives sorting; art never supplies collision.
@export var visual_scene: PackedScene
@export var world_height := 86.0
@export var foreground := false
@export var occlusion_width := 65.0
var visual: Node2D

func _ready() -> void:
	if visual_scene == null: return
	visual = visual_scene.instantiate()
	add_child(visual)
	if visual.has_meta("display_size"):
		var dimensions: Vector2 = visual.get_meta("display_size")
		world_height = dimensions.y
		occlusion_width = maxf(24, dimensions.x * 0.48)
	if visual is Sprite2D and visual.texture != null:
		var factor: float = world_height / visual.texture.get_height()
		visual.scale = Vector2.ONE * factor
		visual.position.y = -world_height * 0.5
	if foreground: z_index = 5

func _process(delta: float) -> void:
	if Engine.is_editor_hint() or not is_instance_valid(visual): return
	var actor := get_tree().get_first_node_in_group("world_player") as Node2D
	if actor == null: return
	var relative := actor.global_position - global_position
	# Keep partial occlusion, fade only the covering prop, never the ground or actor.
	var covers := absf(relative.x) < occlusion_width and relative.y < 8 and relative.y > -world_height
	visual.modulate.a = lerpf(visual.modulate.a, 0.48 if covers else 1.0, minf(1.0, delta * 8.0))
