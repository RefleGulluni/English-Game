extends SceneTree

# 词条数据（D-070）在 Godot 里能读、字段齐全；完整的检查在 scripts/tools/vocab/check_words.py。
const ENTRIES := "res://data/words/entries/"
var failures: Array[String] = []

func _initialize() -> void:
	var tags: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/words/tags.json"))
	_check(tags != null and tags.tags.has("BURIAL"), "tag table loads")
	var cemetery: Array = tags.regions.cemetery
	var count := 0
	for file in DirAccess.get_files_at(ENTRIES):
		if not file.ends_with(".json"):
			continue
		var entry = JSON.parse_string(FileAccess.get_file_as_string(ENTRIES + file))
		_check(entry is Dictionary and entry.lemma + ".json" == file, "%s parses" % file)
		if not entry is Dictionary:
			continue
		for sense in entry.senses:
			count += 1
			_check(str(sense.id).begins_with(entry.lemma + "#"), "%s has a sense id" % file)
			_check(not sense.tags.is_empty(), "%s has tags" % sense.id)
			for tag in sense.tags:
				_check(tags.tags.has(tag), "%s tag %s is in the table" % [sense.id, tag])
			_check(sense.role != "ability" or sense.effect.has("cost"), "%s ability has a cost" % sense.id)
	_check(count >= 38, "first batch present (%d senses)" % count)
	var grave = JSON.parse_string(FileAccess.get_file_as_string(ENTRIES + "grave.json"))
	var shared := 0
	for tag in grave.senses[0].tags:
		if tag in cemetery:
			shared += 1
	_check(shared == 2, "grave shares two tags with the cemetery")
	_check("cet4" in grave.dictionary.exam, "dictionary fields are filled in")
	if failures.is_empty():
		print("WORD_DATA_SMOKE: PASS")
		quit(0)
	else:
		for failure in failures:
			print("FAIL: ", failure)
		quit(1)

func _check(condition: bool, description: String) -> void:
	if not condition:
		failures.append(description)
