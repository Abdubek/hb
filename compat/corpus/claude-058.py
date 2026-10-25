"""claude-058 : A compact espresso cart on four wheels."""
import bpy, bmesh, math, random
from mathutils import Vector, Matrix

random.seed(58)


# ------------------------------------------------------------------ helpers
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scn = bpy.context.scene
    try:
        scn.render.engine = 'BLENDER_EEVEE_NEXT'
    except Exception:
        pass
    scn.render.resolution_x, scn.render.resolution_y = 1600, 1000


def mat(name, color, rough=0.5, metal=0.0, emis=None, estr=0.0, alpha=1.0):
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
    if alpha < 1.0:
        i["Alpha"].default_value = alpha
        try:
            m.blend_method = 'BLEND'
        except Exception:
            pass
        if hasattr(m, "surface_render_method"):
            m.surface_render_method = 'BLENDED'
    return m


def shade_smooth(ob):
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    try:
        bpy.ops.object.shade_auto_smooth(angle=math.radians(35))
    except Exception:
        bpy.ops.object.shade_smooth()


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


def add_box(name, size, loc=(0, 0, 0), rot=(0, 0, 0), material=None, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    ob = bpy.context.object
    ob.name = name
    ob.data.transform(Matrix.Diagonal(Vector((size[0], size[1], size[2], 1.0))))
    ob.location, ob.rotation_euler = loc, rot
    return finish(ob, material, bevel)


def add_cyl(name, r, d, loc=(0, 0, 0), rot=(0, 0, 0), verts=24, material=None,
            r2=None):
    if r2 is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=d)
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r, radius2=r2, depth=d)
    ob = bpy.context.object
    ob.name = name
    ob.location, ob.rotation_euler = loc, rot
    return finish(ob, material, smooth=True)


def add_torus(name, R, r, loc, rot=(0, 0, 0), material=None, mseg=32, nseg=12):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r,
                                     major_segments=mseg, minor_segments=nseg,
                                     location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    return finish(ob, material, smooth=True)


def add_rod(name, p0, p1, r, material=None, verts=12):
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    ob = add_cyl(name, r, max(d.length, 1e-5), tuple((p0 + p1) * 0.5), verts=verts,
                 material=material)
    ob.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    return ob


def look_at(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


# ------------------------------------------------------------------ materials
reset_scene()

M_FLOOR = mat("Floor", (0.24, 0.23, 0.22), 0.55)
M_BODY = mat("CartBody", (0.05, 0.30, 0.27), 0.35)
M_TRIM = mat("BrassTrim", (0.78, 0.60, 0.28), 0.28, 1.0)
M_TOP = mat("WalnutTop", (0.30, 0.17, 0.09), 0.32)
M_STEEL = mat("Steel", (0.72, 0.73, 0.75), 0.22, 1.0)
M_CHROME = mat("Chrome", (0.86, 0.87, 0.89), 0.06, 1.0)
M_BLACK = mat("MattBlack", (0.045, 0.045, 0.05), 0.45)
M_RUBBER = mat("Rubber", (0.05, 0.05, 0.055), 0.85)
M_WHITE = mat("Porcelain", (0.93, 0.93, 0.91), 0.20)
M_BOARD = mat("Chalkboard", (0.07, 0.08, 0.08), 0.8)
M_CHALK = mat("Chalk", (0.90, 0.90, 0.86), 0.9)
M_BEAN = mat("Beans", (0.19, 0.10, 0.05), 0.42)
M_GLASS = mat("Glass", (0.85, 0.90, 0.92), 0.05, 0.0, alpha=0.25)
M_LAMP = mat("Lamp", (1.0, 0.86, 0.62), 0.3, emis=(1.0, 0.84, 0.58), estr=14.0)
M_MILK = mat("Milk", (0.95, 0.94, 0.90), 0.3)

# ------------------------------------------------------------------ floor
bpy.ops.mesh.primitive_plane_add(size=30.0)
bpy.context.object.name = "Floor"
finish(bpy.context.object, M_FLOOR)

# ------------------------------------------------------------------ cart body
CW, CD = 1.30, 0.66            # cart width (x) and depth (y)
AXLE_Z = 0.235                 # rear wheel centre height
BODY_Z0, BODY_Z1 = 0.34, 0.94  # cabinet bottom / top
BODY_H = BODY_Z1 - BODY_Z0
BODY_C = (BODY_Z0 + BODY_Z1) * 0.5

add_box("Cabinet", (CW, CD, BODY_H), (0, 0, BODY_C), material=M_BODY, bevel=0.018)
add_box("CounterTop", (CW + 0.10, CD + 0.09, 0.05), (0, 0, BODY_Z1 + 0.025),
        material=M_TOP, bevel=0.012)
add_box("TopEdge", (CW + 0.11, CD + 0.10, 0.012), (0, 0, BODY_Z1 + 0.055),
        material=M_TRIM)
add_box("Plinth", (CW - 0.06, CD - 0.04, 0.06), (0, 0, BODY_Z0 - 0.02),
        material=M_BLACK, bevel=0.01)

# front panel detail: recessed panels with brass beading
for k, px in enumerate((-0.33, 0.33)):
    add_box("PanelRecess%d" % k, (0.52, 0.02, 0.40), (px, -CD / 2 - 0.005, BODY_C),
            material=M_BLACK)
    add_box("PanelBead%d" % k, (0.56, 0.012, 0.44), (px, -CD / 2 - 0.012, BODY_C),
            material=M_TRIM)
# rear service doors with handles
for k, px in enumerate((-0.32, 0.32)):
    add_box("Door%d" % k, (0.60, 0.02, 0.50), (px, CD / 2 + 0.008, BODY_C),
            material=M_BODY, bevel=0.008)
    add_cyl("Handle%d" % k, 0.014, 0.13, (px + (0.24 if k == 0 else -0.24),
                                          CD / 2 + 0.035, BODY_C),
            rot=(0, 0, 0), verts=12, material=M_TRIM)
# frame chassis under the body
for sy in (-1, 1):
    add_box("Rail", (CW + 0.06, 0.05, 0.05), (0, sy * (CD / 2 - 0.06), BODY_Z0 - 0.04),
            material=M_BLACK)

# ------------------------------------------------------------------ wheels
def spoked_wheel(name, loc, R=0.235, tire=0.045, spokes=10, hub_r=0.05):
    add_torus(name + "_Tire", R - tire, tire, loc, rot=(0, math.pi / 2, 0),
              material=M_RUBBER, mseg=40, nseg=14)
    add_cyl(name + "_Rim", R - tire - 0.005, 0.030, loc, (0, math.pi / 2, 0),
            verts=36, material=M_STEEL)
    add_cyl(name + "_Hub", hub_r, 0.075, loc, (0, math.pi / 2, 0), verts=20,
            material=M_CHROME)
    for s in range(spokes):
        a = 2 * math.pi * s / spokes
        p0 = Vector(loc) + Vector((0, math.cos(a), math.sin(a))) * hub_r
        p1 = Vector(loc) + Vector((0, math.cos(a), math.sin(a))) * (R - tire - 0.01)
        add_rod(name + "_Spoke%d" % s, p0, p1, 0.006, M_CHROME, verts=6)


def caster(name, x, y, R=0.075):
    z = R
    add_box(name + "_Fork", (0.05, 0.09, 0.10), (x, y, z + 0.09), material=M_STEEL,
            bevel=0.008)
    add_cyl(name + "_Swivel", 0.028, 0.12, (x, y + 0.02, z + 0.19), verts=14,
            material=M_STEEL)
    add_cyl(name + "_Plate", 0.055, 0.02, (x, y + 0.02, z + 0.25), verts=16,
            material=M_STEEL)
    add_torus(name + "_Tire", R - 0.022, 0.022, (x, y, z), rot=(0, math.pi / 2, 0),
              material=M_RUBBER, mseg=28, nseg=10)
    add_cyl(name + "_Rim", R - 0.024, 0.032, (x, y, z), (0, math.pi / 2, 0), verts=24,
            material=M_CHROME)


spoked_wheel("WheelR_L", (-CW / 2 - 0.055, 0.20, AXLE_Z))
spoked_wheel("WheelR_R", (CW / 2 + 0.055, 0.20, AXLE_Z))
add_cyl("Axle", 0.020, CW + 0.14, (0, 0.20, AXLE_Z), (0, math.pi / 2, 0), verts=14,
        material=M_STEEL)
caster("CasterL", -CW / 2 + 0.14, -0.22)
caster("CasterR", CW / 2 - 0.14, -0.22)

# push handle over the rear wheels
for sx in (-1, 1):
    add_rod("HandleStay%d" % (sx > 0), (sx * (CW / 2 + 0.02), 0.30, BODY_Z0),
            (sx * (CW / 2 + 0.02), 0.46, 1.02), 0.018, M_STEEL, verts=12)
add_cyl("HandleBar", 0.020, CW + 0.04, (0, 0.46, 1.02), (0, math.pi / 2, 0),
        verts=16, material=M_STEEL)
for sx in (-1, 1):
    add_cyl("Grip%d" % (sx > 0), 0.026, 0.13,
            (sx * (CW / 2 - 0.05), 0.46, 1.02), (0, math.pi / 2, 0), verts=16,
            material=M_BLACK)

# ------------------------------------------------------------------ espresso machine
TOP = BODY_Z1 + 0.05
MX = -0.28
add_box("MachineBody", (0.62, 0.44, 0.36), (MX, 0.03, TOP + 0.18), material=M_CHROME,
        bevel=0.022)
add_box("MachineFascia", (0.60, 0.02, 0.20), (MX, -0.19, TOP + 0.24),
        material=M_BLACK, bevel=0.008)
add_box("CupWarmer", (0.58, 0.40, 0.02), (MX, 0.03, TOP + 0.37), material=M_STEEL)
add_cyl("BoilerCap", 0.05, 0.05, (MX + 0.20, 0.03, TOP + 0.40), verts=18,
        material=M_TRIM)
add_cyl("Manometer", 0.045, 0.02, (MX - 0.20, -0.20, TOP + 0.30),
        (math.pi / 2, 0, 0), verts=20, material=M_WHITE)
add_torus("ManoRing", 0.048, 0.008, (MX - 0.20, -0.205, TOP + 0.30),
          rot=(math.pi / 2, 0, 0), material=M_TRIM, mseg=24, nseg=8)

# drip tray and grates
add_box("DripTray", (0.60, 0.24, 0.035), (MX, -0.10, TOP + 0.018), material=M_STEEL,
        bevel=0.005)
for k in range(11):
    add_box("Grate%d" % k, (0.012, 0.20, 0.006),
            (MX - 0.26 + k * 0.052, -0.10, TOP + 0.038), material=M_BLACK)

# two group heads with portafilters
for k, gx in enumerate((MX - 0.16, MX + 0.16)):
    add_cyl("Group%d" % k, 0.045, 0.10, (gx, -0.16, TOP + 0.14), verts=20,
            material=M_CHROME)
    add_cyl("GroupFlange%d" % k, 0.058, 0.022, (gx, -0.16, TOP + 0.095), verts=20,
            material=M_CHROME)
    add_cyl("Basket%d" % k, 0.052, 0.045, (gx, -0.16, TOP + 0.068), verts=20,
            material=M_STEEL)
    add_rod("PfHandle%d" % k, (gx, -0.20, TOP + 0.068), (gx, -0.34, TOP + 0.052),
            0.013, M_BLACK, verts=10)
    add_cyl("PfTip%d" % k, 0.017, 0.03, (gx, -0.35, TOP + 0.051),
            (math.pi / 2, 0, 0), verts=12, material=M_TRIM)
    add_box("Lever%d" % k, (0.055, 0.02, 0.012), (gx, -0.205, TOP + 0.235),
            material=M_BLACK, bevel=0.004)

# steam wand and hot water tap
add_rod("WandJoint", (MX + 0.30, -0.14, TOP + 0.20), (MX + 0.33, -0.20, TOP + 0.14),
        0.012, M_CHROME, verts=10)
add_rod("SteamWand", (MX + 0.33, -0.20, TOP + 0.14), (MX + 0.35, -0.24, TOP + 0.035),
        0.009, M_CHROME, verts=10)
add_cyl("SteamKnob", 0.028, 0.03, (MX + 0.30, -0.14, TOP + 0.235), verts=16,
        material=M_BLACK)
add_rod("WaterTap", (MX - 0.30, -0.14, TOP + 0.20), (MX - 0.30, -0.20, TOP + 0.09),
        0.008, M_CHROME, verts=10)

# cups warming on top
for k in range(6):
    cx = MX - 0.22 + (k % 3) * 0.20
    cy = -0.05 + (k // 3) * 0.16
    add_cyl("WarmCup%d" % k, 0.032, 0.055, (cx, cy, TOP + 0.405), verts=18,
            material=M_WHITE, r2=0.026)
    add_cyl("WarmSaucer%d" % k, 0.052, 0.008, (cx, cy, TOP + 0.382), verts=20,
            material=M_WHITE)

# ------------------------------------------------------------------ grinder + service
GX = 0.34
add_box("GrinderBase", (0.17, 0.20, 0.30), (GX, 0.10, TOP + 0.15), material=M_BLACK,
        bevel=0.014)
add_cyl("GrinderThroat", 0.06, 0.06, (GX, 0.10, TOP + 0.32), verts=20,
        material=M_STEEL)
hopper = add_cyl("Hopper", 0.055, 0.20, (GX, 0.10, TOP + 0.45), verts=24,
                 material=M_GLASS, r2=0.095)
beans = add_cyl("BeansFill", 0.05, 0.12, (GX, 0.10, TOP + 0.41), verts=20,
                material=M_BEAN, r2=0.078)
add_cyl("HopperLid", 0.098, 0.014, (GX, 0.10, TOP + 0.556), verts=24,
        material=M_BLACK)
add_box("GrinderChute", (0.07, 0.07, 0.09), (GX, -0.02, TOP + 0.11),
        material=M_STEEL, bevel=0.008)
add_cyl("Tamper", 0.028, 0.05, (GX + 0.16, -0.16, TOP + 0.025), verts=18,
        material=M_STEEL)
add_cyl("TamperHandle", 0.022, 0.06, (GX + 0.16, -0.16, TOP + 0.078), verts=18,
        material=M_TOP, r2=0.030)

# milk jug, sugar jar, cup stack on the right of the counter
jug = add_cyl("MilkJug", 0.052, 0.13, (GX + 0.24, 0.14, TOP + 0.065), verts=24,
              material=M_STEEL, r2=0.060)
add_torus("JugHandle", 0.035, 0.006, (GX + 0.30, 0.14, TOP + 0.075),
          rot=(math.pi / 2, 0, math.pi / 2), material=M_STEEL, mseg=20, nseg=8)
add_cyl("SugarJar", 0.045, 0.11, (GX + 0.10, 0.28, TOP + 0.055), verts=22,
        material=M_GLASS)
add_cyl("SugarLid", 0.047, 0.02, (GX + 0.10, 0.28, TOP + 0.12), verts=22,
        material=M_TRIM)
for k in range(5):
    add_cyl("StackCup%d" % k, 0.034, 0.09, (GX + 0.32, -0.16, TOP + 0.05 + k * 0.028),
            verts=18, material=M_WHITE, r2=0.028)

# ------------------------------------------------------------------ signage + awning
add_box("SignBoard", (0.86, 0.035, 0.30), (0.0, -CD / 2 - 0.04, 0.70),
        rot=(math.radians(4), 0, 0), material=M_BOARD, bevel=0.008)
add_box("SignFrame", (0.92, 0.02, 0.36), (0.0, -CD / 2 - 0.055, 0.70),
        rot=(math.radians(4), 0, 0), material=M_TRIM)
for k in range(3):
    add_box("SignText%d" % k, (0.52 - 0.12 * k, 0.005, 0.028),
            (0.0, -CD / 2 - 0.058, 0.79 - k * 0.075), rot=(math.radians(4), 0, 0),
            material=M_CHALK)

# folding awning over the serving side
AW_Y0, AW_Y1 = 0.10, -0.70
AW_Z0, AW_Z1 = 1.92, 1.72
bm = bmesh.new()
cols = []
NU, NV = 24, 8
for j in range(NU + 1):
    u = j / NU
    col = []
    for i in range(NV + 1):
        v = i / NV
        x = -0.80 + 1.60 * u
        y = AW_Y0 + (AW_Y1 - AW_Y0) * v
        z = AW_Z0 + (AW_Z1 - AW_Z0) * v - 0.05 * math.sin(math.pi * u) * math.sin(math.pi * v)
        col.append(bm.verts.new((x, y, z)))
    cols.append(col)
for j in range(NU):
    for i in range(NV):
        f = bm.faces.new((cols[j][i], cols[j + 1][i], cols[j + 1][i + 1], cols[j][i + 1]))
        f.material_index = (j // 3) % 2
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
me = bpy.data.meshes.new("Awning")
bm.to_mesh(me)
bm.free()
awn = bpy.data.objects.new("Awning", me)
bpy.context.collection.objects.link(awn)
awn.data.materials.append(mat("AwnCream", (0.90, 0.87, 0.78), 0.8))
awn.data.materials.append(mat("AwnGreen", (0.06, 0.32, 0.28), 0.8))
awn.modifiers.new("Solidify", 'SOLIDIFY').thickness = 0.01
shade_smooth(awn)

for sx in (-1, 1):
    add_rod("AwnPost%d" % (sx > 0), (sx * 0.72, 0.16, TOP + 0.05),
            (sx * 0.72, 0.12, AW_Z0), 0.016, M_STEEL, verts=12)
    add_rod("AwnArm%d" % (sx > 0), (sx * 0.72, 0.10, AW_Z0),
            (sx * 0.72, -0.70, AW_Z1), 0.013, M_STEEL, verts=10)

# hanging bulb under the awning
add_rod("LampCord", (0.0, -0.28, 1.80), (0.0, -0.28, 1.62), 0.004, M_BLACK, verts=6)
add_cyl("LampShade", 0.085, 0.09, (0.0, -0.28, 1.57), verts=24, material=M_TRIM,
        r2=0.03)
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=0.035,
                                      location=(0.0, -0.28, 1.51))
bpy.context.object.name = "LampBulb"
finish(bpy.context.object, M_LAMP, smooth=True)

# ------------------------------------------------------------------ lighting
world = bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
wbg = world.node_tree.nodes["Background"]
wbg.inputs["Color"].default_value = (0.055, 0.065, 0.085, 1.0)
wbg.inputs["Strength"].default_value = 1.0

kd = bpy.data.lights.new("Key", 'AREA')
kd.energy, kd.size = 320.0, 2.0
kd.color = (1.0, 0.93, 0.84)
key = bpy.data.objects.new("Key", kd)
bpy.context.collection.objects.link(key)
key.location = (-1.6, -2.2, 2.6)
look_at(key, (0, -0.1, 1.0))

fd = bpy.data.lights.new("Fill", 'AREA')
fd.energy, fd.size = 120.0, 3.0
fd.color = (0.72, 0.80, 1.0)
fil = bpy.data.objects.new("Fill", fd)
bpy.context.collection.objects.link(fil)
fil.location = (2.4, -1.8, 1.8)
look_at(fil, (0, 0, 0.9))

rd = bpy.data.lights.new("Rim", 'AREA')
rd.energy, rd.size = 200.0, 2.0
rim = bpy.data.objects.new("Rim", rd)
bpy.context.collection.objects.link(rim)
rim.location = (1.2, 2.6, 2.2)
look_at(rim, (0, 0, 1.0))

pd = bpy.data.lights.new("BulbPoint", 'POINT')
pd.energy, pd.shadow_soft_size = 22.0, 0.05
pd.color = (1.0, 0.82, 0.58)
pt = bpy.data.objects.new("BulbPoint", pd)
bpy.context.collection.objects.link(pt)
pt.location = (0.0, -0.28, 1.50)

# ------------------------------------------------------------------ camera
cd = bpy.data.cameras.new("Camera")
cd.lens = 50
cam = bpy.data.objects.new("Camera", cd)
bpy.context.collection.objects.link(cam)
cam.location = (2.05, -2.55, 1.72)
look_at(cam, (-0.05, -0.05, 1.02))
bpy.context.scene.camera = cam

print("claude-058 espresso cart built: %d objects" % len(bpy.data.objects))
