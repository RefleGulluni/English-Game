@tool
extends Node2D
## Proximity attention does not add a ring or change reward state.
func _draw() -> void:
	draw_line(Vector2(-3,2),Vector2(-1,0),Color(0.75,0.73,0.66,0.28),0.7,true)
