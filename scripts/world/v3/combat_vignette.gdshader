shader_type canvas_item;
// "The world turns dangerous" when a fight starts (KB Combat Presentation): the room's edges sink
// into cold dark mist around the two fighters instead of the camera zooming in, which pixel art
// cannot do (only whole-number scaling). Light and fog may be smooth (Art Bible v3 §7).

uniform vec4 mist_color : source_color = vec4(0.04, 0.05, 0.07, 1.0);
uniform float strength = 0.0; // 0 = exploring, 1 = fully in the fight
uniform vec2 center = vec2(0.5, 0.45); // the middle of the two fighters, in screen UV
uniform float clear_radius = 0.24; // stays untouched around them
uniform float max_alpha = 0.62;
uniform vec2 size = vec2(960.0, 540.0);

void fragment() {
	vec2 d = (UV - center) * vec2(size.x / size.y, 1.0);
	float r = length(d);
	float a = smoothstep(clear_radius, clear_radius + 0.55, r) * max_alpha;
	COLOR = vec4(mist_color.rgb, a * strength);
}
