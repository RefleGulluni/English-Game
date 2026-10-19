shader_type canvas_item;
render_mode unshaded;
uniform float strength : hint_range(0.0, 0.2) = 0.07;
float wave(vec2 p) {
	return (sin(p.x*9.0+sin(p.y*5.0))*sin(p.y*7.0+p.x*3.0)+1.0)*0.5;
}
void fragment() {
	vec2 p = UV + vec2(TIME*0.0018, TIME*0.0004);
	float edge = smoothstep(0.58,0.97,abs(UV.y-0.5)*2.0);
	float mist = wave(p)*wave(p*1.7+0.8);
	COLOR = vec4(0.52,0.57,0.58,strength*edge*mist);
}
