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

def bm_cyl(bm, r, d, center, axis='Z', seg=12):
    tmp = bmesh.new()
    bmesh.ops.create_cone(tmp, cap_ends=True, cap_tris=False, segments=seg,
                          radius1=r, radius2=r, depth=d)
    if axis == 'Y':
        bmesh.ops.rotate(tmp, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, 'X'), verts=tmp.verts)
    elif axis == 'X':
        bmesh.ops.rotate(tmp, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, 'Y'), verts=tmp.verts)
    bmesh.ops.translate(tmp, vec=Vector(center), verts=tmp.verts)
    me = bpy.data.meshes.new("_tmp"); tmp.to_mesh(me); tmp.free()
    bm.from_mesh(me); bpy.data.meshes.remove(me)

def profile_solid(name, pts, x0, x1, mat, bevel=0.0):
    """Extrude a (y, z) polygon along X from x0 to x1."""
    bm = bmesh.new()
    verts = [bm.verts.new((x0, p[0], p[1])) for p in pts]
    face = bm.faces.new(verts)
    res = bmesh.ops.extrude_face_region(bm, geom=[face])
    ext = [e for e in res['geom'] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=ext, vec=(x1 - x0, 0.0, 0.0))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if bevel > 0.0:
        bmesh.ops.bevel(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], offset=bevel,
                        segments=1, profile=0.5, affect='EDGES', clamp_overlap=True)
    return obj_from_bm(name, bm, mat)

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

def add_point(name, loc, energy, color=(1, 1, 1), radius=0.1):
    ld = bpy.data.lights.new(name, 'POINT'); ld.energy = energy; ld.color = color
    ld.shadow_soft_size = radius
    ob = bpy.data.objects.new(name, ld); ob.location = loc
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
set_world((0.02, 0.022, 0.03), 0.6)
rnd = random.Random(64)

M_CAB = new_mat("CabBlack", (0.035, 0.036, 0.042), rough=0.45)
M_CAB_SIDE = new_mat("CabSide", (0.055, 0.058, 0.070), rough=0.42)
M_ART = new_mat("SideArt", (0.16, 0.05, 0.42), rough=0.45)
M_ART2 = new_mat("SideArt2", (0.85, 0.16, 0.35), rough=0.45)
M_TMOLD = new_mat("TMolding", (0.85, 0.22, 0.10), rough=0.35)
M_BEZEL = new_mat("Bezel", (0.02, 0.02, 0.024), rough=0.6)
M_SCREEN = new_mat("Screen", (0.01, 0.02, 0.04), rough=0.10, emission=(0.10, 0.45, 0.85), strength=8.0)
M_SCAN = new_mat("ScreenSprite", (0.02, 0.02, 0.02), rough=0.2, emission=(1.0, 0.85, 0.15), strength=12.0)
M_MARQUEE = new_mat("Marquee", (0.95, 0.95, 0.95), rough=0.35, emission=(1.0, 0.75, 0.35), strength=9.0)
M_CPANEL = new_mat("ControlPanel", (0.09, 0.10, 0.14), rough=0.35)
M_METAL = new_mat("Chrome", (0.72, 0.73, 0.76), rough=0.20, metal=1.0)
M_BALL = new_mat("BallTop", (0.75, 0.05, 0.05), rough=0.15)
M_GRILLE = new_mat("Grille", (0.015, 0.015, 0.018), rough=0.85)
M_FLOOR = new_mat("Floor", (0.10, 0.10, 0.12), rough=0.35)
M_BTNS = [new_mat("Btn_%d" % i, c, 0.22) for i, c in enumerate(
    [(0.85, 0.12, 0.10), (0.95, 0.70, 0.06), (0.10, 0.45, 0.85),
     (0.15, 0.65, 0.25), (0.85, 0.35, 0.05), (0.60, 0.15, 0.70)])]

box("Floor", (12.0, 12.0, 0.06), (0.0, 0.0, -0.03), M_FLOOR)
box("BackWall", (10.0, 0.12, 3.4), (0.0, 1.6, 1.70), new_mat("Wall", (0.07, 0.07, 0.09), 0.9))

# side profile (y, z), extruded to form the two side panels
PROFILE = [
    (0.00, 0.00), (0.00, 0.86), (-0.18, 0.98), (-0.18, 1.06),
    (0.10, 1.20), (0.10, 1.66), (0.06, 1.72), (0.06, 1.86),
    (0.34, 1.96), (0.86, 1.96), (0.86, 0.00),
]
HW = 0.35
TH = 0.05
IN = HW - TH
profile_solid("SidePanelL", PROFILE, -HW, -IN, M_CAB_SIDE)
profile_solid("SidePanelR", PROFILE, IN, HW, M_CAB_SIDE)

for sx in (-1.0, 1.0):
    box("SideArt_%d" % (sx > 0), (0.004, 0.50, 0.90), (sx * (HW + 0.002), 0.42, 1.05), M_ART)
    box("SideArtStripe_%d" % (sx > 0), (0.005, 0.50, 0.10), (sx * (HW + 0.003), 0.42, 0.55), M_ART2)
    cyl("TMoldFront_%d" % (sx > 0), 0.012, 0.86, (sx * (HW - TH * 0.5), 0.0, 0.43), mat=M_TMOLD, seg=10)
    cyl("TMoldTop_%d" % (sx > 0), 0.012, 0.52, (sx * (HW - TH * 0.5), 0.60, 1.96),
        rot=(math.radians(90), 0, 0), mat=M_TMOLD, seg=10)

# structural panels between the sides
box("BasePlinth", (2 * IN, 0.86, 0.06), (0.0, 0.43, 0.03), M_CAB)
box("BackPanel", (2 * IN, 0.06, 1.90), (0.0, 0.83, 1.01), M_CAB)
box("LowerFront", (2 * IN, 0.05, 0.86), (0.0, 0.025, 0.43), M_CAB)
box("TopPanel", (2 * IN, 0.52, 0.06), (0.0, 0.60, 1.93), M_CAB)
box("MonitorFront", (2 * IN, 0.05, 0.46), (0.0, 0.125, 1.43), M_BEZEL)
box("SpeakerPanel", (2 * IN, 0.05, 0.16), (0.0, 0.085, 1.78), M_CAB)
box("PanelSkirt", (2 * IN, 0.03, 0.22), (0.0, -0.09, 0.92), M_CAB, rot=(math.radians(-56.3), 0, 0))
box("PanelLip", (2 * IN, 0.05, 0.09), (0.0, -0.155, 1.02), M_CAB)

# control panel plane
A = Vector((0.0, -0.18, 1.06))
B = Vector((0.0, 0.10, 1.20))
slope = math.atan2(B.z - A.z, B.y - A.y)
mid = (A + B) * 0.5
plen = (B - A).length
NRM = Vector((0.0, -math.sin(slope), math.cos(slope)))
box("ControlPanel", (2 * IN, plen, 0.035), (mid.x, mid.y, mid.z), M_CPANEL, bevel=0.006, rot=(slope, 0, 0))
box("ControlPanelTrim", (2 * IN + 0.006, 0.02, 0.045), (0.0, A.y - 0.005, A.z - 0.005), M_METAL, rot=(slope, 0, 0))

def on_panel(u, t, out=0.0):
    p = A + (B - A) * t
    return (u, p.y + NRM.y * out, p.z + NRM.z * out)

# joystick
cyl("JoyPlate", 0.045, 0.010, on_panel(-0.17, 0.42, 0.008), rot=(slope, 0, 0), mat=M_METAL, seg=24)
cyl("JoyShaft", 0.009, 0.085, on_panel(-0.17, 0.42, 0.055), rot=(slope, 0, 0), mat=M_METAL, seg=14)
cyl("JoyDustCover", 0.030, 0.014, on_panel(-0.17, 0.42, 0.020), rot=(slope, 0, 0), mat=M_CPANEL, seg=20, r2=0.014)
bmb = bmesh.new()
try:
    bmesh.ops.create_uvsphere(bmb, u_segments=20, v_segments=12, radius=0.023)
except TypeError:
    bmesh.ops.create_uvsphere(bmb, u_segments=20, v_segments=12, diameter=0.023)
for f in bmb.faces:
    f.smooth = True
obj_from_bm("JoyBall", bmb, M_BALL, on_panel(-0.17, 0.42, 0.108))

# action buttons, two arcs of three
for row, t in enumerate((0.34, 0.62)):
    for i in range(3):
        u = 0.02 + i * 0.075
        tt = t + (0.03 if i == 1 else 0.0)
        cyl("BtnRing_%d_%d" % (row, i), 0.019, 0.008, on_panel(u, tt, 0.010),
            rot=(slope, 0, 0), mat=M_METAL, seg=18)
        cyl("Btn_%d_%d" % (row, i), 0.0155, 0.010, on_panel(u, tt, 0.017),
            rot=(slope, 0, 0), mat=M_BTNS[(row * 3 + i) % len(M_BTNS)], seg=18)
for i, u in enumerate((-0.05, 0.005)):
    cyl("StartBtn_%d" % i, 0.012, 0.010, on_panel(u, 0.82, 0.012), rot=(slope, 0, 0),
        mat=M_BTNS[i % 2], seg=14)
cyl("JoyPlate2", 0.030, 0.008, on_panel(0.245, 0.80, 0.008), rot=(slope, 0, 0), mat=M_METAL, seg=18)

# monitor
SCR_TILT = math.radians(-8.0)
SZ, SY = 1.44, 0.235
box("Screen", (0.53, 0.014, 0.40), (0.0, SY, SZ), M_SCREEN, rot=(SCR_TILT, 0, 0))
for i in range(9):
    box("Sprite_%d" % i, (rnd.uniform(0.02, 0.05), 0.004, rnd.uniform(0.015, 0.035)),
        (rnd.uniform(-0.22, 0.22), SY - 0.011, SZ + rnd.uniform(-0.15, 0.16)), M_SCAN, rot=(SCR_TILT, 0, 0))
box("HUDBar", (0.44, 0.004, 0.020), (0.0, SY - 0.012, SZ + 0.175), M_SCAN, rot=(SCR_TILT, 0, 0))
box("CRTBody", (0.46, 0.30, 0.34), (0.0, 0.42, SZ - 0.02), M_CAB, bevel=0.02)
box("BezelTop", (0.62, 0.06, 0.05), (0.0, 0.15, 1.665), M_BEZEL)
box("BezelBot", (0.62, 0.06, 0.05), (0.0, 0.15, 1.215), M_BEZEL)
box("BezelL", (0.05, 0.06, 0.50), (-0.285, 0.15, 1.44), M_BEZEL)
box("BezelR", (0.05, 0.06, 0.50), (0.285, 0.15, 1.44), M_BEZEL)
box("Glass", (0.56, 0.008, 0.42), (0.0, 0.118, 1.44),
    new_mat("MonitorGlass", (0.8, 0.85, 0.9), 0.05, transmission=1.0, alpha=0.12))

# speaker grille
bm_holes = bmesh.new()
for cx in (-0.155, 0.155):
    for r in range(4):
        for c in range(7):
            bm_cyl(bm_holes, 0.0075, 0.008, (cx - 0.075 + c * 0.025, 0.055, 1.725 + r * 0.028), axis='Y', seg=8)
obj_from_bm("SpeakerGrille", bm_holes, M_GRILLE)

# marquee
mq_ang = math.atan2(1.96 - 1.86, 0.34 - 0.06)
mq_mid = ((0.06 + 0.34) * 0.5, (1.86 + 1.96) * 0.5)
mq_len = math.hypot(0.28, 0.10)
box("MarqueeBack", (2 * IN, mq_len, 0.03), (0.0, mq_mid[0], mq_mid[1] - 0.012), M_CAB, rot=(mq_ang, 0, 0))
box("Marquee", (2 * IN - 0.03, mq_len - 0.02, 0.012), (0.0, mq_mid[0] - 0.005, mq_mid[1] + 0.012),
    M_MARQUEE, rot=(mq_ang, 0, 0))
box("MarqueeTrimT", (2 * IN, 0.02, 0.030), (0.0, 0.335, 1.975), M_METAL, rot=(mq_ang, 0, 0))
box("MarqueeTrimB", (2 * IN, 0.02, 0.030), (0.0, 0.065, 1.855), M_METAL, rot=(mq_ang, 0, 0))

# coin door
box("CoinDoor", (0.36, 0.035, 0.28), (0.0, -0.012, 0.58), M_METAL, bevel=0.008)
for sx in (-0.10, 0.10):
    box("CoinSlot_%.2f" % sx, (0.016, 0.02, 0.055), (sx, -0.030, 0.66),
        new_mat("SlotDark_%.2f" % sx, (0.01, 0.01, 0.01), 0.8))
    box("CoinPlate_%.2f" % sx, (0.06, 0.012, 0.10), (sx, -0.028, 0.655), M_METAL, bevel=0.004)
box("CoinReturn", (0.16, 0.03, 0.06), (0.0, -0.028, 0.47), M_CAB, bevel=0.006)
box("CreditWindow", (0.11, 0.008, 0.035), (0.0, -0.031, 0.72),
    new_mat("CreditGlow", (0.05, 0.05, 0.05), 0.3, emission=(1.0, 0.4, 0.1), strength=6.0))
for sx in (-1, 1):
    for yy in (0.12, 0.74):
        cyl("Leveller_%d_%.2f" % (sx > 0, yy), 0.018, 0.02, (sx * 0.28, yy, 0.01), mat=M_METAL, seg=12)

# lighting and camera
add_area("Key", (-2.2, -2.4, 3.1), (0.0, 0.2, 1.3), 260.0, size=2.4, color=(0.95, 0.95, 1.0))
add_area("Fill", (2.6, -1.8, 1.6), (0.1, 0.2, 1.2), 70.0, size=2.4, color=(0.45, 0.55, 1.0))
add_area("Rim", (0.0, 2.6, 2.6), (0.0, 0.6, 1.6), 120.0, size=2.0, color=(1.0, 0.45, 0.75))
add_point("MarqueeGlow", (0.0, 0.05, 1.94), 12.0, (1.0, 0.72, 0.35), 0.18)
add_point("ScreenGlow", (0.0, -0.25, 1.45), 20.0, (0.35, 0.65, 1.0), 0.30)
add_camera((1.55, -2.05, 1.52), (0.0, 0.15, 1.12), lens=40.0)
