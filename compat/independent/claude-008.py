import bpy
import bmesh
from mathutils import Vector


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in block:
            if item.users == 0:
                block.remove(item)


def make_material(name, color, roughness=0.5, metallic=0.0, emission=None):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if emission is not None:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 6.0
    return mat


def add_mesh(name, mat, parent=None):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat)
    bpy.context.collection.objects.link(obj)
    if parent is not None:
        obj.parent = parent
    return obj


def finish(bm, obj):
    bm.normal_update()
    bm.to_mesh(obj.data)
    bm.free()


def box(name, mat, size, location, parent=None, rotation=(0.0, 0.0, 0.0)):
    obj = add_mesh(name, mat, parent)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    finish(bm, obj)
    obj.location = location
    obj.rotation_euler = rotation
    return obj


def cylinder(name, mat, r1, r2, depth, location, segments=20, parent=None,
             rotation=(0.0, 0.0, 0.0)):
    obj = add_mesh(name, mat, parent)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=r1, radius2=r2, depth=depth)
    finish(bm, obj)
    obj.location = location
    obj.rotation_euler = rotation
    return obj


clear_scene()

mat_paver = make_material("MAT_Paver_Stone", (0.52, 0.51, 0.49), roughness=0.85)
mat_grout = make_material("MAT_Paver_Grout", (0.22, 0.22, 0.23), roughness=0.95)
mat_steel = make_material("MAT_Pole_Steel", (0.18, 0.19, 0.21), roughness=0.35, metallic=0.9)
mat_alu = make_material("MAT_Housing_Alu", (0.72, 0.73, 0.75), roughness=0.25, metallic=1.0)
mat_lens = make_material("MAT_Lens_Emissive", (0.95, 0.93, 0.80), roughness=0.1,
                        emission=(1.0, 0.95, 0.78))

root = bpy.data.objects.new("STREETLIGHT_ROOT", None)
bpy.context.collection.objects.link(root)

# --- Square pavement base: grout slab with an inset grid of pavers ---
PLAZA = 6.0
box("Pavement_Grout_Slab", mat_grout, (PLAZA, PLAZA, 0.12), (0.0, 0.0, -0.06), root)

N = 5
cell = PLAZA / N
gap = 0.05
for iy in range(N):
    for ix in range(N):
        x = -PLAZA * 0.5 + cell * (ix + 0.5)
        y = -PLAZA * 0.5 + cell * (iy + 0.5)
        box("Paver_%d_%d" % (ix, iy), mat_paver,
            (cell - gap, cell - gap, 0.10), (x, y, 0.01), root)

# Kerb ring around the plaza edge
half = PLAZA * 0.5 + 0.11
box("Kerb_North", mat_grout, (PLAZA + 0.44, 0.22, 0.22), (0.0, half, 0.02), root)
box("Kerb_South", mat_grout, (PLAZA + 0.44, 0.22, 0.22), (0.0, -half, 0.02), root)
box("Kerb_East", mat_grout, (0.22, PLAZA, 0.22), (half, 0.0, 0.02), root)
box("Kerb_West", mat_grout, (0.22, PLAZA, 0.22), (-half, 0.0, 0.02), root)

# --- Streetlight: base plate, tapered pole, arm, luminaire ---
box("Pole_Base_Plate", mat_steel, (0.46, 0.46, 0.06), (0.0, 0.0, 0.09), root)
cylinder("Pole_Base_Collar", mat_steel, 0.20, 0.16, 0.34, (0.0, 0.0, 0.29), 24, root)

POLE_H = 5.4
POLE_BOTTOM = 0.46
cylinder("Pole_Shaft", mat_steel, 0.135, 0.075, POLE_H,
         (0.0, 0.0, POLE_BOTTOM + POLE_H * 0.5), 24, root)
box("Pole_Access_Hatch", mat_alu, (0.16, 0.03, 0.32), (0.0, -0.125, 1.05), root)
cylinder("Pole_Cap", mat_steel, 0.08, 0.05, 0.09,
         (0.0, 0.0, POLE_BOTTOM + POLE_H + 0.04), 16, root)

# Horizontal arm reaching out over the roadway (+X)
ARM_L = 1.5
ARM_Z = POLE_BOTTOM + POLE_H - 0.10
cylinder("Lamp_Arm", mat_steel, 0.055, 0.045, ARM_L, (ARM_L * 0.5, 0.0, ARM_Z), 16, root,
         rotation=(0.0, 1.5707963, 0.0))
cylinder("Arm_Elbow", mat_steel, 0.075, 0.075, 0.14, (0.0, 0.0, ARM_Z), 16, root)

HEAD_X = ARM_L
box("Luminaire_Housing", mat_alu, (0.80, 0.34, 0.10), (HEAD_X, 0.0, ARM_Z - 0.06), root,
    rotation=(0.0, -0.09, 0.0))
box("Luminaire_Heatsink", mat_alu, (0.62, 0.28, 0.05), (HEAD_X, 0.0, ARM_Z + 0.02), root)
box("Luminaire_Lens", mat_lens, (0.68, 0.26, 0.03), (HEAD_X, 0.0, ARM_Z - 0.12), root,
    rotation=(0.0, -0.09, 0.0))

# --- Lighting and camera ---
sun_data = bpy.data.lights.new("KEY_Sun", type='SUN')
sun_data.energy = 3.0
sun = bpy.data.objects.new("KEY_Sun", sun_data)
sun.location = (5.0, -6.0, 9.0)
sun.rotation_euler = (0.62, 0.25, 0.85)
bpy.context.collection.objects.link(sun)

fill_data = bpy.data.lights.new("FILL_Area", type='AREA')
fill_data.energy = 250.0
fill_data.size = 5.0
fill = bpy.data.objects.new("FILL_Area", fill_data)
fill.location = (-6.0, -5.0, 5.0)
fill.rotation_euler = (0.9, -0.4, -0.7)
bpy.context.collection.objects.link(fill)

cam_data = bpy.data.cameras.new("SceneCamera")
cam_data.lens = 40.0
cam = bpy.data.objects.new("SceneCamera", cam_data)
cam.location = (8.5, -9.5, 5.2)
bpy.context.collection.objects.link(cam)
bpy.context.scene.camera = cam

target = bpy.data.objects.new("CameraTarget", None)
target.location = (0.4, 0.0, 3.0)
bpy.context.collection.objects.link(target)
track = cam.constraints.new(type='TRACK_TO')
track.target = target
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'

bpy.context.view_layer.update()
print("Streetlight scene built: %d objects" % len(bpy.context.collection.objects))
