extends SceneTree
## Turns every ground decal in art/cemetery_v3/ground/decals/ (decal_*.png) into a scene the user
## can drag into a room: scenes/props/cemetery/decals/<name>.tscn, one Sprite2D lying flat on the
## ground. Decals have no collision and no Y-sort; they belong under a room's Ground node, after
## the painted terrain layers, so they sit on paths and grass but under every prop and actor.
## The origin is the decal's centre (whole pixels), so it lands where the mouse lets go.
##
##   Godot --headless --path . --import
##   Godot --headless --path . --script res://scripts/tools/bake_ground_decals.gd
## Existing scenes are skipped; pass `-- --force=<name>` to rebuild one.
## Method: docs/GROUND_TERRAIN_METHOD.md §2, §5.

const ART := "res://art/cemetery_v3/ground/decals/"
const OUT := "res://scenes/props/cemetery/decals/"


func _init() -> void:
	var force := ""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--force="):
			force = arg.get_slice("=", 1)
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	var made := 0
	for file in DirAccess.get_files_at(ART):
		if not (file.begins_with("decal_") and file.ends_with(".png")):
			continue
		var decal_name := file.get_basename()
		var path := OUT + decal_name + ".tscn"
		if FileAccess.file_exists(path) and force != decal_name:
			continue
		var tex: Texture2D = load(ART + file)
		var sprite := Sprite2D.new()
		sprite.name = decal_name.trim_prefix("decal_").to_pascal_case()
		sprite.texture = tex
		sprite.centered = false # a centred odd-sized sprite would sit on half pixels
		sprite.offset = Vector2(-(tex.get_width() / 2), -(tex.get_height() / 2))
		var scene := PackedScene.new()
		scene.pack(sprite)
		sprite.free()
		var err := ResourceSaver.save(scene, path)
		print("%s %s" % ["saved" if err == OK else "FAILED", path])
		made += 1
	print("bake_ground_decals: %d scene(s) written" % made)
	quit()
