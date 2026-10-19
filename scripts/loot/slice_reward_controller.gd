extends Node

const WORLD_LOOT := preload("res://scenes/loot/WorldLoot.tscn")
@export var chisel: Resource
var run: RunState
var events: Node
var player: Node2D
var loot_parent: Node2D
var interactions: Node
var roller := preload("res://scripts/loot/drop_reward_resolver.gd").new()
var qa_force_drop := true # Milestone-01 acceptance mode; normal mode already uses 10%.
var encounter_id := "scene.cemetery.broken_graveyard:skeleton:0"

func bind(state: RunState, bus: Node, actor: Node2D, container: Node2D, interaction_system: Node) -> void:
	run = state
	events = bus
	player = actor
	loot_parent = container
	interactions = interaction_system
	roller.setup(run.seed_value)

func echo_once(suffix: String, amount: int, location: Vector2) -> void:
	var reward_id := encounter_id + ":" + suffix
	if not run.grant_world_echo_once(reward_id, amount): return
	# Commit first. Removing VFX, changing scene or interrupting animation cannot erase Echo.
	events.publish(&"echo_spawned", {"reward_id": reward_id, "amount": amount, "position": location, "target": player.global_position})
	var timer := Timer.new()
	add_child(timer)
	timer.one_shot = true
	timer.timeout.connect(func():
		events.publish(&"echo_absorbed", {"reward_id": reward_id, "amount": amount})
		timer.queue_free())
	timer.start(0.45)

func collapsed(enemy_logic: Node) -> void:
	# Only the authoritative CombatState transition drives rewards, never an art event.
	if enemy_logic.combat == null or enemy_logic.combat.finished or not enemy_logic.combat.bone_remains: return
	var location: Vector2 = enemy_logic.get_parent().get_node("LootAnchor").global_position
	var first := not run.world_reward_ledger.has(encounter_id + ":disperse")
	echo_once("disperse", 15, location)
	if not first: return
	var item = roller.roll(enemy_logic.data.ecology_tags, [chisel], qa_force_drop and OS.is_debug_build())
	# A failed special roll has no player-facing notification.
	if item == null: return
	var loot := WORLD_LOOT.instantiate()
	loot_parent.add_child(loot)
	loot.global_position = location + Vector2(36, 24)
	loot.bind(item, encounter_id + ":special:0", run, events)
	interactions.register(loot)
	events.publish(&"special_loot_spawned", {"loot_id": item.id, "instance_id": loot.instance_id, "position": loot.global_position})

func cleared(location: Vector2) -> void:
	echo_once("remains_cleared", 5, location)
