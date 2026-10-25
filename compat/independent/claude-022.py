import bpy
import math
from mathutils import Vector


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


def make_material(name, color, roughness=0.5, metallic=0.0, alpha=1.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = (*color, alpha)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Alpha'].default_value = alpha
    if alpha < 1.0:
        mat.blend_method = 'BLEND'
    return mat


def assign(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    return obj


def cyl(name, radius, depth, location, mat, verts=32, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius,
                                        depth=depth, location=location,
                                        rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    bpy.ops.object.shade_smooth()
    return assign(obj, mat)


def cone(name, r1, r2, depth, location, mat, verts=32):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2,
                                    depth=depth, location=location)
    obj = bpy.context.active_object
    obj.name = name
    bpy.ops.object.shade_smooth()
    return assign(obj, mat)


def ring(name, major, minor, z, mat):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                     major_segments=36, minor_segments=10,
                                     location=(0, 0, z))
    obj = bpy.context.active_object
    obj.name = name
    bpy.ops.object.shade_smooth()
    return assign(obj, mat)


clear_scene()

steel = make_material('MAT_Steel', (0.62, 0.64, 0.67), roughness=0.32, metallic=1.0)
paint = make_material('MAT_RedPaint', (0.55, 0.07, 0.05), roughness=0.35)
glass = make_material('MAT_Globe', (0.85, 0.88, 0.90), roughness=0.05, alpha=0.22)
brass = make_material('MAT_Brass', (0.72, 0.53, 0.20), roughness=0.28, metallic=1.0)
ground_mat = make_material('MAT_Ground', (0.22, 0.21, 0.19), roughness=0.9)

bpy.ops.mesh.primitive_plane_add(size=3.0, location=(0, 0, 0))
bpy.context.active_object.name = 'Ground'
assign(bpy.context.active_object, ground_mat)

# --- body stack -----------------------------------------------------------
cone('Lantern_BaseFoot', 0.125, 0.100, 0.035, (0, 0, 0.018), paint)
cyl('Lantern_FuelTank', 0.098, 0.085, (0, 0, 0.078), paint)
cyl('Lantern_TankCollar', 0.082, 0.020, (0, 0, 0.130), steel)
cyl('Globe_Glass', 0.076, 0.155, (0, 0, 0.218), glass, verts=40)
cyl('Burner_Body', 0.030, 0.070, (0, 0, 0.175), brass, verts=20)
cone('Burner_Mantle', 0.026, 0.010, 0.045, (0, 0, 0.232), glass, verts=20)
cone('Lantern_Hood', 0.120, 0.062, 0.055, (0, 0, 0.323), paint)
cyl('Lantern_VentCap', 0.040, 0.030, (0, 0, 0.365), steel, verts=20)

# fuel valve knob sticking out of the tank
cyl('Fuel_Valve', 0.014, 0.055, (0.095, 0, 0.085), brass, verts=16,
    rot=(0, math.radians(90), 0))
cyl('Fuel_Knob', 0.028, 0.014, (0.128, 0, 0.085), paint, verts=20,
    rot=(0, math.radians(90), 0))

# --- protective frame around the globe ------------------------------------
ring('Frame_RingLower', 0.086, 0.006, 0.148, steel)
ring('Frame_RingUpper', 0.086, 0.006, 0.290, steel)

rod_r = 0.088
for i in range(4):
    a = math.radians(45 + i * 90)
    cyl('Frame_Rod_%d' % (i + 1), 0.006, 0.150,
        (rod_r * math.cos(a), rod_r * math.sin(a), 0.219), steel, verts=12)

# --- bail handle: arc built from short segments, then joined --------------
handle_pivot_z = 0.300
arc_r = 0.135
segments = 14
parts = []
for i in range(segments):
    a0 = math.pi * i / segments
    a1 = math.pi * (i + 1) / segments
    p0 = Vector((arc_r * math.cos(a0), 0.0, handle_pivot_z + arc_r * math.sin(a0)))
    p1 = Vector((arc_r * math.cos(a1), 0.0, handle_pivot_z + arc_r * math.sin(a1)))
    v = p1 - p0
    seg = cyl('Handle_Seg_%02d' % i, 0.0055, v.length, (p0 + p1) / 2.0,
              steel, verts=10)
    seg.rotation_euler = v.to_track_quat('Z', 'Y').to_euler()
    parts.append(seg)

bpy.ops.object.select_all(action='DESELECT')
for p in parts:
    p.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
handle = bpy.context.active_object
handle.name = 'Lantern_Handle'

for sx in (1, -1):
    cyl('Handle_Lug_%s' % ('R' if sx > 0 else 'L'), 0.012, 0.016,
        (sx * arc_r, 0, handle_pivot_z), steel, verts=16,
        rot=(math.radians(90), 0, 0))

# --- lighting and camera --------------------------------------------------
bpy.ops.object.light_add(type='AREA', location=(0.7, -0.8, 0.9))
key = bpy.context.active_object
key.name = 'Key_Light'
key.data.energy = 180
key.data.size = 1.2
key.rotation_euler = (Vector((0, 0, 0.25)) - key.location).to_track_quat('-Z', 'Y').to_euler()

bpy.ops.object.light_add(type='POINT', location=(0, 0, 0.21))
flame = bpy.context.active_object
flame.name = 'Mantle_Glow'
flame.data.energy = 12
flame.data.color = (1.0, 0.82, 0.55)

target = Vector((0, 0, 0.21))
bpy.ops.object.camera_add(location=(0.72, -0.86, 0.55))
cam = bpy.context.active_object
cam.name = 'Camera_Main'
cam.data.lens = 60
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam
