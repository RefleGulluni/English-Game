extends SceneTree

const FIXTURE := preload("res://tests/mechanics_fixture.gd")
const WORDS := preload("res://scripts/run/cemetery_words.gd")
var failures: Array[String] = []

func check(value: bool, message: String) -> void:
	if not value: failures.append(message)

func combat(index: int, relics: Array = [], biome: String = "cemetery") -> CombatState:
	var run := RunManager.new()
	run.start_cemetery_run(123)
	var snapshot := run.state.combat_snapshot()
	snapshot.relics = relics
	snapshot.biome_id = biome
	var result := CombatState.new()
	result.start_battle(index, snapshot)
	result.finish_mulligan()
	result.focus = 100
	return result

func round_end(c: CombatState) -> void:
	c.end_player_turn()
	if c.turn_ending: c.resolve_enemy_action(false)
	c.focus = 100

func _initialize() -> void:
	var c := combat(5)
	check(c.grave_pressure == 0, "Pressure begins at zero")
	c._add_corruption("Obscurity", 5)
	check(c.corruption.Obscurity == 5, "Quiet has no penalty")
	c.grave_pressure = 3
	c._add_corruption("Obscurity", 5)
	c._add_corruption("Obscurity", 5)
	check(c.corruption.Obscurity == 17, "first positive Obscurity gain only +2")
	c.grave_pressure = 5
	c._begin_player_turn(0, true)
	check(c.corruption.Obscurity == 22, "Awakened dominant gain +3 and first Obscurity +2")
	c._finish_battle(true)
	check(c.grave_pressure == 0, "battle outcome resets Pressure")
	c = combat(5)
	round_end(c)
	check(c.grave_pressure == 1, "completed round increments Pressure once")
	c = combat(5, ["pale_candle"], "other_biome")
	c.grave_pressure = 5
	c._add_corruption("Obscurity", 10)
	check(c.corruption.Obscurity == 6, "Candle base effect works outside Cemetery")
	c._begin_player_turn(0, true)
	check(c.corruption.Obscurity == 6, "no Cemetery resonance outside biome")
	c = combat(5, ["pale_candle"])
	c.corruption.Decay = 10
	c.grave_pressure = 5
	c._begin_player_turn(0, true)
	check(c.corruption.Decay == 10, "Candle first Awakened -3 before dominant +3")
	c._begin_player_turn(0, true)
	check(c.corruption.Decay == 13, "Awakened Candle resonance only once")
	c = combat(6, ["mourner_thread"])
	c.grave_pressure = 4
	check(not c.false_intent.is_empty(), "Veil Ghost has a real false possibility")
	c.target_knowledge.CONCEAL.recognize("epitaph")
	FIXTURE.play(c, "OBSERVE")
	check(c.false_removed and c.hidden_revealed and c.modifier_discount and c.grave_pressure == 3, "hidden reveal triggers thread and resonance")
	check(c.target_knowledge.CONCEAL.current_state == "UNDERSTOOD", "actual reveal earns combat context")
	c.toxic_knowledge.recognize("vial")
	c.toxic_knowledge.record_combat_context(true)
	c.toxic_knowledge.record_transfer(true)
	c.toxic_knowledge.record_production(true)
	var toxic := c.deck.make_card("TOXIC")
	check(c.card_cost(toxic) == 0, "thread reduces next Modifier cost by one")
	c.deck.hand.append(toxic)
	c.use_card(int(toxic.instance_id))
	check(not c.modifier_discount, "Modifier consumes one-shot discount")
	check(c.poison_tick_damage() == 1, "Veil Ghost retains Toxic Resistance")
	c = combat(7)
	FIXTURE.play(c, "BIND")
	c.enemy.hp = 0
	c._enemy_defeated()
	check(not c.delayed_this_turn and not c.intent_bound_once, "normal BIND cannot leak into the new Remains intent")
	check(c.bone_remains and not c.finished and c.remains_hp == 10 and c.reassembly_countdown == 2, "HP zero becomes Remains, not Victory")
	var before_hp := c.hp
	round_end(c)
	check(c.hp == before_hp and c.reassembly_countdown == 1, "Remains cannot attack and counts down")
	FIXTURE.play(c, "BIND")
	check(c.reassembly_countdown == 2 and not c.can_use("BIND"), "BIND delays once, not forever")
	round_end(c)
	round_end(c)
	check(not c.bone_remains and c.enemy.hp == 12 and c.enemy.structure == 6 and not c.finished, "Skeleton reassembles at half resources")
	c.enemy.hp = 0
	c._enemy_defeated()
	c.focus = 100
	FIXTURE.play(c, "STRIKE")
	check(c.remains_hp == 7, "STRIKE handles Remains inefficiently")
	FIXTURE.play(c, "SHATTER")
	check(c.finished, "SHATTER prevents reassembly and wins")
	c = combat(7, ["ossuary_key"])
	c.grave_pressure = 4
	c.enemy.hp = 0
	c._enemy_defeated()
	FIXTURE.play(c, "SHATTER")
	check(c.finished and c.ossuary_used, "Key strengthens Remains handling and triggers first prevention")
	c = combat(8)
	c.target_knowledge.MOURN.recognize("stone")
	for index in range(3): round_end(c)
	check(c.mourning == 3 and c.grave_pressure == 4 and c.target_knowledge.MOURN.has_insight(), "Mourning accumulates and intensifies Pressure with actual context")
	FIXTURE.play(c, "OBSERVE")
	check(c.mourning == 1, "OBSERVE reduces Mourning")
	c = combat(9)
	check(c.boss_phase == 1 and "UNKNOWN SORROW" in c.intent_description(), "Boss starts hidden phase one")
	c.target_knowledge.MOURN.recognize("stone")
	c.target_knowledge.MOURN.context("stone")
	check("MOURNING · Grave Pressure" in c.intent_description(), "Mourn understanding improves information only")
	check(c.enemy.hp == 64, "Knowledge does not reduce Boss HP")
	FIXTURE.play(c, "OBSERVE")
	check(c.hidden_revealed, "OBSERVE reveals Boss intent")
	c.enemy.hp = 32
	c._check_boss_phase()
	check(c.boss_phase == 2, "Boss enters phase two at half HP")
	c.intent = preload("res://scripts/combat/cemetery_enemies.gd").hit("KEEPER'S STAFF", 7)
	c.grave_pressure = 5
	c.intent_clarity = 2
	check("9 Physical Damage" in c.intent_description(), "clear Boss warning includes Phase 2 high-Pressure damage")
	var pressure_before := c.grave_pressure
	round_end(c)
	check(c.grave_pressure >= pressure_before + 2, "phase two accelerates Pressure")
	c.enemy.hp = 0
	c._enemy_defeated()
	check(c.finished, "Boss has exactly two phases and can be defeated")
	c = combat(4, ["venom_vessel", "echo_chamber"])
	c.toxic_knowledge.recognize("vial")
	c.toxic_knowledge.record_combat_context(true)
	c.toxic_knowledge.record_transfer(true)
	c.toxic_knowledge.record_production(true)
	FIXTURE.play(c, "TOXIC")
	check(c.enemy_effects.duration("POISONED") == 4, "Venom Vessel first application +1 duration")
	check(c.deck.hand.any(func(card): return card.name == "TOXIC" and card.echo and card.exhaust_on_use), "Echo still uses existing Word system")
	FIXTURE.play(c, "TOXIC")
	check(c.enemy_effects.duration("POISONED") == 3, "refresh remains nonstacking; first bonus not permanent")
	c.delayed_this_turn = true
	c.start_battle(5)
	check(not c.delayed_this_turn, "old BIND cannot leak into the next encounter")
	for message in failures: push_error(message)
	print("CEMETERY_COMBAT_SMOKE: %s" % ("PASS" if failures.is_empty() else "FAIL"))
	quit(0 if failures.is_empty() else 1)
