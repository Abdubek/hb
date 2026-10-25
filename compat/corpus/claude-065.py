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
set_world((0.10, 0.11, 0.13), 0.9)
rnd = random.Random(65)

M_BODY = new_mat("BodyShell", (0.24, 0.27, 0.31), rough=0.35)
M_BODY_D = new_mat("BodyDark", (0.075, 0.080, 0.090), rough=0.42)
M_ACCENT = new_mat("Accent", (0.05, 0.35, 0.62), rough=0.30)
M_STEEL = new_mat("Steel", (0.66, 0.67, 0.70), rough=0.28, metal=1.0)
M_RUBBER = new_mat("Rubber", (0.045, 0.045, 0.05), rough=0.85)
M_GLASS = new_mat("CoverGlass", (0.85, 0.90, 0.95), rough=0.05, transmission=1.0, alpha=0.10)
M_SCREEN = new_mat("ScreenBase", (0.02, 0.03, 0.05), rough=0.10, emission=(0.06, 0.13, 0.24), strength=3.0)
M_UI_HEAD = new_mat("UIHeader", (0.03, 0.05, 0.08), rough=0.2, emission=(0.10, 0.45, 0.85), strength=9.0)
M_UI_A = new_mat("UIBtnA", (0.03, 0.05, 0.05), rough=0.2, emission=(0.15, 0.75, 0.55), strength=8.0)
M_UI_B = new_mat("UIBtnB", (0.05, 0.04, 0.02), rough=0.2, emission=(0.95, 0.65, 0.12), strength=8.0)
M_UI_C = new_mat("UIBtnC", (0.05, 0.05, 0.05), rough=0.2, emission=(0.85, 0.88, 0.95), strength=7.0)
M_SIGN = new_mat("Signage", (0.9, 0.9, 0.9), rough=0.35, emission=(0.98, 0.95, 0.90), strength=8.0)
M_LED_G = new_mat("LedGreen", (0.05, 0.1, 0.05), rough=0.3, emission=(0.20, 1.0, 0.35), strength=12.0)
M_LED_R = new_mat("LedRed", (0.1, 0.03, 0.03), rough=0.3, emission=(1.0, 0.15, 0.10), strength=10.0)
M_SLOTDARK = new_mat("SlotDark", (0.012, 0.012, 0.014), rough=0.85)
M_FLOOR = new_mat("Concrete", (0.34, 0.34, 0.35), rough=0.65)
M_WALL = new_mat("Wall", (0.46, 0.47, 0.49), rough=0.9)

box("Floor", (14.0, 14.0, 0.06), (0.0, 0.0, -0.03), M_FLOOR)
box("BackWall", (10.0, 0.14, 3.2), (0.0, 1.35, 1.60), M_WALL)
box("WallBand", (10.0, 0.02, 0.10), (0.0, 1.27, 1.05), M_ACCENT)

# plinth and body
box("Plinth", (0.86, 0.66, 0.08), (0.0, 0.0, 0.04), M_BODY_D, bevel=0.012, seg=3)
box("Body", (0.74, 0.54, 1.10), (0.0, 0.0, 0.63), M_BODY, bevel=0.022, seg=3)
box("BodyFascia", (0.70, 0.02, 1.02), (0.0, -0.275, 0.64), M_BODY_D, bevel=0.006)
box("AccentStripe", (0.70, 0.008, 0.05), (0.0, -0.288, 1.12), M_ACCENT)
for sx in (-1.0, 1.0):
    box("SideStripe_%d" % (sx > 0), (0.006, 0.36, 0.70), (sx * 0.372, 0.02, 0.72), M_ACCENT)
    cyl("FootB_%d" % (sx > 0), 0.035, 0.02, (sx * 0.34, 0.24, 0.01), mat=M_RUBBER, seg=16)
    cyl("FootF_%d" % (sx > 0), 0.035, 0.02, (sx * 0.34, -0.24, 0.01), mat=M_RUBBER, seg=16)

# tilted head carrying the touch screen
TILT = math.radians(18.0)
HEAD_C = Vector((0.0, 0.02, 1.42))
box("Head", (0.78, 0.30, 0.52), HEAD_C, M_BODY, bevel=0.022, seg=3, rot=(-TILT, 0, 0))
box("HeadCollar", (0.76, 0.52, 0.05), (0.0, 0.0, 1.185), M_BODY_D, bevel=0.010)

R = Matrix.Rotation(-TILT, 4, 'X')
NRM = Vector((0.0, -math.cos(TILT), math.sin(TILT)))
FACE = HEAD_C + R @ Vector((0.0, -0.15, 0.0))

def scr(u, v, out):
    """Point on the screen plane: u across, v up the panel, out along the normal."""
    return FACE + (R @ Vector((u, 0.0, v))) + NRM * out

box("ScreenBezel", (0.68, 0.05, 0.46), scr(0.0, 0.0, 0.020), M_BODY_D, bevel=0.010, seg=3, rot=(-TILT, 0, 0))
box("ScreenPanel", (0.60, 0.012, 0.385), scr(0.0, 0.0, 0.044), M_SCREEN, rot=(-TILT, 0, 0))
box("ScreenGlass", (0.63, 0.006, 0.415), scr(0.0, 0.0, 0.052), M_GLASS, rot=(-TILT, 0, 0))

# on-screen interface
box("UI_Header", (0.56, 0.004, 0.052), scr(0.0, 0.152, 0.049), M_UI_HEAD, rot=(-TILT, 0, 0))
ui_mats = [M_UI_A, M_UI_B, M_UI_A, M_UI_B]
for i in range(4):
    ux = -0.145 + (i % 2) * 0.29
    uv = 0.055 - (i // 2) * 0.115
    box("UI_Btn_%d" % i, (0.255, 0.004, 0.085), scr(ux, uv, 0.049), ui_mats[i],
        bevel=0.006, seg=2, rot=(-TILT, 0, 0))
box("UI_Footer", (0.56, 0.004, 0.040), scr(0.0, -0.155, 0.049), M_UI_C, rot=(-TILT, 0, 0))
for i in range(3):
    box("UI_Tick_%d" % i, (0.055, 0.004, 0.014), scr(-0.20 + i * 0.075, -0.155, 0.052),
        M_UI_HEAD, rot=(-TILT, 0, 0))

# header signage
SIGN_C = HEAD_C + R @ Vector((0.0, -0.03, 0.34))
box("SignBox", (0.82, 0.16, 0.24), SIGN_C, M_BODY_D, bevel=0.014, seg=3, rot=(-TILT, 0, 0))
sign_face = SIGN_C + (R @ Vector((0.0, -0.081, 0.0)))
box("SignFace", (0.74, 0.012, 0.17), sign_face + NRM * 0.004, M_SIGN, rot=(-TILT, 0, 0))
box("SignBar", (0.50, 0.008, 0.030), sign_face + NRM * 0.012 + (R @ Vector((0.0, 0.0, -0.045))),
    M_ACCENT, rot=(-TILT, 0, 0))

# card reader with PIN pad
CR = Vector((0.235, -0.335, 1.01))
box("CardReader", (0.17, 0.13, 0.26), CR, M_BODY_D, bevel=0.014, seg=3)
box("CardReaderFace", (0.15, 0.012, 0.24), (CR.x, CR.y - 0.066, CR.z), M_BODY, bevel=0.006)
box("CardSlot", (0.105, 0.02, 0.014), (CR.x, CR.y - 0.072, CR.z + 0.098), M_SLOTDARK)
box("CardSlotGlow", (0.125, 0.006, 0.026), (CR.x, CR.y - 0.070, CR.z + 0.098), M_LED_G)
for i, rr in enumerate((0.018, 0.028, 0.038)):
    cyl("Tap_%d" % i, rr, 0.004, (CR.x, CR.y - 0.073 - i * 0.001, CR.z + 0.045),
        rot=(math.radians(90), 0, 0), mat=(M_STEEL if i else M_ACCENT), seg=24)
for r in range(4):
    for c in range(3):
        cyl("PinKey_%d_%d" % (r, c), 0.0105, 0.010,
            (CR.x - 0.036 + c * 0.036, CR.y - 0.072, CR.z - 0.020 - r * 0.026),
            rot=(math.radians(90), 0, 0), mat=M_BODY, seg=14)
cyl("PinOK", 0.0105, 0.010, (CR.x + 0.055, CR.y - 0.072, CR.z - 0.046),
    rot=(math.radians(90), 0, 0), mat=M_UI_A, seg=14)
cyl("PinCancel", 0.0105, 0.010, (CR.x + 0.055, CR.y - 0.072, CR.z - 0.020),
    rot=(math.radians(90), 0, 0), mat=M_LED_R, seg=14)
cyl("ReaderLed", 0.007, 0.006, (CR.x - 0.058, CR.y - 0.074, CR.z + 0.045),
    rot=(math.radians(90), 0, 0), mat=M_LED_G, seg=12)
box("Shroud", (0.19, 0.08, 0.02), (CR.x, CR.y - 0.030, CR.z + 0.145), M_BODY_D,
    bevel=0.006, rot=(math.radians(-14), 0, 0))

# ticket and receipt dispensing
box("TicketBezel", (0.30, 0.05, 0.10), (-0.11, -0.290, 0.74), M_STEEL, bevel=0.010)
box("TicketSlot", (0.22, 0.03, 0.020), (-0.11, -0.305, 0.755), M_SLOTDARK)
box("TicketTray", (0.30, 0.11, 0.018), (-0.11, -0.345, 0.700), M_BODY_D, bevel=0.006, rot=(math.radians(10), 0, 0))
box("TicketGlow", (0.24, 0.006, 0.010), (-0.11, -0.309, 0.712), M_UI_HEAD)
box("ReceiptSlot", (0.12, 0.02, 0.012), (-0.11, -0.300, 0.845), M_SLOTDARK)
box("ReceiptBezel", (0.16, 0.03, 0.034), (-0.11, -0.293, 0.845), M_BODY_D, bevel=0.006)
box("Ticket", (0.075, 0.06, 0.002), (-0.11, -0.335, 0.757),
    new_mat("TicketPaper", (0.92, 0.90, 0.84), 0.75), rot=(math.radians(6), 0, 0))

# barcode / QR scanner window
box("ScannerHousing", (0.16, 0.05, 0.13), (-0.22, -0.290, 1.02), M_BODY_D, bevel=0.010)
box("ScannerWindow", (0.12, 0.012, 0.085), (-0.22, -0.312, 1.02),
    new_mat("ScannerGlass", (0.12, 0.02, 0.02), 0.15, emission=(1.0, 0.12, 0.08), strength=3.0))
box("ScannerLabel", (0.14, 0.006, 0.022), (-0.22, -0.306, 0.945), M_UI_C)

# assist button, info plate, speaker grille, grab rail
box("HelpButtonPlate", (0.09, 0.03, 0.09), (0.235, -0.288, 0.76), M_BODY_D, bevel=0.008)
cyl("HelpButton", 0.028, 0.016, (0.235, -0.302, 0.76), rot=(math.radians(90), 0, 0), mat=M_UI_B, seg=20)
box("InfoPlate", (0.22, 0.006, 0.11), (-0.16, -0.289, 0.475), M_UI_C)
for i in range(3):
    box("InfoLine_%d" % i, (0.17, 0.004, 0.010), (-0.16, -0.293, 0.505 - i * 0.024), M_BODY_D)
bm_sp = bmesh.new()
for r in range(3):
    for c in range(6):
        tmp = bmesh.new()
        bmesh.ops.create_cone(tmp, cap_ends=True, cap_tris=False, segments=8,
                              radius1=0.005, radius2=0.005, depth=0.006)
        bmesh.ops.rotate(tmp, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, 'X'), verts=tmp.verts)
        bmesh.ops.translate(tmp, vec=Vector((0.20 + c * 0.016, -0.286, 1.15 - r * 0.016)), verts=tmp.verts)
        me = bpy.data.meshes.new("_sp"); tmp.to_mesh(me); tmp.free()
        bm_sp.from_mesh(me); bpy.data.meshes.remove(me)
obj_from_bm("SpeakerGrille", bm_sp, M_SLOTDARK)
cyl("GrabRail", 0.016, 0.34, (0.386, -0.10, 0.86), rot=(math.radians(90), 0, 0), mat=M_STEEL, seg=16)
for yy in (-0.26, 0.06):
    cyl("RailPost_%.2f" % yy, 0.013, 0.05, (0.372, yy, 0.86), rot=(0, math.radians(90), 0), mat=M_STEEL, seg=12)

# lighting and camera
add_area("Key", (-1.9, -2.4, 3.2), (0.0, -0.1, 1.25), 460.0, size=2.6, color=(1.0, 0.97, 0.93))
add_area("Fill", (2.4, -2.0, 1.9), (0.1, 0.0, 1.1), 150.0, size=3.0, color=(0.82, 0.88, 1.0))
add_area("Rim", (0.6, 2.0, 2.8), (0.0, 0.2, 1.5), 180.0, size=2.2, color=(0.88, 0.92, 1.0))
add_point("ScreenGlow", (0.0, -0.45, 1.55), 18.0, (0.45, 0.65, 1.0), 0.25)
add_point("SignGlow", (0.0, -0.30, 1.78), 10.0, (1.0, 0.95, 0.85), 0.20)
add_camera((1.55, -2.05, 1.62), (0.0, -0.05, 1.08), lens=50.0)
