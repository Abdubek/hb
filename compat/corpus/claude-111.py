"""claude-111 - Radial array of turbine blades around a central hub inside a mechanical housing.

Builds:
  * a lathed hub with nose cone and drive shaft
  * 13 lofted airfoil rotor blades in a radial array
  * 17 downstream stator vanes attached to the casing
  * a lathed casing with bolted flanges, struts and mounting feet
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix


# --------------------------------------------------------------------------- setup
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scn = bpy.context.scene
    scn.unit_settings.system = 'METRIC'


def make_material(name, color, metallic=0.0, rough=0.5, emit=None, strength=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    p.inputs["Metallic"].default_value = metallic
    p.inputs["Roughness"].default_value = rough
    if emit is not None:
        p.inputs["Emission Color"].default_value = (emit[0], emit[1], emit[2], 1.0)
        p.inputs["Emission Strength"].default_value = strength
    return m


def new_object(name, verts, faces, mats=(), smooth=False):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate()
    me.update()
    for m in mats:
        me.materials.append(m)
    if smooth:
        for poly in me.polygons:
            poly.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    return ob


def recalc_normals(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()


BOX_FACES = ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1),
             (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3))


def add_box(verts, faces, center, size, rot_z=0.0):
    mtx = Matrix.Translation(Vector(center)) @ Matrix.Rotation(rot_z, 4, 'Z')
    off = len(verts)
    sx, sy, sz = size
    for dx in (-0.5, 0.5):
        for dy in (-0.5, 0.5):
            for dz in (-0.5, 0.5):
                verts.append(tuple(mtx @ Vector((dx * sx, dy * sy, dz * sz))))
    for f in BOX_FACES:
        faces.append(tuple(off + i for i in f))


def add_beam(verts, faces, p0, p1, w, h, up=(0.0, 0.0, 1.0)):
    """Rectangular prism spanning p0->p1 with cross section w (side) x h (up)."""
    p0 = Vector(p0)
    p1 = Vector(p1)
    d = p1 - p0
    if d.length < 1e-9:
        return
    d.normalize()
    side = d.cross(Vector(up))
    if side.length < 1e-6:
        side = d.cross(Vector((1.0, 0.0, 0.0)))
    side.normalize()
    upv = side.cross(d).normalized()
    off = len(verts)
    for base in (p0, p1):
        for s, u in ((-1, -1), (-1, 1), (1, 1), (1, -1)):
            verts.append(tuple(base + side * (s * w * 0.5) + upv * (u * h * 0.5)))
    faces.append((off + 3, off + 2, off + 1, off + 0))
    faces.append((off + 4, off + 5, off + 6, off + 7))
    for i in range(4):
        j = (i + 1) % 4
        faces.append((off + i, off + 4 + i, off + 4 + j, off + j))


def lathe(verts, faces, profile, segments=72):
    """Revolve a closed (r, z) profile around the Z axis."""
    off = len(verts)
    n = len(profile)
    for s in range(segments):
        a = 2.0 * math.pi * s / segments
        ca, sa = math.cos(a), math.sin(a)
        for (r, z) in profile:
            verts.append((r * ca, r * sa, z))
    for s in range(segments):
        s2 = (s + 1) % segments
        for i in range(n):
            i2 = (i + 1) % n
            faces.append((off + s * n + i, off + s * n + i2,
                          off + s2 * n + i2, off + s2 * n + i))


def add_cylinder(verts, faces, center, radius, height, segments=20, axis='Z'):
    off = len(verts)
    cx, cy, cz = center
    for k, h in enumerate((-0.5, 0.5)):
        for s in range(segments):
            a = 2.0 * math.pi * s / segments
            u, v = radius * math.cos(a), radius * math.sin(a)
            w = h * height
            if axis == 'Z':
                verts.append((cx + u, cy + v, cz + w))
            elif axis == 'Y':
                verts.append((cx + u, cy + w, cz + v))
            else:
                verts.append((cx + w, cy + u, cz + v))
    for s in range(segments):
        s2 = (s + 1) % segments
        faces.append((off + s, off + s2, off + segments + s2, off + segments + s))
    faces.append(tuple(off + segments - 1 - s for s in range(segments)))
    faces.append(tuple(off + segments + s for s in range(segments)))


# --------------------------------------------------------------------------- airfoil
def naca_profile(n_side=22, thick=0.13, camber=0.055, cpos=0.4):
    xs = [0.5 * (1.0 - math.cos(math.pi * i / (n_side - 1))) for i in range(n_side)]

    def yt(x):
        return 5.0 * thick * (0.2969 * math.sqrt(max(x, 0.0)) - 0.1260 * x
                              - 0.3516 * x * x + 0.2843 * x ** 3 - 0.1015 * x ** 4)

    def yc(x):
        if x < cpos:
            return camber / (cpos * cpos) * (2.0 * cpos * x - x * x)
        return camber / ((1.0 - cpos) ** 2) * ((1.0 - 2.0 * cpos) + 2.0 * cpos * x - x * x)

    upper = [(x, yc(x) + yt(x)) for x in xs]
    lower = [(x, yc(x) - yt(x)) for x in reversed(xs)]
    return upper + lower[1:-1]


def add_blade(verts, faces, profile, r0, r1, chord, taper, twist0, twist1,
              sections=12, rot=0.0, sweep=0.0, anchor=0.4):
    """Loft an airfoil radially outward along +X, then rotate about Z by `rot`."""
    rz = Matrix.Rotation(rot, 4, 'Z')
    n = len(profile)
    rings = []
    for i in range(sections + 1):
        s = i / sections
        r = r0 + (r1 - r0) * s
        ch = chord * (1.0 - taper * s)
        tw = math.radians(twist0 + (twist1 - twist0) * s)
        sw = sweep * s * s
        ring = []
        for (u, v) in profile:
            c = (u - anchor) * ch
            t = v * ch
            y = c * math.cos(tw) - t * math.sin(tw) + sw
            z = c * math.sin(tw) + t * math.cos(tw)
            ring.append(len(verts))
            verts.append(tuple(rz @ Vector((r, y, z))))
        rings.append(ring)
    for i in range(sections):
        a, b = rings[i], rings[i + 1]
        for j in range(n):
            j2 = (j + 1) % n
            faces.append((a[j], a[j2], b[j2], b[j]))
    # fan caps at root and tip
    for ring, flip in ((rings[0], True), (rings[-1], False)):
        cx = sum(verts[k][0] for k in ring) / n
        cy = sum(verts[k][1] for k in ring) / n
        cz = sum(verts[k][2] for k in ring) / n
        c = len(verts)
        verts.append((cx, cy, cz))
        for j in range(n):
            j2 = (j + 1) % n
            faces.append((c, ring[j2], ring[j]) if flip else (c, ring[j], ring[j2]))


# --------------------------------------------------------------------------- build
reset_scene()

mat_case = make_material("Casing Steel", (0.42, 0.44, 0.47), metallic=1.0, rough=0.38)
mat_case_in = make_material("Casing Liner", (0.24, 0.25, 0.28), metallic=1.0, rough=0.55)
mat_blade = make_material("Blade Alloy", (0.72, 0.74, 0.78), metallic=1.0, rough=0.17)
mat_hub = make_material("Hub Steel", (0.30, 0.31, 0.34), metallic=1.0, rough=0.30)
mat_bolt = make_material("Fastener", (0.18, 0.18, 0.20), metallic=1.0, rough=0.45)
mat_vane = make_material("Stator Vane", (0.55, 0.52, 0.46), metallic=1.0, rough=0.42)
mat_floor = make_material("Shop Floor", (0.13, 0.14, 0.15), metallic=0.0, rough=0.72)

R_IN = 1.40
R_OUT = 1.62
R_FLANGE = 1.84
Z_LO, Z_HI = -0.78, 0.98
FT = 0.10
BLADES = 13
VANES = 17

# --- hub + shaft ------------------------------------------------------------
hub_profile = [
    (0.05, 0.86), (0.14, 0.82), (0.30, 0.60), (0.44, 0.32),
    (0.53, 0.10), (0.555, -0.06), (0.555, -0.42), (0.50, -0.52),
    (0.30, -0.58), (0.05, -0.58),
]
v, f = [], []
lathe(v, f, hub_profile, segments=72)
add_cylinder(v, f, (0.0, 0.0, -1.05), 0.155, 1.10, segments=28, axis='Z')
add_cylinder(v, f, (0.0, 0.0, -0.60), 0.235, 0.10, segments=32, axis='Z')
hub = new_object("Rotor_Hub", v, f, [mat_hub], smooth=True)
recalc_normals(hub)

# --- rotor blades -----------------------------------------------------------
prof = naca_profile(n_side=22, thick=0.135, camber=0.06)
v, f = [], []
for i in range(BLADES):
    add_blade(v, f, prof, 0.50, 1.325,
              chord=0.62, taper=0.40, twist0=54.0, twist1=14.0,
              sections=14, rot=2.0 * math.pi * i / BLADES, sweep=0.11)
blades = new_object("Rotor_Blades", v, f, [mat_blade], smooth=True)
recalc_normals(blades)

# blade root platforms so the array reads as a bladed disc
v, f = [], []
for i in range(BLADES):
    a = 2.0 * math.pi * i / BLADES
    add_box(v, f, (0.56 * math.cos(a), 0.56 * math.sin(a), 0.0),
            (0.09, 0.30, 0.66), rot_z=a)
roots = new_object("Blade_Roots", v, f, [mat_hub])
recalc_normals(roots)

# --- stator vanes (fixed, downstream of the rotor) --------------------------
vane_prof = naca_profile(n_side=16, thick=0.10, camber=0.03)
v, f = [], []
for i in range(VANES):
    a = 2.0 * math.pi * (i + 0.5) / VANES
    off = len(v)
    add_blade(v, f, vane_prof, 0.57, 1.40,
              chord=0.34, taper=0.05, twist0=-30.0, twist1=-30.0,
              sections=4, rot=a, sweep=0.0)
    # shift the whole vane downstream
    for k in range(off, len(v)):
        p = Vector(v[k])
        v[k] = (p.x, p.y, p.z - 0.44)
vanes = new_object("Stator_Vanes", v, f, [mat_vane], smooth=True)
recalc_normals(vanes)

# --- casing -----------------------------------------------------------------
case_profile = [
    (R_IN, Z_LO), (R_FLANGE, Z_LO), (R_FLANGE, Z_LO + FT), (R_OUT, Z_LO + FT),
    (R_OUT, -0.30), (R_OUT + 0.06, -0.20), (R_OUT + 0.06, 0.28), (R_OUT, 0.38),
    (R_OUT, Z_HI - FT), (R_FLANGE, Z_HI - FT), (R_FLANGE, Z_HI), (R_IN, Z_HI),
]
v, f = [], []
lathe(v, f, case_profile, segments=96)
casing = new_object("Casing", v, f, [mat_case], smooth=True)
recalc_normals(casing)

# inner wear liner ring, just outboard of the blade tips
liner_profile = [(R_IN - 0.015, -0.34), (R_IN, -0.34), (R_IN, 0.42), (R_IN - 0.015, 0.42)]
v, f = [], []
lathe(v, f, liner_profile, segments=96)
liner = new_object("Tip_Liner", v, f, [mat_case_in], smooth=True)
recalc_normals(liner)

# --- flange bolts (linked duplicates) --------------------------------------
v, f = [], []
add_cylinder(v, f, (0.0, 0.0, 0.0), 0.046, 0.055, segments=6, axis='Z')
add_cylinder(v, f, (0.0, 0.0, -0.05), 0.026, 0.12, segments=10, axis='Z')
bolt = new_object("Flange_Bolt_T00", v, f, [mat_bolt])
recalc_normals(bolt)
bolt_mesh = bolt.data
bolt.matrix_world = Matrix.Translation(Vector((R_FLANGE - 0.10, 0.0, Z_HI + 0.028)))

for z, tag in ((Z_HI + 0.028, 'T'), (Z_LO - 0.028, 'B')):
    for i in range(20):
        if tag == 'T' and i == 0:
            continue
        a = 2.0 * math.pi * i / 20
        ob = bpy.data.objects.new("Flange_Bolt_%s%02d" % (tag, i), bolt_mesh)
        bpy.context.collection.objects.link(ob)
        ob.matrix_world = Matrix.Translation(Vector(
            ((R_FLANGE - 0.10) * math.cos(a), (R_FLANGE - 0.10) * math.sin(a), z)))

# --- support struts, feet and inspection cover -----------------------------
v, f = [], []
for i in range(3):
    a = 2.0 * math.pi * i / 3 + 0.35
    p0 = (0.55 * math.cos(a), 0.55 * math.sin(a), -0.66)
    p1 = (R_IN * math.cos(a), R_IN * math.sin(a), -0.66)
    add_beam(v, f, p0, p1, 0.09, 0.16, up=(0.0, 0.0, 1.0))
for sx in (-1.0, 1.0):
    add_box(v, f, (sx * 1.30, 0.0, Z_LO - 0.20), (0.70, 0.42, 0.30))
    add_box(v, f, (sx * 1.30, 0.0, Z_LO - 0.03), (0.34, 0.30, 0.16))
add_box(v, f, (0.0, R_OUT + 0.045, 0.05), (0.46, 0.10, 0.36))
struts = new_object("Casing_Hardware", v, f, [mat_case])
recalc_normals(struts)

v, f = [], []
for i in range(6):
    a = 2.0 * math.pi * i / 6
    add_cylinder(v, f, (0.22 * math.cos(a), R_OUT + 0.09, 0.05 + 0.22 * math.sin(a)),
                 0.022, 0.05, segments=8, axis='Y')
cover_bolts = new_object("Cover_Bolts", v, f, [mat_bolt])
recalc_normals(cover_bolts)

# --- floor ------------------------------------------------------------------
v = [(-7.0, -7.0, Z_LO - 0.35), (7.0, -7.0, Z_LO - 0.35),
     (7.0, 7.0, Z_LO - 0.35), (-7.0, 7.0, Z_LO - 0.35)]
new_object("Floor", v, [(0, 1, 2, 3)], [mat_floor])


# --------------------------------------------------------------------------- lights
def add_area(name, loc, target, size, energy, color=(1.0, 1.0, 1.0)):
    d = bpy.data.lights.new(name, 'AREA')
    d.size = size
    d.energy = energy
    d.color = color
    ob = bpy.data.objects.new(name, d)
    bpy.context.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return ob


add_area("Key", (3.4, -4.2, 4.6), (0.0, 0.0, 0.1), 4.5, 1400.0)
add_area("Fill", (-4.6, -2.6, 1.4), (0.0, 0.0, 0.0), 3.5, 420.0, (0.72, 0.80, 1.0))
add_area("Rim", (-1.6, 4.8, 3.2), (0.0, 0.0, 0.3), 3.0, 700.0, (1.0, 0.92, 0.82))

sun = bpy.data.lights.new("Sun", 'SUN')
sun.energy = 1.6
sun_ob = bpy.data.objects.new("Sun", sun)
bpy.context.collection.objects.link(sun_ob)
sun_ob.rotation_euler = (math.radians(52.0), 0.0, math.radians(38.0))

world = bpy.data.worlds.new("World")
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.05, 0.055, 0.065, 1.0)
bg.inputs[1].default_value = 1.0
bpy.context.scene.world = world

# --------------------------------------------------------------------------- camera
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 62.0
cam = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam)
cam.location = (3.55, -4.55, 2.35)
cam.rotation_euler = (Vector((0.0, 0.0, 0.05)) - Vector(cam.location)).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam

print("claude-111: %d blades, %d stator vanes, %d objects"
      % (BLADES, VANES, len(bpy.data.objects)))
