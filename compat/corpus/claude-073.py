"""claude-073 - Tennis court: ITF markings, sagging net, perimeter fence posts."""

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


def cyl(name, r, h, loc, rot=(0, 0, 0), m=None, verts=20):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h,
                                        location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    if m:
        ob.data.materials.append(m)
    smooth(ob)
    return ob


def tube(name, p1, p2, r, m=None, verts=16):
    a, b = Vector(p1), Vector(p2)
    v = b - a
    ob = cyl(name, r, v.length, tuple((a + b) * 0.5), m=m, verts=verts)
    ob.rotation_euler = v.to_track_quat('Z', 'Y').to_euler()
    return ob


# court constants (metres)
HALF_L = 11.885
DOUB = 5.485
SING = 4.115
SERV = 6.40
NET_HALF = 6.40
POST_H = 1.07
CENTRE_H = 0.914


def net_height(x):
    t = abs(x) / NET_HALF
    return CENTRE_H + (POST_H - CENTRE_H) * (t ** 2)


def build_net(mesh_mat, tape_mat):
    nx, nz = 72, 14
    me = bpy.data.meshes.new("NetMesh")
    bm = bmesh.new()
    cols = []
    for i in range(nx + 1):
        x = -NET_HALF + 2.0 * NET_HALF * i / nx
        h = net_height(x) - 0.055          # under the tape
        cols.append([bm.verts.new((x, 0.0, h * j / nz)) for j in range(nz + 1)])
    for i in range(nx):
        for j in range(nz):
            bm.faces.new((cols[i][j], cols[i + 1][j], cols[i + 1][j + 1], cols[i][j + 1]))
    bm.to_mesh(me)
    bm.free()
    net = bpy.data.objects.new("Net", me)
    bpy.context.collection.objects.link(net)
    me.materials.append(mesh_mat)
    wf = net.modifiers.new("Wireframe", 'WIREFRAME')
    wf.thickness = 0.008
    wf.use_replace = True
    wf.use_boundary = True

    # white tape band following the same sag
    me2 = bpy.data.meshes.new("TapeMesh")
    bm = bmesh.new()
    strip = []
    for i in range(nx + 1):
        x = -NET_HALF + 2.0 * NET_HALF * i / nx
        h = net_height(x)
        strip.append((bm.verts.new((x, 0.0, h)), bm.verts.new((x, 0.0, h - 0.06))))
    for i in range(nx):
        bm.faces.new((strip[i][0], strip[i + 1][0], strip[i + 1][1], strip[i][1]))
    bm.to_mesh(me2)
    bm.free()
    tape = bpy.data.objects.new("NetTape", me2)
    bpy.context.collection.objects.link(tape)
    me2.materials.append(tape_mat)
    so = tape.modifiers.new("Solidify", 'SOLIDIFY')
    so.thickness = 0.014
    so.offset = 0.0
    return net, tape


def fence_panel(name, w, h, cell, loc, rot, m, thick=0.012):
    nx = max(2, int(round(w / cell)))
    ny = max(2, int(round(h / cell)))
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    vs = [[bm.verts.new((-w / 2.0 + w * i / nx, -h / 2.0 + h * j / ny, 0.0))
           for j in range(ny + 1)] for i in range(nx + 1)]
    for i in range(nx):
        for j in range(ny):
            bm.faces.new((vs[i][j], vs[i + 1][j], vs[i + 1][j + 1], vs[i][j + 1]))
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = rot
    bpy.context.collection.objects.link(ob)
    me.materials.append(m)
    wf = ob.modifiers.new("Wireframe", 'WIREFRAME')
    wf.thickness = thick
    wf.use_replace = True
    return ob


def build():
    reset()
    w = bpy.data.worlds.new("World")
    w.use_nodes = True
    bgn = w.node_tree.nodes["Background"]
    bgn.inputs[0].default_value = (0.44, 0.58, 0.82, 1.0)
    bgn.inputs[1].default_value = 1.3
    bpy.context.scene.world = w

    surround = mat("Surround", (0.13, 0.32, 0.26), 0.9)
    playarea = mat("PlayArea", (0.11, 0.30, 0.52), 0.85)
    white = mat("LinePaint", (0.94, 0.94, 0.92), 0.65)
    dark = mat("NetMesh", (0.04, 0.04, 0.05), 0.8)
    postm = mat("PostMetal", (0.10, 0.20, 0.16), 0.45, 0.7)
    fencem = mat("Chainlink", (0.42, 0.45, 0.46), 0.5, 0.9)

    box("Surround", (19.0, 37.0, 0.12), (0.0, 0.0, -0.06), m=surround)
    box("PlayArea", (13.0, 27.5, 0.02), (0.0, 0.0, 0.002), m=playarea)

    def line(name, x1, y1, x2, y2, lw=0.05):
        box(name, (max(abs(x2 - x1), lw), max(abs(y2 - y1), lw), 0.008),
            ((x1 + x2) / 2.0, (y1 + y2) / 2.0, 0.012), m=white)

    for s in (-1.0, 1.0):
        line("Baseline_%s" % s, -DOUB, s * HALF_L, DOUB, s * HALF_L, 0.10)
        line("ServiceLine_%s" % s, -SING, s * SERV, SING, s * SERV)
        line("CentreMark_%s" % s, 0.0, s * HALF_L, 0.0, s * (HALF_L - 0.10), 0.05)
        line("DoublesSide_%s" % s, s * DOUB, -HALF_L, s * DOUB, HALF_L)
        line("SinglesSide_%s" % s, s * SING, -HALF_L, s * SING, HALF_L)
    line("CentreService", 0.0, -SERV, 0.0, SERV)

    # --- net ---------------------------------------------------------------
    build_net(dark, white)
    box("CentreStrap", (0.05, 0.02, CENTRE_H), (0.0, 0.0, CENTRE_H / 2.0), m=white)
    for s in (-1.0, 1.0):
        cyl("NetPost_%s" % s, 0.055, 1.20, (s * NET_HALF, 0.0, 0.52), m=postm, verts=20)
        cyl("NetPostCap_%s" % s, 0.06, 0.03, (s * NET_HALF, 0.0, 1.13), m=postm, verts=20)

    # --- perimeter fence ---------------------------------------------------
    FX, FY, FH = 9.2, 18.0, 3.6
    step = 3.0
    n_side = int(round(2 * FY / step))
    n_end = int(round(2 * FX / step))
    for i in range(n_side + 1):
        y = -FY + 2 * FY * i / n_side
        for s in (-1.0, 1.0):
            cyl("FencePost", 0.05, FH, (s * FX, y, FH / 2.0 - 0.2), m=postm, verts=12)
    for i in range(1, n_end):
        x = -FX + 2 * FX * i / n_end
        for s in (-1.0, 1.0):
            cyl("FencePost", 0.05, FH, (x, s * FY, FH / 2.0 - 0.2), m=postm, verts=12)
    for s in (-1.0, 1.0):
        for z in (FH - 0.25, 1.6):
            tube("RailSide", (s * FX, -FY, z), (s * FX, FY, z), 0.035, m=postm, verts=10)
            tube("RailEnd", (-FX, s * FY, z), (FX, s * FY, z), 0.035, m=postm, verts=10)
        fence_panel("FenceSide_%s" % s, 2 * FY, FH - 0.05, 0.5,
                    (s * FX, 0.0, (FH - 0.05) / 2.0 - 0.2),
                    (math.pi / 2.0, 0.0, math.pi / 2.0), fencem)
        fence_panel("FenceEnd_%s" % s, 2 * FX, FH - 0.05, 0.5,
                    (0.0, s * FY, (FH - 0.05) / 2.0 - 0.2),
                    (math.pi / 2.0, 0.0, 0.0), fencem)

    # a couple of umpire-side details
    box("BenchSeat", (1.6, 0.45, 0.06), (7.8, -2.2, 0.45), m=postm, bevel=0.01)
    for bx in (7.1, 8.5):
        for by in (-2.4, -2.0):
            cyl("BenchLeg", 0.03, 0.42, (bx, by, 0.21), m=postm, verts=10)

    # --- lighting and camera ----------------------------------------------
    ld = bpy.data.lights.new("Sun", 'SUN')
    ld.energy = 4.5
    ld.angle = math.radians(1.5)
    sun = bpy.data.objects.new("Sun", ld)
    sun.rotation_euler = (math.radians(50.0), math.radians(8.0), math.radians(35.0))
    bpy.context.collection.objects.link(sun)

    cd = bpy.data.cameras.new("Camera")
    cd.lens = 35.0
    cam = bpy.data.objects.new("Camera", cd)
    bpy.context.collection.objects.link(cam)
    cam.location = (16.0, -22.0, 10.5)
    cam.rotation_euler = (Vector((0.0, 0.0, 0.9)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam


if __name__ == "__main__":
    build()
