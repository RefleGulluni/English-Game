@tool
extends TileMapLayer
## Editable cell data is authored into the scene by the build utility, never by combat.
@export var terrain_names := PackedStringArray(["wet_stone", "broken_stone", "mud", "moss", "cracked", "puddle_edge"])
@export_enum("Column", "Row") var atlas_material_axis := 0

func terrain_at(cell: Vector2i) -> String:
	var coords := get_cell_atlas_coords(cell)
	var index := coords.x if atlas_material_axis == 0 else coords.y
	return terrain_names[index] if index >= 0 and index < terrain_names.size() else ""
