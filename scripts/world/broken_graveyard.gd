extends Node2D

const TURNS := preload("res://scripts/combat/slice_turn_controller.gd")
@export var seed_value := 9019
@export var qa_force_chisel := true
@export var transition_seconds := 0.65
var manager := RunManager.new()
var combat := CombatState.new()
var entered := false
var encounter_started := false
var encounter_cleared := false
var event_trace: Array[Dictionary] = []
var camera_tween: Tween
var previous_corruption: Dictionary = {}
@onready var player = $CharacterLayer/Player
@onready var skeleton = $CharacterLayer/GraveSkeleton
@onready var loot_layer = $LootLayer/WorldLoot
@onready var presentation = $VFXLayer/PresentationRouter
@onready var events = $Systems/Events
@onready var turns = $Systems/TurnController
@onready var interactions = $Systems/InteractionSystem
@onready var rewards = $Systems/RewardController
@onready var hud = $CombatHUD
@onready var camera: Camera2D = $Camera2D

func _ready() -> void:
	preload("res://scripts/systems/slice_input.gd").install()
	if get_tree().has_meta("slice_seed"): seed_value = int(get_tree().get_meta("slice_seed"))
	if get_tree().has_meta("slice_force_drop"): qa_force_chisel = bool(get_tree().get_meta("slice_force_drop"))
	if bool(get_meta("qa_no_save", false)) or bool(get_tree().get_meta("slice_qa_no_save", false)): manager.persistence_path = ""
	manager.start_cemetery_run(seed_value)
	manager.state.current_node_id = "slice.approach"
	turns.bind(combat, events)
	interactions.player = player
	interactions.register($Entrance)
	interactions.register($Exit)
	interactions.target_changed.connect(func(_target, value): hud.prompt.text = value)
	$Entrance.activated.connect(_enter_graveyard)
	$Exit.activated.connect(func(_action): hud.announce("Broken Graveyard slice complete. Continue exploring, or press R to replay."))
	$Exit.enabled = false
	events.occurred.connect(_on_event)
	rewards.qa_force_drop = qa_force_chisel
	rewards.bind(manager.state, events, player, loot_layer, interactions)
	presentation.bind(events)
	hud.bind(manager.state, combat)
	hud.action_requested.connect(_invoke)
	hud.retain_requested.connect(_retain)
	hud.mulligan_confirmed.connect(func(ids):
		if turns.phase == TURNS.Phase.PLAYER_TURN: combat.finish_mulligan(ids))
	hud.end_turn_requested.connect(func():
		if not hud.overlay_open: turns.end_turn())
	hud.reaction_answered.connect(func(value):
		if not hud.overlay_open: turns.react(value))
	hud.overlay_changed.connect(func(_value): _update_lock())
	hud.restart_requested.connect(restart)
	combat.battle_finished.connect(_battle_finished)
	combat.changed.connect(_combat_changed)
	combat.enemy_action_started.connect(func(action):
		events.publish(&"enemy_attack_started", {"enemy_id": "enemy.grave_skeleton", "position": skeleton.global_position, "action": action.word, "kind": action.kind}))
	for word in manager.learning.words.values():
		word.changed.connect(_word_changed.bind(word.lemma))
	camera.position = player.position + Vector2(0, 60)
	hud.refresh()
	hud.announce("Walk east to the gate. Press E when ENTER appears.")
	if not manager.learning.load_notice.is_empty():
		hud.show_overlay("KNOWLEDGE SAVE WARNING", manager.learning.load_notice, [])

func _word_changed(message: String, lemma: String) -> void:
	events.publish(&"knowledge_stage_changed", {"word_id": lemma, "stage": manager.learning.words[lemma].current_state, "message": message})

func _combat_changed() -> void:
	for family in combat.corruption:
		if previous_corruption.get(family, 0) != combat.corruption[family]:
			events.publish(&"corruption_changed", {"family": family, "value": combat.corruption[family], "tier": combat.inattention_tier if family == "Inattention" else 0})
	previous_corruption = combat.corruption.duplicate()

func _enter_graveyard(_action: StringName) -> void:
	if entered: return
	entered = true
	$Entrance.enabled = false
	$Gate/CollisionShape2D.set_deferred("disabled", true)
	manager.state.current_node_id = "scene.cemetery.broken_graveyard"
	hud.place_label.text = "ENGLISH GAME 0.9 · BROKEN GRAVEYARD"
	events.publish(&"scene_entered", {"scene_id": manager.state.current_node_id})
	hud.announce("A Grave Skeleton guards the path. Approach to engage.")

func _physics_process(_delta: float) -> void:
	_update_lock()
	if entered and not encounter_started and not hud.overlay_open and player.global_position.distance_to(skeleton.global_position) <= 165:
		start_encounter()
	if not player.input_locked and Input.is_action_just_pressed("world_interact"):
		interactions.interact()

func _process(delta: float) -> void:
	if not is_instance_valid(camera) or not is_instance_valid(player): return
	var locked: bool = turns.phase not in [TURNS.Phase.EXPLORATION, TURNS.Phase.DEFEAT]
	var target: Vector2 = (player.position + skeleton.position) * 0.5 + Vector2(0, 80) if locked else player.position + Vector2(0, 60)
	camera.position = camera.position.lerp(target, minf(1, delta * 8))

func _update_lock() -> void:
	if not is_instance_valid(hud): return
	var locked: bool = turns.phase != TURNS.Phase.EXPLORATION or hud.overlay_open
	player.set_input_locked(locked)
	interactions.enabled = not locked
	interactions.refresh()

func start_encounter() -> void:
	if encounter_started or not entered: return
	encounter_started = true
	turns.set_phase(TURNS.Phase.COMBAT_ENTER)
	_update_lock()
	player.face_direction(skeleton.global_position - player.global_position)
	for visual in skeleton.get_node("VisualRoot").get_children():
		if visual.has_method("present_motion"): visual.present_motion(Vector2.ZERO, player.global_position - skeleton.global_position)
	var data: Resource = skeleton.get_node("Logic").data
	var node := {"id": "broken_graveyard_skeleton", "title": "GRAVE SKELETON", "type": "encounter", "words": ["REASSEMBLE", "REMAINS", "SCATTER", "ERODE", "TOXIC"], "tags": ["RISK", "COMBAT"], "biome": "cemetery", "primary": ""}
	node.primary = manager.learning.choose_target(node, manager.rng, 0)
	if not str(node.primary).is_empty(): node.tags.append("MAJOR_LEARNING_OPPORTUNITY")
	manager.selected_node = node
	manager.learning.begin(node, 1)
	var snapshot := manager.state.combat_snapshot()
	snapshot.merge({"enemy_profile": data.profile(), "reassembly_rounds": data.reassembly_rounds, "remains_integrity": data.remains_integrity})
	skeleton.get_node("Logic").bind(combat, events)
	combat.enemy_collapsed.connect(func(): rewards.collapsed(skeleton.get_node("Logic")))
	combat.start_battle(7, snapshot)
	manager.state.prepared_armor = 0
	hud.set_combat_active(true)
	events.publish(&"combat_started", {"enemy_id": data.id, "scene_id": "scene.cemetery.broken_graveyard"})
	if is_instance_valid(camera_tween): camera_tween.kill()
	camera_tween = create_tween()
	camera_tween.tween_property(camera, "zoom", Vector2(1.08, 1.08), transition_seconds)
	camera_tween.tween_callback(func():
		if turns.phase == TURNS.Phase.COMBAT_ENTER:
			turns.set_phase(TURNS.Phase.PLAYER_TURN)
			hud.refresh())

func _invoke(uid: int, restore_target: String) -> void:
	if hud.overlay_open: return
	var card: Dictionary = {}
	for candidate in combat.deck.hand:
		if int(candidate.instance_id) == uid: card = candidate; break
	if card.is_empty(): return
	events.publish(&"word_sigil_selected", {"word_id": card.name, "instance_id": uid, "position": player.global_position})
	if card.name == "OBSERVE": events.publish(&"observe_started", {"word_id": "OBSERVE"})
	if turns.invoke(uid, restore_target):
		events.publish(&"word_sigil_invoked", {"word_id": card.name, "instance_id": uid, "position": player.global_position})
		if card.name == "OBSERVE": events.publish(&"observe_resolved", {"clarity": combat.clarity_name()})
		if card in combat.deck.exhaust_pile: events.publish(&"word_sigil_exhausted", {"word_id": card.name, "instance_id": uid})
		hud.refresh()

func _retain(uid: int) -> void:
	if turns.phase != TURNS.Phase.PLAYER_TURN or hud.overlay_open: return
	if combat.deck.toggle_retain(uid, combat.retain_slots()):
		events.publish(&"word_sigil_retained", {"instance_id": uid, "retained": uid in combat.deck.retained_cards})
		hud.refresh()

func _battle_finished(victory: bool) -> void:
	manager.state.capture_combat(combat)
	manager.cemetery_finish_node()
	if not victory:
		manager.state.completed = true
		manager.state.victory = false
		manager.state.extracted = false
		turns.set_phase(TURNS.Phase.DEFEAT)
		events.publish(&"combat_ended", {"victory": false})
		hud.set_combat_active(false)
		hud.show_overlay("RUN ENDED", "The Grave Skeleton claimed this attempt. Your saved knowledge is preserved.", [{"text": "REPLAY BROKEN GRAVEYARD", "callback": restart}])
		return
	encounter_cleared = true
	events.publish(&"enemy_defeated", {"enemy_id": "enemy.grave_skeleton", "position": skeleton.global_position})
	skeleton.get_node("Logic").unresolved = false
	rewards.cleared(skeleton.get_node("LootAnchor").global_position)
	manager.state.apply_post_combat()
	$Exit.enabled = true
	turns.set_phase(TURNS.Phase.COMBAT_END)
	hud.set_combat_active(false)
	if is_instance_valid(camera_tween): camera_tween.kill()
	camera_tween = create_tween()
	camera_tween.tween_property(camera, "zoom", Vector2.ONE, transition_seconds)
	camera_tween.tween_callback(func():
		turns.set_phase(TURNS.Phase.EXPLORATION)
		_update_lock()
		events.publish(&"combat_ended", {"victory": true})
		hud.announce("Remains cleared. Walk to any glint and press E to PICK UP. Pickup is optional." if loot_layer.get_children().any(func(loot): return loot.visible) else "Remains cleared. You can explore freely again.")
		if not manager.learning.save_error.is_empty(): hud.show_overlay("KNOWLEDGE SAVE WARNING", manager.learning.save_error, []))

func _on_event(event_id: StringName, payload: Dictionary) -> void:
	event_trace.append({"event": String(event_id), "payload": payload})
	if event_trace.size() > 160: event_trace.pop_front()
	if event_id == &"echo_spawned": hud.announce("+%d Echo" % int(payload.amount))
	if event_id == &"loot_picked_up": hud.announce("PICKED UP · %s · Added to Run Bag" % payload.name)
	if event_id == &"special_loot_spawned": hud.announce("A worn object glints among the bones. It stays until you pick it up.")

func _unhandled_key_input(event: InputEvent) -> void:
	if not event.is_pressed() or event.is_echo(): return
	if event.is_action_pressed("open_lexicon"):
		if hud.overlay_open: hud.close_overlay()
		else: hud.show_lexicon()
	elif event.is_action_pressed("open_run_bag"):
		if hud.overlay_open: hud.close_overlay()
		else: hud.show_bag()
	elif event is InputEventKey:
		if event.physical_keycode == KEY_SPACE and not hud.overlay_open: turns.end_turn()
		if event.physical_keycode == KEY_R and (encounter_cleared or turns.phase == TURNS.Phase.DEFEAT): restart()
		if event.physical_keycode == KEY_F2 and OS.is_debug_build() and not hud.overlay_open: show_qa()

func show_qa() -> void:
	hud.show_overlay("BROKEN GRAVEYARD QA", "Seed %d\nForce Chisel: %s\nNormal Special Loot chance: 10%%\nRoll history: %s\nChanging mode affects the next fresh run; it never rerolls an existing corpse.\nNo new biome or other 0.9 scenes are included." % [seed_value, str(qa_force_chisel), str(rewards.roller.roll_history)], [{"text": "REPLAY · FORCED CHISEL (ACCEPTANCE)", "callback": func(): get_tree().set_meta("slice_force_drop", true); restart()}, {"text": "REPLAY · NORMAL 10% LOOT", "callback": func(): get_tree().set_meta("slice_force_drop", false); restart()}])

func restart() -> void:
	get_tree().reload_current_scene()
