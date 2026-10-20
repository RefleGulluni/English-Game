extends Node2D
## Presentation only. Lights/tint are editor-authored nodes, not hidden runtime art.
@export var pulse_amplitude := 0.025
@export var pulse_rate := 0.7
@onready var light: PointLight2D = $GraveyardLocalLight
var base_energy := 0.42
var elapsed := 0.0

func _ready() -> void:
	base_energy = light.energy

func _process(delta: float) -> void:
	elapsed += delta
	light.energy = maxf(0.0, base_energy + sin(elapsed * pulse_rate) * pulse_amplitude)
