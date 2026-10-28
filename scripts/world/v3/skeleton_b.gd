class_name SkeletonB
extends Node2D
## The real Grave Skeleton, design B "余裹者" (D-037, animations D-053 – D-057), playing the
## character group's frame strips. Replaces skeleton_placeholder.gd with the same interface:
## present(snapshot) / hit() / lunge() from the rule layer, plus face(), walk_to(), approach()
## and wander() (pacing about its grave until a fight starts, so it never just stands there).
## Presentation only: it reads the semantic snapshot from skeleton_logic.gd and never changes it.
##
## Rules learned in the preview room (scenes/prototypes/skeleton_anim/):
## - every animation plays its newest returned version (the highest _vN in timing.json);
## - a walk is start step → walk loop → stop step; the stop step only fits after walk frame 8,
##   so walk_to() rounds every walk to whole strides of 40 px (8 frames × 5 px at 50 px/s);
## - collapse plays the strip for its facing when one exists; reassembly rises facing front.

const ANIM := "res://art/character_design/enemies/skeleton/anim/"
const SHADOW_COLOR := Color(0.03, 0.03, 0.05, 0.45)
const STRIDE := 40.0 # one full walk cycle
const WALK_SPEED := 50.0
const CLEARED_TINT := Color(0.62, 0.62, 0.62)

## The node walk_to() moves (the skeleton's root); the strip itself always stays on its feet.
var mover: Node2D
var facing := "front"
## idle · start · walk · stop · hit · collapse · remains · reassemble
var action := "idle"
var _mode := "standing"
var _strip: SpriteStrip
var _target := Vector2.ZERO
var _shake := 0.0
## Spots it paces between while nobody fights it (whole strides apart, in straight lines).
var _wander_spots: Array[Vector2] = []
var _wander_wait := 0.0
## An approach asked for while it was busy; taken as soon as it stands still again.
var _approach: Array = []
## A stand-off asked for while it was busy: [x to stand at, point to look at].
var _stand_off: Array = []
## While a word is still flying at it, the hit and the change of state wait until it lands.
var _hold := 0.0
var _held_hit := false
var _held_snapshot := {}
## BONE CUT in progress: where it started, which way it lunges, how long it has run.
var _attack_from := Vector2.ZERO
var _attack_dir := 0.0
var _attack_t := 0.0
var _attack_key := ""
## Where to look once the current walk ends (the stand-off may walk away from the hero first).
var _look_after_walk := Vector2.INF

static var _keys := {}


func _ready() -> void:
	if _keys.is_empty():
		_keys = JSON.parse_string(FileAccess.get_file_as_string(ANIM + "timing.json")).animations
	add_child(PixelArt.ellipse_sprite(34, 12, SHADOW_COLOR, Vector2(0, -3)))
	_strip = SpriteStrip.new()
	add_child(_strip)
	_strip.finished.connect(_on_finished)
	_play("idle_" + facing)
	_strip.random_phase()


## Keeps hits and state changes (collapse, reassembly) back for a moment: the rules resolve a word
## at once, but on screen it first has to reach the skeleton (scripts/world/v3/combat_view.gd).
func hold_for(seconds: float) -> void:
	_hold = seconds


func present(snapshot: Dictionary) -> void:
	if _hold > 0.0:
		_held_snapshot = snapshot
		return
	var mode := str(snapshot.get("mode", "standing"))
	if mode == _mode:
		return
	var was := _mode
	_mode = mode
	_strip.modulate = CLEARED_TINT if mode == "cleared" else Color.WHITE
	if mode == "standing":
		_switch("reassemble", "reassemble_front")
	elif was == "standing":
		# Each facing collapses its own way once those strips exist (request §21); the front one until then.
		_switch("collapse", "collapse_" + facing if _keys.has("skeleton_B_collapse_" + facing) else "collapse_front")


func present_motion(_velocity: Vector2, _facing: Vector2) -> void:
	pass


## Took damage: the hit strip while standing, a 1 px shudder while it lies in pieces.
func hit() -> void:
	if _hold > 0.0:
		_held_hit = true
		return
	if _mode != "standing":
		_shake = 0.18
	elif action == "idle" or action == "hit":
		_switch("hit", "hit_" + facing)


## The enemy's attack: lean a few pixels toward the target and back (until attack strips exist).
func lunge(toward: Vector2) -> void:
	var dir := (toward - global_position).normalized()
	var tween := create_tween()
	tween.tween_property(_strip, "position", (dir * 8.0).round(), 0.12)
	tween.tween_property(_strip, "position", Vector2.ZERO, 0.2)


## BONE CUT (docs/COMBAT_ANIMATION_REQUEST.md §5): plays the attack strip for the side the hero is
## on while the whole skeleton steps one stride (40 px) in during the wind-up and back during the
## recovery. Returns the seconds until the hit frame, or 0 when that side's strip is not delivered
## (then it only leans in, as before).
func attack(toward: Vector2) -> float:
	var side := "right" if toward.x >= global_position.x else "left"
	_attack_key = "skeleton_B_attack_" + side
	if _mode != "standing" or action != "idle" or not _keys.has(_attack_key):
		lunge(toward)
		return 0.0
	facing = side
	_attack_from = mover.position
	_attack_dir = 1.0 if side == "right" else -1.0
	_attack_t = 0.0
	_switch("attack", "attack_" + side)
	return float(_keys[_attack_key].key_frame.time_ms) / 1000.0


## Turns to look along v (only while standing still).
func face(v: Vector2) -> void:
	var dir := dir_name(v)
	if dir != facing and action == "idle" and _mode == "standing":
		facing = dir
		_play("idle_" + facing)


## Paces between spots (positions in the mover's parent) with pauses and the odd look around.
func wander(spots: Array[Vector2]) -> void:
	_wander_spots = spots
	_wander_wait = randf_range(1.0, 2.5)


func stop_wander() -> void:
	_wander_spots.clear()


## Walks up to target and stops keep_away short of it (whole strides, at most two), or only turns
## when it is already close. If it is busy (mid-step, being hit) it does so right after.
func approach(target: Vector2, keep_away: float) -> void:
	if _mode != "standing":
		return
	if action != "idle":
		_approach = [target, keep_away]
		return
	var to := target - mover.position
	var axis := Vector2(signf(to.x), 0) if absf(to.x) >= absf(to.y) else Vector2(0, signf(to.y))
	var gap := maxf(0.0, absf(to.dot(axis)) - keep_away)
	if gap >= STRIDE:
		walk_to(mover.position + axis * minf(gap, 2 * STRIDE))
	else:
		face(to)


## Combat stand-off (KB Combat Presentation: the two face each other across the room, never
## above / below each other, so fights only need the left and right strips): walks sideways in
## whole strides to stand at x, then turns to look at look_at. Waits until it is free when busy.
func stand_off(x: float, look_at: Vector2) -> void:
	if _mode != "standing":
		return
	if action != "idle":
		_stand_off = [x, look_at]
		return
	var strides := roundi((x - mover.position.x) / STRIDE)
	var side := Vector2(signf(look_at.x - x), 0)
	if strides == 0:
		face(side)
		return
	_look_after_walk = side
	walk_to(mover.position + Vector2(strides * STRIDE, 0))


## Walks straight toward target along its main axis, in whole strides, and stops there.
func walk_to(target: Vector2) -> void:
	if mover == null or action != "idle" or _mode != "standing":
		return
	var to := target - mover.position
	var axis := Vector2(signf(to.x), 0) if absf(to.x) >= absf(to.y) else Vector2(0, signf(to.y))
	var strides := floorf(absf(to.dot(axis)) / STRIDE)
	if strides < 1:
		face(to)
		return
	facing = dir_name(axis)
	_target = mover.position + axis * strides * STRIDE
	_switch("start", "walk_start_" + facing)


static func dir_name(v: Vector2) -> String:
	if absf(v.x) >= absf(v.y):
		return "right" if v.x > 0 else "left"
	return "front" if v.y > 0 else "back"


func _process(delta: float) -> void:
	if _hold > 0.0:
		_hold -= delta
		if _hold <= 0.0:
			if _held_hit:
				_held_hit = false
				hit()
			if not _held_snapshot.is_empty():
				var snapshot := _held_snapshot
				_held_snapshot = {}
				present(snapshot)
	if action == "idle" and _mode == "standing" and not _wander_spots.is_empty():
		_wander_wait -= delta
		if _wander_wait <= 0.0:
			_wander_step()
	if action == "attack":
		_attack_t += delta * 1000.0
		var data: Dictionary = _keys[_attack_key]
		var hit := float(data.key_frame.time_ms)
		var durations: Array = data.durations_ms
		var back_from := hit + float(durations[4]) + float(durations[5]) # holds through the follow-through
		var total := float(data.duration_ms)
		var advance := float(data.get("expected_program_advance_px", 40))
		var share := clampf(_attack_t / hit, 0.0, 1.0) if _attack_t < back_from else 1.0 - clampf((_attack_t - back_from) / (total - back_from), 0.0, 1.0)
		mover.position = _attack_from + Vector2(_attack_dir * roundf(advance * share), 0)
	if action == "walk":
		mover.position = mover.position.move_toward(_target, WALK_SPEED * delta)
		if mover.position == _target:
			_switch("stop", "walk_stop_" + facing)
	if _shake > 0.0:
		_shake -= delta
		_strip.position.x = 0.0 if _shake <= 0.0 else (1.0 if int(_shake * 40.0) % 2 == 0 else -1.0)


## Walk to a spot straight along a row or column from here, or now and then just look around.
func _wander_step() -> void:
	_wander_wait = randf_range(2.0, 4.5)
	var reachable: Array[Vector2] = []
	for spot in _wander_spots:
		var to := spot - mover.position
		if to != Vector2.ZERO and (is_zero_approx(to.x) or is_zero_approx(to.y)):
			reachable.append(spot)
	if reachable.is_empty() or randf() < 0.3:
		face(Vector2.from_angle(randi_range(0, 3) * PI / 2))
	else:
		walk_to(reachable.pick_random())


## What follows each one-shot strip.
func _on_finished() -> void:
	match action:
		"start":
			_switch("walk", "walk_" + facing)
		"stop", "hit", "reassemble", "attack":
			if action == "reassemble":
				facing = "front"
			if action == "attack":
				mover.position = _attack_from
			_switch("idle", "idle_" + facing)
			if _look_after_walk != Vector2.INF:
				face(_look_after_walk)
				_look_after_walk = Vector2.INF
			if not _stand_off.is_empty():
				var wanted := _stand_off
				_stand_off = []
				stand_off(wanted[0], wanted[1])
			if not _approach.is_empty():
				var queued := _approach
				_approach = []
				approach(queued[0], queued[1])
		"collapse":
			_switch("remains", "remains_idle")


func _switch(next_action: String, anim: String) -> void:
	action = next_action
	_play(anim)


## Plays the newest returned version of an animation (the highest _vN).
func _play(anim: String) -> void:
	var key := "skeleton_B_" + anim
	for n in range(9, 1, -1):
		if _keys.has("%s_v%d" % [key, n]):
			_strip.load_strip(ANIM, "%s_v%d" % [key, n])
			return
	_strip.load_strip(ANIM, key)
