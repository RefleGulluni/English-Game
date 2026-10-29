extends SceneTree

# D-075: a new player can use only the five words learned in the prologue; the deck is built from
# the words they can use; ANCHOR stops the next wearing-away.
const PROGRESS := preload("res://scripts/run/lexicon_progress.gd")
const FIXTURE := preload("res://tests/mechanics_fixture.gd")
var failures: Array[String] = []

func _initialize() -> void:
	var progress = PROGRESS.new()
	progress.save_path = ""
	progress.load_or_start()
	var usable: Array[String] = progress.usable_abilities()
	_check(usable.size() == 5 and "anchor" in usable and "strike" in usable, "a new player starts with the five prologue words: %s" % [usable])
	_check(not "shatter" in usable and not "erode" in usable, "words not yet learned stay out")
	var deck: Array[String] = progress.deck_cards()
	_check(deck.size() == 9 and deck.count("STRIKE") == 3 and deck.count("OBSERVE") == 2 and deck.count("ANCHOR") == 1, "starting deck is 9 cards: %s" % [deck])

	progress.set_stage("shatter", "USABLE")
	_check(progress.deck_cards().count("SHATTER") == 1, "learning SHATTER adds it to the deck")
	progress.set_stage("shatter", "RECOGNIZED")
	_check(progress.stage("shatter") == "USABLE", "a learned word is never unlearned")
	progress.learn_all_abilities()
	_check(progress.deck_cards().has("DEFLECT") and not progress.deck_cards().has("SEAL"), "every word combat can play joins; words without a combat effect yet wait")
	progress.reset_to_start()
	_check(progress.usable_abilities().size() == 5, "dev reset returns to the five words")

	var combat := CombatState.new()
	var profile: Dictionary = preload("res://data/enemies/enemy_grave_skeleton.tres").profile()
	combat.start_battle(7, {"enemy_profile": profile, "deck_cards": deck, "deck_seed": 11})
	var all_cards: Array = combat.deck.hand + combat.deck.draw_pile
	_check(all_cards.size() == 9 and all_cards.all(func(card): return str(card.name) in ["STRIKE", "OBSERVE", "BIND", "STABILIZE", "ANCHOR"]), "the fight uses the player's deck, not the 0.8 starter")
	combat.focus = 10
	FIXTURE.play(combat, "ANCHOR")
	_check(combat.anchored, "ANCHOR holds")
	var erode := {}
	for action in combat.enemy.actions:
		if str(action.word) == "ERODE":
			erode = action
	combat.intent = erode
	var armor_before := combat.armor
	var decay_before := int(combat.corruption.get("Decay", 0))
	combat.resolve_enemy_action(false)
	_check(combat.armor == armor_before and int(combat.corruption.get("Decay", 0)) == decay_before, "ANCHOR stops ERODE: no Armor lost, no Decay")
	_check(not combat.anchored, "ANCHOR is spent")

	if failures.is_empty():
		print("STARTING_WORDS_SMOKE: PASS")
		quit(0)
	else:
		for failure in failures:
			print("FAIL: ", failure)
		quit(1)

func _check(condition: bool, description: String) -> void:
	if not condition:
		failures.append(description)
