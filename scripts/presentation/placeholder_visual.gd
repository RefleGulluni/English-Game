@tool
extends Node2D

# Explicitly disposable geometric placeholders, isolated from all gameplay state.
@export_enum("player", "skeleton", "loot", "highlight", "environment") var kind := "skeleton"
var mode := "standing"

func present(snapshot: Dictionary) -> void:
	mode = str(snapshot.get("mode", "standing"))
	queue_redraw()

func _draw() -> void:
	match kind:
		"player":
			draw_circle(Vector2(0, 14), 19, Color("18252b"))
			draw_polygon(PackedVector2Array([Vector2(-15, 15), Vector2(0, -20), Vector2(15, 15)]), PackedColorArray([Color("74aeb5")]))
			draw_circle(Vector2(0, -16), 8, Color("e6d8b5"))
		"skeleton":
			if mode == "cleared":
				draw_circle(Vector2.ZERO, 20, Color("424a42"))
				return
			if mode == "remains":
				for i in range(6): draw_line(Vector2(-22 + i * 7, -8 + i % 2 * 10), Vector2(-13 + i * 7, 10 - i % 2 * 9), Color("c9c2a7"), 4)
				draw_circle(Vector2(-10, -5), 8, Color("d6ceae"))
				return
			draw_circle(Vector2(0, -30), 12, Color("d6ceae"))
			for x in [-4, 4]: draw_circle(Vector2(x, -32), 3, Color("27302c"))
			draw_line(Vector2(0, -18), Vector2(0, 8), Color("c4bda2"), 4)
			for y in [-12, -5, 2]: draw_line(Vector2(-11, y), Vector2(11, y), Color("c4bda2"), 3)
			for side in [-1, 1]:
				draw_line(Vector2(0, 8), Vector2(side * 13, 27), Color("c4bda2"), 4)
				draw_line(Vector2(side * 10, -14), Vector2(side * 23, 3), Color("c4bda2"), 4)
		"loot":
			draw_line(Vector2(-12, 8), Vector2(10, -10), Color("b3a778"), 7)
			draw_line(Vector2(9, -11), Vector2(18, -17), Color("ded3a0"), 5)
		"highlight": draw_arc(Vector2.ZERO, 30, 0, TAU, 48, Color("dfc580"), 2)
		"environment":
			draw_rect(Rect2(0, 0, 1900, 1100), Color("152321"))
			draw_rect(Rect2(130, 450, 1640, 100), Color("344139"))
			for x in range(610, 1650, 170):
				for y in [340, 650]:
					draw_rect(Rect2(x, y, 42, 60), Color("4c5750"))
					draw_line(Vector2(x + 10, y + 17), Vector2(x + 30, y + 17), Color("899183"), 2)
			draw_line(Vector2(480, 100), Vector2(480, 440), Color("657168"), 8)
			draw_line(Vector2(480, 560), Vector2(480, 1000), Color("657168"), 8)
