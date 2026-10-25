import bpy
import bmesh
import math
from mathutils import Vector


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in list(block):
            if item.users == 0:
                block.remove(item)


def make_material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def new_obj(name, material):
    obj = bpy.data.objects.new(name, bpy.data.meshes.new(name + "Mesh"))
    obj.data.materials.append(material)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def box(name, material, size, center, bevel=0.004):
    """Axis-aligned box with an optional small bevel for a molded look."""
    obj = new_obj(name, material)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= size[0]
        v.co.y *= size[1]
        v.co.z *= size[2]
    if bevel > 0.0:
        bmesh.ops.bevel(bm, geom=bm.verts[:] + bm.edges[:], offset=bevel,
                        segments=2, affect='EDGES', clamp_overlap=True)
    bm.to_mesh(obj.data)
    bm.free()
    obj.location = center
    return obj


def cup(name, material, outer, inner, height, center, segments=32):
    """Open-topped round cup: outer wall, inner bore, floor and rim."""
    obj = new_obj(name, material)
    bm = bmesh.new()
    profile = [(inner, 0.012), (inner, height), (outer, height), (outer, 0.0),
               (0.0, 0.0), (0.0, 0.012)]
    verts = [bm.verts.new((r, 0.0, z)) for r, z in profile]
    ring = verts + [verts[0]]
    for a, b in zip(ring, ring[1:]):
        bm.edges.new((a, b))
    bmesh.ops.spin(bm, geom=bm.verts[:] + bm.edges[:], axis=(0, 0, 1), cent=(0, 0, 0),
                   dupli=False, angle=2.0 * math.pi, steps=segments, use_merge=True)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(obj.data)
    bm.free()
    obj.location = center
    return obj


def pen(name, material, radius, length, base, tilt_deg, spin_deg):
    obj = new_obj(name, material)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=True, segments=12,
                          radius1=radius, radius2=radius, depth=length)
    bmesh.ops.translate(bm, verts=bm.verts, vec=(0.0, 0.0, length * 0.5))
    bm.to_mesh(obj.data)
    bm.free()
    obj.location = base
    obj.rotation_euler = (math.radians(tilt_deg), 0.0, math.radians(spin_deg))
    return obj


def add_light(name, energy, size, location, rotation):
    light = bpy.data.lights.new(name + "Data", 'AREA')
    light.energy = energy
    light.size = size
    obj = bpy.data.objects.new(name, light)
    obj.location = location
    obj.rotation_euler = rotation
    bpy.context.scene.collection.objects.link(obj)
    return obj


clear_scene()
scene = bpy.context.scene
scene.world = bpy.data.worlds.new("OrganizerWorld")
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.09, 0.10, 0.11, 1.0)

walnut = make_material("WalnutShell", (0.21, 0.11, 0.055), roughness=0.45)
cork = make_material("CorkLiner", (0.62, 0.47, 0.29), roughness=0.80)
steel = make_material("BrushedSteel", (0.62, 0.63, 0.65), roughness=0.32, metallic=1.0)
charcoal = make_material("CharcoalPlastic", (0.10, 0.10, 0.12), roughness=0.40)
paper = make_material("PaperStack", (0.92, 0.90, 0.86), roughness=0.72)
desk = make_material("DeskTop", (0.30, 0.28, 0.26), roughness=0.60)
accent = make_material("AccentRed", (0.62, 0.14, 0.12), roughness=0.45)
graphite = make_material("Graphite", (0.24, 0.24, 0.26), roughness=0.55)

box("DeskSurface", desk, (2.60, 1.80, 0.04), (0.0, 0.0, -0.02), bevel=0.0)

# Base plinth: everything sits on this one walnut slab.
BASE_T = 0.05
box("BasePlinth", walnut, (1.30, 0.70, BASE_T), (0.0, 0.0, BASE_T * 0.5))
box("BaseFootLeft", charcoal, (0.10, 0.55, 0.014), (-0.52, 0.0, 0.007), bevel=0.002)
box("BaseFootRight", charcoal, (0.10, 0.55, 0.014), (0.52, 0.0, 0.007), bevel=0.002)

# Paper tray: floor plus three walls, open toward the camera (-Y).
TRAY_W, TRAY_D, WALL, WALL_H = 0.74, 0.60, 0.022, 0.11
tray_x, tray_y = -0.26, 0.0
floor_z = BASE_T + 0.011
box("TrayFloor", walnut, (TRAY_W, TRAY_D, 0.022), (tray_x, tray_y, floor_z))
box("TrayWallBack", walnut, (TRAY_W, WALL, WALL_H),
    (tray_x, tray_y + TRAY_D * 0.5 - WALL * 0.5, floor_z + WALL_H * 0.5))
box("TrayWallLeft", walnut, (WALL, TRAY_D, WALL_H),
    (tray_x - TRAY_W * 0.5 + WALL * 0.5, tray_y, floor_z + WALL_H * 0.5))
box("TrayWallRight", walnut, (WALL, TRAY_D, WALL_H),
    (tray_x + TRAY_W * 0.5 - WALL * 0.5, tray_y, floor_z + WALL_H * 0.5))
box("TrayLipFront", walnut, (TRAY_W, WALL, 0.030),
    (tray_x, tray_y - TRAY_D * 0.5 + WALL * 0.5, floor_z + 0.015))
box("TrayLiner", cork, (TRAY_W - 2 * WALL, TRAY_D - 2 * WALL, 0.006),
    (tray_x, tray_y, floor_z + 0.014), bevel=0.0)

# A short stack of sheets, each nudged for a hand-placed look.
for i in range(4):
    box("PaperSheet%02d" % (i + 1), paper, (0.60, 0.46, 0.006),
        (tray_x + 0.006 * i, tray_y - 0.004 * i, floor_z + 0.021 + 0.0075 * i), bevel=0.0)

# Two round pen cups on a raised riser at the right end.
RISER_H = 0.06
box("CupRiser", walnut, (0.44, 0.62, RISER_H), (0.40, 0.0, BASE_T + RISER_H * 0.5))
cup_z = BASE_T + RISER_H
cup("PenCupTall", steel, 0.105, 0.093, 0.30, (0.32, 0.14, cup_z))
cup("PenCupShort", charcoal, 0.095, 0.083, 0.21, (0.47, -0.15, cup_z))

pen("PenBallpoint", charcoal, 0.010, 0.36, (0.30, 0.15, cup_z + 0.02), 7.0, 25.0)
pen("PenFountain", accent, 0.012, 0.34, (0.345, 0.125, cup_z + 0.02), -9.0, 200.0)
pen("PencilGraphite", graphite, 0.009, 0.31, (0.315, 0.175, cup_z + 0.02), 5.0, 120.0)
pen("MarkerWide", steel, 0.013, 0.26, (0.46, -0.14, cup_z + 0.02), 6.0, 300.0)
pen("PencilSpare", accent, 0.009, 0.24, (0.487, -0.168, cup_z + 0.02), -6.0, 60.0)

# Small parts tray tucked in front of the riser, plus a brand plate.
box("ClipTray", charcoal, (0.18, 0.16, 0.030), (0.16, -0.24, BASE_T + 0.015))
box("ClipTrayLiner", cork, (0.15, 0.13, 0.004), (0.16, -0.24, BASE_T + 0.031), bevel=0.0)
box("BrandPlate", steel, (0.14, 0.026, 0.004), (-0.26, -0.336, BASE_T * 0.5 + 0.010), bevel=0.001)

add_light("KeyLight", 300.0, 1.6, (0.9, -1.1, 1.5), (math.radians(42.0), 0.0, math.radians(38.0)))
add_light("FillLight", 90.0, 2.0, (-1.2, 0.9, 1.1), (math.radians(65.0), 0.0, math.radians(-125.0)))

cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("CameraData"))
cam.data.lens = 55.0
cam.location = (1.05, -1.30, 0.85)
scene.collection.objects.link(cam)
scene.camera = cam
cam.rotation_euler = (Vector((0.0, 0.0, 0.13)) - cam.location).to_track_quat('-Z', 'Y').to_euler()

print("Desk organizer scene built: %d objects" % len(scene.collection.objects))
