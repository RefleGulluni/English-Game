@tool
extends Node2D
@export var responding := false
var strength := 0.0
var plate: Sprite2D

func _ready() -> void:
	plate = Sprite2D.new()
	plate.texture = preload("res://art/characters/textures/lexicon_clasp_quiet.png")
	plate.scale = Vector2.ONE * (56.0/plate.texture.get_width())
	add_child(plate)
	strength = 0.0

func respond() -> void:
	var tween := create_tween()
	tween.tween_property(self,"strength",0.7,0.12)
	tween.tween_interval(0.1)
	tween.tween_property(self,"strength",0.0,0.5)

func _process(_delta: float) -> void: queue_redraw()

func _draw() -> void:
	var alpha := 0.65 if responding else strength
	if alpha <= 0.001: return
	# Separate editable geometric response over the matte raster, no baked glow.
	draw_polyline(PackedVector2Array([Vector2(-9,-13),Vector2(-11,-2),Vector2(-5,5),Vector2(-4,13)]),Color(0.85,0.81,0.69,alpha),0.8,true)
