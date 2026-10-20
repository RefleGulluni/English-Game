@tool
extends Node2D
var age := 0.0
var body: Sprite2D
func _ready() -> void:
	body = Sprite2D.new()
	body.texture = preload("res://art/loot/textures/weathered_chisel.png")
	body.scale = Vector2.ONE * (11.0/body.texture.get_width())
	body.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	add_child(body)
func _process(delta: float) -> void:
	age += delta
	queue_redraw()
func _draw() -> void:
	# A single spawn response, never a perpetually flashing reward.
	if age > 1.65 or Engine.is_editor_hint(): return
	var a := sin(clampf(age/1.65,0,1)*PI)*0.5
	draw_line(Vector2(-3,2),Vector2(-1,0),Color(0.9,0.87,0.76,a),1.0,true)
