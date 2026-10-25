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
set_world((0.06, 0.065, 0.08), 0.8)
rnd = random.Random(63)

M_BODY = new_mat("BodyRed", (0.42, 0.045, 0.045), rough=0.35)
M_BODY_D = new_mat("BodyDark", (0.10, 0.10, 0.11), rough=0.45)
M_TRIM = new_mat("Trim", (0.66, 0.67, 0.70), rough=0.30, metal=1.0)
M_INT = new_mat("Interior", (0.55, 0.56, 0.58), rough=0.55)
M_INT_D = new_mat("InteriorBack", (0.13, 0.14, 0.16), rough=0.7)
M_GLASS = new_mat("Glass", (0.92, 0.95, 1.0), rough=0.03, transmission=1.0, ior=1.45, alpha=0.16)
M_SIGN = new_mat("Sign", (0.85, 0.10, 0.10), rough=0.4, emission=(1.0, 0.22, 0.16), strength=6.0)
M_SIGN2 = new_mat("SignWhite", (0.9, 0.9, 0.9), rough=0.4, emission=(1.0, 0.98, 0.92), strength=7.0)
M_LEDSTRIP = new_mat("LedStrip", (1.0, 1.0, 1.0), rough=0.5, emission=(1.0, 0.98, 0.92), strength=5.0)
M_LCD = new_mat("LCD", (0.02, 0.03, 0.03), rough=0.15, emission=(0.25, 1.0, 0.55), strength=5.0)
M_BTN = new_mat("Button", (0.14, 0.14, 0.16), rough=0.35)
M_BTN_HI = new_mat("ButtonHi", (0.75, 0.16, 0.10), rough=0.35)
M_SLOT = new_mat("Slot", (0.02, 0.02, 0.02), rough=0.8)
M_FLAP = new_mat("Flap", (0.10, 0.11, 0.13), rough=0.25, transmission=0.6, alpha=0.45)
M_FLOOR = new_mat("Floor", (0.36, 0.36, 0.37), rough=0.6)
M_WALL = new_mat("Wall", (0.52, 0.53, 0.55), rough=0.9)
M_CAN_TOP = new_mat("CanTop", (0.78, 0.79, 0.82), rough=0.25, metal=1.0)
M_LABELS = [new_mat("Label_%d" % i, c, 0.4) for i, c in enumerate(
    [(0.72, 0.10, 0.10), (0.10, 0.32, 0.68), (0.95, 0.72, 0.10),
     (0.10, 0.52, 0.24), (0.55, 0.15, 0.60), (0.92, 0.42, 0.06)])]
M_BOTTLE = new_mat("BottleGlass", (0.55, 0.72, 0.60), rough=0.08, transmission=0.85, alpha=0.45)

box("Floor", (10.0, 10.0, 0.06), (0.0, 0.0, -0.03), M_FLOOR)
box("BackWall", (8.0, 0.12, 3.2), (0.0, 0.55, 1.60), M_WALL)

# cabinet shell
W, D, H = 1.05, 0.82, 1.90
XL, XR = -W * 0.5, W * 0.5
YF, YB = -D * 0.5, D * 0.5
box("SideL", (0.03, D, H), (XL + 0.015, 0.0, H * 0.5), M_BODY, bevel=0.008)
box("SideR", (0.03, D, H), (XR - 0.015, 0.0, H * 0.5), M_BODY, bevel=0.008)
box("Back", (W, 0.03, H), (0.0, YB - 0.015, H * 0.5), M_BODY_D)
box("Top", (W, D, 0.04), (0.0, 0.0, H - 0.02), M_BODY, bevel=0.010)
box("Bottom", (W, D, 0.08), (0.0, 0.0, 0.04), M_BODY_D, bevel=0.008)

WX0, WX1, WZ0, WZ1 = -0.465, 0.125, 0.42, 1.62
WCX = (WX0 + WX1) * 0.5
box("FrontStripL", (0.06, 0.05, WZ1 - WZ0 + 0.02), (XL + 0.03, YF + 0.025, (WZ0 + WZ1) * 0.5), M_BODY, bevel=0.006)
box("ControlColumn", (0.40, 0.05, 1.54), (0.325, YF + 0.025, 0.85), M_BODY, bevel=0.008)
box("Header", (W, 0.06, 0.28), (0.0, YF + 0.02, 1.76), M_BODY, bevel=0.010)
box("HeaderSign", (0.96, 0.02, 0.22), (0.0, YF - 0.012, 1.76), M_SIGN)
box("HeaderSignBar", (0.60, 0.012, 0.05), (0.0, YF - 0.024, 1.78), M_SIGN2)

# lower front frame around the delivery bin opening
box("LowFrameTop", (0.65, 0.05, 0.04), (-0.20, YF + 0.025, 0.40), M_BODY)
box("LowFrameBot", (0.65, 0.05, 0.04), (-0.20, YF + 0.025, 0.10), M_BODY)
box("LowFrameL", (0.065, 0.05, 0.34), (-0.4925, YF + 0.025, 0.25), M_BODY)
box("LowFrameR", (0.065, 0.05, 0.34), (0.0925, YF + 0.025, 0.25), M_BODY)

# glazing
box("Glass", (WX1 - WX0, 0.016, WZ1 - WZ0), (WCX, YF + 0.012, (WZ0 + WZ1) * 0.5), M_GLASS)
box("GlassTrimT", (WX1 - WX0 + 0.03, 0.03, 0.022), (WCX, YF + 0.012, WZ1 + 0.011), M_TRIM)
box("GlassTrimB", (WX1 - WX0 + 0.03, 0.03, 0.022), (WCX, YF + 0.012, WZ0 - 0.011), M_TRIM)
box("Handle", (0.03, 0.06, 0.90), (WX1 + 0.02, YF - 0.03, 1.05), M_TRIM, bevel=0.008)

# interior
box("IntBack", (WX1 - WX0 + 0.04, 0.02, WZ1 - WZ0), (WCX, 0.36, (WZ0 + WZ1) * 0.5), M_INT_D)
box("IntSideL", (0.02, 0.72, WZ1 - WZ0), (WX0 - 0.01, 0.0, (WZ0 + WZ1) * 0.5), M_INT)
box("IntSideR", (0.02, 0.72, WZ1 - WZ0), (WX1 + 0.01, 0.0, (WZ0 + WZ1) * 0.5), M_INT)
box("IntFloor", (WX1 - WX0, 0.72, 0.02), (WCX, 0.0, WZ0 + 0.01), M_INT)
for sx, xx in ((-1, WX0 + 0.025), (1, WX1 - 0.025)):
    box("LightStrip_%d" % (sx > 0), (0.022, 0.03, 1.10), (xx, -0.30, 1.02), M_LEDSTRIP)

# products
def make_can(name, r, h, center, label):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=18,
                          radius1=r, radius2=r, depth=h)
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=18,
                          radius1=r * 0.86, radius2=r * 0.86, depth=0.008,
                          matrix=Matrix.Translation((0.0, 0.0, h * 0.5 + 0.004)))
    bm.normal_update()
    for f in bm.faces:
        if abs(f.normal.z) < 0.7: f.smooth = True
        if f.calc_center_median().z > h * 0.5 - 0.001: f.material_index = 1
    return obj_from_bm(name, bm, [label, M_CAN_TOP], center)

def make_bottle(name, center, label):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16,
                          radius1=0.032, radius2=0.032, depth=0.13,
                          matrix=Matrix.Translation((0, 0, 0.065)))
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16,
                          radius1=0.032, radius2=0.013, depth=0.045,
                          matrix=Matrix.Translation((0, 0, 0.1525)))
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16,
                          radius1=0.013, radius2=0.013, depth=0.035,
                          matrix=Matrix.Translation((0, 0, 0.1925)))
    bm.normal_update()
    for f in bm.faces:
        if abs(f.normal.z) < 0.7: f.smooth = True
    body = obj_from_bm(name, bm, M_BOTTLE, center)
    cyl(name + "_cap", 0.0145, 0.022, (center[0], center[1], center[2] + 0.221), mat=label, seg=16)
    cyl(name + "_label", 0.0335, 0.070, (center[0], center[1], center[2] + 0.060), mat=label, seg=16)
    return body

shelf_z = [0.50, 0.80, 1.10, 1.40]
col_x = [-0.40, -0.275, -0.15, -0.025, 0.10]
row_y = [-0.24, -0.10, 0.04, 0.18]
for si, sz in enumerate(shelf_z):
    box("Shelf_%d" % si, (WX1 - WX0 - 0.02, 0.68, 0.018), (WCX, 0.0, sz), M_TRIM)
    box("PriceRail_%d" % si, (WX1 - WX0 - 0.02, 0.012, 0.030), (WCX, -0.34, sz + 0.022), M_BODY_D)
    for ci, cx in enumerate(col_x):
        lab = M_LABELS[(si * 3 + ci) % len(M_LABELS)]
        if si % 2 == 0:
            for ri, ry in enumerate(row_y):
                make_can("Can_%d_%d_%d" % (si, ci, ri), 0.033, 0.115, (cx, ry, sz + 0.009 + 0.0575), lab)
        else:
            for ri, ry in enumerate(row_y[:3]):
                make_bottle("Bottle_%d_%d_%d" % (si, ci, ri), (cx, ry, sz + 0.009), lab)
        if ci < len(col_x) - 1:
            box("Divider_%d_%d" % (si, ci), (0.006, 0.62, 0.10), (cx + 0.0625, 0.0, sz + 0.06), M_INT)

# control column: keypad, display, payment
box("KeypadPlate", (0.30, 0.03, 0.32), (0.325, YF + 0.005, 1.20), M_BODY_D, bevel=0.008)
bm_keys = bmesh.new()
for r in range(4):
    for c in range(3):
        bm_cyl(bm_keys, 0.022, 0.020, (0.245 + c * 0.080, YF - 0.008, 1.315 - r * 0.078), axis='Y', seg=16)
obj_from_bm("Keypad", bm_keys, M_BTN)
cyl("KeyHiA", 0.022, 0.022, (0.245, YF - 0.010, 1.081), rot=(math.radians(90), 0, 0), mat=M_BTN_HI, seg=16)
cyl("KeyHiB", 0.022, 0.022, (0.405, YF - 0.010, 1.081), rot=(math.radians(90), 0, 0), mat=M_BTN_HI, seg=16)
box("Display", (0.26, 0.02, 0.10), (0.325, YF + 0.002, 1.45), M_BODY_D, bevel=0.006)
box("DisplayLCD", (0.22, 0.008, 0.068), (0.325, YF - 0.012, 1.45), M_LCD)
box("CoinPlate", (0.09, 0.02, 0.16), (0.455, YF + 0.002, 0.92), M_TRIM, bevel=0.005)
box("CoinSlot", (0.012, 0.02, 0.055), (0.455, YF - 0.012, 0.955), M_SLOT)
cyl("CoinReturnBtn", 0.016, 0.018, (0.455, YF - 0.012, 0.875), rot=(math.radians(90), 0, 0), mat=M_BTN_HI, seg=14)
box("BillUnit", (0.22, 0.04, 0.13), (0.295, YF + 0.005, 0.76), M_BODY_D, bevel=0.008)
box("BillSlot", (0.15, 0.02, 0.014), (0.295, YF - 0.016, 0.795), M_SLOT)
box("BillArrow", (0.05, 0.006, 0.020), (0.295, YF - 0.018, 0.735),
    new_mat("BillLed", (0.1, 0.1, 0.1), 0.4, emission=(0.2, 0.9, 1.0), strength=6.0))
box("CardReader", (0.15, 0.055, 0.19), (0.435, YF - 0.020, 0.57), M_BODY_D, bevel=0.010)
box("CardSlot", (0.10, 0.02, 0.013), (0.435, YF - 0.048, 0.625), M_SLOT)
for i, rr in enumerate((0.016, 0.026, 0.036)):
    cyl("Contactless_%d" % i, rr, 0.004, (0.435, YF - 0.049, 0.545), rot=(math.radians(90), 0, 0), mat=M_TRIM, seg=20)
cyl("CardLed", 0.007, 0.006, (0.375, YF - 0.049, 0.625), rot=(math.radians(90), 0, 0),
    mat=new_mat("GreenLed", (0.05, 0.1, 0.05), 0.3, emission=(0.2, 1.0, 0.35), strength=9.0), seg=12)
box("ReturnCup", (0.11, 0.05, 0.07), (0.225, YF - 0.018, 0.50), M_BODY_D, bevel=0.008)
box("ReturnCupHole", (0.085, 0.03, 0.045), (0.225, YF - 0.030, 0.495), M_SLOT)

# delivery bin
box("BinCavity", (0.52, 0.30, 0.26), (-0.20, 0.02, 0.25), M_SLOT)
box("BinBack", (0.52, 0.02, 0.26), (-0.20, 0.18, 0.25), M_INT_D)
box("BinFlap", (0.50, 0.018, 0.25), (-0.20, YF - 0.005, 0.263), M_FLAP, bevel=0.005, rot=(math.radians(-16), 0, 0))
box("BinLip", (0.56, 0.06, 0.025), (-0.20, YF + 0.01, 0.105), M_TRIM, bevel=0.006)
box("StripeL", (0.006, 0.60, 1.20), (XL - 0.004, 0.05, 1.05), M_SIGN2)

# lighting and camera
add_area("Key", (-2.2, -2.8, 3.0), (-0.1, 0.0, 1.1), 420.0, size=2.5, color=(1.0, 0.97, 0.94))
add_area("Fill", (2.6, -2.4, 1.7), (0.3, 0.0, 1.0), 160.0, size=3.0, color=(0.80, 0.86, 1.0))
add_area("Rim", (0.4, 2.2, 2.6), (0.0, 0.0, 1.4), 140.0, size=2.0, color=(0.85, 0.90, 1.0))
add_camera((1.95, -2.35, 1.55), (0.0, -0.05, 1.00), lens=45.0)
