"""claude-057 : A street market stall with canopy and produce crates."""
import bpy, bmesh, math, random
from mathutils import Vector, Matrix

random.seed(20250909)


# ------------------------------------------------------------------ helpers
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scn = bpy.context.scene
    try:
        scn.render.engine = 'BLENDER_EEVEE_NEXT'
    except Exception:
        pass
    scn.render.resolution_x, scn.render.resolution_y = 1600, 1000


def mat(name, color, rough=0.5, metal=0.0, emis=None, estr=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    i = m.node_tree.nodes["Principled BSDF"].inputs
    i["Base Color"].default_value = (*color, 1.0)
    i["Roughness"].default_value = rough
    i["Metallic"].default_value = metal
    if emis is not None:
        if "Emission Color" in i:
            i["Emission Color"].default_value = (*emis, 1.0)
        i["Emission Strength"].default_value = estr
    return m


def finish(ob, material=None, bevel=0.0, seg=2, smooth=False):
    if material:
        ob.data.materials.append(material)
    if bevel > 0.0:
        b = ob.modifiers.new("Bevel", 'BEVEL')
        b.width, b.segments = bevel, seg
        b.limit_method = 'ANGLE'
        b.angle_limit = math.radians(50)
    if smooth:
        shade_smooth(ob)
    return ob


def shade_smooth(ob):
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    try:
        bpy.ops.object.shade_auto_smooth(angle=math.radians(35))
    except Exception:
        bpy.ops.object.shade_smooth()


def add_box(name, size, loc=(0, 0, 0), rot=(0, 0, 0), material=None, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    ob = bpy.context.object
    ob.name = name
    ob.data.transform(Matrix.Diagonal(Vector((size[0], size[1], size[2], 1.0))))
    ob.location, ob.rotation_euler = loc, rot
    return finish(ob, material, bevel)


def add_cyl(name, r, d, loc=(0, 0, 0), rot=(0, 0, 0), verts=20, material=None,
            r2=None):
    if r2 is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=d)
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r, radius2=r2, depth=d)
    ob = bpy.context.object
    ob.name = name
    ob.location, ob.rotation_euler = loc, rot
    return finish(ob, material, smooth=True)


def add_ico(name, r, loc, material=None, subd=2):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subd, radius=r, location=loc)
    ob = bpy.context.object
    ob.name = name
    return finish(ob, material, smooth=True)


def join(objs, name):
    objs = [o for o in objs if o is not None]
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    ob = bpy.context.object
    ob.name = name
    return ob


def look_at(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


# ------------------------------------------------------------------ materials
reset_scene()

M_GROUND = mat("Cobble", (0.20, 0.19, 0.18), 0.85)
M_PINE = mat("Pine", (0.68, 0.52, 0.31), 0.68)
M_PINE_D = mat("PineDark", (0.50, 0.36, 0.20), 0.72)
M_POST = mat("PaintedPost", (0.16, 0.17, 0.19), 0.45, 0.35)
M_CANVAS_A = mat("CanvasCream", (0.90, 0.86, 0.74), 0.80)
M_CANVAS_B = mat("CanvasRed", (0.62, 0.13, 0.13), 0.80)
M_CLOTH = mat("SkirtCloth", (0.15, 0.28, 0.24), 0.85)
M_BOARD = mat("Chalkboard", (0.07, 0.08, 0.08), 0.75)
M_CHALK = mat("Chalk", (0.92, 0.92, 0.88), 0.9)
M_METAL = mat("Metal", (0.62, 0.63, 0.65), 0.30, 1.0)
M_PAPER = mat("Paper", (0.86, 0.82, 0.72), 0.85)
M_BULB = mat("Bulb", (1.0, 0.85, 0.6), 0.2, emis=(1.0, 0.78, 0.45), estr=18.0)

PRODUCE = {
    "apple": (mat("Apple", (0.62, 0.06, 0.06), 0.32), 0.042, 1.0),
    "orange": (mat("Orange", (0.86, 0.38, 0.04), 0.55), 0.045, 1.0),
    "lemon": (mat("Lemon", (0.88, 0.78, 0.10), 0.45), 0.036, 1.25),
    "tomato": (mat("Tomato", (0.72, 0.11, 0.08), 0.28), 0.038, 0.85),
    "cabbage": (mat("Cabbage", (0.42, 0.56, 0.22), 0.60), 0.075, 0.9),
    "potato": (mat("Potato", (0.54, 0.42, 0.26), 0.78), 0.048, 0.7),
    "aubergine": (mat("Aubergine", (0.24, 0.10, 0.30), 0.30), 0.050, 0.65),
}

# ------------------------------------------------------------------ ground
bpy.ops.mesh.primitive_plane_add(size=40.0)
finish(bpy.context.object, M_GROUND)
bpy.context.object.name = "Ground"

# ------------------------------------------------------------------ stall frame
POST_R = 0.045
POSTS = [(-1.62, 0.62, 2.58), (1.62, 0.62, 2.58),
         (-1.62, -1.30, 2.24), (1.62, -1.30, 2.24)]
for k, (px, py, ph) in enumerate(POSTS):
    add_cyl("Post%d" % k, POST_R, ph, (px, py, ph * 0.5), verts=14, material=M_POST)
    add_cyl("PostFoot%d" % k, 0.10, 0.04, (px, py, 0.02), verts=14, material=M_METAL)

# eaves rails
add_box("RailBack", (3.34, 0.06, 0.07), (0.0, 0.62, 2.55), material=M_POST)
add_box("RailFront", (3.34, 0.06, 0.07), (0.0, -1.30, 2.21), material=M_POST)
for sx in (-1.62, 1.62):
    add_box("RailSide", (0.06, 1.92, 0.07), (sx, -0.34, 2.38),
            rot=(math.radians(-10), 0, 0), material=M_POST)

# ------------------------------------------------------------------ striped canopy
NSTRIPE, PER, NV = 10, 3, 10
NU = NSTRIPE * PER
X0, X1 = -1.78, 1.78
Y0, Y1 = 0.72, -1.55
Z0, Z1 = 2.60, 2.22

bm = bmesh.new()
grid = []
for j in range(NU + 1):
    u = j / NU
    col = []
    for i in range(NV + 1):
        v = i / NV
        x = X0 + (X1 - X0) * u
        y = Y0 + (Y1 - Y0) * v
        z = Z0 + (Z1 - Z0) * v
        z -= 0.10 * math.sin(math.pi * u) * math.sin(math.pi * v)   # fabric sag
        if v > 0.94:
            z -= 0.05 * abs(math.sin(u * math.pi * NSTRIPE))        # scalloped hem
        col.append(bm.verts.new((x, y, z)))
    grid.append(col)
for j in range(NU):
    for i in range(NV):
        f = bm.faces.new((grid[j][i], grid[j + 1][i], grid[j + 1][i + 1], grid[j][i + 1]))
        f.material_index = (j // PER) % 2
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
me = bpy.data.meshes.new("Canopy")
bm.to_mesh(me)
bm.free()
canopy = bpy.data.objects.new("Canopy", me)
bpy.context.collection.objects.link(canopy)
canopy.data.materials.append(M_CANVAS_A)
canopy.data.materials.append(M_CANVAS_B)
sol = canopy.modifiers.new("Solidify", 'SOLIDIFY')
sol.thickness = 0.012
shade_smooth(canopy)

# valance strip hanging from the front hem
bm = bmesh.new()
vrows = []
for j in range(NU + 1):
    u = j / NU
    x = X0 + (X1 - X0) * u
    top = bm.verts.new((x, Y1, Z1 - 0.05 * abs(math.sin(u * math.pi * NSTRIPE))))
    bot = bm.verts.new((x, Y1 + 0.01, Z1 - 0.26 - 0.06 * abs(math.sin(u * math.pi * NSTRIPE))))
    vrows.append((top, bot))
for j in range(NU):
    f = bm.faces.new((vrows[j][0], vrows[j + 1][0], vrows[j + 1][1], vrows[j][1]))
    f.material_index = (j // PER) % 2
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
me = bpy.data.meshes.new("Valance")
bm.to_mesh(me)
bm.free()
val = bpy.data.objects.new("Valance", me)
bpy.context.collection.objects.link(val)
val.data.materials.append(M_CANVAS_B)
val.data.materials.append(M_CANVAS_A)
val.modifiers.new("Solidify", 'SOLIDIFY').thickness = 0.01

# ------------------------------------------------------------------ counter
COUNTER_Z = 0.94
add_box("CounterTop", (3.10, 1.10, 0.05), (0.0, -0.42, COUNTER_Z), material=M_PINE,
        bevel=0.012)
for px in (-1.40, 0.0, 1.40):
    add_box("CounterLeg", (0.08, 0.08, COUNTER_Z - 0.03),
            (px, -0.05, (COUNTER_Z - 0.03) * 0.5), material=M_PINE_D)
    add_box("CounterLeg2", (0.08, 0.08, COUNTER_Z - 0.03),
            (px, -0.86, (COUNTER_Z - 0.03) * 0.5), material=M_PINE_D)
add_box("CounterBrace", (3.05, 0.06, 0.07), (0.0, -0.86, 0.22), material=M_PINE_D)
add_box("Skirt", (3.12, 0.02, 0.62), (0.0, -0.98, 0.60), material=M_CLOTH)
add_box("UnderShelf", (2.90, 0.70, 0.04), (0.0, -0.42, 0.34), material=M_PINE_D)

# back shelving
for k, sz in enumerate((1.05, 1.52)):
    add_box("BackShelf%d" % k, (3.10, 0.34, 0.04), (0.0, 0.52, sz), material=M_PINE)
for px in (-1.50, 0.0, 1.50):
    add_box("ShelfUpright", (0.05, 0.34, 1.55), (px, 0.52, 0.78), material=M_PINE_D)


# ------------------------------------------------------------------ crate builder
def make_crate(name, loc, rot=(0, 0, 0), w=0.60, d=0.42, h=0.26, slats=3):
    parts = []
    t = 0.016
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(add_box("post", (0.035, 0.035, h),
                                 (sx * (w / 2 - 0.02), sy * (d / 2 - 0.02), h / 2)))
    for k in range(slats):
        z = 0.035 + k * (h - 0.08) / max(slats - 1, 1)
        parts.append(add_box("slatF", (w, t, 0.055), (0, -d / 2, z)))
        parts.append(add_box("slatB", (w, t, 0.055), (0, d / 2, z)))
        parts.append(add_box("slatL", (t, d, 0.055), (-w / 2, 0, z)))
        parts.append(add_box("slatR", (t, d, 0.055), (w / 2, 0, z)))
    for k in range(4):
        y = -d / 2 + (k + 0.5) * d / 4
        parts.append(add_box("floor", (w, d / 5.5, t), (0, y, t / 2)))
    ob = join(parts, name)
    ob.data.materials.clear()
    ob.data.materials.append(M_PINE)
    ob.location = loc
    ob.rotation_euler = rot
    b = ob.modifiers.new("Bevel", 'BEVEL')
    b.width, b.segments = 0.004, 1
    return ob


def fill_crate(name, kind, origin, rot_z=0.0, w=0.54, d=0.36, base_z=0.05, layers=2):
    material, r, squash = PRODUCE[kind]
    parts = []
    nx = max(int(w / (2.05 * r)), 1)
    ny = max(int(d / (2.05 * r)), 1)
    for lay in range(layers):
        for ix in range(nx):
            for iy in range(ny):
                if lay == layers - 1 and random.random() < 0.28:
                    continue
                x = -w / 2 + (ix + 0.5) * w / nx + random.uniform(-0.008, 0.008)
                y = -d / 2 + (iy + 0.5) * d / ny + random.uniform(-0.008, 0.008)
                z = base_z + r * squash + lay * 1.7 * r * squash
                if lay % 2:
                    x += r * 0.5
                cs, sn = math.cos(rot_z), math.sin(rot_z)
                p = (origin[0] + x * cs - y * sn, origin[1] + x * sn + y * cs,
                     origin[2] + z)
                s = add_ico("fruit", r * random.uniform(0.9, 1.1), p, subd=2)
                s.scale = (1.0, 1.0, squash)
                s.rotation_euler = (random.uniform(0, 3), random.uniform(0, 3),
                                    random.uniform(0, 3))
                parts.append(s)
    ob = join(parts, name)
    ob.data.materials.clear()
    ob.data.materials.append(material)
    return ob


# crates on the counter, tipped forward for display
COUNTER_CRATES = [(-1.05, "apple"), (-0.35, "orange"), (0.35, "tomato"),
                  (1.05, "lemon")]
for cx, kind in COUNTER_CRATES:
    tilt = math.radians(-11)
    make_crate("Crate_%s" % kind, (cx, -0.42, COUNTER_Z + 0.045), rot=(tilt, 0, 0))
    fill_crate("Produce_%s" % kind, kind, (cx, -0.42, COUNTER_Z + 0.045),
               base_z=0.05, layers=2)
    # tip the produce with the crate
    ob = bpy.data.objects["Produce_%s" % kind]
    piv = Vector((cx, -0.42, COUNTER_Z + 0.045))
    ob.data.transform(Matrix.Translation(-piv))
    ob.data.transform(Matrix.Rotation(tilt, 4, 'X'))
    ob.data.transform(Matrix.Translation(piv))

# stacked crates on the ground, left side
GROUND_STACK = [((-1.85, -0.55, 0.0), "cabbage"),
                ((-1.85, -0.55, 0.27), "potato"),
                ((-1.30, -1.05, 0.0), "aubergine")]
for (gx, gy, gz), kind in GROUND_STACK:
    make_crate("GCrate_%s" % kind, (gx, gy, gz), rot=(0, 0, math.radians(6)))
    fill_crate("GProduce_%s" % kind, kind, (gx, gy, gz), rot_z=math.radians(6),
               base_z=0.05, layers=2)

# empty crates stacked at the right
for k in range(3):
    make_crate("EmptyCrate%d" % k, (1.95, -0.30 - 0.02 * k, k * 0.265),
               rot=(0, 0, math.radians(-8 + 5 * k)))

# a sack of onions leaning on the counter leg
for k in range(2):
    sack = add_ico("Sack%d" % k, 0.20, (0.55 + k * 0.42, -1.12, 0.19),
                   material=mat("Burlap%d" % k, (0.55, 0.46, 0.30), 0.9), subd=3)
    sack.scale = (1.0, 0.85, 0.95)

# ------------------------------------------------------------------ dressing
# chalkboard price sign hung from the front rail
board = add_box("PriceBoard", (0.62, 0.03, 0.44), (-1.05, -1.34, 1.72),
                rot=(math.radians(6), 0, 0), material=M_BOARD, bevel=0.008)
add_box("BoardFrame", (0.68, 0.02, 0.50), (-1.05, -1.36, 1.72),
        rot=(math.radians(6), 0, 0), material=M_PINE_D)
for k in range(4):
    add_box("ChalkLine%d" % k, (0.40 - 0.05 * k, 0.004, 0.022),
            (-1.10, -1.36, 1.86 - k * 0.09), rot=(math.radians(6), 0, 0),
            material=M_CHALK)
add_rod = None  # not needed further

# hanging scale
add_cyl("ScaleDial", 0.13, 0.06, (1.20, -1.28, 1.78), (math.pi / 2, 0, 0), verts=24,
        material=M_METAL)
add_cyl("ScalePan", 0.16, 0.05, (1.20, -1.28, 1.48), verts=24, material=M_METAL,
        r2=0.20)
add_box("ScaleHang", (0.02, 0.02, 0.30), (1.20, -1.28, 2.05), material=M_METAL)

# festoon bulbs under the front rail
for k in range(9):
    u = (k + 0.5) / 9.0
    x = -1.55 + 3.10 * u
    z = 2.14 - 0.10 * math.sin(math.pi * u)
    add_ico("Bulb%d" % k, 0.035, (x, -1.30, z), material=M_BULB, subd=2)

# small paper bags and jars on the back shelf
for k in range(6):
    add_box("Bag%d" % k, (0.16, 0.12, 0.20), (-1.30 + k * 0.52, 0.52, 1.15),
            rot=(0, 0, random.uniform(-0.3, 0.3)), material=M_PAPER, bevel=0.01)
for k in range(5):
    add_cyl("Jar%d" % k, 0.055, 0.20, (-1.10 + k * 0.55, 0.52, 1.64), verts=18,
            material=mat("Jar%d" % k,
                         (random.uniform(0.4, 0.8), random.uniform(0.3, 0.6), 0.18),
                         0.25))

# ------------------------------------------------------------------ world/lights
world = bpy.data.worlds.new("MarketWorld")
bpy.context.scene.world = world
world.use_nodes = True
nt = world.node_tree
bg = nt.nodes["Background"]
bg.inputs["Strength"].default_value = 0.9
sky = nt.nodes.new("ShaderNodeTexSky")
sky.sun_elevation = math.radians(35)
sky.sun_rotation = math.radians(120)
nt.links.new(sky.outputs[0], bg.inputs["Color"])

sd = bpy.data.lights.new("Sun", 'SUN')
sd.energy, sd.angle = 3.2, math.radians(3)
sd.color = (1.0, 0.94, 0.84)
sun = bpy.data.objects.new("Sun", sd)
bpy.context.collection.objects.link(sun)
sun.location = (-5, 6, 8)
look_at(sun, (0, -0.4, 1.0))

kd = bpy.data.lights.new("CanopyFill", 'AREA')
kd.energy, kd.size = 260.0, 3.0
kd.color = (1.0, 0.86, 0.68)
key = bpy.data.objects.new("CanopyFill", kd)
bpy.context.collection.objects.link(key)
key.location = (0.0, -1.6, 2.0)
look_at(key, (0.0, -0.4, 1.0))

rd = bpy.data.lights.new("Rim", 'AREA')
rd.energy, rd.size = 180.0, 4.0
rim = bpy.data.objects.new("Rim", rd)
bpy.context.collection.objects.link(rim)
rim.location = (3.5, 2.5, 2.6)
look_at(rim, (0.0, 0.0, 1.2))

# ------------------------------------------------------------------ camera
cd = bpy.data.cameras.new("Camera")
cd.lens = 40
cam = bpy.data.objects.new("Camera", cd)
bpy.context.collection.objects.link(cam)
cam.location = (3.30, -4.30, 2.05)
look_at(cam, (-0.10, -0.35, 1.15))
bpy.context.scene.camera = cam

print("claude-057 market stall built: %d objects" % len(bpy.data.objects))
