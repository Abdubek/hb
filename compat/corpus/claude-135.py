# claude-135 : Dentist waiting room with reception window, seating,
#              magazine table and planters.  Blender 4.5 LTS.
#
# Builds the whole scene from an empty factory startup.  No rendering,
# no file output, no external assets.

import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

random.seed(1974)

# ----------------------------------------------------------------------
# scene reset
# ----------------------------------------------------------------------

bpy.ops.wm.read_factory_settings(use_empty=True)

scene = bpy.context.scene
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
try:
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
except TypeError:
    scene.render.engine = 'BLENDER_EEVEE'

world = bpy.data.worlds.new("RoomWorld")
world.use_nodes = True
scene.world = world
_bg = world.node_tree.nodes["Background"]
_bg.inputs[0].default_value = (0.055, 0.062, 0.070, 1.0)
_bg.inputs[1].default_value = 1.0


# ----------------------------------------------------------------------
# material helper
# ----------------------------------------------------------------------

def make_mat(name, color, rough=0.55, metal=0.0, alpha=1.0, ior=1.45,
             transmission=0.0, emission=None, emission_strength=0.0,
             sheen=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")

    def s(key, value):
        if bsdf and key in bsdf.inputs:
            bsdf.inputs[key].default_value = value

    s("Base Color", (color[0], color[1], color[2], 1.0))
    s("Roughness", rough)
    s("Metallic", metal)
    s("IOR", ior)
    s("Alpha", alpha)
    s("Transmission Weight", transmission)
    s("Sheen Weight", sheen)
    if emission is not None:
        s("Emission Color", (emission[0], emission[1], emission[2], 1.0))
        s("Emission Strength", emission_strength)
    if alpha < 1.0 or transmission > 0.0:
        try:
            mat.blend_method = 'BLEND'
        except (AttributeError, TypeError):
            pass
        try:
            mat.surface_render_method = 'BLENDED'
        except (AttributeError, TypeError):
            pass
    mat.diffuse_color = (color[0], color[1], color[2], alpha)
    return mat


M = {
    "floor":      make_mat("VinylFloor",     (0.400, 0.392, 0.372), rough=0.35),
    "floor_dark": make_mat("FloorBorder",    (0.196, 0.196, 0.196), rough=0.42),
    "wall":       make_mat("WallPaint",      (0.760, 0.775, 0.755), rough=0.85),
    "accent":     make_mat("AccentPaint",    (0.075, 0.255, 0.265), rough=0.80),
    "ceiling":    make_mat("CeilingTile",    (0.880, 0.880, 0.870), rough=0.95),
    "trim":       make_mat("WhiteTrim",      (0.860, 0.860, 0.855), rough=0.40),
    "wood":       make_mat("LightWood",      (0.400, 0.255, 0.130), rough=0.38),
    "wood_dark":  make_mat("WalnutWood",     (0.140, 0.075, 0.040), rough=0.40),
    "steel":      make_mat("BrushedSteel",   (0.620, 0.630, 0.645), rough=0.28, metal=1.0),
    "chrome":     make_mat("Chrome",         (0.780, 0.790, 0.800), rough=0.12, metal=1.0),
    "fabric_a":   make_mat("SeatTeal",       (0.055, 0.215, 0.230), rough=0.92, sheen=0.35),
    "fabric_b":   make_mat("SeatSand",       (0.330, 0.270, 0.185), rough=0.92, sheen=0.35),
    "plastic":    make_mat("WhitePlastic",   (0.700, 0.705, 0.700), rough=0.35),
    "glass":      make_mat("WindowGlass",    (0.780, 0.850, 0.860), rough=0.03,
                           alpha=0.20, transmission=0.92, ior=1.45),
    "screen":     make_mat("MonitorScreen",  (0.020, 0.030, 0.045), rough=0.20,
                           emission=(0.30, 0.45, 0.60), emission_strength=1.6),
    "panel":      make_mat("LightPanel",     (1.0, 1.0, 1.0), rough=0.4,
                           emission=(1.0, 0.965, 0.910), emission_strength=6.0),
    "daylight":   make_mat("Daylight",       (1.0, 1.0, 1.0), rough=0.5,
                           emission=(0.72, 0.82, 1.0), emission_strength=4.0),
    "soil":       make_mat("PottingSoil",    (0.055, 0.038, 0.026), rough=0.98),
    "pot_a":      make_mat("PotCeramic",     (0.520, 0.480, 0.420), rough=0.45),
    "pot_b":      make_mat("PotCharcoal",    (0.085, 0.090, 0.092), rough=0.55),
    "leaf":       make_mat("LeafGreen",      (0.045, 0.180, 0.055), rough=0.42),
    "leaf2":      make_mat("LeafGreenDark",  (0.022, 0.110, 0.040), rough=0.45),
    "stem":       make_mat("PlantStem",      (0.060, 0.130, 0.048), rough=0.60),
    "paper":      make_mat("PaperWhite",     (0.820, 0.815, 0.800), rough=0.75),
    "mag_a":      make_mat("MagCoverRed",    (0.420, 0.075, 0.070), rough=0.28),
    "mag_b":      make_mat("MagCoverBlue",   (0.060, 0.155, 0.360), rough=0.28),
    "mag_c":      make_mat("MagCoverYellow", (0.520, 0.400, 0.060), rough=0.28),
    "mag_d":      make_mat("MagCoverGreen",  (0.075, 0.290, 0.180), rough=0.28),
    "art_a":      make_mat("ArtCalm",        (0.290, 0.400, 0.420), rough=0.55),
    "art_b":      make_mat("ArtWarm",        (0.470, 0.360, 0.250), rough=0.55),
    "black":      make_mat("MattBlack",      (0.022, 0.022, 0.024), rough=0.65),
}


# ----------------------------------------------------------------------
# geometry builder : accumulates parts in one bmesh -> one object
# ----------------------------------------------------------------------

class Builder:
    """Small helper that welds primitive parts into a single mesh object."""

    def __init__(self, name):
        self.name = name
        self.bm = bmesh.new()
        self.materials = []

    def _mi(self, mat):
        if mat is None:
            mat = M["plastic"]
        if mat not in self.materials:
            self.materials.append(mat)
        return self.materials.index(mat)

    def _place(self, verts, loc, rot, scale):
        mat = (Matrix.Translation(Vector(loc)) @
               Euler(rot, 'XYZ').to_matrix().to_4x4() @
               Matrix.Diagonal(Vector(scale)).to_4x4())
        bmesh.ops.transform(self.bm, matrix=mat, verts=verts)

    def _post(self, verts, mat, bevel=0.0, segments=2,
              smooth=False, smooth_quads_only=False):
        verts = [v for v in verts if v.is_valid]
        edges, faces = set(), set()
        for v in verts:
            edges.update(v.link_edges)
            faces.update(v.link_faces)
        if bevel > 0.0:
            geom = list(verts) + list(edges) + list(faces)
            res = bmesh.ops.bevel(self.bm, geom=geom, offset=bevel,
                                  offset_type='OFFSET', segments=segments,
                                  profile=0.5, affect='EDGES',
                                  clamp_overlap=True)
            faces = set(f for f in faces if f.is_valid)
            faces.update(f for f in res['faces'] if f.is_valid)
        idx = self._mi(mat)
        for f in faces:
            f.material_index = idx
            if smooth_quads_only:
                f.smooth = (len(f.verts) == 4)
            else:
                f.smooth = smooth

    # -- primitives ----------------------------------------------------
    def box(self, size, loc=(0, 0, 0), rot=(0, 0, 0), mat=None,
            bevel=0.0, segments=2):
        res = bmesh.ops.create_cube(self.bm, size=1.0)
        self._place(res['verts'], loc, rot, size)
        self._post(res['verts'], mat, bevel, segments)

    def cyl(self, radius, height, loc=(0, 0, 0), rot=(0, 0, 0), mat=None,
            segments=24, radius_top=None, bevel=0.0):
        r2 = radius if radius_top is None else radius_top
        res = bmesh.ops.create_cone(self.bm, cap_ends=True, cap_tris=False,
                                    segments=segments, radius1=radius,
                                    radius2=r2, depth=height)
        self._place(res['verts'], loc, rot, (1, 1, 1))
        self._post(res['verts'], mat, bevel, 2, smooth_quads_only=True)

    def sphere(self, scale, loc=(0, 0, 0), rot=(0, 0, 0), mat=None,
               u=14, v=8):
        res = bmesh.ops.create_uvsphere(self.bm, u_segments=u, v_segments=v,
                                        radius=1.0)
        self._place(res['verts'], loc, rot, scale)
        self._post(res['verts'], mat, smooth=True)

    # -- output --------------------------------------------------------
    def finish(self, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces)
        me = bpy.data.meshes.new(self.name)
        self.bm.to_mesh(me)
        self.bm.free()
        for mat in self.materials:
            me.materials.append(mat)
        obj = bpy.data.objects.new(self.name, me)
        obj.location = loc
        obj.rotation_euler = rot
        obj.scale = scale
        bpy.context.collection.objects.link(obj)
        return obj


# ----------------------------------------------------------------------
# room dimensions
# ----------------------------------------------------------------------

X0, X1 = -4.0, 4.0          # side walls (inner faces)
YF = -3.2                   # front wall (behind camera)
YP, YPB = 2.86, 3.00        # reception partition, front / back face
YB = 4.40                   # back wall of the reception office
CZ = 2.90                   # ceiling height
T = 0.12                    # wall thickness

WIN_X0, WIN_X1 = -1.40, 0.90    # reception window opening
WIN_Z0, WIN_Z1 = 1.00, 2.05

DOOR_Y0, DOOR_Y1 = -2.60, -1.40  # entrance door in the left wall
DOOR_Z = 2.10


# ----------------------------------------------------------------------
# shell : floor, ceiling, walls, reception partition, baseboards
# ----------------------------------------------------------------------

def build_shell():
    b = Builder("Room")
    span_y = YB - YF + 2 * T
    mid_y = (YF + YB) * 0.5

    # slabs
    b.box((X1 - X0 + 2 * T, span_y, 0.10), (0, mid_y, -0.05), mat=M["floor"])
    b.box((X1 - X0 + 2 * T, span_y, 0.10), (0, mid_y, CZ + 0.05), mat=M["ceiling"])

    # darker inlay border on the waiting-room floor
    b.box((7.4, 5.6, 0.004), (0, -0.25, 0.002), mat=M["floor_dark"])
    b.box((6.9, 5.1, 0.006), (0, -0.25, 0.003), mat=M["floor"])

    # right wall (full)
    b.box((T, span_y, CZ), (X1 + T / 2, mid_y, CZ / 2), mat=M["wall"])
    # front wall
    b.box((X1 - X0 + 2 * T, T, CZ), (0, YF - T / 2, CZ / 2), mat=M["wall"])
    # office back wall
    b.box((X1 - X0 + 2 * T, T, CZ), (0, YB + T / 2, CZ / 2), mat=M["wall"])

    # left wall, split around the entrance doorway
    seg_a = (DOOR_Y0 - (YF - T))
    b.box((T, seg_a, CZ), (X0 - T / 2, (YF - T + DOOR_Y0) / 2, CZ / 2), mat=M["wall"])
    seg_b = ((YB + T) - DOOR_Y1)
    b.box((T, seg_b, CZ), (X0 - T / 2, (DOOR_Y1 + YB + T) / 2, CZ / 2), mat=M["wall"])
    b.box((T, DOOR_Y1 - DOOR_Y0, CZ - DOOR_Z),
          (X0 - T / 2, (DOOR_Y0 + DOOR_Y1) / 2, (DOOR_Z + CZ) / 2), mat=M["wall"])

    # doorframe + glazed entrance door
    for y in (DOOR_Y0, DOOR_Y1):
        b.box((0.16, 0.06, DOOR_Z + 0.06), (X0 - 0.06, y, DOOR_Z / 2), mat=M["trim"])
    b.box((0.16, DOOR_Y1 - DOOR_Y0 + 0.12, 0.06),
          (X0 - 0.06, (DOOR_Y0 + DOOR_Y1) / 2, DOOR_Z + 0.03), mat=M["trim"])
    b.box((0.05, 1.06, 2.02), (X0 - 0.06, -2.02, 1.02), mat=M["steel"])
    b.box((0.02, 0.92, 1.86), (X0 - 0.06, -2.02, 1.03), mat=M["glass"])
    b.cyl(0.022, 0.90, (X0 + 0.02, -2.02, 1.05), (0, 0, 0), M["chrome"], segments=14)

    # daylight card just outside the door
    b.box((0.02, 1.9, 2.3), (X0 - 0.30, -2.02, 1.15), mat=M["daylight"])

    # reception partition wall (accent colour) with window opening
    pw = YPB - YP
    py = (YP + YPB) / 2
    b.box((WIN_X0 - (X0 - T), pw, CZ), ((X0 - T + WIN_X0) / 2, py, CZ / 2), mat=M["accent"])
    b.box(((X1 + T) - WIN_X1, pw, CZ), ((WIN_X1 + X1 + T) / 2, py, CZ / 2), mat=M["accent"])
    b.box((WIN_X1 - WIN_X0, pw, WIN_Z0), ((WIN_X0 + WIN_X1) / 2, py, WIN_Z0 / 2), mat=M["accent"])
    b.box((WIN_X1 - WIN_X0, pw, CZ - WIN_Z1),
          ((WIN_X0 + WIN_X1) / 2, py, (WIN_Z1 + CZ) / 2), mat=M["accent"])

    # window reveal trim
    for z in (WIN_Z0, WIN_Z1):
        b.box((WIN_X1 - WIN_X0 + 0.06, pw + 0.06, 0.035),
              ((WIN_X0 + WIN_X1) / 2, py, z), mat=M["trim"])
    for x in (WIN_X0, WIN_X1):
        b.box((0.05, pw + 0.06, WIN_Z1 - WIN_Z0),
              (x, py, (WIN_Z0 + WIN_Z1) / 2), mat=M["trim"])

    # counter ledge through the opening
    b.box((WIN_X1 - WIN_X0 + 0.24, 0.46, 0.055),
          ((WIN_X0 + WIN_X1) / 2, 2.86, WIN_Z0 - 0.01),
          mat=M["wood"], bevel=0.012)
    for x in (WIN_X0 - 0.02, WIN_X1 + 0.02):
        b.box((0.06, 0.14, 0.16), (x, 2.72, WIN_Z0 - 0.10), mat=M["steel"])

    # sliding glass panes (partly open, gap on the right)
    b.box((1.16, 0.012, 1.00), (-0.83, 2.905, 1.53), mat=M["glass"])
    b.box((0.035, 0.024, 1.00), (-0.24, 2.905, 1.53), mat=M["steel"])
    b.box((1.16, 0.012, 1.00), (-0.30, 2.960, 1.53), mat=M["glass"])
    b.box((0.035, 0.024, 1.00), (0.29, 2.960, 1.53), mat=M["steel"])

    # baseboards
    b.box((X1 - X0, 0.022, 0.11), (0, YF + 0.011, 0.055), mat=M["trim"])
    b.box((0.022, YP - YF, 0.11), (X1 - 0.011, (YF + YP) / 2, 0.055), mat=M["trim"])
    b.box((0.022, DOOR_Y0 - YF, 0.11), (X0 + 0.011, (YF + DOOR_Y0) / 2, 0.055), mat=M["trim"])
    b.box((0.022, YP - DOOR_Y1, 0.11), (X0 + 0.011, (DOOR_Y1 + YP) / 2, 0.055), mat=M["trim"])
    b.box((WIN_X0 - X0, 0.022, 0.11), ((X0 + WIN_X0) / 2, YP - 0.011, 0.055), mat=M["trim"])
    b.box((X1 - WIN_X1, 0.022, 0.11), ((WIN_X1 + X1) / 2, YP - 0.011, 0.055), mat=M["trim"])

    # recessed luminaire housings
    for (lx, ly) in ((-2.10, 0.60), (1.60, 0.60), (-0.30, -2.00), (2.20, -2.20)):
        b.box((1.24, 0.64, 0.06), (lx, ly, CZ - 0.03), mat=M["trim"])
        b.box((1.16, 0.56, 0.03), (lx, ly, CZ - 0.055), mat=M["panel"])
    b.box((0.80, 0.50, 0.04), (0.4, 3.85, CZ - 0.03), mat=M["panel"])

    return b.finish()


# ----------------------------------------------------------------------
# seating
# ----------------------------------------------------------------------

def build_chair(name, loc, rot_z, fabric):
    """Waiting-room chair, modelled facing +Y in local space."""
    b = Builder(name)
    frame = M["chrome"]

    # legs and rails
    for sx in (-1, 1):
        for sy in (-1, 1):
            b.cyl(0.017, 0.44, (sx * 0.205, sy * 0.185, 0.22), mat=frame, segments=12)
    for sy in (-1, 1):
        b.box((0.44, 0.028, 0.028), (0, sy * 0.185, 0.13), mat=frame, bevel=0.006)
    for sx in (-1, 1):
        b.box((0.028, 0.40, 0.028), (sx * 0.205, 0, 0.13), mat=frame, bevel=0.006)

    # seat pan + cushion
    b.box((0.50, 0.48, 0.055), (0, 0.0, 0.455), mat=M["plastic"], bevel=0.018)
    b.box((0.47, 0.45, 0.075), (0, 0.005, 0.505), mat=fabric, bevel=0.032, segments=3)

    # back rest, tilted back a little
    tilt = math.radians(9.0)
    b.box((0.50, 0.075, 0.50), (0, -0.225, 0.79), (tilt, 0, 0),
          mat=M["plastic"], bevel=0.020)
    b.box((0.46, 0.075, 0.46), (0, -0.265, 0.80), (tilt, 0, 0),
          mat=fabric, bevel=0.030, segments=3)
    for sx in (-1, 1):
        b.cyl(0.015, 0.22, (sx * 0.215, -0.205, 0.56), mat=frame, segments=12)

    # armrests
    for sx in (-1, 1):
        b.box((0.055, 0.44, 0.045), (sx * 0.275, -0.01, 0.655),
              mat=M["wood_dark"], bevel=0.018)
        b.cyl(0.014, 0.24, (sx * 0.275, 0.185, 0.545), mat=frame, segments=12)
        b.cyl(0.014, 0.20, (sx * 0.275, -0.205, 0.565), mat=frame, segments=12)

    return b.finish(loc=loc, rot=(0, 0, rot_z))


def build_seating():
    chairs = []
    deg = math.radians

    # row against the front wall, facing into the room (+Y)
    for i in range(5):
        fab = M["fabric_a"] if i % 2 == 0 else M["fabric_b"]
        chairs.append(build_chair("Chair_F%d" % i,
                                  (-2.95 + i * 0.63, -2.78, 0.0), 0.0, fab))

    # row against the right wall, facing -X
    for i in range(5):
        fab = M["fabric_b"] if i % 2 == 0 else M["fabric_a"]
        chairs.append(build_chair("Chair_R%d" % i,
                                  (3.60, -1.30 + i * 0.63, 0.0), deg(90), fab))

    # short row against the left wall, facing +X
    for i in range(3):
        fab = M["fabric_a"] if i % 2 == 0 else M["fabric_b"]
        chairs.append(build_chair("Chair_L%d" % i,
                                  (-3.58, 0.30 + i * 0.63, 0.0), deg(-90), fab))

    # island pair facing the reception window
    for i in range(2):
        chairs.append(build_chair("Chair_M%d" % i,
                                  (-1.55 + i * 0.63, 0.95, 0.0), deg(180),
                                  M["fabric_b"] if i else M["fabric_a"]))
    return chairs


# ----------------------------------------------------------------------
# magazine table
# ----------------------------------------------------------------------

def build_magazine_table(loc, rot_z=0.0):
    b = Builder("MagazineTable")
    b.box((1.12, 0.64, 0.045), (0, 0, 0.415), mat=M["wood"], bevel=0.014, segments=3)
    b.box((1.00, 0.54, 0.028), (0, 0, 0.155), mat=M["wood"], bevel=0.008)
    for sx in (-1, 1):
        for sy in (-1, 1):
            b.cyl(0.023, 0.415, (sx * 0.505, sy * 0.275, 0.2075),
                  mat=M["steel"], segments=12)

    # magazines fanned out on the top
    covers = [M["mag_a"], M["mag_b"], M["mag_c"], M["mag_d"]]
    z = 0.4385
    for i in range(5):
        ang = math.radians(random.uniform(-38, 38))
        px = random.uniform(-0.34, 0.34)
        py = random.uniform(-0.14, 0.14)
        b.box((0.215, 0.285, 0.0075), (px, py, z + 0.004), (0, 0, ang),
              mat=covers[i % len(covers)])
        b.box((0.205, 0.275, 0.0065), (px, py, z + 0.0035), (0, 0, ang),
              mat=M["paper"])
        z += 0.009

    # a small stack on the lower shelf
    for i in range(3):
        b.box((0.215, 0.285, 0.008), (0.30, 0.0, 0.176 + i * 0.009),
              (0, 0, math.radians(random.uniform(-8, 8))),
              mat=covers[(i + 1) % len(covers)])

    # tissue box, because it is that kind of room
    b.box((0.13, 0.13, 0.11), (-0.42, 0.16, 0.493), mat=M["mag_b"], bevel=0.01)
    b.box((0.05, 0.05, 0.05), (-0.42, 0.16, 0.565), mat=M["paper"], bevel=0.012)

    return b.finish(loc=loc, rot=(0, 0, rot_z))


# ----------------------------------------------------------------------
# planters
# ----------------------------------------------------------------------

def build_planter(name, loc, pot_mat, height=0.42, radius=0.24,
                  leaf_count=18, plant_height=0.95, tall=False):
    b = Builder(name)
    b.cyl(radius * 0.78, height, (0, 0, height / 2), mat=pot_mat,
          segments=32, radius_top=radius)
    b.cyl(radius + 0.018, 0.05, (0, 0, height - 0.02), mat=pot_mat, segments=32)
    b.cyl(radius - 0.01, 0.03, (0, 0, height - 0.015), mat=M["soil"], segments=32)

    # a few stems with foliage
    stems = 3 if not tall else 4
    for s in range(stems):
        base_a = random.uniform(0, math.tau)
        lean = random.uniform(0.04, 0.13)
        top = plant_height * random.uniform(0.75, 1.0)
        tx = math.cos(base_a) * lean * top
        ty = math.sin(base_a) * lean * top
        b.cyl(0.016, top, (tx * 0.5, ty * 0.5, height + top / 2),
              (math.atan2(ty, top) * 0.9, -math.atan2(tx, top) * 0.9, 0),
              mat=M["stem"], segments=8)

    for i in range(leaf_count):
        a = random.uniform(0, math.tau)
        h = height + plant_height * random.uniform(0.25, 1.0)
        r = random.uniform(0.06, 0.20)
        pitch = math.radians(random.uniform(-55, -12))
        lm = M["leaf"] if i % 3 else M["leaf2"]
        size = random.uniform(0.85, 1.25)
        b.sphere((0.058 * size, 0.21 * size, 0.010),
                 (math.cos(a) * r, math.sin(a) * r, h),
                 (pitch, 0, a - math.pi / 2), mat=lm)
        # blade tip, slightly drooping
        b.sphere((0.032 * size, 0.11 * size, 0.008),
                 (math.cos(a) * (r + 0.20 * size), math.sin(a) * (r + 0.20 * size),
                  h - 0.10 * size),
                 (math.radians(-70), 0, a - math.pi / 2), mat=lm)

    return b.finish(loc=loc)


# ----------------------------------------------------------------------
# reception office props (seen through the window)
# ----------------------------------------------------------------------

def build_office():
    b = Builder("ReceptionOffice")
    # work counter behind the window
    b.box((2.60, 0.62, 0.05), (-0.25, 3.42, 0.755), mat=M["wood"], bevel=0.012)
    b.box((2.50, 0.05, 0.70), (-0.25, 3.70, 0.37), mat=M["plastic"])
    for sx in (-1, 1):
        b.box((0.05, 0.58, 0.72), (-0.25 + sx * 1.24, 3.42, 0.37), mat=M["plastic"])

    # monitor + keyboard
    b.box((0.16, 0.16, 0.02), (-0.55, 3.55, 0.79), mat=M["black"], bevel=0.006)
    b.cyl(0.028, 0.22, (-0.55, 3.55, 0.90), mat=M["black"], segments=12)
    b.box((0.56, 0.045, 0.34), (-0.55, 3.56, 1.19), (math.radians(-6), 0, 0),
          mat=M["black"], bevel=0.008)
    b.box((0.52, 0.012, 0.30), (-0.55, 3.535, 1.19), (math.radians(-6), 0, 0),
          mat=M["screen"])
    b.box((0.40, 0.15, 0.018), (-0.52, 3.20, 0.79), mat=M["black"], bevel=0.004)

    # shelf of binders on the office back wall
    b.box((2.20, 0.30, 0.04), (0.0, 4.20, 1.70), mat=M["wood"])
    cols = [M["mag_a"], M["mag_b"], M["mag_c"], M["mag_d"], M["accent"]]
    x = -1.00
    for i in range(14):
        w = random.uniform(0.055, 0.09)
        b.box((w, 0.24, 0.30), (x + w / 2, 4.20, 1.87),
              (0, 0, math.radians(random.uniform(-2, 2))), mat=cols[i % 5])
        x += w + 0.006

    # office task chair (a suggestion of one)
    b.cyl(0.03, 0.34, (-0.55, 2.55, 0.17), mat=M["black"], segments=10)
    b.cyl(0.26, 0.04, (-0.55, 2.55, 0.03), mat=M["black"], segments=18)
    b.box((0.44, 0.42, 0.07), (-0.55, 2.55, 0.37), mat=M["fabric_a"], bevel=0.02)
    b.box((0.42, 0.07, 0.42), (-0.55, 2.35, 0.63), (math.radians(-8), 0, 0),
          mat=M["fabric_a"], bevel=0.02)
    return b.finish()


# ----------------------------------------------------------------------
# small props : counter items, wall art, clock, bin, doormat, cooler
# ----------------------------------------------------------------------

def build_props():
    b = Builder("Props")

    # sign-in clipboard and pen on the counter ledge
    b.box((0.24, 0.32, 0.012), (-1.02, 2.80, 1.028), (0, 0, math.radians(-11)),
          mat=M["wood_dark"], bevel=0.004)
    b.box((0.21, 0.29, 0.006), (-1.02, 2.79, 1.038), (0, 0, math.radians(-11)),
          mat=M["paper"])
    b.cyl(0.006, 0.14, (-0.80, 2.76, 1.040), (0, math.radians(90), math.radians(24)),
          mat=M["black"], segments=8)

    # leaflet stand and card holder
    b.box((0.16, 0.11, 0.19), (0.55, 2.82, 1.125), (math.radians(12), 0, 0),
          mat=M["glass"])
    b.box((0.14, 0.02, 0.20), (0.55, 2.81, 1.135), (math.radians(12), 0, 0),
          mat=M["mag_c"])
    b.box((0.10, 0.07, 0.05), (0.20, 2.80, 1.055), mat=M["steel"], bevel=0.006)

    # wall clock on the partition
    b.cyl(0.145, 0.045, (-2.55, 2.835, 2.18), (math.radians(90), 0, 0),
          mat=M["trim"], segments=32)
    b.cyl(0.128, 0.012, (-2.55, 2.808, 2.18), (math.radians(90), 0, 0),
          mat=M["paper"], segments=32)
    b.box((0.012, 0.008, 0.095), (-2.55, 2.800, 2.222), (0, math.radians(18), 0),
          mat=M["black"])
    b.box((0.010, 0.008, 0.065), (-2.55, 2.800, 2.155), (0, math.radians(-105), 0),
          mat=M["black"])

    # framed prints on the right wall
    for i, (yy, art) in enumerate(((-0.55, M["art_a"]), (0.95, M["art_b"]))):
        b.box((0.05, 0.86, 0.62), (3.965, yy, 1.72), mat=M["wood_dark"], bevel=0.012)
        b.box((0.02, 0.76, 0.52), (3.938, yy, 1.72), mat=art)
    # print on the front wall
    b.box((0.90, 0.05, 0.62), (0.85, -3.165, 1.75), mat=M["wood_dark"], bevel=0.012)
    b.box((0.80, 0.02, 0.52), (0.85, -3.138, 1.75), mat=M["art_a"])

    # waste bin near the reception window
    b.cyl(0.135, 0.44, (1.55, 2.58, 0.22), mat=M["steel"], segments=24,
          radius_top=0.165)
    b.cyl(0.172, 0.03, (1.55, 2.58, 0.435), mat=M["black"], segments=24)

    # hand sanitiser column by the door side of the partition
    b.box((0.14, 0.12, 0.30), (-3.05, 2.79, 1.20), mat=M["plastic"], bevel=0.012)
    b.box((0.09, 0.06, 0.05), (-3.05, 2.70, 1.06), mat=M["black"], bevel=0.01)

    # water cooler in the corner
    b.box((0.34, 0.34, 0.92), (3.62, 2.42, 0.46), mat=M["plastic"], bevel=0.02)
    b.box((0.20, 0.06, 0.22), (3.62, 2.24, 0.72), mat=M["black"], bevel=0.01)
    b.cyl(0.145, 0.42, (3.62, 2.42, 1.14), mat=M["glass"], segments=24)
    b.cyl(0.075, 0.10, (3.62, 2.42, 1.38), mat=M["glass"], segments=20, radius_top=0.13)

    # doormat inside the entrance
    b.box((0.95, 1.35, 0.012), (-3.45, -2.02, 0.006), mat=M["black"], bevel=0.004)

    # coat hooks rail near the door
    b.box((0.04, 0.70, 0.09), (-3.955, -0.75, 1.72), mat=M["wood_dark"])
    for i in range(3):
        b.cyl(0.012, 0.10, (-3.925, -1.00 + i * 0.25, 1.70),
              (0, math.radians(90), 0), mat=M["chrome"], segments=10)

    return b.finish()


# ----------------------------------------------------------------------
# lighting
# ----------------------------------------------------------------------

def add_area_light(name, loc, size, energy, color=(1.0, 0.96, 0.90),
                   rot=(0, 0, 0), size_y=None):
    data = bpy.data.lights.new(name, type='AREA')
    if size_y is None:
        data.shape = 'SQUARE'
        data.size = size
    else:
        data.shape = 'RECTANGLE'
        data.size = size
        data.size_y = size_y
    data.energy = energy
    data.color = color
    obj = bpy.data.objects.new(name, data)
    obj.location = loc
    obj.rotation_euler = rot
    bpy.context.collection.objects.link(obj)
    return obj


def build_lighting():
    down = (math.pi, 0, 0)
    for i, (lx, ly) in enumerate(((-2.10, 0.60), (1.60, 0.60),
                                  (-0.30, -2.00), (2.20, -2.20))):
        add_area_light("CeilingPanel_%d" % i, (lx, ly, CZ - 0.08),
                       1.15, 90.0, rot=down, size_y=0.55)

    add_area_light("OfficePanel", (0.40, 3.85, CZ - 0.08), 0.75, 45.0,
                   color=(0.98, 0.98, 1.0), rot=down, size_y=0.45)

    # daylight spilling in through the glazed entrance door
    add_area_light("DoorDaylight", (X0 - 0.22, -2.02, 1.20), 1.05, 260.0,
                   color=(0.72, 0.83, 1.0),
                   rot=(0, math.radians(90), 0), size_y=1.9)

    # gentle fill so the seating never goes fully black
    add_area_light("Fill", (1.60, -2.40, 2.10), 3.2, 40.0,
                   color=(0.95, 0.95, 1.0),
                   rot=(math.radians(62), 0, math.radians(-135)))


# ----------------------------------------------------------------------
# signage text
# ----------------------------------------------------------------------

def build_sign():
    curve = bpy.data.curves.new("ReceptionTextData", type='FONT')
    curve.body = "RECEPTION"
    curve.align_x = 'CENTER'
    curve.align_y = 'CENTER'
    curve.size = 0.135
    curve.space_character = 1.25
    curve.extrude = 0.004
    obj = bpy.data.objects.new("ReceptionSign", curve)
    obj.location = (-0.25, 2.845, 2.35)
    obj.rotation_euler = (math.pi / 2, 0, 0)
    obj.data.materials.append(M["trim"])
    bpy.context.collection.objects.link(obj)

    curve2 = bpy.data.curves.new("SignInTextData", type='FONT')
    curve2.body = "PLEASE SIGN IN"
    curve2.align_x = 'CENTER'
    curve2.align_y = 'CENTER'
    curve2.size = 0.055
    curve2.extrude = 0.002
    obj2 = bpy.data.objects.new("SignInPlate", curve2)
    obj2.location = (-0.25, 2.845, 0.78)
    obj2.rotation_euler = (math.pi / 2, 0, 0)
    obj2.data.materials.append(M["trim"])
    bpy.context.collection.objects.link(obj2)
    return obj, obj2


# ----------------------------------------------------------------------
# camera
# ----------------------------------------------------------------------

def build_camera(loc, target, lens=24.0):
    data = bpy.data.cameras.new("Camera")
    data.lens = lens
    data.clip_start = 0.05
    data.clip_end = 120.0
    data.dof.use_dof = True
    data.dof.focus_distance = (Vector(target) - Vector(loc)).length
    data.dof.aperture_fstop = 5.6
    cam = bpy.data.objects.new("Camera", data)
    cam.location = loc
    direction = Vector(target) - Vector(loc)
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(cam)
    scene.camera = cam
    return cam


# ----------------------------------------------------------------------
# assemble
# ----------------------------------------------------------------------

build_shell()
build_office()
build_seating()
build_magazine_table((-1.25, -1.85, 0.0), rot_z=math.radians(4))
build_magazine_table((2.55, 0.15, 0.0), rot_z=math.radians(90))

build_planter("Planter_Corner_R", (3.45, 1.55, 0.0), M["pot_b"],
              leaf_count=22, plant_height=1.15, tall=True)
build_planter("Planter_Corner_L", (-3.50, 2.35, 0.0), M["pot_a"],
              leaf_count=18, plant_height=0.95)
build_planter("Planter_Window", (1.05, 2.55, 0.0), M["pot_a"],
              height=0.34, radius=0.19, leaf_count=13, plant_height=0.62)
build_planter("Planter_Door", (-3.45, -0.35, 0.0), M["pot_b"],
              height=0.38, radius=0.21, leaf_count=16, plant_height=0.80)

build_props()
build_sign()
build_lighting()
build_camera((3.30, -2.80, 1.66), (-0.65, 1.95, 1.16), lens=24.0)

print("Dentist waiting room built: %d objects" % len(bpy.data.objects))
