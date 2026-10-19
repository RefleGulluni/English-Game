extends SceneTree

const FIXTURE := preload("res://tests/mechanics_fixture.gd")
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

func _run() -> void:
	set_meta("slice_qa_no_save", true) # Also protects the real profile through scene reloads.
	set_meta("slice_force_drop", false)
	var scene := load("res://scenes/main.tscn") as PackedScene
	var world := scene.instantiate()
	root.add_child(world)
	current_scene = world
	await wait_frames()
	world._enter_graveyard(&"ENTER")
	world.start_encounter()
	await create_timer(0.8).timeout
	world.hud.confirm_button.pressed.emit()
	# Explicit isolated reaction fixture, separate from the legal playthrough suite.
	world.combat.deck.hand.append(world.combat.deck.make_card("DEFLECT"))
	world.combat.focus = 1
	world.combat.intent = {"word": "BONE CUT", "kind": "physical", "damage": 5, "family": "Obscurity"}
	world.hud.end_button.pressed.emit()
	check(world.turns.phase == TURNS.Phase.ENEMY_TURN and world.hud.reaction_box.visible, "physical action opens real reaction controls")
	world.hud.show_lexicon()
	world.hud.close_overlay()
	check(world.combat.turn_ending and world.hud.reaction_box.visible, "Lexicon does not consume or bypass a reaction window")
	await wait_frames()
	var rect: Rect2 = world.hud.deflect_button.get_global_rect()
	check(rect.size.x > 80 and rect.end.y <= 720, "DEFLECT is actually inside the viewport")
	var directory := OS.get_environment("SLICE_QA_DIR")
	if not directory.is_empty() and DisplayServer.get_name() != "headless":
		await RenderingServer.frame_post_draw
		get_root().get_texture().get_image().save_png(directory.path_join("reaction.png"))
	world.hud.deflect_button.pressed.emit()
	check(world.combat.metrics.deflect_uses == 1 and world.turns.phase == TURNS.Phase.PLAYER_TURN, "DEFLECT resolves and round returns control")
	world.combat.hp = 0
	world.combat._finish_battle(false)
	await wait_frames()
	check(world.turns.phase == TURNS.Phase.DEFEAT and world.hud.overlay_open and world.player.input_locked, "defeat provides explicit replay instead of a soft-lock")
	# Restart a real current_scene, not a second separate project or a synthetic tree.
	world.restart()
	await wait_frames(10)
	world = current_scene
	check(world != null and not world.encounter_started and world.manager.state.hp == 50 and world.manager.state.world_inventory.is_empty(), "real scene reload starts a clean Run")
	world._enter_graveyard(&"ENTER")
	world.start_encounter()
	await create_timer(0.8).timeout
	world.hud.confirm_button.pressed.emit()
	# Force only the RNG boundary in this unit fixture, not the acceptance path.
	world.rewards.roller.special_chance = 0.0
	world.combat.enemy.hp = 1
	world.combat.focus = 20
	FIXTURE.play(world.combat, "STRIKE")
	check(world.manager.state.echo == 15 and world.get_node("WorldLoot").get_child_count() == 0, "no-drop mode still commits Echo, creates no fake loot object")
	FIXTURE.play(world.combat, "SHATTER")
	FIXTURE.play(world.combat, "SHATTER")
	await create_timer(0.8).timeout
	check(world.encounter_cleared and not world.player.input_locked and world.manager.state.echo == 20, "no special loot never prevents combat exit")
	check(not world.hud.toast.text.contains("glint") and not world.event_trace.any(func(row): return row.event == "special_loot_spawned"), "failed special roll has no misleading empty-loot notification")
	world.queue_free()
	await wait_frames()
	remove_meta("slice_qa_no_save")
	remove_meta("slice_force_drop")
	for message in failures: push_error(message)
	print("SLICE_LIFECYCLE_SMOKE: %s · %d checks" % ["PASS" if failures.is_empty() else "FAIL", checks])
	quit(0 if failures.is_empty() else 1)
