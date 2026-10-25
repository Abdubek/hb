import bpy
import bmesh
import math
from mathutils import Vector


def reset_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in list(coll):
            if item.users == 0:
                coll.remove(item)


def make_material(name, color, metallic=0.0, roughness=0.5):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def new_object(name, bm, mat=None, location=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1)):
    mesh = bpy.data.meshes.new(name)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = rotation
    obj.scale = scale
    if mat is not None:
        mesh.materials.append(mat)
    mesh.shade_smooth()
    return obj


def add_cylinder(name, radius, depth, mat=None, location=(0, 0, 0), rotation=(0, 0, 0), segments=48):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius, radius2=radius, depth=depth)
    return new_object(name, bm, mat, location, rotation)


def add_sphere(name, radius, mat=None, location=(0, 0, 0), hemisphere=False, scale=(1, 1, 1)):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=radius)
    if hemisphere:
        lower = [v for v in bm.verts if v.co.z < -1e-5]
        bmesh.ops.delete(bm, geom=lower, context='VERTS')
    return new_object(name, bm, mat, location, scale=scale)


def add_open_pot(name, radius, height, thickness, mat, location, segments=64):
    """Capped cylinder with its top face removed, walled by a solidify modifier."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius, radius2=radius, depth=height)
    caps = [f for f in bm.faces if len(f.verts) == segments]
    top = max(caps, key=lambda f: f.calc_center_median().z)
    bmesh.ops.delete(bm, geom=[top], context='FACES')
    obj = new_object(name, bm, mat, location)
    solid = obj.modifiers.new("Wall", 'SOLIDIFY')
    solid.thickness = thickness
    solid.offset = -1.0
    return obj


def add_torus(name, major, minor, mat, location):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                     major_segments=64, minor_segments=10,
                                     location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.name = name
    obj.data.materials.append(mat)
    obj.data.shade_smooth()
    return obj


def aim_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


reset_scene()

steel = make_material("Brushed_Steel", (0.72, 0.74, 0.76), metallic=1.0, roughness=0.28)
phenolic = make_material("Black_Phenolic", (0.045, 0.045, 0.05), metallic=0.0, roughness=0.42)
counter = make_material("Counter_Stone", (0.30, 0.29, 0.28), metallic=0.0, roughness=0.55)

R = 0.09
H = 0.11

# --- pan ---
add_open_pot("Pan_Body", R, H, 0.0022, steel, (0.0, 0.0, H * 0.5))
add_cylinder("Pan_Base_Disc", R - 0.002, 0.009, steel, location=(0.0, 0.0, 0.0045))
add_torus("Pan_Rim", R, 0.0028, steel, (0.0, 0.0, H))

# --- handle, angled slightly upward as it leaves the body ---
tilt = math.radians(9.0)
start = Vector((R + 0.006, 0.0, 0.082))
direction = Vector((math.cos(tilt), 0.0, math.sin(tilt)))
length = 0.20
rot = (0.0, math.radians(90.0) - tilt, 0.0)
add_cylinder("Handle_Bracket", 0.019, 0.024, steel, location=tuple(start), rotation=rot, segments=32)
add_cylinder("Handle_Grip", 0.013, length, phenolic,
             location=tuple(start + direction * (length * 0.5)), rotation=rot, segments=32)
add_sphere("Handle_End_Cap", 0.0135, phenolic, tuple(start + direction * length))

# --- lid ---
lid_z = H + 0.003
add_cylinder("Lid_Flange", R + 0.006, 0.005, steel, location=(0.0, 0.0, lid_z))
add_sphere("Lid_Dome", R - 0.004, steel, (0.0, 0.0, lid_z), hemisphere=True, scale=(1.0, 1.0, 0.36))
dome_top = lid_z + (R - 0.004) * 0.36
add_cylinder("Knob_Stem", 0.0085, 0.020, steel, location=(0.0, 0.0, dome_top + 0.008), segments=24)
add_sphere("Lid_Knob", 0.019, phenolic, (0.0, 0.0, dome_top + 0.032))

# --- ground ---
bm = bmesh.new()
bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.7)
new_object("Countertop", bm, counter, (0.05, 0.0, -0.001))

# --- lighting ---
key_data = bpy.data.lights.new("Key_Light", 'AREA')
key_data.energy = 180.0
key_data.size = 0.9
key = bpy.data.objects.new("Key_Light", key_data)
bpy.context.collection.objects.link(key)
key.location = (0.45, -0.45, 0.70)
aim_at(key, (0.05, 0.0, 0.09))

fill_data = bpy.data.lights.new("Fill_Light", 'AREA')
fill_data.energy = 50.0
fill_data.size = 1.2
fill = bpy.data.objects.new("Fill_Light", fill_data)
bpy.context.collection.objects.link(fill)
fill.location = (-0.55, -0.30, 0.40)
aim_at(fill, (0.0, 0.0, 0.09))

world = bpy.context.scene.world or bpy.data.worlds.new("Studio")
bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.05, 0.055, 0.06, 1.0)

# --- camera ---
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 55.0
cam = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam)
cam.location = (0.34, -0.48, 0.30)
aim_at(cam, (0.05, 0.0, 0.085))
bpy.context.scene.camera = cam
