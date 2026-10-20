extends SceneTree
## Build editable Skeleton2D/Bone2D cutout scenes from approved raster parts.
const CONTROLLER := preload("res://scripts/presentation/cutout_rig.gd")
const PLAYER_PARTS := "res://art/cemetery_kit_v1/player/parts/"
var rig_bones: Dictionary = {}
var reference: Dictionary = {}

func _initialize() -> void:
	build.call_deferred()

func build() -> void:
	var kinds: Array = ["skeleton"] if OS.get_cmdline_user_args().has("--skeleton-only") else ["player", "skeleton"]
	if "player" in kinds and not ResourceLoader.exists(PLAYER_PARTS + "head.png"):
		push_error("Approved player parts have not arrived")
		quit(1)
		return
	if "player" in kinds:
		for file in ["head", "torso", "upper_arm_l", "upper_arm_r", "forearm_l", "forearm_r", "hand_l", "hand_r", "thigh_l", "thigh_r", "shin_l", "shin_r", "boot_l", "boot_r", "weapon", "coat_front", "coat_back", "cloak", "belt_pouch", "head_back", "torso_back", "cloak_back", "coat_back_view"]:
			if not ResourceLoader.exists(PLAYER_PARTS + file + ".png"):
				push_error("Missing approved/imported player part: " + file)
				quit(1)
				return
	for kind in kinds:
		rig_bones.clear()
		var actor := Node2D.new()
		actor.name = "PlayerVisual" if kind == "player" else "GraveSkeletonVisual"
		var shadow := Sprite2D.new()
		shadow.name = "ContactShadow"
		var gradient := Gradient.new()
		gradient.colors = PackedColorArray([Color(0.015, 0.02, 0.018, 0.44), Color(0.015, 0.02, 0.018, 0)])
		var mask := GradientTexture2D.new()
		mask.gradient = gradient
		mask.width = 128
		mask.height = 128
		mask.fill = GradientTexture2D.FILL_RADIAL
		mask.fill_from = Vector2(0.5, 0.5)
		mask.fill_to = Vector2(1, 0.5)
		shadow.texture = mask
		shadow.scale = Vector2(54, 15) / 128.0
		shadow.position.y = 1
		actor.add_child(shadow)
		var facing := Node2D.new()
		facing.name = "FacingRoot"
		actor.add_child(facing)
		var skeleton := Skeleton2D.new()
		skeleton.name = "Rig"
		facing.add_child(skeleton)
		var anchor := _bone(skeleton, "Root", Vector2.ZERO)
		if kind == "player": _player(anchor)
		else: _skeleton(anchor, actor, facing)
		var animator := AnimationPlayer.new()
		animator.name = "AnimationPlayer"
		actor.add_child(animator)
		_own(actor, actor)
		root.add_child(actor)
		for key in rig_bones: rig_bones[key].set_meta("track_path", String(actor.get_path_to(rig_bones[key])))
		var library := AnimationLibrary.new()
		var actions := ["idle", "walk", "turn"] if kind == "player" else ["idle", "walk", "attack", "hit", "collapse", "remains", "reassembly", "cleared"]
		for action in actions: library.add_animation(action, _animation(kind, action))
		var reset := _base_pose(0.1)
		library.add_animation("RESET", reset)
		animator.add_animation_library("", library)
		actor.set_script(CONTROLLER)
		actor.actor_kind = kind
		var directory := "res://art/cemetery_kit_v1/%s" % kind
		DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(directory))
		var packed := PackedScene.new()
		packed.pack(actor)
		var error := ResourceSaver.save(packed, directory + "/%s_rig.tscn" % kind)
		print("CUTOUT_RIG_BUILD · ", kind, " · ", error_string(error), " · ", rig_bones.size(), " animated joints")
		actor.free()
	quit()

func _own(node: Node, owner_root: Node) -> void:
	for child in node.get_children():
		child.owner = owner_root
		_own(child, owner_root)

func _bone(parent: Node, label: String, at: Vector2) -> Bone2D:
	var bone := Bone2D.new()
	bone.name = label
	bone.position = at
	bone.set_autocalculate_length_and_angle(false)
	bone.set_length(maxf(6, at.length()))
	bone.rest = bone.transform
	parent.add_child(bone)
	return bone

func _part(parent: Node, key: String, world_pivot: Vector2, offset: Vector2, height: float, back_key := "", front_only := false) -> Bone2D:
	var parent_world := Vector2.ZERO
	if parent is Bone2D: parent_world = parent.get_meta("world_pivot", Vector2.ZERO)
	var bone := _bone(parent, key, world_pivot - parent_world)
	bone.set_meta("world_pivot", world_pivot)
	rig_bones[key] = bone
	var sprite := _cropped_sprite(PLAYER_PARTS + key + ".png", height)
	sprite.name = "Front"
	sprite.position = offset
	sprite.set_meta("part_id", key)
	bone.add_child(sprite)
	if not back_key.is_empty() and ResourceLoader.exists(PLAYER_PARTS + back_key + ".png"):
		sprite.set_meta("view", "front")
		var back := _cropped_sprite(PLAYER_PARTS + back_key + ".png", height)
		back.name = "Back"
		back.position = offset
		back.visible = false
		back.set_meta("view", "back")
		bone.add_child(back)
	elif front_only: sprite.set_meta("view", "front")
	return bone

func _cropped_sprite(path: String, height: float) -> Sprite2D:
	var texture := load(path) as Texture2D
	var bounds := texture.get_image().get_used_rect()
	var region := AtlasTexture.new()
	region.atlas = texture
	region.region = Rect2(bounds)
	var sprite := Sprite2D.new()
	sprite.texture = region
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	sprite.scale = Vector2.ONE * height / maxf(1, bounds.size.y)
	return sprite

func _player(anchor: Bone2D) -> void:
	var pelvis := _bone(anchor, "pelvis", Vector2(0, -52))
	pelvis.set_meta("world_pivot", Vector2(0, -52))
	rig_bones.pelvis = pelvis
	_part(pelvis, "coat_back", Vector2(0, -60), Vector2(0, 22), 47, "coat_back_view")
	_part(pelvis, "cloak", Vector2(0, -99), Vector2(0, 14), 29, "cloak_back")
	for side in ["l", "r"]:
		var x := -8.0 if side == "l" else 9.0
		var thigh := _part(pelvis, "thigh_" + side, Vector2(x, -58), Vector2(0, 11), 23)
		var shin := _part(thigh, "shin_" + side, Vector2(x, -37), Vector2(0, 10), 22)
		_part(shin, "boot_" + side, Vector2(x, -10), Vector2(1, 0), 19)
	var torso := _part(pelvis, "torso", Vector2(0, -86), Vector2(0, 6), 39, "torso_back")
	_part(torso, "coat_front", Vector2(0, -60), Vector2(0, 21), 45, "", true)
	_part(torso, "belt_pouch", Vector2(0, -59), Vector2(0, 0), 13)
	_part(torso, "head", Vector2(0, -107), Vector2.ZERO, 23, "head_back")
	for side in ["l", "r"]:
		var sign_x := -1.0 if side == "l" else 1.0
		var arm := _part(torso, "upper_arm_" + side, Vector2(17 * sign_x, -95), Vector2(0, 11), 23)
		var forearm := _part(arm, "forearm_" + side, Vector2(21 * sign_x, -74), Vector2(0, 9), 20)
		var hand := _part(forearm, "hand_" + side, Vector2(24 * sign_x, -55), Vector2(0, 3), 12)
		if side == "r":
			var blade := _part(hand, "weapon", Vector2(26, -53), Vector2(6, 19), 56)
			blade.rotation = -0.55
			blade.rest = blade.transform
	var clasp := preload("res://art/characters/lexicon_clasp.tscn").instantiate()
	clasp.name = "LexiconClasp"
	clasp.position = Vector2(-5, -4)
	clasp.scale = Vector2.ONE * 0.1
	torso.add_child(clasp)

func _skeleton(anchor: Bone2D, actor: Node2D, facing: Node2D) -> void:
	reference = JSON.parse_string(FileAccess.get_file_as_string("res://art_source/production/broken_graveyard_p01/skeleton_pose_manifest.json"))
	var standing: Dictionary = {}
	var remains: Dictionary = {}
	# Detached bones deliberately keep separate transforms: the burial cords pull structure together.
	var order := ["foot_l", "foot_r", "shin_l", "shin_r", "thigh_l", "thigh_r", "pelvis", "ribcage", "upper_arm_l", "upper_arm_r", "forearm_l", "forearm_r", "hand_l", "hand_r", "weapon", "hip_cloth", "shoulder_cloth", "skull", "burial_cord", "nails"]
	for key in order:
		var pose: Dictionary = reference.standing[key]
		var bone := _bone(anchor, key, Vector2(pose.position[0], pose.position[1]))
		bone.rotation = pose.rotation
		bone.rest = bone.transform
		rig_bones[key] = bone
		var sprite := Sprite2D.new()
		sprite.name = "BoneArt"
		sprite.texture = load("res://" + str(pose.texture))
		sprite.scale = Vector2(pose.scale[0], pose.scale[1])
		sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
		sprite.set_meta("part_id", key)
		bone.add_child(sprite)
		for pair in [[standing, reference.standing[key]], [remains, reference.remains[key]]]:
			var value: Dictionary = pair[1]
			pair[0][key] = {"position": Vector2(value.position[0], value.position[1]), "rotation": float(value.rotation), "scale": Vector2(value.scale[0], value.scale[1])}
	actor.set_meta("reference_standing", standing)
	actor.set_meta("reference_remains", remains)
	var rope := Line2D.new()
	rope.name = "TensionLinks"
	rope.width = 0.65
	rope.default_color = Color(0.28, 0.24, 0.18, 0.72)
	rope.antialiased = true
	facing.add_child(rope)

func _track(animation: Animation, path: String, times: Array, values: Array) -> void:
	var index := animation.find_track(NodePath(path), Animation.TYPE_VALUE)
	if index < 0:
		index = animation.add_track(Animation.TYPE_VALUE)
		animation.track_set_path(index, NodePath(path))
	else:
		while animation.track_get_key_count(index) > 0: animation.track_remove_key(index, 0)
	for i in range(times.size()): animation.track_insert_key(index, times[i], values[i])

func _path(key: String, property: String) -> String:
	return str(rig_bones[key].get_meta("track_path")) + ":" + property

func _base_pose(duration: float) -> Animation:
	var animation := Animation.new()
	animation.length = duration
	for key in rig_bones:
		var bone: Bone2D = rig_bones[key]
		_track(animation, _path(key, "position"), [0, duration], [bone.position, bone.position])
		_track(animation, _path(key, "rotation"), [0, duration], [bone.rotation, bone.rotation])
		_track(animation, _path(key, "scale"), [0, duration], [Vector2.ONE, Vector2.ONE])
	_track(animation, "FacingRoot:position", [0, duration], [Vector2.ZERO, Vector2.ZERO])
	_track(animation, "FacingRoot:modulate", [0, duration], [Color.WHITE, Color.WHITE])
	_track(animation, "ContactShadow:scale", [0, duration], [Vector2(54, 15) / 128.0, Vector2(54, 15) / 128.0])
	return animation

func _rotation(animation: Animation, key: String, times: Array, offsets: Array) -> void:
	var base: float = rig_bones[key].rotation
	_track(animation, _path(key, "rotation"), times, offsets.map(func(value): return base + float(value)))

func _animation(kind: String, action: String) -> Animation:
	var duration := 2.4 if action == "idle" else (0.8 if action == "walk" else 0.18)
	if kind == "skeleton": duration = {"idle": 2.4, "walk": 1.1, "attack": 0.62, "hit": 0.24, "collapse": 0.78, "remains": 2.2, "reassembly": 1.05, "cleared": 0.1}[action]
	var animation := _base_pose(duration)
	if action in ["idle", "walk", "remains"]: animation.loop_mode = Animation.LOOP_LINEAR
	var t := [0.0, duration * 0.25, duration * 0.5, duration * 0.75, duration]
	if kind == "player":
		if action == "walk":
			_rotation(animation, "thigh_l", t, [-0.34, 0, 0.34, 0, -0.34])
			_rotation(animation, "thigh_r", t, [0.34, 0, -0.34, 0, 0.34])
			_rotation(animation, "shin_l", t, [0.14, 0.30, 0.08, 0, 0.14])
			_rotation(animation, "shin_r", t, [0.08, 0, 0.14, 0.30, 0.08])
			_rotation(animation, "upper_arm_l", t, [0.26, 0, -0.26, 0, 0.26])
			_rotation(animation, "upper_arm_r", t, [-0.26, 0, 0.26, 0, -0.26])
			_rotation(animation, "forearm_l", t, [0.04, 0.10, 0.17, 0.1, 0.04])
			_rotation(animation, "forearm_r", t, [0.17, 0.10, 0.04, 0.1, 0.17])
			_rotation(animation, "cloak", t, [-0.09, 0.02, 0.09, -0.02, -0.09])
			_rotation(animation, "coat_back", t, [0.06, -0.02, -0.06, 0.02, 0.06])
			_rotation(animation, "coat_front", t, [-0.03, 0.02, 0.03, -0.02, -0.03])
		elif action == "idle":
			var p: Vector2 = rig_bones.torso.position
			_track(animation, _path("torso", "position"), t, [p, p + Vector2(0, -0.45), p, p + Vector2(0, 0.25), p])
			_rotation(animation, "cloak", t, [0, 0.025, 0, -0.025, 0])
		else:
			_rotation(animation, "torso", [0, duration * 0.5, duration], [0, -0.09, 0])
			_rotation(animation, "coat_back", [0, duration * 0.5, duration], [0, 0.08, 0])
		return animation
	if action in ["collapse", "remains", "reassembly", "cleared"]:
		for key in rig_bones:
			var standing: Dictionary = reference.standing[key]
			var fallen: Dictionary = reference.remains[key]
			var a := Vector2(standing.position[0], standing.position[1])
			var b := Vector2(fallen.position[0], fallen.position[1])
			var flattened := Vector2(float(fallen.scale[0]) / float(standing.scale[0]), float(fallen.scale[1]) / float(standing.scale[1]))
			if action == "collapse":
				_track(animation, _path(key, "position"), [0, 0.50, duration], [a, b + Vector2(0, -2), b])
				_track(animation, _path(key, "rotation"), [0, duration], [standing.rotation, fallen.rotation])
				_track(animation, _path(key, "scale"), [0, duration], [Vector2.ONE, flattened])
			elif action == "reassembly":
				var delay := 0.0 if key == "pelvis" else (0.24 if key == "skull" else 0.12)
				_track(animation, _path(key, "position"), [0, delay + 0.01, duration * 0.84, duration], [b, b, a + Vector2(0, -1.0), a])
				_track(animation, _path(key, "rotation"), [0, delay + 0.01, duration], [fallen.rotation, fallen.rotation, standing.rotation])
				_track(animation, _path(key, "scale"), [0, duration], [flattened, Vector2.ONE])
			else:
				_track(animation, _path(key, "position"), [0, duration], [b, b])
				_track(animation, _path(key, "rotation"), [0, duration], [fallen.rotation, fallen.rotation])
				_track(animation, _path(key, "scale"), [0, duration], [flattened, flattened])
				if key == "skull" and action == "remains": _track(animation, _path(key, "position"), [0, 1.1, 1.25, 1.5, duration], [b, b, b + Vector2(-0.65, -0.25), b, b])
		var small := Vector2(54, 15) / 128.0
		var spread := Vector2(84, 13) / 128.0
		_track(animation, "ContactShadow:scale", [0, duration], [spread if action != "collapse" else small, small if action == "reassembly" else spread])
	elif action == "attack":
		_track(animation, "FacingRoot:position", [0, 0.18, 0.34, duration], [Vector2.ZERO, Vector2(-3, 0), Vector2(-22, 0), Vector2.ZERO])
		_rotation(animation, "weapon", [0, 0.18, 0.34, duration], [0, 0.45, -0.9, 0])
		_rotation(animation, "forearm_l", [0, 0.18, 0.34, duration], [0, 0.18, -0.45, 0])
		_rotation(animation, "ribcage", [0, 0.24, 0.38, duration], [0, 0.05, -0.12, 0])
		_rotation(animation, "pelvis", [0, 0.12, 0.30, duration], [0, -0.08, -0.12, 0])
	elif action == "hit":
		_track(animation, "FacingRoot:position", [0, 0.07, duration], [Vector2.ZERO, Vector2(5, -1), Vector2.ZERO])
		_track(animation, "FacingRoot:modulate", [0, 0.04, duration], [Color.WHITE, Color(1.0, 0.65, 0.48), Color.WHITE])
		_rotation(animation, "skull", [0, 0.09, duration], [0, 0.18, 0])
	else:
		var amplitude := 0.22 if action == "walk" else 0.025
		_rotation(animation, "pelvis", t, [0, amplitude, 0, -amplitude, 0])
		_rotation(animation, "ribcage", t, [amplitude * 0.4, 0, -amplitude * 0.4, 0, amplitude * 0.4])
		_rotation(animation, "upper_arm_l", t, [-amplitude, 0.04, amplitude, -0.04, -amplitude])
		_rotation(animation, "skull", t, [0.03, -0.02, -0.03, 0.02, 0.03])
		if action == "walk":
			_rotation(animation, "thigh_l", t, [-0.25, 0.05, 0.25, -0.05, -0.25])
			_rotation(animation, "thigh_r", t, [0.18, -0.07, -0.18, 0.07, 0.18])
			_rotation(animation, "forearm_r", t, [0.04, -0.15, -0.22, 0.05, 0.04])
	return animation
