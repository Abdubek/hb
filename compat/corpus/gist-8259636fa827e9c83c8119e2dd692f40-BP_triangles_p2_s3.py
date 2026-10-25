import math
import random

import bpy
import bmesh


def clean_scene():
    """
    Remove all objects from the scene
    """
    obj = bpy.context.active_object
    if obj and obj.mode == 'EDIT':
        bpy.ops.object.editmode_toggle()
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()


def setup_light(x, y, z):
    """Add a light to the scene"""
    bpy.ops.object.light_add(type='SUN', location=(x, y, z))


def setup_camera(x, y, z):
    """Add a camera and point it down along the Z axis"""
    bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=(x, y, z))
    rad_rot = math.radians(-90)
    bpy.ops.transform.rotate(value=rad_rot, orient_axis='Z')
    rad_rot = math.radians(-35)
    bpy.ops.transform.rotate(value=rad_rot, orient_axis='Z')

    camera = bpy.context.active_object
    bpy.context.scene.camera = camera


def get_random_color():
    """Generate a random color"""
    red = random.random()  # creates a value from 0.0 to 1.0
    green = random.random()
    blue = random.random()
    alpha = 1.0
    color = (red, green, blue, alpha)
    return color


def create_base_mesh():
    """Add a mesh to the scene"""
    bpy.ops.mesh.primitive_plane_add(size=20)


def subdivide_base_mesh():
    """Subdivide and split mesh using the subdivide and poke commands"""
    bpy.ops.object.editmode_toggle()  # Turn ON Edit Mode

    bpy.ops.mesh.subdivide(number_cuts=8)
    bpy.ops.mesh.poke()

    bpy.ops.object.editmode_toggle()  # Turn OFF Edit Mode


def add_color_to_mesh():
    """Creates and applies a random color to every face of a mesh"""
    base_mesh_object = bpy.context.active_object

    bpy.ops.object.editmode_toggle()  # Turn ON Edit Mode

    my_plane_bmesh = bmesh.from_edit_mesh(base_mesh_object.data)
    for face in my_plane_bmesh.faces:
        apply_color_to_face(base_mesh_object, face)

    bpy.ops.object.editmode_toggle()  # Turn OFF Edit Mode


def apply_color_to_face(mesh_object, face):
    """Create and apply the material to a face"""
    mat = bpy.data.materials.new(name="Material_face_" + str(face.index))
    mat.diffuse_color = get_random_color()  # (R, G, B, A)

    mesh_object.data.materials.append(mat)
    mesh_object.active_material_index = face.index

    face.select = True
    bpy.ops.object.material_slot_assign()
    face.select = False

# ============================================================
# ============================================================
# ============================================================

# Utility Building Blocks
clean_scene()
setup_light(x=0, y=0, z=25)
setup_camera(x=0, y=0, z=20)

create_base_mesh()
subdivide_base_mesh()
add_color_to_mesh()

bpy.ops.render.render('INVOKE_DEFAULT')
