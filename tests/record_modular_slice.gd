extends SceneTree
## Real engine capture driver. Legal drawn cards and real movement; no HP/Focus/RNG edits.
## Run with Godot --write-movie <path>.avi --fixed-fps 30 --script this file.
const TURNS := preload("res://scripts/combat/slice_turn_controller.gd")
var world: Node
var started := 0.0
var elapsed := 0.0
var milestones: Array[Dictionary] = []

func _initialize() -> void:
	_run.call_deferred()

func pause(seconds: float) -> void:
	await create_timer(seconds).timeout

func _process(delta: float) -> bool:
	elapsed += delta
	return false

func mark(label: String) -> void:
	milestones.append({"time": snappedf(elapsed, 0.01), "state": label})
	print("CAPTURE · %.2f · %s" % [elapsed, label])

func _run() -> void:
	set_meta("slice_qa_no_save", true)
	set_meta("slice_force_drop", true)
	world = load("res://scenes/main.tscn").instantiate()
	root.add_child(world)
	current_scene = world
	await pause(0.2)
	world.events.occurred.connect(func(id, _payload):
		if id in [&"enemy_attack_started", &"enemy_collapsed", &"enemy_reassembled", &"echo_spawned", &"echo_absorbed", &"special_loot_spawned", &"loot_picked_up"]: mark(String(id)))
	mark("player_idle")
	await pause(1.1)
	Input.action_press("world_right")
	mark("walk_and_foreground_occlusion")
	while world.player.position.x < 350: await physics_frame
	Input.action_release("world_right")
	Input.action_press("world_interact")
	await physics_frame
	await physics_frame
	Input.action_release("world_interact")
	Input.action_press("world_right")
	while not world.encounter_started: await physics_frame
	Input.action_release("world_right")
	mark("skeleton_idle_and_soft_lock")
	while world.turns.phase != TURNS.Phase.PLAYER_TURN: await physics_frame
	world.hud.confirm_button.pressed.emit()
	await pause(0.35)
	var c: CombatState = world.combat
	for turn in range(90):
		if c.finished: break
		var order: Array = ["RESTORE", "OBSERVE", "STRIKE", "SHATTER", "STABILIZE", "BIND"]
		if c.bone_remains: order = ["SHATTER", "STRIKE", "BIND", "RESTORE", "STABILIZE"]
		for action in order:
			for card in c.deck.hand.duplicate():
				if card.name != action or not c.can_use(action, int(card.instance_id)): continue
				var reserve: int = c.reaction_cost() if c.can_react() and c.intent.kind == "physical" and not c.bone_remains else 0
				if action == "RESTORE" and c.hp > 42: continue
				if action == "OBSERVE" and c.intent_clarity >= 2: continue
				if action == "SHATTER" and c.enemy.structure <= 0 and not c.bone_remains: continue
				if action == "STABILIZE" and int(c.corruption.get(c.dominant_corruption_family(), 0)) < 20: continue
				if c.focus - c.card_cost(card) < reserve and action != "RESTORE": continue
				var before := c.bone_remains
				world._invoke(int(card.instance_id), "hp" if action == "RESTORE" else "")
				await pause(0.16)
				if not before and c.bone_remains:
					await pause(1.2)
					if OS.get_environment("SLICE_CAPTURE_REASSEMBLY") == "1":
						for round_index in range(3):
							world.turns.end_turn()
							await pause(0.7)
						await pause(1.2)
						mark("three_completed_rounds_reassembled")
						print("REASSEMBLY_CAPTURE_RESULT: ", JSON.stringify({"remains": c.bone_remains, "hp": c.enemy.hp, "structure": c.enemy.structure, "echo": world.manager.state.echo, "rolls": world.rewards.roller.roll_history.size()}))
						quit(0 if not c.bone_remains and c.enemy.hp == 12 and world.manager.state.echo == 15 else 1)
						return
				if c.finished: break
			if c.finished: break
		if c.finished: break
		for card in c.deck.hand:
			if card.name in (["SHATTER", "STRIKE"] if c.bone_remains else ["STRIKE", "DEFLECT"]): world._retain(int(card.instance_id))
		world.hud.end_button.pressed.emit()
		mark("enemy_action_round_%d" % c.turn)
		await pause(0.38)
		if c.turn_ending: world.turns.react(c.can_react())
		await pause(0.48 if not c.bone_remains else 0.12)
	if not world.encounter_cleared:
		push_error("Capture failed to clear using legal cards")
		quit(1)
		return
	await pause(0.8)
	mark("movement_restored")
	var loot: Node2D = world.loot_layer.get_child(0)
	Input.action_press("world_right")
	while world.player.global_position.distance_to(loot.global_position) > 68: await physics_frame
	Input.action_release("world_right")
	await pause(0.65)
	mark("pickup_prompt")
	Input.action_press("world_interact")
	await physics_frame
	await physics_frame
	Input.action_release("world_interact")
	await pause(0.35)
	world.hud.show_bag()
	await pause(0.65)
	world.hud.close_overlay()
	await pause(0.25)
	mark("pickup_saved_to_run")
	if world.manager.state.world_inventory.get("relic.weathered_chisel", 0) != 1: push_error("Capture pickup failed")
	print("CAPTURE_RESULT: ", JSON.stringify({"duration": elapsed, "milestones": milestones, "echo": world.manager.state.echo, "inventory": world.manager.state.world_inventory}))
	quit()
