"""claude-096 - A kitchen range with burners, knobs and oven door.

Builds a free standing 30" gas range: steel body, cooktop with four sealed
burners and cast iron grates, a back guard with control knobs and a display,
and a glass oven door with a tubular handle.  Scene includes flanking
counters, a wall, three point lighting and a camera.
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
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'


def make_world(color=(0.045, 0.048, 0.055), strength=1.0):
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


def cyl(name, radius, depth, loc, mat=None, rot=(0.0, 0.0, 0.0), verts=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth,
                                        vertices=verts, location=loc,
                                        rotation=rot)
    ob = bpy.context.object
    ob.name = name
    return assign(ob, mat)


def cone(name, r1, r2, depth, loc, mat=None, rot=(0.0, 0.0, 0.0), verts=32):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=depth,
                                    vertices=verts, location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    return assign(ob, mat)


def torus(name, major, minor, loc, mat=None, rot=(0.0, 0.0, 0.0),
          maj_seg=40, min_seg=12):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                     major_segments=maj_seg,
                                     minor_segments=min_seg,
                                     location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    return assign(ob, mat)


def bevel(obj, width=0.004, segments=2, angle=40.0):
    m = obj.modifiers.new("Bevel", 'BEVEL')
    m.width = width
    m.segments = segments
    m.limit_method = 'ANGLE'
    m.angle_limit = math.radians(angle)
    m.harden_normals = False
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
# materials
# --------------------------------------------------------------------------
def build_materials():
    return {
        "steel": mat_pbr("SteelBrushed", (0.60, 0.615, 0.635), 1.0, 0.28),
        "steel_dark": mat_pbr("SteelDark", (0.30, 0.31, 0.33), 1.0, 0.40),
        "chrome": mat_pbr("Chrome", (0.86, 0.87, 0.89), 1.0, 0.10),
        "iron": mat_pbr("CastIron", (0.042, 0.042, 0.046), 0.25, 0.68),
        "glass": mat_pbr("OvenGlass", (0.012, 0.013, 0.016), 0.0, 0.07),
        "plastic": mat_pbr("KnobPlastic", (0.055, 0.055, 0.062), 0.0, 0.32),
        "white": mat_pbr("WhitePaint", (0.88, 0.88, 0.87), 0.0, 0.45),
        "display": mat_pbr("Display", (0.01, 0.02, 0.02), 0.0, 0.25,
                           emission=(0.10, 0.85, 0.80), emit_strength=3.0),
        "brass": mat_pbr("BurnerBrass", (0.62, 0.45, 0.20), 1.0, 0.42),
        "floor": mat_pbr("FloorTile", (0.26, 0.245, 0.235), 0.0, 0.45),
        "wall": mat_pbr("Wall", (0.83, 0.82, 0.79), 0.0, 0.85),
        "counter": mat_pbr("CounterTop", (0.14, 0.14, 0.15), 0.0, 0.30),
        "cabinet": mat_pbr("Cabinet", (0.72, 0.68, 0.61), 0.0, 0.55),
    }


# --------------------------------------------------------------------------
# range parts
# --------------------------------------------------------------------------
BODY_FRONT = -0.27
BODY_BACK = 0.39
COOKTOP_Z = 0.92


def build_carcass(M):
    parts = []
    body = box("RangeBody", (0.76, 0.66, 0.81), (0.0, 0.06, 0.495), M["steel"])
    bevel(body, 0.006, 3)
    smooth(body)
    parts.append(body)

    # levelling feet
    for sx in (-1, 1):
        for sy in (-1, 1):
            f = cyl("Foot", 0.024, 0.09,
                    (sx * 0.32, 0.06 + sy * 0.26, 0.045), M["steel_dark"], verts=16)
            smooth(f)
            parts.append(f)

    # cooktop slab, slightly proud of the body on every side
    top = box("Cooktop", (0.78, 0.68, 0.03), (0.0, 0.06, COOKTOP_Z - 0.015),
              M["steel"])
    bevel(top, 0.005, 3)
    smooth(top)
    parts.append(top)

    # shallow recessed spill tray on the cooktop
    tray = box("SpillTray", (0.72, 0.62, 0.012), (0.0, 0.06, COOKTOP_Z - 0.004),
               M["steel_dark"])
    bevel(tray, 0.004, 2)
    parts.append(tray)

    # bottom trim / kick strip under the oven door
    trim = box("BottomTrim", (0.74, 0.05, 0.035), (0.0, -0.295, 0.1075),
               M["steel_dark"])
    bevel(trim, 0.003, 2)
    parts.append(trim)
    return parts


def build_backguard(M):
    parts = []
    guard = box("BackGuard", (0.78, 0.07, 0.30), (0.0, 0.355, 1.08), M["steel"])
    bevel(guard, 0.006, 3)
    smooth(guard)
    parts.append(guard)

    face_y = 0.32

    # control panel inset strip
    strip = box("PanelStrip", (0.74, 0.012, 0.13), (0.0, face_y - 0.002, 1.05),
                M["steel_dark"])
    parts.append(strip)

    # digital clock / timer display
    bez = box("DisplayBezel", (0.24, 0.016, 0.085), (0.0, face_y + 0.004, 1.175),
              M["plastic"])
    bevel(bez, 0.003, 2)
    parts.append(bez)
    parts.append(box("DisplayGlass", (0.185, 0.008, 0.05),
                     (0.0, face_y + 0.014, 1.175), M["display"]))

    # four control knobs with pointer marks
    knob_x = (-0.28, -0.10, 0.10, 0.28)
    knob_a = (math.radians(-40), math.radians(15), math.radians(150),
              math.radians(-115))
    for i, (x, a) in enumerate(zip(knob_x, knob_a)):
        collar = cyl("KnobCollar_%d" % i, 0.040, 0.010,
                     (x, face_y + 0.005, 1.05), M["chrome"],
                     rot=(math.radians(90), 0, 0), verts=28)
        smooth(collar)
        parts.append(collar)

        body = cone("Knob_%d" % i, 0.034, 0.030, 0.040,
                    (x, face_y + 0.030, 1.05), M["plastic"],
                    rot=(math.radians(-90), 0, 0), verts=28)
        smooth(body)
        parts.append(body)

        # skirt ring for a nicer silhouette
        ring = torus("KnobRing_%d" % i, 0.031, 0.004,
                     (x, face_y + 0.048, 1.05), M["chrome"],
                     rot=(math.radians(90), 0, 0), maj_seg=28, min_seg=8)
        smooth(ring)
        parts.append(ring)

        px = x + 0.019 * math.sin(a)
        pz = 1.05 + 0.019 * math.cos(a)
        mark = box("KnobMark_%d" % i, (0.006, 0.006, 0.024),
                   (px, face_y + 0.050, pz), M["white"], rot=(0.0, a, 0.0))
        parts.append(mark)

        # engraved index dot above each knob
        parts.append(cyl("KnobIndex_%d" % i, 0.004, 0.004,
                         (x, face_y + 0.004, 1.108), M["white"],
                         rot=(math.radians(90), 0, 0), verts=10))
    return parts


def build_burner(M, x, y, grate_r, cap_r, index):
    """One sealed gas burner plus its round cast iron grate."""
    parts = []
    base_z = COOKTOP_Z + 0.004

    pan = cone("BurnerPan_%d" % index, cap_r + 0.030, cap_r + 0.012, 0.016,
               (x, y, base_z + 0.008), M["steel_dark"], verts=32)
    smooth(pan)
    parts.append(pan)

    ring = cyl("BurnerRing_%d" % index, cap_r, 0.020,
               (x, y, base_z + 0.024), M["brass"], verts=32)
    smooth(ring)
    parts.append(ring)

    # flame ports as a ring of small notches
    ports = 16
    for p in range(ports):
        a = 2.0 * math.pi * p / ports
        parts.append(box("Port_%d_%d" % (index, p), (0.010, 0.006, 0.008),
                         (x + cap_r * math.cos(a), y + cap_r * math.sin(a),
                          base_z + 0.030), M["iron"], rot=(0.0, 0.0, a)))

    cap = cone("BurnerCap_%d" % index, cap_r - 0.002, cap_r - 0.010, 0.014,
               (x, y, base_z + 0.041), M["iron"], verts=32)
    smooth(cap)
    parts.append(cap)

    ign = cyl("Igniter_%d" % index, 0.005, 0.030,
              (x + cap_r + 0.014, y, base_z + 0.018), M["white"], verts=10)
    parts.append(ign)

    # cast iron grate: outer ring + three crossing bars
    gz = base_z + 0.062
    gr = torus("GrateRing_%d" % index, grate_r, 0.010, (x, y, gz), M["iron"],
               maj_seg=36, min_seg=10)
    smooth(gr)
    parts.append(gr)
    for b in range(3):
        a = math.pi * b / 3.0
        bar = box("GrateBar_%d_%d" % (index, b),
                  (0.016, 2.0 * grate_r, 0.014), (x, y, gz), M["iron"],
                  rot=(0.0, 0.0, a))
        bevel(bar, 0.003, 2)
        parts.append(bar)
    # little feet keeping the grate off the enamel
    for f in range(3):
        a = 2.0 * math.pi * f / 3.0 + 0.5
        parts.append(cyl("GrateFoot_%d_%d" % (index, f), 0.008, 0.030,
                         (x + grate_r * 0.86 * math.cos(a),
                          y + grate_r * 0.86 * math.sin(a),
                          gz - 0.024), M["iron"], verts=10))
    return parts


def build_burners(M):
    layout = [(-0.20, -0.08, 0.112, 0.052),
              (0.20, -0.08, 0.098, 0.044),
              (-0.20, 0.24, 0.098, 0.044),
              (0.20, 0.24, 0.082, 0.034)]
    parts = []
    for i, (x, y, gr, cr) in enumerate(layout):
        parts.extend(build_burner(M, x, y, gr, cr, i))
    return parts


def build_oven_door(M):
    parts = []
    door = box("OvenDoor", (0.74, 0.05, 0.68), (0.0, -0.295, 0.462), M["steel"])
    bevel(door, 0.006, 3)
    smooth(door)
    parts.append(door)

    frame = box("DoorFrame", (0.64, 0.014, 0.50), (0.0, -0.326, 0.470),
                M["steel_dark"])
    bevel(frame, 0.004, 2)
    parts.append(frame)

    glass = box("DoorGlass", (0.585, 0.014, 0.445), (0.0, -0.331, 0.470),
                M["glass"])
    parts.append(glass)

    # oven interior hinted behind the glass
    parts.append(box("OvenCavity", (0.60, 0.30, 0.46), (0.0, -0.10, 0.470),
                     M["steel_dark"]))

    # tubular handle on two standoffs
    for sx in (-1, 1):
        st = box("HandleStandoff_%d" % (sx + 1), (0.050, 0.075, 0.050),
                 (sx * 0.290, -0.352, 0.745), M["chrome"])
        bevel(st, 0.006, 3)
        smooth(st)
        parts.append(st)
    bar = cyl("DoorHandle", 0.017, 0.70, (0.0, -0.393, 0.745), M["chrome"],
              rot=(0.0, math.radians(90), 0.0), verts=24)
    smooth(bar)
    parts.append(bar)
    for sx in (-1, 1):
        cap = cyl("HandleCap_%d" % (sx + 1), 0.019, 0.012,
                  (sx * 0.350, -0.393, 0.745), M["chrome"],
                  rot=(0.0, math.radians(90), 0.0), verts=24)
        smooth(cap)
        parts.append(cap)

    # vent slot between door top and cooktop
    parts.append(box("VentSlot", (0.62, 0.018, 0.022), (0.0, -0.276, 0.855),
                     M["iron"]))
    # storage drawer pull hinted at the very bottom
    parts.append(box("DoorSeam", (0.74, 0.008, 0.006), (0.0, -0.322, 0.126),
                     M["iron"]))
    return parts


def build_room(M):
    parts = []
    bpy.ops.mesh.primitive_plane_add(size=8.0, location=(0.0, 0.0, 0.0))
    floor = bpy.context.object
    floor.name = "Floor"
    assign(floor, M["floor"])
    parts.append(floor)

    wall = box("Wall", (7.0, 0.10, 3.0), (0.0, 0.45, 1.50), M["wall"])
    parts.append(wall)

    # flanking base cabinets and counter tops
    for sx in (-1, 1):
        c = box("Cabinet_%d" % (sx + 1), (0.90, 0.62, 0.86),
                (sx * 0.85, 0.09, 0.47), M["cabinet"])
        bevel(c, 0.005, 2)
        parts.append(c)
        parts.append(box("Toe_%d" % (sx + 1), (0.88, 0.52, 0.04),
                         (sx * 0.85, 0.14, 0.02), M["steel_dark"]))
        t = box("Counter_%d" % (sx + 1), (0.94, 0.66, 0.04),
                (sx * 0.85, 0.07, 0.92), M["counter"])
        bevel(t, 0.006, 3)
        parts.append(t)
        # simple cabinet door detail
        parts.append(box("CabDoor_%d" % (sx + 1), (0.78, 0.02, 0.72),
                         (sx * 0.85, -0.23, 0.48), M["cabinet"]))
        h = cyl("CabPull_%d" % (sx + 1), 0.010, 0.16,
                (sx * 0.85, -0.26, 0.78), M["chrome"],
                rot=(0.0, math.radians(90), 0.0), verts=16)
        smooth(h)
        parts.append(h)
    return parts


# --------------------------------------------------------------------------
# lighting / camera
# --------------------------------------------------------------------------
def build_lighting():
    key_data = bpy.data.lights.new("Key", 'AREA')
    key_data.energy = 420.0
    key_data.size = 2.4
    key = bpy.data.objects.new("KeyLight", key_data)
    key.location = (-2.0, -2.3, 3.0)
    bpy.context.collection.objects.link(key)
    look_at(key, (0.0, 0.0, 0.75))

    fill_data = bpy.data.lights.new("Fill", 'AREA')
    fill_data.energy = 110.0
    fill_data.size = 2.0
    fill = bpy.data.objects.new("FillLight", fill_data)
    fill.location = (2.6, -2.0, 1.6)
    bpy.context.collection.objects.link(fill)
    look_at(fill, (0.1, 0.0, 0.6))

    rim_data = bpy.data.lights.new("Rim", 'AREA')
    rim_data.energy = 90.0
    rim_data.size = 1.2
    rim = bpy.data.objects.new("RimLight", rim_data)
    rim.location = (1.1, 1.6, 2.2)
    bpy.context.collection.objects.link(rim)
    look_at(rim, (0.0, 0.1, 0.9))
    return key, fill, rim


def build_camera():
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = 42.0
    cam = bpy.data.objects.new("Camera", cam_data)
    cam.location = (1.32, -1.90, 1.44)
    bpy.context.collection.objects.link(cam)
    look_at(cam, (0.0, -0.05, 0.66))
    bpy.context.scene.camera = cam
    return cam


def main():
    reset_scene()
    make_world((0.05, 0.052, 0.058), 1.0)
    M = build_materials()

    objs = []
    objs += build_room(M)
    objs += build_carcass(M)
    objs += build_backguard(M)
    objs += build_burners(M)
    objs += build_oven_door(M)

    build_lighting()
    build_camera()

    print("claude-096: kitchen range built with %d objects" % len(objs))


if __name__ == "__main__":
    main()
