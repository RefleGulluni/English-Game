extends Node2D

# Art may assign resources here or replace this scene. Gameplay never resolves art paths.
@export var audio_cues: Dictionary = {}
@export var vfx_cues: Dictionary = {}
@export var audio_bus: StringName = &"SFX"
var events: Node
var echoes: Array[Dictionary] = []

func bind(bus: Node) -> void:
	events = bus
	events.occurred.connect(_on_event)

func _on_event(event_id: StringName, payload: Dictionary) -> void:
	if event_id == &"echo_spawned" and not (vfx_cues.get(String(event_id)) is PackedScene):
		echoes.append({"from": to_local(payload.position), "to": to_local(payload.target), "age": 0.0})
	var stream = audio_cues.get(String(event_id))
	if stream is AudioStream:
		var voice := AudioStreamPlayer.new()
		$AudioRoot.add_child(voice)
		voice.stream = stream
		voice.bus = audio_bus if AudioServer.get_bus_index(audio_bus) >= 0 else &"Master"
		voice.finished.connect(voice.queue_free)
		voice.play()
	var effect = vfx_cues.get(String(event_id))
	if effect is PackedScene:
		var instance: Node = effect.instantiate()
		$VFXRoot.add_child(instance)
		if instance is Node2D: instance.global_position = payload.get("position", global_position)
		if instance.has_method("play_event"): instance.play_event(event_id, payload)

func _process(delta: float) -> void:
	for echo in echoes: echo.age = float(echo.age) + delta
	echoes = echoes.filter(func(e): return float(e.age) < 0.5)
	queue_redraw()

func _draw() -> void:
	for echo in echoes:
		var fraction := clampf(float(echo.age) / 0.5, 0, 1)
		for i in range(4):
			var offset := Vector2(0, (i - 1.5) * 8 * (1 - fraction))
			draw_circle(echo.from.lerp(echo.to, fraction) + offset, 3.5 * (1 - fraction * 0.6), Color("80d5c4"))
