class_name CemeteryProp
extends Node2D
## One placeable world prop (a "building block", D-034): the upright part, its ground base and
## its collision live in one scene under scenes/props/, so a prop behaves the same wherever it is
## dropped — in a room built from layout data or dragged into a room by hand.
##
## The scene origin is the ground contact point (where the upright part meets the ground); it is
## also the Y-sort point. Scenes are made by scripts/tools/bake_cemetery_props.gd; collision is
## meant to be adjusted by hand in the editor afterwards.

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


func _process(delta: float) -> void:
	if flat:
		return
	if not is_instance_valid(player):
		player = get_tree().get_first_node_in_group("world_player")
		if player == null:
			return
	var a := move_toward(sprite.modulate.a, FADE_ALPHA if _hides_player() else 1.0, delta * 4.0)
	sprite.modulate.a = a
	if base:
		base.modulate.a = a


## Behind the prop, and an actual stone pixel (not the transparent canvas) covers the body.
func _hides_player() -> bool:
	var feet := player.global_position - global_position
	if feet.y >= 0:
		return false
	var size := _mask.get_size()
	for s in BODY_SAMPLES:
		var p := Vector2i((feet + s - sprite.offset).floor())
		if p.x >= 0 and p.y >= 0 and p.x < size.x and p.y < size.y and _mask.get_bitv(p):
			return true
	return false


## Drops the upright pixels that the base draws identically (same origin), so the overlap is not
## doubled when both fade. Cached per texture: every copy of a prop shares one result.
static func _without_base(upright: Texture2D, ground: Texture2D) -> Texture2D:
	var key := upright.resource_path
	if key.is_empty():
		return PixelArt.without_overlap(upright, ground)
	if not _trimmed.has(key):
		_trimmed[key] = PixelArt.without_overlap(upright, ground)
	return _trimmed[key]
