"""claude-048 - A charging station for electric cars.

Four-bay EV charging plaza: steel canopy with a solar deck and lit soffit,
two dual-outlet charging pedestals with hanging cables, painted bays, kerbs,
bollards, an information totem and two simple parked cars for scale.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = 'METRIC'


def link(obj):
    bpy.context.scene.collection.objects.link(obj)
    return obj


def make_mat(name, color, rough=0.5, metal=0.0, emis=None, emis_str=0.0,
             alpha=1.0, transmission=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if "Transmission Weight" in b.inputs:
        b.inputs["Transmission Weight"].default_value = transmission
    if emis is not None:
        if "Emission Color" in b.inputs:
            b.inputs["Emission Color"].default_value = (emis[0], emis[1], emis[2], 1.0)
        b.inputs["Emission Strength"].default_value = emis_str
    if alpha < 1.0:
        b.inputs["Alpha"].default_value = alpha
        try:
            m.blend_method = 'BLEND'
        except Exception:
            pass
    return m


def tag_new(bm, before, index, smooth=False):
    for f in bm.faces:
        if f not in before:
            f.material_index = index
            if smooth:
                f.smooth = True


def bm_box(bm, center, size, index=0, rot=None):
    m = Matrix.Translation(Vector(center))
    if rot is not None:
        m = m @ Euler(rot).to_matrix().to_4x4()
    m = m @ Matrix.Diagonal(Vector((size[0], size[1], size[2], 1.0)))
    before = set(bm.faces)
    bmesh.ops.create_cube(bm, size=1.0, matrix=m)
    tag_new(bm, before, index)


def bm_cyl(bm, center, radius, depth, index=0, segments=24, r2=None, rot=None, smooth=True):
    m = Matrix.Translation(Vector(center))
    if rot is not None:
        m = m @ Euler(rot).to_matrix().to_4x4()
    before = set(bm.faces)
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius, radius2=(radius if r2 is None else r2),
                          depth=depth, matrix=m)
    for f in bm.faces:
        if f not in before:
            f.material_index = index
            if smooth and abs(f.calc_center_median().z - m.translation.z) < depth * 0.49:
                f.smooth = True


def bm_sphere(bm, center, radius, index=0, subdiv=2, scale=(1, 1, 1)):
    m = Matrix.Translation(Vector(center)) @ Matrix.Diagonal(
        Vector((scale[0], scale[1], scale[2], 1.0)))
    before = set(bm.faces)
    bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=radius, matrix=m)
    tag_new(bm, before, index, smooth=True)


def finish(bm, name, mats, location=(0, 0, 0), rotation=(0, 0, 0)):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    obj.location = location
    obj.rotation_euler = rotation
    for m in mats:
        me.materials.append(m)
    return link(obj)


def poly_tube(name, points, radius, material, res=4):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    sp = cu.splines.new('POLY')
    sp.points.add(len(points) - 1)
    for i, p in enumerate(points):
        sp.points[i].co = (p[0], p[1], p[2], 1.0)
    cu.bevel_depth = radius
    cu.bevel_resolution = res
    cu.use_fill_caps = True
    obj = bpy.data.objects.new(name, cu)
    cu.materials.append(material)
    return link(obj)


def bevel(obj, width=0.02, segments=3):
    mod = obj.modifiers.new("Bevel", 'BEVEL')
    mod.width = width
    mod.segments = segments
    mod.limit_method = 'ANGLE'
    mod.angle_limit = math.radians(50)
    return mod


def look_at(obj, target):
    d = Vector(target) - obj.location
    obj.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


# --------------------------------------------------------------------------
reset_scene()

M_ASPHALT = make_mat("Asphalt", (0.045, 0.046, 0.05), rough=0.92)
M_CONCRETE = make_mat("Concrete", (0.46, 0.45, 0.43), rough=0.85)
M_PAINT_W = make_mat("LinePaintWhite", (0.88, 0.88, 0.86), rough=0.6)
M_PAINT_G = make_mat("BayPaintGreen", (0.07, 0.34, 0.20), rough=0.75)
M_STEEL = make_mat("CanopySteel", (0.68, 0.69, 0.71), rough=0.35, metal=1.0)
M_STEEL_DK = make_mat("DarkSteel", (0.14, 0.15, 0.16), rough=0.45, metal=0.85)
M_SOFFIT = make_mat("Soffit", (0.90, 0.91, 0.92), rough=0.55)
M_LEDPANEL = make_mat("LedStrip", (1.0, 1.0, 1.0), rough=0.3,
                      emis=(0.92, 0.96, 1.0), emis_str=12.0)
M_PVGLASS = make_mat("PVGlass", (0.02, 0.04, 0.12), rough=0.12, metal=0.1)
M_PVFRAME = make_mat("PVFrame", (0.74, 0.75, 0.77), rough=0.3, metal=1.0)
M_CHARGER = make_mat("ChargerShell", (0.93, 0.94, 0.95), rough=0.35)
M_ACCENT = make_mat("BrandGreen", (0.10, 0.62, 0.36), rough=0.4)
M_SCREEN = make_mat("Screen", (0.05, 0.08, 0.12), rough=0.15,
                    emis=(0.30, 0.75, 1.0), emis_str=6.0)
M_RUBBER = make_mat("Rubber", (0.035, 0.035, 0.04), rough=0.85)
M_CABLE = make_mat("Cable", (0.06, 0.06, 0.07), rough=0.7)
M_CARBODY_A = make_mat("CarBodyBlue", (0.03, 0.12, 0.35), rough=0.22, metal=0.6)
M_CARBODY_B = make_mat("CarBodySilver", (0.55, 0.57, 0.60), rough=0.25, metal=0.8)
M_GLASS = make_mat("CarGlass", (0.05, 0.07, 0.09), rough=0.08,
                   transmission=0.85, alpha=0.35)
M_CHROME = make_mat("Chrome", (0.85, 0.86, 0.88), rough=0.12, metal=1.0)
M_TAIL = make_mat("TailLight", (0.6, 0.03, 0.03), rough=0.25,
                  emis=(1.0, 0.08, 0.05), emis_str=4.0)
M_HEAD = make_mat("HeadLight", (0.9, 0.9, 0.9), rough=0.1,
                  emis=(0.9, 0.95, 1.0), emis_str=3.0)

# ------------------------------------------------------------------- ground
bm = bmesh.new()
bm_box(bm, (0, 0, -0.06), (60, 60, 0.12), 0)
bm_box(bm, (0, 0, 0.005), (22, 18, 0.02), 1)   # station apron slab
finish(bm, "Ground", [M_ASPHALT, M_CONCRETE])

# --------------------------------------------------- bay markings and kerbs
BAY_W = 2.7
BAY_L = 5.2
bay_x = [-4.05, -1.35, 1.35, 4.05]
bm = bmesh.new()
for x in bay_x:
    bm_box(bm, (x, 0.0, 0.024), (BAY_W - 0.55, BAY_L - 0.6, 0.008), 1)   # green field
for i in range(len(bay_x) + 1):
    x = -5.4 + i * BAY_W
    bm_box(bm, (x, 0.0, 0.028), (0.12, BAY_L, 0.010), 0)
bm_box(bm, (0, BAY_L / 2, 0.028), (BAY_W * 4 + 0.12, 0.12, 0.010), 0)
# kerb behind the bays where the chargers stand
bm_box(bm, (0, BAY_L / 2 + 0.75, 0.075), (12.0, 1.4, 0.15), 2)
bm_box(bm, (0, BAY_L / 2 + 0.05, 0.09), (12.0, 0.10, 0.19), 2)
finish(bm, "BayMarkings", [M_PAINT_W, M_PAINT_G, M_CONCRETE])

# ------------------------------------------------------------------- canopy
COL_X = [-5.6, 5.6]
COL_Y = [-1.9, 3.1]
ROOF_Z = 4.30
bm = bmesh.new()
for cx in COL_X:
    for cy in COL_Y:
        bm_box(bm, (cx, cy, 0.10), (0.70, 0.70, 0.20), 1)              # base plate
        bm_cyl(bm, (cx, cy, 2.15), 0.16, 4.10, 0, segments=20)          # column
        bm_cyl(bm, (cx, cy, 0.24), 0.22, 0.10, 1, segments=20)
# main beams along X, purlins along Y
for cy in COL_Y:
    bm_box(bm, (0, cy, ROOF_Z - 0.05), (11.9, 0.22, 0.45), 0)
for k in range(7):
    x = -5.4 + k * 1.8
    bm_box(bm, (x, 0.6, ROOF_Z + 0.16), (0.14, 5.6, 0.22), 0)
# diagonal knee braces
for cx in COL_X:
    for cy in COL_Y:
        s = -1 if cx > 0 else 1
        p0 = Vector((cx, cy, ROOF_Z - 1.05))
        p1 = Vector((cx + s * 1.0, cy, ROOF_Z - 0.25))
        d = p1 - p0
        m = (Matrix.Translation((p0 + p1) * 0.5)
             @ d.to_track_quat('Z', 'Y').to_matrix().to_4x4())
        before = set(bm.faces)
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=12,
                              radius1=0.07, radius2=0.07, depth=d.length, matrix=m)
        tag_new(bm, before, 0, smooth=True)
finish(bm, "CanopyStructure", [M_STEEL, M_STEEL_DK])

# roof deck, soffit and LED strips
bm = bmesh.new()
bm_box(bm, (0, 0.6, ROOF_Z + 0.30), (12.4, 6.0, 0.10), 0)          # deck
bm_box(bm, (0, 0.6, ROOF_Z - 0.32), (12.2, 5.8, 0.06), 1)          # soffit panel
for k in range(4):
    x = -4.5 + k * 3.0
    bm_box(bm, (x, 0.6, ROOF_Z - 0.37), (0.22, 5.2, 0.04), 2)      # LED strips
bm_box(bm, (0, -2.45, ROOF_Z + 0.30), (12.4, 0.30, 0.42), 3)       # fascia
bm_box(bm, (0, 3.65, ROOF_Z + 0.30), (12.4, 0.30, 0.42), 3)
finish(bm, "CanopyDeck", [M_STEEL_DK, M_SOFFIT, M_LEDPANEL, M_ACCENT])

# solar modules on top of the canopy deck
bm = bmesh.new()
for c in range(6):
    for r in range(3):
        px = -5.0 + c * 2.0
        py = -1.2 + r * 1.8
        bm_box(bm, (px, py, ROOF_Z + 0.40), (1.86, 1.66, 0.05), 0)
        bm_box(bm, (px, py, ROOF_Z + 0.435), (1.74, 1.54, 0.012), 1)
        for cc in range(3):
            for rr in range(3):
                bm_box(bm, (px - 0.56 + cc * 0.56, py - 0.50 + rr * 0.50,
                            ROOF_Z + 0.443), (0.50, 0.44, 0.004), 1)
finish(bm, "CanopySolar", [M_PVFRAME, M_PVGLASS])


# ------------------------------------------------------------ charge points
def build_charger(name, x, y, yaw):
    bm = bmesh.new()
    bm_box(bm, (0, 0, 0.06), (0.80, 0.60, 0.12), 2)                 # plinth
    bm_box(bm, (0, 0, 0.85), (0.62, 0.42, 1.50), 0)                 # shell
    bm_box(bm, (0, 0, 1.66), (0.66, 0.46, 0.12), 1)                 # accent cap
    bm_box(bm, (0, -0.22, 1.28), (0.40, 0.03, 0.30), 3)             # screen
    bm_box(bm, (0, -0.215, 0.98), (0.30, 0.02, 0.06), 1)            # card reader
    for sx in (-1, 1):                                              # holsters
        bm_box(bm, (sx * 0.20, 0.20, 1.10), (0.16, 0.10, 0.30), 2)
        bm_cyl(bm, (sx * 0.20, 0.28, 1.24), 0.055, 0.16, 2, segments=14,
               rot=(math.radians(90), 0, 0))
    bm_box(bm, (0, 0.215, 0.60), (0.34, 0.02, 0.50), 2)             # vent panel
    for k in range(6):
        bm_box(bm, (0, 0.222, 0.42 + k * 0.07), (0.30, 0.01, 0.025), 1)
    obj = finish(bm, name, [M_CHARGER, M_ACCENT, M_STEEL_DK, M_SCREEN],
                 location=(x, y, 0.15), rotation=(0, 0, yaw))
    bevel(obj, width=0.018, segments=3)
    return obj


CHARGER_Y = BAY_L / 2 + 0.75
build_charger("ChargerA", -2.70, CHARGER_Y, math.radians(180))
build_charger("ChargerB", 2.70, CHARGER_Y, math.radians(180))


# ------------------------------------------------------------------- cars
def build_car(name, x, y, yaw, body_mat, plugged_from=None):
    bm = bmesh.new()
    # lower body
    bm_box(bm, (0, 0.0, 0.62), (1.86, 4.45, 0.66), 0)
    bm_box(bm, (0, 0.25, 1.05), (1.72, 3.05, 0.32), 0)
    # greenhouse
    bm_box(bm, (0, 0.20, 1.36), (1.58, 2.30, 0.46), 1)
    bm_box(bm, (0, 0.20, 1.60), (1.50, 2.05, 0.10), 0)
    # sills, bumpers
    bm_box(bm, (0, -2.18, 0.55), (1.80, 0.22, 0.44), 2)
    bm_box(bm, (0, 2.18, 0.55), (1.80, 0.22, 0.44), 2)
    for sx in (-1, 1):
        bm_box(bm, (sx * 0.94, 0.0, 0.38), (0.10, 3.4, 0.20), 2)
        # lights
        bm_box(bm, (sx * 0.62, 2.27, 0.78), (0.46, 0.08, 0.16), 4)
        bm_box(bm, (sx * 0.62, -2.27, 0.82), (0.46, 0.08, 0.14), 5)
        # mirrors
        bm_box(bm, (sx * 1.00, 0.95, 1.24), (0.22, 0.12, 0.10), 2)
    # wheels
    for sx in (-1, 1):
        for sy in (-1, 1):
            wx, wy = sx * 0.90, sy * 1.42
            bm_cyl(bm, (wx, wy, 0.34), 0.34, 0.24, 3, segments=24,
                   rot=(0, math.radians(90), 0))
            bm_cyl(bm, (wx + sx * 0.02, wy, 0.34), 0.20, 0.26, 6, segments=20,
                   rot=(0, math.radians(90), 0))
            # wheel arch
            bm_box(bm, (sx * 0.93, wy, 0.60), (0.06, 0.86, 0.44), 2)
    # charge port flap
    bm_box(bm, (-0.94, -1.75, 0.86), (0.03, 0.24, 0.20), 2)
    obj = finish(bm, name, [body_mat, M_GLASS, M_RUBBER, M_RUBBER, M_HEAD, M_TAIL,
                            M_CHROME],
                 location=(x, y, 0.02), rotation=(0, 0, yaw))
    bevel(obj, width=0.05, segments=3)

    if plugged_from is not None:
        # hanging cable from charger holster down to the car's port
        c = math.cos(yaw)
        s = math.sin(yaw)
        port_local = Vector((-0.94, -1.75, 0.88))
        port = Vector((x + port_local.x * c - port_local.y * s,
                       y + port_local.x * s + port_local.y * c,
                       0.02 + port_local.z))
        a = Vector(plugged_from)
        pts = []
        for k in range(15):
            t = k / 14.0
            p = a.lerp(port, t)
            p.z -= 0.85 * math.sin(math.pi * t) ** 1.2
            pts.append((p.x, p.y, max(p.z, 0.06)))
        poly_tube(name + "_Cable", pts, 0.028, M_CABLE, res=3)
        bmc = bmesh.new()
        bm_box(bmc, (0, 0, 0), (0.10, 0.16, 0.12), 0)
        finish(bmc, name + "_Connector", [M_STEEL_DK],
               location=(port.x - 0.06 * c, port.y - 0.06 * s, port.z),
               rotation=(0, 0, yaw))
    return obj


build_car("CarBlue", bay_x[1], -0.15, math.radians(180), M_CARBODY_A,
          plugged_from=(-2.70 + 0.20, CHARGER_Y - 0.28, 1.32))
build_car("CarSilver", bay_x[2], -0.10, math.radians(180), M_CARBODY_B,
          plugged_from=(2.70 - 0.20, CHARGER_Y - 0.28, 1.32))

# idle cable coiled on the second outlet of charger A
poly_tube("IdleCable",
          [(-2.90, CHARGER_Y - 0.30, 1.30), (-3.10, CHARGER_Y - 0.55, 0.95),
           (-3.05, CHARGER_Y - 0.70, 0.55), (-2.85, CHARGER_Y - 0.60, 0.35),
           (-2.72, CHARGER_Y - 0.35, 0.42), (-2.86, CHARGER_Y - 0.20, 0.70)],
          0.028, M_CABLE, res=3)

# ------------------------------------------------------------------ bollards
bm = bmesh.new()
for bx in (-6.6, -3.9, 3.9, 6.6):
    bm_cyl(bm, (bx, BAY_L / 2 + 1.25, 0.45), 0.09, 0.90, 0, segments=16)
    bm_cyl(bm, (bx, BAY_L / 2 + 1.25, 0.92), 0.10, 0.06, 1, segments=16)
finish(bm, "Bollards", [M_STEEL_DK, M_ACCENT])

# --------------------------------------------------------------- info totem
bm = bmesh.new()
bm_box(bm, (0, 0, 0.09), (0.90, 0.60, 0.18), 2)
bm_box(bm, (0, 0, 1.70), (0.55, 0.28, 3.20), 0)
bm_box(bm, (0, -0.15, 2.55), (0.42, 0.03, 1.10), 3)
bm_box(bm, (0, 0, 3.42), (0.62, 0.34, 0.24), 1)
finish(bm, "InfoTotem", [M_CHARGER, M_ACCENT, M_STEEL_DK, M_SCREEN],
       location=(-7.6, 2.4, 0.02), rotation=(0, 0, math.radians(-28)))

# ------------------------------------------------------------------ lighting
sun_data = bpy.data.lights.new("Sun", 'SUN')
sun_data.energy = 2.0
sun_data.angle = math.radians(2.0)
sun_data.color = (1.0, 0.86, 0.70)
sun = bpy.data.objects.new("Sun", sun_data)
sun.rotation_euler = (math.radians(63), 0, math.radians(-125))
sun.location = (0, 0, 25)
link(sun)

for k in range(4):
    x = -4.5 + k * 3.0
    ld = bpy.data.lights.new("CanopyLight_%d" % k, 'AREA')
    ld.shape = 'RECTANGLE'
    ld.size, ld.size_y = 0.22, 5.2
    ld.energy = 260.0
    ld.color = (0.95, 0.97, 1.0)
    lo = bpy.data.objects.new("CanopyLight_%d" % k, ld)
    lo.location = (x, 0.6, ROOF_Z - 0.42)
    lo.rotation_euler = (math.radians(180), 0, 0)
    link(lo)

fill = bpy.data.lights.new("DuskFill", 'AREA')
fill.shape = 'SQUARE'
fill.size = 26.0
fill.energy = 900.0
fill.color = (0.45, 0.58, 0.95)
fo = bpy.data.objects.new("DuskFill", fill)
fo.location = (0, 0, 18.0)
link(fo)

world = bpy.data.worlds.new("StationWorld")
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.05, 0.07, 0.12, 1.0)
bg.inputs["Strength"].default_value = 1.2
bpy.context.scene.world = world

# ------------------------------------------------------------------- camera
cam_data = bpy.data.cameras.new("StationCam")
cam_data.lens = 30.0
cam_data.clip_end = 500.0
cam = bpy.data.objects.new("StationCam", cam_data)
cam.location = (11.0, -12.5, 5.4)
link(cam)
look_at(cam, (0.0, 1.0, 1.5))
bpy.context.scene.camera = cam

bpy.context.view_layer.update()
print("claude-048: EV charging station built with %d objects" % len(bpy.data.objects))
