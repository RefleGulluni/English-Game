@tool
extends Node2D
func _process(delta: float) -> void:
	if Engine.is_editor_hint(): return
	var world := get_parent().get_parent()
	var actor := world.get_node_or_null("Player") as Node2D
	if actor == null: return
	for sprite in $Foreground.get_children():
		if not sprite is Sprite2D: continue
		var p: Vector2 = sprite.global_position
		var player_p: Vector2 = actor.global_position
		var covers := absf(player_p.x-p.x)<70 and player_p.y<p.y and player_p.y>p.y-110
		sprite.modulate.a = lerpf(sprite.modulate.a,0.3 if covers else 1.0,minf(1,delta*8))
