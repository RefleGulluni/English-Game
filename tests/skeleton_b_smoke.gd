extends SceneTree
## The real skeleton's presentation rules (scripts/world/v3/skeleton_b.gd): walks in whole strides
## through start → walk → stop, collapse → remains, reassemble → idle, hits only while standing.

var failures: Array[String] = []
var visual: SkeletonB
var strip: SpriteStrip


func check(value: bool, message: String) -> void:
	if not value: failures.append(message)


## Steps both the skeleton and its strip by hand, so the test does not depend on real time.
func run(seconds: float) -> void:
	for i in int(seconds / 0.02):
		strip._process(0.02)
		visual._process(0.02)


func _initialize() -> void:
	var root := Node2D.new()
	root.position = Vector2(200, 200)
	visual = SkeletonB.new()
	visual.mover = root
	root.add_child(visual)
	visual._ready()
	strip = visual.get_child(1)
	check(visual.action == "idle" and strip.current.begins_with("skeleton_B_idle_front"), "starts standing idle")
	check(strip.current == "skeleton_B_idle_front_v2", "plays the newest returned version")

	visual.walk_to(Vector2(105, 210))
	check(visual.action == "start" and strip.current.begins_with("skeleton_B_walk_start_left"), "a walk begins with the start step")
	run(0.28)
	check(root.position == Vector2(200, 200), "the start step stays in place")
	run(0.04)
	check(visual.action == "walk", "start step hands over to the walk loop")
	run(1.6)
	check(root.position == Vector2(120, 200), "walks 95 px as two whole 40 px strides, along its main axis: %s" % root.position)
	check(visual.action == "stop" and strip.current.begins_with("skeleton_B_walk_stop_left"), "arrival plays the stop step")
	run(0.32)
	check(visual.action == "idle" and strip.current.begins_with("skeleton_B_idle_left"), "stop step ends in the idle")

	visual.walk_to(Vector2(130, 200))
	check(visual.action == "idle", "less than a stride only turns, it does not walk")
	visual.hit()
	check(visual.action == "hit" and strip.current.begins_with("skeleton_B_hit_right"), "hit plays the strip for its facing")
	run(0.4)
	check(visual.action == "idle", "hit returns to idle")

	# Pacing about its grave: only straight-line walks between the spots, never off them.
	root.position = Vector2(200, 200)
	var spots: Array[Vector2] = [Vector2(200, 200), Vector2(120, 200), Vector2(120, 240), Vector2(200, 240)]
	visual.wander(spots)
	var walks := 0
	for i in 40:
		var was := root.position
		run(0.5)
		if root.position != was: walks += 1
		if visual.action == "idle":
			check(spots.has(root.position), "rests only on its spots: %s" % root.position)
	check(walks >= 1, "it walks about instead of only standing")
	# A fight starts while it is mid-step: it finishes the step, then walks up to the hero.
	while visual.action != "walk":
		run(0.02)
	visual.stop_wander()
	visual.approach(root.position + Vector2(0, -180), 56)
	check(visual.action == "walk", "an approach waits for the current walk to finish")
	run(6.0)
	check(visual.action == "idle" and visual.facing == "back", "and stands facing the hero")
	visual.hit()
	run(0.4)

	visual.present({"mode": "remains"})
	check(visual.action == "collapse", "falling apart plays the collapse")
	run(1.4) # the side and back collapses take 1.28 s
	check(visual.action == "remains" and strip.current == "skeleton_B_remains_idle", "collapse ends in the remains idle")
	visual.hit()
	check(visual.action == "remains", "hits on the remains only shudder")
	visual.present({"mode": "standing"})
	check(visual.action == "reassemble" and strip.current == "skeleton_B_reassemble_front_v5", "rising plays the newest reassembly")
	visual.approach(root.position + Vector2(-50, 0), 56)
	check(visual.action == "reassemble", "turning to the hero waits until it has risen")
	run(5.0)
	check(visual.action == "idle" and visual.facing == "left", "after rising it turns to the hero: %s" % visual.facing)
	visual.present({"mode": "remains"})
	check(visual.action == "collapse" and strip.current == "skeleton_B_collapse_left", "facing left it falls with the left collapse")
	run(1.4)
	visual.present({"mode": "cleared"})
	check(strip.modulate != Color.WHITE and visual.action == "remains", "a cleared skeleton stays as dimmed remains")

	root.free()
	if failures.is_empty():
		print("skeleton_b_smoke: PASS")
	else:
		for f in failures: print("FAIL: ", f)
	quit(1 if not failures.is_empty() else 0)
