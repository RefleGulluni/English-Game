extends RefCounted

const WORDS := preload("res://scripts/run/cemetery_words.gd")
const EXTRA := {
	"ERODE": ["wear away or weaken gradually", "Rain erodes the old gravestone, slowly wearing its carved letters away.", "The carved letters become less distinct as the stone slowly wears away.", "Rain slowly ___ the gravestone.", "erodes"],
	"TOXIC": ["harmful or poisonous", "The caretaker seals a toxic vial. A spilled drop kills the nearby flowers.", "The substance harms living things instead of restoring them.", "The liquid is ___ to the flowers.", "toxic"],
}
const VARIANTS := {
	"MOURN": ["The caretaker mourns a friend who died. His tears express sorrow, not anger.", "A mourner kneels at the burial stone, grieving for someone lost."],
	"LINGER": ["The bell is silent now, but its sound still lingers in the air.", "The smoke lingers after the candle goes out; it stays longer than expected."],
	"CONCEAL": ["Moss conceals the inscription. Beneath it the name is hidden, not destroyed.", "The veil conceals the ghost's intent until you look beneath it."],
	"REASSEMBLE": ["The separated bones reassemble, joining together into a body again.", "The caretaker reassembles the broken marker, putting its pieces back together."],
	"REMAINS": ["The remains are what is left of the body after it has fallen.", "Only the old coffin's remains are left: broken wood where it once stood."],
	"HOLLOW": ["The skull is hollow: there is an empty space inside it.", "A hollow tree shelters the candle in its empty interior."],
	"BURY": ["They bury the coffin, placing it below the earth and covering it.", "The caretaker buries a keepsake beneath the grave's soil."],
	"HAUNT": ["The shadow haunts the grave, returning like a ghost each night.", "Memories haunt the caretaker; they keep returning to trouble him."],
	"WITHER": ["The flowers wither: they gradually lose freshness and strength.", "The leaves wither on the neglected wreath, slowly drying out."],
	"SCATTER": ["The blow scatters the bones, spreading the separated pieces across the path.", "The wind scatters dry petals over the graves."],
	"GRAVE": ["The grave is the place where the body was buried beneath the marker.", "A fresh grave holds the buried coffin under the earth."],
	"ECHO": ["An echo is the bell's sound returning after reflection from the stone walls.", "The caretaker calls once; an echo answers as the sound reflects back."],
	"ERODE": ["Rain erodes the stone by slowly wearing it away, not by exploding it.", "Wind erodes the marker's edges, gradually weakening the stone."],
	"TOXIC": ["The vial is toxic: its liquid is harmful or poisonous to living things.", "Toxic mist damages the flowers; it harms them instead of making them stronger."],
}
const WORLD_CONTEXT := {
	"MOURN": "The caretaker is expressing sorrow for someone who died.",
	"LINGER": "The sound stays after the bell has stopped producing it.",
	"CONCEAL": "Removing the moss would reveal the hidden name underneath.",
	"REASSEMBLE": "The separated bones are joining into a whole body again.",
	"REMAINS": "The bones are what is left after the body is gone.",
	"HOLLOW": "There is an empty space inside the skull.",
	"BURY": "The earth covers the coffin after it is placed below ground.",
	"HAUNT": "The shadow repeatedly returns to the same place.",
	"WITHER": "The flowers gradually lose their freshness and strength.",
	"SCATTER": "The separated bones spread over the path, rather than joining together.",
	"GRAVE": "The marked place holds a body buried beneath the earth.",
	"ECHO": "The returning sound is the original bell sound reflected by the walls.",
}

static func exercise(id: String, node: Dictionary, schedule) -> Dictionary:
	var data: Array = WORDS.DATA[id] if id in WORDS.DATA else EXTRA[id]
	var kind: String = schedule.weak_layer(id)
	var correct := str(data[0])
	var prompt := str(data[1]) + "\nWhat does %s mean in this scene?" % id
	var options: Array[String] = [correct, "restore physical health immediately", "tie a moving object in place"]
	if kind == "context":
		correct = str(WORLD_CONTEXT[id]) if id in WORLD_CONTEXT else str(data[2])
		prompt = str(data[1]) + "\nWhich consequence fits this scene?"
		options = [correct, "The word always means immediate direct HP damage.", "The word has no connection to this scene."]
	elif kind == "production":
		correct = str(data[4]) if id in EXTRA else id
		prompt = str(data[3]) + "\nThe caretaker asks you to describe what happens."
		options = [correct, "RESTORE", "BIND"]
	var history: Array = schedule.records[id].corrective_history
	var candidates: Array = []
	for index in range(VARIANTS[id].size()):
		if not history.any(func(row): return int(row.variant) == index and schedule.clock - int(row.clock) < int(preload("res://scripts/run/pacing_config.gd").QA.corrective_reuse_gap)):
			candidates.append(index)
	var chosen: int = int(candidates[schedule.clock % candidates.size()]) if not candidates.is_empty() else schedule.clock % VARIANTS[id].size()
	return {"id": "%s:%s:%s" % [node.id, id, kind], "wordSenseId": schedule.records[id].sense_id, "evidenceType": kind, "errorCategory": kind, "prompt": prompt, "correctAnswer": correct, "options": options, "correctiveLine": VARIANTS[id][chosen], "correctiveContextTag": str(node.id), "variant": chosen, "semanticCompatibilityTags": node.get("words", []), "prerequisiteKnowledgeStage": schedule.words[id].current_state, "targetKnowledgeStage": "RECOGNIZED" if kind == "recognition" else ("UNDERSTOOD" if kind == "context" else "USABLE")}
