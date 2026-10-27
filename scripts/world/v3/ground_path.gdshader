shader_type canvas_item;
// Path terrain tiles carry only the shape: pure white means "inside the path", every other colour
// (wet rim, stray pebbles) is drawn as it is. White is replaced by the path texture sampled at the
// pixel's world position, so the path surface is one big seamless texture, not a 32 px repeat.

uniform sampler2D path_texture : filter_nearest, repeat_enable;

varying vec2 world_pos;

void vertex() {
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 0.0, 1.0)).xy;
}

void fragment() {
	vec4 c = texture(TEXTURE, UV);
	if (c.a > 0.5 && min(c.r, min(c.g, c.b)) > 0.99) {
		vec2 size = vec2(textureSize(path_texture, 0));
		COLOR = vec4(texture(path_texture, (floor(world_pos) + 0.5) / size).rgb, 1.0);
	} else {
		COLOR = c;
	}
}
