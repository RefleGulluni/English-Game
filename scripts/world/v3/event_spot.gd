extends Node2D
## The thing in an event room the player walks up to (E): it carries the room's script card
## (data/events/<biome>/<id>.json) and asks the scene to open it. Solved, it stays quiet.
##
## D-079: a language-layer mark breathes over it, so the player sees from across the room that
## something here can be looked into; it softens once they are close (the thing's own word takes
## over) and goes out when the event is done. Since 2026-10-30 the mark is the glint the user
## likes from the first room (WordWorld.draw_glint), not the exit glyph for "event".

signal opened(spot: Node2D)


var card := {}
var solved := false
var _mark: Node2D
var _hero: Node2D
var _time := 0.0
var _alpha := 0.0


func setup(card_path: String, at: Vector2) -> void:
	card = JSON.parse_string(FileAccess.get_file_as_string(card_path))
	position = at


func can_interact(_player: Node2D) -> bool:
	return not solved


func get_prompt() -> String:
	return "[E] %s" % str(card.get("prompt", "Look closer"))


func interact(_player: Node2D) -> bool:
	opened.emit(self)
	return true


func show_mark(at: Vector2, language_layer: CanvasLayer, hero: Node2D) -> void:
	_hero = hero
	_mark = Node2D.new()
	_mark.position = at.round()
	_mark.draw.connect(_draw_mark)
	language_layer.add_child(_mark)


func _exit_tree() -> void:
	if is_instance_valid(_mark):
		_mark.queue_free()


func _process(delta: float) -> void:
	if not is_instance_valid(_mark):
		return
	_time += delta
	var near := is_instance_valid(_hero) and _hero.global_position.distance_to(global_position) < 110.0
	_alpha = move_toward(_alpha, 0.0 if solved else (0.35 if near else 1.0), delta * 1.5)
	_mark.visible = _alpha > 0.0
	_mark.queue_redraw()


func _draw_mark() -> void:
	WordWorld.draw_glint(_mark, Vector2(-1, -1), _alpha, _time)
