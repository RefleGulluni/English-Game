shader_type canvas_item;
render_mode unshaded;
uniform float density : hint_range(0.0, 0.12) = 0.045;
void fragment() {
	vec2 p = UV + vec2(TIME * 0.003, TIME * 0.001);
	float bands = pow(0.5 + 0.5 * sin(p.y * 32.0 + sin(p.x * 9.0 + TIME * 0.13)), 5.0);
	float holes = 0.5 + 0.5 * sin(p.x * 21.0 + p.y * 13.0);
	COLOR = vec4(0.57, 0.64, 0.65, bands * holes * density);
}
