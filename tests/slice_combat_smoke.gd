extends SceneTree

const DATA := preload("res://data/enemies/enemy_grave_skeleton.tres")
const FIXTURE := preload("res://tests/mechanics_fixture.gd")
var failures: Array[String] = []

func check(value: bool, message: String) -> void:
	if not value: failures.append(message)

func _initialize() -> void:
	var c := CombatState.new()
	c.start_battle(7, {"enemy_profile": DATA.profile(), "reassembly_rounds": DATA.reassembly_rounds, "remains_integrity": DATA.remains_integrity})
	c.finish_mulligan()
	c.enemy.hp = 1 # Unit fixture: isolate the transition, not a claimed legal playthrough.
	FIXTURE.play(c, "STRIKE")
	check(c.bone_remains and not c.finished and c.remains_hp == 10 and c.reassembly_countdown == 3, "HP0 creates live Remains with three-round window")
	var rounds := c.completed_rounds
	for left in [2, 1]:
		c.end_player_turn()
		check(c.bone_remains and c.reassembly_countdown == left, "no early reassembly")
	c.end_player_turn()
	check(not c.bone_remains and c.completed_rounds == rounds + 3 and c.enemy.hp == 12 and c.enemy.structure == 6, "third complete round restores half HP and Structure")
	c.enemy.hp = 1
	c.focus = 20
	FIXTURE.play(c, "STRIKE")
	check(c.bone_remains and c.reassembly_countdown == 3, "new Remains phase resets countdown")
	FIXTURE.play(c, "BIND")
	check(c.reassembly_countdown == 4 and not c.can_use("BIND"), "BIND delays once per Remains phase")
	FIXTURE.play(c, "STRIKE")
	check(c.remains_hp == 7, "STRIKE deals three Integrity")
	FIXTURE.play(c, "SHATTER")
	check(c.finished and c.hp > 0 and c.remains_hp == 0, "SHATTER deals eight Integrity and clears encounter")
	var state := RunState.new()
	check(state.grant_world_echo_once("enemy:first", 15) and not state.grant_world_echo_once("enemy:first", 15) and state.echo == 15, "disperse Echo ledger prevents repeat farming")
	check(state.claim_world_loot("drop:1", "relic.weathered_chisel") and not state.claim_world_loot("drop:1", "relic.weathered_chisel"), "same object cannot be collected twice")
	check(state.world_inventory["relic.weathered_chisel"] == 1 and "relic.weathered_chisel" in state.relics, "pickup writes run inventory and relic identity without inventing effect")
	state.reset()
	check(state.world_inventory.is_empty() and state.collected_loot_ids.is_empty() and state.world_reward_ledger.is_empty(), "Run reset does not leak loot/reward ledgers")
	for message in failures: push_error(message)
	print("SLICE_COMBAT_SMOKE: %s" % ("PASS" if failures.is_empty() else "FAIL"))
	quit(0 if failures.is_empty() else 1)
