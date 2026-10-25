"""claude-071 - A picnic table with attached benches (A-frame, crossed legs)."""

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
    """Exact sized box; object scale stays 1.0 so bevel widths are uniform."""
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
        bv.angle_limit = math.radians(40.0)
    return ob


def beam(name, p1, p2, w, d, m=None, bevel=0.0):
    """Board of cross section (w along X, d along Y) spanning p1->p2."""
    a, b = Vector(p1), Vector(p2)
    v = b - a
    ob = box(name, (w, d, v.length), tuple((a + b) * 0.5), m=m, bevel=bevel)
    ob.rotation_euler = v.to_track_quat('Z', 'Y').to_euler()
    return ob


def cyl(name, r, h, loc, rot=(0, 0, 0), m=None, verts=16):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h,
                                        location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    if m:
        ob.data.materials.append(m)
    smooth(ob)
    return ob


def camera(loc, target, lens=45.0):
    cd = bpy.data.cameras.new("Camera")
    cd.lens = lens
    cam = bpy.data.objects.new("Camera", cd)
    bpy.context.collection.objects.link(cam)
    cam.location = loc
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam
    return cam


def sun(rot, energy, color=(1.0, 0.96, 0.9)):
    ld = bpy.data.lights.new("Sun", 'SUN')
    ld.energy = energy
    ld.angle = math.radians(2.0)
    ld.color = color
    ob = bpy.data.objects.new("Sun", ld)
    ob.rotation_euler = rot
    bpy.context.collection.objects.link(ob)
    return ob


def world(col, strength):
    w = bpy.data.worlds.new("World")
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (col[0], col[1], col[2], 1.0)
    bg.inputs[1].default_value = strength
    bpy.context.scene.world = w


# ------------------------------------------------------------------ build
def build():
    reset()
    world((0.42, 0.56, 0.78), 1.1)

    wood_top = mat("WoodTop", (0.46, 0.29, 0.15), 0.62)
    wood_frm = mat("WoodFrame", (0.38, 0.23, 0.115), 0.72)
    steel = mat("Steel", (0.55, 0.56, 0.58), 0.32, 1.0)
    grass = mat("Grass", (0.19, 0.30, 0.11), 0.92)

    box("Ground", (26.0, 26.0, 0.2), (0.0, 0.0, -0.1), m=grass)

    TOP_Z = 0.75          # finished table height
    PT = 0.04             # top plank thickness
    PW = 0.145            # plank width
    GAP = 0.012
    LEN = 1.90            # table length along X
    BENCH_Z = 0.45
    BT = 0.035            # bench plank thickness
    FRAME_X = 0.62        # the two leg frames

    # --- table top planks -------------------------------------------------
    pitch = PW + GAP
    for i in range(5):
        y = (i - 2) * pitch
        box("TopPlank_%d" % i, (LEN, PW, PT), (0.0, y, TOP_Z - PT / 2.0),
            m=wood_top, bevel=0.006)

    # --- bench planks (two per side) -------------------------------------
    for s in (-1.0, 1.0):
        for i, off in enumerate((-0.0785, 0.0785)):
            y = s * 0.66 + off
            box("BenchPlank_%s%d" % ("L" if s < 0 else "R", i),
                (LEN, PW, BT), (0.0, y, BENCH_Z - BT / 2.0),
                m=wood_top, bevel=0.005)

    # --- leg frames -------------------------------------------------------
    top_beam_z = TOP_Z - PT - 0.03      # centre of the top cross member
    bench_beam_z = BENCH_Z - BT - 0.03  # centre of the bench cross member

    for sx in (-1.0, 1.0):
        x = sx * FRAME_X

        # crossed splayed legs
        beam("Leg_%s_A" % sx, (x, -0.90, 0.0), (x, 0.30, 0.72),
             0.09, 0.05, m=wood_frm, bevel=0.006)
        beam("Leg_%s_B" % sx, (x, 0.90, 0.0), (x, -0.30, 0.72),
             0.09, 0.05, m=wood_frm, bevel=0.006)

        # bench cross member and top cross member
        box("BenchBeam_%s" % sx, (0.085, 1.76, 0.06), (x, 0.0, bench_beam_z),
            m=wood_frm, bevel=0.006)
        box("TopBeam_%s" % sx, (0.085, 0.74, 0.06), (x, 0.0, top_beam_z),
            m=wood_frm, bevel=0.006)

        # diagonal braces: bench member outer ends up to the top frame
        for sy in (-1.0, 1.0):
            beam("Brace_%s_%s" % (sx, sy),
                 (x, sy * 0.80, bench_beam_z + 0.02),
                 (x, sy * 0.09, top_beam_z - 0.02),
                 0.06, 0.04, m=wood_frm, bevel=0.005)

        # bolt heads where the members meet the legs
        for (by, bz) in ((0.24, bench_beam_z), (-0.24, bench_beam_z),
                         (0.30, top_beam_z), (-0.30, top_beam_z),
                         (0.78, bench_beam_z), (-0.78, bench_beam_z)):
            cyl("Bolt", 0.014, 0.09, (x, by, bz), rot=(0.0, math.pi / 2.0, 0.0),
                m=steel, verts=12)

    # longitudinal stringer tying the two frames together
    box("Stringer", (2 * FRAME_X + 0.17, 0.09, 0.05), (0.0, 0.0, top_beam_z - 0.055),
        m=wood_frm, bevel=0.005)

    # --- lighting and camera ---------------------------------------------
    sun((math.radians(52.0), 0.0, math.radians(38.0)), 4.0)

    ld = bpy.data.lights.new("Fill", 'AREA')
    ld.energy = 220.0
    ld.size = 4.0
    fill = bpy.data.objects.new("Fill", ld)
    fill.location = (-3.0, -3.5, 3.2)
    fill.rotation_euler = (Vector((0.0, 0.0, 0.6)) - fill.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(fill)

    camera((3.1, -3.5, 2.15), (0.0, 0.0, 0.55), lens=45.0)


if __name__ == "__main__":
    build()
