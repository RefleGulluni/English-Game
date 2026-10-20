@tool
extends Node2D
var body: Sprite2D
var clasp: Node2D
var response := 0.0

func _ready() -> void:
	body = Sprite2D.new()
	body.texture = preload("res://art/characters/textures/wordbearer_base.png")
	body.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	body.scale = Vector2.ONE * (118.0/body.texture.get_height())
	body.position = Vector2(0,-58)
	add_child(body)
	clasp = preload("res://art/characters/lexicon_clasp.tscn").instantiate()
	clasp.position = Vector2(-5,-92)
	clasp.scale = Vector2.ONE * 0.1
	add_child(clasp)
	if not Engine.is_editor_hint(): _bind_events.call_deferred()

func _bind_events() -> void:
	var bus := get_tree().get_first_node_in_group("gameplay_events")
	if bus != null and not bus.occurred.is_connected(_event): bus.occurred.connect(_event)

func _event(id: StringName, _payload: Dictionary) -> void:
	if id == &"word_sigil_invoked": clasp.respond()

func _draw() -> void:
	draw_set_transform(Vector2(0,2),0,Vector2(1,0.35))
	draw_circle(Vector2.ZERO,22,Color(0.02,0.025,0.025,0.28))
