class_name PixelArt
extends RefCounted
## Small helpers for the v3 pixel world: loading PNGs straight from disk (no editor import
## needed), contact shadows, and the radial lantern light. All sizes are native pixels.


static func image(res_path: String) -> Image:
	var img := Image.load_from_file(ProjectSettings.globalize_path(res_path))
	img.convert(Image.FORMAT_RGBA8)
	return img


static func texture(res_path: String) -> Texture2D:
	return ImageTexture.create_from_image(image(res_path))


## A flat filled ellipse, used as a contact shadow under feet and placeholder actors.
static func ellipse_sprite(width: int, height: int, color: Color, offset := Vector2.ZERO) -> Sprite2D:
	var img := Image.create_empty(width, height, false, Image.FORMAT_RGBA8)
	for y in height:
		for x in width:
			var d := Vector2((x + 0.5) / width * 2.0 - 1.0, (y + 0.5) / height * 2.0 - 1.0)
			if d.length_squared() <= 1.0:
				img.set_pixel(x, y, color)
	var s := Sprite2D.new()
	s.texture = ImageTexture.create_from_image(img)
	s.position = offset.round()
	return s


static func radial_light(size: int) -> Texture2D:
	var gradient := Gradient.new()
	gradient.set_color(0, Color(1, 1, 1, 1))
	gradient.set_color(1, Color(1, 1, 1, 0))
	var tex := GradientTexture2D.new()
	tex.gradient = gradient
	tex.fill = GradientTexture2D.FILL_RADIAL
	tex.fill_from = Vector2(0.5, 0.5)
	tex.fill_to = Vector2(1.0, 0.5)
	tex.width = size
	tex.height = size
	return tex


static func lowest_opaque_row(img: Image) -> int:
	for y in range(img.get_height() - 1, -1, -1):
		for x in img.get_width():
			if img.get_pixel(x, y).a > 0.5:
				return y
	return img.get_height() - 1


## Contact shadow shaped like the prop's own base: the bottom rows of its silhouette squashed
## flat and nudged down-right (light from the upper left).
static func footprint_shadow(tex: Texture2D, color: Color) -> Sprite2D:
	var src := tex.get_image()
	var w := src.get_width()
	var h := lowest_opaque_row(src) + 1
	var band := mini(24, h)
	var out_h := band / 2 + 3
	var img := Image.create_empty(w + 4, out_h, false, Image.FORMAT_RGBA8)
	for r in band:
		for x in w:
			if src.get_pixel(x, h - band + r).a > 0.5:
				for k in 3: # thicken downwards so thin roots still leave a shadow
					img.set_pixel(x + 2, mini(r / 2 + k, out_h - 1), color)
	var s := Sprite2D.new()
	s.texture = ImageTexture.create_from_image(img)
	s.centered = false
	s.position = Vector2(-w / 2, -band / 2 + 1)
	return s


## Drops the upright part's pixels that its ground base already draws identically (both share
## the same bottom-centre origin), so the overlap is not doubled when both fade.
static func without_overlap(upright: Texture2D, base: Texture2D) -> Texture2D:
	var img := upright.get_image()
	var b := base.get_image()
	var dx := (b.get_width() - img.get_width()) / 2
	var dy := b.get_height() - img.get_height()
	for y in img.get_height():
		for x in img.get_width():
			var bx := x + dx
			var by := y + dy
			if bx < 0 or by < 0 or bx >= b.get_width() or by >= b.get_height():
				continue
			var p := img.get_pixel(x, y)
			var q := b.get_pixel(bx, by)
			if p.a > 0.5 and q.a > 0.5 and absf(p.r - q.r) + absf(p.g - q.g) + absf(p.b - q.b) < 0.06:
				img.set_pixel(x, y, Color(0, 0, 0, 0))
	return ImageTexture.create_from_image(img)
