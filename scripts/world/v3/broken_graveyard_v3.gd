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
## The skeleton is the real design B (skeleton_b.gd). The fight is shown by combat_view.gd (first pass
## of the KB combat presentation, 2026-10-28): stand-off across the room, mist instead of zoom, thin
## word bar, intent over the enemy. The 0.9 HUD stays only for messages, prompts and the Lexicon /
## bag pages. Grey-box parts: exit glyphs and room 2 / area 2 contents are stand-ins.
##
## Keys: WASD move · E interact · Tab Lexicon book · L knowledge list · B run bag ·
## Space end turn · R replay (after the fight) · F fullscreen · dev: - (F5) back to the five
## starting words, = (F6) every ability word (D-075)
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
const EVENT_SPOT := preload("res://scripts/world/v3/event_spot.gd")
const HUD_SCENE := preload("res://scenes/ui/CombatHUD.tscn")
const HERO_SCENE := preload("res://scenes/player/hero_b1.tscn")
const SKELETON_DATA := preload("res://data/enemies/enemy_grave_skeleton.tres")
const CHISEL := preload("res://data/loot/loot_weathered_chisel.tres")

const NATIVE := Vector2i(960, 540)
const HUD_DESIGN_SIZE := Vector2(1280, 720) # the 0.9 HUD was laid out for this screen
const ENCOUNTER_DISTANCE := 110.0
const STAND_OFF := 120.0 # how far apart, side to side, the two stand in a fight (about three strides)

# Room layouts. Props: [file, origin, collision rect relative to the PNG origin, ellipse?]
## Veiled Walk base ground (art group, D-084): wetter, darker, colder than the outer graveyard's
## mud, so these rooms no longer need a blue tint over the old placeholder plate.
const VEILED_GROUND := ["res://art/cemetery_v3/ground/base/veiled_base_01.png", "res://art/cemetery_v3/ground/base/veiled_base_02.png"]
const ROOMS := {
	# The first word route (D-078, docs/FIRST_WORD_ROUTE_SHATTER.md), fixed until the user says to
	# connect the random route: a broken stone (seen) → the broken wing (recognised) → a fight where
	# the word is lent once (understood) → the cracked slab (used) → a fight with it in hand.
	"bg_1": {
		"id": "bg_1", "area": "BROKEN GRAVEYARD", "seed": 11, "start": Vector2(60, 470),
		"props": [
			["dead_tree_01", Vector2(185, 222), Rect2(-52, -48, 104, 46), true],
			["tombstone_upright_01", Vector2(322, 170), Rect2(-32, -15, 44, 15)],
			["tombstone_upright_01", Vector2(578, 92), Rect2(-32, -15, 44, 15)],
			["tombstone_fragment_01", Vector2(645, 124), Rect2(-24, -28, 48, 28)],
			# A cross broken in two, beside the stepping stones: the first thing in the run that carries a word.
			["tombstone_cross_01_broken", Vector2(430, 300), null],
			["tombstone_upright_01", Vector2(892, 272), Rect2(-32, -15, 44, 15)],
			["open_grave_01", Vector2(815, 328), Rect2(-40, -64, 96, 64)],
			["tombstone_upright_01", Vector2(82, 444), Rect2(-32, -15, 44, 15)],
			["tombstone_tilted_01", Vector2(205, 492), Rect2(-32, -18, 48, 18)],
		],
		# Words over things: near = where the player has to come, at = where the word hangs.
		"words": [{"lemma": "shatter", "near": Vector2(430, 310), "at": Vector2(430, 186)}],
		# World Bible: the skeleton stands by an open grave, not in the middle like a spawn point.
		"skeleton": Vector2(742, 338),
		"dormant": true, # D-079: it lies as bones by its grave until you come near
		"exits": [
			{"zone": Rect2(836, 0, 104, 26), "side": "top", "kind": "event", "target": "bg_2", "glyph_at": Vector2(888, 40)},
		],
	},
	"bg_2": {
		"id": "bg_2", "area": "BROKEN GRAVEYARD", "seed": 23,
		"props": [
			["fountain_broken_wing_01", Vector2(480, 300), null], # the angel whose wing was shattered (character group, 2026-10-30)
			["tombstone_upright_01", Vector2(160, 150), Rect2(-32, -15, 44, 15)],
			["tombstone_tilted_01", Vector2(250, 330), Rect2(-32, -18, 48, 18)],
			["tombstone_fragment_01", Vector2(700, 440), Rect2(-24, -28, 48, 28)],
			["tombstone_upright_01", Vector2(780, 140), Rect2(-32, -15, 44, 15)],
		],
		"words": [{"lemma": "shatter", "near": Vector2(480, 330), "at": Vector2(480, 104)}],
		"event": {"card": "res://data/events/cemetery/broken_wing.json", "at": Vector2(480, 322), "mark": Vector2(480, 90)},
		"hello": "A stone angel kneels by a dry fountain. Go and look [E].",
		"exits": [
			{"zone": Rect2(934, 250, 26, 110), "side": "right", "kind": "combat", "target": "bg_3", "glyph_at": Vector2(920, 240)},
		],
	},
	"bg_3": {
		"id": "bg_3", "area": "BROKEN GRAVEYARD", "seed": 29,
		"props": [
			["tombstone_upright_01", Vector2(200, 160), Rect2(-32, -15, 44, 15)],
			["dead_tree_01", Vector2(560, 170), Rect2(-52, -48, 104, 46), true],
			["tombstone_tilted_01", Vector2(320, 450), Rect2(-32, -18, 48, 18)],
			["open_grave_01", Vector2(760, 330), Rect2(-40, -64, 96, 64)],
			["tombstone_upright_01", Vector2(860, 470), Rect2(-32, -15, 44, 15)],
		],
		"skeleton": Vector2(690, 340),
		"hello": "Another one waits by its grave.",
		"exits": [
			{"zone": Rect2(934, 250, 26, 110), "side": "right", "kind": "event", "target": "vw_1", "glyph_at": Vector2(920, 240)},
		],
	},
	"vw_1": {
		"id": "vw_1", "area": "VEILED WALK", "seed": 31, "ground_tiles": VEILED_GROUND, "dead_grass": 6,
		"props": [
			["grave_slab_01", Vector2(480, 300), null],
			["tombstone_fragment_01", Vector2(260, 200), Rect2(-24, -28, 48, 28)],
			["tombstone_tilted_01", Vector2(700, 420), Rect2(-32, -18, 48, 18)],
			["tombstone_upright_01", Vector2(760, 170), Rect2(-32, -15, 44, 15)],
		],
		"words": [{"lemma": "shatter", "near": Vector2(480, 312), "at": Vector2(480, 214)}],
		"event": {"card": "res://data/events/cemetery/cracked_slab.json", "at": Vector2(480, 312), "mark": Vector2(480, 190)},
		"hello": "Something taps under a cracked slab [E].",
		"exits": [
			{"zone": Rect2(934, 250, 26, 110), "side": "right", "kind": "combat", "target": "vw_2", "glyph_at": Vector2(920, 240)},
		],
	},
	"vw_2": {
		"id": "vw_2", "area": "VEILED WALK", "seed": 37, "ground_tiles": VEILED_GROUND, "dead_grass": 6,
		"props": [
			["tombstone_upright_01", Vector2(240, 180), Rect2(-32, -15, 44, 15)],
			["open_grave_01", Vector2(760, 330), Rect2(-40, -64, 96, 64)],
			["tombstone_fragment_01", Vector2(380, 440), Rect2(-24, -28, 48, 28)],
		],
		"skeleton": Vector2(690, 340),
		"dormant": true,
		"hello": "The last one on this walk. Use what you have learned.",
		"exits": [],
	},
}
const NODE_TITLES := {"event": "EVENT", "rest": "REST", "combat": "COMBAT", "elite": "ELITE",
	"mystery": "MYSTERY", "relic": "RELIC", "final": "FINAL"}

@export var seed_value := 9019
@export var qa_force_chisel := true

var manager := RunManager.new()
var progress := preload("res://scripts/run/lexicon_progress.gd").new() # which ability words this player can use (D-075)
var combat := CombatState.new()
var room: CemeteryRoom
var room_id := ""
var exits: Array[Node2D] = []
var hero: HeroB1
var skeleton: Node2D
var encounter_started := false # in this room
var encounter_cleared := false # this room's fight is won
var cleared_rooms := {} # room id -> true once its fight is won
var words: WordWorld # words met in the world: floating words, event boxes, notes (D-078)
var _logic: Node # the skeleton logic of the fight in progress
var transitioning := false
# Words that just became USABLE wait here for their ceremony. The hero stands still meanwhile, and
# the ceremony plays once nothing else is going on: never dropped (user 2026-10-30: walking on
# after the slab, the book never opened).
var _rites: Array[String] = []
var _rite_wait := 0.0
const RITE_PAUSE := 0.8 # seconds the hero stands still before the book opens
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
var view: CombatView
var _hud_header: Array[Control] = [] # the 0.9 grey-box title block, hidden while fighting


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
	words = WordWorld.new()
	add_child(words)
	words.hero = hero
	words.advanced.connect(_word_advanced)
	_lexicon.open_changed.connect(func(open): words.visible = not open) # the book covers the world, words too

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

	view = CombatView.new()
	add_child(view)
	view.setup(_viewport, _language, screen, combat)
	view.invoke_requested.connect(_invoke)
	view.retain_requested.connect(_retain)
	view.end_turn_requested.connect(func():
		if not hud.overlay_open: turns.end_turn())
	view.mulligan_confirmed.connect(func(ids):
		if turns.phase == TURNS.Phase.PLAYER_TURN: combat.finish_mulligan(ids))
	view.reaction_answered.connect(func(value):
		if not hud.overlay_open: turns.react(value))
	_hud_header = [hud.ui_root.get_child(0), hud.ui_root.get_child(1)]

	_bind_rules()
	_load_room("bg_1", "")
	hud.refresh()
	hud.announce("Follow the old path. Bones lie by the open grave.")
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
	if bool(get_tree().get_meta("slice_qa_no_save", false)) or _capturing():
		manager.persistence_path = ""
		progress.save_path = ""
	progress.load_or_start()
	words.progress = progress
	_lexicon.progress = progress # a word's page shows the sentences it was met in
	_lexicon.set_progress(progress.known_words())
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
			var visual: SkeletonB = skeleton.get_node("VisualRoot/Visual")
			var hit_in := visual.attack(hero.global_position) if str(action.kind) == "physical" else 0.0
			if hit_in > 0.0:
				view.enemy_attack(hit_in, 1.05)
			elif str(action.kind) == "physical":
				visual.lunge(hero.global_position)
			else:
				visual.shed(hero.global_position)
			events.publish(&"enemy_attack_started", {"enemy_id": "enemy.grave_skeleton", "position": skeleton.global_position, "action": action.word, "kind": action.kind}))
	combat.enemy_collapsed.connect(func():
		rewards.collapsed(_logic)
		_lend_word())
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
	if ROOMS[room_id].get("dormant", false): # the heap rises first, then the fight begins
		hero.face_direction(Vector2(signf(skeleton.position.x - hero.position.x), 0))
		hud.announce("The bones are moving.")
		await get_tree().create_timer(skeleton.get_node("VisualRoot/Visual").rise() + 0.2).timeout
	_stand_off()
	var node := {"id": "broken_graveyard_skeleton", "title": "GRAVE SKELETON", "type": "encounter", "words": ["REASSEMBLE", "REMAINS", "SCATTER", "ERODE", "TOXIC"], "tags": ["RISK", "COMBAT"], "biome": "cemetery", "primary": ""}
	node.primary = manager.learning.choose_target(node, manager.rng, 0)
	if not str(node.primary).is_empty():
		node.tags.append("MAJOR_LEARNING_OPPORTUNITY")
	manager.selected_node = node
	manager.learning.begin(node, 1)
	var snapshot := manager.state.combat_snapshot()
	snapshot.merge({"enemy_profile": SKELETON_DATA.profile(), "reassembly_rounds": SKELETON_DATA.reassembly_rounds, "remains_integrity": SKELETON_DATA.remains_integrity})
	snapshot.deck_cards = progress.deck_cards(manager.learning) # only the words this player can use
	_logic = skeleton.get_node("Logic")
	# The new fight first, then the skeleton reads it: bound first, it read the last fight's end
	# ("cleared") and fell to pieces before rising again.
	combat.start_battle(7, snapshot)
	_logic.bind(combat, events)
	manager.state.prepared_armor = 0
	hud.set_combat_active(true)
	hud.combat_panel.hide() # the fight is shown by the combat view
	for part in _hud_header:
		part.hide()
	view.open(hero, skeleton, SKELETON_DATA.display_name)
	words.note_y = 132.0
	words.holding = true # learning moments wait for the fight to end
	events.publish(&"combat_started", {"enemy_id": SKELETON_DATA.id, "scene_id": manager.state.current_node_id})
	# The fight starts where they stand: no black screen, no separate battle page (0.9 spec §10).
	get_tree().create_timer(0.4).timeout.connect(func():
		if turns.phase == TURNS.Phase.COMBAT_ENTER:
			turns.set_phase(TURNS.Phase.PLAYER_TURN)
			hud.refresh())


func _invoke(uid: int, restore_target: String) -> bool:
	if hud.overlay_open or view.busy:
		return false
	var card: Dictionary = {}
	for candidate in combat.deck.hand:
		if int(candidate.instance_id) == uid:
			card = candidate
			break
	if card.is_empty():
		return false
	events.publish(&"word_sigil_selected", {"word_id": card.name, "instance_id": uid, "position": hero.global_position})
	var before := view.hold_enemy(uid) # the rules resolve now; the skeleton reacts when the word lands
	var on_remains := combat.bone_remains
	if turns.invoke(uid, restore_target):
		if bool(card.get("borrowed", false)):
			# Using the lent word where it matters is the proof (D-078 step 3): context evidence.
			if on_remains:
				var lemma := str(card.card_id).to_lower()
				var past := str(WordWorld.WORDS.dictionary(lemma).get("forms", {}).get("past", lemma))
				words.evidence(lemma, "context", "fight:" + room_id, "The fallen bones [%s] at your word." % past,
					"A skeleton fight · " + str(ROOMS[room_id].area).capitalize())
			else:
				hud.announce("It works, a little. A word like this is meant for what has already fallen apart.")
		events.publish(&"word_sigil_invoked", {"word_id": card.name, "instance_id": uid, "position": hero.global_position})
		if card in combat.deck.exhaust_pile:
			events.publish(&"word_sigil_exhausted", {"word_id": card.name, "instance_id": uid})
		view.play_cast(card, before)
		hud.refresh()
		return true
	view.release_enemy()
	return false


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
	get_tree().create_timer(0.9).timeout.connect(func(): # let the last word land first
		view.close()
		words.note_y = 400.0
		get_tree().create_timer(0.6).timeout.connect(func(): words.holding = false) # once the bar has faded
		for part in _hud_header:
			part.show())
	if not victory:
		manager.state.completed = true
		manager.state.victory = false
		manager.state.extracted = false
		turns.set_phase(TURNS.Phase.DEFEAT)
		events.publish(&"combat_ended", {"victory": false})
		hud.show_overlay("RUN ENDED", "The Grave Skeleton claimed this attempt. Your saved knowledge is preserved.", [{"text": "REPLAY BROKEN GRAVEYARD", "callback": restart}])
		return
	encounter_cleared = true
	cleared_rooms[room_id] = true
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
		if exits.is_empty():
			hud.announce("The bones lie still. The grey-box route ends here: press R to walk it again (the - key forgets the words learned on the way).")
		else:
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
			if is_instance_valid(skeleton): # once it stands it turns to the hero again
				skeleton.get_node("VisualRoot/Visual").stand_off(skeleton.position.x, hero.position)


# --- Words learned in the world (D-078) ------------------------------------------------------

## A word half known is lent for one use in a fight (step 3 of a word route): when the bones fall,
## a RECOGNIZED ability word that fits the moment appears in the hand, drawn in pencil.
func _lend_word() -> void:
	var lemma := "shatter" # the first route; later the route data names its word and its moment
	if progress.stage(lemma) != "RECOGNIZED" or not CombatContent.SKILLS.has(lemma.to_upper()):
		return
	if combat.deck.hand.any(func(c): return bool(c.get("borrowed", false))):
		return
	var card := combat.deck.make_card(lemma.to_upper())
	card["time_properties"].append("EXHAUST")
	card["temporary"] = true
	card["exhaust_on_use"] = true
	card["borrowed"] = true
	combat.deck.hand.append(card)
	words.note("A half-known word comes to you  ·  %s" % lemma.to_upper(), WordWorld.PENCIL)
	hud.announce("SHATTER is in your hand, in pencil: lent for one use. The remains are what it is for.")
	view.refresh()


func _open_event(spot: Node2D) -> void:
	var card: Dictionary = spot.card
	var lemma := str(card.get("word", ""))
	var options: Array = []
	if str(card.get("options_from", "")) == "usable_words":
		# Production: the answers are the player's own words, plus the word in question once it is
		# understood (not yet in their hand, but they know it well enough to try it).
		var own: Array = progress.usable_abilities(manager.learning)
		if progress.stage(lemma) == "UNDERSTOOD" and lemma not in own:
			own.append(lemma)
		var replies: Dictionary = card.get("replies", {})
		for word in own:
			var reply = replies.get(word, replies.get("_default", ""))
			var correct: bool = reply is Dictionary and bool(reply.get("correct", false))
			options.append({"label": str(word).to_upper(), "reply": str(reply.text) if reply is Dictionary else str(reply), "correct": correct,
				"understood": progress.stage(word) == "UNDERSTOOD"}) # known, not yet in hand: drawn in ink
	else:
		options = card.get("options", [])
	words.open_event(card, options, func(result: Dictionary):
		_update_lock()
		if result.is_empty():
			return
		if bool(result.correct):
			spot.solved = true
			interactions.refresh()
			var line := ""
			for text in card.get("text", []): # the line that carries the word, in [brackets]
				if "[" in str(text):
					line = str(text)
			words.evidence(lemma, str(card.evidence), "event:" + str(card.id), line,
				str(card.get("title", "")).capitalize() + " · " + str(ROOMS[room_id].area).capitalize())
			if card.has("breaks"):
				_break_prop(str(card.breaks), spot.position)
				words.remove_near(spot.position)
			hud.announce(str(card.get("done", ""))))
	_update_lock()


## The thing an event was about gives way (the slab shatters): it fades, rubble is left.
func _break_prop(file: String, at: Vector2) -> void:
	for node in room.sorted.get_children():
		if node is CemeteryProp and str(node.scene_file_path).get_file().get_basename() == file and node.position.distance_to(at) < 60:
			var rubble: Node2D = load(CemeteryRoom.PROP_SCENES + "rubble_pile_01.tscn").instantiate()
			rubble.position = node.position
			rubble.modulate.a = 0.0
			room.sorted.add_child(rubble)
			var tween := create_tween().set_parallel()
			tween.tween_property(node, "modulate:a", 0.0, 0.5)
			tween.tween_property(rubble, "modulate:a", 1.0, 0.5).set_delay(0.2)
			tween.chain().tween_callback(node.queue_free)
			return


func _word_advanced(lemma: String, stage: String) -> void:
	_lexicon.set_progress(progress.known_words())
	events.publish(&"knowledge_stage_changed", {"word_id": lemma, "stage": stage, "message": "world"})
	if stage == "USABLE":
		# Only for a new ability: the book opens by itself at its page and the word lights up,
		# letter by letter, then leaves the book as a card (D-078 §5; D-081). Any key skips.
		_rites.append(lemma)
		_rite_wait = RITE_PAUSE


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
	if id.begins_with("vw_"): # trying a ground for the Veiled Walk: -- --vw_plate=<png> --vw_tint=r,g,b
		layout = layout.duplicate()
		for arg in OS.get_cmdline_user_args():
			if str(arg).begins_with("--vw_plate="):
				layout.plate_file = str(arg).get_slice("=", 1)
			elif str(arg).begins_with("--vw_tint="):
				var rgb := str(arg).get_slice("=", 1).split(",")
				layout.tint = Color(float(rgb[0]), float(rgb[1]), float(rgb[2]))
	room = CemeteryRoom.new(layout)
	_viewport.add_child(room)
	room.sorted.add_child(hero)
	room.player = hero
	hero.position = _entry_point(layout, entered_from, exit_zone)
	rewards.bind(manager.state, events, hero, room.sorted, interactions)
	encounter_started = false
	encounter_cleared = cleared_rooms.has(id)
	words.set_room_words(layout.get("words", []))
	if layout.has("event"):
		var spot: Node2D = EVENT_SPOT.new()
		spot.setup(layout.event.card, layout.event.at)
		spot.show_mark(layout.event.get("mark", layout.event.at + Vector2(0, -120)), _language, hero)
		spot.opened.connect(_open_event)
		room.add_child(spot)
		interactions.register(spot)
	skeleton = null
	if layout.has("skeleton"):
		skeleton = _make_skeleton(layout.skeleton)
		room.sorted.add_child(skeleton)
		if not encounter_cleared and layout.get("dormant", false):
			skeleton.get_node("VisualRoot/Visual").lie_dormant() # a heap of bones until you come near (D-079)
		elif not encounter_cleared:
			var home: Vector2 = layout.skeleton
			# It paces a small loop beside its grave (left of and below it, clear of the stones).
			skeleton.get_node("VisualRoot/Visual").wander([home, home + Vector2(-80, 0), home + Vector2(-80, 40), home + Vector2(0, 40)] as Array[Vector2])
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


## When the fight starts the skeleton stops pacing and walks sideways (whole strides) until it
## stands across from the hero, about three strides to the side, at whatever height it already is:
## a diagonal stand-off in the room, never one above the other, so fights need only the left and
## right animations (KB Combat Presentation §1). The hero turns to face it.
func _stand_off() -> void:
	var visual: SkeletonB = skeleton.get_node("VisualRoot/Visual")
	visual.stop_wander()
	var side := signf(skeleton.position.x - hero.position.x)
	if side == 0.0:
		side = 1.0 if hero.position.x < NATIVE.x / 2.0 else -1.0
	var x := hero.position.x + side * STAND_OFF
	if x < 40.0 or x > NATIVE.x - 40.0: # no room on that side: go round to the other
		x = hero.position.x - side * STAND_OFF
	visual.stand_off(x, hero.position)
	hero.face_direction(Vector2(signf(x - hero.position.x), 0))


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
	else:
		await _fade.cover(_fade.ROOM_SECONDS)
		_load_room(exit.target, side, zone)
		await _fade.reveal(_fade.ROOM_SECONDS)
	hud.announce(str(next.get("hello", "%s · walk on." % NODE_TITLES.get(kind, kind.to_upper()))))
	transitioning = false
	_update_lock()


# --- Per-frame -------------------------------------------------------------------------

func _physics_process(delta: float) -> void:
	if not _rites.is_empty():
		_rite_wait -= delta
		if _rite_wait <= 0.0 and turns.phase == TURNS.Phase.EXPLORATION and not transitioning and not hud.overlay_open \
				and not words.is_busy() and not _lexicon.is_open and hero.book_phase == "":
			_lexicon.ceremony(_rites.pop_front(), progress.ceremonies_seen > 0)
			progress.ceremonies_seen += 1
			progress.save()
			_rite_wait = RITE_PAUSE
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
	var locked: bool = turns.phase != TURNS.Phase.EXPLORATION or hud.overlay_open or transitioning or words.is_busy() or not _rites.is_empty()
	hero.set_input_locked(locked)
	interactions.enabled = not locked and hero.book_phase == ""
	interactions.refresh()


func _unhandled_key_input(event: InputEvent) -> void:
	if not event.is_pressed() or event.is_echo():
		return
	var key: Key = event.physical_keycode
	if _lexicon.in_ceremony(): # keys do nothing: only holding Space / Esc skips it (the book polls)
		get_viewport().set_input_as_handled()
	elif key == KEY_TAB or (key == KEY_ESCAPE and _lexicon.is_open):
		# The book opens only while exploring; it can always be closed.
		if _lexicon.is_open or (turns.phase == TURNS.Phase.EXPLORATION and not transitioning and not hud.overlay_open and not words.is_busy() and hero.book_phase == ""):
			_lexicon.toggle()
	elif _lexicon.is_open: # the book's own keys: W / S choose, A / D turn a page, 1 / 2 / 3 pace
		_lexicon._unhandled_input(event)
	elif event.is_action_pressed("open_lexicon"):
		if hud.overlay_open: hud.close_overlay()
		else: hud.show_lexicon()
	elif event.is_action_pressed("open_run_bag"):
		if hud.overlay_open: hud.close_overlay()
		else: hud.show_bag()
	elif key == KEY_SPACE and not hud.overlay_open and not view.busy:
		turns.end_turn()
	elif key == KEY_R and ((encounter_cleared and exits.is_empty()) or turns.phase == TURNS.Phase.DEFEAT):
		restart()
	elif key in [KEY_F5, KEY_F6, KEY_MINUS, KEY_EQUAL] and turns.phase == TURNS.Phase.EXPLORATION: # dev: - (or F5) back to the five starting words, = (or F6) every ability word; on a Mac F5 is dictation
		if key in [KEY_F5, KEY_MINUS]: progress.reset_to_start()
		else: progress.learn_all_abilities()
		_lexicon.set_progress(progress.known_words())
		hud.prompt.text = "Words you can use: " + ", ".join(progress.usable_abilities(manager.learning)).to_upper()
	elif key == KEY_F:
		var win := get_window()
		win.mode = Window.MODE_WINDOWED if win.mode == Window.MODE_FULLSCREEN else Window.MODE_FULLSCREEN


func restart() -> void:
	get_tree().reload_current_scene()


# --- Capture mode: scripted walk-through with screenshots ------------------------------------

func _capturing() -> bool:
	return Array(OS.get_cmdline_user_args()).any(func(arg): return str(arg).begins_with("--capture="))


func _capture() -> void:
	var dir := ""
	for arg in OS.get_cmdline_user_args():
		if str(arg).begins_with("--capture="):
			dir = str(arg).get_slice("=", 1)
	DirAccess.make_dir_recursive_absolute(dir)
	await _frames(20)
	if "--route" in OS.get_cmdline_user_args(): # the SHATTER word route, one picture per step (D-078)
		await _capture_route(dir)
		get_tree().quit()
		return
	if "--sky" in OS.get_cmdline_user_args(): # the Lexicon sky, one picture per level (D-088)
		await _capture_sky(dir)
		get_tree().quit()
		return
	if "--look" in OS.get_cmdline_user_args(): # the rooms as they stand, no fights (art checks)
		for id in ["bg_2", "vw_1", "vw_2"]:
			cleared_rooms[id] = true
			_load_room(id, "")
			hero.position = Vector2(560, 400)
			await get_tree().create_timer(1.2).timeout
			await _shot(dir + "/look_%s.png" % id)
		get_tree().quit()
		return
	if "--lexicon" in OS.get_cmdline_user_args(): # the book opening and closing, frame by frame (D-068)
		_lexicon.toggle()
		for i in 24:
			await _shot(dir + "/lex_open_%02d.png" % i)
			await get_tree().create_timer(0.1).timeout
		for i in 10: # the constellation drawing itself
			await _shot(dir + "/lex_sky_%02d.png" % i)
			await get_tree().create_timer(0.18).timeout
		_lexicon.turn_page(true) # a page turn forward, then back
		for i in 12:
			await _shot(dir + "/lex_turn_%02d.png" % i)
			await get_tree().create_timer(0.07).timeout
		await get_tree().create_timer(0.3).timeout
		_lexicon.turn_page(false)
		for i in 12:
			await _shot(dir + "/lex_back_%02d.png" % i)
			await get_tree().create_timer(0.07).timeout
		await get_tree().create_timer(0.3).timeout
		_lexicon.toggle()
		for i in 20:
			await _shot(dir + "/lex_close_%02d.png" % i)
			await get_tree().create_timer(0.1).timeout
		get_tree().quit()
		return
	await _shot(dir + "/01_room.png")
	# --mirror: meet it from the right (it then swings to the right; until both sides are delivered).
	hero.position = skeleton.position + (Vector2(100, 30) if "--mirror" in OS.get_cmdline_user_args() else Vector2(-100, 30))
	await get_tree().create_timer(2.6).timeout # the skeleton steps across, the mist and bar come in
	await _shot(dir + "/02_combat.png")
	# Play: keep the opening hand, use every affordable word, take hits, until it ends.
	var collapsed_shot := false
	var cast_shots := 0
	var attack_shot := false
	var dust_shot := false
	for i in 20000: # a five-word deck makes for longer fights (D-075)
		if combat.finished:
			break
		if combat.bone_remains and not collapsed_shot:
			collapsed_shot = true
			await get_tree().create_timer(1.6).timeout
			await _shot(dir + "/03_remains.png")
		if turns.phase == TURNS.Phase.PLAYER_TURN and not view.busy:
			if combat.deck.mulligan_pending:
				combat.finish_mulligan([])
			else:
				var played := false
				var order := combat.deck.hand.duplicate() # attacks first, so a small deck still finishes the fight
				order.sort_custom(func(a, b): return int(str(a.name) in ["SHATTER", "STRIKE"]) > int(str(b.name) in ["SHATTER", "STRIKE"]))
				for card in order:
					if combat.card_cost(card) <= combat.focus and combat.disabled_reason(str(card.name), int(card.instance_id)).is_empty():
						if cast_shots < 3: # the word, its hover preview, it leaving the bar, then its shape on the way
							view.forced_hover = int(card.instance_id)
							view._show_word_tip(card, view._words.get_child(combat.deck.hand.find(card)))
							await get_tree().create_timer(0.5).timeout
							await _shot(dir + "/02%s_preview_%s.png" % ["abc"[cast_shots], str(card.name).to_lower()])
							if cast_shots == 0: # the same moment in the cold palette, to compare
								view.set_palette("cold")
								view._show_word_tip(card, view._words.get_child(combat.deck.hand.find(card)))
								await get_tree().create_timer(0.2).timeout
								await _shot(dir + "/02a_preview_cold.png")
								view.set_palette("warm")
							view._hide_tip()
							view.forced_hover = -1
						if _invoke(int(card.instance_id), "hp"):
							played = true
							if cast_shots < 3:
								await get_tree().create_timer(0.3).timeout
								await _shot(dir + "/02%s_leave_%s.png" % ["abc"[cast_shots], str(card.name).to_lower()])
								await get_tree().create_timer(view.LEAD + view.IMPACT_AT - 0.22).timeout
								await _shot(dir + "/02%s_cast_%s.png" % ["abc"[cast_shots], str(card.name).to_lower()])
								await get_tree().create_timer(0.05).timeout # just after it lands: bone chips, ash, threads
								await _shot(dir + "/02%s_hit_%s.png" % ["abc"[cast_shots], str(card.name).to_lower()])
								cast_shots += 1
							break
				if not played:
					var physical := str(combat.intent.get("kind", "")) == "physical" and not combat.bone_remains
					turns.end_turn()
					if combat.turn_ending and not combat.finished:
						turns.react(false)
					if not physical and not dust_shot and not combat.bone_remains and not combat.finished:
						dust_shot = true # GRAVE DUST and the like: it shakes and sheds dust
						await get_tree().create_timer(0.3).timeout
						await _shot(dir + "/02f_dust.png")
					if physical and not attack_shot:
						attack_shot = true # the skeleton's BONE CUT: wind-up, then its hit frame
						await get_tree().create_timer(0.38).timeout
						await _shot(dir + "/02d_attack_windup.png")
						await get_tree().create_timer(0.17).timeout
						await _shot(dir + "/02e_attack_hit.png")
						await get_tree().create_timer(0.12).timeout
						await _shot(dir + "/02g_hero_hit.png")
		elif turns.phase == TURNS.Phase.ENEMY_TURN and combat.turn_ending:
			turns.react(false)
		hud.refresh()
		await _frames(2)
	await _frames(60)
	await _shot(dir + "/04_after.png")
	# All nine exit glyphs in a row along the top of the room, to judge them against each other.
	var lineup: Array[Node2D] = []
	for i in ROOM_EXIT.KINDS.size():
		var sample: Node2D = ROOM_EXIT.new()
		sample.setup({"zone": Rect2(), "kind": ROOM_EXIT.KINDS[i], "target": "", "side": "top", "glyph_at": Vector2(240 + i * 60, 40)}, _language)
		add_child(sample)
		sample.enabled = true
		lineup.append(sample)
	await _frames(4)
	await _shot(dir + "/04b_exit_glyphs.png")
	for sample in lineup:
		sample.queue_free()
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


## Walks the word route without playing the fights out: each fight is cut short (the bones fall at
## once, then it is won), so only the learning moments are pictured.
const SKIP_DEMO := 0.35 # capture: a hold part-way to a skip

func _capture_route(dir: String) -> void:
	var wait := func(t: float): await get_tree().create_timer(t).timeout
	hero.position = Vector2(560, 240)
	await wait.call(0.5)
	await _shot(dir + "/r01_room.png")
	hero.position = Vector2(250, 420) # across the room: only the glint shows
	await wait.call(0.8)
	await _shot(dir + "/r01b_glint.png")
	hero.position = Vector2(380, 360) # near the broken cross: the word is seen
	await wait.call(0.35)
	await _shot(dir + "/r02a_writing.png")
	await wait.call(1.2)
	await _shot(dir + "/r02_seen.png")
	_lexicon.set_progress(progress.known_words())
	_lexicon.show_word("shatter")
	_lexicon.set_open_now(true)
	await wait.call(0.3)
	await _shot(dir + "/r02b_book_seen.png")
	_lexicon.set_open_now(false)
	cleared_rooms["bg_1"] = true
	_load_room("bg_2", "")
	hero.position = Vector2(200, 480)
	await wait.call(1.5)
	await _shot(dir + "/r03a_angel_far.png")
	hero.position = Vector2(480, 352)
	await wait.call(1.0)
	await _shot(dir + "/r03_angel.png")
	interactions.interact()
	await wait.call(0.6)
	await _shot(dir + "/r04_question.png")
	words._choose(0) # wrong first: worn away
	await wait.call(0.5)
	await _shot(dir + "/r05_wrong.png")
	words._close()
	await wait.call(0.3)
	interactions.interact()
	await wait.call(0.4)
	words._choose(1)
	await wait.call(0.5)
	await _shot(dir + "/r06_right.png")
	words._close()
	await wait.call(0.8)
	await _shot(dir + "/r07_recognized.png")
	await wait.call(0.5)
	await _shot(dir + "/r07a_slip_underline.png")
	await wait.call(0.5)
	await _shot(dir + "/r07b_slip_pencil.png")
	await wait.call(1.05)
	await _shot(dir + "/r07c_slip_flying.png")
	_load_room("bg_3", "")
	hero.position = skeleton.position + Vector2(-100, 30)
	await wait.call(2.8)
	if combat.deck.mulligan_pending:
		combat.finish_mulligan([])
	combat._enemy_defeated() # the bones fall: the half-known word is lent
	hud.refresh()
	view.refresh()
	await wait.call(1.4)
	await _shot(dir + "/r08_lent.png")
	var lent: Dictionary = combat.deck.hand.filter(func(c): return bool(c.get("borrowed", false))).front()
	combat.focus = 4 # one carried over: four nodes by HP
	view.refresh()
	view.forced_hover = int(lent.instance_id)
	view._show_word_tip(lent, view._words.get_child(combat.deck.hand.find(lent)))
	await wait.call(0.5)
	await _shot(dir + "/r09_lent_tip.png")
	var binds: Array = combat.deck.hand.filter(func(c): return str(c.card_id) == "BIND")
	if not binds.is_empty():
		view._hide_tip()
		view.forced_hover = int(binds[0].instance_id)
		view._show_word_tip(binds[0], view._words.get_child(combat.deck.hand.find(binds[0])))
		await wait.call(0.5)
		await _shot(dir + "/r09b_bind_tip.png")
	view._hide_tip()
	view.forced_hover = -1
	combat.focus = maxi(combat.focus, 3)
	_invoke(int(lent.instance_id), "hp")
	await wait.call(1.0)
	await _shot(dir + "/r10_understood.png")
	combat._finish_battle(true)
	await wait.call(2.0)
	await _shot(dir + "/r10b_slip_writing.png")
	await wait.call(1.0)
	await _shot(dir + "/r10c_slip_ink.png")
	await wait.call(1.6)
	_load_room("vw_1", "")
	hero.position = Vector2(480, 340)
	await wait.call(1.0)
	await _shot(dir + "/r11_slab.png")
	interactions.interact()
	await wait.call(0.6)
	await _shot(dir + "/r12_which_word.png")
	words._choose(words._answers.size() - 1) # SHATTER comes last: the word just understood
	await wait.call(0.5)
	await _shot(dir + "/r13_shattered.png")
	words._close()
	await wait.call(0.8)
	await _shot(dir + "/r14_usable.png")
	await wait.call(4.0)
	await _shot(dir + "/r15_book.png")
	await wait.call(0.8)
	await _shot(dir + "/r15b_lighting.png")
	await wait.call(1.5)
	await _shot(dir + "/r15c_card.png")
	await wait.call(2.0)
	await _shot(dir + "/r15d_closing.png")
	if _lexicon.is_open:
		_lexicon.toggle()
	await wait.call(2.5)
	_load_room("vw_2", "") # a heap of bones that rises when the hero comes near (D-079)
	hero.position = Vector2(400, 380)
	await wait.call(0.8)
	await _shot(dir + "/r16_bones.png")
	hero.position = skeleton.position + Vector2(-100, 20)
	await wait.call(0.9)
	await _shot(dir + "/r17_rising.png")
	await wait.call(3.0)
	await _shot(dir + "/r18_fight.png")
	combat._finish_battle(true) # a second ceremony: this one can be skipped by holding Space
	await wait.call(1.5)
	_lexicon.ceremony("shatter", true)
	await wait.call(2.6)
	await _shot(dir + "/r19_skip_hint.png")
	_lexicon._hold = SKIP_DEMO
	await wait.call(0.05)
	await _shot(dir + "/r19b_skip_holding.png")
	_lexicon.skip_ceremony()
	await wait.call(2.0)
	# Several words at once (D-086): a pile, peeled off one page at a time.
	for lemma in ["bind", "scatter", "shatter"]:
		words.show_slip(lemma, "UNDERSTOOD" if lemma == "shatter" else "RECOGNIZED")
	await wait.call(0.6)
	await _shot(dir + "/r20_pile.png")
	await wait.call(0.75)
	await _shot(dir + "/r20b_pile_next.png")
	await wait.call(1.1)
	await _shot(dir + "/r20c_pile_last.png")
	print("ROUTE shatter=%s deck=%s" % [progress.stage("shatter"), progress.deck_cards(manager.learning)])


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


## A player some way in: words at every stage, then the book from the whole sky down to one word,
## and one redraw caught halfway.
func _capture_sky(dir: String) -> void:
	var wait := func(t: float): await get_tree().create_timer(t).timeout
	for pair in [["shatter", "USABLE"], ["scatter", "RECOGNIZED"], ["crumble", "ENCOUNTERED"], ["decay", "UNDERSTOOD"],
			["erode", "RECOGNIZED"], ["wither", "USABLE"], ["grave", "UNDERSTOOD"], ["bury", "ENCOUNTERED"], ["bone", "RECOGNIZED"],
			["grief", "UNDERSTOOD"], ["memory", "ENCOUNTERED"], ["fog", "RECOGNIZED"], ["lantern", "UNDERSTOOD"], ["bell", "ENCOUNTERED"]]:
		progress.set_stage(pair[0], pair[1])
	progress.remember("decay", "RECOGNIZED", "Everything here is slowly [decaying].", "The Sunken Grave · Broken Graveyard")
	progress.remember("decay", "UNDERSTOOD", "The wood of the cross has [decayed] to dust.", "A skeleton fight · Veiled Walk")
	_lexicon.set_progress(progress.known_words())
	_lexicon.set_open_now(true)
	_lexicon._go(1, [0, 0, 0, 0], 0, false)
	_lexicon._sky = 0.0
	await wait.call(2.5)
	await _shot(dir + "/s1_sky.png")
	_lexicon.zoom_in(0) # Breaking
	await wait.call(0.35)
	await _shot(dir + "/s1b_redrawing.png")
	await wait.call(2.2)
	await _shot(dir + "/s2_region.png")
	_lexicon.zoom_in(1) # Wearing away
	await wait.call(2.5)
	await _shot(dir + "/s3_cluster.png")
	_lexicon.zoom_in(0) # DECAY
	await wait.call(2.5)
	await _shot(dir + "/s4_constellation.png")
	_lexicon.selected = 1
	_lexicon.queue_redraw()
	await wait.call(0.3)
	await _shot(dir + "/s4b_chosen.png")
	_lexicon.zoom_in(1) # decay
	await wait.call(2.5)
	await _shot(dir + "/s5_word.png")
	_lexicon.turn_page(true)
	await wait.call(0.4)
	await _shot(dir + "/s5b_turning.png")
	await wait.call(1.0)
	await _shot(dir + "/s5c_next_word.png")


func _shot(path: String) -> void:
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(path)
