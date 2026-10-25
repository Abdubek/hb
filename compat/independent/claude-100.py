import bpy
import bmesh
from mathutils import Vector

# ---------------------------------------------------------------- utilities

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras):
        for item in block:
            if item.users == 0:
                block.remove(item)


def make_material(name, color, roughness=0.6, metallic=0.0):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return mat


def add_box(name, size, location, material, parent=None):
    """Box given by full dimensions, centred on `location`."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    obj.data.materials.append(material)
    bpy.context.collection.objects.link(obj)
    if parent:
        obj.parent = parent
    return obj


def add_cylinder(name, radius, depth, location, material, rotation=(0, 0, 0), parent=None):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16,
                          radius1=radius, radius2=radius, depth=depth)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    obj.rotation_euler = rotation
    obj.data.materials.append(material)
    bpy.context.collection.objects.link(obj)
    if parent:
        obj.parent = parent
    return obj


def new_empty(name, location=(0, 0, 0)):
    e = bpy.data.objects.new(name, None)
    e.empty_display_size = 0.4
    e.location = location
    bpy.context.collection.objects.link(e)
    return e


# ---------------------------------------------------------------- materials

clear_scene()

MAT_CONCRETE = make_material("Concrete", (0.62, 0.61, 0.58), roughness=0.85)
MAT_ASPHALT = make_material("Asphalt", (0.16, 0.16, 0.17), roughness=0.95)
MAT_STEEL = make_material("PaintedSteel", (0.24, 0.30, 0.36), roughness=0.35, metallic=0.9)
MAT_PANEL = make_material("CanopyPanel", (0.72, 0.82, 0.85), roughness=0.12)
MAT_WOOD = make_material("BenchWood", (0.46, 0.29, 0.15), roughness=0.7)
MAT_YELLOW = make_material("SafetyLine", (0.92, 0.72, 0.10), roughness=0.6)
MAT_RAIL = make_material("Rail", (0.35, 0.33, 0.31), roughness=0.4, metallic=1.0)
MAT_SIGN = make_material("SignFace", (0.05, 0.22, 0.45), roughness=0.4)

PLATFORM_L = 14.0
PLATFORM_W = 4.4
PLATFORM_H = 0.55

# ---------------------------------------------------------------- ground & platform

station = new_empty("Station")

add_box("Ground", (30.0, 20.0, 0.1), (0, 0, -0.05), MAT_ASPHALT, station)
add_box("Platform_Deck", (PLATFORM_L, PLATFORM_W, PLATFORM_H),
        (0, 0, PLATFORM_H / 2), MAT_CONCRETE, station)

# tactile warning strip along the track edge
add_box("Platform_SafetyLine", (PLATFORM_L, 0.45, 0.03),
        (0, -PLATFORM_W / 2 + 0.35, PLATFORM_H + 0.015), MAT_YELLOW, station)

# track bed with two rails on the boarding side
add_box("Track_Bed", (PLATFORM_L + 6.0, 3.0, 0.2),
        (0, -PLATFORM_W / 2 - 1.8, 0.1), MAT_ASPHALT, station)
for i, y_off in enumerate((-1.0, 0.44)):
    add_box("Rail_%d" % (i + 1), (PLATFORM_L + 6.0, 0.12, 0.16),
            (0, -PLATFORM_W / 2 - 1.8 + y_off, 0.28), MAT_RAIL, station)

# access steps at the far end
for i in range(3):
    add_box("Step_%d" % (i + 1), (2.4, 0.4, PLATFORM_H),
            (PLATFORM_L / 2 + 0.2 + i * 0.4, 1.2, PLATFORM_H / 2 - (i + 1) * 0.14),
            MAT_CONCRETE, station)

# ---------------------------------------------------------------- canopy

canopy = new_empty("Canopy")
canopy.parent = station

COL_Y = 1.3
COL_H = 2.9
ROOF_Z = PLATFORM_H + COL_H

for i, x in enumerate((-4.2, 0.0, 4.2)):
    add_cylinder("Canopy_Column_%d" % (i + 1), 0.09, COL_H,
                 (x, COL_Y, PLATFORM_H + COL_H / 2), MAT_STEEL, parent=canopy)
    # cantilever bracket reaching out over the platform
    add_box("Canopy_Bracket_%d" % (i + 1), (0.12, 2.6, 0.14),
            (x, COL_Y - 1.3, ROOF_Z - 0.1), MAT_STEEL, canopy)

for i, y in enumerate((COL_Y, COL_Y - 2.4)):
    add_box("Canopy_Beam_%d" % (i + 1), (10.4, 0.14, 0.22),
            (0, y, ROOF_Z + 0.05), MAT_STEEL, canopy)

# roof deck, slightly tilted so rain runs off toward the track
roof = add_box("Canopy_Roof", (10.8, 3.4, 0.08),
               (0, COL_Y - 1.2, ROOF_Z + 0.24), MAT_PANEL, canopy)
roof.rotation_euler = (0.07, 0, 0)

add_box("Canopy_Fascia", (10.8, 0.1, 0.24),
        (0, COL_Y - 2.85, ROOF_Z + 0.18), MAT_STEEL, canopy)

# ---------------------------------------------------------------- benches


def build_bench(name, x, y):
    grp = new_empty(name, (x, y, 0))
    grp.parent = station
    seat_z = PLATFORM_H + 0.45
    for i, sx in enumerate((-0.75, 0.75)):
        add_box("%s_Leg_%d" % (name, i + 1), (0.08, 0.5, 0.45),
                (x + sx, y, PLATFORM_H + 0.225), MAT_STEEL, grp)
    for i in range(3):
        add_box("%s_Slat_%d" % (name, i + 1), (1.9, 0.14, 0.05),
                (x, y - 0.18 + i * 0.18, seat_z), MAT_WOOD, grp)
    for i, sx in enumerate((-0.75, 0.75)):
        add_box("%s_BackPost_%d" % (name, i + 1), (0.07, 0.07, 0.55),
                (x + sx, y + 0.24, seat_z + 0.25), MAT_STEEL, grp)
    for i in range(2):
        add_box("%s_Back_%d" % (name, i + 1), (1.9, 0.05, 0.13),
                (x, y + 0.24, seat_z + 0.2 + i * 0.18), MAT_WOOD, grp)
    return grp


build_bench("Bench_A", -3.2, 1.05)
build_bench("Bench_B", 2.6, 1.05)

# ---------------------------------------------------------------- sign & litter bin

sign = new_empty("Sign")
sign.parent = station
add_cylinder("Sign_Post", 0.06, 2.4, (-6.0, 1.4, PLATFORM_H + 1.2), MAT_STEEL, parent=sign)
add_box("Sign_Board", (1.6, 0.08, 0.5), (-6.0, 1.4, PLATFORM_H + 2.1), MAT_SIGN, sign)

add_cylinder("Litter_Bin", 0.24, 0.8, (5.6, 1.5, PLATFORM_H + 0.4), MAT_STEEL, parent=station)
add_cylinder("Litter_Bin_Lid", 0.27, 0.06, (5.6, 1.5, PLATFORM_H + 0.83), MAT_RAIL, parent=station)

# ---------------------------------------------------------------- lighting & camera

sun_data = bpy.data.lights.new("SunLight", type='SUN')
sun_data.energy = 3.5
sun = bpy.data.objects.new("SunLight", sun_data)
sun.location = (8, 10, 14)
sun.rotation_euler = (0.9, 0.1, -2.3)
bpy.context.collection.objects.link(sun)

fill_data = bpy.data.lights.new("FillLight", type='AREA')
fill_data.energy = 300.0
fill_data.size = 8.0
fill = bpy.data.objects.new("FillLight", fill_data)
fill.location = (-8, -10, 7)
fill.rotation_euler = (1.0, 0, -0.7)
bpy.context.collection.objects.link(fill)

cam_data = bpy.data.cameras.new("StationCamera")
cam_data.lens = 35.0
cam = bpy.data.objects.new("StationCamera", cam_data)
cam.location = (13.5, -13.0, 8.0)
bpy.context.collection.objects.link(cam)

target = new_empty("CameraTarget", (0.0, 0.0, 1.6))
track = cam.constraints.new(type='TRACK_TO')
track.target = target
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'

bpy.context.scene.camera = cam
