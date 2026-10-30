shader_type canvas_item;
// A word seen once and not yet read (ENCOUNTERED, KB Lexicon Interface §5: "incomplete but
// recognisable letterforms"): its first letters stay, the rest loses more and more of its strokes
// towards the end, in whole native pixels and small clumps, as if the world had rubbed it out.
// Seeded by position only, so it holds still.

uniform float strength = 0.0; // 0: draw everything (other stages, the glint)
uniform float erase_from = 0.0; // local x where the rubbing out starts
uniform float erase_to = 1.0; // and where it is heaviest
uniform float seed = 0.0;

varying vec2 local;

void vertex() {
	local = VERTEX;
}

float hash(vec2 p) {
	return fract(sin(dot(p + seed, vec2(12.9898, 78.233))) * 43758.5453);
}

void fragment() {
	float t = smoothstep(erase_from, erase_to, local.x);
	float grain = mix(hash(floor(local)), hash(floor(local / 3.0) + 17.0), 0.65);
	if (grain < strength * (0.2 + 0.62 * t) * step(erase_from, local.x)) {
		COLOR.a = 0.0;
	}
}
