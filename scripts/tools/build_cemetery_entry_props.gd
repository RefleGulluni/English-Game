extends SceneTree
## Puts every prop of the cemetery entry greybox into the scene as blocks the user can drag,
## delete and copy in the editor: a Props node (Y-sorted) holding one instance of
## scenes/props/cemetery/<name>.tscn per prop of the old layout (gate, fence, roadside graves,
## trees, fountain...) and per grave of the generated yard rows. From then on the greybox uses the
## Props node instead of its built-in layout, so the room is the user's to arrange.
##
## Only runs while the scene has no Props node; after that the props are the user's work.
## The editor-only Reference picture showed these props; the real blocks replace it, so it goes.
##
##   Godot --headless --path . --script res://scripts/tools/build_cemetery_entry_props.gd

const ROOM := "res://scenes/prototypes/cemetery_entry/cemetery_entry_greybox.tscn"
const ENTRY := preload("res://scripts/prototypes/cemetery_entry/cemetery_entry_greybox.gd")
const BLOCKS := "res://scenes/props/cemetery/"


func _init() -> void:
	var root: Node = load(ROOM).instantiate()
	if root.has_node("Props"):
		print("the entry already has its Props (the user's arrangement); nothing changed")
		root.free()
		quit()
		return
	var props := Node2D.new()
	props.name = "Props"
	props.y_sort_enabled = true
	root.add_child(props)
	root.move_child(props, root.get_node("Ground").get_index() + 1)
	props.owner = root
	var made := 0
	for p in ENTRY.LAYOUT.props + ENTRY.yard_graves():
		var block: Node2D = load(BLOCKS + str(p[0]) + ".tscn").instantiate()
		block.position = p[1] - Vector2(0, block.get("ground_gap"))
		props.add_child(block, true)
		block.owner = root
		made += 1
	var reference := root.get_node_or_null("Reference")
	if reference:
		root.remove_child(reference)
		reference.free()
	var scene := PackedScene.new()
	scene.pack(root)
	ResourceSaver.save(scene, ROOM)
	root.free()
	print("entry props saved: %d blocks in %s" % [made, ROOM])
	quit()
