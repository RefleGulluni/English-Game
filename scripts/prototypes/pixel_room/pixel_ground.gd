extends RefCounted
## Placeholder Cemetery ground for the pixel validation room.
##
## Generated at native pixel resolution from colours of art/pixel_test/shared_palette.gpl:
## banded mud blotches, a few wet puddles and sparse dead-grass tufts. It only stands in
## until real pixel terrain tiles exist; it is not a production asset.

const MUD := [Color8(24, 19, 17), Color8(38, 31, 24), Color8(46, 42, 34), Color8(61, 55, 46)]
const WET_EDGE := Color8(24, 19, 17)
const WET := Color8(46, 42, 34)
const WET_GLINT := Color8(79, 75, 72)
const GRASS := [Color8(89, 78, 56), Color8(104, 87, 58), Color8(130, 109, 82), Color8(148, 119, 80)]


static func generate(size: Vector2i, seed_value := 7) -> ImageTexture:
	var blotch := FastNoiseLite.new()
	blotch.seed = seed_value
	blotch.frequency = 0.016
	blotch.fractal_octaves = 3
	var detail := FastNoiseLite.new()
	detail.seed = seed_value + 1
	detail.frequency = 0.08
	var water := FastNoiseLite.new()
	water.seed = seed_value + 2
	water.frequency = 0.007
	water.fractal_octaves = 2

	var img := Image.create_empty(size.x, size.y, false, Image.FORMAT_RGBA8)
	for y in size.y:
		for x in size.x:
			# Posterised noise gives flat, blotchy colour areas instead of per-pixel noise.
			var b := blotch.get_noise_2d(x, y) * 0.5 + 0.5 + detail.get_noise_2d(x, y) * 0.1
			var c: Color = MUD[clampi(int(b * 4.0), 0, 3)]
			var w := water.get_noise_2d(x, y)
			if w > 0.56:
				c = WET_GLINT if w > 0.68 else WET
			elif w > 0.53:
				c = WET_EDGE
			img.set_pixel(x, y, c)

	var rng := RandomNumberGenerator.new()
	rng.seed = seed_value
	for i in size.x * size.y / 700:
		var p := Vector2i(rng.randi_range(3, size.x - 4), rng.randi_range(6, size.y - 1))
		if water.get_noise_2d(p.x, p.y) > 0.38:
			continue
		if blotch.get_noise_2d(p.x, p.y) < -0.1 and rng.randf() < 0.7:
			continue # tufts cluster instead of covering everything evenly
		_tuft(img, p, rng)
	return ImageTexture.create_from_image(img)


static func _tuft(img: Image, root: Vector2i, rng: RandomNumberGenerator) -> void:
	for blade in rng.randi_range(2, 4):
		var x := root.x + rng.randi_range(-2, 2)
		var lean := rng.randi_range(-1, 1)
		var c: Color = GRASS[rng.randi_range(0, GRASS.size() - 1)]
		for t in rng.randi_range(2, 5):
			img.set_pixel(x + (lean * t) / 3, root.y - t, c)
