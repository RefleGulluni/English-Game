extends RefCounted

const CORE := ["MOURN", "LINGER", "CONCEAL", "REASSEMBLE"]
const ELASTIC := ["REMAINS", "HOLLOW", "BURY", "HAUNT", "WITHER", "SCATTER", "GRAVE", "ECHO"]
const DATA := {
	"MOURN": ["feel or express sorrow for someone who died", "The caretaker weeps beside a friend's grave.", "The Wraith's grief intensifies pressure.", "They ___ their lost companion.", "MOURNING predicts increasing Grave Pressure."],
	"LINGER": ["remain longer than expected", "The bell stops, but its sound remains in the air.", "The Wraith returns before the survival vigil ends.", "The last notes ___ after the bell falls silent.", "Dispersal is temporary; the vigil must still finish."],
	"CONCEAL": ["hide from sight or discovery", "Moss covers the name on the stone.", "A veiled ghost hides its true intent.", "The fog can ___ the inscription.", "OBSERVE reveals hidden or false intent."],
	"REASSEMBLE": ["put separated parts together again", "Loose bones join into the shape of a skeleton.", "Bone Remains reform after their countdown.", "The scattered bones begin to ___.", "Destroy Remains or delay their countdown before reassembly."],
	"REMAINS": ["what is left after something is gone", "Bones lie where the body once rested.", "Bone Remains persist after the skeleton falls.", "Only the ___ of the old body are left.", "Remains are a separate target, not immediate victory."],
	"HOLLOW": ["having an empty space inside", "The empty skull makes a thin sound.", "A ghost has no material Structure.", "The empty skull is ___.", "Incorporeal targets have no Structure to break."],
	"BURY": ["place and cover beneath the ground", "The caretaker covers a coffin with earth.", "The grave conceals a body's resting place.", "They ___ the coffin beneath the earth.", "Burial is a scene concept, not a new damage spell."],
	"HAUNT": ["appear repeatedly as a ghost or troubling memory", "The same shadow returns every night.", "A Wraith reforms after dispersal.", "Memories of the lost still ___ this place.", "Dispersal does not end a survival encounter."],
	"WITHER": ["lose strength or freshness gradually", "Flowers beside the stone slowly dry out.", "ERODE weakens defenses over time.", "Without water, the flowers ___.", "Gradual weakening is distinct from direct HP damage."],
	"SCATTER": ["spread separated pieces over an area", "A broken skeleton's bones spread across the path.", "SHATTER breaks apart Bone Remains efficiently.", "The blow will ___ the loose bones.", "SHATTER is more efficient than STRIKE against Remains."],
	"GRAVE": ["a place where a dead body is buried", "A marked burial place lies beneath the stone.", "The Cemetery grows restless as turns pass.", "A stone marks the person's ___.", "Grave Pressure is encounter-local, not persistent corruption."],
	"ECHO": ["a sound heard again after reflection", "A bell's sound returns from the stone walls.", "An Echo copy repeats a learned Word and exhausts.", "An ___ answers the bell from the walls.", "Echo copies cost more and Exhaust after use."],
}
const FORMS := {"mourns": "MOURN", "mourned": "MOURN", "mourning": "MOURN", "lingers": "LINGER", "lingered": "LINGER", "lingering": "LINGER", "conceals": "CONCEAL", "concealed": "CONCEAL", "concealing": "CONCEAL", "reassembles": "REASSEMBLE", "reassembled": "REASSEMBLE", "reassembling": "REASSEMBLE", "erodes": "ERODE", "eroded": "ERODE", "eroding": "ERODE", "buried": "BURY", "buries": "BURY", "burying": "BURY", "haunted": "HAUNT", "haunts": "HAUNT", "haunting": "HAUNT", "withered": "WITHER", "withers": "WITHER", "withering": "WITHER", "scattered": "SCATTER", "scatters": "SCATTER", "scattering": "SCATTER", "graves": "GRAVE", "echoes": "ECHO", "echoed": "ECHO", "echoing": "ECHO"}

## The meaning a player sees once they recognise a word: from the word library (D-071), or the
## 0.8 line below if the library does not have it. The rest of each DATA row (scenes, combat
## lines, cloze, mechanism) is 0.8 learning content, kept until the new learning screens.
static func meaning(lemma_id: String) -> String:
	var id := lemma(lemma_id)
	var fallback := str(DATA[id][0]) if id in DATA else ""
	return preload("res://scripts/run/word_library.gd").sense(id, fallback)

static func lemma(surface: String) -> String:
	return str(FORMS.get(surface.to_lower(), surface.to_upper()))

static func word(lemma_id: String):
	return preload("res://scripts/run/cemetery_knowledge.gd").new(lemma(lemma_id))
