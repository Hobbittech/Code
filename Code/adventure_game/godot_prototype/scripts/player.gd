extends CharacterBody3D

const WALK_SPEED := 4.0
const LOOK_SENSITIVITY := 0.0025
const MAX_LOOK_ANGLE := deg_to_rad(80.0)

@onready var head: Node3D = $Head
@onready var interaction_ray: RayCast3D = $Head/Camera3D/RayCast3D

var look_pitch := 0.0


func _ready() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		rotate_y(-event.relative.x * LOOK_SENSITIVITY)
		look_pitch = clampf(
			look_pitch - event.relative.y * LOOK_SENSITIVITY,
			-MAX_LOOK_ANGLE,
			MAX_LOOK_ANGLE
		)
		head.rotation.x = look_pitch
	elif event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_ESCAPE:
			Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		elif event.keycode == KEY_E and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
			interact()
	elif event is InputEventMouseButton and event.pressed:
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED


func _physics_process(_delta: float) -> void:
	var move_input := Vector2.ZERO
	if Input.is_key_pressed(KEY_A):
		move_input.x -= 1.0
	if Input.is_key_pressed(KEY_D):
		move_input.x += 1.0
	if Input.is_key_pressed(KEY_W):
		move_input.y += 1.0
	if Input.is_key_pressed(KEY_S):
		move_input.y -= 1.0

	var direction := (transform.basis * Vector3(move_input.x, 0, -move_input.y)).normalized()
	velocity.x = direction.x * WALK_SPEED
	velocity.z = direction.z * WALK_SPEED
	if not is_on_floor():
		velocity += get_gravity() * _delta
	move_and_slide()


func interact() -> void:
	interaction_ray.force_raycast_update()
	if not interaction_ray.is_colliding():
		get_parent().show_message("Nothing is within reach. Look at an object and press E.")
		return

	var target := interaction_ray.get_collider() as Node3D
	if is_instance_valid(target) and target.has_meta("interaction_id"):
		get_parent().interact_with(target.get_meta("interaction_id"), target)
	else:
		get_parent().show_message("It looks ordinary—for now.")
