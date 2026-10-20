extends SceneTree
var failures: Array[String] = []
var checks := 0

func _initialize() -> void:
	_run.call_deferred()

func check(value: bool, message: String) -> void:
	checks += 1
	if not value: failures.append(message)

func wait_frames(count := 3) -> void:
	for i in range(count): await physics_frame

func _run() -> void:
	set_meta("slice_qa_no_save", true)
	var world: Node2D = load("res://scenes/main.tscn").instantiate()
	root.add_child(world)
	await wait_frames()
	var environment: Node = world.get_node("Environment")
	for layer in ["GroundTileMap", "StructureLayer", "PropLayer", "ForegroundLayer", "FogLayer", "LightingLayer"]:
		check(environment.has_node(layer), "modular layer exists: " + layer)
	for layer in ["CharacterLayer", "LootLayer", "VFXLayer"]: check(world.has_node(layer), "runtime layer exists: " + layer)
	var ground: TileMapLayer = environment.get_node("GroundTileMap")
	check(ground.get_used_cells().size() == 135, "real editable tile cells replace the full background")
	var materials: Dictionary = {}
	for cell in ground.get_used_cells(): materials[ground.terrain_at(cell)] = true
	var blend: TileMapLayer = environment.get_node("GroundBlendLayer")
	for cell in blend.get_used_cells(): materials[blend.terrain_at(cell)] = true
	check(materials.size() == 6, "all six terrain materials are actually used")
	check(environment.get_node("PropLayer").get_child_count() >= 14, "props are individual reusable scene instances")
	check(world.y_sort_enabled and world.get_node("CharacterLayer").y_sort_enabled and environment.y_sort_enabled and environment.get_node("PropLayer").y_sort_enabled, "feet pivots sort actors and props in a common nested Y-sort domain")
	check(not environment.has_node("BackgroundGround/Foundation"), "no baked full-scene backdrop participates in runtime")
	var fence: Node2D = environment.get_node("StructureLayer/Fence_N_0")
	var footprint: SegmentShape2D = environment.get_node("StructureLayer/StructureFootprints/Fence_N_0").shape
	check(footprint.a.is_equal_approx(fence.visual.get_node("SocketA").global_position) and footprint.b.is_equal_approx(fence.visual.get_node("SocketB").global_position), "fence collision follows the actual projected feet sockets")
	var fence_art: Sprite2D = fence.visual.get_node("Artwork")
	check(is_equal_approx(fence_art.scale.x, fence_art.scale.y), "fence artwork is not stretched to fake collision alignment")
	var rail: Node2D = environment.get_node("ForegroundLayer/ApproachRail")
	var original: Vector2 = world.player.position
	world.player.position = Vector2(rail.position.x, rail.position.y - 30)
	await create_timer(0.4).timeout
	check(rail.visual.modulate.a > 0.3 and rail.visual.modulate.a < 0.8, "foreground partially occludes but fades enough to preserve player readability")
	world.player.position = original
	await create_timer(0.4).timeout
	check(rail.visual.modulate.a > 0.9, "occluder restores when the player leaves")
	check(environment.get_node("LightingLayer").find_child("EnvironmentTint", true, false) is CanvasModulate, "environment tint is an independent engine layer")
	check(environment.get_node("LightingLayer").find_child("GraveyardLocalLight", true, false) is PointLight2D, "local light influences actual lit canvas sprites")
	for actor in [world.player, world.skeleton]:
		var visual: Node = actor.get_node("VisualRoot").get_child(0)
		var animator := visual.find_child("AnimationPlayer", true, false) as AnimationPlayer
		check(visual.find_child("Rig", true, false) is Skeleton2D and visual.find_children("*", "Bone2D", true, false).size() >= 20, "real Skeleton2D/Bone2D rig, not an empty animation wrapper")
		check(visual.find_child("ContactShadow", true, false) is Sprite2D, "actor has a separate contact shadow")
		check(animator != null, "actor uses a real AnimationPlayer")
		if animator != null:
			var actions: Array = ["idle", "walk", "turn"] if actor == world.player else ["idle", "walk", "attack", "hit", "collapse", "remains", "reassembly"]
			for action in actions:
				check(animator.has_animation(action) and animator.get_animation(action).get_track_count() > 0, "authored animation tracks: " + action)
	var player_visual: Node = world.player.get_node("VisualRoot").get_child(0)
	var enemy_visual: Node = world.skeleton.get_node("VisualRoot").get_child(0)
	var weapon: Bone2D = enemy_visual.find_child("weapon", true, false)
	check(weapon != null and weapon.get_parent().name == "hand_l", "weapon grip is genuinely parented to the holding hand bone")
	var enemy_animator: AnimationPlayer = enemy_visual.get_node("AnimationPlayer")
	enemy_animator.play("attack")
	for sample in [0.0, 0.18, 0.34, 0.58]:
		enemy_animator.seek(sample, true)
		check(weapon.global_position.distance_to(weapon.get_parent().global_position) < 2, "weapon remains attached throughout the attack")
	enemy_visual.present_motion(Vector2.ZERO, Vector2.LEFT)
	check(player_visual.has_method("present_motion"), "player consumes semantic motion, not gameplay state")
	var before: Vector2 = world.player.position
	Input.action_press("world_right")
	await wait_frames(20)
	var locomotion := player_visual.find_child("AnimationPlayer", true, false) as AnimationPlayer
	if locomotion != null: check(locomotion.current_animation == "walk", "real movement selects the walk clip")
	if locomotion != null:
		var thigh: Bone2D = player_visual.get_node("FacingRoot/Rig/Root/pelvis/thigh_l")
		var angle := thigh.rotation
		await wait_frames(8)
		check(absf(thigh.rotation - angle) > 0.03, "walk actually moves the leg, not only the actor texture")
	Input.action_release("world_right")
	check(world.player.position.x > before.x + 35, "rig still follows real physics movement")
	Input.action_press("world_up")
	await wait_frames(20)
	Input.action_release("world_up")
	check(player_visual.back_view, "northward movement uses authored back-view body parts")
	Input.action_press("world_left")
	await wait_frames(20)
	Input.action_release("world_left")
	check(player_visual.get_node("FacingRoot").scale.x < 0 and not player_visual.back_view, "leftward turn mirrors the front rig instead of sliding a single sprite")
	world.turns.set_phase(preload("res://scripts/combat/slice_turn_controller.gd").Phase.COMBAT_ENTER)
	await wait_frames(2)
	before = world.player.position
	Input.action_press("world_right")
	await wait_frames(6)
	Input.action_release("world_right")
	check(world.player.position == before, "animation cannot defeat gameplay movement lock")
	world.queue_free()
	await wait_frames()
	for message in failures: push_error(message)
	print("MODULAR_SCENE_SMOKE: %s · %d checks" % ["PASS" if failures.is_empty() else "FAIL", checks])
	quit(0 if failures.is_empty() else 1)
