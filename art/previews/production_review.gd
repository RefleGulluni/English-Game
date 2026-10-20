extends Control
const SIGIL = preload("res://art/ui/word_sigil.tscn")
const SKELETON = preload("res://art/enemies/enm_skeleton_visual.tscn")
var tabs: TabContainer
var rig: Node2D
var voices: AudioStreamPlayer
var environment: Node2D
var preview_cost := 1

func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var bg := ColorRect.new()
	bg.color = Color("161c20")
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)
	var title := Label.new()
	title.text = "BROKEN GRAVEYARD / PRODUCTION PREPARATION P01"
	title.position = Vector2(24,14)
	title.add_theme_font_size_override("font_size",21)
	add_child(title)
	tabs = TabContainer.new()
	tabs.position = Vector2(20,54)
	tabs.size = size-Vector2(40,74)
	tabs.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	tabs.offset_left = 20
	tabs.offset_top = 54
	tabs.offset_right = -20
	tabs.offset_bottom = -20
	add_child(tabs)
	_build_skeleton()
	_build_environment()
	_build_sigils()
	_build_effects()
	_build_audio()

func _page(title: String) -> Control:
	var page := Control.new()
	page.name = title
	tabs.add_child(page)
	return page

func _label(parent: Node, text: String, position: Vector2, font_size := 16) -> Label:
	var node := Label.new()
	node.text = text
	node.position = position
	node.add_theme_font_size_override("font_size",font_size)
	node.add_theme_color_override("font_color",Color("d8d0b8"))
	parent.add_child(node)
	return node

func _button(parent: Node, text: String, pos: Vector2, action: Callable) -> Button:
	var node := Button.new()
	node.text = text
	node.position = pos
	node.size = Vector2(176,34)
	node.pressed.connect(action)
	parent.add_child(node)
	return node

func _build_skeleton() -> void:
	var page := _page("Skeleton")
	_label(page,"20 CUTOUT PARTS / SAME PARTS FOR STANDING, COLLAPSE AND REASSEMBLY",Vector2(22,14))
	rig = SKELETON.instantiate()
	rig.position = Vector2(260,400)
	rig.scale = Vector2.ONE*2.5
	page.add_child(rig)
	_button(page,"IDLE",Vector2(26,450),func(): rig.present({"mode":"standing"}))
	_button(page,"ATTACK",Vector2(214,450),func(): rig.play_attack())
	_button(page,"COLLAPSE",Vector2(402,450),func(): rig.present({"mode":"remains","reassemble_in":3}))
	_button(page,"REASSEMBLY",Vector2(590,450),func(): rig.present({"mode":"standing"}))
	_button(page,"CLEARED",Vector2(778,450),func(): rig.present({"mode":"cleared"}))
	_label(page,"Left: 2.5x inspection. Pieces: independent transparent textures. Contact root remains (0,0).",Vector2(26,500),14)
	var index := 0
	for file in ["skull","ribcage","pelvis","weapon","upper_arm_l","upper_arm_r","forearm_l","forearm_r","thigh_l","thigh_r","shin_l","shin_r","hand_l","hand_r","foot_l","foot_r","shoulder_cloth","hip_cloth","burial_cord","nails"]:
		var rect := Sprite2D.new()
		rect.texture = load("res://art/enemies/skeleton_parts/"+file+".png")
		rect.position = Vector2(570+(index%5)*130,75+(index/5)*94)
		rect.scale = Vector2.ONE*minf(84.0/rect.texture.get_width(),67.0/rect.texture.get_height())
		page.add_child(rect)
		_label(page,file,rect.position+Vector2(-40,33),11)
		index += 1

func _build_environment() -> void:
	var page := _page("Environment Layers")
	_label(page,"1900 x 1100 / COLLISION-ALIGNED MODULES / FOG IS A SEPARATE SHADER",Vector2(20,12))
	var container := SubViewportContainer.new()
	container.position = Vector2(20,56)
	container.size = Vector2(950,550)
	container.stretch = true
	page.add_child(container)
	var viewport := SubViewport.new()
	viewport.size = Vector2i(950,550)
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	container.add_child(viewport)
	environment = preload("res://art/environments/env_broken_graveyard_visual.tscn").instantiate()
	environment.scale = Vector2.ONE*0.5
	viewport.add_child(environment)
	var index := 0
	for name in ["BackgroundGround","Backdrop","Midground","Foreground","Atmosphere"]:
		var check := CheckButton.new()
		check.text = name
		check.button_pressed = true
		check.position = Vector2(985,62+index*55)
		check.toggled.connect(func(value): environment.get_node(name).visible = value)
		page.add_child(check)
		index += 1

func _build_sigils() -> void:
	var page := _page("Word Sigil States")
	var scroll := ScrollContainer.new()
	scroll.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	page.add_child(scroll)
	var list := VBoxContainer.new()
	scroll.add_child(list)
	var note := Label.new()
	note.text = "Word-led semantic geometry / 9 states / demo cost = 1 chamber, supply real cost via set_presentation()."
	list.add_child(note)
	for state in ["IDLE","HOVERED","SELECTED","INVOKING","USED","RETAINED","ECHO_COPY","EXHAUSTED","DISABLED"]:
		var row := HBoxContainer.new()
		list.add_child(row)
		var name_label := Label.new()
		name_label.text = state
		name_label.custom_minimum_size = Vector2(160,118)
		row.add_child(name_label)
		for word in ["OBSERVE","SHATTER","ERODE"]:
			var sigil := SIGIL.instantiate()
			sigil.word_id = word
			sigil.visual_state = state
			sigil.accept_input = false
			sigil.focus_cost = preview_cost
			sigil.custom_minimum_size = Vector2(308,118)
			row.add_child(sigil)

func _build_effects() -> void:
	var page := _page("Clasp and VFX")
	var quiet := preload("res://art/characters/lexicon_clasp.tscn").instantiate()
	quiet.position = Vector2(175,145)
	quiet.scale = Vector2.ONE*2.2
	page.add_child(quiet)
	_label(page,"QUIET / ENLARGED",Vector2(80,228))
	var response := preload("res://art/characters/lexicon_clasp.tscn").instantiate()
	response.position = Vector2(450,145)
	response.scale = Vector2.ONE*2.2
	response.responding = true
	page.add_child(response)
	_label(page,"RESPONDING / ENLARGED",Vector2(340,228))
	var tiny := preload("res://art/loot/loot_weathered_chisel_visual.tscn").instantiate()
	tiny.position = Vector2(760,145)
	page.add_child(tiny)
	_label(page,"CHISEL / 1x WORLD SIZE",Vector2(665,228))
	var large := preload("res://art/loot/loot_weathered_chisel_visual.tscn").instantiate()
	large.position = Vector2(1040,145)
	large.scale = Vector2.ONE*10
	page.add_child(large)
	_label(page,"CHISEL / 10x INSPECTION",Vector2(935,228))
	_label(page,"Echo moves from left to right. No coins, beam or reward mutation.",Vector2(90,310))
	_button(page,"PLAY ECHO",Vector2(90,390),func():
		var fx := preload("res://art/vfx/echo_absorb.tscn").instantiate()
		page.add_child(fx)
		fx.position = Vector2(170,350)
		fx.play_event(&"echo_spawned",{"target":Vector2(520,350)}))
	_button(page,"PLAY LOOT GLINT",Vector2(290,390),func():
		var fx := preload("res://art/vfx/loot_glint.tscn").instantiate()
		page.add_child(fx)
		fx.position = Vector2(760,145)
		fx.play_event(&"special_loot_spawned",{}))
	_button(page,"PULSE CLASP",Vector2(490,390),func(): response.responding = false; response.respond())

func _build_audio() -> void:
	var page := _page("Audio Drafts")
	_label(page,"ORIGINAL SYNTHETIC FOLEY / RESONANCE CANDIDATES — LISTEN BEFORE FINAL APPROVAL",Vector2(30,18))
	voices = AudioStreamPlayer.new()
	page.add_child(voices)
	var names := {"Skeleton collapse":"enemies/skeleton_collapse","Bone scatter":"enemies/bone_scatter","Reassembly tension":"enemies/bone_reassembly_tension","Echo absorb":"loot/echo_absorb","Special Loot clink":"loot/special_loot_clink","Pickup":"loot/pickup","OBSERVE invoke":"words/observe_invoke","SHATTER invoke":"words/shatter_invoke","ERODE invoke":"words/erode_invoke"}
	var index := 0
	for name in names:
		var path := "res://audio/"+str(names[name])+".wav"
		_button(page,name,Vector2(45+(index%3)*310,90+(index/3)*110),func(): voices.stream = load(path); voices.play())
		index += 1
	_label(page,"Nine 48 kHz mono WAVs. Editable synthesis source retained; not recorded bone/metal Foley.",Vector2(45,475),15)
