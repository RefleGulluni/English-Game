shader_type canvas_item;
// Mist where a room's ground runs into its far backdrop strip: fading in from nothing (so tall far
// props poking up into the sky are not cut by a straight line), thick across the strip's flat lower
// edge and the straight line where the ground starts, thinning downwards over the far rows of props.
// The lower edge wobbles and drifts slowly, so there is never a ruler-straight line.
// Fog may be smooth (Art Bible v3 §7); the language layer sits above it and is never fogged.

uniform vec4 fog_color : source_color = vec4(0.30, 0.32, 0.36, 1.0);
uniform float max_alpha = 0.78;
uniform float thick_from = 0.22; // share of the height over which it fades in from nothing at the top
uniform float thin_from = 0.35; // share of the height that stays thick before it starts to thin
uniform float wobble = 0.16; // how far (share of the height) the edge moves up and down
uniform float drift = 4.0; // px per second sideways
uniform vec2 size = vec2(960.0, 190.0); // the fog rect in px (a ColorRect has no texture to measure)

float hash(float n) {
	return fract(sin(n) * 43758.5453);
}

float noise(float x) {
	float i = floor(x);
	float f = fract(x);
	f = f * f * (3.0 - 2.0 * f);
	return mix(hash(i), hash(i + 1.0), f);
}

void fragment() {
	vec2 px = UV * size;
	float x = px.x + TIME * drift;
	float edge = noise(x / 90.0) * 0.65 + noise(x / 31.0 + 7.0) * 0.35; // 0..1, two scales of bank
	float d = UV.y + (edge - 0.5) * wobble;
	float a = max_alpha * smoothstep(0.0, thick_from, UV.y) * (1.0 - smoothstep(thin_from, 1.0, d));
	COLOR = vec4(fog_color.rgb, a);
}
