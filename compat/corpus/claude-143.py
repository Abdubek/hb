"""
claude-143 — Timber train station canopy with repeating trusses and a glazed roof.
Blender 4.5 LTS.  Builds the whole scene from factory startup; no render, no save.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler


# ----------------------------------------------------------------------------
# scene reset
# ----------------------------------------------------------------------------
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    try:
        scene.render.engine = 'CYCLES'
        scene.cycles.samples = 128
        scene.cycles.preview_samples = 32
    except Exception:
        pass
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.length_unit = 'METERS'
    return scene


# ----------------------------------------------------------------------------
# materials
# ----------------------------------------------------------------------------
def new_material(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    out.location = (400, 0)
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (100, 0)
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat, nt, bsdf


def set_in(node, key, value):
    if key in node.inputs:
        node.inputs[key].default_value = value


def make_simple(name, color, roughness=0.6, metallic=0.0, specular=0.5):
    mat, nt, bsdf = new_material(name)
    set_in(bsdf, 'Base Color', (*color, 1.0))
    set_in(bsdf, 'Roughness', roughness)
    set_in(bsdf, 'Metallic', metallic)
    set_in(bsdf, 'Specular IOR Level', specular)
    return mat


def make_wood(name, light, dark, grain_scale=6.0, stretch=14.0, roughness=0.5):
    """Procedural sawn-timber: stretched wave bands + noise distortion, plus bump."""
    mat, nt, bsdf = new_material(name)
    coord = nt.nodes.new('ShaderNodeTexCoord')
    coord.location = (-900, 0)
    mapping = nt.nodes.new('ShaderNodeMapping')
    mapping.location = (-720, 0)
    mapping.inputs['Scale'].default_value = (1.0, 1.0, 1.0 / stretch)

    noise = nt.nodes.new('ShaderNodeTexNoise')
    noise.location = (-540, -240)
    noise.inputs['Scale'].default_value = grain_scale * 1.5
    noise.inputs['Detail'].default_value = 6.0
    noise.inputs['Roughness'].default_value = 0.6

    wave = nt.nodes.new('ShaderNodeTexWave')
    wave.location = (-540, 60)
    wave.wave_type = 'BANDS'
    wave.bands_direction = 'Z'
    wave.wave_profile = 'SIN'
    wave.inputs['Scale'].default_value = grain_scale
    wave.inputs['Distortion'].default_value = 6.0
    wave.inputs['Detail'].default_value = 3.0
    wave.inputs['Detail Scale'].default_value = 1.5

    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.location = (-330, 60)
    ramp.color_ramp.interpolation = 'EASE'
    ramp.color_ramp.elements[0].position = 0.25
    ramp.color_ramp.elements[0].color = (*dark, 1.0)
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = (*light, 1.0)

    bump = nt.nodes.new('ShaderNodeBump')
    bump.location = (-120, -260)
    bump.inputs['Strength'].default_value = 0.22
    bump.inputs['Distance'].default_value = 0.01

    rough_mix = nt.nodes.new('ShaderNodeMapRange')
    rough_mix.location = (-120, -60)
    rough_mix.inputs['To Min'].default_value = roughness - 0.12
    rough_mix.inputs['To Max'].default_value = roughness + 0.12

    nt.links.new(coord.outputs['Object'], mapping.inputs['Vector'])
    nt.links.new(mapping.outputs['Vector'], wave.inputs['Vector'])
    nt.links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
    nt.links.new(wave.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    nt.links.new(wave.outputs['Fac'], rough_mix.inputs['Value'])
    nt.links.new(rough_mix.outputs['Result'], bsdf.inputs['Roughness'])
    nt.links.new(noise.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    set_in(bsdf, 'Specular IOR Level', 0.35)
    return mat


def make_glass(name):
    mat, nt, bsdf = new_material(name)
    set_in(bsdf, 'Base Color', (0.86, 0.93, 0.90, 1.0))
    set_in(bsdf, 'Roughness', 0.04)
    set_in(bsdf, 'Transmission Weight', 1.0)
    set_in(bsdf, 'IOR', 1.52)
    set_in(bsdf, 'Metallic', 0.0)
    try:
        mat.blend_method = 'BLEND'
    except Exception:
        pass
    try:
        mat.use_backface_culling = False
    except Exception:
        pass
    return mat


def make_emissive(name, color, strength):
    mat, nt, bsdf = new_material(name)
    set_in(bsdf, 'Base Color', (*color, 1.0))
    set_in(bsdf, 'Roughness', 0.4)
    set_in(bsdf, 'Emission Color', (*color, 1.0))
    set_in(bsdf, 'Emission Strength', strength)
    return mat


def make_concrete(name, color, roughness=0.85, noise_scale=30.0):
    mat, nt, bsdf = new_material(name)
    coord = nt.nodes.new('ShaderNodeTexCoord')
    coord.location = (-700, 0)
    noise = nt.nodes.new('ShaderNodeTexNoise')
    noise.location = (-500, 0)
    noise.inputs['Scale'].default_value = noise_scale
    noise.inputs['Detail'].default_value = 8.0
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.location = (-300, 0)
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (color[0] * 0.75, color[1] * 0.75, color[2] * 0.75, 1.0)
    ramp.color_ramp.elements[1].position = 0.68
    ramp.color_ramp.elements[1].color = (*color, 1.0)
    bump = nt.nodes.new('ShaderNodeBump')
    bump.location = (-120, -230)
    bump.inputs['Strength'].default_value = 0.25
    nt.links.new(coord.outputs['Object'], noise.inputs['Vector'])
    nt.links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    nt.links.new(noise.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    set_in(bsdf, 'Roughness', roughness)
    set_in(bsdf, 'Specular IOR Level', 0.3)
    return mat


# ----------------------------------------------------------------------------
# geometry builder — accumulates boxes / cylinders into one bmesh per material
# ----------------------------------------------------------------------------
class Builder:
    def __init__(self, name):
        self.name = name
        self.bm = bmesh.new()

    # --- primitives ---------------------------------------------------------
    def box(self, center, size, rot=None):
        """Axis-aligned (or Euler-rotated) box, `size` = full dimensions."""
        geom = bmesh.ops.create_cube(self.bm, size=1.0)
        rmat = Matrix.Identity(4)
        if rot is not None:
            rmat = Euler(rot, 'XYZ').to_matrix().to_4x4()
        m = (Matrix.Translation(Vector(center)) @ rmat
             @ Matrix.Diagonal((size[0], size[1], size[2], 1.0)))
        bmesh.ops.transform(self.bm, matrix=m, verts=geom['verts'])

    def beam(self, p1, p2, w, h, extend=0.0):
        """Rectangular member between two points; w across X-ish, h in-plane."""
        p1 = Vector(p1)
        p2 = Vector(p2)
        d = p2 - p1
        L = d.length
        if L < 1e-6:
            return
        d = d / L
        L += 2.0 * extend
        quat = d.to_track_quat('Z', 'Y')
        m = (Matrix.Translation((p1 + p2) * 0.5) @ quat.to_matrix().to_4x4()
             @ Matrix.Diagonal((w, h, L, 1.0)))
        geom = bmesh.ops.create_cube(self.bm, size=1.0)
        bmesh.ops.transform(self.bm, matrix=m, verts=geom['verts'])

    def cyl(self, p1, p2, r, segments=16, r2=None, smooth=True):
        p1 = Vector(p1)
        p2 = Vector(p2)
        d = p2 - p1
        L = d.length
        if L < 1e-6:
            return
        quat = d.normalized().to_track_quat('Z', 'Y')
        geom = bmesh.ops.create_cone(
            self.bm, cap_ends=True, cap_tris=False, segments=segments,
            radius1=r, radius2=(r if r2 is None else r2), depth=L)
        m = Matrix.Translation((p1 + p2) * 0.5) @ quat.to_matrix().to_4x4()
        bmesh.ops.transform(self.bm, matrix=m, verts=geom['verts'])
        if smooth:
            for v in geom['verts']:
                for f in v.link_faces:
                    if len(f.verts) == 4:
                        f.smooth = True

    # --- output -------------------------------------------------------------
    def finish(self, material, collection=None):
        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces[:])
        me = bpy.data.meshes.new(self.name)
        self.bm.to_mesh(me)
        self.bm.free()
        me.validate()
        me.materials.append(material)
        obj = bpy.data.objects.new(self.name, me)
        (collection or bpy.context.scene.collection).objects.link(obj)
        return obj


def new_collection(name, parent=None):
    col = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(col)
    return col


# ----------------------------------------------------------------------------
# canopy parameters
# ----------------------------------------------------------------------------
N_BAYS = 8
BAY = 4.5
X0 = -0.5 * N_BAYS * BAY                 # -18.0
TRUSS_X = [X0 + i * BAY for i in range(N_BAYS + 1)]
LENGTH = N_BAYS * BAY                    # 36.0

PLAT_Z = 0.30                            # platform top level
COL_Y = 4.00                             # column centre lines
EAVE_Y = 5.50                            # end of the top chord
TIE_Z = PLAT_Z + 3.95                    # 4.25 — bottom chord centre
CHORD_EAVE_Z = TIE_Z + 0.34              # top chord centre at the eave
RIDGE_Z = 6.55                           # top chord centre at the ridge

COL_W = 0.34                             # column section
TIE_W, TIE_H = 0.28, 0.42                # tie beam
CH_W, CH_H = 0.24, 0.34                  # rafter / top chord
POST_W, POST_H = 0.20, 0.26              # king post
STR_W, STR_H = 0.17, 0.22                # struts
PUR_W, PUR_H = 0.15, 0.20                # purlins

SLOPE = math.atan2(RIDGE_Z - CHORD_EAVE_Z, EAVE_Y)     # ~17.6 deg
PURLIN_T = [0.03, 0.27, 0.51, 0.75, 0.985]             # along the rafter


def rafter_frame(side):
    """Return (eave point, ridge point, unit direction, outward normal)."""
    eave = Vector((0.0, side * EAVE_Y, CHORD_EAVE_Z))
    ridge = Vector((0.0, 0.0, RIDGE_Z))
    d = (ridge - eave).normalized()
    n = Vector((0.0, d.z, -d.y))
    if n.z < 0.0:
        n = -n
    return eave, ridge, d, n


# ----------------------------------------------------------------------------
# structure
# ----------------------------------------------------------------------------
def build_structure(col, mats):
    posts = Builder('Canopy_Columns')
    truss = Builder('Canopy_Trusses')
    purl = Builder('Canopy_Purlins')
    steel = Builder('Canopy_Ironmongery')
    glass = Builder('Canopy_Glazing')
    ped = Builder('Column_Pedestals')

    # --- repeating trusses --------------------------------------------------
    for xi, x in enumerate(TRUSS_X):
        end_truss = (xi == 0 or xi == len(TRUSS_X) - 1)

        for s in (-1.0, 1.0):
            # column with a light taper cap plate
            posts.box((x, s * COL_Y, (PLAT_Z + TIE_Z - TIE_H * 0.5) * 0.5),
                      (COL_W, COL_W, TIE_Z - TIE_H * 0.5 - PLAT_Z))
            ped.box((x, s * COL_Y, PLAT_Z + 0.11), (COL_W + 0.26, COL_W + 0.26, 0.22))
            steel.box((x, s * COL_Y, TIE_Z - TIE_H * 0.5 - 0.015),
                      (COL_W + 0.10, COL_W + 0.10, 0.03))
            # base shoe + holding-down bolts
            steel.box((x, s * COL_Y, PLAT_Z + 0.25), (COL_W + 0.06, COL_W + 0.06, 0.06))
            for by in (-1, 1):
                steel.cyl((x, s * COL_Y + by * (COL_W * 0.5 + 0.05), PLAT_Z + 0.22),
                          (x, s * COL_Y + by * (COL_W * 0.5 + 0.05), PLAT_Z + 0.34),
                          0.016, 8)

            # knee brace from column into the tie beam
            kb_a = Vector((x, s * COL_Y, PLAT_Z + 2.55))
            kb_b = Vector((x, s * (COL_Y - 1.25), TIE_Z - TIE_H * 0.5))
            truss.beam(kb_a, kb_b, 0.15, 0.24, extend=0.06)
            steel.cyl((x - 0.10, kb_a.y, kb_a.z), (x + 0.10, kb_a.y, kb_a.z), 0.018, 8)
            steel.cyl((x - 0.10, kb_b.y, kb_b.z - 0.05),
                      (x + 0.10, kb_b.y, kb_b.z - 0.05), 0.018, 8)

        # bottom chord / tie beam, spanning the full canopy width
        truss.box((x, 0.0, TIE_Z), (TIE_W, 2.0 * EAVE_Y + 0.30, TIE_H))

        # king post
        truss.box((x, 0.0, (TIE_Z + RIDGE_Z) * 0.5),
                  (POST_W, POST_H, RIDGE_Z - TIE_Z + CH_H * 0.4))

        for s in (-1.0, 1.0):
            eave, ridge, d, n = rafter_frame(s)
            a = Vector((x, eave.y, eave.z))
            b = Vector((x, ridge.y, ridge.z))
            truss.beam(a, b, CH_W, CH_H, extend=0.05)

            # diagonal strut, tie beam -> rafter mid-point
            foot = Vector((x, s * 2.55, TIE_Z + TIE_H * 0.35))
            mid = eave + d * (d.dot(ridge - eave) * 0.50)
            head = Vector((x, mid.y, mid.z - CH_H * 0.25))
            truss.beam(foot, head, STR_W, STR_H, extend=0.05)

            # steel gusset plates + bolts at the panel points
            steel.box((x, foot.y, foot.z + 0.02), (CH_W + 0.09, 0.42, 0.014))
            steel.cyl((x - 0.09, head.y, head.z), (x + 0.09, head.y, head.z), 0.019, 8)
            steel.cyl((x - 0.09, s * 1.10, TIE_Z + 0.02),
                      (x + 0.09, s * 1.10, TIE_Z + 0.02), 0.019, 8)
            # eave seat block
            truss.box((x, s * (COL_Y), TIE_Z + TIE_H * 0.5 + 0.09),
                      (CH_W, 0.55, 0.18))

        # apex plate
        steel.box((x, 0.0, RIDGE_Z - 0.02), (CH_W + 0.10, 0.62, 0.016))
        steel.cyl((x - 0.10, 0.0, RIDGE_Z - 0.30), (x + 0.10, 0.0, RIDGE_Z - 0.30), 0.02, 8)

        # gable infill boards on the two end trusses
        if end_truss:
            sx = -0.16 if xi == 0 else 0.16
            for s in (-1.0, 1.0):
                eave, ridge, d, n = rafter_frame(s)
                for t in (0.18, 0.38, 0.58, 0.78):
                    p = eave + d * (t * (ridge - eave).length)
                    truss.box((x + sx, p.y, (p.z + TIE_Z) * 0.5 + 0.05),
                              (0.06, 0.14, max(0.05, p.z - TIE_Z - 0.10)))

    # --- longitudinal members ----------------------------------------------
    # wall plates over the columns
    for s in (-1.0, 1.0):
        purl.box((0.0, s * COL_Y, TIE_Z - TIE_H * 0.5 - 0.10),
                 (LENGTH + 0.9, 0.20, 0.20))

    # ridge beam
    purl.box((0.0, 0.0, RIDGE_Z + CH_H * 0.5 + 0.13),
             (LENGTH + 0.9, 0.26, 0.26))

    # purlins + glazing bars + glass, both roof slopes
    for s in (-1.0, 1.0):
        eave, ridge, d, n = rafter_frame(s)
        rl = (ridge - eave).length
        rot = (-s * SLOPE, 0.0, 0.0)
        pts = []
        for t in PURLIN_T:
            p = eave + d * (t * rl) + n * (CH_H * 0.5 + PUR_H * 0.5)
            pts.append(p)
            purl.box((0.0, p.y, p.z), (LENGTH + 0.9, PUR_W, PUR_H), rot)

        # glazing bars running up the slope over every truss line
        for x in TRUSS_X:
            a = eave + n * (CH_H * 0.5 + PUR_H + 0.02)
            b = ridge + n * (CH_H * 0.5 + PUR_H + 0.02)
            steel.beam((x, a.y, a.z), (x, b.y, b.z), 0.09, 0.07)

        # glass panels: one per bay per purlin gap
        off = n * (CH_H * 0.5 + PUR_H + 0.045)
        for i in range(len(pts) - 1):
            lo = eave + d * (PURLIN_T[i] * rl) + off
            hi = eave + d * (PURLIN_T[i + 1] * rl) + off
            c = (lo + hi) * 0.5
            span = (hi - lo).length - 0.10
            if span <= 0.05:
                continue
            for bi in range(N_BAYS):
                px = (TRUSS_X[bi] + TRUSS_X[bi + 1]) * 0.5
                glass.box((px, c.y, c.z), (BAY - 0.16, span, 0.022), rot)

        # eaves: fascia, gutter trough, drip edge
        fy = s * (EAVE_Y + 0.20)
        top = eave + n * (CH_H * 0.5 + PUR_H + 0.05)
        purl.box((0.0, fy, top.z - 0.10), (LENGTH + 0.9, 0.06, 0.34))
        gy = s * (EAVE_Y + 0.36)
        steel.box((0.0, gy, top.z - 0.30), (LENGTH + 0.9, 0.26, 0.03))
        for k in (-1, 1):
            steel.box((0.0, gy + k * 0.115, top.z - 0.20),
                      (LENGTH + 0.9, 0.03, 0.22))
        # gutter brackets
        for x in TRUSS_X:
            steel.box((x, gy, top.z - 0.33), (0.05, 0.34, 0.04))
            # rainwater goods on every second frame
        for x in TRUSS_X[::2]:
            steel.cyl((x, gy, top.z - 0.32), (x, s * (COL_Y + 0.30), top.z - 0.46), 0.055, 12)
            steel.cyl((x, s * (COL_Y + 0.30), top.z - 0.46),
                      (x, s * (COL_Y + 0.30), PLAT_Z + 0.05), 0.055, 12)

    # ridge flashing
    for s in (-1.0, 1.0):
        eave, ridge, d, n = rafter_frame(s)
        p = ridge + d * (-0.35) + n * (CH_H * 0.5 + PUR_H + 0.09)
        steel.box((0.0, p.y, p.z), (LENGTH + 0.9, 0.75, 0.025), (-s * SLOPE, 0.0, 0.0))

    # longitudinal sway bracing in alternate bays
    for bi in range(N_BAYS):
        if bi % 2 == 0:
            continue
        xa, xb = TRUSS_X[bi], TRUSS_X[bi + 1]
        zl, zh = PLAT_Z + 1.35, TIE_Z - TIE_H * 0.5 - 0.22
        for s in (-1.0, 1.0):
            truss.beam((xa, s * COL_Y, zl), (xb, s * COL_Y, zh), 0.10, 0.14)
            truss.beam((xb, s * COL_Y, zl), (xa, s * COL_Y, zh), 0.10, 0.14)
            steel.cyl(((xa + xb) * 0.5, s * COL_Y - 0.11, (zl + zh) * 0.5),
                      ((xa + xb) * 0.5, s * COL_Y + 0.11, (zl + zh) * 0.5), 0.022, 8)

    objs = [
        posts.finish(mats['wood_col'], col),
        truss.finish(mats['wood_beam'], col),
        purl.finish(mats['wood_purlin'], col),
        steel.finish(mats['steel'], col),
        glass.finish(mats['glass'], col),
        ped.finish(mats['concrete_dark'], col),
    ]
    return objs


# ----------------------------------------------------------------------------
# platform, track and ground
# ----------------------------------------------------------------------------
def build_platform(col, mats):
    plat = Builder('Platform_Slab')
    plat.box((0.0, 0.0, PLAT_Z * 0.5), (LENGTH + 12.0, 13.2, PLAT_Z))
    # coping course along both edges
    for s in (-1.0, 1.0):
        plat.box((0.0, s * 6.35, PLAT_Z - 0.06), (LENGTH + 12.0, 0.50, PLAT_Z + 0.02))
    plat_obj = plat.finish(mats['concrete'], col)

    strip = Builder('Tactile_Strip')
    for s in (-1.0, 1.0):
        strip.box((0.0, s * 5.85, PLAT_Z + 0.006), (LENGTH + 12.0, 0.60, 0.02))
    strip_obj = strip.finish(mats['yellow'], col)

    ground = Builder('Ballast_Ground')
    ground.box((0.0, 0.0, -0.30), (110.0, 70.0, 0.60))
    for s in (-1.0, 1.0):
        ground.box((0.0, s * 10.2, 0.05), (LENGTH + 24.0, 6.6, 0.24))
    ground_obj = ground.finish(mats['gravel'], col)

    track = Builder('Track')
    half_len = (LENGTH + 24.0) * 0.5
    for s in (-1.0, 1.0):
        cy = s * 10.2
        n_sleep = int((2 * half_len) // 0.75)
        for i in range(n_sleep + 1):
            x = -half_len + i * 0.75
            track.box((x, cy, 0.24), (0.26, 2.60, 0.16))
        for r in (-1, 1):
            ry = cy + r * 0.7175
            track.box((0.0, ry, 0.36), (2 * half_len, 0.15, 0.04))   # foot
            track.box((0.0, ry, 0.44), (2 * half_len, 0.05, 0.13))   # web
            track.box((0.0, ry, 0.53), (2 * half_len, 0.09, 0.05))   # head
    track_obj = track.finish(mats['rail'], col)

    return [plat_obj, strip_obj, ground_obj, track_obj]


# ----------------------------------------------------------------------------
# furniture: benches, pendant lamps, signs
# ----------------------------------------------------------------------------
def build_furniture(col, mats):
    wood = Builder('Benches_Timber')
    frame = Builder('Furniture_Steel')
    shades = Builder('Lamp_Shades')
    bulbs = Builder('Lamp_Bulbs')
    signs = Builder('Signage')

    # benches, back to back against the column line
    for bx in (-13.5, -4.5, 4.5, 13.5):
        for s in (-1.0, 1.0):
            by = s * (COL_Y - 1.05)
            for i in range(4):
                wood.box((bx, by + s * (i * 0.13 - 0.20), PLAT_Z + 0.46),
                         (1.85, 0.11, 0.05))
            for i in range(3):
                wood.box((bx, by - s * 0.28, PLAT_Z + 0.62 + i * 0.15),
                         (1.85, 0.05, 0.11), (0.16 * s, 0.0, 0.0))
            for lx in (-0.72, 0.72):
                frame.box((bx + lx, by, PLAT_Z + 0.23), (0.06, 0.62, 0.46))
                frame.box((bx + lx, by, PLAT_Z + 0.02), (0.10, 0.72, 0.04))

    # pendant lamps hung from the tie beams at mid-bay
    for bi in range(N_BAYS):
        px = (TRUSS_X[bi] + TRUSS_X[bi + 1]) * 0.5
        if bi % 2 == 1:
            continue
        for ly in (-2.4, 2.4):
            top = PLAT_Z + 3.95 - TIE_H * 0.5
            frame.cyl((px, ly, top), (px, ly, top - 0.55), 0.022, 10)
            shades.cyl((px, ly, top - 0.55), (px, ly, top - 0.82),
                       0.10, 20, r2=0.30)
            bulbs.cyl((px, ly, top - 0.83), (px, ly, top - 0.80), 0.27, 20)

    # hanging platform signs
    for sx in (-9.0, 9.0):
        top = PLAT_Z + 3.95 - TIE_H * 0.5
        for hy in (-0.55, 0.55):
            frame.cyl((sx, hy, top), (sx, hy, top - 0.35), 0.018, 8)
        signs.box((sx, 0.0, top - 0.62), (0.05, 1.70, 0.56))
        frame.box((sx, 0.0, top - 0.62), (0.02, 1.78, 0.62))

    return [
        wood.finish(mats['wood_beam'], col),
        frame.finish(mats['steel_dark'], col),
        shades.finish(mats['steel_dark'], col),
        bulbs.finish(mats['bulb'], col),
        signs.finish(mats['sign'], col),
    ]


# ----------------------------------------------------------------------------
# world, lights, camera
# ----------------------------------------------------------------------------
def build_world(scene):
    world = bpy.data.worlds.new('CanopySky')
    scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputWorld')
    out.location = (300, 0)
    bg = nt.nodes.new('ShaderNodeBackground')
    bg.location = (100, 0)
    bg.inputs['Strength'].default_value = 1.0
    sky = nt.nodes.new('ShaderNodeTexSky')
    sky.location = (-160, 0)
    try:
        sky.sky_type = 'NISHITA'
        sky.sun_elevation = math.radians(28.0)
        sky.sun_rotation = math.radians(215.0)
        sky.altitude = 60.0
        sky.air_density = 1.1
        sky.dust_density = 1.6
    except Exception:
        pass
    nt.links.new(sky.outputs['Color'], bg.inputs['Color'])
    nt.links.new(bg.outputs['Background'], out.inputs['Surface'])


def build_lights(col):
    sun_data = bpy.data.lights.new('KeySun', 'SUN')
    sun_data.energy = 4.0
    sun_data.angle = math.radians(1.6)
    sun_data.color = (1.0, 0.95, 0.86)
    sun = bpy.data.objects.new('KeySun', sun_data)
    sun.rotation_euler = (math.radians(56.0), 0.0, math.radians(215.0))
    sun.location = (-20.0, -25.0, 24.0)
    col.objects.link(sun)

    fill_data = bpy.data.lights.new('SkyFill', 'AREA')
    fill_data.energy = 900.0
    fill_data.shape = 'RECTANGLE'
    fill_data.size = 30.0
    fill_data.size_y = 14.0
    fill_data.color = (0.72, 0.82, 1.0)
    fill = bpy.data.objects.new('SkyFill', fill_data)
    fill.location = (6.0, -14.0, 16.0)
    fill.rotation_euler = (math.radians(38.0), 0.0, 0.0)
    col.objects.link(fill)

    for i, px in enumerate((-13.5, -4.5, 4.5, 13.5)):
        pd = bpy.data.lights.new('Pendant_%d' % i, 'POINT')
        pd.energy = 90.0
        pd.shadow_soft_size = 0.28
        pd.color = (1.0, 0.86, 0.68)
        po = bpy.data.objects.new('Pendant_%d' % i, pd)
        po.location = (px, 0.0, PLAT_Z + 3.1)
        col.objects.link(po)


def build_camera(scene, col):
    cam_data = bpy.data.cameras.new('CanopyCam')
    cam_data.lens = 32.0
    cam_data.sensor_width = 36.0
    cam_data.clip_end = 500.0
    cam_data.dof.use_dof = True
    cam_data.dof.focus_distance = 26.0
    cam_data.dof.aperture_fstop = 5.6
    cam = bpy.data.objects.new('CanopyCam', cam_data)
    cam.location = (-26.0, -21.0, 6.4)
    target = Vector((2.0, 0.0, 3.4))
    cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
    col.objects.link(cam)
    scene.camera = cam

    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.film_transparent = False
    return cam


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------
def main():
    scene = reset_scene()

    mats = {
        'wood_col': make_wood('Timber_Column', (0.42, 0.26, 0.14), (0.24, 0.13, 0.07),
                              grain_scale=7.0, stretch=16.0, roughness=0.55),
        'wood_beam': make_wood('Timber_Truss', (0.55, 0.37, 0.21), (0.34, 0.20, 0.10),
                               grain_scale=6.0, stretch=18.0, roughness=0.5),
        'wood_purlin': make_wood('Timber_Purlin', (0.60, 0.43, 0.26), (0.38, 0.24, 0.13),
                                 grain_scale=8.0, stretch=22.0, roughness=0.48),
        'steel': make_simple('Steel_Galv', (0.52, 0.54, 0.56), 0.35, 1.0),
        'steel_dark': make_simple('Steel_Dark', (0.055, 0.058, 0.062), 0.42, 0.9),
        'rail': make_simple('Rail_Steel', (0.20, 0.17, 0.15), 0.55, 1.0),
        'glass': make_glass('Roof_Glazing'),
        'concrete': make_concrete('Platform_Concrete', (0.60, 0.58, 0.55), 0.85, 26.0),
        'concrete_dark': make_concrete('Pedestal_Concrete', (0.42, 0.40, 0.38), 0.9, 40.0),
        'gravel': make_concrete('Ballast', (0.27, 0.25, 0.23), 0.95, 90.0),
        'yellow': make_simple('Tactile_Yellow', (0.85, 0.62, 0.05), 0.65),
        'bulb': make_emissive('Lamp_Glow', (1.0, 0.83, 0.62), 14.0),
        'sign': make_emissive('Sign_Board', (0.03, 0.12, 0.32), 1.2),
    }

    canopy_col = new_collection('Canopy')
    site_col = new_collection('Site')
    furn_col = new_collection('Furniture')
    light_col = new_collection('Lighting')

    build_structure(canopy_col, mats)
    build_platform(site_col, mats)
    build_furniture(furn_col, mats)
    build_world(scene)
    build_lights(light_col)
    build_camera(scene, light_col)

    bpy.context.view_layer.update()


if __name__ == '__main__':
    main()
