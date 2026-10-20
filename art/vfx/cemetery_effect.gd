extends Node2D
## Short-lived, event-fed visual. No gameplay state or reward mutation.
@export_enum("echo","loot","word","tension") var effect_kind := "echo"
var age := 0.0
var lifetime := 0.8
var target := Vector2.ZERO
var word := ""
var started := false

func play_event(_id: StringName, payload: Dictionary) -> void:
	started = true
	if effect_kind == "echo":
		lifetime = 0.72
		target = to_local(Vector2(payload.get("target",global_position)))
	elif effect_kind == "loot":
		lifetime = 1.65
	elif effect_kind == "word":
		lifetime = 0.62
		# Read-only world position survives presentation layer reparenting.
		if payload.has("position"):
			global_position = Vector2(payload["position"])
		else:
			var actor := get_tree().get_first_node_in_group("world_player") as Node2D
			if actor == null:
				var ancestor := get_parent()
				while ancestor != null and actor == null:
					actor = ancestor.get_node_or_null("Player") as Node2D
					ancestor = ancestor.get_parent()
			if actor != null: global_position = actor.global_position
		word = str(payload.get("word_id","")).to_upper()
		var names := {"OBSERVE":"observe_invoke","SHATTER":"shatter_invoke","ERODE":"erode_invoke"}
		if names.has(word): _sound("res://audio/words/"+str(names[word])+".wav")
	else: lifetime = 0.7

func _sound(path: String) -> void:
	var player := AudioStreamPlayer.new()
	player.stream = load(path)
	player.bus = &"SFX" if AudioServer.get_bus_index("SFX") >= 0 else &"Master"
	player.volume_db = -5.0
	add_child(player)
	player.play()

func _process(delta: float) -> void:
	if not started: return
	age += delta
	if effect_kind == "echo" and age-delta < lifetime*0.78 and age >= lifetime*0.78:
		_sound("res://audio/loot/echo_absorb.wav")
	if age >= lifetime+0.5: queue_free(); return
	queue_redraw()

func _draw() -> void:
	if not started: return
	var t := clampf(age/lifetime,0,1)
	if effect_kind == "echo":
		for i in range(3):
			var u := clampf(t-float(i)*0.07,0,1)
			var p := Vector2.ZERO.lerp(target,u) + Vector2(0,-sin(u*PI)*(22+i*5))
			var fade := sin(u*PI)*0.62
			var points := PackedVector2Array([p+Vector2(-2,0),p+Vector2(0,-3),p+Vector2(2,0),p+Vector2(0,2)])
			draw_colored_polygon(points,Color(0.76,0.8,0.75,fade))
			var previous := Vector2.ZERO.lerp(target,maxf(0,u-0.04))+Vector2(0,-sin(maxf(0,u-0.04)*PI)*(22+i*5))
			draw_line(previous,p,Color(0.7,0.76,0.72,fade*0.22),0.6,true)
	elif effect_kind == "loot":
		var alpha := sin(t*PI)*0.46
		draw_line(Vector2(-3,2),Vector2(-1,0),Color(0.86,0.83,0.72,alpha),1.05,true)
	elif effect_kind == "tension":
		draw_polyline(PackedVector2Array([Vector2(-15,-3),Vector2(0,-7-sin(t*PI)*1.5),Vector2(13,-2)]),Color(0.65,0.62,0.52,sin(t*PI)*0.14),0.55,true)
	elif effect_kind == "word":
		var radius := 16+t*18
		draw_arc(Vector2(0,-32),radius,0.3,1.3,18,Color(0.82,0.8,0.7,sin(t*PI)*0.22),0.65,true)
