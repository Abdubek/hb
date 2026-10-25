import bpy
import bmesh
import math
from mathutils import Vector


def make_material(name, color, metallic=0.0, roughness=0.5):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def add_box(name, dims, loc, mat, rot=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    ob.scale = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(mat)
    return ob


def add_cyl(name, radius, height, loc, mat, rot=(0.0, 0.0, 0.0), verts=24):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=height, vertices=verts,
                                        location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    for poly in ob.data.polygons:
        poly.use_smooth = True
    ob.data.materials.append(mat)
    return ob


def make_basin(name, mat, loc, r_top=0.21, r_bottom=0.13, depth=0.17, wall=0.015):
    """Solid cone shell hollowed out by insetting and pushing down the top face."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=32,
                          radius1=r_bottom, radius2=r_top, depth=depth)
    top = max(bm.faces, key=lambda f: f.calc_center_median().z)
    bmesh.ops.inset_individual(bm, faces=[top], thickness=wall, depth=0.0)
    bmesh.ops.translate(bm, verts=list(top.verts), vec=(0.0, 0.0, -(depth - wall)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for poly in me.polygons:
        poly.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    ob.location = loc
    ob.data.materials.append(mat)
    return ob


def boolean_cut(target, cutter, name="SinkCut"):
    mod = target.modifiers.new(name, 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = cutter
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


def aim(ob, target):
    direction = Vector(target) - ob.location
    ob.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


# --- materials -------------------------------------------------------------
walnut = make_material("VanityWalnut", (0.24, 0.13, 0.07), 0.0, 0.45)
stone = make_material("StoneTop", (0.86, 0.85, 0.82), 0.0, 0.25)
porcelain = make_material("Porcelain", (0.96, 0.96, 0.94), 0.0, 0.15)
chrome = make_material("Chrome", (0.87, 0.88, 0.90), 1.0, 0.07)
mirror = make_material("MirrorGlass", (0.92, 0.94, 0.96), 1.0, 0.02)
wall_mat = make_material("WallPaint", (0.80, 0.82, 0.81), 0.0, 0.75)
tile = make_material("FloorTile", (0.35, 0.36, 0.38), 0.0, 0.35)
glass = make_material("FrostedGlass", (0.95, 0.95, 0.90), 0.0, 0.35)

# --- room shell ------------------------------------------------------------
add_box("Floor", (4.0, 3.0, 0.06), (0.0, 0.6, -0.03), tile)
add_box("BackWall", (4.0, 0.10, 2.6), (0.0, 0.35, 1.30), wall_mat)

# --- cabinet ---------------------------------------------------------------
cab_w, cab_d, cab_h = 1.40, 0.52, 0.72
cab_z = 0.10 + cab_h / 2.0
add_box("ToeKick", (cab_w - 0.10, cab_d - 0.10, 0.10), (0.0, 0.06, 0.05), walnut)
add_box("CabinetCarcass", (cab_w, cab_d, cab_h), (0.0, 0.04, cab_z), walnut)

for tag, x in (("L", -0.35), ("R", 0.35)):
    add_box("Door_" + tag, (0.66, 0.03, 0.66), (x, -0.23, cab_z), walnut)
    handle_x = x + (0.28 if tag == "L" else -0.28)
    add_cyl("DoorHandle_" + tag, 0.010, 0.18, (handle_x, -0.255, cab_z), chrome, verts=12)

# --- countertop with basin cut-out ----------------------------------------
top_z = 0.10 + cab_h + 0.02
counter = add_box("Countertop", (1.50, 0.58, 0.04), (0.0, 0.02, top_z), stone)
add_box("Backsplash", (1.50, 0.03, 0.10), (0.0, 0.29, top_z + 0.07), stone)

bpy.ops.mesh.primitive_cylinder_add(radius=0.185, depth=0.4, vertices=32,
                                    location=(0.0, 0.0, top_z))
cutter = bpy.context.object
cutter.name = "BasinCutter"
boolean_cut(counter, cutter)

make_basin("SinkBasin", porcelain, (0.0, 0.0, top_z - 0.10))
add_cyl("DrainRing", 0.024, 0.012, (0.0, 0.0, top_z - 0.182), chrome, verts=18)
add_cyl("PTrap", 0.022, 0.22, (0.0, 0.0, top_z - 0.30), chrome, verts=16)

# --- faucet ----------------------------------------------------------------
faucet_y = 0.20
add_cyl("FaucetBase", 0.035, 0.022, (0.0, faucet_y, top_z + 0.03), chrome, verts=24)
add_cyl("FaucetRiser", 0.020, 0.24, (0.0, faucet_y, top_z + 0.16), chrome, verts=20)
add_cyl("FaucetElbow", 0.020, 0.020, (0.0, faucet_y, top_z + 0.28), chrome, verts=20)
add_cyl("FaucetSpout", 0.018, 0.20, (0.0, faucet_y - 0.10, top_z + 0.28), chrome,
        rot=(math.radians(90), 0.0, 0.0), verts=20)
add_cyl("FaucetNozzle", 0.016, 0.05, (0.0, faucet_y - 0.19, top_z + 0.26), chrome, verts=18)

for tag, x in (("Hot", -0.19), ("Cold", 0.19)):
    add_cyl("ValveBase_" + tag, 0.026, 0.02, (x, faucet_y, top_z + 0.03), chrome, verts=18)
    add_cyl("ValveLever_" + tag, 0.010, 0.11, (x, faucet_y - 0.045, top_z + 0.06), chrome,
            rot=(math.radians(70), 0.0, 0.0), verts=10)

# --- mirror and wall light -------------------------------------------------
mirror_z = 1.62
add_box("MirrorFrame", (1.00, 0.05, 0.86), (0.0, 0.28, mirror_z), walnut)
add_box("MirrorGlassPanel", (0.92, 0.01, 0.78), (0.0, 0.25, mirror_z), mirror)
add_box("VanityLightBar", (0.60, 0.06, 0.05), (0.0, 0.28, 2.14), chrome)
for i in range(3):
    add_cyl("LightShade_%d" % i, 0.055, 0.10, (-0.22 + i * 0.22, 0.28, 2.06), glass, verts=18)

# --- small props -----------------------------------------------------------
add_cyl("SoapDispenser", 0.035, 0.14, (-0.52, 0.05, top_z + 0.09), porcelain, verts=20)
add_cyl("SoapPump", 0.008, 0.06, (-0.52, 0.05, top_z + 0.18), chrome, verts=10)
add_cyl("TumblerCup", 0.038, 0.10, (0.52, 0.06, top_z + 0.07), glass, verts=20)
add_box("FoldedTowel", (0.26, 0.18, 0.06), (0.50, -0.10, top_z + 0.05),
        make_material("TowelCotton", (0.75, 0.78, 0.80), 0.0, 0.9))

# --- lighting and camera ---------------------------------------------------
bpy.ops.object.light_add(type='AREA', location=(0.0, -0.6, 2.25))
key = bpy.context.object
key.name = "KeyLight"
key.data.energy = 220.0
key.data.size = 1.6
aim(key, (0.0, 0.05, 1.0))

bpy.ops.object.light_add(type='AREA', location=(1.8, -1.6, 1.9))
fill = bpy.context.object
fill.name = "FillLight"
fill.data.energy = 90.0
fill.data.size = 1.2
aim(fill, (0.0, 0.0, 1.1))

bpy.ops.object.camera_add(location=(1.55, -2.05, 1.70))
cam = bpy.context.object
cam.name = "SceneCamera"
cam.data.lens = 42.0
aim(cam, (0.0, 0.05, 1.10))
bpy.context.scene.camera = cam
