extends SceneTree

const WORD := preload("res://scripts/run/word_knowledge.gd")
const AUTO := preload("res://tests/auto_combat.gd")
var failures: Array[String] = []
var checks := 0

func _initialize() -> void:
	var victories := 0
	for seed_index in range(48):
		var erode = _word("erode")
		var toxic = _word("toxic")
		var combat := CombatState.new()
		var index := seed_index % 6
		combat.start_battle(index, {"knowledge": erode, "toxic_knowledge": toxic, "deck_seed": 8300 + seed_index * 17, "relics": ["echo_chamber", "unfinished_sentence", "clear_lens", "quiet_mind"]})
		combat.changed.connect(_verify.bind(combat))
		var won := AUTO.fight(combat)
		victories += 1 if won else 0
		_verify(combat)
		if not combat.finished:
			failures.append("Combat did not terminate within 60 legal rounds: seed %d" % seed_index)
	for failure in failures:
		push_error(failure)
	print("ECOLOGY_SEED_SMOKE: %s · 48 seeds · %d invariant checks · policy wins %d/48" % ["PASS" if failures.is_empty() else "FAIL", checks, victories])
	quit(0 if failures.is_empty() else 1)

func _word(id: String):
	var word := WORD.new(id)
	word.recognize("seed_test")
	word.record_combat_context(true)
	word.record_transfer(true)
	word.record_production(true)
	return word

func _verify(combat: CombatState) -> void:
	checks += 1
	var ids := {}
	var count := 0
	for pile in [combat.deck.hand, combat.deck.draw_pile, combat.deck.discard_pile, combat.deck.exhaust_pile]:
		for card in pile:
			count += 1
			if ids.has(card.instance_id):
				failures.append("Duplicate card instance across piles")
			ids[card.instance_id] = true
	if count != combat.deck.next_id:
		failures.append("Lost or duplicated card after play / discard / shuffle / Echo / Exhaust")
	if combat.focus < 0 or combat.focus > 4 or combat.hp < 0 or combat.enemy.hp < 0 or combat.enemy.armor < 0:
		failures.append("Combat resource invariant violated")
	for effect in combat.enemy_effects.active.values():
		if effect.stack_count != 1 or effect.duration < 1 or effect.duration > 4:
			failures.append("Semantic effect unexpectedly stacks or extends without bound")
