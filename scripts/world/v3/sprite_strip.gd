class_name SpriteStrip
extends Sprite2D
## Plays one horizontal frame strip (96×96 cells unless the animation says otherwise) with per-frame durations from the character
## group's timing.json. The feet sit on the node's origin, like every v3 actor and prop.

signal finished

var _durations: Array = []
var _loop := true
var _hold_last := false
var _frame_time := 0.0
var playing := false
var current := "" # the timing.json key now playing

static var _textures := {} # sheet path -> texture, shared by every strip


## dir: the folder that holds timing.json and the sheet; anim: the key in timing.json.
func load_strip(dir: String, anim: String) -> void:
	var timing: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(dir + "timing.json"))
	var data: Dictionary = timing.animations[anim]
	current = anim
	# An animation may bring its own cell and anchor (the 160x96 attack, feet at (80, 96)).
	var cell: Array = data.get("frame_size", timing.get("frame_size", [96, 96]))
	var anchor: Array = data.get("anchor", [cell[0] / 2, cell[1]])
	var path := dir + str(data.sprite_sheet)
	if not _textures.has(path):
		_textures[path] = PixelArt.texture(path)
	texture = _textures[path]
	hframes = int(data.frames)
	centered = false
	offset = Vector2(-int(anchor[0]), -int(anchor[1]))
	_durations = data.durations_ms
	_loop = bool(data.get("loop", true))
	_hold_last = bool(data.get("hold_last_frame", false))
	restart()


## Jumps to a random moment of a looping strip, so several actors sharing one idle don't move in step.
func random_phase() -> void:
	var total := 0.0
	for d in _durations:
		total += float(d)
	_frame_time = randf() * total
	frame = 0
	while _frame_time >= float(_durations[frame]):
		_frame_time -= float(_durations[frame])
		frame += 1


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
