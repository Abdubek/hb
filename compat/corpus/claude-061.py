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

def bm_box(bm, size, center, bevel=0.0):
    tmp = bmesh.new()
    bmesh.ops.create_cube(tmp, size=1.0)
    bmesh.ops.scale(tmp, vec=Vector(size), verts=tmp.verts)
    if bevel > 0.0:
        bmesh.ops.bevel(tmp, geom=tmp.verts[:] + tmp.edges[:] + tmp.faces[:], offset=bevel,
                        segments=1, profile=0.5, affect='EDGES', clamp_overlap=True)
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
set_world((0.05, 0.055, 0.07), 0.55)
rnd = random.Random(61)

M_BRICK = new_mat("Brick", (0.42, 0.18, 0.13), rough=0.92)
M_BRICK2 = new_mat("BrickDark", (0.31, 0.14, 0.11), rough=0.95)
M_MORTAR = new_mat("Mortar", (0.62, 0.60, 0.55), rough=0.95)
M_STONE = new_mat("Hearthstone", (0.30, 0.29, 0.28), rough=0.75)
M_WOOD = new_mat("MantelWood", (0.24, 0.12, 0.055), rough=0.42)
M_SOOT = new_mat("Soot", (0.035, 0.032, 0.030), rough=0.95)
M_IRON = new_mat("Iron", (0.07, 0.07, 0.075), rough=0.42, metal=1.0)
M_BARK = new_mat("Bark", (0.20, 0.135, 0.09), rough=0.9)
M_LOGEND = new_mat("LogEnd", (0.60, 0.46, 0.30), rough=0.8)
M_EMBER = new_mat("Ember", (0.35, 0.06, 0.01), rough=0.9, emission=(1.0, 0.35, 0.06), strength=14.0)
M_FLAME = new_mat("Flame", (0.9, 0.4, 0.08), rough=0.9, emission=(1.0, 0.55, 0.15), strength=9.0, alpha=0.55)
M_WALL = new_mat("Plaster", (0.68, 0.65, 0.60), rough=0.9)
M_FLOOR = new_mat("FloorWood", (0.20, 0.13, 0.08), rough=0.55)

# room
box("Floor", (9.0, 9.0, 0.06), (0.0, 0.5, -0.03), M_FLOOR)
box("BackWall", (7.0, 0.16, 3.2), (0.0, 0.58, 1.60), M_WALL)
box("Baseboard", (7.0, 0.04, 0.12), (0.0, 0.48, 0.06), M_WALL)

# hearth
box("HearthSlab", (2.95, 1.05, 0.12), (0.0, -0.025, 0.06), M_STONE, bevel=0.012)
box("HearthNosing", (2.95, 0.05, 0.04), (0.0, -0.525, 0.10), M_STONE, bevel=0.008)

# masonry mass: facade x -1.15..1.15, z 0.12..1.62 ; opening x -0.60..0.60, z .12..1.05
box("PierL", (0.55, 0.50, 1.50), (-0.875, 0.25, 0.87), M_MORTAR)
box("PierR", (0.55, 0.50, 1.50), (0.875, 0.25, 0.87), M_MORTAR)
box("Lintel", (1.20, 0.50, 0.57), (0.0, 0.25, 1.335), M_MORTAR)
box("FireboxBack", (1.24, 0.06, 0.95), (0.0, 0.47, 0.595), M_SOOT)
box("FireboxSideL", (0.03, 0.44, 0.93), (-0.585, 0.22, 0.585), M_SOOT)
box("FireboxSideR", (0.03, 0.44, 0.93), (0.585, 0.22, 0.585), M_SOOT)
box("FireboxTop", (1.20, 0.44, 0.03), (0.0, 0.22, 1.035), M_SOOT)
box("FireboxFloor", (1.20, 0.44, 0.03), (0.0, 0.22, 0.135), M_SOOT)

# brick veneer over the facade, skipping the firebox opening
BW, BH, GAP, BD = 0.235, 0.095, 0.014, 0.055
bm_light = bmesh.new()
bm_dark = bmesh.new()

def lay_row(bm_a, bm_b, x0, x1, zc, offset):
    x = x0 - offset
    while x < x1 - 0.02:
        a = max(x, x0); b = min(x + BW, x1); w = b - a
        if w > 0.045:
            target = bm_b if rnd.random() < 0.28 else bm_a
            bm_box(target, (w - GAP, BD, BH - GAP), ((a + b) * 0.5, -BD * 0.5, zc), bevel=0.004)
        x += BW

z = 0.12 + BH * 0.5
row = 0
while z < 1.62 - BH * 0.4:
    off = (BW * 0.5) if row % 2 else 0.0
    if z + BH * 0.5 <= 1.06:
        lay_row(bm_light, bm_dark, -1.15, -0.60, z, off)
        lay_row(bm_light, bm_dark, 0.60, 1.15, z, off)
    else:
        lay_row(bm_light, bm_dark, -1.15, 1.15, z, off)
    z += BH; row += 1

obj_from_bm("BricksA", bm_light, M_BRICK)
obj_from_bm("BricksB", bm_dark, M_BRICK2)
box("Keystone", (0.16, 0.07, 0.17), (0.0, -0.035, 1.14), M_BRICK2, bevel=0.006)

# mantel
box("Mantel", (2.60, 0.72, 0.13), (0.0, 0.14, 1.685), M_WOOD, bevel=0.014, seg=3)
box("MantelLip", (2.60, 0.05, 0.05), (0.0, -0.195, 1.60), M_WOOD, bevel=0.008)
for sx in (-1.0, 1.0):
    box("Corbel_%d" % (sx > 0), (0.16, 0.26, 0.16), (sx * 0.95, 0.02, 1.545), M_WOOD, bevel=0.02)

# grate
for sx in (-1.0, 1.0):
    box("GrateRail_%d" % (sx > 0), (0.035, 0.44, 0.045), (sx * 0.42, 0.22, 0.215), M_IRON, bevel=0.008)
    for gy in (0.06, 0.38):
        cyl("GrateLeg_%d_%.2f" % (sx > 0, gy), 0.016, 0.09, (sx * 0.42, gy, 0.19), mat=M_IRON, seg=10)
bm_bars = bmesh.new()
for i in range(8):
    tmp = bmesh.new()
    bmesh.ops.create_cone(tmp, cap_ends=True, cap_tris=False, segments=10,
                          radius1=0.013, radius2=0.013, depth=0.90)
    bmesh.ops.rotate(tmp, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, 'Y'), verts=tmp.verts)
    bmesh.ops.translate(tmp, vec=Vector((0.0, 0.045 + i * 0.048, 0.235)), verts=tmp.verts)
    me = bpy.data.meshes.new("_bar"); tmp.to_mesh(me); tmp.free()
    bm_bars.from_mesh(me); bpy.data.meshes.remove(me)
for f in bm_bars.faces:
    if abs(f.normal.x) < 0.7: f.smooth = True
obj_from_bm("GrateBars", bm_bars, M_IRON)

# logs
def make_log(name, length, radius, center, rot, seed, mats):
    r = random.Random(seed)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=14,
                          radius1=radius, radius2=radius * r.uniform(0.86, 0.98), depth=length)
    bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, 'Y'), verts=bm.verts)
    for v in bm.verts:
        v.co.y += r.uniform(-1.0, 1.0) * radius * 0.10
        v.co.z += r.uniform(-1.0, 1.0) * radius * 0.10
        v.co.x += r.uniform(-1.0, 1.0) * radius * 0.05
    bm.normal_update()
    for f in bm.faces:
        if abs(f.normal.x) > 0.7: f.material_index = 1
        else: f.smooth = True
    return obj_from_bm(name, bm, mats, center, rot)

LOGMATS = [M_BARK, M_LOGEND]
fire_logs = [
    (0.95, 0.070, (-0.02, 0.13, 0.30), (0.0, 0.0, math.radians(3))),
    (0.90, 0.065, (0.03, 0.29, 0.30), (0.0, 0.0, math.radians(-4))),
    (0.86, 0.062, (-0.05, 0.21, 0.42), (0.0, math.radians(2), math.radians(6))),
    (0.80, 0.058, (0.04, 0.33, 0.43), (0.0, 0.0, math.radians(-2))),
    (0.74, 0.055, (0.0, 0.25, 0.545), (0.0, math.radians(-3), math.radians(9))),
]
for i, (ln, rr, ctr, rt) in enumerate(fire_logs):
    make_log("FireLog_%d" % i, ln, rr, ctr, rt, 100 + i, LOGMATS)

for i in range(6):
    make_log("Kindling_%d" % i, rnd.uniform(0.4, 0.6), rnd.uniform(0.014, 0.02),
             (rnd.uniform(-0.25, 0.25), rnd.uniform(0.10, 0.36), 0.255),
             (rnd.uniform(-0.2, 0.2), 0.0, rnd.uniform(-0.6, 0.6)), 200 + i, LOGMATS)

bm_e = bmesh.new()
for i in range(24):
    bm_box(bm_e, (rnd.uniform(0.04, 0.09), rnd.uniform(0.04, 0.08), 0.025),
           (rnd.uniform(-0.42, 0.42), rnd.uniform(0.08, 0.38), 0.185))
obj_from_bm("EmberBed", bm_e, M_EMBER)
for i in range(5):
    h = rnd.uniform(0.18, 0.34)
    cyl("Flame_%d" % i, rnd.uniform(0.05, 0.08), h,
        (rnd.uniform(-0.25, 0.25), rnd.uniform(0.14, 0.32), 0.30 + h * 0.5),
        rot=(0, 0, rnd.uniform(0, 3.0)), mat=M_FLAME, seg=10, r2=0.004)

# log pile stacked on the hearth
pile = [(1.02, -0.16, 0.20), (1.16, -0.16, 0.20), (1.30, -0.16, 0.20),
        (1.09, -0.16, 0.325), (1.23, -0.16, 0.325), (1.16, -0.16, 0.45)]
for i, (px, py, pz) in enumerate(pile):
    make_log("PileLog_%d" % i, 0.52, 0.065, (px, py, pz),
             (0.0, 0.0, math.radians(90) + rnd.uniform(-0.04, 0.04)), 300 + i, LOGMATS)

# fire tools
cyl("ToolStand", 0.09, 0.025, (-1.30, -0.28, 0.145), mat=M_IRON, seg=20)
cyl("ToolPost", 0.014, 0.62, (-1.30, -0.28, 0.46), mat=M_IRON, seg=12)
for i, ang in enumerate((0.4, 2.5, 4.6)):
    cyl("Tool_%d" % i, 0.008, 0.52,
        (-1.30 + 0.055 * math.cos(ang), -0.28 + 0.055 * math.sin(ang), 0.40),
        rot=(math.radians(4) * math.cos(ang), math.radians(4) * math.sin(ang), 0), mat=M_IRON, seg=8)

# mantel props
cyl("Candle_L", 0.028, 0.20, (-0.80, 0.09, 1.85), mat=new_mat("Wax", (0.90, 0.86, 0.76), 0.55), seg=18)
cyl("Candle_R", 0.028, 0.14, (-0.62, 0.09, 1.82), mat=new_mat("Wax2", (0.88, 0.83, 0.72), 0.55), seg=18)
box("Frame", (0.30, 0.03, 0.24), (0.72, 0.16, 1.87), new_mat("FrameWood", (0.15, 0.09, 0.05), 0.4), bevel=0.008)
box("FrameArt", (0.24, 0.01, 0.18), (0.72, 0.142, 1.87), new_mat("Art", (0.35, 0.38, 0.42), 0.6))

# lighting and camera
add_point("FireCore", (0.0, 0.22, 0.34), 90.0, (1.0, 0.44, 0.14), 0.16)
add_point("FireHigh", (0.0, 0.18, 0.72), 30.0, (1.0, 0.52, 0.20), 0.22)
add_point("FireSpill", (0.0, -0.30, 0.30), 22.0, (1.0, 0.46, 0.16), 0.30)
add_area("Key", (-2.4, -2.9, 2.9), (0.0, 0.2, 1.1), 220.0, size=2.6, color=(1.0, 0.94, 0.86))
add_area("Fill", (2.8, -2.6, 1.9), (0.0, 0.1, 1.0), 70.0, size=3.0, color=(0.72, 0.80, 1.0))
add_camera((2.30, -3.55, 1.62), (0.0, 0.10, 0.92), lens=45.0)
