class_name SkeletonB
extends Node2D
## The real Grave Skeleton, design B "余裹者" (D-037, animations D-053 – D-057), playing the
## character group's frame strips. Replaces skeleton_placeholder.gd with the same interface:
## present(snapshot) / hit() / lunge() from the rule layer, plus face() and walk_to().
## Presentation only: it reads the semantic snapshot from skeleton_logic.gd and never changes it.
##
## Rules learned in the preview room (scenes/prototypes/skeleton_anim/):
## - every animation plays its newest returned version (the highest _vN in timing.json);
## - a walk is start step → walk loop → stop step; the stop step only fits after walk frame 8,
##   so walk_to() rounds every walk to whole strides of 40 px (8 frames × 5 px at 50 px/s);
## - collapse / reassemble exist only facing front.

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


func present(snapshot: Dictionary) -> void:
	var mode := str(snapshot.get("mode", "standing"))
	if mode == _mode:
		return
	var was := _mode
	_mode = mode
	_strip.modulate = CLEARED_TINT if mode == "cleared" else Color.WHITE
	if mode == "standing":
		_switch("reassemble", "reassemble_front")
	elif was == "standing":
		_switch("collapse", "collapse_front")


func present_motion(_velocity: Vector2, _facing: Vector2) -> void:
	pass


## Took damage: the hit strip while standing, a 1 px shudder while it lies in pieces.
func hit() -> void:
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


## Turns to look along v (only while standing still).
func face(v: Vector2) -> void:
	var dir := dir_name(v)
	if dir != facing and action == "idle" and _mode == "standing":
		facing = dir
		_play("idle_" + facing)


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
	if action == "walk":
		mover.position = mover.position.move_toward(_target, WALK_SPEED * delta)
		if mover.position == _target:
			_switch("stop", "walk_stop_" + facing)
	if _shake > 0.0:
		_shake -= delta
		_strip.position.x = 0.0 if _shake <= 0.0 else (1.0 if int(_shake * 40.0) % 2 == 0 else -1.0)


## What follows each one-shot strip.
func _on_finished() -> void:
	match action:
		"start":
			_switch("walk", "walk_" + facing)
		"stop", "hit":
			_switch("idle", "idle_" + facing)
		"collapse":
			_switch("remains", "remains_idle")
		"reassemble":
			facing = "front"
			_switch("idle", "idle_front")


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
