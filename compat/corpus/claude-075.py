"""claude-075 - Rooftop HVAC unit with fan grilles, louvres and ductwork."""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = 'METRIC'


def mat(name, col, rough=0.5, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (col[0], col[1], col[2], 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m


def smooth(ob, angle=40.0):
    for p in ob.data.polygons:
        p.use_smooth = True
    es = ob.modifiers.new("EdgeSplit", 'EDGE_SPLIT')
    es.split_angle = math.radians(angle)


def box(name, dims, loc=(0, 0, 0), rot=(0, 0, 0), m=None, bevel=0.0):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(dims), verts=bm.verts)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = rot
    bpy.context.collection.objects.link(ob)
    if m:
        me.materials.append(m)
    if bevel > 0.0:
        bv = ob.modifiers.new("Bevel", 'BEVEL')
        bv.width = bevel
        bv.segments = 2
        bv.limit_method = 'ANGLE'
    return ob


def cyl(name, r, h, loc, rot=(0, 0, 0), m=None, verts=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h,
                                        location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    if m:
        ob.data.materials.append(m)
    smooth(ob)
    return ob


def tube(name, p1, p2, r, m=None, verts=14):
    a, b = Vector(p1), Vector(p2)
    v = b - a
    ob = cyl(name, r, v.length, tuple((a + b) * 0.5), m=m, verts=verts)
    ob.rotation_euler = v.to_track_quat('Z', 'Y').to_euler()
    return ob


def torus(name, major, minor, loc, m=None, mseg=48, nseg=8):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                     major_segments=mseg, minor_segments=nseg,
                                     location=loc)
    ob = bpy.context.object
    ob.name = name
    if m:
        ob.data.materials.append(m)
    smooth(ob)
    return ob


def fan_section(name, centre, cowl_r, steel, grille_m, blade_m):
    cx, cy, cz = centre
    cyl(name + "_Cowl", cowl_r, 0.22, (cx, cy, cz + 0.11), m=steel, verts=40)
    cyl(name + "_Throat", cowl_r - 0.05, 0.24, (cx, cy, cz + 0.05), m=steel, verts=40)
    top = cz + 0.22

    for r in (cowl_r * 0.36, cowl_r * 0.62, cowl_r * 0.90):
        torus(name + "_Ring", r, 0.010, (cx, cy, top), m=grille_m, mseg=40, nseg=6)
    torus(name + "_Rim", cowl_r + 0.02, 0.022, (cx, cy, top - 0.01), m=steel, mseg=44, nseg=8)
    for k in range(10):
        a = math.pi * k / 10.0
        box(name + "_Spoke", (0.018, 2.0 * cowl_r * 0.94, 0.014),
            (cx, cy, top), rot=(0.0, 0.0, a), m=grille_m)
    cyl(name + "_GrilleHub", 0.075, 0.05, (cx, cy, top + 0.01), m=grille_m, verts=16)

    # fan and motor below the grille
    cyl(name + "_Hub", 0.10, 0.16, (cx, cy, cz - 0.02), m=steel, verts=20)
    for k in range(6):
        a = 2.0 * math.pi * k / 6.0
        blade = box(name + "_Blade", (cowl_r * 0.72, 0.14, 0.010), m=blade_m)
        blade.matrix_world = (Matrix.Translation((cx, cy, cz - 0.02)) @
                              Matrix.Rotation(a, 4, 'Z') @
                              Matrix.Translation((cowl_r * 0.46, 0.0, 0.0)) @
                              Matrix.Rotation(math.radians(26.0), 4, 'X'))


def louvre_panel(name, centre, width, rows, steel, louvre_m, face_y):
    cx, cy, cz = centre
    box(name + "_Frame", (width + 0.10, 0.05, rows * 0.095 + 0.10),
        (cx, cy, cz), m=steel, bevel=0.006)
    for i in range(rows):
        z = cz - rows * 0.095 / 2.0 + 0.05 + i * 0.095
        box(name + "_Slat", (width, 0.085, 0.016),
            (cx, cy + face_y * 0.03, z),
            rot=(math.radians(32.0) * face_y, 0.0, 0.0), m=louvre_m)


def duct_run(name, y, steel):
    """Horizontal run out of the +X end, square mitred elbow, drop to the roof."""
    w, h = 0.70, 0.55
    z = 1.05
    x0, x1 = 1.55, 3.85
    box(name + "_Horiz", (x1 - x0, w, h), ((x0 + x1) / 2.0, y, z), m=steel, bevel=0.01)
    box(name + "_Elbow", (h, w, h), (x1 + h / 2.0, y, z), m=steel, bevel=0.01)
    box(name + "_Drop", (h, w, z - h / 2.0 - 0.0),
        (x1 + h / 2.0, y, (z - h / 2.0) / 2.0), m=steel, bevel=0.01)
    # flanged joints
    for fx in (x0 + 0.05, x0 + 0.85, x0 + 1.65, x1 - 0.02):
        box(name + "_Flange", (0.03, w + 0.07, h + 0.07), (fx, y, z), m=steel)
    for fz in (0.75, 0.30):
        box(name + "_DropFlange", (h + 0.07, w + 0.07, 0.03),
            (x1 + h / 2.0, y, fz), m=steel)
    # roof curb and support stand
    box(name + "_Curb", (h + 0.30, w + 0.30, 0.22), (x1 + h / 2.0, y, 0.11),
        m=steel, bevel=0.01)
    for sx in (x0 + 0.7, x0 + 1.7):
        box(name + "_StandPad", (0.22, 0.30, 0.06), (sx, y, 0.03), m=steel)
        box(name + "_StandPost", (0.07, 0.07, z - h / 2.0),
            (sx, y, (z - h / 2.0) / 2.0), m=steel)
        box(name + "_StandCap", (0.20, w + 0.06, 0.05),
            (sx, y, z - h / 2.0 - 0.025), m=steel)


def build():
    reset()
    w = bpy.data.worlds.new("World")
    w.use_nodes = True
    bgn = w.node_tree.nodes["Background"]
    bgn.inputs[0].default_value = (0.40, 0.52, 0.72, 1.0)
    bgn.inputs[1].default_value = 1.1
    bpy.context.scene.world = w

    gravel = mat("RoofGravel", (0.34, 0.32, 0.30), 0.95)
    concrete = mat("Parapet", (0.55, 0.54, 0.52), 0.9)
    galv = mat("Galvanised", (0.62, 0.63, 0.65), 0.38, 0.85)
    panel = mat("UnitPanel", (0.72, 0.73, 0.72), 0.45, 0.5)
    dark = mat("DarkSteel", (0.20, 0.21, 0.22), 0.5, 0.8)
    grille_m = mat("GrilleWire", (0.28, 0.29, 0.30), 0.45, 0.9)
    blade_m = mat("FanBlade", (0.16, 0.17, 0.18), 0.35, 0.9)
    copper = mat("Insulation", (0.10, 0.10, 0.12), 0.85)
    yellow = mat("Label", (0.85, 0.70, 0.10), 0.6)

    # --- roof deck and parapet -------------------------------------------
    box("RoofDeck", (18.0, 15.0, 0.40), (0.0, 0.0, -0.20), m=gravel)
    for sx in (-1.0, 1.0):
        box("ParapetX", (0.30, 15.0, 0.85), (sx * 8.85, 0.0, 0.42), m=concrete, bevel=0.02)
    for sy in (-1.0, 1.0):
        box("ParapetY", (18.0, 0.30, 0.85), (0.0, sy * 7.35, 0.42), m=concrete, bevel=0.02)

    # --- curb and unit housing -------------------------------------------
    box("Curb", (3.45, 2.45, 0.32), (0.0, 0.0, 0.16), m=dark, bevel=0.015)
    box("CurbGasket", (3.50, 2.50, 0.04), (0.0, 0.0, 0.34), m=copper)
    UZ0, UZ1 = 0.34, 1.86
    box("Housing", (3.20, 2.20, UZ1 - UZ0), (0.0, 0.0, (UZ0 + UZ1) / 2.0),
        m=panel, bevel=0.018)
    box("TopCap", (3.26, 2.26, 0.05), (0.0, 0.0, UZ1 + 0.02), m=galv, bevel=0.01)
    box("BaseRail", (3.26, 2.26, 0.09), (0.0, 0.0, UZ0 + 0.045), m=galv, bevel=0.008)

    # panel seams
    for i in range(-2, 3):
        for sy in (-1.0, 1.0):
            box("Seam", (0.03, 0.03, UZ1 - UZ0 - 0.10),
                (i * 0.62, sy * 1.10, (UZ0 + UZ1) / 2.0), m=galv)
    for sx in (-1.0, 1.0):
        box("CornerPost", (0.05, 0.05, UZ1 - UZ0), (sx * 1.585, 1.085, (UZ0 + UZ1) / 2.0), m=galv)
        box("CornerPost", (0.05, 0.05, UZ1 - UZ0), (sx * 1.585, -1.085, (UZ0 + UZ1) / 2.0), m=galv)

    # --- fan sections on the roof of the unit ----------------------------
    fan_section("FanA", (-0.82, 0.35, UZ1 + 0.04), 0.46, galv, grille_m, blade_m)
    fan_section("FanB", (0.82, 0.35, UZ1 + 0.04), 0.46, galv, grille_m, blade_m)

    # flue and rain cap
    cyl("Flue", 0.11, 0.55, (0.0, -0.72, UZ1 + 0.30), m=galv, verts=20)
    cyl("FlueCap", 0.19, 0.05, (0.0, -0.72, UZ1 + 0.60), m=galv, verts=20)
    for k in range(3):
        a = 2.0 * math.pi * k / 3.0
        tube("CapLeg", (0.11 * math.cos(a), -0.72 + 0.11 * math.sin(a), UZ1 + 0.52),
             (0.15 * math.cos(a), -0.72 + 0.15 * math.sin(a), UZ1 + 0.585), 0.008, m=galv, verts=6)

    # --- louvred intakes on both long faces ------------------------------
    louvre_panel("LouvreS", (-0.35, -1.13, 1.05), 2.10, 10, galv, dark, -1.0)
    louvre_panel("LouvreN", (-0.35, 1.13, 1.05), 2.10, 10, galv, dark, 1.0)
    box("CoilGuardS", (2.20, 0.02, 1.00), (-0.35, -1.16, 1.05), m=grille_m)
    box("CoilGuardN", (2.20, 0.02, 1.00), (-0.35, 1.16, 1.05), m=grille_m)

    # --- access panel, controls, service details --------------------------
    box("AccessPanel", (0.03, 0.95, 1.05), (-1.62, 0.55, 1.05), m=galv, bevel=0.008)
    for hz in (0.70, 1.40):
        box("Hinge", (0.05, 0.07, 0.12), (-1.64, 0.10, hz), m=dark)
    cyl("Handle", 0.022, 0.16, (-1.66, 0.92, 1.05), rot=(0.0, math.pi / 2.0, 0.0),
        m=dark, verts=10)
    box("Nameplate", (0.01, 0.34, 0.20), (-1.63, -0.55, 1.35), m=yellow)

    box("Disconnect", (0.28, 0.24, 0.42), (-1.75, -0.60, 0.95), m=dark, bevel=0.01)
    tube("Conduit", (-1.75, -0.60, 0.74), (-1.75, -0.60, 0.12), 0.026, m=galv, verts=10)
    tube("ConduitRun", (-1.75, -0.60, 0.10), (-1.75, -2.60, 0.10), 0.026, m=galv, verts=10)

    # refrigerant / condensate lines dropping to the roof
    for i, (yy, rr) in enumerate(((-0.20, 0.045), (0.05, 0.030))):
        tube("Line_%d" % i, (-1.62, yy, 0.80), (-2.10, yy, 0.80), rr, m=copper, verts=10)
        tube("LineDrop_%d" % i, (-2.10, yy, 0.82), (-2.10, yy, 0.16), rr, m=copper, verts=10)
        box("LineClamp_%d" % i, (0.10, 0.10, 0.05), (-2.10, yy, 0.45), m=galv)
    box("LineStand", (0.20, 0.55, 0.16), (-2.10, -0.08, 0.08), m=dark, bevel=0.01)

    # --- ductwork ---------------------------------------------------------
    duct_run("SupplyDuct", -0.55, galv)
    duct_run("ReturnDuct", 0.55, galv)
    box("DuctCollar_S", (0.06, 0.82, 0.67), (1.58, -0.55, 1.05), m=galv)
    box("DuctCollar_R", (0.06, 0.82, 0.67), (1.58, 0.55, 1.05), m=galv)

    # --- lighting and camera ---------------------------------------------
    ld = bpy.data.lights.new("Sun", 'SUN')
    ld.energy = 4.0
    ld.angle = math.radians(2.0)
    sun = bpy.data.objects.new("Sun", ld)
    sun.rotation_euler = (math.radians(55.0), math.radians(8.0), math.radians(-55.0))
    bpy.context.collection.objects.link(sun)

    ald = bpy.data.lights.new("Fill", 'AREA')
    ald.energy = 600.0
    ald.size = 5.0
    fill = bpy.data.objects.new("Fill", ald)
    fill.location = (-5.0, -6.0, 4.5)
    fill.rotation_euler = (Vector((0.0, 0.0, 1.0)) - fill.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(fill)

    cd = bpy.data.cameras.new("Camera")
    cd.lens = 40.0
    cam = bpy.data.objects.new("Camera", cd)
    bpy.context.collection.objects.link(cam)
    cam.location = (7.6, -7.4, 4.6)
    cam.rotation_euler = (Vector((0.4, 0.0, 1.15)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam


if __name__ == "__main__":
    build()
