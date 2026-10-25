"""claude-074 - A row of three beach umbrellas with lounge chairs on sand."""

import bpy
import bmesh
import math
import random
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


def cyl(name, r, h, loc, rot=(0, 0, 0), m=None, verts=16):
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


def group(parts, name, loc, rot):
    """Parent locally built parts under an empty placed in the scene."""
    e = bpy.data.objects.new(name, None)
    e.empty_display_size = 0.3
    e.location = loc
    e.rotation_euler = rot
    bpy.context.collection.objects.link(e)
    for ob in parts:
        ob.parent = e
    return e


def make_canopy(idx, col_a, col_b):
    """Scalloped eight panel parasol canopy, alternating stripe materials."""
    R, rim_z, apex_z = 1.38, 1.62, 2.12
    n = 16                                  # 8 ribs + 8 scallop midpoints
    me = bpy.data.meshes.new("Canopy_%d" % idx)
    bm = bmesh.new()
    apex = bm.verts.new((0.0, 0.0, apex_z))
    ring1, ring2 = [], []
    for i in range(n):
        a = 2.0 * math.pi * i / n
        rib = (i % 2 == 0)
        r1 = 0.46 * R
        z1 = apex_z - (0.20 if rib else 0.235)
        ring1.append(bm.verts.new((r1 * math.cos(a), r1 * math.sin(a), z1)))
        r2 = R if rib else 0.955 * R
        z2 = rim_z if rib else rim_z - 0.115
        ring2.append(bm.verts.new((r2 * math.cos(a), r2 * math.sin(a), z2)))
    for i in range(n):
        j = (i + 1) % n
        slot = (i // 2) % 2
        f = bm.faces.new((apex, ring1[i], ring1[j]))
        f.material_index = slot
        f = bm.faces.new((ring1[i], ring2[i], ring2[j], ring1[j]))
        f.material_index = slot
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("Canopy_%d" % idx, me)
    bpy.context.collection.objects.link(ob)
    me.materials.append(col_a)
    me.materials.append(col_b)
    so = ob.modifiers.new("Solidify", 'SOLIDIFY')
    so.thickness = 0.012
    so.offset = 0.0
    smooth(ob, 55.0)
    return ob, R, rim_z, apex_z


def make_umbrella(idx, loc, rz, tilt, col_a, col_b, pole_m, rib_m):
    canopy, R, rim_z, apex_z = make_canopy(idx, col_a, col_b)
    parts = [canopy]
    parts.append(cyl("Pole_%d_low" % idx, 0.032, 1.30, (0.0, 0.0, 0.50), m=pole_m, verts=14))
    parts.append(cyl("Pole_%d_up" % idx, 0.026, 1.20, (0.0, 0.0, 1.55), m=pole_m, verts=14))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.045, segments=16, ring_count=8,
                                         location=(0.0, 0.0, apex_z + 0.10))
    finial = bpy.context.object
    finial.name = "Finial_%d" % idx
    finial.data.materials.append(pole_m)
    smooth(finial)
    parts.append(finial)
    parts.append(cyl("Hub_%d" % idx, 0.05, 0.10, (0.0, 0.0, apex_z - 0.16), m=pole_m, verts=12))
    parts.append(cyl("Runner_%d" % idx, 0.045, 0.14, (0.0, 0.0, 1.42), m=pole_m, verts=12))
    for k in range(8):
        a = 2.0 * math.pi * k / 8.0
        p1 = (0.42 * R * math.cos(a) * 0.12, 0.42 * R * math.sin(a) * 0.12, apex_z - 0.14)
        p2 = (R * math.cos(a), R * math.sin(a), rim_z - 0.005)
        parts.append(tube("Rib_%d_%d" % (idx, k), p1, p2, 0.009, m=rib_m, verts=8))
        # stretcher from the runner out to mid rib
        mp = (0.55 * R * math.cos(a), 0.55 * R * math.sin(a), rim_z + 0.30)
        parts.append(tube("Stretcher_%d_%d" % (idx, k),
                          (0.05 * math.cos(a), 0.05 * math.sin(a), 1.45), mp,
                          0.007, m=rib_m, verts=6))
    return group(parts, "Umbrella_%d" % idx, loc, (tilt, 0.0, rz))


def make_chair(idx, loc, rz, frame_m, fabric_m, towel_m=None):
    parts = []
    p0 = (0.0, -0.72, 0.36)
    p1 = (0.0, 0.30, 0.38)
    p2 = (0.0, 0.66, 0.94)
    for sx in (-1.0, 1.0):
        x = sx * 0.32
        parts.append(tube("Rail_%d" % idx, (x, p0[1], p0[2]), (x, p1[1], p1[2]), 0.022, m=frame_m))
        parts.append(tube("Back_%d" % idx, (x, p1[1], p1[2]), (x, p2[1], p2[2]), 0.022, m=frame_m))
        parts.append(tube("LegF_%d" % idx, (x, -0.62, 0.37), (x, -0.72, 0.02), 0.02, m=frame_m))
        parts.append(tube("LegR_%d" % idx, (x, 0.26, 0.375), (x, 0.36, 0.02), 0.02, m=frame_m))
        parts.append(tube("ArmPost_%d" % idx, (x, -0.10, 0.37), (x, -0.10, 0.60), 0.018, m=frame_m))
        parts.append(tube("Arm_%d" % idx, (x, -0.30, 0.60), (x, 0.33, 0.66), 0.018, m=frame_m))
    parts.append(tube("CrossF_%d" % idx, (-0.32, -0.72, 0.03), (0.32, -0.72, 0.03), 0.018, m=frame_m))
    parts.append(tube("CrossR_%d" % idx, (-0.32, 0.36, 0.03), (0.32, 0.36, 0.03), 0.018, m=frame_m))
    parts.append(tube("TopBar_%d" % idx, (-0.32, 0.66, 0.94), (0.32, 0.66, 0.94), 0.022, m=frame_m))

    y = -0.66
    while y < 0.26:
        z = 0.36 + (y + 0.72) / 1.02 * 0.02 + 0.028
        parts.append(box("Slat_%d" % idx, (0.62, 0.075, 0.018), (0.0, y, z),
                         m=fabric_m, bevel=0.004))
        y += 0.113
    theta = math.atan2(0.56, 0.36)
    d = Vector((0.0, 0.36, 0.56)).normalized()
    nrm = Vector((0.0, -math.sin(theta), math.cos(theta)))
    base = Vector((0.0, 0.30, 0.38))
    t = 0.06
    while t < 0.64:
        c = base + d * t + nrm * 0.03
        parts.append(box("BackSlat_%d" % idx, (0.62, 0.075, 0.018), tuple(c),
                         rot=(theta, 0.0, 0.0), m=fabric_m, bevel=0.004))
        t += 0.113

    if towel_m is not None:
        parts.append(box("Towel_%d" % idx, (0.52, 0.80, 0.022), (0.02, -0.24, 0.42),
                         rot=(0.02, 0.0, 0.05), m=towel_m, bevel=0.008))
    return group(parts, "Chair_%d" % idx, loc, (0.0, 0.0, rz))


def build():
    reset()
    random.seed(7)
    w = bpy.data.worlds.new("World")
    w.use_nodes = True
    bgn = w.node_tree.nodes["Background"]
    bgn.inputs[0].default_value = (0.45, 0.62, 0.90, 1.0)
    bgn.inputs[1].default_value = 1.8
    bpy.context.scene.world = w

    sand_m = mat("Sand", (0.80, 0.72, 0.55), 0.95)
    sea_m = mat("Sea", (0.06, 0.32, 0.42), 0.12)
    pole_m = mat("PoleAlu", (0.72, 0.73, 0.75), 0.30, 0.9)
    rib_m = mat("Ribs", (0.55, 0.40, 0.24), 0.6)
    frame_m = mat("ChairFrame", (0.88, 0.88, 0.86), 0.35, 0.6)
    fabric_m = mat("ChairFabric", (0.90, 0.88, 0.82), 0.8)
    towel_m = mat("Towel", (0.85, 0.32, 0.25), 0.85)
    white = mat("CanopyWhite", (0.93, 0.92, 0.88), 0.75)
    stripes = [mat("CanopyRed", (0.78, 0.13, 0.12), 0.75),
               mat("CanopyBlue", (0.10, 0.32, 0.66), 0.75),
               mat("CanopyYellow", (0.90, 0.68, 0.10), 0.75)]

    bpy.ops.mesh.primitive_grid_add(x_subdivisions=140, y_subdivisions=140, size=44.0,
                                    location=(0.0, 0.0, 0.0))
    sand = bpy.context.object
    sand.name = "Sand"
    sand.data.materials.append(sand_m)
    tex = bpy.data.textures.new("SandNoise", 'CLOUDS')
    tex.noise_scale = 1.4
    tex.noise_depth = 3
    dsp = sand.modifiers.new("Displace", 'DISPLACE')
    dsp.texture = tex
    dsp.strength = 0.16
    dsp.mid_level = 0.5
    for p in sand.data.polygons:
        p.use_smooth = True

    box("Sea", (70.0, 30.0, 0.1), (0.0, 30.0, -0.12), m=sea_m)

    for i in range(3):
        x = -4.2 + i * 4.2
        rz = math.radians(random.uniform(-25.0, 25.0))
        tilt = math.radians(random.uniform(4.0, 11.0))
        make_umbrella(i, (x, 0.0, 0.0), rz, tilt, stripes[i], white, pole_m, rib_m)

        for k, sx in enumerate((-1.0, 1.0)):
            cx = x + sx * 1.02 + random.uniform(-0.08, 0.08)
            cy = -0.35 + random.uniform(-0.15, 0.2)
            crz = math.radians(180.0 + sx * random.uniform(6.0, 20.0))
            make_chair(i * 2 + k, (cx, cy, 0.0), crz, frame_m, fabric_m,
                       towel_m if (i + k) % 3 == 0 else None)

    # a beach ball for scale
    ball = mat("Ball", (0.95, 0.55, 0.15), 0.4)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.17, segments=28, ring_count=16,
                                         location=(1.9, -2.3, 0.17))
    b = bpy.context.object
    b.name = "BeachBall"
    b.data.materials.append(ball)
    smooth(b)

    ld = bpy.data.lights.new("Sun", 'SUN')
    ld.energy = 5.5
    ld.angle = math.radians(1.0)
    ld.color = (1.0, 0.96, 0.88)
    sun = bpy.data.objects.new("Sun", ld)
    sun.rotation_euler = (math.radians(42.0), math.radians(5.0), math.radians(-40.0))
    bpy.context.collection.objects.link(sun)

    cd = bpy.data.cameras.new("Camera")
    cd.lens = 40.0
    cam = bpy.data.objects.new("Camera", cd)
    bpy.context.collection.objects.link(cam)
    cam.location = (8.2, -9.6, 3.4)
    cam.rotation_euler = (Vector((-0.4, -0.2, 1.15)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam


if __name__ == "__main__":
    build()
