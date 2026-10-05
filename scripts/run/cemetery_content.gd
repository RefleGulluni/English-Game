extends RefCounted

const WORDS := preload("res://scripts/run/cemetery_words.gd")
const BIOME := {"biome_id": "cemetery", "display_name": "Cemetery", "layers": 6, "native_enemy_tags": ["GHOST", "SKELETON", "WRAITH"], "target_word_tags": ["DEATH", "MEMORY", "HIDDEN", "DECAY", "REMAINS", "SILENCE", "GRIEF", "BURIAL"], "biome_property": "GRAVE PRESSURE"}
const RELICS := ["clear_lens", "unfinished_sentence", "iron_script", "venom_vessel", "mourner_thread", "ossuary_key", "pale_candle", "echo_chamber"]
const POOL := [
	{"id": "ghost", "type": "encounter", "title": "GHOST", "battle": 5, "weight": 12.0, "words": ["CONCEAL", "HOLLOW"], "echo": 18},
	{"id": "veil_ghost", "type": "encounter", "title": "VEIL GHOST", "battle": 6, "weight": 10.0, "words": ["CONCEAL", "HOLLOW"], "echo": 20},
	{"id": "grave_skeleton", "type": "encounter", "title": "GRAVE SKELETON", "battle": 7, "weight": 12.0, "words": ["REASSEMBLE", "REMAINS", "SCATTER"], "echo": 20},
	{"id": "neglect_wraith", "type": "encounter", "title": "NEGLECT WRAITH · SURVIVE", "battle": 2, "objective": "survive", "weight": 10.0, "words": ["LINGER", "HAUNT"], "echo": 20},
	{"id": "mourning_wraith", "type": "encounter", "title": "MOURNING WRAITH", "battle": 8, "weight": 11.0, "words": ["MOURN", "LINGER"], "echo": 22},
	{"id": "elite_skeleton", "type": "elite", "title": "GRAVE SKELETON · ELITE", "battle": 7, "elite": true, "min_layer": 2, "weight": 5.0, "words": ["REASSEMBLE"], "echo": 40},
	{"id": "elite_veil", "type": "elite", "title": "VEIL GHOST · ELITE", "battle": 6, "elite": true, "min_layer": 2, "weight": 5.0, "words": ["CONCEAL"], "echo": 40},
	{"id": "mourning_stone", "type": "event", "title": "THE MOURNING STONE", "weight": 8.0, "words": ["MOURN", "BURY", "GRAVE"]},
	{"id": "hidden_epitaph", "type": "event", "title": "THE HIDDEN EPITAPH", "weight": 8.0, "words": ["CONCEAL", "HOLLOW"]},
	{"id": "scattered_bones", "type": "event", "title": "THE SCATTERED BONES", "weight": 8.0, "words": ["REASSEMBLE", "REMAINS", "SCATTER"]},
	{"id": "lingering_bell", "type": "event", "title": "THE LINGERING BELL", "weight": 8.0, "words": ["LINGER", "ECHO", "HAUNT"]},
	{"id": "grave_inscription", "type": "event", "title": "GRAVE INSCRIPTION", "weight": 7.0, "words": WORDS.CORE + WORDS.ELASTIC, "production": true},
	{"id": "caretaker_note", "type": "event", "title": "THE CARETAKER'S NOTE", "weight": 7.0, "words": WORDS.CORE + WORDS.ELASTIC, "production": true},
	{"id": "withered_flowers", "type": "event", "title": "WITHERED FLOWERS", "weight": 5.0, "words": ["WITHER", "MOURN"]},
	{"id": "rest", "type": "rest", "title": "SHELTERED GRAVE", "weight": 7.0, "words": [], "safe": true},
	{"id": "relic_cache", "type": "relic", "title": "CARETAKER'S RELIC", "weight": 3.0, "min_layer": 2, "words": [], "safe": true},
]

static func node(id: String) -> Dictionary:
	for entry in POOL:
		if entry.id == id:
			return entry.duplicate(true)
	return {}

static func boss() -> Dictionary:
	return {"id": "mourning_keeper", "type": "final", "title": "THE MOURNING KEEPER", "battle": 9, "echo": 90, "words": ["MOURN", "CONCEAL"], "detail": "Two-phase Boss. Veiled Mourning → Grave Awakening."}
