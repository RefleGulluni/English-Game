extends SceneTree
## Exports individual transparent UI textures from the actual editable Control.
const WORDS := ["OBSERVE","SHATTER","ERODE"]
const STATES := ["IDLE","HOVERED","SELECTED","INVOKING","USED","RETAINED","ECHO_COPY","EXHAUSTED","DISABLED"]
func _initialize() -> void: _capture.call_deferred()
func _capture() -> void:
	for word in WORDS:
		for state in STATES:
			var viewport := SubViewport.new()
			viewport.size = Vector2i(440,248)
			viewport.transparent_bg = true
			viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
			root.add_child(viewport)
			var widget := preload("res://art/ui/word_sigil.tscn").instantiate()
			viewport.add_child(widget)
			widget.size = Vector2(220,124)
			widget.scale = Vector2.ONE*2
			# Costs are runtime data. The raster fallback deliberately excludes Focus costs.
			widget.set_presentation({"word_id":word,"state":state,"focus_cost":0})
			widget.phase = 0.2
			widget.set_process(false)
			widget.queue_redraw()
			await process_frame
			await RenderingServer.frame_post_draw
			var picture := viewport.get_texture().get_image()
			var path: String = "res://art/cemetery_kit_v1/ui/"+word.to_lower()+"_"+state.to_lower()+".png"
			assert(picture.save_png(path)==OK)
			viewport.queue_free()
			await process_frame
	print("SIGIL_UI_EXPORT: PASS / 27 individual transparent 440x248 textures; dynamic costs remain live Control data")
	quit()
