import bpy, bmesh, math
from mathutils import Vector, Matrix


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in list(coll):
            if item.users == 0:
                coll.remove(item)


def make_material(name, color, roughness=0.45, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    b.inputs["Roughness"].default_value = roughness
    b.inputs["Metallic"].default_value = metallic
    return m


def new_object(name, bm, material, location=(0, 0, 0), rotation=(0, 0, 0), smooth=True):
    me = bpy.data.meshes.new(name + "_mesh")
    bm.to_mesh(me)
    bm.free()
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    ob.location = location
    ob.rotation_euler = rotation
    ob.data.materials.append(material)
    bpy.context.collection.objects.link(ob)
    return ob


def loft(bm, rings, cap=True, closed=False):
    vr = [[bm.verts.new(p) for p in ring] for ring in rings]
    pairs = list(zip(vr, vr[1:]))
    if closed:
        pairs.append((vr[-1], vr[0]))
    for a, b in pairs:
        n = len(a)
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((a[i], a[j], b[j], b[i]))
    if cap and not closed:
        bm.faces.new(list(reversed(vr[0])))
        bm.faces.new(vr[-1])
    bm.normal_update()


def axis_euler(axis):
    return Vector(axis).normalized().to_track_quat('Z', 'Y').to_euler()


def add_cylinder(name, radius, depth, center, axis, material, seg=20):
    bm = bmesh.new()
    rings = []
    for z in (-depth * 0.5, depth * 0.5):
        rings.append([Vector((radius * math.cos(2 * math.pi * i / seg),
                              radius * math.sin(2 * math.pi * i / seg), z)) for i in range(seg)])
    loft(bm, rings)
    return new_object(name, bm, material, center, axis_euler(axis))


def add_box(name, size, center, material, rotation=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    return new_object(name, bm, material, center, rotation, smooth=False)


def add_torus(name, major, minor, center, axis, material, mseg=24, nseg=10):
    bm = bmesh.new()
    rings = []
    for i in range(mseg):
        a = 2 * math.pi * i / mseg
        out = Vector((math.cos(a), math.sin(a), 0.0))
        hub = out * major
        ring = []
        for j in range(nseg):
            b = 2 * math.pi * j / nseg
            ring.append(hub + out * (minor * math.cos(b)) + Vector((0.0, 0.0, minor * math.sin(b))))
        rings.append(ring)
    loft(bm, rings, cap=False, closed=True)
    return new_object(name, bm, material, center, axis_euler(axis))


def fillet_path(pts, radius, seg=7):
    """Replace sharp corners of a polyline with circular arcs (pipe elbows)."""
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        c = pts[i]
        d1 = (pts[i - 1] - c).normalized()
        d2 = (pts[i + 1] - c).normalized()
        ang = d1.angle(d2)
        axis = d1.cross(d2)
        if ang < 1e-3 or abs(ang - math.pi) < 1e-3 or axis.length < 1e-9:
            out.append(c)
            continue
        half = ang * 0.5
        tan_len = min(radius / math.tan(half),
                      (pts[i - 1] - c).length * 0.45, (pts[i + 1] - c).length * 0.45)
        r = tan_len * math.tan(half)
        center = c + (d1 + d2).normalized() * (r / math.sin(half))
        v1 = (c + d1 * tan_len) - center
        v2 = (c + d2 * tan_len) - center
        total = v1.angle(v2)
        axis.normalize()
        for k in range(seg + 1):
            out.append(center + (Matrix.Rotation(total * k / seg, 4, axis) @ v1))
    out.append(pts[-1])
    clean = [out[0]]
    for p in out[1:]:
        if (p - clean[-1]).length > 1e-4:
            clean.append(p)
    return clean


def add_tube(name, waypoints, radius, material, fillet=0.9, seg=16):
    pts = fillet_path([Vector(p) for p in waypoints], fillet)
    n = len(pts)
    tangents = []
    for i in range(n):
        if i == 0:
            t = pts[1] - pts[0]
        elif i == n - 1:
            t = pts[-1] - pts[-2]
        else:
            t = pts[i + 1] - pts[i - 1]
        tangents.append(t.normalized())
    up = Vector((0.0, 0.0, 1.0))
    if abs(tangents[0].dot(up)) > 0.9:
        up = Vector((1.0, 0.0, 0.0))
    ref = (up - tangents[0] * tangents[0].dot(up)).normalized()
    bm = bmesh.new()
    rings = []
    for i, p in enumerate(pts):
        t = tangents[i]
        ref = ref - t * ref.dot(t)
        if ref.length < 1e-6:
            helper = Vector((0.0, 0.0, 1.0)) if abs(t.z) < 0.9 else Vector((1.0, 0.0, 0.0))
            ref = t.cross(helper)
        ref.normalize()
        side = t.cross(ref)
        rings.append([p + ref * (radius * math.cos(2 * math.pi * k / seg))
                      + side * (radius * math.sin(2 * math.pi * k / seg)) for k in range(seg)])
    loft(bm, rings)
    return new_object(name, bm, material)


def join_objects(name, objs):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    objs[0].name = name
    return objs[0]


def add_valve(name, center, pipe_axis, size, mat_body, mat_wheel):
    center = Vector(center)
    up = Vector((0.0, 0.0, 1.0)) if abs(Vector(pipe_axis).normalized().z) < 0.8 else Vector((1.0, 0.0, 0.0))
    parts = [add_cylinder(name + "_Body", size * 0.62, size * 1.15, center, pipe_axis, mat_body)]
    parts.append(add_cylinder(name + "_Bonnet", size * 0.34, size * 1.0,
                              center + up * (size * 0.8), up, mat_body))
    parts.append(add_cylinder(name + "_Stem", size * 0.09, size * 1.3,
                              center + up * (size * 1.6), up, mat_wheel))
    hub_c = center + up * (size * 2.1)
    parts.append(add_torus(name + "_Rim", size * 0.62, size * 0.09, hub_c, up, mat_wheel))
    parts.append(add_cylinder(name + "_Hub", size * 0.16, size * 0.16, hub_c, up, mat_wheel))
    frame = up.to_track_quat('Z', 'Y').to_matrix()
    for k in range(3):
        a = 2 * math.pi * k / 3
        radial = frame @ Vector((math.cos(a), math.sin(a), 0.0))
        parts.append(add_cylinder(name + "_Spoke%d" % k, size * 0.06, size * 1.14,
                                  hub_c, radial, mat_wheel, seg=8))
    return join_objects(name, parts)


clear_scene()
mat_pipe = make_material("PipeSteel", (0.58, 0.60, 0.63), 0.38, 0.85)
mat_branch = make_material("PipePainted", (0.20, 0.42, 0.62), 0.45, 0.25)
mat_valve = make_material("ValveBody", (0.72, 0.32, 0.16), 0.50, 0.30)
mat_wheel = make_material("ValveWheel", (0.14, 0.14, 0.16), 0.42, 0.60)
mat_struct = make_material("StructureGrey", (0.40, 0.40, 0.42), 0.70, 0.10)
mat_floor = make_material("FloorConcrete", (0.55, 0.54, 0.51), 0.90)

add_box("Floor_Slab", (26.0, 14.0, 0.4), (0.0, 1.0, -0.2), mat_floor)

MAIN = [(-9.5, 0.0, 1.0), (-9.5, 0.0, 4.6), (-2.0, 0.0, 4.6),
        (-2.0, 0.0, 1.7), (5.0, 0.0, 1.7), (5.0, 0.0, 5.2), (9.8, 0.0, 5.2)]
add_tube("Pipe_MainRun", MAIN, 0.42, mat_pipe, fillet=1.0)
add_tube("Pipe_Branch", [(-6.0, 2.6, 3.1), (2.2, 2.6, 3.1),
                         (2.2, 2.6, 6.4), (9.0, 2.6, 6.4)], 0.26, mat_branch, fillet=0.7)
add_tube("Pipe_BranchRiser", [(-6.0, 2.6, 0.2), (-6.0, 2.6, 3.1)], 0.26, mat_branch, fillet=0.5)

# bolted flange pairs along the runs
FLANGES = [((-6.2, 0.0, 4.6), (1, 0, 0), 0.42), ((1.0, 0.0, 1.7), (1, 0, 0), 0.42),
           ((5.0, 0.0, 3.4), (0, 0, 1), 0.42), ((6.0, 2.6, 6.4), (1, 0, 0), 0.26)]
for idx, (loc, axis, rad) in enumerate(FLANGES):
    off = Vector(axis).normalized() * 0.22
    add_cylinder("Flange_%d_A" % idx, rad * 1.9, 0.10, Vector(loc), axis, mat_pipe)
    add_cylinder("Flange_%d_B" % idx, rad * 1.9, 0.10, Vector(loc) + off, axis, mat_pipe)
    add_cylinder("Flange_%d_Spacer" % idx, rad * 1.15, 0.24, Vector(loc) + off * 0.5, axis, mat_pipe)

add_valve("Valve_Main", (1.9, 0.0, 1.7), (1, 0, 0), 0.9, mat_valve, mat_wheel)
add_valve("Valve_Riser", (5.0, 0.0, 4.2), (0, 0, 1), 0.8, mat_valve, mat_wheel)
add_valve("Valve_Branch", (-1.4, 2.6, 3.1), (1, 0, 0), 0.6, mat_valve, mat_wheel)

# pipe supports: legs with saddle plates under the horizontal runs
SUPPORTS = [(-5.0, 0.0, 4.6, 0.42), (-0.2, 0.0, 1.7, 0.42), (3.6, 0.0, 1.7, 0.42),
            (8.2, 0.0, 5.2, 0.42), (-3.5, 2.6, 3.1, 0.26), (6.6, 2.6, 6.4, 0.26)]
for idx, (x, y, z, r) in enumerate(SUPPORTS):
    add_box("Support_%d_Leg" % idx, (0.22, 0.22, z - r), (x, y, (z - r) * 0.5), mat_struct)
    add_box("Support_%d_Saddle" % idx, (0.5, 0.7, 0.12), (x, y, z - r - 0.02), mat_struct)
    add_box("Support_%d_Foot" % idx, (0.6, 0.6, 0.08), (x, y, 0.04), mat_struct)
add_box("Support_Brace", (0.16, 3.0, 0.16), (-3.5, 1.3, 2.6), mat_struct)

key = bpy.data.objects.new("KeyLight", bpy.data.lights.new("KeyLightData", 'AREA'))
key.data.energy = 900.0
key.data.size = 8.0
key.location = (8.0, -10.0, 12.0)
key.rotation_euler = (math.radians(45.0), 0.0, math.radians(30.0))
bpy.context.collection.objects.link(key)

sun = bpy.data.objects.new("FillSun", bpy.data.lights.new("FillSunData", 'SUN'))
sun.data.energy = 2.0
sun.rotation_euler = (math.radians(60.0), 0.0, math.radians(-40.0))
bpy.context.collection.objects.link(sun)

cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 42.0
cam = bpy.data.objects.new("Camera", cam_data)
cam.location = (16.0, -17.0, 10.5)
cam.rotation_euler = (Vector((0.0, 1.0, 3.2)) - Vector(cam.location)).to_track_quat('-Z', 'Y').to_euler()
bpy.context.collection.objects.link(cam)
bpy.context.scene.camera = cam
