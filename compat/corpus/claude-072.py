"""claude-072 - Basketball hoop: pole, backboard, rim and a skinned net."""

import bpy
import bmesh
import math
from mathutils import Vector


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


def bar(name, p1, p2, w, d, m=None, bevel=0.0):
    a, b = Vector(p1), Vector(p2)
    v = b - a
    ob = box(name, (w, d, v.length), tuple((a + b) * 0.5), m=m, bevel=bevel)
    ob.rotation_euler = v.to_track_quat('Z', 'Y').to_euler()
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


def camera(loc, target, lens=42.0):
    cd = bpy.data.cameras.new("Camera")
    cd.lens = lens
    cam = bpy.data.objects.new("Camera", cd)
    bpy.context.collection.objects.link(cam)
    cam.location = loc
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam
    return cam


def world(col, strength):
    w = bpy.data.worlds.new("World")
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (col[0], col[1], col[2], 1.0)
    bg.inputs[1].default_value = strength
    bpy.context.scene.world = w


RIM_R = 0.2286
RIM_Z = 3.05
RIM_Y = -(0.15 + RIM_R)     # rim centre, 150 mm clear of the board face
BOARD_BOTTOM = 2.90


def build_net(m):
    """Diamond net cage of edges driven by a Skin + Subsurf modifier."""
    rows, cols = 9, 12
    depth, bot_r = 0.42, 0.115
    me = bpy.data.meshes.new("Net")
    bm = bmesh.new()
    grid = []
    for i in range(rows):
        t = i / (rows - 1.0)
        r = RIM_R + (bot_r - RIM_R) * (t ** 0.8)
        z = RIM_Z - depth * t
        off = 0.5 if i % 2 else 0.0
        ring = []
        for j in range(cols):
            a = 2.0 * math.pi * (j + off) / cols
            ring.append(bm.verts.new((r * math.cos(a) + 0.0,
                                      r * math.sin(a) + RIM_Y,
                                      z)))
        grid.append(ring)
    bm.verts.ensure_lookup_table()
    for i in range(rows - 1):
        for j in range(cols):
            k = (j - 1) % cols if i % 2 == 0 else (j + 1) % cols
            bm.edges.new((grid[i][j], grid[i + 1][j]))
            bm.edges.new((grid[i][j], grid[i + 1][k]))
    for j in range(cols):                      # bottom ring
        bm.edges.new((grid[rows - 1][j], grid[rows - 1][(j + 1) % cols]))
    bm.to_mesh(me)
    bm.free()

    ob = bpy.data.objects.new("Net", me)
    bpy.context.collection.objects.link(ob)
    me.materials.append(m)
    sk = ob.modifiers.new("Skin", 'SKIN')
    sk.use_smooth_shade = True
    layer = ob.data.skin_vertices[0].data
    for sv in layer:
        sv.radius = (0.006, 0.006)
    layer[0].use_root = True
    sub = ob.modifiers.new("Subdivision", 'SUBSURF')
    sub.levels = 1
    sub.render_levels = 1
    return ob


def build():
    reset()
    world((0.45, 0.58, 0.80), 1.2)

    asphalt = mat("Asphalt", (0.15, 0.15, 0.16), 0.95)
    paint = mat("CourtPaint", (0.88, 0.88, 0.86), 0.7)
    white = mat("BoardWhite", (0.90, 0.90, 0.90), 0.18)
    black = mat("BoardTrim", (0.05, 0.05, 0.05), 0.35)
    orange = mat("RimOrange", (0.75, 0.22, 0.03), 0.35, 0.6)
    grey = mat("PoleSteel", (0.30, 0.31, 0.33), 0.42, 0.85)
    pad = mat("PolePad", (0.08, 0.10, 0.35), 0.75)
    concrete = mat("Concrete", (0.55, 0.54, 0.51), 0.9)
    netm = mat("NetCord", (0.92, 0.92, 0.90), 0.7)

    box("Ground", (26.0, 30.0, 0.2), (0.0, -6.0, -0.1), m=asphalt)

    # --- court markings (baseline at y = +1.22, court runs toward -Y) -----
    def line(name, x1, y1, x2, y2, w=0.05):
        box(name, (max(abs(x2 - x1), w), max(abs(y2 - y1), w), 0.006),
            ((x1 + x2) / 2.0, (y1 + y2) / 2.0, 0.004), m=paint)

    line("Baseline", -7.5, 1.22, 7.5, 1.22, 0.05)
    line("LaneL", -2.44, 1.22, -2.44, -4.57)
    line("LaneR", 2.44, 1.22, 2.44, -4.57)
    line("FreeThrow", -2.44, -4.57, 2.44, -4.57)
    bpy.ops.mesh.primitive_torus_add(major_radius=1.80, minor_radius=0.03,
                                     major_segments=64, minor_segments=6,
                                     location=(0.0, -4.57, 0.004))
    circ = bpy.context.object
    circ.name = "FreeThrowCircle"
    circ.scale = (1.0, 1.0, 0.15)
    circ.data.materials.append(paint)
    smooth(circ)

    # --- footing and pole -------------------------------------------------
    box("Footing", (1.1, 1.1, 0.25), (0.0, 1.45, 0.10), m=concrete, bevel=0.02)
    cyl("Pole", 0.085, 3.90, (0.0, 1.45, 1.95), m=grey, verts=28)
    cyl("PolePad", 0.135, 1.90, (0.0, 1.45, 1.05), m=pad, verts=24)
    cyl("BasePlate", 0.22, 0.05, (0.0, 1.45, 0.245), m=grey, verts=20)

    # yoke plates on the pole and the arms out to the board
    box("YokeTop", (0.72, 0.14, 0.10), (0.0, 1.45, 3.68), m=grey, bevel=0.008)
    box("YokeLow", (0.72, 0.14, 0.10), (0.0, 1.45, 3.00), m=grey, bevel=0.008)
    for sx in (-1.0, 1.0):
        x = sx * 0.28
        bar("ArmTop_%s" % sx, (x, 1.40, 3.68), (x, 0.06, 3.72), 0.07, 0.09,
            m=grey, bevel=0.006)
        bar("ArmLow_%s" % sx, (x, 1.40, 3.00), (x, 0.06, 3.06), 0.07, 0.09,
            m=grey, bevel=0.006)
        bar("Diag_%s" % sx, (x, 1.40, 3.04), (x, 0.12, 3.62), 0.05, 0.07,
            m=grey, bevel=0.005)

    # --- backboard --------------------------------------------------------
    board_h = 1.05
    board_cz = BOARD_BOTTOM + board_h / 2.0
    box("Backboard", (1.80, 0.045, board_h), (0.0, 0.0225, board_cz),
        m=white, bevel=0.006)
    box("BoardFrameTop", (1.84, 0.06, 0.05), (0.0, 0.045, board_cz + board_h / 2.0),
        m=grey)
    box("BoardFrameBot", (1.84, 0.06, 0.05), (0.0, 0.045, board_cz - board_h / 2.0),
        m=grey)

    # painted border and shooter's square, sitting just proud of the face
    yf = -0.004
    bw = 0.05
    box("BorderT", (1.70, 0.006, bw), (0.0, yf, board_cz + 0.475), m=black)
    box("BorderB", (1.70, 0.006, bw), (0.0, yf, board_cz - 0.475), m=black)
    box("BorderL", (bw, 0.006, 1.00), (-0.825, yf, board_cz), m=black)
    box("BorderR", (bw, 0.006, 1.00), (0.825, yf, board_cz), m=black)
    sq_w, sq_h = 0.59, 0.45
    sq_cz = RIM_Z + sq_h / 2.0
    box("SquareT", (sq_w, 0.006, 0.04), (0.0, yf, sq_cz + sq_h / 2.0), m=black)
    box("SquareB", (sq_w, 0.006, 0.04), (0.0, yf, sq_cz - sq_h / 2.0), m=black)
    box("SquareL", (0.04, 0.006, sq_h), (-sq_w / 2.0, yf, sq_cz), m=black)
    box("SquareR", (0.04, 0.006, sq_h), (sq_w / 2.0, yf, sq_cz), m=black)

    # --- rim, bracket and net --------------------------------------------
    bpy.ops.mesh.primitive_torus_add(major_radius=RIM_R, minor_radius=0.0095,
                                     major_segments=48, minor_segments=10,
                                     location=(0.0, RIM_Y, RIM_Z))
    rim = bpy.context.object
    rim.name = "Rim"
    rim.data.materials.append(orange)
    smooth(rim)

    box("RimPlate", (0.30, 0.03, 0.24), (0.0, 0.015, RIM_Z - 0.02), m=orange, bevel=0.005)
    box("RimBracket", (0.16, 0.20, 0.08), (0.0, -0.09, RIM_Z - 0.03), m=orange, bevel=0.006)
    bar("RimStay", (0.0, -0.02, RIM_Z - 0.16), (0.0, -0.16, RIM_Z - 0.02),
        0.10, 0.04, m=orange)
    for sx in (-1.0, 1.0):
        cyl("NetHook_%s" % sx, 0.012, 0.03,
            (sx * RIM_R * 0.9, RIM_Y + 0.05, RIM_Z - 0.012), m=orange, verts=8)

    build_net(netm)

    # --- lighting and camera ---------------------------------------------
    ld = bpy.data.lights.new("Sun", 'SUN')
    ld.energy = 4.2
    ld.angle = math.radians(2.0)
    sun = bpy.data.objects.new("Sun", ld)
    sun.rotation_euler = (math.radians(48.0), math.radians(6.0), math.radians(-125.0))
    bpy.context.collection.objects.link(sun)

    ald = bpy.data.lights.new("Fill", 'AREA')
    ald.energy = 900.0
    ald.size = 6.0
    fill = bpy.data.objects.new("Fill", ald)
    fill.location = (-5.0, -7.0, 6.0)
    fill.rotation_euler = (Vector((0.0, -0.5, 3.0)) - fill.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(fill)

    camera((4.6, -7.6, 3.3), (0.0, -0.5, 2.85), lens=45.0)


if __name__ == "__main__":
    build()
