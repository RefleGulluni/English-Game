extends Node

signal target_changed(target: Node, prompt: String)
@export var radius := 82.0
var player: Node2D
var current: Node2D
var enabled := true
var targets: Array[Node2D] = []

func register(target: Node2D) -> void:
	if target not in targets: targets.append(target)

func _physics_process(_delta: float) -> void:
	refresh()

func refresh() -> void:
	var nearest: Node2D
	var distance := radius
	if enabled and is_instance_valid(player):
		for target in targets:
			if not is_instance_valid(target) or not target.has_method("can_interact") or not target.can_interact(player): continue
			var d := player.global_position.distance_to(target.global_position)
			if d <= distance:
				nearest = target
				distance = d
	if nearest == current: return
	if is_instance_valid(current) and current.has_method("set_highlighted"): current.set_highlighted(false)
	current = nearest
	if is_instance_valid(current) and current.has_method("set_highlighted"): current.set_highlighted(true)
	target_changed.emit(current, current.get_prompt() if is_instance_valid(current) else "")

func interact() -> bool:
	refresh()
	if not enabled or not is_instance_valid(current) or not current.can_interact(player): return false
	return current.interact(player)
