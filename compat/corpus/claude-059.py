"""claude-059 : A bathroom vanity with sink, mirror and faucet."""
import bpy, bmesh, math
from mathutils import Vector, Matrix


# ------------------------------------------------------------------ helpers
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scn = bpy.context.scene
    try:
        scn.render.engine = 'BLENDER_EEVEE_NEXT'
    except Exception:
        pass
    scn.render.resolution_x, scn.render.resolution_y = 1400, 1750


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


def add_cyl(name, r, d, loc=(0, 0, 0), rot=(0, 0, 0), verts=28, material=None,
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


def look_at(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


# ------------------------------------------------------------------ materials
reset_scene()

M_WALL = mat("WallPaint", (0.80, 0.81, 0.79), 0.72)
M_TILE = mat("TileBack", (0.78, 0.82, 0.82), 0.20)
M_GROUT = mat("Grout", (0.60, 0.62, 0.62), 0.85)
M_FLOOR = mat("FloorTile", (0.30, 0.30, 0.31), 0.30)
M_CAB = mat("CabinetOak", (0.36, 0.24, 0.14), 0.42)
M_CAB_D = mat("CabinetOakDark", (0.28, 0.18, 0.10), 0.45)
M_STONE = mat("Countertop", (0.88, 0.87, 0.84), 0.16)
M_PORC = mat("Porcelain", (0.96, 0.96, 0.95), 0.10)
M_CHROME = mat("Chrome", (0.90, 0.91, 0.93), 0.05, 1.0)
M_MIRROR = mat("Mirror", (0.92, 0.94, 0.95), 0.01, 1.0)
M_GLASSSHADE = mat("Shade", (0.95, 0.93, 0.88), 0.35, emis=(1.0, 0.93, 0.80),
                   estr=9.0)
M_TOWEL = mat("Towel", (0.72, 0.76, 0.78), 0.90)
M_TOWEL2 = mat("TowelAccent", (0.36, 0.50, 0.55), 0.90)
M_GLASS = mat("Glass", (0.85, 0.92, 0.94), 0.05, 0.0, alpha=0.22)
M_SOAP = mat("Soap", (0.85, 0.78, 0.62), 0.35)
M_LEAF = mat("Leaf", (0.20, 0.36, 0.18), 0.55)
M_BASKET = mat("Basket", (0.55, 0.42, 0.24), 0.75)

# ------------------------------------------------------------------ room shell
WALL_Y = 0.0
add_box("BackWall", (5.0, 0.12, 3.0), (0, WALL_Y + 0.06, 1.5), material=M_WALL)
add_box("SideWall", (0.12, 3.0, 3.0), (-1.90, -1.44, 1.5), material=M_WALL)
add_box("Floor", (5.0, 3.2, 0.10), (0, -1.55, -0.05), material=M_FLOOR)
add_box("Ceiling", (5.0, 3.2, 0.10), (0, -1.55, 2.85), material=M_WALL)
add_box("Skirting", (5.0, 0.02, 0.09), (0, -0.01, 0.045), material=M_WALL)

# tiled splash-back area behind the vanity
TILE_W, TILE_H, GAP = 0.20, 0.20, 0.006
add_box("TileField", (2.10, 0.012, 1.20), (0, -0.005, 1.28), material=M_GROUT)
for r in range(6):
    for c in range(10):
        x = -0.95 + c * (TILE_W + GAP * 0.5)
        z = 0.72 + r * (TILE_H + GAP * 0.5)
        if x > 1.0:
            continue
        add_box("Tile_%d_%d" % (r, c), (TILE_W, 0.010, TILE_H), (x, -0.014, z),
                material=M_TILE, bevel=0.004)

# ------------------------------------------------------------------ vanity cabinet
VW, VD, VH = 1.50, 0.55, 0.78     # width, depth, cabinet height
VZ0 = 0.13                        # floating above a recessed plinth
CAB_C = VZ0 + VH / 2
add_box("CabinetCarcass", (VW, VD, VH), (0, -VD / 2 + 0.01, CAB_C), material=M_CAB,
        bevel=0.008)
add_box("CabinetPlinth", (VW - 0.14, VD - 0.10, VZ0), (0, -VD / 2 + 0.02, VZ0 / 2),
        material=M_CAB_D)

# two doors and a central drawer bank
for k, dx in enumerate((-0.47, 0.47)):
    add_box("Door%d" % k, (0.52, 0.022, VH - 0.06), (dx, -VD - 0.002, CAB_C),
            material=M_CAB_D, bevel=0.006)
    add_box("DoorPanel%d" % k, (0.40, 0.010, VH - 0.20), (dx, -VD - 0.010, CAB_C),
            material=M_CAB, bevel=0.004)
    add_cyl("DoorPull%d" % k, 0.008, 0.11, (dx + (0.20 if k == 0 else -0.20),
                                            -VD - 0.030, CAB_C + 0.20),
            verts=12, material=M_CHROME)
for k in range(2):
    z = VZ0 + 0.20 + k * 0.36
    add_box("Drawer%d" % k, (0.42, 0.022, 0.32), (0.0, -VD - 0.002, z),
            material=M_CAB_D, bevel=0.006)
    add_box("DrawerPull%d" % k, (0.24, 0.028, 0.020), (0.0, -VD - 0.026, z + 0.11),
            material=M_CHROME, bevel=0.006)

# stone countertop with a small back-splash upstand
TOP_Z = VZ0 + VH
add_box("Countertop", (VW + 0.06, VD + 0.05, 0.045), (0, -VD / 2 + 0.005, TOP_Z + 0.022),
        material=M_STONE, bevel=0.006)
add_box("Upstand", (VW + 0.06, 0.028, 0.09), (0, -0.012, TOP_Z + 0.09),
        material=M_STONE, bevel=0.005)
COUNTER_TOP_Z = TOP_Z + 0.045

# ------------------------------------------------------------------ vessel basin
BASIN_C = Vector((0.0, -0.30, COUNTER_TOP_Z))
bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=48,
                      radius1=0.145, radius2=0.205, depth=0.135)
# lift so the base sits on the counter
bmesh.ops.translate(bm, verts=bm.verts, vec=(0.0, 0.0, 0.0675))
top_face = max(bm.faces, key=lambda f: f.calc_center_median().z)
res = bmesh.ops.inset_individual(bm, faces=[top_face], thickness=0.016, depth=0.0)
bmesh.ops.translate(bm, verts=list(top_face.verts), vec=(0, 0, -0.105))
# small dished floor: pull the centre down a touch more
inner = list(top_face.verts)
centre = sum((v.co for v in inner), Vector()) / len(inner)
for v in inner:
    v.co.z -= 0.008 * (1.0 - (v.co - centre).length / 0.20)
bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.006, segments=2, affect='EDGES',
                profile=0.6)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
me = bpy.data.meshes.new("Basin")
bm.to_mesh(me)
bm.free()
basin = bpy.data.objects.new("Basin", me)
bpy.context.collection.objects.link(basin)
basin.location = BASIN_C
finish(basin, M_PORC, smooth=True)

add_cyl("Drain", 0.021, 0.008, (BASIN_C.x, BASIN_C.y, BASIN_C.z + 0.030), verts=24,
        material=M_CHROME)
add_torus("DrainRing", 0.026, 0.004, (BASIN_C.x, BASIN_C.y, BASIN_C.z + 0.031),
          material=M_CHROME, mseg=28, nseg=8)

# ------------------------------------------------------------------ faucet
FX, FY = 0.0, -0.09
add_cyl("FaucetBase", 0.038, 0.022, (FX, FY, COUNTER_TOP_Z + 0.011), verts=28,
        material=M_CHROME)

cu = bpy.data.curves.new("FaucetSpoutCurve", 'CURVE')
cu.dimensions = '3D'
cu.bevel_depth = 0.017
cu.bevel_resolution = 6
cu.resolution_u = 14
cu.fill_mode = 'FULL'
sp = cu.splines.new('BEZIER')
sp.bezier_points.add(3)
coords = [(FX, FY, COUNTER_TOP_Z + 0.02),
          (FX, FY, COUNTER_TOP_Z + 0.20),
          (FX, FY - 0.10, COUNTER_TOP_Z + 0.255),
          (FX, FY - 0.185, COUNTER_TOP_Z + 0.205)]
for bp, co in zip(sp.bezier_points, coords):
    bp.co = co
    bp.handle_left_type = bp.handle_right_type = 'AUTO'
spout = bpy.data.objects.new("FaucetSpout", cu)
bpy.context.collection.objects.link(spout)
spout.data.materials.append(M_CHROME)
shade_smooth(spout)

add_cyl("Aerator", 0.019, 0.018, (FX, FY - 0.185, COUNTER_TOP_Z + 0.190), verts=20,
        material=M_CHROME)

# two lever handles either side of the spout
for sgn in (-1, 1):
    hx = FX + sgn * 0.155
    add_cyl("HandleBase%d" % (sgn > 0), 0.030, 0.020, (hx, FY, COUNTER_TOP_Z + 0.010),
            verts=22, material=M_CHROME)
    add_cyl("HandleStem%d" % (sgn > 0), 0.014, 0.055, (hx, FY, COUNTER_TOP_Z + 0.045),
            verts=16, material=M_CHROME)
    lev = add_box("HandleLever%d" % (sgn > 0), (0.020, 0.100, 0.016),
                  (hx, FY - 0.040, COUNTER_TOP_Z + 0.078),
                  rot=(math.radians(-16), 0, 0), material=M_CHROME, bevel=0.006)

# ------------------------------------------------------------------ mirror
MIR_Z = 1.62
add_box("MirrorFrame", (1.06, 0.055, 1.16), (0, 0.03, MIR_Z), material=M_CAB_D,
        bevel=0.010)
add_box("MirrorGlass", (0.96, 0.012, 1.06), (0, 0.0, MIR_Z), material=M_MIRROR)
add_box("MirrorBevel", (0.90, 0.006, 1.00), (0, -0.008, MIR_Z), material=M_MIRROR)

# wall sconces flanking the mirror
for sgn in (-1, 1):
    sx = sgn * 0.78
    add_cyl("SconceBack%d" % (sgn > 0), 0.045, 0.030, (sx, 0.02, MIR_Z + 0.18),
            (math.pi / 2, 0, 0), verts=22, material=M_CHROME)
    add_cyl("SconceArm%d" % (sgn > 0), 0.014, 0.10, (sx, -0.06, MIR_Z + 0.18),
            (math.pi / 2, 0, 0), verts=14, material=M_CHROME)
    sh = add_cyl("SconceShade%d" % (sgn > 0), 0.055, 0.14, (sx, -0.13, MIR_Z + 0.18),
                 verts=26, material=M_GLASSSHADE, r2=0.070)
    ld = bpy.data.lights.new("SconceLight%d" % (sgn > 0), 'POINT')
    ld.energy, ld.shadow_soft_size = 28.0, 0.06
    ld.color = (1.0, 0.92, 0.82)
    lo = bpy.data.objects.new("SconceLight%d" % (sgn > 0), ld)
    bpy.context.collection.objects.link(lo)
    lo.location = (sx, -0.13, MIR_Z + 0.18)

# ------------------------------------------------------------------ accessories
# soap dispenser
add_cyl("SoapBody", 0.033, 0.11, (0.36, -0.24, COUNTER_TOP_Z + 0.055), verts=24,
        material=M_GLASS)
add_cyl("SoapFill", 0.029, 0.075, (0.36, -0.24, COUNTER_TOP_Z + 0.038), verts=20,
        material=M_SOAP)
add_cyl("SoapCollar", 0.020, 0.030, (0.36, -0.24, COUNTER_TOP_Z + 0.125), verts=18,
        material=M_CHROME)
add_box("SoapNozzle", (0.055, 0.018, 0.014), (0.325, -0.24, COUNTER_TOP_Z + 0.142),
        material=M_CHROME, bevel=0.004)

# tumbler with two toothbrushes
add_cyl("Tumbler", 0.036, 0.10, (-0.42, -0.24, COUNTER_TOP_Z + 0.05), verts=24,
        material=M_PORC, r2=0.040)
for k, sgn in enumerate((-1, 1)):
    add_cyl("Brush%d" % k, 0.006, 0.16,
            (-0.42 + sgn * 0.010, -0.24 + sgn * 0.008, COUNTER_TOP_Z + 0.11),
            rot=(math.radians(sgn * 7), math.radians(sgn * 5), 0), verts=10,
            material=M_TOWEL2 if k else M_PORC)

# folded towel stack and a small tray
add_box("Tray", (0.30, 0.20, 0.014), (-0.50, -0.40, COUNTER_TOP_Z + 0.007),
        material=M_CAB_D, bevel=0.005)
for k in range(2):
    add_box("FoldedTowel%d" % k, (0.24, 0.16, 0.045),
            (-0.50, -0.40, COUNTER_TOP_Z + 0.038 + k * 0.048),
            material=M_TOWEL if k == 0 else M_TOWEL2, bevel=0.012)

# towel ring on the side wall return
add_box("RingPlate", (0.02, 0.05, 0.05), (-0.84, -0.02, 1.02), material=M_CHROME,
        bevel=0.006)
add_torus("TowelRing", 0.09, 0.008, (-0.84, -0.14, 0.96),
          rot=(0, math.pi / 2, 0), material=M_CHROME, mseg=32, nseg=10)
hang = add_box("HangingTowel", (0.012, 0.16, 0.34), (-0.845, -0.14, 0.77),
               material=M_TOWEL, bevel=0.010)

# small plant on the counter
add_cyl("PotBody", 0.055, 0.10, (0.60, -0.36, COUNTER_TOP_Z + 0.05), verts=24,
        material=M_BASKET, r2=0.065)
for k in range(9):
    a = 2 * math.pi * k / 9
    leaf = add_box("Leaf%d" % k, (0.020, 0.10, 0.006),
                   (0.60 + 0.045 * math.cos(a), -0.36 + 0.045 * math.sin(a),
                    COUNTER_TOP_Z + 0.145),
                   rot=(math.radians(38), 0, a), material=M_LEAF, bevel=0.004)

# floor mat
add_box("BathMat", (1.10, 0.62, 0.022), (0.0, -0.95, 0.011), material=M_TOWEL2,
        bevel=0.008)

# ------------------------------------------------------------------ lighting
world = bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
wbg = world.node_tree.nodes["Background"]
wbg.inputs["Color"].default_value = (0.16, 0.18, 0.21, 1.0)
wbg.inputs["Strength"].default_value = 0.6

cd = bpy.data.lights.new("CeilingSoft", 'AREA')
cd.energy, cd.size, cd.size_y = 160.0, 1.6, 1.0
cd.shape = 'RECTANGLE'
cd.color = (1.0, 0.96, 0.92)
ceil = bpy.data.objects.new("CeilingSoft", cd)
bpy.context.collection.objects.link(ceil)
ceil.location = (0.0, -1.05, 2.70)
look_at(ceil, (0.0, -0.35, 1.0))

fd = bpy.data.lights.new("FrontFill", 'AREA')
fd.energy, fd.size = 70.0, 2.2
fd.color = (0.82, 0.88, 1.0)
fil = bpy.data.objects.new("FrontFill", fd)
bpy.context.collection.objects.link(fil)
fil.location = (1.6, -2.4, 1.9)
look_at(fil, (0.0, -0.3, 1.2))

# ------------------------------------------------------------------ camera
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 35
cam = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam)
cam.location = (0.90, -2.15, 1.60)
look_at(cam, (-0.02, -0.20, 1.15))
bpy.context.scene.camera = cam

print("claude-059 bathroom vanity built: %d objects" % len(bpy.data.objects))
