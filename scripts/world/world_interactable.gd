extends Node2D

signal activated(action: StringName)
@export var action: StringName = &"ENTER"
@export var display_name := "Broken Graveyard"
var enabled := true

func can_interact(player: Node) -> bool:
	return enabled and is_instance_valid(player) and player.has_method("can_world_interact") and player.can_world_interact()

func get_prompt() -> String:
	return "%s · %s  [E]" % [action, display_name]

func interact(player: Node) -> bool:
	if not can_interact(player): return false
	activated.emit(action)
	return true
