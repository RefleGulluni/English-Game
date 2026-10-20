extends SceneTree
var checks := 0
var failures: Array[String] = []
func _initialize() -> void: _run.call_deferred()
func check(value: bool, message: String) -> void:
	checks += 1
	if not value: failures.append(message)
func _run() -> void:
	var world := preload("res://scenes/main.tscn").instantiate()
	world.set_meta("qa_no_save",true)
	root.add_child(world)
	for i in range(4): await process_frame
	var visual := world.get_node("GraveSkeleton/VisualRoot/GraveSkeletonVisual")
	check(visual.nodes.size()==20,"twenty independent skeleton parts")
	var baseline_echo: int = world.manager.state.echo
	visual.present({"mode":"remains","integrity":10,"reassemble_in":3})
	await create_timer(0.7).timeout
	check(visual.mode=="remains" and not visual.moving,"collapse reaches the remains pose")
	check(world.manager.state.echo==baseline_echo,"presentation snapshot cannot grant Echo")
	check(world.get_node("WorldLoot").get_child_count()==0,"presentation snapshot cannot spawn loot")
	visual.present({"mode":"standing"})
	await create_timer(0.9).timeout
	check(visual.mode=="standing" and not visual.moving,"reassembly reaches original standing pose")
	visual.present({"mode":"cleared"})
	await create_timer(0.65).timeout
	check(not visual.rope.visible,"cleared pose releases all tension links")
	check(world.get_node("GraveSkeleton/Hitbox")!=null and world.get_node("GraveSkeleton/LootAnchor")!=null,"logic-owned nodes preserved")
	var sigil := preload("res://art/ui/word_sigil.tscn").instantiate()
	root.add_child(sigil)
	for word in ["OBSERVE","SHATTER","ERODE"]:
		for state in sigil.STATES:
			sigil.set_presentation({"word_id":word,"state":state,"focus_cost":2,"instance_id":42})
			check(sigil.visual_state==state and sigil.word_id==word,"sigil accepts "+word+"/"+state)
	sigil.set_presentation({"word_id":"OBSERVE","state":"SELECTED","enabled":false})
	check(sigil.visual_state=="DISABLED","business availability overrides selected presentation")
	var clasp: Node2D = world.get_node("Player/VisualRoot/PlayerVisual").clasp
	world.events.publish(&"word_sigil_invoked",{"word_id":"OBSERVE","instance_id":42})
	await create_timer(0.15).timeout
	check(clasp.strength>0.1,"invocation reaches player clasp after deferred event binding")
	await create_timer(1.7).timeout
	check(clasp.strength==0.0,"clasp returns to quiet")
	check(world.get_node("PresentationRouter/VFXRoot").get_child_count()==0,"short effects release themselves")
	check(world.manager.state.echo==baseline_echo,"word VFX cannot mutate rewards")
	world.queue_free()
	sigil.queue_free()
	await process_frame
	print("ART_CONTRACT_SMOKE: ", "PASS" if failures.is_empty() else "FAIL", " / ",checks," checks")
	for message in failures: push_error(message)
	quit(0 if failures.is_empty() else 1)
