extends Node

# Instance-scoped event bus: world controllers own state, presentation only subscribes.
# Payloads contain IDs, positions and semantic values, never texture/audio/animation paths.
signal occurred(event_id: StringName, payload: Dictionary)
var sequence := 0

func _ready() -> void:
	add_to_group("gameplay_events")

func publish(event_id: StringName, payload: Dictionary = {}) -> void:
	sequence += 1
	var message := payload.duplicate(true)
	message["sequence"] = sequence
	message.make_read_only()
	occurred.emit(event_id, message)
