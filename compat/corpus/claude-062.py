import bpy, bmesh, math, random
from mathutils import Vector, Matrix, Euler

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    try: sc.render.engine = 'BLENDER_EEVEE_NEXT'
    except TypeError: pass
    sc.unit_settings.system = 'METRIC'

def new_mat(name, color, rough=0.5, metal=0.0, emission=None, strength=1.0, transmission=0.0, ior=1.45, alpha=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    b.inputs["IOR"].default_value = ior
    b.inputs["Alpha"].default_value = alpha
    if "Transmission Weight" in b.inputs:
        b.inputs["Transmission Weight"].default_value = transmission
    if emission is not None:
        b.inputs["Emission Color"].default_value = (emission[0], emission[1], emission[2], 1.0)
        b.inputs["Emission Strength"].default_value = strength
    if transmission > 0.0 or alpha < 1.0:
        try: m.surface_render_method = 'BLENDED'
        except AttributeError: pass
    return m

def obj_from_bm(name, bm, mats=None, loc=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc; ob.rotation_euler = rot
    bpy.context.collection.objects.link(ob)
    if mats:
        for m in (mats if isinstance(mats, (list, tuple)) else [mats]):
            ob.data.materials.append(m)
    return ob

def box(name, size, center=(0, 0, 0), mat=None, bevel=0.0, seg=2, rot=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    if bevel > 0.0:
        bmesh.ops.bevel(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], offset=bevel,
                        segments=seg, profile=0.5, affect='EDGES', clamp_overlap=True)
    return obj_from_bm(name, bm, mat, center, rot)

def cyl(name, radius, depth, center=(0, 0, 0), rot=(0, 0, 0), mat=None, seg=24, r2=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                          radius1=radius, radius2=(radius if r2 is None else r2), depth=depth)
    for f in bm.faces:
        if abs(f.normal.z) < 0.7: f.smooth = True
    return obj_from_bm(name, bm, mat, center, rot)

def add_camera(loc, target, lens=50.0, name="Camera"):
    cd = bpy.data.cameras.new(name); cd.lens = lens
    ob = bpy.data.objects.new(name, cd); ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(ob)
    bpy.context.scene.camera = ob
    return ob

def add_area(name, loc, target, energy, size=2.0, color=(1, 1, 1)):
    ld = bpy.data.lights.new(name, 'AREA'); ld.energy = energy; ld.size = size; ld.color = color
    ob = bpy.data.objects.new(name, ld); ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(ob)
    return ob

def set_world(color=(0.05, 0.05, 0.06), strength=1.0):
    w = bpy.context.scene.world
    if w is None:
        w = bpy.data.worlds.new("World"); bpy.context.scene.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (color[0], color[1], color[2], 1.0)
    bg.inputs[1].default_value = strength

# ---------------------------------------------------------------- scene ----
reset_scene()
set_world((0.09, 0.10, 0.12), 0.7)
rnd = random.Random(62)

M_WALNUT = new_mat("Walnut", (0.135, 0.072, 0.040), rough=0.42)
M_WALNUT_D = new_mat("WalnutDark", (0.095, 0.050, 0.028), rough=0.45)
M_OAK = new_mat("OakTop", (0.34, 0.22, 0.13), rough=0.38)
M_BRASS = new_mat("Brass", (0.72, 0.55, 0.24), rough=0.28, metal=1.0)
M_STEEL = new_mat("Steel", (0.62, 0.63, 0.65), rough=0.30, metal=1.0)
M_BLACK = new_mat("TVShell", (0.030, 0.031, 0.034), rough=0.38)
M_BEZEL = new_mat("Bezel", (0.055, 0.056, 0.060), rough=0.28)
M_SCREEN = new_mat("Screen", (0.02, 0.03, 0.05), rough=0.12, emission=(0.16, 0.30, 0.52), strength=4.0)
M_FELT = new_mat("SpeakerFelt", (0.10, 0.10, 0.11), rough=0.95)
M_WALL = new_mat("Wall", (0.72, 0.71, 0.68), rough=0.9)
M_FLOOR = new_mat("Floor", (0.30, 0.21, 0.14), rough=0.45)
M_RUG = new_mat("Rug", (0.24, 0.26, 0.29), rough=0.95)
M_PLANT = new_mat("Leaf", (0.10, 0.30, 0.12), rough=0.6)
M_POT = new_mat("Pot", (0.70, 0.66, 0.60), rough=0.6)

# room
box("Floor", (10.0, 10.0, 0.06), (0.0, 0.0, -0.03), M_FLOOR)
box("BackWall", (8.0, 0.12, 3.0), (0.0, 0.46, 1.50), M_WALL)
box("Baseboard", (8.0, 0.03, 0.10), (0.0, 0.385, 0.05), M_WALL)
box("Rug", (4.0, 2.8, 0.012), (0.0, -1.5, 0.006), M_RUG)

# console carcass
CX, CY = 1.90, 0.44
FRONT = -CY * 0.5
Z0, Z1 = 0.17, 0.62
box("CarcassBack", (CX, 0.02, Z1 - Z0), (0.0, CY * 0.5 - 0.01, (Z0 + Z1) * 0.5), M_WALNUT_D)
box("CarcassBottom", (CX, CY, 0.022), (0.0, 0.0, Z0 + 0.011), M_WALNUT)
box("CarcassTopDeck", (CX, CY, 0.022), (0.0, 0.0, Z1 - 0.011), M_WALNUT)
for sx in (-1.0, 1.0):
    box("CarcassSide_%d" % (sx > 0), (0.022, CY, Z1 - Z0),
        (sx * (CX * 0.5 - 0.011), 0.0, (Z0 + Z1) * 0.5), M_WALNUT)
box("MidRail", (CX - 0.05, CY - 0.05, 0.018), (0.0, 0.0, 0.398), M_WALNUT_D)
for sx in (-1.0, 1.0):
    box("Divider_%d" % (sx > 0), (0.018, CY - 0.06, Z1 - Z0 - 0.05),
        (sx * 0.305, 0.01, (Z0 + Z1) * 0.5), M_WALNUT_D)
box("Top", (CX + 0.10, CY + 0.06, 0.036), (0.0, 0.0, Z1 + 0.018), M_OAK, bevel=0.006, seg=3)

# splayed tapered legs
for sx in (-1.0, 1.0):
    for sy in (-1.0, 1.0):
        cyl("Leg_%d%d" % (sx > 0, sy > 0), 0.028, 0.20,
            (sx * (CX * 0.5 - 0.13), sy * (CY * 0.5 - 0.10), 0.085),
            rot=(sy * math.radians(6), -sx * math.radians(6), 0.0),
            mat=M_WALNUT_D, seg=16, r2=0.016)

# drawers: two rows of three, with bar pulls
DW, DH, DT = 0.605, 0.205, 0.020
for ri, rz in enumerate((0.505, 0.285)):
    for ci, cx in enumerate((-0.615, 0.0, 0.615)):
        box("DrawerFront_%d_%d" % (ri, ci), (DW - 0.012, DT, DH - 0.012),
            (cx, FRONT - DT * 0.5 - 0.002, rz), M_WALNUT, bevel=0.006, seg=3)
        box("DrawerInset_%d_%d" % (ri, ci), (DW - 0.10, 0.006, DH - 0.08),
            (cx, FRONT - DT - 0.004, rz), M_WALNUT_D)
        hy = FRONT - DT - 0.030
        cyl("Handle_%d_%d" % (ri, ci), 0.0085, 0.30, (cx, hy, rz),
            rot=(0.0, math.radians(90), 0.0), mat=M_BRASS, seg=16)
        for hx in (-0.135, 0.135):
            cyl("HandlePost_%d_%d_%d" % (ri, ci, hx > 0), 0.006, 0.026,
                (cx + hx, FRONT - DT - 0.014, rz), rot=(math.radians(90), 0.0, 0.0),
                mat=M_BRASS, seg=10)

# television
TVZ = Z1 + 0.036
box("TVBase", (0.46, 0.26, 0.018), (0.0, 0.02, TVZ + 0.009), M_BLACK, bevel=0.005)
box("TVNeck", (0.10, 0.055, 0.24), (0.0, 0.02, TVZ + 0.13), M_BLACK, bevel=0.006)
box("TVNeckPlate", (0.16, 0.07, 0.06), (0.0, 0.02, TVZ + 0.245), M_BLACK, bevel=0.008)
TILT = math.radians(-3.0)
PANEL_Z = TVZ + 0.24 + 0.345
PANEL_Y = 0.045
box("TVPanel", (1.28, 0.032, 0.745), (0.0, PANEL_Y, PANEL_Z), M_BLACK, bevel=0.004, seg=2, rot=(TILT, 0, 0))
box("TVBackBoss", (0.70, 0.030, 0.40), (0.0, PANEL_Y + 0.030, PANEL_Z - 0.06), M_BLACK, bevel=0.006, rot=(TILT, 0, 0))
box("TVBezel", (1.29, 0.010, 0.755), (0.0, PANEL_Y - 0.020, PANEL_Z), M_BEZEL, bevel=0.003, rot=(TILT, 0, 0))
box("TVScreen", (1.245, 0.006, 0.710), (0.0, PANEL_Y - 0.027, PANEL_Z), M_SCREEN, rot=(TILT, 0, 0))
box("TVStrip", (1.10, 0.004, 0.045), (0.0, PANEL_Y - 0.033, PANEL_Z - 0.30),
    new_mat("ScreenUI", (0.05, 0.05, 0.06), 0.2, emission=(0.85, 0.90, 1.0), strength=6.0), rot=(TILT, 0, 0))
cyl("TVLed", 0.006, 0.006, (0.0, PANEL_Y - 0.034, PANEL_Z - 0.375), rot=(math.radians(90), 0, 0),
    mat=new_mat("Led", (0.05, 0.05, 0.05), 0.3, emission=(0.2, 1.0, 0.3), strength=8.0), seg=10)

# soundbar with perforated grille
box("Soundbar", (0.92, 0.085, 0.075), (0.0, -0.10, TVZ + 0.040), M_BLACK, bevel=0.012, seg=3)
bm_g = bmesh.new()
for i in range(46):
    tmp = bmesh.new()
    bmesh.ops.create_cone(tmp, cap_ends=True, cap_tris=False, segments=8,
                          radius1=0.0055, radius2=0.0055, depth=0.006)
    bmesh.ops.rotate(tmp, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, 'X'), verts=tmp.verts)
    bmesh.ops.translate(tmp, vec=Vector((-0.42 + (i // 2) * 0.0365, -0.146,
                                         TVZ + 0.026 + (i % 2) * 0.028)), verts=tmp.verts)
    me = bpy.data.meshes.new("_g"); tmp.to_mesh(me); tmp.free()
    bm_g.from_mesh(me); bpy.data.meshes.remove(me)
obj_from_bm("SoundbarGrille", bm_g, M_FELT)

# props
for i, c in enumerate([(0.55, 0.14, 0.12), (0.12, 0.28, 0.42), (0.78, 0.68, 0.30)]):
    box("Book_%d" % i, (0.20, 0.15, 0.030 + i * 0.004), (-0.78, -0.06, TVZ + 0.018 + i * 0.036),
        new_mat("BookMat_%d" % i, c, 0.65), bevel=0.003, rot=(0, 0, math.radians(rnd.uniform(-6, 6))))
cyl("Vase", 0.055, 0.20, (0.76, 0.02, TVZ + 0.10), mat=M_POT, seg=24, r2=0.038)
for i in range(7):
    a = i * 0.9
    cyl("Stem_%d" % i, 0.004, 0.26,
        (0.76 + 0.05 * math.cos(a), 0.02 + 0.05 * math.sin(a), TVZ + 0.31),
        rot=(math.radians(12) * math.sin(a), math.radians(12) * math.cos(a), 0.0), mat=M_PLANT, seg=6)
    box("Leaf_%d" % i, (0.05, 0.012, 0.10),
        (0.76 + 0.10 * math.cos(a), 0.02 + 0.10 * math.sin(a), TVZ + 0.42), M_PLANT, bevel=0.006, rot=(0, 0, a))
box("Remote", (0.048, 0.17, 0.018), (0.30, -0.14, TVZ + 0.009), M_BLACK, bevel=0.006, rot=(0, 0, math.radians(-14)))
box("MediaBox", (0.34, 0.26, 0.055), (0.0, 0.02, Z0 + 0.05), M_STEEL, bevel=0.006)
box("MediaFace", (0.30, 0.006, 0.020), (0.0, -0.112, Z0 + 0.05),
    new_mat("MediaUI", (0.03, 0.03, 0.03), 0.3, emission=(0.3, 0.8, 1.0), strength=3.0))

# lighting and camera
add_area("Key", (-2.6, -3.0, 2.9), (-0.2, 0.0, 0.9), 420.0, size=2.6, color=(1.0, 0.96, 0.90))
add_area("Fill", (3.0, -2.4, 1.8), (0.3, 0.1, 0.8), 130.0, size=3.0, color=(0.80, 0.86, 1.0))
add_area("Rim", (0.0, 1.6, 2.4), (0.0, 0.0, 1.2), 90.0, size=2.0, color=(0.9, 0.92, 1.0))
add_area("ScreenGlow", (0.0, -0.9, PANEL_Z), (0.0, 0.2, PANEL_Z), 25.0, size=1.2, color=(0.55, 0.72, 1.0))
add_camera((2.55, -3.10, 1.55), (0.0, 0.0, 0.90), lens=48.0)
