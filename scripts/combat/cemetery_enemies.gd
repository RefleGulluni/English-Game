extends RefCounted

static func concept(word: String, amount: int, text: String, extra: Dictionary = {}) -> Dictionary:
	var result := {"word": word, "kind": "concept", "family": "Obscurity", "corruption": amount, "sense": text, "partial": text, "clear": "%s · Obscurity +%d." % [text, amount]}
	result.merge(extra, true)
	return result

static func hit(word: String, damage: int) -> Dictionary:
	return {"word": word, "kind": "physical", "damage": damage, "family": "Obscurity", "sense": "strike with a cemetery weapon", "partial": "A physical strike approaches.", "clear": "%d Physical Damage. DEFLECT can answer." % damage}

static func profile(id: String, name: String, hp: int, structure: int, actions: Array, traits: Array, words: Array) -> Dictionary:
	var sequence: Array[String] = []
	for action in actions:
		sequence.append(str(action.word))
	return {"enemy_id": id, "name": name, "subtitle": "Cemetery · " + " / ".join(traits), "families": ["OBSCURITY"], "hp": hp, "structure": structure, "armor": 0, "max_armor": 12, "has_structure": structure > 0, "traits": traits, "words": words, "tutorial": " / ".join(traits), "actions": actions, "sequence": sequence}

static func profiles() -> Array:
	var veil := profile("veil_ghost", "VEIL GHOST", 28, 0, [concept("CONCEAL", 10, "Hide the real intent.", {"hidden": true}), hit("PHANTOM TOUCH", 5)], ["INCORPOREAL", "PHASE SHIFT", "FALSE INTENT"], ["CONCEAL", "HOLLOW"])
	veil["ghost_family"] = true
	veil["toxic_resistance"] = 0.75
	var skeleton := profile("grave_skeleton", "GRAVE SKELETON", 24, 12, [hit("BONE CUT", 5), concept("GRAVE DUST", 4, "The bones shed dust that obscures the grave.")], ["BONE REMAINS", "REASSEMBLE"], ["REASSEMBLE", "REMAINS", "SCATTER"])
	skeleton.actions.append(concept("ERODE", 6, "Grave dust gradually wears away your Armor.", {"family": "Decay", "armor_damage": 1}))
	skeleton.actions.append(concept("TOXIC DUST", 0, "Poisonous residue drifts from the bones.", {"poison": 3}))
	skeleton.sequence.append_array(["ERODE", "TOXIC DUST"])
	var wraith := profile("mourning_wraith", "MOURNING WRAITH", 30, 8, [concept("MOURN", 8, "Sorrow intensifies Grave Pressure.", {"mourning": true}), hit("GRIEF TOUCH", 5), concept("LINGER", 6, "The grief remains after the sound fades.")], ["MOURNING"], ["MOURN", "LINGER", "HAUNT"])
	var boss := profile("mourning_keeper", "THE MOURNING KEEPER", 64, 16, [concept("MOURN", 8, "Sorrow gathers behind the veil.", {"hidden": true, "mourning": true}), hit("KEEPER'S STAFF", 6), concept("CONCEAL", 10, "Hide the true intent.", {"hidden": true})], ["VEILED MOURNING", "GRAVE AWAKENING"], ["MOURN", "CONCEAL"])
	return [veil, skeleton, wraith, boss]
