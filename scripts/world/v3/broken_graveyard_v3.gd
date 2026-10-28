extends Node
## The formal Broken Graveyard on the v3 pixel world (2026-10-25, first grey-box pass).
##
## Visual layer from the validated prototype (scenes/prototypes/graveyard_room): native 960x540
## world in a SubViewport, integer scaling, nearest filtering, ground plate + separate props,
## Y-sort, contact shadows, hero B1 animations, the Lexicon book on Tab.
## Rule layer unchanged from 0.9 (scripts/world/broken_graveyard.gd): RunManager, CombatState,
## turn controller, skeleton logic, reward controller, world loot, gameplay event bus.
## Rooms and exits follow Decision Log D-022 / D-023 (KB: Scene Structure and Transitions).
##
## The skeleton is the real design B (skeleton_b.gd). Grey-box parts: the combat HUD is the 0.9 one
## scaled to the 960x540 screen, exit glyphs and room 2 / area 2 contents are stand-ins.
##
## Keys: WASD move · E interact · Tab Lexicon book · L knowledge list · B run bag ·
## Space end turn · R replay (after the fight) · F fullscreen
## Capture: Godot --path . res://scenes/world/broken_graveyard_v3.tscn -- --capture=<abs dir>

const TURNS := preload("res://scripts/combat/slice_turn_controller.gd")
const EVENTS := preload("res://scripts/systems/gameplay_events.gd")
const INTERACTIONS := preload("res://scripts/world/interaction_system.gd")
const REWARDS := preload("res://scripts/loot/slice_reward_controller.gd")
const SKELETON_LOGIC := preload("res://scripts/combat/skeleton_logic.gd")
const SKELETON_VISUAL := preload("res://scripts/world/v3/skeleton_b.gd")
const ROOM_EXIT := preload("res://scripts/world/v3/room_exit.gd")
const SCREEN_FADE := preload("res://scripts/world/v3/screen_fade.gd")
const LEXICON := preload("res://scripts/prototypes/graveyard_room/lexicon_overlay.gd")
const HUD_SCENE := preload("res://scenes/ui/CombatHUD.tscn")
const HERO_SCENE := preload("res://scenes/player/hero_b1.tscn")
const SKELETON_DATA := preload("res://data/enemies/enemy_grave_skeleton.tres")
const CHISEL := preload("res://data/loot/loot_weathered_chisel.tres")

const NATIVE := Vector2i(960, 540)
const HUD_DESIGN_SIZE := Vector2(1280, 720) # the 0.9 HUD was laid out for this screen
const ENCOUNTER_DISTANCE := 110.0
const SKELETON_KEEPS_AWAY := 56.0 # how close the skeleton walks up to the hero when a fight starts

# Room layouts. Props: [file, origin, collision rect relative to the PNG origin, ellipse?]
const ROOMS := {
	"bg_1": {
		"id": "bg_1", "area": "BROKEN GRAVEYARD", "seed": 11, "start": Vector2(60, 470),
		"props": [
			["dead_tree_01", Vector2(185, 222), Rect2(-52, -48, 104, 46), true],
			["tombstone_upright_01", Vector2(322, 170), Rect2(-32, -15, 44, 15)],
			["tombstone_upright_01", Vector2(578, 92), Rect2(-32, -15, 44, 15)],
			["tombstone_fragment_01", Vector2(645, 124), Rect2(-24, -28, 48, 28)],
			["tombstone_upright_01", Vector2(892, 272), Rect2(-32, -15, 44, 15)],
			["open_grave_01", Vector2(815, 328), Rect2(-40, -64, 96, 64)],
			["tombstone_upright_01", Vector2(82, 444), Rect2(-32, -15, 44, 15)],
			["tombstone_tilted_01", Vector2(205, 492), Rect2(-32, -18, 48, 18)],
		],
		# World Bible: the skeleton stands by an open grave, not in the middle like a spawn point.
		"skeleton": Vector2(742, 338),
		"exits": [
			{"zone": Rect2(836, 0, 104, 26), "side": "top", "kind": "event", "target": "bg_2", "glyph_at": Vector2(888, 40)},
			{"zone": Rect2(934, 130, 26, 100), "side": "right", "kind": "rest", "target": "bg_2", "glyph_at": Vector2(920, 120)},
		],
	},
	"bg_2": {
		"id": "bg_2", "area": "BROKEN GRAVEYARD", "seed": 23,
		"props": [
			["tombstone_upright_01", Vector2(160, 150), Rect2(-32, -15, 44, 15)],
			["tombstone_tilted_01", Vector2(300, 250), Rect2(-32, -18, 48, 18)],
			["dead_tree_01", Vector2(560, 210), Rect2(-52, -48, 104, 46), true],
			["tombstone_fragment_01", Vector2(420, 430), Rect2(-24, -28, 48, 28)],
			["tombstone_upright_01", Vector2(700, 440), Rect2(-32, -15, 44, 15)],
			["tombstone_upright_01", Vector2(760, 120), Rect2(-32, -15, 44, 15)],
		],
		"exits": [
			{"zone": Rect2(934, 250, 26, 110), "side": "right", "kind": "area", "target": "vw_1", "glyph_at": Vector2(920, 240)},
		],
	},
	"vw_1": {
		"id": "vw_1", "area": "VEILED WALK", "seed": 31, "tint": Color(0.56, 0.62, 0.78), "dead_grass": 6,
		"props": [
			["tombstone_fragment_01", Vector2(300, 200), Rect2(-24, -28, 48, 28)],
			["tombstone_tilted_01", Vector2(640, 380), Rect2(-32, -18, 48, 18)],
		],
		"exits": [],
	},
}
const NODE_TITLES := {"event": "EVENT", "rest": "REST", "combat": "COMBAT", "elite": "ELITE"}

@export var seed_value := 9019
@export var qa_force_chisel := true

var manager := RunManager.new()
var combat := CombatState.new()
var room: CemeteryRoom
var room_id := ""
var exits: Array[Node2D] = []
var hero: HeroB1
var skeleton: Node2D
var encounter_started := false
var encounter_cleared := false
var transitioning := false
var event_trace: Array[Dictionary] = []

var _viewport: SubViewport
var _language: CanvasLayer # language layer inside the world viewport: untouched by world tint
var _fade: CanvasLayer
var _lexicon: Control
var events: Node
var turns: Node
var interactions: Node
var rewards: Node
var hud: CanvasLayer


func _ready() -> void:
	_setup_window()
	_install_input()
	_viewport = SubViewport.new()
	_viewport.size = NATIVE
	_viewport.canvas_item_default_texture_filter = Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_NEAREST
	_viewport.snap_2d_transforms_to_pixel = true
	_viewport.snap_2d_vertices_to_pixel = true
	add_child(_viewport)
	_language = CanvasLayer.new()
	_language.layer = 5
	_viewport.add_child(_language)
	_fade = SCREEN_FADE.new()
	_viewport.add_child(_fade)
	var screen := TextureRect.new()
	screen.name = "WorldScreen"
	screen.texture = _viewport.get_texture()
	screen.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	screen.size = Vector2(NATIVE)
	screen.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(screen)

	events = EVENTS.new()
	events.name = "Events"
	add_child(events)
	turns = TURNS.new()
	add_child(turns)
	interactions = INTERACTIONS.new()
	interactions.radius = 40.0 # native pixels: about half the hero's height
	add_child(interactions)
	rewards = REWARDS.new()
	rewards.chisel = CHISEL
	add_child(rewards)

	hero = HERO_SCENE.instantiate()
	_lexicon = LEXICON.new()
	add_child(_lexicon)
	_lexicon.set_process_unhandled_input(false) # Tab is routed here, so it respects combat and transitions
	_lexicon.screen_rect = Rect2(Vector2.ZERO, Vector2(NATIVE))
	_lexicon.pixel = 1 # this scene works in native units; the window scales them
	_lexicon.size = Vector2(NATIVE)
	_lexicon.open_changed.connect(hero.set_book_open)

	hud = HUD_SCENE.instantiate()
	add_child(hud)
	# The 0.9 HUD keeps its 1280x720 layout, shrunk onto the 960x540 screen (grey-box only:
	# the combat presentation is still to be designed). Text stays sharp at any window size.
	hud.scale = Vector2(NATIVE) / HUD_DESIGN_SIZE
	hud.ui_root.set_anchors_preset(Control.PRESET_TOP_LEFT)
	hud.ui_root.size = HUD_DESIGN_SIZE
	hud.combat_panel.offset_top = -300 # keep the upper half of the screen for the two fighters
	# When the words need more room than that, the panel grows upward instead of off the screen.
	hud.combat_panel.grow_vertical = Control.GROW_DIRECTION_BEGIN
	var panel_style := StyleBoxFlat.new()
	panel_style.bg_color = Color(0.03, 0.04, 0.05, 0.62) # the fighters stay visible through it
	for edge in [SIDE_LEFT, SIDE_RIGHT, SIDE_TOP, SIDE_BOTTOM]:
		panel_style.set_content_margin(edge, 12)
	hud.combat_panel.add_theme_stylebox_override("panel", panel_style)
	for node in hud.ui_root.find_children("*", "Label", true, false):
		if (node as Label).text.begins_with("WASD"):
			node.text = "WASD move · E interact · TAB Lexicon book · L word list · B Run Bag · F fullscreen"
	for node in hud.ui_root.find_children("*", "Button", true, false):
		if (node as Button).text == "RUN BAG [TAB]": # Tab opens the Lexicon book in this scene
			node.text = "RUN BAG [B]"

	_bind_rules()
	_load_room("bg_1", "")
	hud.refresh()
	hud.announce("Follow the old path. Something stands by the open grave.")
	if not manager.learning.load_notice.is_empty():
		hud.show_overlay("KNOWLEDGE SAVE WARNING", manager.learning.load_notice, [])
	if "--capture" in str(OS.get_cmdline_user_args()):
		_capture()


func _setup_window() -> void:
	var win := get_window()
	win.content_scale_size = NATIVE
	win.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	win.content_scale_aspect = Window.CONTENT_SCALE_ASPECT_KEEP
	win.content_scale_stretch = Window.CONTENT_SCALE_STRETCH_INTEGER
	if DisplayServer.get_name() == "headless" or win.mode != Window.MODE_WINDOWED:
		return
	# Largest whole multiple of 960x540 that fits the screen (2x on 1080p, 4x on 4K).
	var usable := DisplayServer.screen_get_usable_rect(win.current_screen)
	var k := maxi(1, mini(usable.size.x / NATIVE.x, (usable.size.y - 40) / NATIVE.y))
	win.size = NATIVE * k
	win.position = usable.position + (usable.size - win.size) / 2


func _install_input() -> void:
	preload("res://scripts/systems/slice_input.gd").install()
	# Tab opens the Lexicon book here; the run bag moves to B.
	for event in InputMap.action_get_events("open_run_bag"):
		InputMap.action_erase_event("open_run_bag", event)
	var bag := InputEventKey.new()
	bag.physical_keycode = KEY_B
	InputMap.action_add_event("open_run_bag", bag)


# --- Rule layer wiring (same contracts as the 0.9 slice) ----------------------------------

func _bind_rules() -> void:
	if get_tree().has_meta("slice_seed"):
		seed_value = int(get_tree().get_meta("slice_seed"))
	if bool(get_tree().get_meta("slice_qa_no_save", false)):
		manager.persistence_path = ""
	manager.start_cemetery_run(seed_value)
	manager.state.current_node_id = "scene.cemetery.broken_graveyard"
	turns.bind(combat, events)
	interactions.player = hero
	interactions.target_changed.connect(func(_target, value): hud.prompt.text = value)
	events.occurred.connect(_on_event)
	rewards.qa_force_drop = qa_force_chisel
	hud.bind(manager.state, combat)
	hud.place_label.text = "ENGLISH GAME · BROKEN GRAVEYARD · v3 GREY-BOX"
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
	combat.enemy_action_started.connect(func(action):
		if is_instance_valid(skeleton):
			skeleton.get_node("VisualRoot/Visual").lunge(hero.global_position)
			events.publish(&"enemy_attack_started", {"enemy_id": "enemy.grave_skeleton", "position": skeleton.global_position, "action": action.word, "kind": action.kind}))
	for word in manager.learning.words.values():
		word.changed.connect(_word_changed.bind(word.lemma))


func _word_changed(message: String, lemma: String) -> void:
	events.publish(&"knowledge_stage_changed", {"word_id": lemma, "stage": manager.learning.words[lemma].current_state, "message": message})


func start_encounter() -> void:
	if encounter_started or not is_instance_valid(skeleton):
		return
	encounter_started = true
	turns.set_phase(TURNS.Phase.COMBAT_ENTER)
	_update_lock()
	hero.face_direction(skeleton.global_position - hero.global_position)
	_skeleton_steps_up()
	var node := {"id": "broken_graveyard_skeleton", "title": "GRAVE SKELETON", "type": "encounter", "words": ["REASSEMBLE", "REMAINS", "SCATTER", "ERODE", "TOXIC"], "tags": ["RISK", "COMBAT"], "biome": "cemetery", "primary": ""}
	node.primary = manager.learning.choose_target(node, manager.rng, 0)
	if not str(node.primary).is_empty():
		node.tags.append("MAJOR_LEARNING_OPPORTUNITY")
	manager.selected_node = node
	manager.learning.begin(node, 1)
	var snapshot := manager.state.combat_snapshot()
	snapshot.merge({"enemy_profile": SKELETON_DATA.profile(), "reassembly_rounds": SKELETON_DATA.reassembly_rounds, "remains_integrity": SKELETON_DATA.remains_integrity})
	var logic: Node = skeleton.get_node("Logic")
	logic.bind(combat, events)
	combat.enemy_collapsed.connect(func(): rewards.collapsed(logic))
	combat.start_battle(7, snapshot)
	manager.state.prepared_armor = 0
	hud.set_combat_active(true)
	events.publish(&"combat_started", {"enemy_id": SKELETON_DATA.id, "scene_id": manager.state.current_node_id})
	# The fight starts where they stand: no black screen, no separate battle page (0.9 spec §10).
	get_tree().create_timer(0.4).timeout.connect(func():
		if turns.phase == TURNS.Phase.COMBAT_ENTER:
			turns.set_phase(TURNS.Phase.PLAYER_TURN)
			hud.refresh())


func _invoke(uid: int, restore_target: String) -> void:
	if hud.overlay_open:
		return
	var card: Dictionary = {}
	for candidate in combat.deck.hand:
		if int(candidate.instance_id) == uid:
			card = candidate
			break
	if card.is_empty():
		return
	events.publish(&"word_sigil_selected", {"word_id": card.name, "instance_id": uid, "position": hero.global_position})
	if turns.invoke(uid, restore_target):
		events.publish(&"word_sigil_invoked", {"word_id": card.name, "instance_id": uid, "position": hero.global_position})
		if card in combat.deck.exhaust_pile:
			events.publish(&"word_sigil_exhausted", {"word_id": card.name, "instance_id": uid})
		hud.refresh()


func _retain(uid: int) -> void:
	if turns.phase != TURNS.Phase.PLAYER_TURN or hud.overlay_open:
		return
	if combat.deck.toggle_retain(uid, combat.retain_slots()):
		events.publish(&"word_sigil_retained", {"instance_id": uid, "retained": uid in combat.deck.retained_cards})
		hud.refresh()


func _battle_finished(victory: bool) -> void:
	manager.state.capture_combat(combat)
	manager.cemetery_finish_node()
	hud.set_combat_active(false)
	if not victory:
		manager.state.completed = true
		manager.state.victory = false
		manager.state.extracted = false
		turns.set_phase(TURNS.Phase.DEFEAT)
		events.publish(&"combat_ended", {"victory": false})
		hud.show_overlay("RUN ENDED", "The Grave Skeleton claimed this attempt. Your saved knowledge is preserved.", [{"text": "REPLAY BROKEN GRAVEYARD", "callback": restart}])
		return
	encounter_cleared = true
	events.publish(&"enemy_defeated", {"enemy_id": "enemy.grave_skeleton", "position": skeleton.global_position})
	skeleton.get_node("Logic").unresolved = false
	rewards.cleared(skeleton.get_node("LootAnchor").global_position)
	manager.state.apply_post_combat()
	turns.set_phase(TURNS.Phase.COMBAT_END)
	get_tree().create_timer(0.4).timeout.connect(func():
		turns.set_phase(TURNS.Phase.EXPLORATION)
		_update_lock()
		for exit in exits:
			exit.enabled = true
		events.publish(&"combat_ended", {"victory": true})
		var loot_waiting := room.sorted.get_children().any(func(n): return n.has_method("get_prompt") and n.visible)
		hud.announce("The bones lie still. Pick up what glints [E], then choose an exit." if loot_waiting else "The bones lie still. Choose an exit.")
		if not manager.learning.save_error.is_empty():
			hud.show_overlay("KNOWLEDGE SAVE WARNING", manager.learning.save_error, []))


func _on_event(event_id: StringName, payload: Dictionary) -> void:
	event_trace.append({"event": String(event_id), "payload": payload})
	if event_trace.size() > 160:
		event_trace.pop_front()
	match event_id:
		&"echo_spawned":
			hud.announce("+%d Echo" % int(payload.amount))
		&"loot_picked_up":
			hud.announce("PICKED UP · %s · Added to Run Bag" % payload.name)
		&"special_loot_spawned":
			hud.announce("A worn object glints among the bones. It stays until you pick it up.")
		&"enemy_damaged":
			if is_instance_valid(skeleton):
				skeleton.get_node("VisualRoot/Visual").hit()
		&"enemy_collapsed":
			hud.announce("It falls apart, but the cords still hold. Break the remains before it rises.")
		&"enemy_reassembled":
			hud.announce("The bones pull themselves back together.")


# --- Rooms, exits and transitions (D-022, D-023) --------------------------------------------

func _load_room(id: String, entered_from: String, exit_zone := Rect2()) -> void:
	if is_instance_valid(room):
		room.sorted.remove_child(hero)
		room.queue_free()
	for exit in exits:
		exit.queue_free()
	exits.clear()
	room_id = id
	var layout: Dictionary = ROOMS[id]
	room = CemeteryRoom.new(layout)
	_viewport.add_child(room)
	room.sorted.add_child(hero)
	room.player = hero
	hero.position = _entry_point(layout, entered_from, exit_zone)
	rewards.bind(manager.state, events, hero, room.sorted, interactions)
	skeleton = null
	if layout.has("skeleton"):
		skeleton = _make_skeleton(layout.skeleton)
		room.sorted.add_child(skeleton)
	for data in layout.exits:
		var exit: Node2D = ROOM_EXIT.new()
		exit.setup(data, _language)
		exit.taken.connect(_take_exit)
		room.add_child(exit)
		exit.enabled = not layout.has("skeleton") or encounter_cleared
		exits.append(exit)


## Leaving through one side enters the next room from the opposite side, so the player keeps
## a sense of walking onward although the rooms are not stitched together.
func _entry_point(layout: Dictionary, entered_from: String, zone: Rect2) -> Vector2:
	match entered_from:
		"top": return Vector2(clampf(zone.get_center().x, 60, 900), 520)
		"bottom": return Vector2(clampf(zone.get_center().x, 60, 900), 110)
		"right": return Vector2(28, clampf(zone.get_center().y + 40, 120, 520))
		"left": return Vector2(932, clampf(zone.get_center().y + 40, 120, 520))
	return layout.get("start", Vector2(480, 400))


func _make_skeleton(at: Vector2) -> Node2D:
	var root := Node2D.new()
	root.name = "GraveSkeleton"
	root.position = at
	var logic: Node = SKELETON_LOGIC.new()
	logic.name = "Logic"
	logic.data = SKELETON_DATA
	root.add_child(logic)
	var visual_root := Node2D.new()
	visual_root.name = "VisualRoot"
	root.add_child(visual_root)
	var visual: Node2D = SKELETON_VISUAL.new()
	visual.name = "Visual"
	visual.mover = root
	visual_root.add_child(visual)
	var anchor := Marker2D.new()
	anchor.name = "LootAnchor"
	anchor.position = Vector2(0, 4)
	root.add_child(anchor)
	var body := StaticBody2D.new() # the hero cannot walk through it
	var shape := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(24, 8)
	shape.shape = rect
	shape.position = Vector2(0, -4)
	body.add_child(shape)
	root.add_child(body)
	return root


## When the fight starts the skeleton walks up to meet the hero (whole strides, stopping a
## little short of them), or just turns to face them when they are already close.
func _skeleton_steps_up() -> void:
	var visual: Node2D = skeleton.get_node("VisualRoot/Visual")
	var to := hero.global_position - skeleton.global_position
	var gap := maxf(0.0, (absf(to.x) if absf(to.x) >= absf(to.y) else absf(to.y)) - SKELETON_KEEPS_AWAY)
	if gap >= SkeletonB.STRIDE:
		visual.walk_to(skeleton.position + _axis(to) * minf(gap, 2 * SkeletonB.STRIDE))
	else:
		visual.face(to)


func _axis(v: Vector2) -> Vector2:
	return Vector2(signf(v.x), 0) if absf(v.x) >= absf(v.y) else Vector2(0, signf(v.y))


func _take_exit(exit: Node2D) -> void:
	if transitioning:
		return
	transitioning = true
	_update_lock()
	var next: Dictionary = ROOMS[exit.target]
	var new_area: bool = next.area != ROOMS[room_id].area
	var side: String = exit.side
	var zone: Rect2 = exit.zone
	var kind: String = exit.kind
	if new_area:
		await _fade.cover(_fade.AREA_SECONDS)
		_load_room(exit.target, side, zone)
		await _fade.write_title(next.area)
		await _fade.reveal(_fade.AREA_SECONDS)
		hud.place_label.text = "ENGLISH GAME · %s · v3 GREY-BOX" % next.area
		hud.announce("The grey-box ends here. Press R to walk it again.")
	else:
		await _fade.cover(_fade.ROOM_SECONDS)
		_load_room(exit.target, side, zone)
		await _fade.reveal(_fade.ROOM_SECONDS)
		hud.announce("%s · placeholder room. Walk on through the exit to the east." % NODE_TITLES.get(kind, kind.to_upper()))
	transitioning = false
	_update_lock()


# --- Per-frame -------------------------------------------------------------------------

func _physics_process(_delta: float) -> void:
	_update_lock()
	if is_instance_valid(skeleton) and not encounter_started and not hud.overlay_open and not transitioning \
			and hero.global_position.distance_to(skeleton.global_position) <= ENCOUNTER_DISTANCE:
		start_encounter()
	if not transitioning and turns.phase == TURNS.Phase.EXPLORATION:
		for exit in exits:
			exit.check(hero)
	if not hero.input_locked and Input.is_action_just_pressed("world_interact"):
		interactions.interact()


func _update_lock() -> void:
	var locked: bool = turns.phase != TURNS.Phase.EXPLORATION or hud.overlay_open or transitioning
	hero.set_input_locked(locked)
	interactions.enabled = not locked and hero.book_phase == ""
	interactions.refresh()


func _unhandled_key_input(event: InputEvent) -> void:
	if not event.is_pressed() or event.is_echo():
		return
	var key: Key = event.physical_keycode
	if key == KEY_TAB or (key == KEY_ESCAPE and _lexicon.is_open):
		# The book opens only while exploring; it can always be closed.
		if _lexicon.is_open or (turns.phase == TURNS.Phase.EXPLORATION and not transitioning and not hud.overlay_open and hero.book_phase == ""):
			_lexicon.toggle()
	elif event.is_action_pressed("open_lexicon"):
		if hud.overlay_open: hud.close_overlay()
		else: hud.show_lexicon()
	elif event.is_action_pressed("open_run_bag"):
		if hud.overlay_open: hud.close_overlay()
		else: hud.show_bag()
	elif key == KEY_SPACE and not hud.overlay_open:
		turns.end_turn()
	elif key == KEY_R and (encounter_cleared or turns.phase == TURNS.Phase.DEFEAT):
		restart()
	elif key == KEY_F:
		var win := get_window()
		win.mode = Window.MODE_WINDOWED if win.mode == Window.MODE_FULLSCREEN else Window.MODE_FULLSCREEN


func restart() -> void:
	get_tree().reload_current_scene()


# --- Capture mode: scripted walk-through with screenshots ------------------------------------

func _capture() -> void:
	var dir := str(OS.get_cmdline_user_args()[0]).get_slice("=", 1)
	DirAccess.make_dir_recursive_absolute(dir)
	await _frames(20)
	await _shot(dir + "/01_room.png")
	hero.position = skeleton.position + Vector2(-100, 30)
	await _frames(30)
	await _shot(dir + "/02_combat.png")
	# Play: keep the opening hand, use every affordable word, take hits, until it ends.
	var collapsed_shot := false
	for i in 400:
		if combat.finished:
			break
		if combat.bone_remains and not collapsed_shot:
			collapsed_shot = true
			await _frames(10)
			await _shot(dir + "/03_remains.png")
		if turns.phase == TURNS.Phase.PLAYER_TURN:
			if combat.deck.mulligan_pending:
				combat.finish_mulligan([])
			else:
				var played := false
				for card in combat.deck.hand.duplicate():
					if combat.card_cost(card) <= combat.focus and turns.invoke(int(card.instance_id), "hp"):
						played = true
						break
				if not played:
					turns.end_turn()
		elif turns.phase == TURNS.Phase.ENEMY_TURN and combat.turn_ending:
			turns.react(false)
		hud.refresh()
		await _frames(2)
	await _frames(60)
	await _shot(dir + "/04_after.png")
	print("CAPTURE result finished=%s cleared=%s hp=%s" % [combat.finished, encounter_cleared, combat.hp])
	if encounter_cleared:
		hero.position = Vector2(888, 30)
		await _frames(4)
		hero.position = Vector2(888, 12)
		await _frames(6)
		await _shot(dir + "/05_room_fade.png")
		await get_tree().create_timer(0.8).timeout
		await _shot(dir + "/06_room2.png")
		hero.position = Vector2(945, 300)
		await get_tree().create_timer(1.2).timeout
		await _shot(dir + "/07_area_title.png")
		await get_tree().create_timer(2.5).timeout
		await _shot(dir + "/08_area2.png")
	get_tree().quit()


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func _shot(path: String) -> void:
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(path)
