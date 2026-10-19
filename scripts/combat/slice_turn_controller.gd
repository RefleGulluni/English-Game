extends Node

enum Phase { EXPLORATION, COMBAT_ENTER, PLAYER_TURN, ENEMY_TURN, ROUND_RESOLVE, COMBAT_END, DEFEAT }
signal phase_changed(phase: Phase)
var phase := Phase.EXPLORATION
var combat: CombatState
var events: Node

func bind(model: CombatState, bus: Node) -> void:
	combat = model
	events = bus
	combat.round_resolution_started.connect(func(): set_phase(Phase.ROUND_RESOLVE))
	combat.round_completed.connect(func():
		if not combat.finished: set_phase(Phase.PLAYER_TURN))

func set_phase(value: Phase) -> void:
	if phase == value: return
	phase = value
	phase_changed.emit(phase)
	if events != null: events.publish(&"combat_phase_changed", {"phase": Phase.keys()[phase]})

func invoke(uid: int, restore_target: String = "hp") -> bool:
	if phase != Phase.PLAYER_TURN or combat == null or combat.finished: return false
	return combat.use_card(uid, restore_target)

func end_turn() -> void:
	if phase != Phase.PLAYER_TURN or combat == null or combat.deck.mulligan_pending or combat.finished: return
	set_phase(Phase.ENEMY_TURN)
	combat.end_player_turn()

func react(deflect: bool) -> void:
	if phase != Phase.ENEMY_TURN or combat == null or not combat.turn_ending: return
	combat.resolve_enemy_action(deflect)
