shader_type canvas_item;

// Terrain Prototype v2: stone / mud blend.
// TEXTURE is the dual-grid mask (white = stone, black = mud) built by dual_grid_terrain.gd.
// Stone and mud are sampled in world space so the seamless textures never break at cell borders.

uniform sampler2D stone_tex : repeat_enable, filter_linear_mipmap;
uniform sampler2D mud_tex : repeat_enable, filter_linear_mipmap;
uniform sampler2D noise_tex : repeat_enable, filter_linear;

uniform float stone_world_size = 320.0; // world px covered by one stone texture repeat
uniform float mud_world_size = 420.0;
uniform float noise_world_size = 160.0;

uniform float edge_breakup : hint_range(0.0, 1.0) = 0.22; // painterly wobble of the mask edge
uniform float edge_softness : hint_range(0.0, 0.5) = 0.025;
uniform float joint_bleed : hint_range(0.0, 2.0) = 0.9; // mud creeping into stone joints near the edge
uniform float joint_lo = 0.012;
uniform float joint_hi = 0.05;
uniform float damp_strength : hint_range(0.0, 1.0) = 0.15; // darker wet band on stone next to mud
uniform float mud_desaturate : hint_range(0.0, 1.0) = 0.3;

uniform float warp_noise_world_size = 300.0;

// Set from script, in mask UV (world px / mask world size):
uniform vec2 probe_uv = vec2(0.01); // reach of the wet band / joint bleed
uniform vec2 warp_uv = vec2(0.0); // large-scale wobble that breaks the grid silhouette
uniform vec2 round_uv = vec2(0.0); // blur radius that rounds square corners

varying vec2 world_pos;

void vertex() {
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 0.0, 1.0)).xy;
}

float lum(vec3 c) {
	return dot(c, vec3(0.299, 0.587, 0.114));
}

void fragment() {
	vec2 suv = world_pos / stone_world_size;
	vec3 stone = texture(stone_tex, suv).rgb;
	vec3 mud = texture(mud_tex, world_pos / mud_world_size).rgb;
	mud = mix(mud, vec3(lum(mud)), mud_desaturate);

	// Domain warp: shift where the mask is read by a slow noise, so edges stop following the grid.
	vec2 wp = world_pos / warp_noise_world_size;
	vec2 warp = vec2(texture(noise_tex, wp).r, texture(noise_tex, wp + vec2(0.37, 0.71)).r) - 0.5;
	vec2 muv = UV + warp * 2.0 * warp_uv;

	// Blurred read of the mask: rounds the square corners the brushes inherit from the grid.
	float mask = texture(TEXTURE, muv).r;
	for (int k = 0; k < 12; k++) {
		float a = float(k) * 0.5235988;
		vec2 dir = vec2(cos(a), sin(a));
		mask += texture(TEXTURE, muv + dir * round_uv).r + texture(TEXTURE, muv + dir * round_uv * 0.5).r;
	}
	mask /= 25.0;

	// How close this pixel is to mud: 0 deep inside stone, ~0.5 right at the edge.
	float around = 0.0;
	for (int k = 0; k < 12; k++) {
		float a = float(k) * 0.5235988;
		around += texture(TEXTURE, muv + vec2(cos(a), sin(a)) * probe_uv).r;
	}
	float mud_near = clamp(1.0 - around / 12.0, 0.0, 1.0);

	// Joints are darker than the local average of the stone texture.
	float local_avg = lum(textureLod(stone_tex, suv, 5.0).rgb);
	float joint = smoothstep(joint_lo, joint_hi, local_avg - lum(stone));

	float n = texture(noise_tex, world_pos / noise_world_size).r;
	float field = mask + (n - 0.5) * edge_breakup - joint * joint_bleed * smoothstep(0.05, 0.5, mud_near);
	float s = smoothstep(0.5 - edge_softness, 0.5 + edge_softness, field);

	vec3 wet_stone = stone * (1.0 - damp_strength * smoothstep(0.0, 0.45, mud_near));
	COLOR = vec4(mix(mud, wet_stone, s), 1.0);
}
