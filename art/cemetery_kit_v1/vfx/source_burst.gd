extends Node2D
## Optional independent dust/bone source consumer. Pure presentation; no gameplay callbacks.
@export_enum("bone","dust") var kind := "bone"
var age := 0.0
var started := false
var parts: Array[Sprite2D] = []
var vectors: Array[Vector2] = []
func play_event(_id: StringName, payload: Dictionary) -> void:
	if started: return
	started = true
	if payload.has("position"): global_position = Vector2(payload["position"])
	var texture: Texture2D = preload("res://art/cemetery_kit_v1/vfx/bone_splinters.png") if kind=="bone" else preload("res://art/cemetery_kit_v1/vfx/dust.png")
	for i in range(4 if kind=="bone" else 2):
		var sprite := Sprite2D.new()
		sprite.texture = texture
		sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
		var extent := 5.0 if kind=="bone" else 25.0
		sprite.scale = Vector2.ONE*extent/texture.get_height()
		sprite.modulate = Color(0.7,0.7,0.65,0.6 if kind=="bone" else 0.16)
		add_child(sprite)
		parts.append(sprite)
		vectors.append(Vector2(-19+i*12,-20-i*4))
func _process(delta: float) -> void:
	if not started: return
	age += delta
	var t := minf(age/0.72,1)
	for i in parts.size():
		parts[i].position = vectors[i]*t + Vector2(0,20*t*t)
		parts[i].rotation = t*(i-1.5)*0.8
		parts[i].modulate.a = (0.55 if kind=="bone" else 0.16)*(1-t)
	if age>0.8: queue_free()
