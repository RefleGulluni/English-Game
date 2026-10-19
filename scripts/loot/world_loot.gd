extends Node2D

enum State { SPAWNING, IDLE, HIGHLIGHTED, PICKING_UP, COLLECTED }
var state := State.SPAWNING
var data: Resource
var instance_id := ""
var run: RunState
var events: Node
var ready_delay := 0.18

func bind(item: Resource, unique_id: String, run_state: RunState, bus: Node) -> void:
	data = item
	instance_id = unique_id
	run = run_state
	events = bus
	get_node("DataBinding").set_meta("loot_id", data.id)

func _process(delta: float) -> void:
	if state != State.SPAWNING: return
	ready_delay -= delta
	if ready_delay <= 0: state = State.IDLE

func can_interact(player: Node) -> bool:
	return state in [State.IDLE, State.HIGHLIGHTED] and run != null and is_instance_valid(player) and player.has_method("can_world_interact") and player.can_world_interact() and global_position.distance_to(player.global_position) <= 82.0

func get_prompt() -> String:
	return "PICK UP · %s  [E]" % data.display_name if data != null else ""

func set_highlighted(value: bool) -> void:
	if state not in [State.IDLE, State.HIGHLIGHTED]: return
	state = State.HIGHLIGHTED if value else State.IDLE
	$HighlightRoot.visible = value
	if value and events != null: events.publish(&"loot_highlighted", {"loot_id": data.id, "instance_id": instance_id})

func interact(player: Node) -> bool:
	if not can_interact(player): return false
	state = State.PICKING_UP
	# Atomic state + instance ledger prevents double key/click and duplicate inventory rewards.
	if not run.claim_world_loot(instance_id, data.id):
		state = State.COLLECTED
		hide()
		return false
	state = State.COLLECTED
	hide()
	if events != null: events.publish(&"loot_picked_up", {"loot_id": data.id, "name": data.display_name, "instance_id": instance_id, "position": global_position})
	return true
