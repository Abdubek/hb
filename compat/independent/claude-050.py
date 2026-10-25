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


def new_object(name, bm, material, location=(0, 0, 0), rotation=(0, 0, 0)):
    me = bpy.data.meshes.new(name + "_mesh")
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    ob.location = location
    ob.rotation_euler = rotation
    ob.data.materials.append(material)
    bpy.context.collection.objects.link(ob)
    return ob


def loft(bm, rings, cap=True):
    vr = [[bm.verts.new(p) for p in ring] for ring in rings]
    for a, b in zip(vr, vr[1:]):
        n = len(a)
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((a[i], a[j], b[j], b[i]))
    if cap:
        bm.faces.new(list(reversed(vr[0])))
        bm.faces.new(vr[-1])
    bm.normal_update()


def circle_z(radius, z, n=24):
    return [Vector((radius * math.cos(2 * math.pi * i / n),
                    radius * math.sin(2 * math.pi * i / n), z)) for i in range(n)]


def circle_y(radius, y, n=24):
    return [Vector((radius * math.cos(2 * math.pi * i / n), y,
                    radius * math.sin(2 * math.pi * i / n))) for i in range(n)]


def super_ring(w, h, y, n=20, e=3.0):
    """Superelliptical cross section in XZ, positioned along the rotor axis Y."""
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        c, s = math.cos(a), math.sin(a)
        x = w * math.copysign(abs(c) ** (2.0 / e), c)
        z = h * math.copysign(abs(s) ** (2.0 / e), s)
        pts.append(Vector((x, y, z)))
    return pts


def blade_section(chord, thick, twist_deg, z, n=18):
    rot = Matrix.Rotation(math.radians(twist_deg), 2)
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        v = rot @ Vector((0.5 * chord * math.cos(a), 0.5 * thick * math.sin(a)))
        pts.append(Vector((v.x, v.y, z)))
    return pts


def add_camera(loc, target, lens=48.0):
    cam = bpy.data.cameras.new("Camera")
    cam.lens = lens
    ob = bpy.data.objects.new("Camera", cam)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(ob)
    bpy.context.scene.camera = ob
    return ob


TOWER_H = 42.0
HUB = Vector((0.0, -1.0, TOWER_H + 1.2))

clear_scene()
mat_shell = make_material("TurbineShell", (0.90, 0.90, 0.88), 0.35)
mat_blade = make_material("BladeSkin", (0.94, 0.94, 0.93), 0.22)
mat_metal = make_material("HubMetal", (0.55, 0.57, 0.60), 0.30, 0.85)
mat_conc = make_material("Concrete", (0.62, 0.60, 0.56), 0.85)

# concrete foundation pad
bm = bmesh.new()
loft(bm, [circle_z(4.6, 0.0, 32), circle_z(4.4, 0.55, 32), circle_z(2.6, 0.8, 32)])
new_object("Foundation_Pad", bm, mat_conc)

# tapered tower
bm = bmesh.new()
rings = []
for i in range(15):
    t = i / 14.0
    rings.append(circle_z(1.95 + (0.82 - 1.95) * (t ** 0.85), 0.7 + t * TOWER_H, 28))
loft(bm, rings)
new_object("Tower_Tapered", bm, mat_shell)

# yaw ring on top of the tower
bm = bmesh.new()
loft(bm, [circle_z(0.95, TOWER_H + 0.6, 28), circle_z(1.05, TOWER_H + 1.0, 28)])
new_object("Yaw_Ring", bm, mat_metal)

# nacelle housing lofted along the rotor axis
bm = bmesh.new()
profile = [(1.05, 1.00, -0.6), (1.45, 1.42, 0.6), (1.55, 1.48, 3.4),
           (1.35, 1.20, 5.6), (0.85, 0.72, 6.6)]
loft(bm, [super_ring(w, h, y) for (w, h, y) in profile])
new_object("Nacelle_Housing", bm, mat_shell, location=(0.0, HUB.y, HUB.z))

# anemometer mast on the nacelle roof
bm = bmesh.new()
loft(bm, [circle_z(0.07, 0.0, 10), circle_z(0.05, 1.6, 10)])
new_object("Anemometer_Mast", bm, mat_metal, location=(0.0, HUB.y + 5.4, HUB.z + 1.15))

# rotor spinner: nose cone pointing along -Y
bm = bmesh.new()
loft(bm, [circle_y(0.16, -3.3, 24), circle_y(0.70, -2.5, 24),
          circle_y(1.10, -1.4, 24), circle_y(1.18, -0.6, 24)])
new_object("Rotor_Spinner", bm, mat_shell, location=HUB)

# three tapered, twisted blades spaced 120 degrees about the rotor axis
SECTIONS = [(0.00, 1.10, 1.10, 22.0), (0.04, 1.30, 1.05, 22.0), (0.12, 2.30, 0.85, 17.0),
            (0.30, 2.05, 0.52, 10.0), (0.55, 1.60, 0.34, 5.0), (0.78, 1.15, 0.22, 2.0),
            (0.93, 0.70, 0.13, 0.5), (1.00, 0.18, 0.05, 0.0)]
BLADE_LEN = 21.0
for b_idx in range(3):
    yaw = math.radians(120.0 * b_idx)
    bm = bmesh.new()
    rings = []
    for frac, chord, thick, twist in SECTIONS:
        sweep = 0.7 * frac * frac
        ring = blade_section(chord, thick, twist, 1.0 + frac * BLADE_LEN)
        rings.append([p + Vector((sweep, 0.0, 0.0)) for p in ring])
    blade = new_object("Blade_%d" % (b_idx + 1), bm, mat_blade,
                       location=HUB, rotation=(0.0, yaw, 0.0))
    bmc = bmesh.new()
    loft(bmc, [circle_z(0.72, 0.55, 20), circle_z(0.72, 1.15, 20)])
    root = new_object("Blade_%d_Root" % (b_idx + 1), bmc, mat_metal,
                      location=HUB, rotation=(0.0, yaw, 0.0))
    root.parent = blade
    root.matrix_parent_inverse = blade.matrix_world.inverted()

sun = bpy.data.objects.new("Sun", bpy.data.lights.new("SunLight", 'SUN'))
sun.data.energy = 4.0
sun.location = (20.0, -20.0, 60.0)
sun.rotation_euler = (math.radians(55.0), 0.0, math.radians(35.0))
bpy.context.collection.objects.link(sun)

add_camera((52.0, -58.0, 30.0), (0.0, 0.0, 27.0))
