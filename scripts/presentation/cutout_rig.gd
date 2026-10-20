extends Node2D
## Presentation-only state bridge. Animation callbacks never settle combat or rewards.
@export_enum("player", "skeleton") var actor_kind := "player"
var mode := "standing"
var moving := false
var facing := Vector2.RIGHT
var back_view := false
var one_shot := ""
var last_snapshot: Dictionary = {}
var nodes: Dictionary = {} # Public visual lookup retained for inspection, not gameplay.
var rest: Dictionary = {}
var fallen: Dictionary = {}
var rope: Line2D
var clasp: Node2D
var view_sprites: Array[Sprite2D] = []
@onready var animator: AnimationPlayer = $AnimationPlayer
@onready var facing_root: Node2D = $FacingRoot

func _ready() -> void:
	rest = get_meta("reference_standing", {})
	fallen = get_meta("reference_remains", {})
	rope = find_child("TensionLinks", true, false) as Line2D
	clasp = find_child("LexiconClasp", true, false) as Node2D
	for item in find_children("*", "Sprite2D", true, false):
		if item.has_meta("part_id"):
			nodes[str(item.get_meta("part_id"))] = item
		if item.has_meta("view"): view_sprites.append(item)
	animator.animation_finished.connect(_finished)
	_play("idle")
	_bind_events.call_deferred()

func _bind_events() -> void:
	var bus := get_tree().get_first_node_in_group("gameplay_events")
	if bus != null and not bus.occurred.is_connected(_event): bus.occurred.connect(_event)

func present_motion(velocity: Vector2, direction: Vector2) -> void:
	var was_facing := facing
	if direction.length_squared() > 0.01: facing = direction.normalized()
	moving = velocity.length_squared() > 4.0
	if actor_kind == "player":
		facing_root.scale.x = -1.0 if facing.x < -0.1 else 1.0
		_set_back(facing.y < -0.25)
		var turned := was_facing.dot(facing) < 0.35
		if turned and one_shot.is_empty(): _play_once("turn")
	else:
		facing_root.scale.x = -1.0 if facing.x > 0.1 else 1.0
	if one_shot.is_empty(): _play("walk" if moving and mode == "standing" else ("idle" if mode == "standing" else ("cleared" if mode == "cleared" else "remains")))

func _set_back(value: bool) -> void:
	if back_view == value: return
	back_view = value
	if is_instance_valid(clasp): clasp.visible = not back_view
	for item in view_sprites:
		item.visible = (str(item.get_meta("view")) == "back") == back_view

func present(snapshot: Dictionary) -> void:
	last_snapshot = snapshot.duplicate(true)
	var next := str(snapshot.get("mode", "standing"))
	if next == mode: return
	var before := mode
	mode = next
	modulate = Color(0.68, 0.66, 0.60, 0.80) if mode == "cleared" else Color.WHITE
	if mode == "remains": _play_once("collapse")
	elif mode == "standing" and before in ["remains", "cleared"]: _play_once("reassembly")
	else:
		one_shot = ""
		_play("cleared" if mode == "cleared" else "idle")

func _event(id: StringName, payload: Dictionary) -> void:
	if actor_kind == "skeleton":
		if str(payload.get("enemy_id", "")) != "enemy.grave_skeleton" or mode != "standing": return
		if id == &"enemy_attack_started": _play_once("attack")
		elif id == &"enemy_damaged" and one_shot != "reassembly": _play_once("hit")
	elif id == &"word_sigil_invoked":
		var clasp := find_child("LexiconClasp", true, false)
		if clasp != null and clasp.has_method("respond"): clasp.respond()

func play_attack() -> void: # Also available to isolated visual review scenes.
	if mode == "standing": _play_once("attack")

func _play(clip: String) -> void:
	if animator.has_animation(clip) and animator.current_animation != clip: animator.play(clip, 0.04)

func _play_once(clip: String) -> void:
	if not animator.has_animation(clip): return
	one_shot = clip
	animator.play(clip, 0.025)
	animator.seek(0, true)

func _finished(clip: StringName) -> void:
	if String(clip) != one_shot: return
	one_shot = ""
	_play(("cleared" if mode == "cleared" else "remains") if mode != "standing" else ("walk" if moving else "idle"))

func _process(_delta: float) -> void:
	if actor_kind != "skeleton": return
	if rope == null: return
	rope.visible = mode != "cleared"
	var points := PackedVector2Array()
	for key in ["upper_arm_l", "ribcage", "pelvis", "thigh_r"]:
		if nodes.has(key): points.append(rope.to_local(nodes[key].global_position))
	rope.points = points
