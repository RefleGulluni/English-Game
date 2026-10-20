extends Node

@export var data: Resource
var combat: CombatState
var events: Node
var previous: Dictionary = {}
var unresolved := false

func bind(model: CombatState, bus: Node) -> void:
	combat = model
	events = bus
	combat.changed.connect(sync)
	combat.enemy_collapsed.connect(_collapse)
	combat.enemy_reassembled.connect(_reassemble)
	previous.clear()
	if events != null: events.publish(&"enemy_spawned", {"enemy_id": data.id, "position": get_parent().global_position})
	sync()

func snapshot() -> Dictionary:
	if combat == null: return {"mode": "standing", "hp": data.max_hp, "structure": data.structure}
	return {"mode": "cleared" if combat.finished and combat.hp > 0 else ("remains" if combat.bone_remains else "standing"), "hp": combat.enemy.get("hp", 0), "structure": combat.enemy.get("structure", 0), "integrity": combat.remains_hp, "reassemble_in": combat.reassembly_countdown}

func sync() -> void:
	if combat == null or combat.enemy.is_empty(): return
	var current := snapshot()
	if not previous.is_empty():
		if int(current.hp) < int(previous.hp): events.publish(&"enemy_damaged", {"enemy_id": data.id, "component": "hp", "amount": int(previous.hp) - int(current.hp)})
		if int(current.integrity) < int(previous.integrity): events.publish(&"enemy_damaged", {"enemy_id": data.id, "component": "integrity", "amount": int(previous.integrity) - int(current.integrity)})
		if int(current.structure) < int(previous.structure): events.publish(&"enemy_damaged", {"enemy_id": data.id, "component": "structure", "amount": int(previous.structure) - int(current.structure)})
		if current.structure != previous.structure: events.publish(&"enemy_structure_changed", {"enemy_id": data.id, "value": current.structure})
		if int(previous.structure) > 0 and int(current.structure) == 0: events.publish(&"enemy_exposed", {"enemy_id": data.id, "position": get_parent().global_position + Vector2(0, -65)})
	previous = current
	# Presentation receives a semantic snapshot. It cannot change the combat model.
	for child in get_parent().get_node("VisualRoot").get_children():
		if child.has_method("present"): child.present(current.duplicate(true))

func _collapse() -> void:
	unresolved = true
	sync()
	events.publish(&"enemy_collapsed", {"enemy_id": data.id, "position": get_parent().get_node("LootAnchor").global_position})

func _reassemble() -> void:
	unresolved = false
	sync()
	events.publish(&"enemy_reassembled", {"enemy_id": data.id, "position": get_parent().global_position})

func unresolved_snapshot() -> Dictionary:
	# Future cross-scene interface only; this milestone does not simulate unloaded scenes.
	return {"enemy_id": data.id, "unresolved": unresolved, "countdown": combat.reassembly_countdown if combat != null else 0}
