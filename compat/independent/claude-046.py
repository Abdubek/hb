import bpy
import bmesh
import math
from mathutils import Vector


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in list(coll):
            if item.users == 0:
                coll.remove(item)


def mat(name, color, rough=0.5, metal=0.0):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m


def box(name, size, loc, material):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.scale = size
    ob.data.materials.append(material)
    return ob


def cyl(name, radius, depth, loc, material, verts=24, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=verts,
                                        location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    ob.data.materials.append(material)
    return ob


def beveled_slab(name, size, loc, material, bevel=0.02):
    """Cap slab with softened edges, built with bmesh."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges), offset=bevel,
                    segments=2, affect='EDGES')
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.data.materials.append(material)
    bpy.context.collection.objects.link(ob)
    return ob


def add_camera(loc, target, lens=38.0):
    cam = bpy.data.objects.new("BoothCamera", bpy.data.cameras.new("BoothCamera"))
    cam.data.lens = lens
    cam.location = loc
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    return cam


clear_scene()

M_CARPET = mat("Booth_Carpet", (0.06, 0.07, 0.09), rough=0.9)
M_PANEL = mat("Booth_PanelWhite", (0.86, 0.86, 0.84), rough=0.55)
M_ALU = mat("Booth_Aluminium", (0.72, 0.73, 0.75), rough=0.35, metal=1.0)
M_ACCENT = mat("Booth_AccentOrange", (0.85, 0.31, 0.06), rough=0.45)
M_WOOD = mat("Booth_CounterOak", (0.42, 0.27, 0.14), rough=0.6)
M_PRODUCT = mat("Booth_ProductGloss", (0.15, 0.35, 0.55), rough=0.15, metal=0.3)

# --- floor platform ------------------------------------------------------
box("Booth_FloorDeck", (8.4, 6.4, 0.12), (0.0, 0.0, -0.06), M_CARPET)

# --- modular back wall: repeated 1 m panels in an aluminium frame --------
PANEL_W, PANEL_H, PANEL_T = 0.98, 3.0, 0.08
for i in range(8):
    x = -3.5 + i * 1.0
    box("Booth_BackPanel_%02d" % (i + 1), (PANEL_W, PANEL_T, PANEL_H),
        (x, 3.0, PANEL_H / 2.0), M_PANEL)
for i in range(9):
    x = -4.0 + i * 1.0
    cyl("Booth_BackPost_%02d" % (i + 1), 0.05, PANEL_H + 0.1,
        (x, 3.0, (PANEL_H + 0.1) / 2.0), M_ALU)

# --- modular side wall ---------------------------------------------------
for i in range(5):
    y = -1.0 + i * 1.0
    box("Booth_SidePanel_%02d" % (i + 1), (PANEL_T, PANEL_W, PANEL_H),
        (-4.0, y, PANEL_H / 2.0), M_PANEL)
for i in range(6):
    y = -1.5 + i * 1.0
    cyl("Booth_SidePost_%02d" % (i + 1), 0.05, PANEL_H + 0.1,
        (-4.0, y, (PANEL_H + 0.1) / 2.0), M_ALU)

# --- header beam and signage --------------------------------------------
box("Booth_HeaderBeam", (8.2, 0.16, 0.22), (0.0, 3.0, 3.2), M_ALU)
box("Booth_SignBoard", (4.4, 0.1, 0.8), (0.0, 2.88, 3.85), M_ACCENT)
for i in range(4):
    box("Booth_SignBlock_%02d" % (i + 1), (0.5, 0.06, 0.34),
        (-1.5 + i * 1.0, 2.8, 3.85), M_PANEL)
cyl("Booth_SignMast_L", 0.05, 0.9, (-2.0, 2.98, 3.4), M_ALU)
cyl("Booth_SignMast_R", 0.05, 0.9, (2.0, 2.98, 3.4), M_ALU)

# --- display plinths with products --------------------------------------
PLINTHS = [
    ("A", (-2.4, 0.6), 0.95, 0.55, "sphere"),
    ("B", (0.0, 1.1), 1.10, 0.60, "cylinder"),
    ("C", (2.4, 0.6), 0.85, 0.55, "cone"),
]
for tag, (px, py), height, footprint, kind in PLINTHS:
    box("Plinth_%s_Body" % tag, (footprint, footprint, height), (px, py, height / 2.0), M_PANEL)
    box("Plinth_%s_Reveal" % tag, (footprint * 0.92, footprint * 0.92, 0.05),
        (px, py, 0.06), M_ACCENT)
    beveled_slab("Plinth_%s_Cap" % tag, (footprint + 0.08, footprint + 0.08, 0.05),
                 (px, py, height + 0.025), M_ALU)
    if kind == "sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.17, segments=24, ring_count=12,
                                             location=(px, py, height + 0.22))
    elif kind == "cylinder":
        bpy.ops.mesh.primitive_cylinder_add(radius=0.13, depth=0.42, vertices=24,
                                            location=(px, py, height + 0.26))
    else:
        bpy.ops.mesh.primitive_cone_add(radius1=0.18, radius2=0.0, depth=0.42, vertices=24,
                                        location=(px, py, height + 0.26))
    prod = bpy.context.object
    prod.name = "Plinth_%s_Product" % tag
    prod.data.materials.append(M_PRODUCT)

# --- reception counter ---------------------------------------------------
box("Counter_Body", (1.8, 0.7, 1.05), (-2.9, -1.9, 0.525), M_PANEL)
box("Counter_Front", (1.84, 0.06, 0.6), (-2.9, -2.26, 0.5), M_ACCENT)
beveled_slab("Counter_Top", (1.95, 0.85, 0.06), (-2.9, -1.9, 1.08), M_WOOD)
box("Counter_Shelf", (1.6, 0.55, 0.05), (-2.9, -1.9, 0.45), M_ALU)

# --- lighting rails and spots -------------------------------------------
for i, x in enumerate((-2.6, 0.0, 2.6)):
    cyl("Booth_LightRail_%02d" % (i + 1), 0.04, 2.6, (x, 1.7, 3.3), M_ALU,
        rot=(math.radians(90), 0, 0))
    lamp = bpy.data.objects.new("Booth_Spot_%02d" % (i + 1), bpy.data.lights.new(
        "Booth_SpotData_%02d" % (i + 1), 'SPOT'))
    lamp.data.energy = 400.0
    lamp.data.spot_size = math.radians(65)
    lamp.location = (x, 1.4, 3.2)
    lamp.rotation_euler = (math.radians(28), 0, 0)
    bpy.context.collection.objects.link(lamp)

fill = bpy.data.objects.new("Booth_FillLight", bpy.data.lights.new("Booth_FillData", 'AREA'))
fill.data.energy = 300.0
fill.data.size = 6.0
fill.location = (2.0, -5.0, 5.0)
fill.rotation_euler = (math.radians(50), 0, math.radians(20))
bpy.context.collection.objects.link(fill)

add_camera((7.5, -8.5, 4.6), (-0.3, 0.6, 1.3))
bpy.context.scene.world = bpy.data.worlds.new("BoothWorld")
bpy.context.scene.world.use_nodes = True
bpy.context.scene.world.node_tree.nodes["Background"].inputs[1].default_value = 0.35
