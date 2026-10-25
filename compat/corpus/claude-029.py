"""claude-029 : warehouse pallet rack loaded with boxes and barrels (Blender 4.5 LTS)."""

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
    sc.render.engine = 'CYCLES'
    if hasattr(sc, "cycles"):
        sc.cycles.samples = 96
        sc.cycles.use_denoising = True
    sc.render.resolution_x = 1800
    sc.render.resolution_y = 1100
    world = bpy.data.worlds.new("World")
    sc.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.045, 0.050, 0.060, 1.0)
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


def add_tube(bm, p1, p2, radius, segments=12, caps=True):
    a, b = Vector(p1), Vector(p2)
    d = b - a
    if d.length < 1e-6:
        return
    m = Matrix.Translation((a + b) * 0.5) @ d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
    before = set(bm.faces)
    bmesh.ops.create_cone(bm, cap_ends=caps, cap_tris=False, segments=segments,
                          radius1=radius, radius2=radius, depth=d.length,
                          matrix=m, calc_uvs=True)
    axis = d.normalized()
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


def mat_simple(name, color, rough=0.5, metallic=0.0, alpha=1.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    b = mat.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metallic
    if alpha < 1.0:
        b.inputs["Alpha"].default_value = alpha
        if hasattr(mat, "blend_method"):
            mat.blend_method = 'BLEND'
    return mat


def mat_noisy(name, c1, c2, scale=8.0, detail=6.0, rough=0.65,
              mapping_scale=(1.0, 1.0, 1.0), bump=0.15, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    b = nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metallic
    coord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = mapping_scale
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = scale
    noise.inputs["Detail"].default_value = detail
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.36
    ramp.color_ramp.elements[0].color = (c1[0], c1[1], c1[2], 1.0)
    ramp.color_ramp.elements[1].position = 0.64
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
#  rack structure
# --------------------------------------------------------------------------- #

FRAME_X = (-2.70, 0.0, 2.70)
BAY_X = (-1.35, 1.35)
COL_Y = 0.55
UPRIGHT_H = 3.90
BEAM_Z = (0.95, 1.95, 2.95)
BRACE_Z = (0.30, 0.90, 1.50, 2.10, 2.70, 3.30, 3.80)
DECK = [bz + 0.0825 for bz in BEAM_Z]        # top of decking per level


def build_frames(steel_blue, galv):
    bm = bmesh.new()
    for x in FRAME_X:
        for sy in (-1, 1):
            add_box(bm, (0.090, 0.090, UPRIGHT_H), (x, sy * COL_Y, UPRIGHT_H * 0.5))
        for z in BRACE_Z:
            add_tube(bm, (x, -COL_Y + 0.045, z), (x, COL_Y - 0.045, z), 0.020)
        for k in range(len(BRACE_Z) - 1):
            z0, z1 = BRACE_Z[k], BRACE_Z[k + 1]
            if k % 2 == 0:
                add_tube(bm, (x, -COL_Y + 0.045, z0), (x, COL_Y - 0.045, z1), 0.018)
            else:
                add_tube(bm, (x, COL_Y - 0.045, z0), (x, -COL_Y + 0.045, z1), 0.018)
    finish("RackFrames", bm, steel_blue, bevel=0.004, bevel_seg=1)

    bm = bmesh.new()
    for x in FRAME_X:
        for sy in (-1, 1):
            add_box(bm, (0.170, 0.170, 0.014), (x, sy * COL_Y, 0.007))
            for sx2 in (-1, 1):
                add_cyl(bm, 0.010, 0.070, (x + sx2 * 0.058, sy * COL_Y, 0.030),
                        segments=10)
    finish("RackFootplates", bm, galv)


def build_beams(orange, galv):
    bm = bmesh.new()
    for bx in BAY_X:
        for bz in BEAM_Z:
            for sy in (-1, 1):
                add_box(bm, (2.620, 0.055, 0.115), (bx, sy * 0.500, bz))
                add_box(bm, (2.620, 0.055, 0.020),
                        (bx, sy * 0.500 - sy * 0.050, bz - 0.048))
            for sx in (-1, 1):                       # end connectors
                for sy in (-1, 1):
                    add_box(bm, (0.030, 0.075, 0.170),
                            (bx + sx * 1.325, sy * 0.500, bz))
    finish("RackBeams", bm, orange, bevel=0.004, bevel_seg=1)

    bm = bmesh.new()
    for bx in BAY_X:
        for bz in BEAM_Z:
            for i in range(5):
                y = -0.440 + i * 0.220
                add_box(bm, (2.600, 0.115, 0.025), (bx, y, bz + 0.070))
            for i in range(4):
                add_tube(bm, (bx - 1.290, -0.450 + i * 0.30, bz + 0.055),
                         (bx + 1.290, -0.450 + i * 0.30, bz + 0.055), 0.008)
    finish("RackDecking", bm, galv)


def build_sign(paper, ink, orange):
    bm = bmesh.new()
    add_box(bm, (0.360, 0.006, 0.220), (0.0, -COL_Y - 0.050, 1.620))
    plate = finish("LoadSign", bm, paper)
    text_obj("LoadSignTitle", "BAY 12", 0.060,
             (0.0, -COL_Y - 0.056, 1.690), (math.pi * 0.5, 0.0, 0.0), ink)
    text_obj("LoadSignBody", "MAX 1200 kg\nPER LEVEL", 0.036,
             (0.0, -COL_Y - 0.056, 1.580), (math.pi * 0.5, 0.0, 0.0), ink)
    bm = bmesh.new()
    add_box(bm, (0.380, 0.010, 0.030), (0.0, -COL_Y - 0.046, 1.745))
    finish("LoadSignTrim", bm, orange)
    return plate


# --------------------------------------------------------------------------- #
#  loads
# --------------------------------------------------------------------------- #

def pallet_geom(bm, pre):
    """1.2 x 0.8 stringer pallet, long axis along X, base at local z = 0."""
    for x in (-0.525, 0.0, 0.525):
        add_box(bm, (0.145, 0.800, 0.020), (x, 0.0, 0.010), pre=pre)
    for y in (-0.350, 0.0, 0.350):
        add_box(bm, (1.200, 0.095, 0.100), (0.0, y, 0.070), pre=pre)
    for i in range(7):
        x = -0.540 + i * 0.180
        add_box(bm, (0.120, 0.800, 0.018), (x, 0.0, 0.129), pre=pre)


PALLET_H = 0.138


def build_pallets(placements, wood):
    bm = bmesh.new()
    for (x, y, z, rz) in placements:
        pre = Matrix.Translation(Vector((x, y, z))) @ Matrix.Rotation(rz, 4, 'Z')
        pallet_geom(bm, pre)
    return finish("Pallets", bm, wood, bevel=0.0025, bevel_seg=1)


def build_barrels(placements, blue, steel, r=0.220, h=0.860):
    bm = bmesh.new()
    cb = bmesh.new()
    for (x, y, z, rz) in placements:
        pre = Matrix.Translation(Vector((x, y, z))) @ Matrix.Rotation(rz, 4, 'Z')
        add_cyl(bm, r, h, (0.0, 0.0, h * 0.5), segments=32, pre=pre)
        for zr in (h * 0.30, h * 0.55, h * 0.78):
            add_cyl(bm, r + 0.016, 0.042, (0.0, 0.0, zr), segments=32, pre=pre)
        add_cyl(cb, r + 0.011, 0.036, (0.0, 0.0, h - 0.020), segments=32, pre=pre)
        add_cyl(cb, r + 0.011, 0.036, (0.0, 0.0, 0.020), segments=32, pre=pre)
        add_cyl(cb, 0.040, 0.016, (r * 0.55, 0.0, h + 0.006), segments=14, pre=pre)
        add_cyl(cb, 0.026, 0.014, (-r * 0.55, 0.0, h + 0.005), segments=12, pre=pre)
    finish("Barrels", bm, blue)
    finish("BarrelRings", cb, steel)


def build_carton(name, size, loc, rz, board, tape, label=None,
                 paper=None, ink=None, ink_red=None):
    w, d, h = size
    bm = bmesh.new()
    add_box(bm, (w, d, h), (0.0, 0.0, h * 0.5))
    obj = finish(name, bm, board, loc=loc, rot=(0.0, 0.0, rz),
                 bevel=0.008, bevel_seg=2)

    tb = bmesh.new()
    add_box(tb, (w * 1.002, 0.070, 0.0025), (0.0, 0.0, h + 0.0012))
    add_box(tb, (0.070, d * 0.52, 0.0025), (0.0, -d * 0.26, h + 0.0012))
    attach(finish(name + "_Tape", tb, tape), obj)

    if label is not None:
        code, detail = label
        y_face = -d * 0.5
        lb = bmesh.new()
        add_box(lb, (min(0.240, w * 0.62), 0.0022, 0.150),
                (0.0, y_face - 0.0016, h * 0.55))
        attach(finish(name + "_LabelCard", lb, paper), obj)
        attach(text_obj(name + "_Code", code, 0.045,
                        (0.0, y_face - 0.005, h * 0.55 + 0.042),
                        (math.pi * 0.5, 0.0, 0.0), ink), obj)
        attach(text_obj(name + "_Detail", detail, 0.021,
                        (0.0, y_face - 0.005, h * 0.55 - 0.026),
                        (math.pi * 0.5, 0.0, 0.0), ink), obj)
        attach(text_obj(name + "_Stamp", "FRAGILE", 0.030,
                        (0.0, y_face - 0.008, h * 0.55 - 0.140),
                        (math.pi * 0.5, 0.0, 0.0), ink_red), obj)
    return obj


# --------------------------------------------------------------------------- #
#  scene
# --------------------------------------------------------------------------- #

def main():
    reset_scene()
    random.seed(29)

    orange = mat_simple("RackOrange", (0.72, 0.26, 0.045), rough=0.38)
    steel_blue = mat_simple("RackBlue", (0.055, 0.135, 0.340), rough=0.40)
    galv = mat_simple("Galvanised", (0.55, 0.56, 0.58), rough=0.42, metallic=1.0)
    steel = mat_simple("Steel", (0.62, 0.63, 0.65), rough=0.32, metallic=1.0)
    drum_blue = mat_noisy("DrumBlue", (0.055, 0.185, 0.400), (0.100, 0.265, 0.520),
                          scale=25.0, rough=0.34, bump=0.06)
    board = mat_noisy("Cardboard", (0.48, 0.35, 0.21), (0.66, 0.50, 0.31),
                      scale=90.0, detail=8.0, rough=0.82, bump=0.28)
    tape = mat_simple("PackTape", (0.72, 0.63, 0.44), rough=0.28)
    wood = mat_noisy("PalletWood", (0.40, 0.28, 0.16), (0.62, 0.47, 0.29),
                     scale=14.0, mapping_scale=(1.0, 26.0, 1.0), rough=0.75, bump=0.26)
    paper = mat_simple("LabelPaper", (0.93, 0.91, 0.85), rough=0.78)
    ink = mat_simple("Ink", (0.05, 0.05, 0.06), rough=0.60)
    ink_red = mat_simple("InkRed", (0.52, 0.06, 0.05), rough=0.60)
    wrap = mat_simple("ShrinkWrap", (0.62, 0.68, 0.72), rough=0.32, alpha=0.22)
    concrete = mat_noisy("WarehouseFloor", (0.26, 0.26, 0.27), (0.40, 0.40, 0.41),
                         scale=4.0, rough=0.88, bump=0.05)
    wallm = mat_noisy("Wall", (0.30, 0.31, 0.32), (0.38, 0.39, 0.40),
                      scale=3.0, rough=0.92, bump=0.03)
    yellow = mat_simple("FloorPaint", (0.78, 0.62, 0.06), rough=0.55)

    bm = bmesh.new()
    add_box(bm, (26.0, 22.0, 0.12), (0.0, 0.0, -0.06))
    finish("Floor", bm, concrete)
    bm = bmesh.new()
    add_box(bm, (26.0, 0.20, 7.0), (0.0, 2.60, 3.50))
    finish("BackWall", bm, wallm)
    bm = bmesh.new()
    for y in (-1.35, -1.50):
        add_box(bm, (16.0, 0.075, 0.004), (0.0, y, 0.002))
    finish("AisleStripes", bm, yellow)

    build_frames(steel_blue, galv)
    build_beams(orange, galv)
    build_sign(paper, ink, orange)

    # ---- pallets -------------------------------------------------------- #
    pallet_spots = []
    for bx in BAY_X:
        for dx in (-0.640, 0.640):
            pallet_spots.append((bx + dx, 0.0, 0.0, random.uniform(-0.02, 0.02)))
    pallet_spots.append((BAY_X[0] - 0.640, 0.0, DECK[1], 0.0))
    pallet_spots.append((BAY_X[1] + 0.640, 0.0, DECK[1], 0.0))
    pallet_spots.append((BAY_X[0] + 0.640, 0.0, DECK[2], 0.0))
    build_pallets(pallet_spots, wood)

    # ---- barrels: 4 per pallet on three pallets -------------------------- #
    barrel_spots = []
    for (px, py, pz) in ((BAY_X[0] - 0.640, 0.0, 0.0),
                         (BAY_X[1] + 0.640, 0.0, 0.0),
                         (BAY_X[0] - 0.640, 0.0, DECK[1])):
        for dx in (-0.280, 0.280):
            for dy in (-0.250, 0.250):
                barrel_spots.append((px + dx, py + dy, pz + PALLET_H,
                                     random.uniform(0.0, TAU)))
    build_barrels(barrel_spots, drum_blue, steel)

    # ---- cartons --------------------------------------------------------- #
    labels = [("SKU 4417", "VALVE KITS\n24 UNITS"),
              ("SKU 5120", "FILTERS\n40 UNITS"),
              ("SKU 6033", "GLASS JARS\n12 UNITS"),
              ("SKU 7781", "BELT DRIVES\n18 UNITS"),
              ("SKU 8290", "FASTENERS\n60 UNITS"),
              ("SKU 9145", "GASKETS\n36 UNITS")]
    li = 0

    def stack(base_x, base_y, base_z, layers):
        nonlocal li
        z = base_z
        for (w, d, h, cols) in layers:
            for c in range(cols):
                x = base_x + (c - (cols - 1) * 0.5) * (w + 0.035)
                lab = labels[li % len(labels)] if z < base_z + 0.9 else None
                if lab is not None:
                    li += 1
                build_carton("Carton_%02d_%d" % (li, int(z * 100)),
                             (w, d, h), (x, base_y, z),
                             random.uniform(-0.05, 0.05), board, tape,
                             label=lab, paper=paper, ink=ink, ink_red=ink_red)
            z += h + 0.004

    # floor level, cardboard pallets
    stack(BAY_X[0] + 0.640, 0.0, PALLET_H, [(0.52, 0.60, 0.42, 2), (0.44, 0.52, 0.34, 2)])
    stack(BAY_X[1] - 0.640, 0.0, PALLET_H, [(0.58, 0.62, 0.46, 2), (0.36, 0.44, 0.30, 2)])
    # level 1
    stack(BAY_X[1] - 0.500, 0.0, DECK[0], [(0.60, 0.64, 0.44, 3), (0.48, 0.54, 0.36, 3)])
    stack(BAY_X[0] + 0.100, 0.0, DECK[0], [(0.54, 0.60, 0.40, 3)])
    # level 2
    stack(BAY_X[1] - 0.400, 0.0, DECK[1], [(0.56, 0.60, 0.42, 3), (0.40, 0.48, 0.32, 2)])
    # level 3
    stack(BAY_X[1] + 0.200, 0.0, DECK[2], [(0.50, 0.56, 0.38, 3)])

    # shrink-wrapped unit load on the top level of the left bay
    wrap_x = BAY_X[0] + 0.640
    stack(wrap_x, 0.0, DECK[2] + PALLET_H,
          [(0.50, 0.58, 0.36, 2), (0.50, 0.58, 0.36, 2)])
    bm = bmesh.new()
    add_box(bm, (1.120, 0.680, 0.760), (wrap_x, 0.0, DECK[2] + PALLET_H + 0.375))
    finish("ShrinkWrap", bm, wrap, bevel=0.02, bevel_seg=2)

    # ---- lighting and camera -------------------------------------------- #
    add_area("HighBay1", (-2.2, -2.6, 6.4), (-2.0, 0.0, 1.6), 5200.0, size=3.2,
             color=(1.0, 0.98, 0.94))
    add_area("HighBay2", (2.6, -2.4, 6.4), (2.2, 0.0, 1.6), 5200.0, size=3.2,
             color=(1.0, 0.98, 0.94))
    add_area("Fill", (-7.0, -6.0, 3.4), (0.0, 0.0, 1.8), 1600.0, size=6.0,
             color=(0.82, 0.88, 1.0))
    add_area("Rim", (0.0, 3.4, 3.6), (0.0, 0.4, 2.2), 900.0, size=4.0)
    add_camera((6.2, -6.8, 3.45), (-0.10, 0.0, 1.55), lens=40.0)


if __name__ == "__main__":
    main()
