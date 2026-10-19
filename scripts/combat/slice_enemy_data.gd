extends Resource

@export var id := "enemy.grave_skeleton"
@export var display_name := "GRAVE SKELETON"
@export var max_hp := 24
@export var structure := 12
@export var armor := 0
@export var remains_integrity := 10
@export var reassembly_rounds := 3
@export var ecology_tags: Array[String] = ["BONE", "BURIAL", "RUST", "REMAINS", "REASSEMBLY"]

func profile() -> Dictionary:
	var result: Dictionary = preload("res://scripts/combat/cemetery_enemies.gd").profiles()[1].duplicate(true)
	result.merge({"enemy_id": id, "name": display_name, "hp": max_hp, "structure": structure, "armor": armor}, true)
	return result
