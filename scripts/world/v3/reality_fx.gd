class_name RealityFx
extends Node2D
## The world's reaction when a word lands (docs/COMBAT_ANIMATION_REQUEST.md §7, §12): bone chips,
## a puff of bone ash, shroud threads. The character group draws the strips; this places them.
##
## Each effect stands on the ground (its node sits at a ground y, so the Y-sorted room orders it
## against the skeleton correctly) and draws its sprite lifted by `height`. Positions are whole
## pixels; chips fly a parabola, land, lie still a moment and fade.

const ANIM := "res://art/character_design/enemies/skeleton/anim/"
const CHIPS := ["fx_bone_chip_a", "fx_bone_chip_b", "fx_bone_chip_c"]
const GRAVITY := 420.0
const REST := 0.7 # seconds a landed chip lies still before fading
const FADE := 0.3

var _strip: SpriteStrip
var _velocity := Vector2.ZERO # x along the ground, y = upward speed of the lift
var _height := 0.0
var _flying := false
var _rest := 0.0


## 2-4 chips thrown from a point `height` px above `ground`, away along `dir` (+1 right, -1 left).
static func chips(parent: Node, ground: Vector2, height: float, dir: float, count: int) -> void:
	for i in count:
		var fx := _make(parent, CHIPS[randi() % CHIPS.size()], ground + Vector2(randi_range(-4, 4), randi_range(-4, 8)), height + randi_range(-6, 6))
		fx._strip.random_phase()
		fx._velocity = Vector2(dir * randf_range(30.0, 95.0), randf_range(70.0, 140.0))
		fx._flying = true


## One puff of bone ash rising from `height` px above `ground`.
static func dust(parent: Node, ground: Vector2, height := 0.0) -> void:
	_make(parent, "fx_bone_dust", ground, height)._free_when_done()


## Shroud threads torn loose `height` px above `ground`.
static func threads(parent: Node, ground: Vector2, height: float) -> void:
	_make(parent, "fx_shroud_threads", ground, height)._free_when_done()


## The nearest Y-sorted layer above `node` (the room's), where effects belong.
static func layer_for(node: Node) -> Node:
	var at := node.get_parent()
	while at is Node2D and not (at as Node2D).y_sort_enabled and at.get_parent() != null:
		at = at.get_parent()
	return at


## `ground` is a global position.
static func _make(parent: Node, anim: String, ground: Vector2, height: float) -> RealityFx:
	var fx := RealityFx.new()
	fx.position = ((parent as Node2D).to_local(ground) if parent is Node2D else ground).round()
	fx._height = height
	fx._strip = SpriteStrip.new()
	fx._strip.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	fx.add_child(fx._strip)
	fx._strip.load_strip(ANIM, anim)
	fx._strip.position = Vector2(0, -roundf(height))
	parent.add_child(fx)
	return fx


func _free_when_done() -> void:
	_strip.finished.connect(func():
		visible = false # the strip rewinds to frame 0 as it finishes
		queue_free())


func _process(delta: float) -> void:
	if _flying:
		_velocity.y -= GRAVITY * delta
		_height += _velocity.y * delta
		position.x += _velocity.x * delta
		if _height <= 0.0:
			_height = 0.0
			_flying = false
			_strip.playing = false # it lands on whatever face it was showing
		_strip.position = Vector2(roundf(position.x) - position.x, -roundf(_height))
	elif _rest >= 0.0 and _strip.current.begins_with("fx_bone_chip"):
		_rest += delta
		if _rest > REST:
			modulate.a = clampf(1.0 - (_rest - REST) / FADE, 0.0, 1.0)
			if _rest > REST + FADE:
				queue_free()
