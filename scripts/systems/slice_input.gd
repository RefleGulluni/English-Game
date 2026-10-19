extends RefCounted

static func install() -> void:
	var bindings := {"world_left": [KEY_A, KEY_LEFT], "world_right": [KEY_D, KEY_RIGHT], "world_up": [KEY_W, KEY_UP], "world_down": [KEY_S, KEY_DOWN], "world_interact": [KEY_E], "open_lexicon": [KEY_L], "open_run_bag": [KEY_TAB]}
	for action in bindings:
		if not InputMap.has_action(action): InputMap.add_action(action)
		for key in bindings[action]:
			var event := InputEventKey.new()
			event.physical_keycode = key
			if not InputMap.action_has_event(action, event): InputMap.action_add_event(action, event)
