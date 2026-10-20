extends SceneTree
var failures: Array[String] = []
var output := "res://art_source/production/broken_graveyard_p01/reviews"

func _initialize() -> void: _run.call_deferred()

func capture(name: String) -> void:
	for i in range(3): await process_frame
	await RenderingServer.frame_post_draw
	var path := ProjectSettings.globalize_path(output+"/"+name+".png")
	var err := root.get_texture().get_image().save_png(path)
	if err != OK: failures.append(path)

func _run() -> void:
	root.size = Vector2i(1280,720)
	var review := preload("res://art/previews/production_review.tscn").instantiate()
	root.add_child(review)
	await create_timer(0.3).timeout
	var pose_file := FileAccess.open(output.get_base_dir()+"/skeleton_pose_manifest.json",FileAccess.WRITE)
	var poses := {"standing":{}, "remains":{}}
	for key in review.rig.nodes:
		for category in ["standing","remains"]:
			var transform: Dictionary = review.rig.rest[key] if category == "standing" else review.rig.fallen[key]
			poses[category][key] = {"position":[transform.position.x,transform.position.y],"rotation":transform.rotation,"scale":[transform.scale.x,transform.scale.y],"texture":"art/enemies/skeleton_parts/"+str(key)+".png"}
	pose_file.store_string(JSON.stringify(poses,"  "))
	review.tabs.current_tab = 0
	await capture("skeleton_production_sheet")
	review.rig.present({"mode":"remains","reassemble_in":3})
	await create_timer(0.65).timeout
	await capture("bone_remains_pose")
	review.rig.present({"mode":"standing"})
	await create_timer(0.4).timeout
	await capture("reassembly_midpoint")
	review.tabs.current_tab = 1
	await capture("environment_layer_breakdown")
	review.tabs.current_tab = 3
	await capture("clasp_chisel_vfx_sheet")
	var transparent := SubViewport.new()
	transparent.size = Vector2i(256,192)
	transparent.transparent_bg = true
	transparent.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(transparent)
	var clasp := preload("res://art/characters/lexicon_clasp.tscn").instantiate()
	clasp.position = Vector2(128,96)
	clasp.scale = Vector2.ONE*3.0
	clasp.responding = true
	transparent.add_child(clasp)
	for i in range(3): await process_frame
	await RenderingServer.frame_post_draw
	transparent.get_texture().get_image().save_png(ProjectSettings.globalize_path(output+"/clasp_responding_transparent.png"))
	transparent.queue_free()
	review.tabs.current_tab = 4
	await capture("audio_draft_list")
	var sheet_view := SubViewport.new()
	sheet_view.size = Vector2i(1280,1280)
	sheet_view.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(sheet_view)
	var sheet := preload("res://art/previews/production_review.tscn").instantiate()
	sheet_view.add_child(sheet)
	sheet.tabs.current_tab = 2
	for i in range(3): await process_frame
	await RenderingServer.frame_post_draw
	sheet_view.get_texture().get_image().save_png(ProjectSettings.globalize_path(output+"/word_sigil_nine_states.png"))
	sheet_view.queue_free()
	var animated := SubViewport.new()
	animated.size = Vector2i(512,384)
	animated.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(animated)
	var animated_rig := preload("res://art/enemies/enm_skeleton_visual.tscn").instantiate()
	animated_rig.position = Vector2(256,340)
	animated_rig.scale = Vector2.ONE*2.5
	animated.add_child(animated_rig)
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(output+"/animation_frames"))
	for i in range(25):
		if i == 3: animated_rig.present({"mode":"remains"})
		if i == 14: animated_rig.present({"mode":"standing"})
		await create_timer(0.08).timeout
		await RenderingServer.frame_post_draw
		animated.get_texture().get_image().save_png(ProjectSettings.globalize_path(output+"/animation_frames/frame_%02d.png"%i))
	animated.queue_free()
	var fx_view := SubViewport.new()
	fx_view.size = Vector2i(512,256)
	fx_view.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(fx_view)
	var chisel := preload("res://art/loot/loot_weathered_chisel_visual.tscn").instantiate()
	chisel.position = Vector2(110,140)
	fx_view.add_child(chisel)
	var actor := preload("res://art/characters/chr_player_visual.tscn").instantiate()
	actor.position = Vector2(405,175)
	actor.scale = Vector2.ONE*0.8
	fx_view.add_child(actor)
	var echo := preload("res://art/vfx/echo_absorb.tscn").instantiate()
	fx_view.add_child(echo)
	echo.position = Vector2(110,140)
	echo.play_event(&"echo_spawned",{"target":Vector2(405,140)})
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(output+"/vfx_frames"))
	for i in range(25):
		await create_timer(0.08).timeout
		await RenderingServer.frame_post_draw
		fx_view.get_texture().get_image().save_png(ProjectSettings.globalize_path(output+"/vfx_frames/frame_%02d.png"%i))
	fx_view.queue_free()
	review.queue_free()
	await process_frame
	print("ART_CAPTURE_COMPLETE failures=",failures.size())
	quit(0 if failures.is_empty() else 1)
