extends Node2D
## Replaced in the game by skeleton_b.gd (the real design B, 2026-10-28); kept for reference.
## Grey-box Grave Skeleton for the v3 world until the character design group delivers the real
## sprites (docs/SKELETON_DESIGN_REQUEST.md). Drawn in code on the native pixel grid: a 96 px
## tall standing figure and a low Bone Remains pile, both plain greys (cyan is reserved for the
## language layer). Presentation only: it reads the semantic snapshot from skeleton_logic.gd.

const BONE := Color8(150, 146, 136)
const BONE_DARK := Color8(96, 92, 86)
const CORD := Color8(38, 32, 30)
const HOLLOW := Color8(20, 18, 20)
const SHADOW_COLOR := Color(0.03, 0.03, 0.05, 0.45)

var _standing: Texture2D
var _remains: Texture2D
var _sprite: Sprite2D
var _mode := "standing"
var _flash := 0.0
var _shake := 0.0


func _ready() -> void:
	_standing = ImageTexture.create_from_image(_draw_standing())
	_remains = ImageTexture.create_from_image(_draw_remains())
	add_child(PixelArt.ellipse_sprite(34, 12, SHADOW_COLOR, Vector2(0, -3)))
	_sprite = Sprite2D.new()
	add_child(_sprite)
	_show("standing")


func present(snapshot: Dictionary) -> void:
	var mode := str(snapshot.get("mode", "standing"))
	if mode != _mode:
		_show(mode)


func present_motion(_velocity: Vector2, _facing: Vector2) -> void:
	pass


## A short white flash and 1 px shake when it takes damage.
func hit() -> void:
	_flash = 0.12
	_shake = 0.18


## The enemy's attack: lean a few pixels toward the target and back.
func lunge(toward: Vector2) -> void:
	var dir := (toward - global_position).normalized()
	var tween := create_tween()
	tween.tween_property(_sprite, "position", _base_offset() + (dir * 8.0).round(), 0.12)
	tween.tween_property(_sprite, "position", _base_offset(), 0.2)


func _process(delta: float) -> void:
	_flash = maxf(0.0, _flash - delta)
	_shake = maxf(0.0, _shake - delta)
	_sprite.modulate = Color(2.2, 2.2, 2.2) if _flash > 0.0 else (Color(0.62, 0.62, 0.62) if _mode == "cleared" else Color.WHITE)
	if _shake > 0.0:
		_sprite.position = _base_offset() + Vector2(1 if int(_shake * 40.0) % 2 == 0 else -1, 0)
		if _shake <= delta:
			_sprite.position = _base_offset()


func _show(mode: String) -> void:
	_mode = mode
	_sprite.texture = _standing if mode == "standing" else _remains
	_sprite.position = _base_offset()


func _base_offset() -> Vector2:
	return Vector2(0, -_sprite.texture.get_height() / 2)


# --- Drawing (native pixels, feet at the bottom row) --------------------------------------

func _draw_standing() -> Image:
	var img := Image.create_empty(96, 96, false, Image.FORMAT_RGBA8)
	# Legs: two thin bones, the left one slightly bent (it does not stand like a person).
	_rect(img, 40, 62, 3, 16, BONE)
	_rect(img, 38, 78, 3, 16, BONE)
	_rect(img, 53, 62, 3, 32, BONE)
	_rect(img, 35, 93, 7, 3, BONE_DARK)
	_rect(img, 52, 93, 7, 3, BONE_DARK)
	# Pelvis, spine, ribcage.
	_rect(img, 38, 56, 20, 7, BONE)
	_rect(img, 43, 58, 10, 3, HOLLOW)
	_rect(img, 46, 26, 4, 31, BONE_DARK)
	for i in 5:
		_rect(img, 37 + (i % 2), 29 + i * 5, 22 - (i % 2) * 2, 3, BONE)
	# Shoulders out of line, arms hanging unevenly.
	_rect(img, 33, 24, 13, 4, BONE)
	_rect(img, 50, 26, 14, 4, BONE)
	_rect(img, 31, 27, 3, 22, BONE)
	_rect(img, 29, 49, 3, 17, BONE)
	_rect(img, 62, 29, 3, 20, BONE)
	_rect(img, 64, 49, 3, 15, BONE)
	_rect(img, 27, 66, 5, 5, BONE_DARK)
	_rect(img, 64, 64, 5, 5, BONE_DARK)
	# Skull, tilted a little, with hollow eyes and jaw.
	_ellipse(img, Vector2(49, 13), Vector2(9, 9), BONE)
	_rect(img, 43, 10, 4, 4, HOLLOW)
	_rect(img, 51, 10, 4, 4, HOLLOW)
	_rect(img, 45, 18, 9, 3, BONE_DARK)
	_rect(img, 46, 21, 7, 3, BONE)
	# Burial cords binding the joints: the structure that refuses to end.
	_rect(img, 32, 37, 29, 1, CORD)
	_rect(img, 37, 59, 22, 1, CORD)
	_rect(img, 30, 48, 4, 2, CORD)
	_rect(img, 62, 48, 4, 2, CORD)
	_rect(img, 39, 77, 5, 2, CORD)
	_rect(img, 47, 25, 2, 33, CORD)
	return img


func _draw_remains() -> Image:
	var img := Image.create_empty(64, 28, false, Image.FORMAT_RGBA8)
	_ellipse(img, Vector2(32, 21), Vector2(26, 6), BONE_DARK)
	_rect(img, 8, 18, 22, 3, BONE)
	_rect(img, 34, 20, 20, 3, BONE)
	_rect(img, 20, 13, 3, 10, BONE)
	_rect(img, 40, 14, 14, 3, BONE)
	for i in 3:
		_rect(img, 24 + i * 4, 15, 2, 7, BONE)
	_ellipse(img, Vector2(14, 11), Vector2(6, 6), BONE)
	_rect(img, 11, 9, 3, 3, HOLLOW)
	_rect(img, 16, 9, 2, 3, HOLLOW)
	# One shin still upright, tied by a cord: it is not finished.
	_rect(img, 47, 2, 3, 16, BONE)
	_rect(img, 46, 8, 5, 1, CORD)
	_rect(img, 22, 16, 26, 1, CORD)
	_rect(img, 47, 9, 1, 9, CORD)
	return img


func _rect(img: Image, x: int, y: int, w: int, h: int, color: Color) -> void:
	img.fill_rect(Rect2i(x, y, w, h).intersection(Rect2i(Vector2i.ZERO, img.get_size())), color)


func _ellipse(img: Image, center: Vector2, radius: Vector2, color: Color) -> void:
	for y in range(int(center.y - radius.y), int(center.y + radius.y) + 1):
		for x in range(int(center.x - radius.x), int(center.x + radius.x) + 1):
			var d := Vector2((x + 0.5 - center.x) / radius.x, (y + 0.5 - center.y) / radius.y)
			if d.length_squared() <= 1.0 and x >= 0 and y >= 0 and x < img.get_width() and y < img.get_height():
				img.set_pixel(x, y, color)
