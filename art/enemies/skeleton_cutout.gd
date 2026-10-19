@tool
extends Node2D
## Presentation only. All poses are local to the unchanged actor contact origin.
const ROOT := "res://art/enemies/skeleton_parts/"
var mode := "standing"
var elapsed := 0.0
var moving := false
var nodes: Dictionary = {}
var rest: Dictionary = {}
var fallen: Dictionary = {}
var pose_tween: Tween
var attack_tween: Tween
var rope: Line2D
var pulse := 0.0
var last_snapshot: Dictionary = {}

func _ready() -> void:
	_build()
	if not Engine.is_editor_hint(): _bind_events.call_deferred()

func _bind_events() -> void:
	var bus := get_tree().get_first_node_in_group("gameplay_events")
	if bus != null and not bus.occurred.is_connected(_on_event): bus.occurred.connect(_on_event)

func _build() -> void:
	if not nodes.is_empty(): return
	var definitions := [
		["foot_l", Vector2(-15,-3), Vector2(18,12), -0.1],
		["foot_r", Vector2(15,-3), Vector2(18,12), 0.1],
		["shin_l", Vector2(-13,-20), Vector2(11,28), 0.08],
		["shin_r", Vector2(13,-20), Vector2(11,28), -0.08],
		["thigh_l", Vector2(-9,-43), Vector2(12,28), 0.16],
		["thigh_r", Vector2(9,-43), Vector2(12,28), -0.16],
		["pelvis", Vector2(0,-57), Vector2(29,22), 0.04],
		["ribcage", Vector2(0,-83), Vector2(35,40), -0.04],
		["upper_arm_l", Vector2(-21,-85), Vector2(10,27), 0.22],
		["upper_arm_r", Vector2(21,-85), Vector2(10,27), -0.25],
		["forearm_l", Vector2(-27,-63), Vector2(10,25), 0.17],
		["forearm_r", Vector2(28,-63), Vector2(10,25), -0.32],
		["hand_l", Vector2(-31,-45), Vector2(12,17), 0.13],
		["hand_r", Vector2(34,-45), Vector2(12,17), -0.3],
		["weapon", Vector2(-43,-39), Vector2(18,65), -0.48],
		["hip_cloth", Vector2(0,-51), Vector2(33,32), 0.0],
		["shoulder_cloth", Vector2(-16,-78), Vector2(18,32), 0.1],
		["skull", Vector2(2,-112), Vector2(22,27), 0.15],
		["burial_cord", Vector2(0,-78), Vector2(23,24), 0.0],
		["nails", Vector2(12,-58), Vector2(6,7), 0.2],
	]
	for i in range(definitions.size()):
		var d: Array = definitions[i]
		var sprite := Sprite2D.new()
		sprite.name = d[0]
		sprite.texture = load(ROOT + str(d[0]) + ".png")
		sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
		sprite.position = d[1]
		sprite.rotation = d[3]
		sprite.scale = d[2] / sprite.texture.get_size()
		add_child(sprite)
		nodes[d[0]] = sprite
		rest[d[0]] = {"position": sprite.position, "rotation": sprite.rotation, "scale": sprite.scale}
		var p := Vector2(-39 + (i * 29) % 81, -5 - (i * 13) % 29)
		if d[0] == "ribcage": p = Vector2(0,-17)
		if d[0] == "skull": p = Vector2(32,-5)
		if d[0] == "weapon": p = Vector2(-24,9)
		fallen[d[0]] = {"position": p, "rotation": -0.8 + float(i % 6) * 0.48, "scale": sprite.scale * Vector2(1,0.72)}
	rope = Line2D.new()
	rope.name = "TensionLinks"
	rope.width = 0.65
	rope.default_color = Color(0.28,0.24,0.18,0.7)
	rope.antialiased = true
	add_child(rope)
	queue_redraw()

func present(snapshot: Dictionary) -> void:
	if nodes.is_empty(): _build()
	last_snapshot = snapshot.duplicate(true)
	var next := str(snapshot.get("mode", "standing"))
	if next == mode: return
	var previous := mode
	mode = next
	var destination: Dictionary = rest if mode == "standing" else fallen
	if is_instance_valid(pose_tween): pose_tween.kill()
	if is_instance_valid(attack_tween): attack_tween.kill()
	moving = true
	pose_tween = create_tween().set_parallel(true)
	var duration := 0.8 if mode == "standing" else 0.58
	for key in nodes:
		var sprite: Sprite2D = nodes[key]
		var target: Dictionary = destination[key]
		pose_tween.tween_property(sprite, "position", target.position, duration).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
		pose_tween.tween_property(sprite, "rotation", target.rotation, duration)
		pose_tween.tween_property(sprite, "scale", target.scale, duration)
		var tint := Color(0.62,0.6,0.55,0.85) if mode == "cleared" else Color.WHITE
		pose_tween.tween_property(sprite, "modulate", tint, 0.3)
	pose_tween.chain().tween_callback(func(): moving = false)
	if previous == "remains" and mode == "standing": elapsed = 0.0

func _on_event(id: StringName, payload: Dictionary) -> void:
	if id == &"enemy_damaged" and str(payload.get("enemy_id","")) == "enemy.grave_skeleton":
		pulse = 0.23
	if id == &"combat_phase_changed" and str(payload.get("phase","")) == "ENEMY_TURN" and mode == "standing":
		play_attack()

func play_attack() -> void:
	if moving or mode != "standing": return
	var arm: Sprite2D = nodes["forearm_l"]
	var weapon: Sprite2D = nodes["weapon"]
	if is_instance_valid(attack_tween): attack_tween.kill()
	attack_tween = create_tween().set_parallel(true)
	attack_tween.tween_property(arm, "rotation", float(rest.forearm_l.rotation) - 0.38, 0.12)
	attack_tween.tween_property(weapon, "rotation", float(rest.weapon.rotation) - 0.5, 0.12)
	attack_tween.chain().tween_interval(0.05)
	attack_tween.chain().tween_property(arm, "rotation", rest.forearm_l.rotation, 0.23)
	attack_tween.parallel().tween_property(weapon, "rotation", rest.weapon.rotation, 0.23)

func _process(delta: float) -> void:
	if nodes.is_empty(): return
	elapsed += delta
	pulse = maxf(0.0, pulse-delta)
	if not moving:
		var head: Sprite2D = nodes["skull"]
		if mode == "standing":
			head.position = rest.skull.position + Vector2(0,sin(elapsed*1.6)*0.4)
		elif mode == "remains":
			# A short local tug with long pauses, never a glowing or floating pile.
			var tug := pow(maxf(0.0,sin(elapsed*1.7)),16.0)
			head.position = fallen.skull.position + Vector2(-0.65*tug,-0.25*tug)
	var rib: Sprite2D = nodes["ribcage"]
	var arm: Sprite2D = nodes["upper_arm_l"]
	var hip: Sprite2D = nodes["pelvis"]
	rope.points = PackedVector2Array([arm.position, rib.position+Vector2(6,5), hip.position, nodes["thigh_r"].position])
	rope.visible = mode != "cleared"
	if pulse > 0.0: rib.modulate = Color(1.0,0.82+pulse*0.4,0.7+pulse,1)
	elif mode != "cleared": rib.modulate = Color.WHITE
	queue_redraw()

func _draw() -> void:
	draw_set_transform(Vector2(0,1),0,Vector2(1,0.3))
	draw_circle(Vector2.ZERO, 26 if mode == "standing" else 42, Color(0.025,0.03,0.03,0.28))
