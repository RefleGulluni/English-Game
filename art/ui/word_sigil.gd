@tool
extends Control
## Reusable presentation control. It requests actions; it never spends Focus.
signal invocation_requested(instance_id: int)
const STATES := ["IDLE","HOVERED","SELECTED","INVOKING","USED","RETAINED","ECHO_COPY","EXHAUSTED","DISABLED"]
const FONT = preload("res://art/ui/fonts/CormorantGaramond.ttf")
@export_enum("OBSERVE","SHATTER","ERODE") var word_id := "OBSERVE"
@export_enum("IDLE","HOVERED","SELECTED","INVOKING","USED","RETAINED","ECHO_COPY","EXHAUSTED","DISABLED") var visual_state := "IDLE"
@export_range(0,8) var focus_cost := 1
@export var instance_id := -1
@export var accept_input := true
var phase := 0.0
var hover := false

func _ready() -> void:
	custom_minimum_size = Vector2(208,118)
	mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	focus_mode = Control.FOCUS_ALL
	mouse_entered.connect(func(): hover = true; queue_redraw())
	mouse_exited.connect(func(): hover = false; queue_redraw())
	resized.connect(queue_redraw)

func set_presentation(snapshot: Dictionary) -> void:
	word_id = str(snapshot.get("word_id",word_id)).to_upper()
	instance_id = int(snapshot.get("instance_id",instance_id))
	focus_cost = int(snapshot.get("focus_cost",focus_cost))
	visual_state = str(snapshot.get("state","IDLE")).to_upper()
	if not bool(snapshot.get("enabled",true)): visual_state = "DISABLED"
	tooltip_text = str(snapshot.get("reason",""))
	phase = 0.0
	queue_redraw()

func _gui_input(event: InputEvent) -> void:
	if not accept_input or visual_state in ["DISABLED","EXHAUSTED","USED"]: return
	var clicked: bool = event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed
	if clicked or event.is_action_pressed("ui_accept"):
		invocation_requested.emit(instance_id)
		accept_event()

func _process(delta: float) -> void:
	phase += delta
	queue_redraw()

func _draw() -> void:
	var state := "HOVERED" if hover and visual_state == "IDLE" else visual_state
	var alpha := 0.92
	if state == "USED": alpha = 0.42
	if state == "DISABLED": alpha = 0.48
	if state == "EXHAUSTED": alpha = 0.5
	var ink := Color(0.84,0.8,0.69,alpha)
	if state == "HOVERED": ink = Color(0.97,0.94,0.83,1)
	var center := size*0.5 + Vector2(0,-10)
	var unit := minf(size.x/220.0,size.y/124.0)
	draw_set_transform(center,0,Vector2.ONE*unit)
	var font_size := 29
	var width := FONT.get_string_size(word_id,HORIZONTAL_ALIGNMENT_LEFT,-1,font_size).x
	if state == "ECHO_COPY":
		draw_string(FONT,Vector2(-width*0.5+3,12),word_id,HORIZONTAL_ALIGNMENT_LEFT,-1,font_size,Color(0.62,0.68,0.69,0.22))
		_geometry(ink*Color(1,1,1,0.25),Vector2(3,2),state)
	_geometry(ink,Vector2.ZERO,state)
	draw_string(FONT,Vector2(-width*0.5,9),word_id,HORIZONTAL_ALIGNMENT_LEFT,-1,font_size,ink)
	# Cost is a chain of energy chambers in the lower semantic structure, not a corner numeral.
	var active := state in ["SELECTED","INVOKING"]
	var count := clampi(focus_cost,0,8)
	for index in range(count):
		var p := Vector2((index-(count-1)*0.5)*12,42)
		if index == 0: draw_line(Vector2(0,28),p,ink*Color(1,1,1,0.55),0.7,true)
		if index > 0: draw_line(p-Vector2(8,0),p-Vector2(3,0),ink*Color(1,1,1,0.55),0.65,true)
		draw_arc(p,3.1,0,TAU,20,ink,0.8,true)
		if active: draw_circle(p,1.6,ink)
	if state == "RETAINED":
		draw_polyline(PackedVector2Array([Vector2(-8,49),Vector2(-8,54),Vector2(8,54),Vector2(8,49)]),ink,0.75,true)
	if state == "INVOKING":
		var radius := 47.0 + minf(phase,0.55)*9
		var fade := maxf(0.0,1.0-phase/0.65)
		draw_arc(Vector2.ZERO,radius,0.12,1.25,24,Color(ink,fade*0.6),0.8,true)
		draw_arc(Vector2.ZERO,radius,PI+0.12,PI+1.25,24,Color(ink,fade*0.6),0.8,true)

func _geometry(ink: Color, offset: Vector2, state: String) -> void:
	var color := ink*Color(1,1,1,0.65)
	var lift := -2.0 if state == "SELECTED" else 0.0
	match word_id:
		"OBSERVE":
			for sign_y in [-1.0,1.0]:
				var points := PackedVector2Array()
				for i in range(25):
					var t := float(i)/24
					points.append(offset+Vector2(-39+78*t,sign_y*(15+20*sin(t*PI))+lift))
				draw_polyline(points,color,0.8,true)
			for side in [-1.0,1.0]:
				for sign_y in [-1.0,1.0]:
					draw_line(offset+Vector2(side*100,0),offset+Vector2(side*28,sign_y*29),color,0.65,true)
				draw_circle(offset+Vector2(side*100,0),1.3,color)
			draw_line(offset+Vector2(0,-39),offset+Vector2(0,-47),color,0.75,true)
		"SHATTER":
			var spread := 3.0 if state in ["SELECTED","INVOKING"] else 0.0
			var pieces := [
				[Vector2(-52,-19),Vector2(-39,-32),Vector2(-25,-21)],
				[Vector2(1,-18),Vector2(1,-35),Vector2(12,-28),Vector2(12,-17)],
				[Vector2(36,-18),Vector2(48,-30),Vector2(54,-24)],
				[Vector2(-44,21),Vector2(-35,31),Vector2(-26,23)],
				[Vector2(0,22),Vector2(6,35),Vector2(13,29)],
				[Vector2(36,20),Vector2(49,29),Vector2(53,18)]
			]
			for i in range(pieces.size()):
				if state == "EXHAUSTED" and i % 2 == 0: continue
				var pts := PackedVector2Array()
				for p in pieces[i]: pts.append(p+offset+Vector2((-1 if i%2 else 1)*spread,0))
				draw_polyline(pts,color,0.9,true)
		"ERODE":
			for i in range(37):
				if i in [5,6,7,9,10,11]: continue
				if state == "EXHAUSTED" and i in [3,4,12,13,14]: continue
				var a := TAU*float(i)/40
				var b := TAU*float(i+1)/40
				if absf(sin(a)) < 0.42: continue
				var ra := 39.0+sin(float(i)*4.1)*1.5
				var rb := 39.0+sin(float(i+1)*4.1)*1.5
				draw_line(offset+Vector2(cos(a)*ra,sin(a)*ra),offset+Vector2(cos(b)*rb,sin(b)*rb),color,0.7+0.45*(1.0-float(i)/40),true)
			for i in range(4):
				var p := offset+Vector2(39+i*4,-20+i*7)
				draw_line(p,p+Vector2(1.3,0.7),color*Color(1,1,1,0.65),0.75,true)
