"""claude-026 : a wooden pallet carrying six labeled crates (Blender 4.5 LTS)."""

import bpy, bmesh, math, random
from mathutils import Vector, Matrix, Euler

TAU = math.pi * 2.0

# --------------------------------------------------------------------------- #
#  helpers
# --------------------------------------------------------------------------- #

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = 'METRIC'
    sc.unit_settings.length_unit = 'METERS'
    sc.render.engine = 'CYCLES'
    if hasattr(sc, "cycles"):
        sc.cycles.samples = 96
        sc.cycles.use_denoising = True
    sc.render.resolution_x = 1600
    sc.render.resolution_y = 1100
    world = bpy.data.worlds.new("World")
    sc.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.06, 0.065, 0.08, 1.0)
    bg.inputs["Strength"].default_value = 1.0
    return sc


def link(obj):
    bpy.context.scene.collection.objects.link(obj)
    return obj


def attach(child, parent):
    child.parent = parent
    child.matrix_parent_inverse = Matrix.Identity(4)
    return child


def _M(size, loc, rot, pre=None):
    m = (Matrix.Translation(Vector(loc))
         @ Euler(rot, 'XYZ').to_matrix().to_4x4()
         @ Matrix.Diagonal(Vector(size).to_4d()))
    return (pre @ m) if pre is not None else m


def add_box(bm, size, loc=(0.0, 0.0, 0.0), rot=(0.0, 0.0, 0.0), pre=None):
    bmesh.ops.create_cube(bm, size=1.0, matrix=_M(size, loc, rot, pre), calc_uvs=True)


def add_cyl(bm, radius, depth, loc=(0.0, 0.0, 0.0), rot=(0.0, 0.0, 0.0),
            segments=24, r2=None, caps=True, pre=None):
    m = _M((1.0, 1.0, 1.0), loc, rot, pre)
    before = set(bm.faces)
    bmesh.ops.create_cone(bm, cap_ends=caps, cap_tris=False, segments=segments,
                          radius1=radius, radius2=(radius if r2 is None else r2),
                          depth=depth, matrix=m, calc_uvs=True)
    axis = (m.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized()
    for f in bm.faces:
        if f not in before and abs(f.normal.normalized().dot(axis)) < 0.85:
            f.smooth = True


def finish(name, bm, mat=None, loc=(0.0, 0.0, 0.0), rot=(0.0, 0.0, 0.0),
           bevel=0.0, bevel_seg=2):
    if bevel > 0.0:
        geom = list(bm.verts) + list(bm.edges) + list(bm.faces)
        bmesh.ops.bevel(bm, geom=geom, offset=bevel, offset_type='OFFSET',
                        segments=bevel_seg, profile=0.5, affect='EDGES',
                        clamp_overlap=True)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.validate()
    obj = bpy.data.objects.new(name, me)
    obj.location = loc
    obj.rotation_euler = rot
    if mat is not None:
        me.materials.append(mat)
    return link(obj)


def mat_simple(name, color, rough=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    b = mat.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metallic
    return mat


def mat_noisy(name, c1, c2, scale=8.0, detail=6.0, rough=0.65,
              mapping_scale=(1.0, 1.0, 1.0), bump=0.15, distortion=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    b = nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    coord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = mapping_scale
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = scale
    noise.inputs["Detail"].default_value = detail
    if "Distortion" in noise.inputs:
        noise.inputs["Distortion"].default_value = distortion
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.34
    ramp.color_ramp.elements[0].color = (c1[0], c1[1], c1[2], 1.0)
    ramp.color_ramp.elements[1].position = 0.66
    ramp.color_ramp.elements[1].color = (c2[0], c2[1], c2[2], 1.0)
    bumpn = nodes.new("ShaderNodeBump")
    bumpn.inputs["Strength"].default_value = bump
    links.new(coord.outputs["Object"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    links.new(noise.outputs["Fac"], bumpn.inputs["Height"])
    links.new(bumpn.outputs["Normal"], b.inputs["Normal"])
    return mat


def text_obj(name, body, size, loc, rot, mat, extrude=0.0012):
    cu = bpy.data.curves.new(name, type='FONT')
    cu.body = body
    cu.size = size
    cu.align_x = 'CENTER'
    cu.align_y = 'CENTER'
    cu.extrude = extrude
    cu.space_line = 0.85
    obj = bpy.data.objects.new(name, cu)
    obj.location = loc
    obj.rotation_euler = rot
    if mat is not None:
        cu.materials.append(mat)
    return link(obj)


def add_camera(loc, target, lens=50.0):
    cd = bpy.data.cameras.new("Camera")
    cd.lens = lens
    obj = bpy.data.objects.new("Camera", cd)
    obj.location = loc
    obj.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    link(obj)
    bpy.context.scene.camera = obj
    return obj


def add_area(name, loc, target, energy, size=2.0, color=(1.0, 1.0, 1.0)):
    ld = bpy.data.lights.new(name, type='AREA')
    ld.energy = energy
    ld.size = size
    ld.color = color
    obj = bpy.data.objects.new(name, ld)
    obj.location = loc
    obj.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return link(obj)


# --------------------------------------------------------------------------- #
#  pallet
# --------------------------------------------------------------------------- #

PAL_L, PAL_W = 1.20, 0.80
BOT_T, STR_H, TOP_T = 0.020, 0.100, 0.018
DECK_Z = BOT_T + STR_H + TOP_T          # 0.138 -> top of pallet
TOP_XS = [-PAL_L / 2 + 0.06 + i * ((PAL_L - 0.12) / 6.0) for i in range(7)]
STR_YS = (-PAL_W / 2 + 0.05, 0.0, PAL_W / 2 - 0.05)


def build_pallet(wood, nail_mat):
    bm = bmesh.new()
    for x in (-PAL_L / 2 + 0.075, 0.0, PAL_L / 2 - 0.075):      # bottom boards
        add_box(bm, (0.145, PAL_W, BOT_T), (x, 0.0, BOT_T * 0.5))
    for y in STR_YS:                                            # stringers
        add_box(bm, (PAL_L, 0.095, STR_H), (0.0, y, BOT_T + STR_H * 0.5))
    ztop = BOT_T + STR_H + TOP_T * 0.5
    for x in TOP_XS:                                            # top deck
        add_box(bm, (0.120, PAL_W, TOP_T), (x, 0.0, ztop))
    pallet = finish("Pallet", bm, wood, bevel=0.0025, bevel_seg=2)

    nb = bmesh.new()
    for x in TOP_XS:
        for y in STR_YS:
            add_cyl(nb, 0.0042, 0.005, (x, y, DECK_Z - 0.0015), segments=8)
    for x in (-PAL_L / 2 + 0.075, 0.0, PAL_L / 2 - 0.075):
        for y in STR_YS:
            add_cyl(nb, 0.0042, 0.005, (x, y, 0.0018), segments=8)
    attach(finish("PalletNails", nb, nail_mat), pallet)
    return pallet


# --------------------------------------------------------------------------- #
#  crate
# --------------------------------------------------------------------------- #

def build_crate(name, center, size, rz, wood, nail_mat):
    w, d, h = size
    slat_t, post = 0.014, 0.038
    bm = bmesh.new()
    for sx in (-1, 1):
        for sy in (-1, 1):
            add_box(bm, (post, post, h),
                    (sx * (w * 0.5 - post * 0.5), sy * (d * 0.5 - post * 0.5), h * 0.5))
    courses = (0.058, h * 0.5, h - 0.058)
    for sy in (-1, 1):
        for z in courses:
            add_box(bm, (w, slat_t, 0.088), (0.0, sy * (d * 0.5 - slat_t * 0.5), z))
    for sx in (-1, 1):
        for z in courses:
            add_box(bm, (slat_t, d - 2.0 * post, 0.088),
                    (sx * (w * 0.5 - slat_t * 0.5), 0.0, z))
    add_box(bm, (w, 0.070, 0.022), (0.0, -d * 0.5 + 0.05, 0.011))       # skids
    add_box(bm, (w, 0.070, 0.022), (0.0, d * 0.5 - 0.05, 0.011))
    for i in range(4):                                                  # floor slats
        y = -d * 0.5 + 0.055 + i * ((d - 0.11) / 3.0)
        add_box(bm, (w - 2.0 * post, 0.078, 0.016), (0.0, y, 0.030))
    for i in range(4):                                                  # lid slats
        y = -d * 0.5 + 0.050 + i * ((d - 0.10) / 3.0)
        add_box(bm, (w, 0.086, 0.018), (0.0, y, h - 0.009))
    crate = finish(name, bm, wood, loc=center, rot=(0.0, 0.0, rz),
                   bevel=0.0022, bevel_seg=1)

    nb = bmesh.new()
    for sx in (-1, 1):
        for sy in (-1, 1):
            for z in courses:
                add_cyl(nb, 0.0035, 0.006, (sx * (w * 0.5 - post * 0.4),
                                            sy * (d * 0.5 - 0.004), z),
                        (math.pi * 0.5, 0.0, 0.0), segments=8)
    for i in range(4):
        y = -d * 0.5 + 0.050 + i * ((d - 0.10) / 3.0)
        for sx in (-1, 1):
            add_cyl(nb, 0.0035, 0.006, (sx * (w * 0.5 - post * 0.4), y, h - 0.0015),
                    segments=8)
    attach(finish(name + "_Nails", nb, nail_mat), crate)
    return crate


def label_crate(crate, size, side, code, detail, paper, ink, ink_red):
    """side = -1 -> label on the -Y face, +1 -> label on the +Y face."""
    w, d, h = size
    y_face = side * (d * 0.5)
    face_rot = (math.pi * 0.5, 0.0, 0.0 if side < 0 else math.pi)
    lb = bmesh.new()
    add_box(lb, (0.205, 0.0022, 0.150), (0.0, y_face + side * 0.0018, h * 0.55))
    attach(finish(crate.name + "_LabelCard", lb, paper), crate)
    attach(text_obj(crate.name + "_Code", code, 0.042,
                    (0.0, y_face + side * 0.005, h * 0.55 + 0.040), face_rot, ink), crate)
    attach(text_obj(crate.name + "_Detail", detail, 0.019,
                    (0.0, y_face + side * 0.005, h * 0.55 - 0.024), face_rot, ink), crate)
    attach(text_obj(crate.name + "_Stamp", "FRAGILE", 0.028,
                    (0.0, y_face + side * 0.010, h * 0.55 - 0.135), face_rot, ink_red), crate)
    # stencil on the lid, readable from the elevated camera
    attach(text_obj(crate.name + "_LidCode", code, 0.040,
                    (0.0, 0.055, h + 0.0012), (0.0, 0.0, 0.0), ink), crate)
    attach(text_obj(crate.name + "_LidUp", "THIS SIDE UP", 0.020,
                    (0.0, -0.065, h + 0.0012), (0.0, 0.0, 0.0), ink), crate)


# --------------------------------------------------------------------------- #
#  scene
# --------------------------------------------------------------------------- #

LABELS = [("A-114", "MACHINE PARTS\nGROSS 68 kg"),
          ("A-115", "GLASSWARE\nGROSS 42 kg"),
          ("A-116", "BEARINGS\nGROSS 91 kg"),
          ("B-207", "CERAMIC TILE\nGROSS 77 kg"),
          ("B-208", "SPARE MOTORS\nGROSS 84 kg"),
          ("B-209", "HAND TOOLS\nGROSS 55 kg")]


def main():
    reset_scene()
    random.seed(26)

    pallet_wood = mat_noisy("PalletWood", (0.40, 0.27, 0.15), (0.62, 0.46, 0.28),
                            scale=14.0, mapping_scale=(1.0, 26.0, 1.0),
                            rough=0.74, bump=0.28)
    crate_wood = mat_noisy("CrateWood", (0.54, 0.39, 0.22), (0.75, 0.58, 0.36),
                           scale=12.0, mapping_scale=(22.0, 1.0, 1.0),
                           rough=0.68, bump=0.22)
    concrete = mat_noisy("Concrete", (0.25, 0.25, 0.26), (0.40, 0.40, 0.41),
                         scale=5.0, rough=0.88, bump=0.06)
    nail_mat = mat_simple("Nail", (0.44, 0.45, 0.47), rough=0.34, metallic=1.0)
    paper = mat_simple("LabelPaper", (0.93, 0.91, 0.84), rough=0.78)
    ink = mat_simple("Ink", (0.05, 0.05, 0.06), rough=0.6)
    ink_red = mat_simple("InkRed", (0.52, 0.06, 0.05), rough=0.6)

    fb = bmesh.new()
    add_box(fb, (14.0, 14.0, 0.10), (0.0, 0.0, -0.05))
    finish("Floor", fb, concrete)

    build_pallet(pallet_wood, nail_mat)

    size = (0.360, 0.340, 0.300)
    idx = 0
    for row, y in enumerate((-0.190, 0.190)):
        for x in (-0.400, 0.0, 0.400):
            code, detail = LABELS[idx]
            name = "Crate_%s" % code.replace("-", "")
            rz = random.uniform(-0.035, 0.035)
            crate = build_crate(name, (x, y, DECK_Z), size, rz, crate_wood, nail_mat)
            label_crate(crate, size, -1 if row == 0 else 1, code, detail,
                        paper, ink, ink_red)
            idx += 1

    add_area("Key", (2.4, -2.0, 3.1), (0.0, 0.0, 0.30), 900.0, size=3.0,
             color=(1.0, 0.96, 0.90))
    add_area("Fill", (-2.8, -1.6, 2.0), (0.0, 0.0, 0.30), 260.0, size=4.0,
             color=(0.82, 0.88, 1.0))
    add_area("Rim", (-1.2, 2.9, 2.4), (0.0, 0.2, 0.35), 480.0, size=2.5)
    add_camera((1.85, -2.25, 1.60), (0.0, 0.0, 0.34), lens=48.0)


if __name__ == "__main__":
    main()
