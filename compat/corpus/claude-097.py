"""claude-097 - A refrigerator with shelves and an open door.

A top freezer refrigerator: steel wrapped cabinet, white liner, glass shelves,
a crisper drawer, door bins and a lower door swung open on an empty acting as
the hinge.  Lit for a three quarter front-left view that looks into the
compartment.
"""

import bpy
import bmesh
import math
from mathutils import Vector


# --------------------------------------------------------------------------
# generic helpers
# --------------------------------------------------------------------------
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = 'METRIC'


def make_world(color=(0.05, 0.05, 0.055), strength=1.0):
    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (*color, 1.0)
    bg.inputs[1].default_value = strength
    bpy.context.scene.world = world
    return world


def mat_pbr(name, color, metallic=0.0, roughness=0.5, alpha=1.0,
            emission=None, emit_strength=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission is not None and "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emit_strength
    if alpha < 1.0:
        bsdf.inputs["Alpha"].default_value = alpha
        try:
            mat.blend_method = 'BLEND'
        except Exception:
            pass
    return mat


def assign(obj, mat):
    if mat is not None:
        obj.data.materials.append(mat)
    return obj


def box(name, size, loc, mat=None, rot=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    ob.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return assign(ob, mat)


def cyl(name, radius, depth, loc, mat=None, rot=(0.0, 0.0, 0.0), verts=24):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth,
                                        vertices=verts, location=loc,
                                        rotation=rot)
    ob = bpy.context.object
    ob.name = name
    return assign(ob, mat)


def bevel(obj, width=0.005, segments=2, angle=40.0):
    m = obj.modifiers.new("Bevel", 'BEVEL')
    m.width = width
    m.segments = segments
    m.limit_method = 'ANGLE'
    m.angle_limit = math.radians(angle)
    return obj


def smooth(obj, angle=35.0):
    try:
        for o in bpy.context.selected_objects:
            o.select_set(False)
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.shade_auto_smooth(angle=math.radians(angle))
    except Exception:
        for p in obj.data.polygons:
            p.use_smooth = True
    return obj


def look_at(obj, target):
    d = Vector(target) - obj.location
    obj.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


# --------------------------------------------------------------------------
# dimensions
# --------------------------------------------------------------------------
W = 0.72          # cabinet width
D = 0.70          # cabinet depth
H = 1.78          # cabinet height
XL, XR = -W / 2, W / 2
YF, YB = -D / 2, D / 2
WALLT = 0.05      # cabinet wall thickness
DIV_Z = 1.245     # freezer / fridge divider centre


def build_materials():
    return {
        "steel": mat_pbr("BrushedSteel", (0.58, 0.595, 0.615), 1.0, 0.26),
        "steel_dark": mat_pbr("DarkSteel", (0.20, 0.21, 0.22), 1.0, 0.40),
        "liner": mat_pbr("Liner", (0.90, 0.905, 0.90), 0.0, 0.42),
        "liner_warm": mat_pbr("LinerWarm", (0.86, 0.87, 0.87), 0.0, 0.50),
        "gasket": mat_pbr("Gasket", (0.80, 0.80, 0.79), 0.0, 0.72),
        "glass": mat_pbr("ShelfGlass", (0.72, 0.80, 0.80), 0.0, 0.06, alpha=0.30),
        "plastic": mat_pbr("ClearPlastic", (0.78, 0.82, 0.83), 0.0, 0.18,
                           alpha=0.45),
        "trim": mat_pbr("ShelfTrim", (0.30, 0.31, 0.33), 0.4, 0.40),
        "chrome": mat_pbr("Chrome", (0.87, 0.88, 0.90), 1.0, 0.12),
        "lamp": mat_pbr("LampPanel", (0.95, 0.95, 0.92), 0.0, 0.30,
                        emission=(1.0, 0.97, 0.90), emit_strength=6.0),
        "floor": mat_pbr("Floor", (0.24, 0.23, 0.22), 0.0, 0.48),
        "wall": mat_pbr("Wall", (0.80, 0.79, 0.77), 0.0, 0.88),
        "milk": mat_pbr("Carton", (0.90, 0.90, 0.88), 0.0, 0.55),
        "juice": mat_pbr("Juice", (0.75, 0.30, 0.10), 0.0, 0.30),
        "green": mat_pbr("Produce", (0.28, 0.45, 0.18), 0.0, 0.55),
    }


# --------------------------------------------------------------------------
# cabinet
# --------------------------------------------------------------------------
def build_cabinet(M):
    parts = []

    base = box("Base", (W, D, 0.09), (0.0, 0.0, 0.045), M["steel_dark"])
    bevel(base, 0.005, 2)
    parts.append(base)

    for sx, tag in ((-1, "L"), (1, "R")):
        side = box("Side_%s" % tag, (WALLT, D, H - 0.09),
                   (sx * (W / 2 - WALLT / 2), 0.0, 0.09 + (H - 0.09) / 2),
                   M["steel"])
        bevel(side, 0.006, 3)
        smooth(side)
        parts.append(side)

    back = box("Back", (W - 2 * WALLT, WALLT, H - 0.09),
               (0.0, YB - WALLT / 2, 0.09 + (H - 0.09) / 2), M["steel"])
    parts.append(back)

    top = box("Top", (W, D, 0.06), (0.0, 0.0, H - 0.03), M["steel"])
    bevel(top, 0.006, 3)
    smooth(top)
    parts.append(top)

    div = box("Divider", (W - 2 * WALLT, D - WALLT, 0.055),
              (0.0, -WALLT / 2, DIV_Z), M["liner"])
    bevel(div, 0.004, 2)
    parts.append(div)

    # white liner for the fresh food compartment
    ix = W / 2 - WALLT - 0.008
    iz0, iz1 = 0.095, DIV_Z - 0.028
    for sx, tag in ((-1, "L"), (1, "R")):
        parts.append(box("LinerSide_%s" % tag, (0.012, D - WALLT - 0.01,
                                                iz1 - iz0),
                         (sx * ix, -WALLT / 2 - 0.005, (iz0 + iz1) / 2),
                         M["liner"]))
    parts.append(box("LinerBack", (2 * ix, 0.012, iz1 - iz0),
                     (0.0, YB - WALLT - 0.006, (iz0 + iz1) / 2),
                     M["liner_warm"]))
    parts.append(box("LinerFloor", (2 * ix, D - WALLT - 0.01, 0.012),
                     (0.0, -WALLT / 2 - 0.005, iz0 + 0.006), M["liner"]))

    # moulded shelf ladders on the liner side walls
    for sx in (-1, 1):
        for i in range(6):
            parts.append(box("Ladder_%d_%d" % (sx + 1, i),
                             (0.010, 0.34, 0.012),
                             (sx * (ix - 0.008), -0.02, 0.34 + i * 0.16),
                             M["trim"]))

    # interior lamp housing at the top of the compartment
    hous = box("LampHousing", (0.26, 0.16, 0.05),
               (0.0, YB - 0.14, iz1 - 0.045), M["liner"])
    bevel(hous, 0.006, 2)
    parts.append(hous)
    parts.append(box("LampPanel", (0.22, 0.12, 0.010),
                     (0.0, YB - 0.14, iz1 - 0.072), M["lamp"]))

    light_data = bpy.data.lights.new("FridgeLamp", 'POINT')
    light_data.energy = 22.0
    light_data.color = (1.0, 0.95, 0.85)
    light_data.shadow_soft_size = 0.06
    lamp = bpy.data.objects.new("FridgeLamp", light_data)
    lamp.location = (0.0, YB - 0.16, iz1 - 0.09)
    bpy.context.collection.objects.link(lamp)
    parts.append(lamp)
    return parts


def build_shelves(M):
    parts = []
    ix = W / 2 - WALLT - 0.020
    depth = D - WALLT - 0.06
    cy = -WALLT / 2 - 0.02
    for i, z in enumerate((0.52, 0.79, 1.06)):
        sh = box("Shelf_%d" % i, (2 * ix, depth, 0.012), (0.0, cy, z),
                 M["glass"])
        parts.append(sh)
        trim = box("ShelfTrim_%d" % i, (2 * ix + 0.006, 0.018, 0.026),
                   (0.0, cy - depth / 2 - 0.004, z), M["trim"])
        bevel(trim, 0.004, 2)
        parts.append(trim)

    # crisper drawer under the lowest shelf
    dz = 0.30
    drawer_front = box("CrisperFront", (2 * ix - 0.02, 0.016, 0.20),
                       (0.0, cy - depth / 2 + 0.01, dz), M["plastic"])
    bevel(drawer_front, 0.005, 2)
    parts.append(drawer_front)
    parts.append(box("CrisperBody", (2 * ix - 0.03, depth - 0.05, 0.19),
                     (0.0, cy + 0.02, dz - 0.005), M["plastic"]))
    parts.append(box("CrisperRail", (2 * ix - 0.01, depth - 0.02, 0.014),
                     (0.0, cy, dz + 0.115), M["trim"]))

    # a little food to give the compartment scale
    parts.append(box("Carton", (0.09, 0.09, 0.24), (-0.18, cy + 0.02, 0.925),
                     M["milk"]))
    j = cyl("Jug", 0.055, 0.20, (0.02, cy + 0.05, 0.905), M["juice"], verts=20)
    smooth(j)
    parts.append(j)
    b = cyl("Bowl", 0.085, 0.07, (0.16, cy - 0.02, 1.13), M["liner"], verts=24)
    smooth(b)
    parts.append(b)
    parts.append(box("Produce", (0.16, 0.16, 0.10), (-0.10, cy, 0.34),
                     M["green"]))
    return parts


# --------------------------------------------------------------------------
# doors
# --------------------------------------------------------------------------
def build_lower_door(M):
    """Door built in the closed position, then parented to a hinge empty."""
    parts = []
    z0, z1 = 0.10, DIV_Z - 0.045
    zc = (z0 + z1) / 2
    dh = z1 - z0
    y_out = YF - 0.062

    panel = box("DoorPanel", (W, 0.062, dh), (0.0, y_out + 0.031, zc),
                M["steel"])
    bevel(panel, 0.007, 3)
    smooth(panel)
    parts.append(panel)

    liner = box("DoorLiner", (W - 0.02, 0.055, dh - 0.02),
                (0.0, YF - 0.028, zc), M["liner"])
    bevel(liner, 0.006, 2)
    parts.append(liner)

    # magnetic gasket frame around the liner
    gy = YF - 0.004
    parts.append(box("GasketTop", (W - 0.03, 0.030, 0.030),
                     (0.0, gy, z1 - 0.025), M["gasket"]))
    parts.append(box("GasketBot", (W - 0.03, 0.030, 0.030),
                     (0.0, gy, z0 + 0.025), M["gasket"]))
    for sx in (-1, 1):
        parts.append(box("GasketSide_%d" % (sx + 1), (0.030, 0.030, dh - 0.08),
                         (sx * (W / 2 - 0.025), gy, zc), M["gasket"]))

    # three door bins
    for i, bz in enumerate((0.34, 0.66, 0.98)):
        bw = W - 0.10
        parts.append(box("BinFloor_%d" % i, (bw, 0.085, 0.012),
                         (0.0, YF + 0.030, bz), M["plastic"]))
        f = box("BinFront_%d" % i, (bw, 0.014, 0.13),
                (0.0, YF + 0.072, bz + 0.062), M["plastic"])
        bevel(f, 0.004, 2)
        parts.append(f)
        for sx in (-1, 1):
            parts.append(box("BinEnd_%d_%d" % (i, sx + 1), (0.014, 0.085, 0.13),
                             (sx * bw / 2, YF + 0.030, bz + 0.062),
                             M["plastic"]))
    # bottles in the lowest bin
    for i, x in enumerate((-0.22, -0.10, 0.06)):
        bt = cyl("Bottle_%d" % i, 0.033, 0.24, (x, YF + 0.030, 0.34 + 0.13),
                 M["juice"] if i % 2 else M["milk"], verts=16)
        smooth(bt)
        parts.append(bt)

    # vertical bar handle on the outside face
    hx = XL + 0.10
    for sz in (-1, 1):
        st = box("HandleStandoff_%d" % (sz + 1), (0.045, 0.055, 0.045),
                 (hx, y_out - 0.028, zc + sz * 0.28), M["chrome"])
        bevel(st, 0.005, 3)
        smooth(st)
        parts.append(st)
    bar = cyl("DoorHandle", 0.017, 0.66, (hx, y_out - 0.062, zc), M["chrome"],
              rot=(0.0, 0.0, 0.0), verts=24)
    smooth(bar)
    parts.append(bar)

    # hinge empty at the right front vertical edge
    hinge = bpy.data.objects.new("DoorHinge", None)
    hinge.empty_display_type = 'PLAIN_AXES'
    hinge.empty_display_size = 0.15
    bpy.context.collection.objects.link(hinge)
    hinge.location = (XR - 0.01, YF - 0.02, zc)
    bpy.context.view_layer.update()

    inv = hinge.matrix_world.inverted()
    for ob in parts:
        ob.parent = hinge
        ob.matrix_parent_inverse = inv
    hinge.rotation_euler = (0.0, 0.0, math.radians(112.0))
    parts.append(hinge)
    return parts


def build_freezer_door(M):
    parts = []
    z0, z1 = DIV_Z + 0.020, H - 0.02
    zc = (z0 + z1) / 2
    dh = z1 - z0
    panel = box("FreezerDoor", (W, 0.062, dh), (0.0, YF - 0.031, zc),
                M["steel"])
    bevel(panel, 0.007, 3)
    smooth(panel)
    parts.append(panel)

    hz = z0 + 0.09
    for sx in (-1, 1):
        st = box("FzStandoff_%d" % (sx + 1), (0.045, 0.055, 0.045),
                 (sx * 0.26, YF - 0.090, hz), M["chrome"])
        bevel(st, 0.005, 3)
        smooth(st)
        parts.append(st)
    bar = cyl("FreezerHandle", 0.017, 0.60, (0.0, YF - 0.124, hz), M["chrome"],
              rot=(0.0, math.radians(90), 0.0), verts=24)
    smooth(bar)
    parts.append(bar)

    # brand badge
    parts.append(box("Badge", (0.14, 0.008, 0.022), (0.0, YF - 0.064, z0 + 0.26),
                     M["chrome"]))
    return parts


def build_room(M):
    parts = []
    bpy.ops.mesh.primitive_plane_add(size=10.0, location=(0.0, 0.0, 0.0))
    floor = bpy.context.object
    floor.name = "Floor"
    assign(floor, M["floor"])
    parts.append(floor)
    parts.append(box("Wall", (6.0, 0.10, 3.0), (0.0, YB + 0.10, 1.5), M["wall"]))
    parts.append(box("SideWall", (0.10, 4.0, 3.0), (1.9, YB - 1.6, 1.5),
                     M["wall"]))
    return parts


def build_lighting():
    key_data = bpy.data.lights.new("Key", 'AREA')
    key_data.energy = 500.0
    key_data.size = 2.6
    key = bpy.data.objects.new("KeyLight", key_data)
    key.location = (-2.4, -2.6, 3.2)
    bpy.context.collection.objects.link(key)
    look_at(key, (0.0, -0.2, 1.0))

    fill_data = bpy.data.lights.new("Fill", 'AREA')
    fill_data.energy = 140.0
    fill_data.size = 2.2
    fill = bpy.data.objects.new("FillLight", fill_data)
    fill.location = (2.8, -2.4, 1.5)
    bpy.context.collection.objects.link(fill)
    look_at(fill, (0.2, -0.3, 1.0))

    rim_data = bpy.data.lights.new("Rim", 'AREA')
    rim_data.energy = 120.0
    rim_data.size = 1.4
    rim = bpy.data.objects.new("RimLight", rim_data)
    rim.location = (-1.8, 1.4, 2.6)
    bpy.context.collection.objects.link(rim)
    look_at(rim, (-0.2, 0.0, 1.3))


def build_camera():
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = 40.0
    cam = bpy.data.objects.new("Camera", cam_data)
    cam.location = (-2.05, -2.55, 1.85)
    bpy.context.collection.objects.link(cam)
    look_at(cam, (-0.05, -0.10, 0.98))
    bpy.context.scene.camera = cam
    return cam


def main():
    reset_scene()
    make_world((0.055, 0.057, 0.062), 1.0)
    M = build_materials()

    objs = []
    objs += build_room(M)
    objs += build_cabinet(M)
    objs += build_shelves(M)
    objs += build_lower_door(M)
    objs += build_freezer_door(M)

    build_lighting()
    build_camera()

    print("claude-097: refrigerator built with %d objects" % len(objs))


if __name__ == "__main__":
    main()
