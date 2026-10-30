class_name CemeteryProp
extends Node2D
## One placeable world prop (a "building block", D-034): the upright part, its ground base and
## its collision live in one scene under scenes/props/, so a prop behaves the same wherever it is
## dropped — in a room built from layout data or dragged into a room by hand.
##
## The scene origin is the ground contact point (where the upright part meets the ground); it is
## also the Y-sort point. Scenes are made by scripts/tools/bake_cemetery_props.gd; collision is
## meant to be adjusted by hand in the editor afterwards.
##
## Wide props (the fountain): one sort point at the foot is wrong beside them, where the hero
## stands level with the rim yet "above" the foot. With a collision polygon, the prop is sorted by
## the front edge of that footprint at the hero's x instead (beyond its ends, the end point), and
## the same line decides whether the hero is behind it.

const FADE_ALPHA := 0.45
const BASE_Z := -5 # with the room's dead grass; the ground plate sits below at -10
## Points on the hero's body (relative to its feet) that count for "the prop hides the hero".
const BODY_SAMPLES := [Vector2(0, -16), Vector2(0, -40), Vector2(0, -64), Vector2(0, -86),
		Vector2(-12, -30), Vector2(12, -30), Vector2(-12, -60), Vector2(12, -60)]

## Lies on the ground (a slab): drawn with the bases, so it never covers anyone.
@export var flat := false
## Transparent rows under the foot in the PNG; layouts give the PNG's bottom-centre origin.
@export var ground_gap := 0

var player: Node2D

@onready var sprite: Sprite2D = $Sprite
@onready var base: Sprite2D = get_node_or_null("Base")

static var _masks := {}
static var _trimmed := {}
var _mask: BitMap
var _footprint := PackedVector2Array() # the collision polygon, in this prop's space


func _ready() -> void:
	var key := sprite.texture.resource_path
	if base:
		base.z_index = BASE_Z
		sprite.texture = _without_base(sprite.texture, base.texture)
	if flat:
		sprite.z_index = BASE_Z
	_mask = _masks.get(key)
	if _mask == null:
		_mask = BitMap.new()
		_mask.create_from_image_alpha(sprite.texture.get_image())
		_masks[key] = _mask
	var shape := get_node_or_null("Body/CollisionPolygon2D") as CollisionPolygon2D
	if shape and not flat and shape.polygon.size() >= 3:
		var to_prop: Transform2D = (shape.get_parent() as Node2D).transform * shape.transform
		_footprint = to_prop * shape.polygon
		y_sort_enabled = true # the sprite then sorts by its own position, moved below


func _process(delta: float) -> void:
	if flat:
		return
	if not is_instance_valid(player):
		player = get_tree().get_first_node_in_group("world_player")
		if player == null:
			return
	if not _footprint.is_empty():
		var front := roundf(_front_y((player.global_position - global_position).x))
		sprite.offset.y += sprite.position.y - front # the picture stays put, its sort point moves
		sprite.position.y = front
	var a := move_toward(sprite.modulate.a, FADE_ALPHA if _hides_player() else 1.0, delta * 4.0)
	sprite.modulate.a = a
	if base:
		base.modulate.a = a


## Behind the prop, and an actual stone pixel (not the transparent canvas) covers the body.
func _hides_player() -> bool:
	var feet := player.global_position - global_position
	if feet.y >= sprite.position.y:
		return false
	var size := _mask.get_size()
	for s in BODY_SAMPLES:
		var p := Vector2i((feet + s - sprite.position - sprite.offset).floor())
		if p.x >= 0 and p.y >= 0 and p.x < size.x and p.y < size.y and _mask.get_bitv(p):
			return true
	return false


## The footprint's front (lowest on screen) edge at x; beyond its ends, the end point's.
func _front_y(x: float) -> float:
	var low := INF
	var high := -INF
	for point in _footprint:
		low = minf(low, point.x)
		high = maxf(high, point.x)
	x = clampf(x, low, high)
	var front := -INF
	for i in _footprint.size():
		var a := _footprint[i]
		var b := _footprint[(i + 1) % _footprint.size()]
		if x < minf(a.x, b.x) or x > maxf(a.x, b.x):
			continue
		front = maxf(front, maxf(a.y, b.y) if is_equal_approx(a.x, b.x) else lerpf(a.y, b.y, (x - a.x) / (b.x - a.x)))
	return front if front > -INF else 0.0


## Drops the upright pixels that the base draws identically (same origin), so the overlap is not
## doubled when both fade. Cached per texture: every copy of a prop shares one result.
static func _without_base(upright: Texture2D, ground: Texture2D) -> Texture2D:
	var key := upright.resource_path
	if key.is_empty():
		return PixelArt.without_overlap(upright, ground)
	if not _trimmed.has(key):
		_trimmed[key] = PixelArt.without_overlap(upright, ground)
	return _trimmed[key]
