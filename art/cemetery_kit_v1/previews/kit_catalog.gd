extends Control
## Reusable kit sampler, deliberately independent of game state and final map layout.
var stage: Node2D
var ground: TileMapLayer
var prop_slot: Node2D
var actor: Node2D
var skeleton: Node2D
var catalog: Array = []
var actor_velocity := Vector2.ZERO
var last_facing := Vector2.RIGHT
var readout: Label
func _ready() -> void:
	var background := ColorRect.new()
	background.color = Color(0.07,0.085,0.09)
	background.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	background.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(background)
	stage = Node2D.new()
	stage.position = Vector2(340,110)
	add_child(stage)
	ground = TileMapLayer.new()
	ground.tile_set = preload("res://art/cemetery_kit_v1/terrain/cemetery_tileset.tres")
	ground.scale = Vector2.ONE*0.5
	ground.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	stage.add_child(ground)
	_set_material(0)
	prop_slot = Node2D.new()
	prop_slot.position = Vector2(320,320)
	stage.add_child(prop_slot)
	var title := Label.new()
	title.text = "Cemetery Production Kit v1 — Godot Asset Sampler"
	title.position = Vector2(24,18)
	add_child(title)
	var instructions := Label.new()
	instructions.text = "F6 runs this sampler. WASD / arrows move the rig. All modules are separate scene instances."
	instructions.position = Vector2(24,52)
	add_child(instructions)
	var panel := VBoxContainer.new()
	panel.position = Vector2(24,110)
	panel.size = Vector2(285,600)
	add_child(panel)
	var terrain := OptionButton.new()
	for name in ["Wet stone","Broken stone","Mud","Moss","Cracked floor","Puddle / damp"]: terrain.add_item(name)
	terrain.item_selected.connect(_set_material)
	panel.add_child(terrain)
	catalog = JSON.parse_string(FileAccess.get_file_as_string("res://art/cemetery_kit_v1/module_manifest.json"))
	var selector := OptionButton.new()
	for entry in catalog:
		if entry.has("scene"): selector.add_item(entry.name)
	selector.item_selected.connect(func(index: int):
		var scenes: Array = catalog.filter(func(entry: Dictionary): return entry.has("scene"))
		show_prop(scenes[index])
	)
	panel.add_child(selector)
	readout = Label.new()
	readout.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	readout.custom_minimum_size = Vector2(280,130)
	panel.add_child(readout)
	show_prop(catalog[0])
	actor = _optional_rig("res://art/cemetery_kit_v1/player/player_rig.tscn",Vector2(220,340))
	skeleton = _optional_rig("res://art/cemetery_kit_v1/skeleton/skeleton_rig.tscn",Vector2(480,340))
	for animation in ["idle","walk","attack","hit","collapse","remains","reassembly"]:
		var button := Button.new()
		button.text = "Skeleton: "+animation
		button.pressed.connect(func():
			if skeleton != null:
				var player := skeleton.find_child("AnimationPlayer",true,false) as AnimationPlayer
				if player != null and player.has_animation(animation): player.play(animation)
		)
		panel.add_child(button)
	for spec in [["Echo", "res://art/vfx/echo_absorb.tscn"],["Bone scatter","res://art/cemetery_kit_v1/vfx/bone_scatter.tscn"],["Dust","res://art/cemetery_kit_v1/vfx/dust_burst.tscn"]]:
		var button := Button.new()
		button.text = spec[0]
		button.pressed.connect(func():
			var effect: Node2D = load(spec[1]).instantiate()
			stage.add_child(effect)
			effect.position = Vector2(400,320)
			effect.play_event(&"preview",{"position":effect.global_position,"target":stage.to_global(Vector2(220,290))})
		)
		panel.add_child(button)
	var sigils := HBoxContainer.new()
	sigils.position = Vector2(340,650)
	add_child(sigils)
	for word in ["observe","shatter","erode"]:
		var widget: Control = load("res://art/cemetery_kit_v1/ui/"+word+".tscn").instantiate()
		sigils.add_child(widget)
		widget.set_presentation({"word_id":word,"focus_cost":2,"state":"IDLE"})
func _optional_rig(path: String, point: Vector2) -> Node2D:
	if not ResourceLoader.exists(path): return null
	var rig: Node2D = load(path).instantiate()
	stage.add_child(rig)
	rig.position = point
	return rig
func _set_material(index: int) -> void:
	for y in range(4):
		for x in range(5): ground.set_cell(Vector2i(x,y),0,Vector2i(index,0))
func show_prop(entry: Dictionary) -> void:
	for child in prop_slot.get_children(): child.queue_free()
	if entry.has("scene"):
		var item: Node2D = load("res://"+str(entry.scene)).instantiate()
		prop_slot.add_child(item)
		readout.text = str(entry.name)+"\n"+str(entry.scene)+"\nWorld size: "+str(entry.get("display_size",[]))+"\nTransparent PNG + Sprite2D; uniform scale.\nContact origin: bottom centre."
func _process(delta: float) -> void:
	if actor == null: return
	var motion := Input.get_vector("ui_left","ui_right","ui_up","ui_down")
	if Input.is_physical_key_pressed(KEY_A): motion.x -= 1
	if Input.is_physical_key_pressed(KEY_D): motion.x += 1
	if Input.is_physical_key_pressed(KEY_W): motion.y -= 1
	if Input.is_physical_key_pressed(KEY_S): motion.y += 1
	actor_velocity = motion.limit_length()*100
	actor.position += actor_velocity*delta
	actor.position = actor.position.clamp(Vector2(0,120),Vector2(640,500))
	if motion.length()>0.01: last_facing = motion.normalized()
	if actor.has_method("present_motion"): actor.present_motion(actor_velocity,last_facing)
