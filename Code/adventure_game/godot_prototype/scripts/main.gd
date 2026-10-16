extends Node3D

var inventory: Array[String] = []
var pencil_clue_found := false
var book_clue_found := false
var choosing_ending := false
var message_label: Label
var inventory_label: Label

var wood_material: StandardMaterial3D
var stone_material: StandardMaterial3D
var dark_material: StandardMaterial3D
var gold_material: StandardMaterial3D
var blue_material: StandardMaterial3D
var paper_material: StandardMaterial3D


func _ready() -> void:
	_create_materials()
	_create_room()
	_create_interface()
	show_message("The writer's study. Find the three objects, then learn what the blank wall and living book remember.")


func _unhandled_key_input(event: InputEvent) -> void:
	if not choosing_ending or not event.pressed or event.echo:
		return
	if event.keycode == KEY_O:
		choosing_ending = false
		show_message("You open the door. The erased story returns, and you become its keeper. Chapter complete.")
	elif event.keycode == KEY_L:
		choosing_ending = false
		show_message("You seal the door. The forgotten magic can rest, though its story remains unknown. Chapter complete.")


func interact_with(interaction_id: String, target: Node3D) -> void:
	if choosing_ending:
		show_message("Choose an ending: press O to open the door or L to seal it.")
		return

	match interaction_id:
		"pencil", "book", "key":
			_take_object(interaction_id, target)
		"blank_wall":
			if inventory.has("pencil"):
				pencil_clue_found = true
				show_message("You draw a line across the blank wall. Hidden letters appear: 'The door remembers what was written.'")
			else:
				show_message("The wall is blank. Perhaps something could write on it.")
		"book_stand":
			if inventory.has("book"):
				book_clue_found = true
				show_message("The book rewrites itself: 'A name freely given opens the way; a name forgotten closes it.'")
			else:
				show_message("A book-shaped hollow waits on the stand.")
		"unwritten_door":
			_try_door()
		_:
			show_message("Nothing happens.")


func _take_object(item: String, target: Node3D) -> void:
	if inventory.has(item):
		show_message("You already have the %s." % item)
		return
	inventory.append(item)
	target.queue_free()
	_update_inventory()
	match item:
		"pencil":
			show_message("You take the pencil. It feels warm, as if it is eager to write.")
		"book":
			show_message("You take the book. Its blank pages ripple like water.")
		"key":
			show_message("You take the iron key. It is cold, with a tiny mark shaped like a door.")


func _try_door() -> void:
	if not inventory.has("key"):
		show_message("The door has a keyhole. Find the small iron key on the desk.")
		return
	if not pencil_clue_found or not book_clue_found:
		show_message("The keyhole changes shape, then goes still. The blank wall and the living book may hold the missing clues.")
		return
	choosing_ending = true
	show_message("The key turns in your hand. Press O to open the door and restore the story, or L to seal it and let the magic rest.")


func show_message(text: String) -> void:
	if is_instance_valid(message_label):
		message_label.text = text


func _create_materials() -> void:
	wood_material = _material(Color("#60432f"), 0.0, 0.0)
	stone_material = _material(Color("#34384d"), 0.0, 0.0)
	dark_material = _material(Color("#171a2a"), 0.0, 0.0)
	gold_material = _material(Color("#f4c15d"), 0.45, 0.2)
	blue_material = _material(Color("#55b9df"), 0.25, 0.12)
	paper_material = _material(Color("#eadbb6"), 0.0, 0.0)


func _material(color: Color, metallic: float, emission: float) -> StandardMaterial3D:
	var result := StandardMaterial3D.new()
	result.albedo_color = color
	result.metallic = metallic
	result.roughness = 0.55
	if emission > 0.0:
		result.emission_enabled = true
		result.emission = color
		result.emission_energy_multiplier = emission
	return result


func _create_room() -> void:
	var environment := WorldEnvironment.new()
	var world := Environment.new()
	world.background_mode = Environment.BG_COLOR
	world.background_color = Color("#101323")
	world.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	world.ambient_light_color = Color("#aab2d4")
	world.ambient_light_energy = 0.35
	environment.environment = world
	add_child(environment)

	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-48, -28, 0)
	sun.light_color = Color("#b9c9ff")
	sun.light_energy = 0.45
	add_child(sun)

	var floor := _add_box("Stone Floor", Vector3(12, 0.3, 12), Vector3(0, -0.15, 0), stone_material, true)
	floor.name = "StoneFloor"
	_add_box("Left Wall", Vector3(0.3, 4, 12), Vector3(-6, 2, 0), dark_material, true)
	_add_box("Right Wall", Vector3(0.3, 4, 12), Vector3(6, 2, 0), dark_material, true)
	_add_box("Back Left Wall", Vector3(4.3, 4, 0.3), Vector3(-3.85, 2, -6), dark_material, true)
	_add_box("Back Right Wall", Vector3(4.3, 4, 0.3), Vector3(3.85, 2, -6), dark_material, true)
	_add_box("Wall Above Door", Vector3(3.4, 1.2, 0.3), Vector3(0, 3.4, -6), dark_material, true)

	_add_box("Writing Desk", Vector3(3.2, 0.18, 1.1), Vector3(0, 1.05, -2.5), wood_material, true)
	for x_position in [-1.35, 1.35]:
		for z_position in [-2.9, -2.1]:
			_add_box("Desk Leg", Vector3(0.16, 1.05, 0.16), Vector3(x_position, 0.52, z_position), wood_material, true)

	_add_pickup("Pencil", "pencil", Vector3(-0.85, 1.29, -2.5), Vector3(0.1, 0.48, 0.1), gold_material)
	_add_pickup("Book", "book", Vector3(0, 1.29, -2.5), Vector3(0.56, 0.14, 0.42), paper_material)
	_add_pickup("Iron Key", "key", Vector3(0.85, 1.29, -2.5), Vector3(0.36, 0.08, 0.18), gold_material)

	_add_box("Blank Wall Marker", Vector3(1.4, 1.5, 0.15), Vector3(-4.5, 1.35, -3.3), blue_material, false, "blank_wall")
	_add_box("Book Stand", Vector3(1.1, 0.9, 0.7), Vector3(4.2, 0.5, -3.7), wood_material, true)
	_add_box("Living Book", Vector3(0.55, 0.12, 0.42), Vector3(4.2, 1.1, -3.7), paper_material, false, "book_stand")
	_add_box("Unwritten Door", Vector3(2.1, 2.2, 0.2), Vector3(0, 1.1, -5.75), dark_material, false, "unwritten_door")
	_add_box("Door Keyhole", Vector3(0.12, 0.2, 0.04), Vector3(0.45, 1.1, -5.62), gold_material, false)

	_add_point_light(Vector3(-3.8, 3.4, -2.7), Color("#77c8ff"), 1.3, 6.0)
	_add_point_light(Vector3(3.8, 3.2, -3.1), Color("#f1b75d"), 1.0, 5.0)
	_add_point_light(Vector3(0, 3.1, -5.4), Color("#a778ff"), 1.1, 4.0)


func _add_box(
	object_name: String,
	size: Vector3,
	position: Vector3,
	material: Material,
	solid: bool,
	interaction_id: String = ""
) -> StaticBody3D:
	var body := StaticBody3D.new()
	body.name = object_name
	body.position = position
	if not interaction_id.is_empty():
		body.set_meta("interaction_id", interaction_id)
	var mesh_instance := MeshInstance3D.new()
	var mesh := BoxMesh.new()
	mesh.size = size
	mesh_instance.mesh = mesh
	mesh_instance.material_override = material
	body.add_child(mesh_instance)
	if solid or not interaction_id.is_empty():
		var collision := CollisionShape3D.new()
		var shape := BoxShape3D.new()
		shape.size = size
		collision.shape = shape
		body.add_child(collision)
	add_child(body)
	return body


func _add_pickup(
	object_name: String,
	interaction_id: String,
	position: Vector3,
	size: Vector3,
	material: Material
) -> void:
	var body := StaticBody3D.new()
	body.name = object_name
	body.position = position
	body.set_meta("interaction_id", interaction_id)
	var visual := MeshInstance3D.new()
	var mesh := BoxMesh.new()
	mesh.size = size
	visual.mesh = mesh
	visual.material_override = material
	body.add_child(visual)
	var collision := CollisionShape3D.new()
	var shape := BoxShape3D.new()
	shape.size = size + Vector3(0.16, 0.18, 0.16)
	collision.shape = shape
	body.add_child(collision)
	add_child(body)


func _add_point_light(position: Vector3, color: Color, energy: float, range: float) -> void:
	var light := OmniLight3D.new()
	light.position = position
	light.light_color = color
	light.light_energy = energy
	light.omni_range = range
	add_child(light)


func _create_interface() -> void:
	var canvas := CanvasLayer.new()
	add_child(canvas)

	var panel := ColorRect.new()
	panel.color = Color(0.035, 0.045, 0.08, 0.86)
	panel.anchor_left = 0.04
	panel.anchor_top = 0.73
	panel.anchor_right = 0.96
	panel.anchor_bottom = 0.96
	canvas.add_child(panel)

	message_label = Label.new()
	message_label.position = Vector2(22, 14)
	message_label.size = Vector2(1120, 92)
	message_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	message_label.add_theme_color_override("font_color", Color("#f3ead2"))
	message_label.add_theme_font_size_override("font_size", 19)
	panel.add_child(message_label)

	inventory_label = Label.new()
	inventory_label.position = Vector2(22, 100)
	inventory_label.size = Vector2(1120, 30)
	inventory_label.add_theme_color_override("font_color", Color("#9edcf4"))
	inventory_label.add_theme_font_size_override("font_size", 16)
	panel.add_child(inventory_label)

	var crosshair := Label.new()
	crosshair.text = "+"
	crosshair.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	crosshair.position = Vector2(-8, -16)
	crosshair.add_theme_color_override("font_color", Color("#ffffff"))
	crosshair.add_theme_font_size_override("font_size", 28)
	canvas.add_child(crosshair)

	var controls := Label.new()
	controls.text = "WASD move  |  Mouse look  |  E interact  |  Esc release mouse"
	controls.position = Vector2(24, 22)
	controls.add_theme_color_override("font_color", Color("#e4e8f5"))
	controls.add_theme_font_size_override("font_size", 16)
	canvas.add_child(controls)
	_update_inventory()


func _update_inventory() -> void:
	if not is_instance_valid(inventory_label):
		return
	var items := ", ".join(inventory)
	if items.is_empty():
		items = "empty"
	inventory_label.text = "Inventory: %s" % items
