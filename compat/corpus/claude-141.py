"""Concrete pedestrian underpass -- Blender 4.5 LTS.

Builds, from factory startup and with no external assets:
  * a cast-in-place concrete box tunnel (16 m covered length, 4 m clear width)
  * open stair trenches at both ends: two 10-riser flights and a mid landing
  * retaining walls, portal heads, copings, pilasters and a dado band
  * recessed side drainage channels + transverse trench drains with gratings
  * wall-mounted raking handrails and grade-level guardrails with balusters
  * recessed ceiling luminaires and wall bulkheads (emissive geometry + lamps)
  * surrounding paving, sun / world lighting and a framed camera

Scene construction only -- nothing is rendered or saved.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix

# --------------------------------------------------------------------------
# parameters
# --------------------------------------------------------------------------
HW = 2.00                  # interior half width
WT = 0.40                  # wall thickness
OW = HW + WT               # outer half width (2.40)
FZ = -3.60                 # finished floor level
CZ = -0.85                 # interior ceiling level
RT = 0.45                  # roof slab thickness
ZBOT = -4.15               # underside of the structure
TUNX = 8.00                # covered half length

S0 = 9.50                  # x of the first riser
TREAD = 0.32
RISER = 0.18
NSTEP = 10                 # risers per flight (2 x 10 x 0.18 = 3.60 m)
LAND = 1.40                # mid landing length
F1E = S0 + NSTEP * TREAD           # 12.70  top of flight 1
LE = F1E + LAND                    # 14.10  end of landing
TOPX = LE + NSTEP * TREAD          # 17.30  grade level

CH0, CH1 = 1.62, 1.88      # longitudinal drainage channel edges (|y|)
CHZ = FZ - 0.22            # channel invert
DRX = 9.05                 # end of the longitudinal channels
TDR0, TDR1 = 9.05, 9.35    # transverse trench drain

COPE_TOP = 0.22            # top of the parapet coping
GRADE = 0.0


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.length_unit = 'METERS'
    try:
        scene.render.engine = 'CYCLES'
        scene.cycles.samples = 128
        scene.cycles.preview_samples = 32
    except (AttributeError, TypeError):
        pass
    try:
        scene.view_settings.view_transform = 'AgX'
        scene.view_settings.look = 'AgX - Medium Contrast'
    except TypeError:
        pass
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080


def new_collection(name):
    coll = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(coll)
    return coll


class Mesher:
    """Accumulates primitives into a single bmesh, then emits one object."""

    def __init__(self):
        self.bm = bmesh.new()

    # -- primitives --------------------------------------------------------
    def box(self, x0, x1, y0, y1, z0, z1):
        """Axis aligned box given by its bounds."""
        mat = (Matrix.Translation(((x0 + x1) * 0.5,
                                   (y0 + y1) * 0.5,
                                   (z0 + z1) * 0.5)) @
               Matrix.Diagonal((x1 - x0, y1 - y0, z1 - z0, 1.0)))
        try:
            bmesh.ops.create_cube(self.bm, size=1.0, matrix=mat, calc_uvs=True)
        except TypeError:
            bmesh.ops.create_cube(self.bm, size=1.0, matrix=mat)

    def cyl(self, p0, p1, radius, segments=16):
        """Capped cylinder between two points."""
        p0, p1 = Vector(p0), Vector(p1)
        direction = p1 - p0
        length = direction.length
        if length < 1.0e-6:
            return
        rot = direction.to_track_quat('Z', 'Y').to_matrix().to_4x4()
        mat = Matrix.Translation((p0 + p1) * 0.5) @ rot
        kw = dict(cap_ends=True, cap_tris=False, segments=segments,
                  depth=length, matrix=mat)
        try:
            bmesh.ops.create_cone(self.bm, radius1=radius, radius2=radius, **kw)
        except TypeError:
            bmesh.ops.create_cone(self.bm, diameter1=radius, diameter2=radius,
                                  **kw)

    def prism_xz(self, points, y0, y1):
        """Closed polygon in the XZ plane extruded along Y."""
        verts = [self.bm.verts.new((x, y0, z)) for (x, z) in points]
        face = self.bm.faces.new(verts)
        ret = bmesh.ops.extrude_face_region(self.bm, geom=[face])
        moved = [e for e in ret["geom"] if isinstance(e, bmesh.types.BMVert)]
        bmesh.ops.translate(self.bm, verts=moved, vec=(0.0, y1 - y0, 0.0))
        self.bm.normal_update()

    # -- output ------------------------------------------------------------
    def to_object(self, name, material, collection):
        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces)
        me = bpy.data.meshes.new(name)
        self.bm.to_mesh(me)
        self.bm.free()
        self.bm = None
        if material is not None:
            me.materials.append(material)
        ob = bpy.data.objects.new(name, me)
        collection.objects.link(ob)
        return ob


# --------------------------------------------------------------------------
# materials
# --------------------------------------------------------------------------
def _principled(mat):
    return mat.node_tree.nodes["Principled BSDF"]


def _set(node, key, value):
    if key in node.inputs:
        node.inputs[key].default_value = value


def concrete_material(name, base, roughness=0.82, noise_scale=14.0,
                      bump=0.30, streak=0.0):
    """Board-marked looking concrete: noise driven colour break-up + bump."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    bsdf = _principled(mat)
    bsdf.location = (200, 0)

    coord = nodes.new("ShaderNodeTexCoord")
    coord.location = (-1000, 0)
    mapping = nodes.new("ShaderNodeMapping")
    mapping.location = (-820, 0)
    if streak > 0.0:
        mapping.inputs["Scale"].default_value = (1.0, 1.0, 1.0 / max(streak, 0.05))

    big = nodes.new("ShaderNodeTexNoise")
    big.location = (-620, 150)
    big.inputs["Scale"].default_value = noise_scale * 0.18
    big.inputs["Detail"].default_value = 4.0
    _set(big, "Roughness", 0.65)

    fine = nodes.new("ShaderNodeTexNoise")
    fine.location = (-620, -150)
    fine.inputs["Scale"].default_value = noise_scale * 4.0
    fine.inputs["Detail"].default_value = 8.0
    _set(fine, "Roughness", 0.75)

    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.location = (-380, 150)
    e0 = ramp.color_ramp.elements[0]
    e1 = ramp.color_ramp.elements[1]
    e0.position = 0.30
    e0.color = (base[0] * 0.72, base[1] * 0.72, base[2] * 0.74, 1.0)
    e1.position = 0.72
    e1.color = (min(base[0] * 1.14, 1.0), min(base[1] * 1.14, 1.0),
                min(base[2] * 1.12, 1.0), 1.0)

    mix = nodes.new("ShaderNodeMixRGB")
    mix.location = (-160, 60)
    mix.blend_type = 'OVERLAY'
    mix.inputs["Fac"].default_value = 0.28
    mix.inputs[2].default_value = (0.55, 0.55, 0.55, 1.0)

    bump_node = nodes.new("ShaderNodeBump")
    bump_node.location = (-160, -220)
    bump_node.inputs["Strength"].default_value = bump
    bump_node.inputs["Distance"].default_value = 0.02

    rough = nodes.new("ShaderNodeMapRange")
    rough.location = (-160, -420)
    rough.inputs["To Min"].default_value = max(roughness - 0.12, 0.05)
    rough.inputs["To Max"].default_value = min(roughness + 0.10, 1.0)

    links.new(coord.outputs["Object"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], big.inputs["Vector"])
    links.new(mapping.outputs["Vector"], fine.inputs["Vector"])
    links.new(big.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], mix.inputs[1])
    links.new(fine.outputs["Fac"], mix.inputs["Fac"])
    links.new(mix.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(fine.outputs["Fac"], bump_node.inputs["Height"])
    links.new(bump_node.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(fine.outputs["Fac"], rough.inputs["Value"])
    links.new(rough.outputs["Result"], bsdf.inputs["Roughness"])

    _set(bsdf, "Specular IOR Level", 0.35)
    return mat


def simple_material(name, base, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = _principled(mat)
    _set(bsdf, "Base Color", (base[0], base[1], base[2], 1.0))
    _set(bsdf, "Roughness", roughness)
    _set(bsdf, "Metallic", metallic)
    return mat


def metal_material(name, base, roughness=0.35, metallic=1.0, noise=8.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = _principled(mat)
    _set(bsdf, "Base Color", (base[0], base[1], base[2], 1.0))
    _set(bsdf, "Metallic", metallic)

    coord = nt.nodes.new("ShaderNodeTexCoord")
    coord.location = (-700, -200)
    tex = nt.nodes.new("ShaderNodeTexNoise")
    tex.location = (-500, -200)
    tex.inputs["Scale"].default_value = noise
    tex.inputs["Detail"].default_value = 6.0
    rng = nt.nodes.new("ShaderNodeMapRange")
    rng.location = (-300, -200)
    rng.inputs["To Min"].default_value = max(roughness - 0.10, 0.05)
    rng.inputs["To Max"].default_value = min(roughness + 0.18, 1.0)
    bump = nt.nodes.new("ShaderNodeBump")
    bump.location = (-300, -450)
    bump.inputs["Strength"].default_value = 0.08

    nt.links.new(coord.outputs["Object"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Fac"], rng.inputs["Value"])
    nt.links.new(rng.outputs["Result"], bsdf.inputs["Roughness"])
    nt.links.new(tex.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def emission_material(name, color, strength):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    for node in list(nt.nodes):
        if node.type != 'OUTPUT_MATERIAL':
            nt.nodes.remove(node)
    out = nt.nodes["Material Output"]
    emit = nt.nodes.new("ShaderNodeEmission")
    emit.location = (-220, 0)
    emit.inputs["Color"].default_value = (color[0], color[1], color[2], 1.0)
    emit.inputs["Strength"].default_value = strength
    nt.links.new(emit.outputs["Emission"], out.inputs["Surface"])
    return mat


# --------------------------------------------------------------------------
# geometry: profiles and sub-assemblies
# --------------------------------------------------------------------------
def stair_profile(sign):
    """Return (profile points, nosing list) for the staircase at +/- x."""
    pts = [(S0, ZBOT), (S0, FZ)]
    nosings = []
    x, z = S0, FZ
    for _ in range(NSTEP):                 # flight 1
        z += RISER
        pts.append((x, z))
        x += TREAD
        pts.append((x, z))
        nosings.append((x, z))
    x += LAND                              # mid landing
    pts.append((x, z))
    for _ in range(NSTEP):                 # flight 2
        z += RISER
        pts.append((x, z))
        x += TREAD
        pts.append((x, z))
        nosings.append((x, z))
    pts.append((x, ZBOT))

    if sign < 0:
        pts = [(-px, pz) for (px, pz) in reversed(pts)]
        nosings = [(-nx, nz) for (nx, nz) in nosings]
    return pts, nosings


def rake_z(x):
    """Walking surface level of the stair at absolute x (>= 0 side)."""
    x = abs(x)
    if x <= S0:
        return FZ
    if x >= TOPX:
        return GRADE
    if x <= F1E:
        n = min(NSTEP, int((x - S0) / TREAD) + 1)
        return FZ + RISER * n
    if x <= LE:
        return FZ + RISER * NSTEP
    n = min(NSTEP, int((x - LE) / TREAD) + 1)
    return FZ + RISER * (NSTEP + n)


def guardrail(m, p0, p1, height=1.10, post_sp=1.55, bal_sp=0.155):
    """Post-and-rail guardrail with vertical baluster infill."""
    p0, p1 = Vector(p0), Vector(p1)
    span = p1 - p0
    length = span.length
    if length < 0.2:
        return
    u = span / length

    nposts = max(2, int(round(length / post_sp)) + 1)
    for i in range(nposts):
        base = p0 + u * (length * i / (nposts - 1))
        m.cyl(base, base + Vector((0.0, 0.0, height)), 0.032, 12)
        m.box(base.x - 0.055, base.x + 0.055,
              base.y - 0.055, base.y + 0.055,
              base.z - 0.005, base.z + 0.018)          # base plate

    for h, r in ((height, 0.026), (height * 0.52, 0.020), (0.075, 0.016)):
        m.cyl(p0 + Vector((0.0, 0.0, h)), p1 + Vector((0.0, 0.0, h)), r, 12)

    nbal = max(1, int(length / bal_sp))
    for i in range(1, nbal):
        base = p0 + u * (length * i / nbal)
        m.cyl(base + Vector((0.0, 0.0, 0.075)),
              base + Vector((0.0, 0.0, height - 0.02)), 0.009, 6)


def handrail(m, p0, p1, wall_y, radius=0.026):
    """Raking wall-mounted handrail with brackets back to the wall face."""
    p0, p1 = Vector(p0), Vector(p1)
    m.cyl(p0, p1, radius, 12)
    length = (p1 - p0).length
    n = max(2, int(round(length / 1.35)) + 1)
    for i in range(n):
        p = p0.lerp(p1, i / (n - 1))
        m.cyl(p, Vector((p.x, wall_y, p.z)), 0.013, 8)
        m.box(p.x - 0.045, p.x + 0.045,
              min(wall_y, p.y) - 0.012, max(wall_y, p.y) + 0.012,
              p.z - 0.045, p.z + 0.045) if False else None


# --------------------------------------------------------------------------
# build
# --------------------------------------------------------------------------
def build():
    reset_scene()

    col_struct = new_collection("Structure")
    col_metal = new_collection("Metalwork")
    col_light = new_collection("Lighting")
    col_env = new_collection("Environment")

    mat_concrete = concrete_material("Concrete_Cast", (0.455, 0.450, 0.435),
                                     roughness=0.84, noise_scale=13.0,
                                     bump=0.32)
    mat_concrete_dark = concrete_material("Concrete_Dado", (0.255, 0.262, 0.275),
                                          roughness=0.55, noise_scale=22.0,
                                          bump=0.18)
    mat_paving = concrete_material("Paving_Asphalt", (0.115, 0.115, 0.120),
                                   roughness=0.90, noise_scale=26.0,
                                   bump=0.45)
    mat_steel = metal_material("Steel_Galvanised", (0.560, 0.575, 0.590),
                               roughness=0.33, metallic=1.0, noise=9.0)
    mat_grate = metal_material("Steel_Grating", (0.400, 0.405, 0.415),
                               roughness=0.52, metallic=1.0, noise=16.0)
    mat_housing = simple_material("Luminaire_Housing", (0.055, 0.058, 0.062),
                                  roughness=0.35, metallic=0.85)
    mat_lamp = emission_material("Luminaire_Lens", (1.00, 0.955, 0.870), 14.0)
    mat_nosing = simple_material("Nosing_Safety", (0.720, 0.520, 0.045),
                                 roughness=0.45)

    # ---------------------------------------------------------------- shell
    s = Mesher()

    # structural base slab under the covered section
    s.box(-DRX - 0.55, DRX + 0.55, -OW + 0.35, OW - 0.35, ZBOT, CHZ)

    # walking slab and channel-side strip (both sides), leaving the channels
    s.box(-DRX, DRX, -CH0, CH0, CHZ, FZ)
    for sy in (1.0, -1.0):
        s.box(-DRX, DRX, sy * CH1, sy * (HW + 0.05), CHZ, FZ)

    # short slabs between the transverse drains and the first riser
    for sx in (1.0, -1.0):
        s.box(sx * TDR1, sx * (S0 + 0.10), -(HW + 0.05), HW + 0.05, CHZ, FZ)

    # tunnel side walls
    for sy in (1.0, -1.0):
        y0, y1 = sorted((sy * HW, sy * OW))
        s.box(-TUNX, TUNX, y0, y1, ZBOT, CZ)

    # roof slab and earth-cover fill over the tunnel
    s.box(-TUNX, TUNX, -OW, OW, CZ, CZ + RT)
    s.box(-TUNX, TUNX, -OW, OW, CZ + RT, GRADE)

    # portal head beams at both mouths
    for sx in (1.0, -1.0):
        x0, x1 = sorted((sx * (TUNX - 0.10), sx * (TUNX + 0.40)))
        s.box(x0, x1, -OW, OW, CZ, 0.10)
        s.box(x0 - 0.06, x1 + 0.06, -OW - 0.05, OW + 0.05, 0.10, COPE_TOP)

    # trench retaining walls + copings
    for sx in (1.0, -1.0):
        wx0, wx1 = sorted((sx * TUNX, sx * TOPX))
        for sy in (1.0, -1.0):
            y0, y1 = sorted((sy * HW, sy * OW))
            s.box(wx0, wx1, y0, y1, ZBOT, 0.10)
            c0, c1 = sorted((sy * (HW - 0.05), sy * (OW + 0.05)))
            s.box(wx0, wx1, c0, c1, 0.10, COPE_TOP)

    # staircases
    for sx in (1.0, -1.0):
        pts, _ = stair_profile(sx)
        s.prism_xz(pts, -(HW + 0.06), HW + 0.06)

    # wall pilasters inside the tunnel
    for px in [-7.0, -5.0, -3.0, -1.0, 1.0, 3.0, 5.0, 7.0]:
        for sy in (1.0, -1.0):
            y0, y1 = sorted((sy * (HW - 0.10), sy * (HW + 0.02)))
            s.box(px - 0.16, px + 0.16, y0, y1, FZ, CZ)

    # kerb upstand alongside each channel, keeps water off the walkway
    for sy in (1.0, -1.0):
        y0, y1 = sorted((sy * (CH1 - 0.02), sy * (CH1 + 0.10)))
        s.box(-DRX, DRX, y0, y1, FZ, FZ + 0.05)

    s.to_object("Underpass_Concrete", mat_concrete, col_struct)

    # ------------------------------------------------------------ dado band
    d = Mesher()
    for sy in (1.0, -1.0):
        y0, y1 = sorted((sy * (HW - 0.035), sy * (HW + 0.005)))
        d.box(-TUNX + 0.02, TUNX - 0.02, y0, y1, FZ + 0.06, FZ + 1.20)
        # chamfered cap on the band
        d.box(-TUNX + 0.02, TUNX - 0.02, y0, y1, FZ + 1.20, FZ + 1.24)
    d.to_object("Wall_Dado_Band", mat_concrete_dark, col_struct)

    # ------------------------------------------------------------- gratings
    g = Mesher()
    bar_top = FZ - 0.006
    bar_bot = FZ - 0.052
    for sy in (1.0, -1.0):
        y0, y1 = sorted((sy * (CH0 - 0.02), sy * (CH1 + 0.02)))
        # channel frame angles
        g.box(-DRX, DRX, y0, y0 + 0.035, bar_bot - 0.015, bar_top)
        g.box(-DRX, DRX, y1 - 0.035, y1, bar_bot - 0.015, bar_top)
        # transverse bars
        x = -DRX + 0.09
        while x < DRX - 0.05:
            g.box(x, x + 0.050, y0, y1, bar_bot, bar_top)
            x += 0.160
        # longitudinal tie rods
        for ty in (0.35, 0.65):
            yy = y0 + (y1 - y0) * ty
            g.cyl((-DRX, yy, bar_bot + 0.012), (DRX, yy, bar_bot + 0.012),
                  0.006, 6)

    # transverse trench drains at the foot of each stair
    for sx in (1.0, -1.0):
        x0, x1 = sorted((sx * (TDR0 - 0.02), sx * (TDR1 + 0.02)))
        g.box(x0, x0 + 0.035, -(HW + 0.02), HW + 0.02, bar_bot - 0.015, bar_top)
        g.box(x1 - 0.035, x1, -(HW + 0.02), HW + 0.02, bar_bot - 0.015, bar_top)
        y = -HW + 0.05
        while y < HW - 0.05:
            g.box(x0, x1, y, y + 0.050, bar_bot, bar_top)
            y += 0.160
    g.to_object("Drainage_Gratings", mat_grate, col_metal)

    # ------------------------------------------------------- stair nosings
    n = Mesher()
    for sx in (1.0, -1.0):
        _, nosings = stair_profile(sx)
        for (nx, nz) in nosings:
            x0, x1 = sorted((nx - sx * 0.02, nx - sx * 0.11))
            n.box(x0, x1, -(HW - 0.12), HW - 0.12, nz - 0.020, nz + 0.005)
    n.to_object("Stair_Nosings", mat_nosing, col_struct)

    # ------------------------------------------------------------ metalwork
    r = Mesher()
    rail_z = COPE_TOP
    for sx in (1.0, -1.0):
        xa, xb = sx * (TUNX + 0.32), sx * TOPX
        for sy in (1.0, -1.0):
            ry = sy * (OW - 0.02)
            guardrail(r, (xa, ry, rail_z), (xb, ry, rail_z))
        # return across the portal head
        xc = sx * (TUNX + 0.15)
        guardrail(r, (xc, -(OW - 0.02), rail_z), (xc, OW - 0.02, rail_z))

    # raking wall handrails, 0.95 m above the nosing line
    hh = 0.95
    for sx in (1.0, -1.0):
        for sy in (1.0, -1.0):
            ry = sy * (HW - 0.15)
            wall_y = sy * (HW - 0.02)
            runs = [((S0 - 0.30), FZ + hh, F1E, FZ + NSTEP * RISER + hh),
                    (F1E, FZ + NSTEP * RISER + hh, LE, FZ + NSTEP * RISER + hh),
                    (LE, FZ + NSTEP * RISER + hh, TOPX + 0.30, GRADE + hh)]
            for (ax, az, bx, bz) in runs:
                handrail(r,
                         (sx * ax, ry, az),
                         (sx * bx, ry, bz),
                         wall_y)
            # newel drops at both ends of the run
            r.cyl((sx * (S0 - 0.30), ry, FZ + hh),
                  (sx * (S0 - 0.30), ry, FZ + hh - 0.28), 0.026, 12)
            r.cyl((sx * (TOPX + 0.30), ry, GRADE + hh),
                  (sx * (TOPX + 0.30), ry, GRADE + hh - 0.28), 0.026, 12)
    r.to_object("Railings_Steel", mat_steel, col_metal)

    # -------------------------------------------------------- luminaires
    housings = Mesher()
    lenses = Mesher()

    ceiling_x = [-6.0, -3.0, 0.0, 3.0, 6.0]
    for cx in ceiling_x:
        housings.box(cx - 0.72, cx + 0.72, -0.18, 0.18, CZ - 0.025, CZ + 0.11)
        lenses.box(cx - 0.66, cx + 0.66, -0.135, 0.135, CZ - 0.035, CZ - 0.018)

    bulkheads = []
    for sx in (1.0, -1.0):
        for bx in (10.20, 12.60):
            bz = min(rake_z(bx) + 1.95, -0.50)
            for sy in (1.0, -1.0):
                x = sx * bx
                y0, y1 = sorted((sy * (HW - 0.14), sy * (HW - 0.005)))
                housings.box(x - 0.20, x + 0.20, y0, y1, bz - 0.15, bz + 0.15)
                ly0, ly1 = sorted((sy * (HW - 0.175), sy * (HW - 0.135)))
                lenses.box(x - 0.155, x + 0.155, ly0, ly1, bz - 0.105, bz + 0.105)
                bulkheads.append((x, sy * (HW - 0.30), bz))

    housings.to_object("Luminaire_Housings", mat_housing, col_light)
    lenses.to_object("Luminaire_Lenses", mat_lamp, col_light)

    # ---------------------------------------------------------- environment
    e = Mesher()
    gy = OW + 0.10
    e.box(-30.0, 30.0, gy, 16.0, -0.60, GRADE)
    e.box(-30.0, 30.0, -16.0, -gy, -0.60, GRADE)
    e.box(TOPX, 30.0, -gy, gy, -0.60, GRADE)
    e.box(-30.0, -TOPX, -gy, gy, -0.60, GRADE)
    # low kerbs framing the approach aprons
    for sx in (1.0, -1.0):
        for sy in (1.0, -1.0):
            y0, y1 = sorted((sy * (OW + 0.10), sy * (OW + 0.24)))
            x0, x1 = sorted((sx * TOPX, sx * 30.0))
            e.box(x0, x1, y0, y1, GRADE - 0.02, GRADE + 0.12)
    e.to_object("Ground_Paving", mat_paving, col_env)

    # -------------------------------------------------------------- lamps
    for i, cx in enumerate(ceiling_x):
        ld = bpy.data.lights.new("CeilingLamp_%d" % i, type='AREA')
        ld.shape = 'RECTANGLE'
        ld.size = 1.30
        ld.size_y = 0.26
        ld.energy = 90.0
        ld.color = (1.0, 0.95, 0.86)
        ob = bpy.data.objects.new(ld.name, ld)
        ob.location = (cx, 0.0, CZ - 0.06)
        ob.rotation_euler = (math.pi, 0.0, 0.0)
        col_light.objects.link(ob)

    for i, (bx, by, bz) in enumerate(bulkheads):
        ld = bpy.data.lights.new("BulkheadLamp_%d" % i, type='POINT')
        ld.energy = 35.0
        ld.shadow_soft_size = 0.09
        ld.color = (1.0, 0.94, 0.84)
        ob = bpy.data.objects.new(ld.name, ld)
        ob.location = (bx, by, bz)
        col_light.objects.link(ob)

    sun_data = bpy.data.lights.new("Sun", type='SUN')
    sun_data.energy = 3.2
    sun_data.angle = math.radians(1.5)
    sun_data.color = (1.0, 0.95, 0.87)
    sun = bpy.data.objects.new("Sun", sun_data)
    sun.location = (14.0, -14.0, 20.0)
    sun.rotation_euler = (math.radians(54.0), 0.0, math.radians(38.0))
    col_light.objects.link(sun)

    # soft bounce into the open stair trench
    fill_data = bpy.data.lights.new("TrenchFill", type='AREA')
    fill_data.shape = 'RECTANGLE'
    fill_data.size = 8.0
    fill_data.size_y = 4.0
    fill_data.energy = 220.0
    fill_data.color = (0.72, 0.80, 0.95)
    fill = bpy.data.objects.new("TrenchFill", fill_data)
    fill.location = (13.0, 0.0, 5.0)
    fill.rotation_euler = (math.pi, 0.0, 0.0)
    col_light.objects.link(fill)

    # -------------------------------------------------------------- world
    world = bpy.data.worlds.new("UnderpassWorld")
    world.use_nodes = True
    wnt = world.node_tree
    bg = wnt.nodes["Background"]
    bg.inputs["Strength"].default_value = 1.1
    sky = wnt.nodes.new("ShaderNodeTexSky")
    sky.location = (-320, 0)
    try:
        sky.sky_type = 'NISHITA'
        sky.sun_elevation = math.radians(38.0)
        sky.sun_rotation = math.radians(210.0)
        sky.altitude = 0.0
    except (AttributeError, TypeError):
        pass
    wnt.links.new(sky.outputs["Color"], bg.inputs["Color"])
    bpy.context.scene.world = world

    # ------------------------------------------------------------- camera
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = 28.0
    cam_data.clip_end = 300.0
    cam_data.sensor_width = 36.0
    cam = bpy.data.objects.new("Camera", cam_data)
    cam.location = Vector((23.5, -9.5, 4.6))
    target = Vector((9.0, 0.0, -1.8))
    cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam_data.dof.use_dof = True
    cam_data.dof.focus_distance = (target - cam.location).length
    cam_data.dof.aperture_fstop = 5.6
    col_env.objects.link(cam)
    bpy.context.scene.camera = cam


if __name__ == "__main__":
    build()
