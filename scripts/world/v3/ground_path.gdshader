shader_type canvas_item;
// Path terrain tiles carry only the shape: pure white means "inside the path", every other colour
// (wet rim, stray pebbles) is drawn as it is. White is replaced by the path texture sampled at the
// pixel's world position, so the path surface is one big seamless texture, not a 32 px repeat.
//
// macro_strength (D-076): a slow rise and fall of light across the ground, much larger than the
// 224x128 texture, so its repeat is harder to pick out. Worked out per whole world pixel, so it
// stays on the pixel grid; 0 turns it off (the terrains approved before it keep 0 until the user
// has compared).

uniform sampler2D path_texture : filter_nearest, repeat_enable;
uniform float macro_strength = 0.0; // how far brightness swings either way, e.g. 0.08 = +-8 %
uniform float macro_size = 260.0; // world pixels across one light or dark patch

varying vec2 world_pos;

void vertex() {
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 0.0, 1.0)).xy;
}

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

// Smooth value noise, 0..1.
float noise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x), mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x), f.y);
}

void fragment() {
	vec4 c = texture(TEXTURE, UV);
	if (c.a > 0.5 && min(c.r, min(c.g, c.b)) > 0.99) {
		vec2 pixel = floor(world_pos);
		vec2 size = vec2(textureSize(path_texture, 0));
		vec3 surface = texture(path_texture, (pixel + 0.5) / size).rgb;
		if (macro_strength > 0.0) {
			// two octaves, the second skewed so the patches don't line up with the texture's grid
			float n = 0.65 * noise(pixel / macro_size) + 0.35 * noise(mat2(vec2(0.8, 0.6), vec2(-0.6, 0.8)) * pixel / (macro_size * 0.45) + 17.0);
			surface *= 1.0 + macro_strength * (n * 2.0 - 1.0);
		}
		COLOR = vec4(surface, 1.0);
	} else {
		COLOR = c;
	}
}
