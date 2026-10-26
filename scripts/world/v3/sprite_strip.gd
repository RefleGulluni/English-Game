class_name SpriteStrip
extends Sprite2D
## Plays one horizontal frame strip (96×96 cells) with per-frame durations from the character
## group's timing.json. The feet sit on the node's origin, like every v3 actor and prop.

signal finished

var _durations: Array = []
var _loop := true
var _hold_last := false
var _frame_time := 0.0
var playing := false


## dir: the folder that holds timing.json and the sheet; anim: the key in timing.json.
func load_strip(dir: String, anim: String) -> void:
	var timing: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(dir + "timing.json"))
	var data: Dictionary = timing.animations[anim]
	var cell: Array = timing.get("frame_size", [96, 96])
	texture = PixelArt.texture(dir + str(data.sprite_sheet))
	hframes = int(data.frames)
	centered = false
	offset = Vector2(-cell[0] / 2, -cell[1])
	_durations = data.durations_ms
	_loop = bool(data.get("loop", true))
	_hold_last = bool(data.get("hold_last_frame", false))
	restart()


func restart() -> void:
	frame = 0
	_frame_time = 0.0
	playing = true


func _process(delta: float) -> void:
	if not playing or _durations.is_empty():
		return
	_frame_time += delta * 1000.0
	while playing and _frame_time >= float(_durations[frame]):
		_frame_time -= float(_durations[frame])
		if frame + 1 < hframes:
			frame += 1
		elif _loop:
			frame = 0
		else:
			playing = false
			if not _hold_last:
				frame = 0
			finished.emit()
