extends SceneTree
var checks := 0
var failures: Array[String] = []
func _initialize() -> void: _run.call_deferred()
func verify(condition: bool, reason: String) -> void:
	checks += 1
	if not condition: failures.append(reason)
func _run() -> void:
	var tiles := preload("res://art/cemetery_kit_v1/terrain/cemetery_tileset.tres")
	verify(tiles.tile_size==Vector2i(256,256),"texture tile size256, world scale0.5 required")
	verify(tiles.get_source(0).get_tiles_count()==24,"six materials times four phases")
	verify(tiles.get_source(1).get_tiles_count()==80,"five materials times sixteen independent edges")
	var entries: Array = JSON.parse_string(FileAccess.get_file_as_string("res://art/cemetery_kit_v1/module_manifest.json"))
	for entry in entries:
		if not entry.has("scene"): continue
		var scene: Node2D = load("res://"+str(entry.scene)).instantiate()
		root.add_child(scene)
		var artwork := scene.get_node("Artwork") as Sprite2D
		verify(artwork.texture!=null,entry.name+" texture loads")
		verify(is_equal_approx(artwork.scale.x,artwork.scale.y),entry.name+" keeps uniform scale")
		verify(is_equal_approx(artwork.position.y,-artwork.texture.get_height()*artwork.scale.y/2),entry.name+" bottom centre origin")
		if entry.role=="Structure": verify(scene.has_node("SocketA") and scene.has_node("SocketB"),entry.name+" separate ground sockets")
		scene.queue_free()
	for word in ["observe","shatter","erode"]:
		var widget: Control = load("res://art/cemetery_kit_v1/ui/"+word+".tscn").instantiate()
		root.add_child(widget)
		verify(widget.word_id==word.to_upper(),word+" native semantic UI wrapper")
		widget.queue_free()
	for path in ["res://art/cemetery_kit_v1/vfx/bone_scatter.tscn","res://art/cemetery_kit_v1/vfx/dust_burst.tscn"]:
		var effect: Node2D = load(path).instantiate()
		root.add_child(effect)
		effect.play_event(&"preview",{"position":Vector2(40,40)})
		verify(effect.get_child_count()>0,path+" consumes actual independent source textures")
	await create_timer(1).timeout
	verify(root.find_child("BoneScatter",true,false)==null and root.find_child("DustBurst",true,false)==null,"source bursts self-release")
	print("CEMETERY_KIT_RESOURCE_SMOKE: ","PASS" if failures.is_empty() else "FAIL"," / ",checks," checks")
	for reason in failures: push_error(reason)
	quit(0 if failures.is_empty() else 1)
