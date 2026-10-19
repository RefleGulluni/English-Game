extends SceneTree

const TURNS := preload("res://scripts/combat/slice_turn_controller.gd")
var failures: Array[String] = []
var checks := 0

func _initialize() -> void:
	_run.call_deferred()

func check(value: bool, message: String) -> void:
	checks += 1
	if not value: failures.append(message)

func wait_frames(count: int = 3) -> void:
	for i in range(count): await physics_frame

func capture(world: Node, filename: String) -> void:
	await wait_frames(2)
	if world.hud.combat_panel.visible:
		var rect: Rect2 = world.hud.end_button.get_global_rect()
		check(rect.size.x > 100 and rect.end.y <= 720 and rect.position.y >= 0, "end turn is a visible clickable button inside the viewport")
		if world.hud.reaction_box.visible:
			var reaction_rect: Rect2 = world.hud.deflect_button.get_global_rect()
			check(reaction_rect.size.x > 80 and reaction_rect.end.y <= 720, "reaction button remains visible and clickable")
	var directory := OS.get_environment("SLICE_QA_DIR")
	if directory.is_empty() or DisplayServer.get_name() == "headless": return
	await RenderingServer.frame_post_draw
	check(world.get_viewport().get_texture().get_image().save_png(directory.path_join(filename + ".png")) == OK, "viewport capture saved")

func _fight(world: Node) -> void:
	var c: CombatState = world.combat
	world.hud.confirm_button.pressed.emit()
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
				var before_echo: int = world.manager.state.echo
				world._invoke(int(card.instance_id), "hp" if action == "RESTORE" else "")
				if before_echo == 0 and world.manager.state.echo == 15:
					check(c.bone_remains and c.reassembly_countdown == 3 and world.player.input_locked, "collapse grants 15 Echo before final defeat; world stays locked")
					check(world.get_node("WorldLoot").get_child_count() == 1 and world.manager.state.world_inventory.is_empty(), "special reward is a world object, not instant inventory")
					await capture(world, "remains_loot")
				if c.finished: break
			if c.finished: break
		if c.finished: break
		for card in c.deck.hand:
			if card.name in (["SHATTER", "STRIKE"] if c.bone_remains else ["STRIKE", "DEFLECT"]): world._retain(int(card.instance_id))
		world.hud.end_button.pressed.emit()
		if c.turn_ending:
			await capture(world, "reaction")
			world.hud.deflect_button.pressed.emit() if c.can_react() else world.turns.react(false)
		await wait_frames(1)

func _run() -> void:
	var world := (load("res://scenes/main.tscn") as PackedScene).instantiate()
	world.set_meta("qa_no_save", true)
	root.add_child(world)
	await wait_frames()
	check(world.turns.phase == TURNS.Phase.EXPLORATION and not world.player.input_locked, "main scene starts in free exploration")
	world.events.publish(&"enemy_collapsed", {"enemy_id": "enemy.grave_skeleton", "position": Vector2.ZERO})
	check(world.manager.state.echo == 0 and world.get_node("WorldLoot").get_child_count() == 0, "presentation event alone cannot award gameplay rewards")
	check(not world.hud.combat_panel.visible and not world.hud.survival.text.contains("FOCUS"), "exploration HUD has no Focus/card wall")
	await capture(world, "approach")
	Input.action_press("world_right")
	await wait_frames(42)
	Input.action_release("world_right")
	await wait_frames()
	check(world.player.position.x > 330 and world.hud.prompt.text.contains("ENTER"), "real physics movement approaches contextual entrance")
	Input.action_press("world_interact")
	await wait_frames(2)
	Input.action_release("world_interact")
	await wait_frames(2)
	check(world.entered, "single interaction key enters Broken Graveyard")
	Input.action_press("world_right")
	for frame in range(250):
		await physics_frame
		if world.encounter_started: break
	Input.action_release("world_right")
	await create_timer(0.8).timeout
	check(world.encounter_started and world.turns.phase == TURNS.Phase.PLAYER_TURN and world.hud.combat_panel.visible, "approach enters same-scene combat after soft transition")
	var position_before: Vector2 = world.player.position
	Input.action_press("world_right")
	await wait_frames(10)
	Input.action_release("world_right")
	check(world.player.position == position_before and world.hud.prompt.text.is_empty(), "world movement and interaction prompts soft-lock during combat")
	world.hud.show_lexicon()
	await wait_frames()
	var body: Label = world.hud.overlay.find_child("Body", true, false)
	check(not body.text.contains("Known meaning") and not body.text.contains("put separated"), "Lexicon does not reveal unknown answers")
	world.hud.close_overlay()
	await capture(world, "combat")
	await _fight(world)
	await create_timer(0.9).timeout
	check(world.combat.finished and world.encounter_cleared and world.combat.hp > 0, "legal drawn-card playthrough clears Skeleton and Bone Remains")
	check(world.turns.phase == TURNS.Phase.EXPLORATION and not world.player.input_locked and not world.hud.combat_panel.visible, "camera/HUD/input restore without a scene switch or forced pickup")
	check(world.manager.state.echo == 20 and world.rewards.roller.roll_history.size() == 1, "15+5 Echo, exactly one special roll even with potential reassembly")
	world.rewards.collapsed(world.skeleton.get_node("Logic"))
	check(world.manager.state.echo == 20 and world.rewards.roller.roll_history.size() == 1 and world.get_node("WorldLoot").get_child_count() == 1, "replayed collapse event cannot farm Echo or special rolls")
	check(world.manager.state.world_inventory.is_empty(), "loot is not automatically absorbed")
	var loot: Node2D = world.get_node("WorldLoot").get_child(0)
	check(not loot.can_interact(world.player), "far-away pickup denied")
	Input.action_press("world_right")
	for frame in range(150):
		await physics_frame
		if world.player.position.distance_to(loot.position) < 70: break
	Input.action_release("world_right")
	await wait_frames()
	check(world.hud.prompt.text.contains("PICK UP"), "nearby real loot shows contextual PICK UP")
	await capture(world, "pickup_prompt")
	Input.action_press("world_interact")
	await wait_frames(2)
	Input.action_release("world_interact")
	await wait_frames(3)
	check(world.manager.state.world_inventory.get("relic.weathered_chisel", 0) == 1 and not loot.visible, "manual E pickup commits reward to Run State")
	check(not loot.interact(world.player) and world.manager.state.world_inventory["relic.weathered_chisel"] == 1, "double pickup denied")
	world.hud.show_bag()
	await capture(world, "run_bag")
	world.hud.close_overlay()
	check(not world.player.input_locked, "closing bag resumes free movement")
	check(world.event_trace.any(func(row): return row.event == "echo_absorbed") and world.event_trace.any(func(row): return row.event == "loot_picked_up"), "VFX/audio event contract emitted")
	var effect_node := Node2D.new()
	var effect_scene := PackedScene.new()
	effect_scene.pack(effect_node)
	effect_node.free()
	world.get_node("PresentationRouter").vfx_cues["observe_started"] = effect_scene
	world.events.publish(&"observe_started", {"position": world.skeleton.global_position})
	check(world.get_node("PresentationRouter/VFXRoot").get_child_count() == 1 and world.manager.state.echo == 20, "art can plug a VFX scene into events without modifying gameplay")
	# Presentation can be removed without changing rewards or combat ownership.
	world.get_node("PresentationRouter").queue_free()
	world.skeleton.get_node("VisualRoot").queue_free()
	await wait_frames()
	check(world.manager.state.echo == 20 and world.manager.state.world_inventory.size() == 1, "presentation removal does not erase gameplay state")
	world.queue_free()
	await wait_frames()
	for message in failures: push_error(message)
	print("SLICE_WORLD_SMOKE: %s · %d checks" % ["PASS" if failures.is_empty() else "FAIL", checks])
	quit(0 if failures.is_empty() else 1)
