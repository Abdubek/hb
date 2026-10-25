import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

random.seed(20260909)

# =============================================================================
#  Corner cafe interior  --  banquette seating, service counter, pendant lights
# =============================================================================

ROOM = dict(x0=-5.0, x1=5.0, y0=-4.0, y1=4.0, h=3.40)
WT = 0.15                      # wall thickness
SILL_Z = 0.45                  # top of the window parapet
GLASS_TOP = 2.85               # head of the glazing

_SMOOTH = []                   # objects that want angle based smoothing
_COLLS = {}


# ----------------------------------------------------------------- scene reset
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = 'METRIC'
    sc.unit_settings.length_unit = 'METERS'
    try:
        sc.render.engine = 'CYCLES'
        sc.cycles.samples = 128
        sc.cycles.preview_samples = 32
        sc.cycles.use_denoising = True
    except Exception:
        pass
    sc.render.resolution_x = 1920
    sc.render.resolution_y = 1080
    sc.render.film_transparent = False
    try:
        sc.view_settings.view_transform = 'AgX'
        sc.view_settings.look = 'AgX - Medium Contrast'
    except Exception:
        pass


def coll(name):
    if name not in _COLLS:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
        _COLLS[name] = c
    return _COLLS[name]


def link(ob, name):
    coll(name).objects.link(ob)
    return ob


# ------------------------------------------------------------------- materials
def mat_basic(name, color, rough=0.5, metal=0.0, ior=1.45, alpha=1.0,
              transmission=0.0, coat=0.0, sheen=0.0,
              emission=None, emission_strength=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    if bsdf is None:
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        out = nt.nodes.get("Material Output") or nt.nodes.new("ShaderNodeOutputMaterial")
        nt.links.new(bsdf.outputs[0], out.inputs[0])

    def s(key, val):
        if key in bsdf.inputs:
            bsdf.inputs[key].default_value = val

    s("Base Color", (color[0], color[1], color[2], 1.0))
    s("Roughness", rough)
    s("Metallic", metal)
    s("IOR", ior)
    s("Alpha", alpha)
    s("Transmission Weight", transmission)
    s("Coat Weight", coat)
    s("Sheen Weight", sheen)
    if emission is not None:
        s("Emission Color", (emission[0], emission[1], emission[2], 1.0))
        s("Emission Strength", emission_strength)
    if alpha < 1.0 or transmission > 0.0:
        try:
            m.blend_method = 'BLEND'
        except Exception:
            pass
        try:
            m.use_transparent_shadow = True
        except Exception:
            pass
    m.diffuse_color = (color[0], color[1], color[2], alpha)
    return m


def mat_checker_floor():
    """Classic black & white cafe tiles, rotated 45 degrees."""
    m = bpy.data.materials.new("FloorTile")
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.22
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = 0.25

    tc = nt.nodes.new("ShaderNodeTexCoord")
    tc.location = (-900, 0)
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.location = (-700, 0)
    mp.inputs["Rotation"].default_value = (0.0, 0.0, math.radians(45.0))
    mp.inputs["Scale"].default_value = (3.0, 3.0, 3.0)
    ck = nt.nodes.new("ShaderNodeTexChecker")
    ck.location = (-500, 0)
    ck.inputs["Color1"].default_value = (0.82, 0.80, 0.75, 1.0)
    ck.inputs["Color2"].default_value = (0.045, 0.045, 0.05, 1.0)
    ck.inputs["Scale"].default_value = 1.0

    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.location = (-500, -260)
    nz.inputs["Scale"].default_value = 40.0
    nz.inputs["Detail"].default_value = 4.0
    rr = nt.nodes.new("ShaderNodeMapRange")
    rr.location = (-300, -260)
    rr.inputs["To Min"].default_value = 0.14
    rr.inputs["To Max"].default_value = 0.34

    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], ck.inputs["Vector"])
    nt.links.new(ck.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(nz.outputs["Fac"], rr.inputs["Value"])
    nt.links.new(rr.outputs["Result"], bsdf.inputs["Roughness"])
    return m


def mat_marble():
    m = bpy.data.materials.new("MarbleTop")
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.13
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = 0.4

    tc = nt.nodes.new("ShaderNodeTexCoord")
    tc.location = (-1000, 0)
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.location = (-800, 0)
    nz.inputs["Scale"].default_value = 2.4
    nz.inputs["Detail"].default_value = 8.0
    if "Distortion" in nz.inputs:
        nz.inputs["Distortion"].default_value = 1.6
    wv = nt.nodes.new("ShaderNodeTexWave")
    wv.location = (-600, 0)
    wv.wave_type = 'BANDS'
    wv.inputs["Scale"].default_value = 1.4
    wv.inputs["Distortion"].default_value = 14.0
    wv.inputs["Detail"].default_value = 3.0
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.location = (-380, 0)
    ramp.color_ramp.elements[0].position = 0.34
    ramp.color_ramp.elements[0].color = (0.88, 0.87, 0.85, 1.0)
    ramp.color_ramp.elements[1].position = 0.62
    ramp.color_ramp.elements[1].color = (0.36, 0.37, 0.39, 1.0)

    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    nt.links.new(nz.outputs["Fac"], wv.inputs["Vector"])
    nt.links.new(wv.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    return m


def build_materials():
    M = {}
    M['floor'] = mat_checker_floor()
    M['marble'] = mat_marble()
    M['wall'] = mat_basic("WallGreen", (0.055, 0.115, 0.098), rough=0.72)
    M['wain'] = mat_basic("WainscotCream", (0.72, 0.68, 0.60), rough=0.42)
    M['ceiling'] = mat_basic("CeilingWhite", (0.86, 0.85, 0.83), rough=0.85)
    M['oak'] = mat_basic("OakTrim", (0.40, 0.245, 0.115), rough=0.36, coat=0.15)
    M['walnut'] = mat_basic("Walnut", (0.145, 0.078, 0.042), rough=0.38, coat=0.12)
    M['leather'] = mat_basic("BanquetteLeather", (0.115, 0.20, 0.155),
                             rough=0.44, sheen=0.25)
    M['brass'] = mat_basic("Brass", (0.72, 0.53, 0.24), rough=0.22, metal=1.0)
    M['brass_dark'] = mat_basic("BrassAged", (0.44, 0.33, 0.16), rough=0.38, metal=1.0)
    M['chrome'] = mat_basic("Chrome", (0.90, 0.90, 0.91), rough=0.09, metal=1.0)
    M['blackmetal'] = mat_basic("BlackMetal", (0.035, 0.035, 0.038), rough=0.34, metal=0.85)
    M['glass'] = mat_basic("WindowGlass", (0.93, 0.96, 0.95), rough=0.02,
                           ior=1.50, alpha=0.12, transmission=1.0)
    M['glass_case'] = mat_basic("CaseGlass", (0.96, 0.98, 0.97), rough=0.01,
                                ior=1.50, alpha=0.10, transmission=1.0)
    M['ceramic'] = mat_basic("Ceramic", (0.90, 0.89, 0.86), rough=0.14, coat=0.35)
    M['chalkboard'] = mat_basic("Chalkboard", (0.035, 0.045, 0.042), rough=0.88)
    M['chalk'] = mat_basic("Chalk", (0.86, 0.86, 0.82), rough=0.95)
    M['leaf'] = mat_basic("Foliage", (0.075, 0.20, 0.065), rough=0.55, sheen=0.2)
    M['terracotta'] = mat_basic("Terracotta", (0.42, 0.19, 0.115), rough=0.68)
    M['soil'] = mat_basic("Soil", (0.055, 0.04, 0.03), rough=0.94)
    M['concrete'] = mat_basic("Sidewalk", (0.38, 0.375, 0.36), rough=0.82)
    M['asphalt'] = mat_basic("Asphalt", (0.075, 0.075, 0.08), rough=0.72)
    M['brick'] = mat_basic("ExtBrick", (0.28, 0.155, 0.115), rough=0.80)
    M['extglass'] = mat_basic("ExtGlass", (0.09, 0.11, 0.13), rough=0.14, metal=0.4)
    M['bulb'] = mat_basic("BulbEmit", (1.0, 0.78, 0.50), rough=0.4,
                          emission=(1.0, 0.72, 0.42), emission_strength=14.0)
    M['paper'] = mat_basic("Paper", (0.80, 0.78, 0.73), rough=0.75)
    M['pastry'] = mat_basic("Pastry", (0.62, 0.40, 0.19), rough=0.62)
    M['icing'] = mat_basic("Icing", (0.86, 0.72, 0.68), rough=0.42)
    M['fabric'] = mat_basic("CushionFabric", (0.46, 0.20, 0.16), rough=0.80, sheen=0.4)
    M['rubber'] = mat_basic("MatRubber", (0.045, 0.05, 0.05), rough=0.92)
    return M


# ------------------------------------------------------------- bmesh utilities
def _xform(bm, verts, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
    Mtx = (Matrix.Translation(Vector(loc)) @
           Euler(rot, 'XYZ').to_matrix().to_4x4() @
           Matrix.Diagonal(Vector(scale).to_4d()))
    bmesh.ops.transform(bm, matrix=Mtx, verts=verts)
    return verts


def bm_box(bm, size=(1, 1, 1), loc=(0, 0, 0), rot=(0, 0, 0)):
    res = bmesh.ops.create_cube(bm, size=1.0)
    v = res['verts']
    bmesh.ops.scale(bm, vec=Vector(size), verts=v)
    return _xform(bm, v, loc, rot)


def bm_span(bm, p0, p1):
    """Axis aligned box from two opposite corners."""
    p0 = Vector(p0)
    p1 = Vector(p1)
    size = Vector((abs(p1.x - p0.x), abs(p1.y - p0.y), abs(p1.z - p0.z)))
    ctr = (p0 + p1) * 0.5
    return bm_box(bm, size, ctr)


def bm_cyl(bm, r1, r2, depth, loc=(0, 0, 0), rot=(0, 0, 0), segs=24, caps=True):
    kw = dict(cap_ends=caps, cap_tris=False, segments=segs, depth=depth)
    try:
        res = bmesh.ops.create_cone(bm, radius1=r1, radius2=r2, **kw)
    except TypeError:
        res = bmesh.ops.create_cone(bm, diameter1=r1 * 2.0, diameter2=r2 * 2.0, **kw)
    v = res['verts']
    _xform(bm, v, loc, rot)
    for vv in v:
        for f in vv.link_faces:
            f.smooth = True
    return v


def bm_sphere(bm, r, loc=(0, 0, 0), scale=(1, 1, 1), rot=(0, 0, 0), subd=2):
    try:
        res = bmesh.ops.create_icosphere(bm, subdivisions=subd, radius=r)
    except TypeError:
        res = bmesh.ops.create_icosphere(bm, subdivisions=subd, diameter=r * 2.0)
    v = res['verts']
    _xform(bm, v, loc, rot, scale)
    for vv in v:
        for f in vv.link_faces:
            f.smooth = True
    return v


def finish(name, bm, mat=None, collection="Props", loc=(0, 0, 0), rot=(0, 0, 0)):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.validate(verbose=False)
    ob = bpy.data.objects.new(name, me)
    if mat is not None:
        ob.data.materials.append(mat)
    link(ob, collection)
    ob.location = Vector(loc)
    ob.rotation_euler = Euler(rot, 'XYZ')
    return ob


def bevel(ob, width=0.008, segments=2, angle=45.0):
    md = ob.modifiers.new("Bevel", 'BEVEL')
    md.width = width
    md.segments = segments
    md.limit_method = 'ANGLE'
    md.angle_limit = math.radians(angle)
    return md


def want_smooth(ob):
    _SMOOTH.append(ob)
    return ob


def apply_auto_smooth():
    for ob in _SMOOTH:
        try:
            for o in list(bpy.context.selected_objects):
                o.select_set(False)
            bpy.context.view_layer.objects.active = ob
            ob.select_set(True)
            bpy.ops.object.shade_auto_smooth(angle=math.radians(38.0))
            ob.select_set(False)
        except Exception:
            pass


# ------------------------------------------------------------------- the shell
def build_shell(M):
    x0, x1, y0, y1, h = ROOM['x0'], ROOM['x1'], ROOM['y0'], ROOM['y1'], ROOM['h']

    bm = bmesh.new()
    bm_span(bm, (x0 - WT, y0 - WT, -0.14), (x1 + WT, y1 + WT, 0.0))
    finish("Floor", bm, M['floor'], "Shell")

    bm = bmesh.new()
    bm_span(bm, (x0 - WT, y0 - WT, h), (x1 + WT, y1 + WT, h + 0.16))
    finish("Ceiling", bm, M['ceiling'], "Shell")

    # solid back and right walls
    bm = bmesh.new()
    bm_span(bm, (x0 - WT, y1, 0.0), (x1 + WT, y1 + WT, h))
    bm_span(bm, (x1, y0 - WT, 0.0), (x1 + WT, y1, h))
    finish("SolidWalls", bm, M['wall'], "Shell")

    # wainscot panelling on the two solid walls
    bm = bmesh.new()
    bm_span(bm, (x0, y1 - 0.028, 0.10), (x1, y1, 1.02))
    bm_span(bm, (x1 - 0.028, y0, 0.10), (x1, y1, 1.02))
    for i in range(24):                                 # vertical stiles
        xp = x0 + 0.24 + i * 0.41
        if xp < x1 - 0.2:
            bm_span(bm, (xp - 0.022, y1 - 0.046, 0.12), (xp + 0.022, y1 - 0.026, 1.0))
    for i in range(18):
        yp = y0 + 0.24 + i * 0.41
        if yp < y1 - 0.2:
            bm_span(bm, (x1 - 0.046, yp - 0.022, 0.12), (x1 - 0.026, yp + 0.022, 1.0))
    finish("Wainscot", bm, M['wain'], "Shell")

    # chair rail + skirting
    bm = bmesh.new()
    bm_span(bm, (x0, y1 - 0.06, 1.02), (x1, y1, 1.09))
    bm_span(bm, (x1 - 0.06, y0, 1.02), (x1, y1, 1.09))
    bm_span(bm, (x0, y1 - 0.045, 0.0), (x1, y1, 0.11))
    bm_span(bm, (x1 - 0.045, y0, 0.0), (x1, y1, 0.11))
    bm_span(bm, (x0, y0, 0.0), (x1, y0 + 0.045, 0.11))
    bm_span(bm, (x0, y0, 0.0), (x0 + 0.045, y1, 0.11))
    ob = finish("Trim", bm, M['oak'], "Shell")
    bevel(ob, 0.006, 2)

    # cornice
    bm = bmesh.new()
    bm_span(bm, (x0, y1 - 0.09, h - 0.12), (x1, y1, h))
    bm_span(bm, (x1 - 0.09, y0, h - 0.12), (x1, y1, h))
    bm_span(bm, (x0, y0, h - 0.12), (x1, y0 + 0.09, h))
    bm_span(bm, (x0, y0, h - 0.12), (x0 + 0.09, y1, h))
    ob = finish("Cornice", bm, M['ceiling'], "Shell")
    bevel(ob, 0.01, 2)


def build_facades(M):
    """Two glazed street facades meeting at the corner, entrance door on -X."""
    x0, x1, y0, y1, h = ROOM['x0'], ROOM['x1'], ROOM['y0'], ROOM['y1'], ROOM['h']
    fy = y0 - WT                       # outer face of the front facade
    fx = x0 - WT                       # outer face of the side facade

    frame = bmesh.new()
    glass = bmesh.new()
    ledge = bmesh.new()

    # ---- front facade (runs along X at y = y0), 6 bays
    bm_span(frame, (fx, fy, 0.0), (x1 + WT, y0, SILL_Z))                 # parapet
    bm_span(frame, (fx, fy, GLASS_TOP), (x1 + WT, y0, h))                # header
    xs = [x0 + i * (x1 - x0) / 6.0 for i in range(7)]
    for xp in xs[1:-1]:
        bm_span(frame, (xp - 0.06, fy, SILL_Z), (xp + 0.06, y0, GLASS_TOP))
    for i in range(6):
        a, b = xs[i] + 0.06, xs[i + 1] - 0.06
        bm_span(frame, (a, fy + 0.02, 2.32), (b, y0 - 0.02, 2.40))       # transom
        bm_span(glass, (a, fy + 0.055, SILL_Z + 0.01), (b, fy + 0.075, 2.32))
        bm_span(glass, (a, fy + 0.055, 2.40), (b, fy + 0.075, GLASS_TOP - 0.01))
    bm_span(ledge, (x0, y0 - 0.02, SILL_Z), (x1, y0 + 0.14, SILL_Z + 0.05))

    # ---- side facade (runs along Y at x = x0): glazing, then door, then wall
    gy1 = 1.50
    dy0, dy1 = 1.50, 2.80
    bm_span(frame, (fx, fy, 0.0), (x0, gy1, SILL_Z))
    bm_span(frame, (fx, fy, GLASS_TOP), (x0, gy1, h))
    ys = [y0 + i * (gy1 - y0) / 4.0 for i in range(5)]
    for yp in ys[1:-1]:
        bm_span(frame, (fx, yp - 0.06, SILL_Z), (x0, yp + 0.06, GLASS_TOP))
    for i in range(4):
        a, b = ys[i] + 0.06, ys[i + 1] - 0.06
        bm_span(frame, (fx + 0.02, a, 2.32), (x0 - 0.02, b, 2.40))
        bm_span(glass, (fx + 0.055, a, SILL_Z + 0.01), (fx + 0.075, b, 2.32))
        bm_span(glass, (fx + 0.055, a, 2.40), (fx + 0.075, b, GLASS_TOP - 0.01))
    bm_span(ledge, (x0 - 0.02, y0, SILL_Z), (x0 + 0.14, gy1, SILL_Z + 0.05))

    # door opening surround, transom and the wall stub carrying the back bar
    bm_span(frame, (fx, dy0 - 0.07, 0.0), (x0, dy0 + 0.07, 2.62))
    bm_span(frame, (fx, dy1 - 0.07, 0.0), (x0, dy1 + 0.07, 2.62))
    bm_span(frame, (fx, dy0, 2.48), (x0, dy1, 2.62))
    bm_span(glass, (fx + 0.055, dy0 + 0.07, 2.62), (fx + 0.075, dy1 - 0.07, h - 0.02))
    bm_span(frame, (fx, dy1 + 0.07, 0.0), (x0, y1, h))       # solid return
    # corner post
    bm_span(frame, (fx, fy, 0.0), (x0 - 0.02, y0 - 0.02, h))

    ob = finish("FacadeFrame", frame, M['blackmetal'], "Shell")
    bevel(ob, 0.006, 1)
    finish("FacadeGlass", glass, M['glass'], "Shell")
    ob = finish("WindowLedge", ledge, M['oak'], "Shell")
    bevel(ob, 0.008, 2)

    # ---- door leaf (glazed, oak stiles, brass push bar)
    leaf = bmesh.new()
    lz = 2.42
    bm_span(leaf, (-0.03, -0.60, 0.0), (0.03, -0.52, lz))
    bm_span(leaf, (-0.03, 0.52, 0.0), (0.03, 0.60, lz))
    bm_span(leaf, (-0.03, -0.60, 0.0), (0.03, 0.60, 0.30))
    bm_span(leaf, (-0.03, -0.60, lz - 0.12), (0.03, 0.60, lz))
    bm_span(leaf, (-0.03, -0.60, 1.06), (0.03, 0.60, 1.14))
    ob = finish("DoorLeaf", leaf, M['oak'], "Shell",
                loc=(x0 - 0.075, (dy0 + dy1) * 0.5, 0.0), rot=(0, 0, math.radians(-9)))
    bevel(ob, 0.006, 2)

    dg = bmesh.new()
    bm_span(dg, (-0.008, -0.52, 0.30), (0.008, 0.52, 1.06))
    bm_span(dg, (-0.008, -0.52, 1.14), (0.008, 0.52, lz - 0.12))
    finish("DoorGlass", dg, M['glass'], "Shell",
           loc=(x0 - 0.075, (dy0 + dy1) * 0.5, 0.0), rot=(0, 0, math.radians(-9)))

    hw = bmesh.new()
    bm_cyl(hw, 0.017, 0.017, 1.05, (0.055, 0.34, 1.06), segs=14)
    bm_cyl(hw, 0.014, 0.014, 0.10, (0.03, 0.34, 0.60), rot=(0, math.radians(90), 0), segs=10)
    bm_cyl(hw, 0.014, 0.014, 0.10, (0.03, 0.34, 1.52), rot=(0, math.radians(90), 0), segs=10)
    ob = finish("DoorHardware", hw, M['brass'], "Shell",
                loc=(x0 - 0.075, (dy0 + dy1) * 0.5, 0.0), rot=(0, 0, math.radians(-9)))
    want_smooth(ob)

    # entrance mat
    bm = bmesh.new()
    bm_span(bm, (x0 + 0.10, dy0 - 0.05, 0.0), (x0 + 1.05, dy1 + 0.05, 0.015))
    finish("DoorMat", bm, M['rubber'], "Props")


def build_exterior(M):
    """A minimal streetscape so the corner glazing reads as a real corner."""
    x0, y0 = ROOM['x0'], ROOM['y0']

    bm = bmesh.new()
    bm_span(bm, (-40, -40, -0.60), (40, 40, -0.30))
    finish("Street", bm, M['asphalt'], "Exterior")

    bm = bmesh.new()
    bm_span(bm, (-40, y0 - 4.2, -0.30), (40, y0 - 0.16, -0.14))
    bm_span(bm, (x0 - 4.2, -40, -0.30), (x0 - 0.16, 40, -0.14))
    bm_span(bm, (-40, y0 - 4.35, -0.30), (40, y0 - 4.2, -0.02))       # kerb
    bm_span(bm, (x0 - 4.35, -40, -0.30), (x0 - 4.2, 40, -0.02))
    finish("Sidewalk", bm, M['concrete'], "Exterior")

    bm = bmesh.new()
    bm_span(bm, (-13.0, -22.0, -0.2), (2.0, -12.0, 13.5))
    bm_span(bm, (4.0, -24.0, -0.2), (17.0, -13.0, 10.0))
    bm_span(bm, (-22.0, 2.0, -0.2), (-12.0, 16.0, 15.0))
    finish("Blocks", bm, M['brick'], "Exterior")

    bm = bmesh.new()
    for z in (2.0, 4.6, 7.2, 9.8):
        for i in range(6):
            xa = -12.4 + i * 2.4
            bm_span(bm, (xa, -12.12, z), (xa + 1.5, -11.98, z + 1.7))
    for z in (2.0, 4.6, 7.2):
        for i in range(5):
            ya = 2.6 + i * 2.5
            bm_span(bm, (-12.12, ya, z), (-11.98, ya + 1.6, z + 1.7))
    finish("BlockWindows", bm, M['extglass'], "Exterior")

    # street lamp on the corner
    bm = bmesh.new()
    bm_cyl(bm, 0.10, 0.07, 4.4, (x0 - 2.4, y0 - 2.4, 2.0), segs=14)
    bm_cyl(bm, 0.16, 0.16, 0.12, (x0 - 2.4, y0 - 2.4, -0.08), segs=16)
    bm_cyl(bm, 0.20, 0.11, 0.32, (x0 - 2.4, y0 - 2.4, 4.30), segs=16)
    ob = finish("StreetLamp", bm, M['blackmetal'], "Exterior")
    want_smooth(ob)


# ------------------------------------------------------------------- banquette
def make_banquette(name, length, loc, rot_z, M, seg_len=0.72):
    """Upholstered bench.  Local frame: wall plane at y=0, room toward +Y,
    bench extends along local X from -length/2 to +length/2."""
    L = length
    nseg = max(1, int(round(L / seg_len)))
    sw = L / nseg

    wood = bmesh.new()
    bm_span(wood, (-L / 2, 0.03, 0.02), (L / 2, 0.58, 0.30))          # plinth
    bm_span(wood, (-L / 2, 0.0, 0.30), (L / 2, 0.10, 1.06))           # back board
    bm_span(wood, (-L / 2 - 0.02, -0.01, 1.06), (L / 2 + 0.02, 0.18, 1.15))  # cap rail
    for i in range(nseg + 1):                                          # divider legs
        xp = -L / 2 + i * sw
        bm_span(wood, (xp - 0.025, 0.05, 0.0), (xp + 0.025, 0.56, 0.30))
    ob_w = finish(name + "_Frame", wood, M['walnut'], "Furniture", loc=loc, rot=(0, 0, rot_z))
    bevel(ob_w, 0.008, 2)

    hide = bmesh.new()
    for i in range(nseg):
        cx = -L / 2 + (i + 0.5) * sw
        bm_box(hide, (sw - 0.03, 0.56, 0.16), (cx, 0.31, 0.375))       # seat pad
        bm_box(hide, (sw - 0.04, 0.15, 0.62), (cx, 0.165, 0.70),
               rot=(math.radians(7), 0, 0))                            # back pad
    ob_h = finish(name + "_Pads", hide, M['leather'], "Furniture", loc=loc, rot=(0, 0, rot_z))
    bevel(ob_h, 0.035, 4, angle=60)

    btn = bmesh.new()
    for i in range(nseg):
        cx = -L / 2 + (i + 0.5) * sw
        for bx in (-sw * 0.24, sw * 0.24):
            for bz in (0.60, 0.82):
                bm_sphere(btn, 0.017, (cx + bx, 0.088, bz), scale=(1, 0.55, 1), subd=1)
    ob_b = finish(name + "_Buttons", btn, M['brass_dark'], "Furniture",
                  loc=loc, rot=(0, 0, rot_z))
    want_smooth(ob_b)
    return ob_w, ob_h, ob_b


def build_banquettes(M):
    x0, y0 = ROOM['x0'], ROOM['y0']

    # along the front glazing
    ax_a, ax_b = x0 + 0.72, 0.70
    make_banquette("BanquetteFront", ax_b - ax_a, ((ax_a + ax_b) * 0.5, y0, 0.0), 0.0, M)

    # along the side glazing (local +Y maps to world +X with rot_z = -90)
    ay_a, ay_b = -3.28, 0.95
    make_banquette("BanquetteSide", ay_b - ay_a, (x0, (ay_a + ay_b) * 0.5, 0.0),
                   math.radians(-90.0), M)

    # corner unit that ties the two runs together
    wood = bmesh.new()
    bm_span(wood, (x0 + 0.03, y0 + 0.03, 0.02), (x0 + 0.72, y0 + 0.72, 0.30))
    bm_span(wood, (x0, y0 + 0.72, 0.30), (x0 + 0.72, y0 + 0.82, 1.06))
    bm_span(wood, (x0 + 0.72, y0, 0.30), (x0 + 0.82, y0 + 0.72, 1.06))
    bm_span(wood, (x0 - 0.02, y0 - 0.02, 1.06), (x0 + 0.84, y0 + 0.84, 1.15))
    ob = finish("BanquetteCorner_Frame", wood, M['walnut'], "Furniture")
    bevel(ob, 0.008, 2)

    hide = bmesh.new()
    bm_span(hide, (x0 + 0.04, y0 + 0.04, 0.30), (x0 + 0.71, y0 + 0.71, 0.455))
    bm_span(hide, (x0 + 0.06, y0 + 0.60, 0.46), (x0 + 0.72, y0 + 0.72, 1.05))
    bm_span(hide, (x0 + 0.60, y0 + 0.06, 0.46), (x0 + 0.72, y0 + 0.60, 1.05))
    ob = finish("BanquetteCorner_Pads", hide, M['leather'], "Furniture")
    bevel(ob, 0.03, 3, angle=60)

    # scatter cushions
    cus = bmesh.new()
    bm_box(cus, (0.40, 0.16, 0.40), (x0 + 0.44, y0 + 0.50, 0.66),
           rot=(math.radians(12), 0, math.radians(-38)))
    bm_box(cus, (0.36, 0.14, 0.36), (x0 + 1.90, y0 + 0.28, 0.62),
           rot=(math.radians(10), 0, math.radians(6)))
    bm_box(cus, (0.36, 0.14, 0.36), (x0 + 0.28, -1.60, 0.62),
           rot=(math.radians(10), 0, math.radians(88)))
    ob = finish("Cushions", cus, M['fabric'], "Furniture")
    bevel(ob, 0.05, 4, angle=70)


# ------------------------------------------------------- tables, chairs, stools
def make_bistro_table(name, loc, M, r=0.42, top_h=0.735):
    bm = bmesh.new()
    bm_cyl(bm, r, r, 0.045, (0, 0, top_h - 0.0225), segs=48)
    ob_top = finish(name + "_Top", bm, M['marble'], "Furniture", loc=loc)
    bevel(ob_top, 0.008, 2)
    want_smooth(ob_top)

    bm = bmesh.new()
    bm_cyl(bm, 0.048, 0.042, top_h - 0.10, (0, 0, (top_h - 0.10) * 0.5 + 0.035), segs=20)
    bm_cyl(bm, 0.085, 0.075, 0.05, (0, 0, top_h - 0.075), segs=20)
    bm_cyl(bm, 0.245, 0.185, 0.035, (0, 0, 0.0175), segs=28)
    bm_cyl(bm, 0.15, 0.10, 0.045, (0, 0, 0.052), segs=24)
    ob_b = finish(name + "_Base", bm, M['blackmetal'], "Furniture", loc=loc)
    want_smooth(ob_b)
    return ob_top, ob_b


def make_square_table(name, loc, rot_z, M, w=0.78):
    bm = bmesh.new()
    bm_box(bm, (w, w, 0.05), (0, 0, 0.71))
    bm_box(bm, (w - 0.10, 0.05, 0.10), (0, 0, 0.63))
    for sx in (-1, 1):
        for sy in (-1, 1):
            bm_cyl(bm, 0.026, 0.020, 0.685,
                   (sx * (w / 2 - 0.06), sy * (w / 2 - 0.06), 0.3425), segs=14)
    ob = finish(name, bm, M['walnut'], "Furniture", loc=loc, rot=(0, 0, rot_z))
    bevel(ob, 0.006, 2)
    want_smooth(ob)
    return ob


def make_chair(name, loc, rot_z, M):
    """Bentwood style cafe chair; back faces local -Y (the chair looks +Y)."""
    bm = bmesh.new()
    bm_cyl(bm, 0.215, 0.205, 0.045, (0, 0.005, 0.4375), segs=28)          # seat
    legs = [(0.155, 0.155), (-0.155, 0.155), (0.155, -0.16), (-0.155, -0.16)]
    for lx, ly in legs:
        bm_cyl(bm, 0.020, 0.027, 0.415, (lx, ly, 0.2075), segs=12)
    for a, b in ((legs[0], legs[1]), (legs[2], legs[3]),
                 (legs[0], legs[2]), (legs[1], legs[3])):
        mid = ((a[0] + b[0]) * 0.5, (a[1] + b[1]) * 0.5)
        ln = math.hypot(b[0] - a[0], b[1] - a[1])
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        bm_cyl(bm, 0.013, 0.013, ln, (mid[0], mid[1], 0.155),
               rot=(0, math.radians(90), ang), segs=10)
    for sx in (-0.165, 0.165):                                            # back posts
        bm_cyl(bm, 0.023, 0.021, 0.53, (sx, -0.215, 0.705),
               rot=(math.radians(9), 0, 0), segs=12)
    bm_cyl(bm, 0.026, 0.026, 0.40, (0, -0.283, 0.945),
           rot=(0, math.radians(90), 0), segs=14)                          # crest rail
    bm_cyl(bm, 0.020, 0.020, 0.36, (0, -0.253, 0.735),
           rot=(0, math.radians(90), 0), segs=12)                          # mid rail
    bm_cyl(bm, 0.016, 0.016, 0.21, (0, -0.268, 0.840),
           rot=(math.radians(9), 0, 0), segs=10)                           # splat
    ob = finish(name, bm, M['walnut'], "Furniture", loc=loc, rot=(0, 0, rot_z))
    bevel(ob, 0.005, 2)
    want_smooth(ob)
    return ob


def make_stool(name, loc, rot_z, M, seat_h=0.72):
    bm = bmesh.new()
    bm_cyl(bm, 0.175, 0.170, 0.05, (0, 0, seat_h - 0.025), segs=28)
    ob_s = finish(name + "_Seat", bm, M['oak'], "Furniture", loc=loc, rot=(0, 0, rot_z))
    bevel(ob_s, 0.012, 3)
    want_smooth(ob_s)

    bm = bmesh.new()
    for i in range(4):
        a = math.radians(45 + i * 90)
        rr = 0.145
        bm_cyl(bm, 0.014, 0.019, seat_h - 0.03,
               (math.cos(a) * rr * 0.62, math.sin(a) * rr * 0.62, (seat_h - 0.03) * 0.5),
               rot=(math.radians(6) * math.sin(a), -math.radians(6) * math.cos(a), 0),
               segs=10)
    for i in range(4):
        a0 = math.radians(45 + i * 90)
        a1 = math.radians(135 + i * 90)
        rr = 0.135
        p0 = (math.cos(a0) * rr, math.sin(a0) * rr)
        p1 = (math.cos(a1) * rr, math.sin(a1) * rr)
        mid = ((p0[0] + p1[0]) * 0.5, (p0[1] + p1[1]) * 0.5)
        ln = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
        bm_cyl(bm, 0.011, 0.011, ln, (mid[0], mid[1], 0.24),
               rot=(0, math.radians(90), ang), segs=8)
    ob_l = finish(name + "_Frame", bm, M['blackmetal'], "Furniture",
                  loc=loc, rot=(0, 0, rot_z))
    want_smooth(ob_l)
    return ob_s, ob_l


def make_cup(name, loc, M, saucer=True):
    bm = bmesh.new()
    if saucer:
        bm_cyl(bm, 0.072, 0.058, 0.010, (0, 0, 0.005), segs=24)
    bm_cyl(bm, 0.038, 0.032, 0.062, (0, 0, 0.042), segs=22)
    bm_cyl(bm, 0.033, 0.033, 0.004, (0, 0, 0.068), segs=22)
    bm_cyl(bm, 0.010, 0.010, 0.055, (0.046, 0, 0.045),
           rot=(0, math.radians(90), 0), segs=8)
    ob = finish(name, bm, M['ceramic'], "Props", loc=loc)
    want_smooth(ob)
    return ob


def build_seating(M):
    x0, y0 = ROOM['x0'], ROOM['y0']
    tables = []

    # front window run
    for i, xt in enumerate((-3.90, -2.35, -0.80)):
        make_bistro_table("TableF%d" % i, (xt, y0 + 1.05, 0.0), M)
        tables.append((xt, y0 + 1.05))
        make_chair("ChairF%d" % i, (xt - 0.02, y0 + 1.92, 0.0), math.radians(178 + i * 3), M)
        make_cup("CupF%d" % i, (xt - 0.12 + 0.05 * i, y0 + 0.96, 0.735), M)

    # side window run
    for i, yt in enumerate((-1.90, -0.45)):
        make_bistro_table("TableS%d" % i, (x0 + 1.05, yt, 0.0), M, r=0.40)
        tables.append((x0 + 1.05, yt))
        make_chair("ChairS%d" % i, (x0 + 1.92, yt + 0.03, 0.0), math.radians(92 - i * 4), M)
        make_cup("CupS%d" % i, (x0 + 1.02, yt + 0.10, 0.735), M)

    # free standing tables in the room
    make_square_table("TableM0", (1.55, -2.30, 0.0), math.radians(6), M)
    make_chair("ChairM0a", (1.55, -3.02, 0.0), math.radians(4), M)
    make_chair("ChairM0b", (1.55, -1.58, 0.0), math.radians(184), M)
    make_chair("ChairM0c", (2.28, -2.30, 0.0), math.radians(272), M)
    make_cup("CupM0", (1.40, -2.20, 0.735), M)

    make_square_table("TableM1", (3.55, -1.35, 0.0), math.radians(-9), M)
    make_chair("ChairM1a", (3.55, -2.08, 0.0), math.radians(-6), M)
    make_chair("ChairM1b", (3.55, -0.62, 0.0), math.radians(176), M)
    make_cup("CupM1", (3.68, -1.28, 0.735), M)

    # window bar ledge with stools, on the unoccupied stretch of front glazing
    bm = bmesh.new()
    bm_span(bm, (0.95, y0 - 0.02, 1.00), (4.65, y0 + 0.40, 1.05))
    ob = finish("WindowBar", bm, M['oak'], "Furniture")
    bevel(ob, 0.01, 3)

    bm = bmesh.new()
    for xb in (1.30, 2.80, 4.30):
        bm_span(bm, (xb - 0.035, y0 + 0.02, SILL_Z + 0.02), (xb + 0.035, y0 + 0.34, 1.00))
    finish("WindowBarBrackets", bm, M['blackmetal'], "Furniture")

    for i, xb in enumerate((1.55, 2.80, 4.05)):
        make_stool("BarStoolW%d" % i, (xb, y0 + 0.92, 0.0),
                   math.radians(2 + i * 5), M, seat_h=0.70)
    make_cup("CupW0", (2.72, y0 + 0.20, 1.05), M)
    return tables


# --------------------------------------------------------------------- counter
def build_counter(M):
    cx0, cx1 = -1.70, 4.55
    cy0, cy1 = 2.55, 3.35            # front / back of the counter body
    top_z = 1.06

    body = bmesh.new()
    bm_span(body, (cx0, cy0 + 0.08, 0.0), (cx1, cy1, 0.11))                # plinth
    bm_span(body, (cx0, cy0, 0.11), (cx1, cy1, top_z - 0.06))              # carcass
    bm_span(body, (cx0, 1.60, 0.11), (cx0 + 0.75, cy0, top_z - 0.06))      # return wing
    bm_span(body, (cx0, 1.68, 0.0), (cx0 + 0.75, cy0, 0.11))
    ob = finish("CounterBody", body, M['wall'], "Counter")
    bevel(ob, 0.006, 2)

    # beadboard front
    slats = bmesh.new()
    n = int((cx1 - cx0) / 0.135)
    for i in range(n):
        xa = cx0 + 0.02 + i * 0.135
        bm_span(slats, (xa, cy0 - 0.022, 0.14), (xa + 0.105, cy0, top_z - 0.10))
    m = int((cy0 - 1.60) / 0.135)
    for i in range(m):
        ya = 1.62 + i * 0.135
        bm_span(slats, (cx0 - 0.022, ya, 0.14), (cx0, ya + 0.105, top_z - 0.10))
    bm_span(slats, (cx0 - 0.03, cy0 - 0.03, top_z - 0.10), (cx1, cy0, top_z - 0.06))
    ob = finish("CounterBeadboard", slats, M['oak'], "Counter")
    bevel(ob, 0.004, 2)

    top = bmesh.new()
    bm_span(top, (cx0 - 0.05, cy0 - 0.10, top_z - 0.06), (cx1 + 0.05, cy1 + 0.04, top_z))
    bm_span(top, (cx0 - 0.05, 1.55, top_z - 0.06), (cx0 + 0.80, cy0 - 0.10, top_z))
    ob = finish("CounterTop", top, M['marble'], "Counter")
    bevel(ob, 0.012, 3)

    build_pastry_case(M, x=-1.40, y=2.95, z=top_z)
    build_espresso(M, x=1.20, y=2.98, z=top_z)
    build_counter_props(M, top_z)
    build_back_bar(M)

    for i, xb in enumerate((2.15, 3.15, 4.15)):
        make_stool("BarStoolC%d" % i, (xb, 1.95, 0.0), math.radians(174 + i * 6),
                   M, seat_h=0.74)


def build_pastry_case(M, x, y, z):
    w, d, hh = 1.00, 0.62, 0.46
    frame = bmesh.new()
    for sx in (-1, 1):
        for sy in (-1, 1):
            bm_span(frame, (x + sx * w / 2 - sx * 0.022, y + sy * d / 2 - sy * 0.022, z),
                    (x + sx * w / 2, y + sy * d / 2, z + hh))
    for sz in (0.0, hh - 0.022):
        bm_span(frame, (x - w / 2, y - d / 2, z + sz),
                (x + w / 2, y - d / 2 + 0.022, z + sz + 0.022))
        bm_span(frame, (x - w / 2, y + d / 2 - 0.022, z + sz),
                (x + w / 2, y + d / 2, z + sz + 0.022))
        bm_span(frame, (x - w / 2, y - d / 2, z + sz),
                (x - w / 2 + 0.022, y + d / 2, z + sz + 0.022))
        bm_span(frame, (x + w / 2 - 0.022, y - d / 2, z + sz),
                (x + w / 2, y + d / 2, z + sz + 0.022))
    bm_span(frame, (x - w / 2, y - d / 2, z + 0.20),
            (x + w / 2, y - d / 2 + 0.018, z + 0.222))
    ob = finish("CaseFrame", frame, M['brass'], "Counter")
    bevel(ob, 0.004, 2)

    glass = bmesh.new()
    bm_span(glass, (x - w / 2 + 0.02, y - d / 2 + 0.006, z + 0.02),
            (x + w / 2 - 0.02, y - d / 2 + 0.016, z + hh - 0.02))
    bm_span(glass, (x - w / 2 + 0.02, y + d / 2 - 0.016, z + 0.02),
            (x + w / 2 - 0.02, y + d / 2 - 0.006, z + hh - 0.02))
    bm_span(glass, (x - w / 2 + 0.006, y - d / 2 + 0.02, z + 0.02),
            (x - w / 2 + 0.016, y + d / 2 - 0.02, z + hh - 0.02))
    bm_span(glass, (x + w / 2 - 0.016, y - d / 2 + 0.02, z + 0.02),
            (x + w / 2 - 0.006, y + d / 2 - 0.02, z + hh - 0.02))
    bm_span(glass, (x - w / 2 + 0.02, y - d / 2 + 0.02, z + hh - 0.016),
            (x + w / 2 - 0.02, y + d / 2 - 0.02, z + hh - 0.006))
    finish("CaseGlass", glass, M['glass_case'], "Counter")

    shelves = bmesh.new()
    bm_span(shelves, (x - w / 2 + 0.03, y - d / 2 + 0.03, z + 0.20),
            (x + w / 2 - 0.03, y + d / 2 - 0.03, z + 0.214))
    bm_span(shelves, (x - w / 2 + 0.03, y - d / 2 + 0.03, z + 0.012),
            (x + w / 2 - 0.03, y + d / 2 - 0.03, z + 0.026))
    finish("CaseShelves", shelves, M['glass_case'], "Counter")

    plates = bmesh.new()
    goods = bmesh.new()
    icing = bmesh.new()
    for row, sz in enumerate((0.026, 0.214)):
        for i in range(3):
            px = x - 0.32 + i * 0.32
            py = y + (-0.10 if row == 0 else 0.06)
            bm_cyl(plates, 0.125, 0.115, 0.010, (px, py, z + sz + 0.005), segs=24)
            if (i + row) % 2 == 0:
                for k in range(3):
                    a = math.radians(120 * k + 25 * row)
                    bm_sphere(goods, 0.048,
                              (px + math.cos(a) * 0.05, py + math.sin(a) * 0.05,
                               z + sz + 0.045),
                              scale=(1.0, 1.0, 0.62), subd=2)
            else:
                bm_cyl(goods, 0.105, 0.100, 0.075, (px, py, z + sz + 0.05), segs=22)
                bm_cyl(icing, 0.104, 0.104, 0.014, (px, py, z + sz + 0.094), segs=22)
    ob = finish("CasePlates", plates, M['ceramic'], "Counter")
    want_smooth(ob)
    ob = finish("CaseGoods", goods, M['pastry'], "Counter")
    want_smooth(ob)
    ob = finish("CaseIcing", icing, M['icing'], "Counter")
    want_smooth(ob)


def build_espresso(M, x, y, z):
    chrome = bmesh.new()
    bm_span(chrome, (x - 0.36, y - 0.26, z), (x + 0.36, y + 0.26, z + 0.30))
    bm_span(chrome, (x - 0.33, y - 0.24, z + 0.30), (x + 0.33, y + 0.24, z + 0.44))
    bm_span(chrome, (x - 0.36, y - 0.28, z + 0.44), (x + 0.36, y + 0.28, z + 0.48))
    for gx in (-0.18, 0.18):                                    # group heads
        bm_cyl(chrome, 0.052, 0.046, 0.10, (x + gx, y - 0.20, z + 0.25), segs=18)
        bm_cyl(chrome, 0.036, 0.040, 0.055, (x + gx, y - 0.20, z + 0.175), segs=16)
    for sx in (-0.33, 0.33):                                    # steam wands
        bm_cyl(chrome, 0.010, 0.008, 0.30, (x + sx, y - 0.14, z + 0.20),
               rot=(math.radians(18), 0, 0), segs=10)
        bm_cyl(chrome, 0.030, 0.026, 0.055, (x + sx, y - 0.06, z + 0.35), segs=12)
    bm_cyl(chrome, 0.055, 0.055, 0.018, (x - 0.02, y - 0.255, z + 0.38),
           rot=(math.radians(90), 0, 0), segs=20)               # pressure gauge
    ob = finish("EspressoBody", chrome, M['chrome'], "Counter")
    bevel(ob, 0.008, 3)
    want_smooth(ob)

    blk = bmesh.new()
    for gx in (-0.18, 0.18):
        bm_cyl(blk, 0.022, 0.020, 0.16, (x + gx, y - 0.30, z + 0.155),
               rot=(math.radians(96), 0, 0), segs=12)
        bm_sphere(blk, 0.026, (x + gx, y - 0.385, z + 0.145), subd=2)
    for lx in (-0.28, -0.09, 0.09, 0.28):
        bm_span(blk, (x + lx - 0.03, y - 0.265, z + 0.31),
                (x + lx + 0.03, y - 0.22, z + 0.335))
    ob = finish("EspressoTrim", blk, M['blackmetal'], "Counter")
    want_smooth(ob)

    dial = bmesh.new()
    bm_cyl(dial, 0.045, 0.045, 0.004, (x - 0.02, y - 0.266, z + 0.38),
           rot=(math.radians(90), 0, 0), segs=20)
    ob = finish("EspressoGauge", dial, M['ceramic'], "Counter")
    want_smooth(ob)

    # grinder beside the machine
    gr = bmesh.new()
    gx = x + 0.60
    bm_span(gr, (gx - 0.10, y - 0.13, z), (gx + 0.10, y + 0.13, z + 0.34))
    bm_span(gr, (gx - 0.075, y - 0.15, z + 0.06), (gx + 0.075, y - 0.11, z + 0.16))
    ob = finish("Grinder", gr, M['blackmetal'], "Counter")
    bevel(ob, 0.008, 2)

    hop = bmesh.new()
    bm_cyl(hop, 0.075, 0.105, 0.22, (gx, y, z + 0.45), segs=24)
    ob = finish("GrinderHopper", hop, M['glass_case'], "Counter")
    want_smooth(ob)

    beans = bmesh.new()
    for i in range(40):
        a = random.uniform(0, math.tau)
        rr = random.uniform(0.0, 0.07)
        bm_sphere(beans, 0.010,
                  (gx + math.cos(a) * rr, y + math.sin(a) * rr,
                   z + 0.40 + random.uniform(0.0, 0.06)),
                  scale=(1.0, 0.7, 0.6), rot=(0, 0, a), subd=1)
    ob = finish("CoffeeBeans", beans, M['walnut'], "Counter")
    want_smooth(ob)


def build_counter_props(M, top_z):
    # stacked cups
    bm = bmesh.new()
    for i, (sx, sy) in enumerate(((2.35, 3.05), (2.58, 3.05), (2.35, 2.82))):
        for k in range(4 - (i % 2)):
            bm_cyl(bm, 0.038 + 0.002 * k, 0.033, 0.062,
                   (sx, sy, top_z + 0.03 + k * 0.028), segs=20)
    bm_cyl(bm, 0.085, 0.085, 0.012, (3.05, 2.98, top_z + 0.006), segs=24)
    ob = finish("CupStacks", bm, M['ceramic'], "Counter")
    want_smooth(ob)

    # till on a stand
    bm = bmesh.new()
    bm_span(bm, (3.55, 2.80, top_z), (3.95, 3.16, top_z + 0.045))
    bm_box(bm, (0.24, 0.03, 0.19), (3.75, 2.92, top_z + 0.15),
           rot=(math.radians(-16), 0, 0))
    bm_cyl(bm, 0.028, 0.028, 0.14, (3.75, 3.02, top_z + 0.10), segs=12)
    ob = finish("Register", bm, M['blackmetal'], "Counter")
    bevel(ob, 0.006, 2)

    bm = bmesh.new()
    bm_cyl(bm, 0.065, 0.070, 0.16, (4.25, 2.92, top_z + 0.08), segs=24)
    ob = finish("TipJar", bm, M['glass_case'], "Counter")
    want_smooth(ob)

    bm = bmesh.new()
    bm_span(bm, (-0.62, 2.82, top_z), (-0.34, 3.10, top_z + 0.10))
    bm_span(bm, (-0.60, 2.84, top_z + 0.10), (-0.36, 3.08, top_z + 0.12))
    ob = finish("NapkinCaddy", bm, M['oak'], "Counter")
    bevel(ob, 0.005, 2)

    bm = bmesh.new()
    bm_cyl(bm, 0.075, 0.070, 0.24, (-0.15, 2.95, top_z + 0.12), segs=24)
    bm_cyl(bm, 0.078, 0.078, 0.012, (-0.15, 2.95, top_z + 0.246), segs=24)
    ob = finish("WaterJug", bm, M['glass_case'], "Counter")
    want_smooth(ob)


def build_back_bar(M):
    y1 = ROOM['y1']
    yf = y1 - 0.34                      # front face of the shelf unit

    bm = bmesh.new()
    for xp in (-1.60, 0.10, 1.75):
        bm_span(bm, (xp - 0.03, yf, 0.95), (xp + 0.03, y1, 2.62))
    for zp in (1.30, 1.72, 2.14, 2.56):
        bm_span(bm, (-1.63, yf, zp - 0.035), (1.78, y1, zp))
    bm_span(bm, (-1.63, yf, 0.95), (1.78, y1, 1.02))
    ob = finish("BackBarShelves", bm, M['oak'], "Counter")
    bevel(ob, 0.006, 2)

    # crockery, jars and bags on the shelves
    cer = bmesh.new()
    glassy = bmesh.new()
    bags = bmesh.new()
    for zp in (1.30, 1.72, 2.14):
        x = -1.52
        while x < 1.66:
            pick = random.random()
            if pick < 0.34:
                for k in range(random.randint(2, 4)):
                    bm_cyl(cer, 0.042, 0.036, 0.066,
                           (x + 0.05, y1 - 0.17, zp + 0.033 + k * 0.03), segs=18)
                x += 0.16
            elif pick < 0.62:
                r = random.uniform(0.045, 0.062)
                hh = random.uniform(0.16, 0.24)
                bm_cyl(glassy, r, r * 0.92, hh,
                       (x + r + 0.01, y1 - 0.17, zp + hh * 0.5), segs=20)
                bm_cyl(glassy, r * 0.35, r * 0.30, 0.05,
                       (x + r + 0.01, y1 - 0.17, zp + hh + 0.02), segs=12)
                x += r * 2 + 0.05
            else:
                w = random.uniform(0.11, 0.16)
                bm_box(bags, (w, 0.10, 0.26), (x + w / 2, y1 - 0.18, zp + 0.13),
                       rot=(0, 0, random.uniform(-0.10, 0.10)))
                x += w + 0.05
    ob = finish("BackBarCrockery", cer, M['ceramic'], "Counter")
    want_smooth(ob)
    ob = finish("BackBarJars", glassy, M['glass_case'], "Counter")
    want_smooth(ob)
    ob = finish("BackBarBags", bags, M['fabric'], "Counter")
    bevel(ob, 0.008, 2)

    # chalkboard menu over the counter
    bm = bmesh.new()
    bm_span(bm, (2.10, y1 - 0.06, 1.32), (4.55, y1 - 0.045, 2.58))
    finish("MenuBoard", bm, M['chalkboard'], "Counter")

    bm = bmesh.new()
    bm_span(bm, (2.02, y1 - 0.09, 1.24), (4.63, y1 - 0.03, 1.32))
    bm_span(bm, (2.02, y1 - 0.09, 2.58), (4.63, y1 - 0.03, 2.66))
    bm_span(bm, (2.02, y1 - 0.09, 1.24), (2.10, y1 - 0.03, 2.66))
    bm_span(bm, (4.55, y1 - 0.09, 1.24), (4.63, y1 - 0.03, 2.66))
    ob = finish("MenuFrame", bm, M['walnut'], "Counter")
    bevel(ob, 0.006, 2)

    # chalk "writing": short bars in two columns
    bm = bmesh.new()
    for col, cx in enumerate((2.30, 3.55)):
        z = 2.40
        bm_span(bm, (cx, y1 - 0.052, z), (cx + 0.62, y1 - 0.048, z + 0.035))
        z -= 0.16
        for row in range(6):
            w = random.uniform(0.34, 0.78)
            bm_span(bm, (cx, y1 - 0.052, z), (cx + w, y1 - 0.048, z + 0.018))
            bm_span(bm, (cx + 0.86, y1 - 0.052, z), (cx + 0.98, y1 - 0.048, z + 0.018))
            z -= 0.135
    finish("MenuChalk", bm, M['chalk'], "Counter")


# ------------------------------------------------------------ pendant lighting
def make_pendant(name, x, y, z_bottom, M, shade_r=0.17, energy=22.0, cool=False):
    ceil_z = ROOM['h']
    shade_h = shade_r * 0.95
    top_z = z_bottom + shade_h

    bm = bmesh.new()
    bm_cyl(bm, shade_r, shade_r * 0.26, shade_h, (0, 0, shade_h * 0.5), segs=40, caps=False)
    ob = finish(name + "_Shade", bm, M['brass'], "Lighting", loc=(x, y, z_bottom))
    md = ob.modifiers.new("Solidify", 'SOLIDIFY')
    md.thickness = 0.006
    md.offset = 0.0
    want_smooth(ob)

    bm = bmesh.new()
    bm_cyl(bm, 0.008, 0.008, ceil_z - top_z, (0, 0, (ceil_z - top_z) * 0.5), segs=8)
    bm_cyl(bm, 0.055, 0.05, 0.03, (0, 0, ceil_z - top_z - 0.015), segs=20)
    bm_cyl(bm, 0.032, 0.030, 0.075, (0, 0, -0.03), segs=16)          # lamp holder
    ob = finish(name + "_Cord", bm, M['brass_dark'], "Lighting", loc=(x, y, top_z))
    want_smooth(ob)

    bm = bmesh.new()
    bm_sphere(bm, shade_r * 0.34, (0, 0, z_bottom - shade_r * 0.14),
              scale=(1.0, 1.0, 1.25), subd=3)
    ob = finish(name + "_Bulb", bm, M['bulb'], "Lighting", loc=(x, y, 0.0))
    want_smooth(ob)

    ld = bpy.data.lights.new(name + "_Light", 'POINT')
    ld.energy = energy
    ld.color = (0.95, 0.93, 0.90) if cool else (0.86, 0.72, 0.52)
    ld.shadow_soft_size = 0.07
    lo = bpy.data.objects.new(name + "_Light", ld)
    lo.location = (x, y, z_bottom - shade_r * 0.16)
    link(lo, "Lighting")
    return lo


def build_pendants(M, tables):
    # one pendant over every window side table
    for i, (tx, ty) in enumerate(tables):
        make_pendant("PendT%d" % i, tx, ty, 1.86, M, shade_r=0.175, energy=24.0)

    # three over the service counter
    for i, xp in enumerate((-1.05, 0.90, 2.85)):
        make_pendant("PendC%d" % i, xp, 2.92, 2.02, M, shade_r=0.21, energy=32.0)

    # small pendants over the window bar
    for i, xp in enumerate((1.55, 2.80, 4.05)):
        make_pendant("PendW%d" % i, xp, ROOM['y0'] + 0.22, 2.18, M,
                     shade_r=0.115, energy=14.0)

    # discreet fill over the middle tables
    make_pendant("PendM0", 1.55, -2.30, 2.00, M, shade_r=0.175, energy=22.0)
    make_pendant("PendM1", 3.55, -1.35, 2.00, M, shade_r=0.175, energy=22.0)


# ----------------------------------------------------------------------- props
def make_plant(name, loc, M, scale=1.0, leaves=26):
    bm = bmesh.new()
    bm_cyl(bm, 0.17 * scale, 0.135 * scale, 0.34 * scale, (0, 0, 0.17 * scale), segs=26)
    bm_cyl(bm, 0.185 * scale, 0.175 * scale, 0.05 * scale, (0, 0, 0.325 * scale), segs=26)
    ob = finish(name + "_Pot", bm, M['terracotta'], "Props", loc=loc)
    want_smooth(ob)

    bm = bmesh.new()
    bm_cyl(bm, 0.155 * scale, 0.15 * scale, 0.03 * scale, (0, 0, 0.315 * scale), segs=20)
    ob = finish(name + "_Soil", bm, M['soil'], "Props", loc=loc)
    want_smooth(ob)

    bm = bmesh.new()
    trunk_top = 0.68 * scale
    bm_cyl(bm, 0.028 * scale, 0.018 * scale, trunk_top - 0.30 * scale,
           (0, 0, (trunk_top + 0.30 * scale) * 0.5), segs=10)
    for i in range(leaves):
        a = random.uniform(0, math.tau)
        rr = random.uniform(0.06, 0.42) * scale
        zz = trunk_top + random.uniform(-0.16, 0.46) * scale
        bm_sphere(bm, random.uniform(0.09, 0.15) * scale,
                  (math.cos(a) * rr, math.sin(a) * rr, zz),
                  scale=(1.0, 0.42, 0.28),
                  rot=(random.uniform(-0.5, 0.5), random.uniform(-0.7, 0.7), a),
                  subd=1)
    ob = finish(name + "_Foliage", bm, M['leaf'], "Props", loc=loc)
    want_smooth(ob)


def build_props(M):
    x0, x1, y0, y1 = ROOM['x0'], ROOM['x1'], ROOM['y0'], ROOM['y1']

    make_plant("PlantCorner", (x1 - 0.55, y0 + 0.75, 0.0), M, scale=1.35, leaves=34)
    make_plant("PlantDoor", (x0 + 0.55, y1 - 0.95, 0.0), M, scale=1.0, leaves=24)
    make_plant("PlantLedge", (3.45, y0 + 0.20, 1.05), M, scale=0.42, leaves=12)
    make_plant("PlantCounter", (-1.62, 1.80, 1.06), M, scale=0.40, leaves=12)

    # framed pictures on the wainscoted right wall
    fr = bmesh.new()
    art = bmesh.new()
    for yp, zp, w, hh in ((-2.55, 1.85, 0.52, 0.66),
                          (-1.75, 2.02, 0.42, 0.34),
                          (-1.72, 1.55, 0.42, 0.42),
                          (-0.85, 1.90, 0.60, 0.46)):
        bm_span(fr, (x1 - 0.07, yp - w / 2, zp - hh / 2), (x1 - 0.03, yp + w / 2, zp + hh / 2))
        bm_span(art, (x1 - 0.072, yp - w / 2 + 0.04, zp - hh / 2 + 0.04),
                (x1 - 0.066, yp + w / 2 - 0.04, zp + hh / 2 - 0.04))
    ob = finish("PictureFrames", fr, M['brass_dark'], "Props")
    bevel(ob, 0.004, 2)
    finish("PictureArt", art, M['paper'], "Props")

    # coat hook rail beside the door
    bm = bmesh.new()
    bm_span(bm, (x0 + 0.02, y1 - 1.95, 1.62), (x0 + 0.07, y1 - 0.55, 1.74))
    ob = finish("CoatRail", bm, M['walnut'], "Props")
    bevel(ob, 0.005, 2)

    bm = bmesh.new()
    for i in range(5):
        yp = y1 - 1.80 + i * 0.30
        bm_cyl(bm, 0.014, 0.014, 0.11, (x0 + 0.10, yp, 1.68),
               rot=(0, math.radians(90), 0), segs=10)
        bm_sphere(bm, 0.022, (x0 + 0.155, yp, 1.68), subd=2)
    ob = finish("CoatHooks", bm, M['brass'], "Props")
    want_smooth(ob)

    # newspaper on the window bar, a book on a table
    bm = bmesh.new()
    bm_box(bm, (0.30, 0.42, 0.012), (1.62, y0 + 0.19, 1.062), rot=(0, 0, math.radians(9)))
    bm_box(bm, (0.16, 0.23, 0.030), (-2.30, y0 + 1.05, 0.752), rot=(0, 0, math.radians(-24)))
    ob = finish("Reading", bm, M['paper'], "Props")
    bevel(ob, 0.003, 1)

    # bud vases on the window tables
    bm = bmesh.new()
    for vx, vy in ((-3.72, y0 + 1.16), (-0.62, y0 + 1.16), (x0 + 1.18, -0.32)):
        bm_cyl(bm, 0.032, 0.026, 0.14, (vx, vy, 0.805), segs=16)
    ob = finish("Vases", bm, M['glass_case'], "Props")
    want_smooth(ob)

    bm = bmesh.new()
    for vx, vy in ((-3.72, y0 + 1.16), (-0.62, y0 + 1.16), (x0 + 1.18, -0.32)):
        bm_cyl(bm, 0.006, 0.005, 0.22, (vx, vy, 0.98), rot=(0.06, 0.04, 0), segs=6)
        bm_sphere(bm, 0.030, (vx + 0.012, vy + 0.008, 1.09), scale=(1, 1, 0.7), subd=1)
    ob = finish("VaseFlowers", bm, M['fabric'], "Props")
    want_smooth(ob)


# -------------------------------------------------------------------- lighting
def build_world():
    world = bpy.data.worlds.new("CafeWorld")
    bpy.context.scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputWorld")
    out.location = (300, 0)
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.location = (80, 0)
    bg.inputs["Strength"].default_value = 1.0
    sky = nt.nodes.new("ShaderNodeTexSky")
    sky.location = (-180, 0)
    try:
        sky.sky_type = 'NISHITA'
        sky.sun_elevation = math.radians(24.0)
        sky.sun_rotation = math.radians(212.0)
        sky.sun_intensity = 0.5
        sky.altitude = 30.0
        sky.air_density = 1.1
        sky.dust_density = 1.6
    except Exception:
        pass
    nt.links.new(sky.outputs[0], bg.inputs["Color"])
    nt.links.new(bg.outputs[0], out.inputs["Surface"])


def build_lighting():
    x0, y0 = ROOM['x0'], ROOM['y0']

    ld = bpy.data.lights.new("Sun", 'SUN')
    ld.energy = 2.6
    ld.angle = math.radians(1.6)
    ld.color = (1.0, 0.93, 0.82)
    sun = bpy.data.objects.new("Sun", ld)
    sun.rotation_euler = (math.radians(56.0), math.radians(6.0), math.radians(-142.0))
    sun.location = (-12.0, -12.0, 12.0)
    link(sun, "Lighting")

    # sky fill pushed through each glazed facade
    ld = bpy.data.lights.new("SkyFillFront", 'AREA')
    ld.shape = 'RECTANGLE'
    ld.size = 9.4
    ld.size_y = 2.4
    ld.energy = 220.0
    ld.color = (0.78, 0.86, 1.0)
    ob = bpy.data.objects.new("SkyFillFront", ld)
    ob.location = (0.0, y0 - 0.55, 1.70)
    ob.rotation_euler = (math.radians(90.0), 0.0, 0.0)
    link(ob, "Lighting")

    ld = bpy.data.lights.new("SkyFillSide", 'AREA')
    ld.shape = 'RECTANGLE'
    ld.size = 5.6
    ld.size_y = 2.4
    ld.energy = 160.0
    ld.color = (0.78, 0.86, 1.0)
    ob = bpy.data.objects.new("SkyFillSide", ld)
    ob.location = (x0 - 0.55, -1.2, 1.70)
    ob.rotation_euler = (0.0, math.radians(-90.0), 0.0)
    link(ob, "Lighting")

    # warm wash over the back bar shelving
    ld = bpy.data.lights.new("BackBarWash", 'AREA')
    ld.shape = 'RECTANGLE'
    ld.size = 3.2
    ld.size_y = 0.4
    ld.energy = 26.0
    ld.color = (1.0, 0.80, 0.58)
    ob = bpy.data.objects.new("BackBarWash", ld)
    ob.location = (0.1, ROOM['y1'] - 0.30, 2.90)
    ob.rotation_euler = (math.radians(-14.0), 0.0, 0.0)
    link(ob, "Lighting")

    # soft bounce keeping the room's shadow side readable
    ld = bpy.data.lights.new("RoomBounce", 'AREA')
    ld.shape = 'RECTANGLE'
    ld.size = 6.0
    ld.size_y = 4.0
    ld.energy = 45.0
    ld.color = (1.0, 0.94, 0.86)
    ob = bpy.data.objects.new("RoomBounce", ld)
    ob.location = (1.6, 0.2, ROOM['h'] - 0.12)
    link(ob, "Lighting")


# ---------------------------------------------------------------------- camera
def build_camera():
    cd = bpy.data.cameras.new("CafeCam")
    cd.lens = 22.0
    cd.sensor_width = 36.0
    cd.clip_start = 0.02
    cd.clip_end = 200.0
    cam = bpy.data.objects.new("CafeCam", cd)
    cam.location = (4.30, 3.05, 1.62)
    link(cam, "Camera")

    target = Vector((-3.10, -2.30, 1.05))
    d = target - cam.location
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()

    cd.dof.use_dof = True
    cd.dof.focus_distance = d.length
    cd.dof.aperture_fstop = 3.5

    bpy.context.scene.camera = cam
    return cam


# ------------------------------------------------------------------------ main
def main():
    reset_scene()
    M = build_materials()
    build_world()
    build_shell(M)
    build_facades(M)
    build_exterior(M)
    build_banquettes(M)
    tables = build_seating(M)
    build_counter(M)
    build_pendants(M, tables)
    build_props(M)
    build_lighting()
    build_camera()
    apply_auto_smooth()

    meshes = [o for o in bpy.data.objects if o.type == 'MESH']
    faces = sum(len(o.data.polygons) for o in meshes)
    lights = len([o for o in bpy.data.objects if o.type == 'LIGHT'])
    print("Corner cafe built: %d mesh objects, %d faces, %d lights" %
          (len(meshes), faces, lights))


if __name__ == "__main__":
    main()
