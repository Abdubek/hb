# claude-121 : Kitbash sci-fi airlock  --  Blender 4.5 LTS
# Builds a bulkhead airlock with twin sliding door panels (partly open),
# conduit runs, greebled wall plating, warning beacons, control panel,
# floor grating and an interior tunnel seen through the door gap.

import bpy, bmesh, math, random
from mathutils import Vector

TAU = math.pi * 2.0

# --------------------------------------------------------------------------- #
#  scene bootstrap
# --------------------------------------------------------------------------- #

def factory_reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scn = bpy.context.scene
    for engine in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            scn.render.engine = engine
            break
        except TypeError:
            continue
    scn.unit_settings.system = 'METRIC'


def new_coll(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c


def link(ob, coll):
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    coll.objects.link(ob)


def set_mat(ob, mat):
    if mat is not None:
        ob.data.materials.append(mat)


def add_bevel(ob, width=0.012, segments=2, angle=62.0):
    m = ob.modifiers.new("Bevel", 'BEVEL')
    m.width = width
    m.segments = segments
    m.limit_method = 'ANGLE'
    m.angle_limit = math.radians(angle)
    m.miter_outer = 'MITER_ARC'


def smooth(ob):
    for p in ob.data.polygons:
        p.use_smooth = True


# --------------------------------------------------------------------------- #
#  primitive helpers (mesh-level sizing keeps object scale at 1.0)
# --------------------------------------------------------------------------- #

def box(name, size, loc, coll, mat=None, rot=(0.0, 0.0, 0.0), bev=0.0, seg=2):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts[:])
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = rot
    link(ob, coll)
    set_mat(ob, mat)
    if bev > 0.0:
        add_bevel(ob, width=bev, segments=seg)
    return ob


def cyl(name, radius, depth, loc, coll, mat=None, rot=(0.0, 0.0, 0.0),
        verts=24, bev=0.0, shade=False):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius,
                                        depth=depth, location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.name = name
    link(ob, coll)
    set_mat(ob, mat)
    if bev > 0.0:
        add_bevel(ob, width=bev, segments=2)
    if shade:
        smooth(ob)
    return ob


def sphere(name, radius, loc, coll, mat=None, segments=28, rings=14, scale_z=1.0):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings,
                                         radius=radius, location=loc)
    ob = bpy.context.active_object
    ob.name = name
    if scale_z != 1.0:
        me = ob.data
        for v in me.vertices:
            v.co.z *= scale_z
    link(ob, coll)
    set_mat(ob, mat)
    smooth(ob)
    return ob


def torus(name, major, minor, loc, coll, mat=None, rot=(0.0, 0.0, 0.0),
          mseg=32, nseg=12):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                     major_segments=mseg, minor_segments=nseg,
                                     location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.name = name
    link(ob, coll)
    set_mat(ob, mat)
    smooth(ob)
    return ob


def conduit(name, pts, radius, coll, mat=None, handle='AUTO', caps=True):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    sp = cu.splines.new('BEZIER')
    sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = Vector(p)
        bp.handle_left_type = handle
        bp.handle_right_type = handle
    cu.bevel_depth = radius
    cu.bevel_resolution = 4
    cu.resolution_u = 10
    cu.use_fill_caps = caps
    ob = bpy.data.objects.new(name, cu)
    link(ob, coll)
    set_mat(ob, mat)
    return ob


def bolt(name, loc, coll, mat, radius=0.035, depth=0.055,
         rot=(math.pi * 0.5, 0.0, 0.0)):
    return cyl(name, radius, depth, loc, coll, mat, rot=rot, verts=8)


def bolt_row(name, a, b, n, coll, mat, radius=0.035):
    a, b = Vector(a), Vector(b)
    for i in range(n):
        t = 0.0 if n == 1 else i / (n - 1.0)
        bolt(f"{name}_{i}", a.lerp(b, t), coll, mat, radius=radius)


# --------------------------------------------------------------------------- #
#  materials
# --------------------------------------------------------------------------- #

def make_mat(name, base, metallic=0.9, rough=0.45, emis=None, emis_str=0.0,
             alpha=1.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*base, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = rough
    if emis is not None:
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (*emis, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emis_str
    if alpha < 1.0:
        bsdf.inputs["Alpha"].default_value = alpha
        if hasattr(mat, "surface_render_method"):
            mat.surface_render_method = 'BLENDED'
        elif hasattr(mat, "blend_method"):
            mat.blend_method = 'BLEND'
    mat.diffuse_color = (*base, 1.0)
    return mat


def make_hazard_mat(name="MAT_hazard", angle=45.0, scale=7.0):
    """Diagonal yellow / black warning stripes, procedural in object space."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    n, l = nt.nodes, nt.links
    bsdf = n.get("Principled BSDF")
    bsdf.inputs["Metallic"].default_value = 0.35
    bsdf.inputs["Roughness"].default_value = 0.55

    coord = n.new("ShaderNodeTexCoord")
    coord.location = (-900, 0)
    mapping = n.new("ShaderNodeMapping")
    mapping.location = (-700, 0)
    mapping.inputs["Rotation"].default_value = (0.0, math.radians(angle), 0.0)
    mapping.inputs["Scale"].default_value = (scale, scale, scale)
    wave = n.new("ShaderNodeTexWave")
    wave.location = (-500, 0)
    wave.wave_type = 'BANDS'
    wave.bands_direction = 'Z'
    wave.wave_profile = 'SAW'
    wave.inputs["Scale"].default_value = 1.0
    wave.inputs["Distortion"].default_value = 0.0
    ramp = n.new("ShaderNodeValToRGB")
    ramp.location = (-300, 0)
    ramp.color_ramp.interpolation = 'CONSTANT'
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (0.85, 0.55, 0.03, 1.0)
    ramp.color_ramp.elements[1].position = 0.5
    ramp.color_ramp.elements[1].color = (0.02, 0.02, 0.025, 1.0)

    l.new(coord.outputs["Object"], mapping.inputs["Vector"])
    l.new(mapping.outputs["Vector"], wave.inputs["Vector"])
    l.new(wave.outputs["Fac"], ramp.inputs["Fac"])
    l.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    mat.diffuse_color = (0.8, 0.55, 0.05, 1.0)
    return mat


def build_materials():
    M = {}
    M["hull"]      = make_mat("MAT_hull",      (0.238, 0.252, 0.268), 0.85, 0.44)
    M["panel"]     = make_mat("MAT_panel",     (0.315, 0.330, 0.345), 0.90, 0.36)
    M["panel_dk"]  = make_mat("MAT_panel_dk",  (0.088, 0.094, 0.104), 0.80, 0.52)
    M["steel"]     = make_mat("MAT_steel",     (0.520, 0.545, 0.570), 1.00, 0.24)
    M["door"]      = make_mat("MAT_door",      (0.150, 0.180, 0.205), 0.92, 0.30)
    M["door_trim"] = make_mat("MAT_door_trim", (0.400, 0.410, 0.420), 1.00, 0.22)
    M["rubber"]    = make_mat("MAT_seal",      (0.020, 0.020, 0.022), 0.05, 0.82)
    M["copper"]    = make_mat("MAT_copper",    (0.560, 0.290, 0.140), 1.00, 0.30)
    M["hose"]      = make_mat("MAT_hose",      (0.055, 0.058, 0.062), 0.25, 0.68)
    M["grate"]     = make_mat("MAT_grate",     (0.130, 0.138, 0.148), 0.88, 0.55)
    M["glass"]     = make_mat("MAT_glass",     (0.40, 0.62, 0.72), 0.10, 0.05,
                              emis=(0.25, 0.55, 0.70), emis_str=0.35, alpha=0.28)
    M["hazard"]    = make_hazard_mat()
    M["hazard_fl"] = make_hazard_mat("MAT_hazard_floor", angle=0.0, scale=3.0)
    M["red"]       = make_mat("MAT_lamp_red",   (0.55, 0.03, 0.02), 0.0, 0.30,
                              emis=(1.0, 0.09, 0.03), emis_str=22.0)
    M["amber"]     = make_mat("MAT_lamp_amber", (0.60, 0.30, 0.02), 0.0, 0.30,
                              emis=(1.0, 0.45, 0.05), emis_str=16.0)
    M["green"]     = make_mat("MAT_lamp_green", (0.05, 0.45, 0.12), 0.0, 0.30,
                              emis=(0.12, 1.0, 0.30), emis_str=12.0)
    M["strip"]     = make_mat("MAT_strip",      (0.70, 0.85, 0.95), 0.0, 0.40,
                              emis=(0.55, 0.80, 1.0), emis_str=7.0)
    M["screen"]    = make_mat("MAT_screen",     (0.05, 0.30, 0.40), 0.0, 0.25,
                              emis=(0.20, 0.85, 1.0), emis_str=5.0)
    return M


# --------------------------------------------------------------------------- #
#  bulkhead wall
# --------------------------------------------------------------------------- #

WALL_X = 5.0          # half width of the bulkhead
WALL_Z = 4.6          # bulkhead height
WALL_Y0, WALL_Y1 = 0.0, 0.55     # front / back face of the wall slab
OP_X, OP_Z = 1.20, 3.00          # door opening half-width and height


def build_bulkhead(coll, M):
    yc = (WALL_Y0 + WALL_Y1) * 0.5
    yd = WALL_Y1 - WALL_Y0

    # main slab, split around the opening
    left_w = WALL_X - OP_X
    box("bulk_left", (left_w, yd, OP_Z), (-(OP_X + left_w * 0.5), yc, OP_Z * 0.5),
        coll, M["hull"], bev=0.02)
    box("bulk_right", (left_w, yd, OP_Z), ((OP_X + left_w * 0.5), yc, OP_Z * 0.5),
        coll, M["hull"], bev=0.02)
    box("bulk_lintel", (WALL_X * 2.0, yd, WALL_Z - OP_Z),
        (0.0, yc, (WALL_Z + OP_Z) * 0.5), coll, M["hull"], bev=0.02)

    # large armour plates bolted to the face
    plates = [(-3.45, 1.05, 2.45, 1.85), (-3.45, 1.05, 0.62, 1.05),
              ( 3.45, 1.05, 2.45, 1.85), ( 3.45, 1.05, 0.62, 1.05),
              (-2.05, 1.10, 3.90, 1.10), ( 2.05, 1.10, 3.90, 1.10)]
    for i, (cx, w, cz, h) in enumerate(plates):
        box(f"plate_{i}", (w, 0.07, h), (cx, -0.035, cz), coll,
            M["panel"], bev=0.018)
        bolt_row(f"plate_bolt_a{i}", (cx - w * 0.42, -0.075, cz - h * 0.42),
                 (cx + w * 0.42, -0.075, cz - h * 0.42), 4, coll, M["steel"])
        bolt_row(f"plate_bolt_b{i}", (cx - w * 0.42, -0.075, cz + h * 0.42),
                 (cx + w * 0.42, -0.075, cz + h * 0.42), 4, coll, M["steel"])

    # top capping beam and buttress ribs
    box("cap_beam", (WALL_X * 2.0, 0.75, 0.22), (0.0, 0.25, WALL_Z - 0.11),
        coll, M["panel"], bev=0.02)
    for i, cx in enumerate((-4.35, -2.75, 2.75, 4.35)):
        box(f"rib_{i}", (0.28, 0.34, WALL_Z - 0.35), (cx, -0.17, (WALL_Z - 0.35) * 0.5),
            coll, M["panel_dk"], bev=0.02)
        bolt_row(f"rib_bolt_{i}", (cx, -0.35, 0.45), (cx, -0.35, WALL_Z - 0.55),
                 7, coll, M["steel"], radius=0.03)

    # raised trim frame around the opening
    jamb = (0.30, 0.34, OP_Z + 0.34)
    box("jamb_L", jamb, (-(OP_X + 0.15), -0.17, (OP_Z + 0.34) * 0.5 - 0.17),
        coll, M["door_trim"], bev=0.02)
    box("jamb_R", jamb, ((OP_X + 0.15), -0.17, (OP_Z + 0.34) * 0.5 - 0.17),
        coll, M["door_trim"], bev=0.02)
    box("header", (OP_X * 2.0 + 0.60, 0.34, 0.30), (0.0, -0.17, OP_Z + 0.15),
        coll, M["door_trim"], bev=0.02)
    bolt_row("jamb_bolt_L", (-(OP_X + 0.15), -0.35, 0.25),
             (-(OP_X + 0.15), -0.35, OP_Z - 0.05), 9, coll, M["steel"])
    bolt_row("jamb_bolt_R", ((OP_X + 0.15), -0.35, 0.25),
             ((OP_X + 0.15), -0.35, OP_Z - 0.05), 9, coll, M["steel"])
    bolt_row("header_bolt", (-OP_X - 0.15, -0.35, OP_Z + 0.15),
             (OP_X + 0.15, -0.35, OP_Z + 0.15), 9, coll, M["steel"])

    # hazard chevrons on the jambs and header
    box("hz_jamb_L", (0.11, 0.10, OP_Z - 0.10), (-(OP_X + 0.02), -0.34, OP_Z * 0.5),
        coll, M["hazard"])
    box("hz_jamb_R", (0.11, 0.10, OP_Z - 0.10), ((OP_X + 0.02), -0.34, OP_Z * 0.5),
        coll, M["hazard"])
    box("hz_header", (OP_X * 2.0 + 0.50, 0.10, 0.11), (0.0, -0.34, OP_Z + 0.02),
        coll, M["hazard"])

    # inner reveal of the opening + compression seals
    box("reveal_L", (0.06, 0.55, OP_Z), (-OP_X + 0.03, 0.275, OP_Z * 0.5),
        coll, M["panel_dk"])
    box("reveal_R", (0.06, 0.55, OP_Z), (OP_X - 0.03, 0.275, OP_Z * 0.5),
        coll, M["panel_dk"])
    box("reveal_T", (OP_X * 2.0, 0.55, 0.06), (0.0, 0.275, OP_Z - 0.03),
        coll, M["panel_dk"])
    box("seal_L", (0.05, 0.10, OP_Z), (-OP_X + 0.025, 0.10, OP_Z * 0.5),
        coll, M["rubber"])
    box("seal_R", (0.05, 0.10, OP_Z), (OP_X - 0.025, 0.10, OP_Z * 0.5),
        coll, M["rubber"])
    box("seal_T", (OP_X * 2.0, 0.10, 0.05), (0.0, 0.10, OP_Z - 0.025),
        coll, M["rubber"])

    # door guide rails
    box("rail_top", (OP_X * 2.0 + 1.40, 0.30, 0.12), (0.0, 0.28, OP_Z - 0.06),
        coll, M["steel"], bev=0.012)
    box("rail_bottom", (OP_X * 2.0 + 1.40, 0.30, 0.10), (0.0, 0.28, 0.05),
        coll, M["steel"], bev=0.012)
    for i, cx in enumerate((-1.95, -0.55, 0.55, 1.95)):
        cyl(f"rail_roller_{i}", 0.055, 0.18, (cx, 0.28, OP_Z - 0.16), coll,
            M["copper"], rot=(0.0, math.pi * 0.5, 0.0), verts=16, shade=True)


def wall_greebles(coll, M, seed=11):
    """Kitbash clutter: small plates, vents, canisters and junction boxes."""
    rng = random.Random(seed)
    zones = [(-4.85, -1.45, 0.20, 4.45), (1.45, 4.85, 0.20, 4.45)]
    idx = 0
    for zx0, zx1, zz0, zz1 in zones:
        for _ in range(22):
            w = rng.uniform(0.22, 0.80)
            h = rng.uniform(0.16, 0.62)
            t = rng.uniform(0.03, 0.13)
            cx = rng.uniform(zx0 + w * 0.5, zx1 - w * 0.5)
            cz = rng.uniform(zz0 + h * 0.5, zz1 - h * 0.5)
            mat = rng.choice([M["panel"], M["panel_dk"], M["steel"], M["hull"]])
            box(f"greeb_{idx}", (w, t, h), (cx, -t * 0.5 - 0.06, cz), coll,
                mat, bev=0.010)
            idx += 1
            r = rng.random()
            if r < 0.30:                                    # louvre vent
                for k in range(3):
                    box(f"greeb_vent_{idx}_{k}",
                        (w * 0.74, 0.035, h * 0.13),
                        (cx, -t - 0.075, cz - h * 0.22 + k * h * 0.22),
                        coll, M["panel_dk"], bev=0.006)
            elif r < 0.52:                                  # canister / tank
                cyl(f"greeb_can_{idx}", min(w, h) * 0.30, 0.20,
                    (cx, -t - 0.16, cz), coll, M["steel"],
                    rot=(math.pi * 0.5, 0.0, 0.0), verts=16, shade=True)
            elif r < 0.68:                                  # bolt border
                bolt_row(f"greeb_bolt_{idx}", (cx - w * 0.4, -t - 0.09, cz),
                         (cx + w * 0.4, -t - 0.09, cz), 4, coll, M["steel"],
                         radius=0.026)
            elif r < 0.78:                                  # tiny status lamp
                mat_l = rng.choice([M["amber"], M["green"], M["strip"]])
                cyl(f"greeb_lamp_{idx}", 0.035, 0.05,
                    (cx + w * 0.3, -t - 0.09, cz + h * 0.28), coll, mat_l,
                    rot=(math.pi * 0.5, 0.0, 0.0), verts=12, shade=True)
    # a pair of chunky junction boxes
    for i, (cx, cz) in enumerate(((-4.15, 1.85), (4.10, 2.20))):
        box(f"junction_{i}", (0.62, 0.34, 0.86), (cx, -0.24, cz), coll,
            M["panel_dk"], bev=0.02)
        box(f"junction_lid_{i}", (0.50, 0.06, 0.72), (cx, -0.43, cz), coll,
            M["panel"], bev=0.014)
        bolt_row(f"junction_bolt_{i}", (cx - 0.24, -0.47, cz - 0.34),
                 (cx - 0.24, -0.47, cz + 0.34), 4, coll, M["steel"], radius=0.028)
        cyl(f"junction_dial_{i}", 0.09, 0.05, (cx + 0.16, -0.48, cz + 0.24),
            coll, M["screen"], rot=(math.pi * 0.5, 0.0, 0.0), verts=16, shade=True)


# --------------------------------------------------------------------------- #
#  sliding door panels
# --------------------------------------------------------------------------- #

def door_panel(coll, M, side, seed=3):
    """side = -1 (left leaf) or +1 (right leaf). Leaves are partly retracted."""
    rng = random.Random(seed)
    tag = "L" if side < 0 else "R"
    w, h, t = 1.30, OP_Z - 0.04, 0.16
    y_mid = 0.28                       # panel sits recessed in the frame
    y_front = y_mid - t * 0.5          # -Y facing surface
    cx = side * 1.10                   # retracted: leaves a 0.90 m gap
    cz = h * 0.5 + 0.02

    box(f"door_{tag}", (w, t, h), (cx, y_mid, cz), coll, M["door"], bev=0.022, seg=3)

    # perimeter trim + horizontal banding
    box(f"door_{tag}_trim_top", (w - 0.06, 0.05, 0.10),
        (cx, y_front - 0.025, cz + h * 0.5 - 0.10), coll, M["door_trim"], bev=0.010)
    box(f"door_{tag}_trim_bot", (w - 0.06, 0.05, 0.10),
        (cx, y_front - 0.025, 0.14), coll, M["door_trim"], bev=0.010)
    for k, zz in enumerate((0.55, 1.05, 2.55)):
        box(f"door_{tag}_band_{k}", (w - 0.14, 0.04, 0.06),
            (cx, y_front - 0.02, zz), coll, M["panel_dk"], bev=0.008)

    # main raised plate with recessed sub-panels
    box(f"door_{tag}_plate", (w - 0.22, 0.055, 1.15),
        (cx, y_front - 0.027, 1.80), coll, M["panel"], bev=0.014)
    for k in range(4):
        box(f"door_{tag}_sub_{k}", (w * 0.34, 0.03, 0.24),
            (cx - side * 0.24 + (k % 2) * side * 0.48,
             y_front - 0.062, 1.42 + (k // 2) * 0.62),
            coll, M["panel_dk"], bev=0.008)

    # viewport
    win_x = cx - side * 0.28
    torus(f"door_{tag}_win_ring", 0.235, 0.045, (win_x, y_front - 0.02, 2.42),
          coll, M["steel"], rot=(math.pi * 0.5, 0.0, 0.0), mseg=28, nseg=10)
    cyl(f"door_{tag}_win_glass", 0.215, 0.05, (win_x, y_front + 0.01, 2.42),
        coll, M["glass"], rot=(math.pi * 0.5, 0.0, 0.0), verts=28, shade=True)
    for k in range(6):
        a = k * TAU / 6.0 + 0.3
        bolt(f"door_{tag}_win_bolt_{k}",
             (win_x + math.cos(a) * 0.30, y_front - 0.05, 2.42 + math.sin(a) * 0.30),
             coll, M["steel"], radius=0.028, depth=0.05)

    # meeting-edge seal, hazard stripe and latch fingers
    edge = cx - side * (w * 0.5 - 0.055)
    box(f"door_{tag}_seal", (0.05, t * 0.92, h - 0.04), (edge - side * 0.03, y_mid, cz),
        coll, M["rubber"])
    box(f"door_{tag}_hazard", (0.13, 0.05, h - 0.30),
        (edge + side * 0.09, y_front - 0.025, cz), coll, M["hazard"])
    for k in range(5):
        box(f"door_{tag}_latch_{k}", (0.10, t * 0.55, 0.13),
            (edge - side * 0.06, y_mid, 0.42 + k * 0.62), coll, M["steel"], bev=0.010)

    # actuator ram running back into the frame
    cyl(f"door_{tag}_ram", 0.075, 0.62, (cx + side * 0.40, y_mid + 0.14, 2.78),
        coll, M["steel"], rot=(0.0, math.pi * 0.5, 0.0), verts=16, shade=True)
    cyl(f"door_{tag}_ram_rod", 0.035, 0.95, (cx + side * 0.92, y_mid + 0.14, 2.78),
        coll, M["copper"], rot=(0.0, math.pi * 0.5, 0.0), verts=12, shade=True)

    # small kitbash greebles on the leaf
    for k in range(7):
        gw = rng.uniform(0.10, 0.34)
        gh = rng.uniform(0.06, 0.20)
        gx = cx + rng.uniform(-w * 0.32, w * 0.32)
        gz = rng.uniform(0.30, 1.20)
        box(f"door_{tag}_greeb_{k}", (gw, 0.035, gh), (gx, y_front - 0.02, gz),
            coll, rng.choice([M["panel"], M["panel_dk"], M["steel"]]), bev=0.007)

    # leaf-status lamp strip
    box(f"door_{tag}_strip", (w * 0.5, 0.03, 0.045),
        (cx, y_front - 0.032, 2.02), coll,
        M["amber"] if side < 0 else M["green"])


# --------------------------------------------------------------------------- #
#  interior tunnel visible through the gap
# --------------------------------------------------------------------------- #

def build_interior(coll, M):
    y0, y1 = WALL_Y1, 5.0
    depth = y1 - y0
    yc = (y0 + y1) * 0.5
    hz = 3.15

    box("int_floor", (2.80, depth, 0.10), (0.0, yc, -0.05), coll, M["grate"], bev=0.012)
    box("int_ceil", (2.80, depth, 0.12), (0.0, yc, hz + 0.06), coll, M["hull"], bev=0.012)
    box("int_wall_L", (0.12, depth, hz), (-1.34, yc, hz * 0.5), coll, M["hull"], bev=0.012)
    box("int_wall_R", (0.12, depth, hz), (1.34, yc, hz * 0.5), coll, M["hull"], bev=0.012)
    box("int_back", (2.80, 0.14, hz), (0.0, y1 - 0.07, hz * 0.5), coll, M["panel_dk"],
        bev=0.014)
    box("int_back_hatch", (1.30, 0.06, 1.90), (0.0, y1 - 0.17, 1.05), coll,
        M["door"], bev=0.02)
    box("int_back_glow", (1.05, 0.03, 0.12), (0.0, y1 - 0.21, 2.14), coll, M["strip"])

    # structural ribs
    for i, yy in enumerate((1.20, 2.35, 3.50, 4.55)):
        box(f"int_rib_L_{i}", (0.16, 0.20, hz), (-1.22, yy, hz * 0.5), coll,
            M["panel"], bev=0.012)
        box(f"int_rib_R_{i}", (0.16, 0.20, hz), (1.22, yy, hz * 0.5), coll,
            M["panel"], bev=0.012)
        box(f"int_rib_T_{i}", (2.60, 0.20, 0.16), (0.0, yy, hz - 0.08), coll,
            M["panel"], bev=0.012)

    # ceiling and cove light strips
    box("int_strip_ceil", (0.34, depth - 0.5, 0.05), (0.0, yc, hz - 0.02),
        coll, M["strip"])
    box("int_strip_L", (0.05, depth - 0.5, 0.10), (-1.25, yc, 2.70), coll, M["strip"])
    box("int_strip_R", (0.05, depth - 0.5, 0.10), (1.25, yc, 2.70), coll, M["strip"])

    # interior floor hazard band and pipes
    box("int_floor_hazard", (2.55, 0.34, 0.02), (0.0, y0 + 0.42, 0.005), coll,
        M["hazard_fl"])
    conduit("int_pipe_L", [(-1.16, y0 + 0.10, 0.42), (-1.16, y1 - 0.30, 0.42),
                           (-1.16, y1 - 0.30, 1.60)], 0.055, coll, M["steel"])
    conduit("int_pipe_R", [(1.16, y0 + 0.10, 0.60), (1.16, y1 - 0.30, 0.60),
                           (1.16, y1 - 0.30, 1.40)], 0.045, coll, M["copper"])


# --------------------------------------------------------------------------- #
#  conduits and hoses on the outer face
# --------------------------------------------------------------------------- #

def build_conduits(coll, M):
    y = -0.30

    # main trunk arching over the doorway
    trunks = [(-2.62, 2.62, 4.02, 0.085, M["steel"]),
              (-2.86, 2.86, 3.80, 0.065, M["copper"]),
              (-2.40, 2.40, 4.24, 0.055, M["panel_dk"])]
    for i, (xa, xb, ztop, r, mat) in enumerate(trunks):
        pts = [(xa, y, 0.24), (xa, y, ztop), (xb, y, ztop), (xb, y, 0.24)]
        conduit(f"trunk_{i}", pts, r, coll, mat)
        for k in range(6):
            zz = 0.45 + k * 0.62
            torus(f"trunk_clamp_a{i}_{k}", r + 0.035, 0.030, (xa, y, zz), coll,
                  M["steel"], rot=(math.pi * 0.5, 0.0, 0.0), mseg=16, nseg=8)
            torus(f"trunk_clamp_b{i}_{k}", r + 0.035, 0.030, (xb, y, zz), coll,
                  M["steel"], rot=(math.pi * 0.5, 0.0, 0.0), mseg=16, nseg=8)
        for k in range(5):
            xx = -1.8 + k * 0.9
            torus(f"trunk_clamp_top{i}_{k}", r + 0.035, 0.030, (xx, y, ztop), coll,
                  M["steel"], rot=(0.0, math.pi * 0.5, 0.0), mseg=16, nseg=8)

    # horizontal service runs on the flanks
    for i, (zz, r, mat) in enumerate(((1.55, 0.06, M["copper"]),
                                      (1.30, 0.045, M["steel"]))):
        conduit(f"run_L_{i}", [(-4.90, y - 0.12, zz), (-1.62, y - 0.12, zz),
                               (-1.62, y - 0.12, zz + 0.85)], r, coll, mat)
        conduit(f"run_R_{i}", [(4.90, y - 0.12, zz), (1.62, y - 0.12, zz),
                               (1.62, y - 0.12, zz + 0.85)], r, coll, mat)
        for k in range(5):
            xx = 4.55 - k * 0.72
            torus(f"run_clampR_{i}_{k}", r + 0.032, 0.028, (xx, y - 0.12, zz), coll,
                  M["steel"], rot=(0.0, math.pi * 0.5, 0.0), mseg=14, nseg=8)
            torus(f"run_clampL_{i}_{k}", r + 0.032, 0.028, (-xx, y - 0.12, zz), coll,
                  M["steel"], rot=(0.0, math.pi * 0.5, 0.0), mseg=14, nseg=8)

    # sagging flexible hoses
    conduit("hose_a", [(-3.90, -0.42, 2.55), (-3.20, -0.62, 2.05),
                       (-2.55, -0.48, 2.35), (-1.95, -0.36, 1.30)],
            0.048, coll, M["hose"])
    conduit("hose_b", [(3.95, -0.42, 2.85), (3.30, -0.66, 2.20),
                       (2.60, -0.50, 2.55), (2.05, -0.36, 3.05)],
            0.040, coll, M["hose"])
    conduit("hose_c", [(-1.70, -0.40, 0.55), (-1.05, -0.70, 0.32),
                       (-0.30, -0.62, 0.30)], 0.055, coll, M["hose"])

    # pressure manifold with valves
    box("manifold", (0.70, 0.30, 0.44), (-3.05, -0.30, 0.62), coll,
        M["panel_dk"], bev=0.018)
    for k in range(3):
        xx = -3.30 + k * 0.25
        cyl(f"valve_body_{k}", 0.055, 0.26, (xx, -0.48, 0.62), coll, M["steel"],
            rot=(math.pi * 0.5, 0.0, 0.0), verts=14, shade=True)
        torus(f"valve_wheel_{k}", 0.095, 0.022, (xx, -0.60, 0.62), coll,
              M["copper"], rot=(math.pi * 0.5, 0.0, 0.0), mseg=18, nseg=8)
    cyl("manifold_gauge", 0.085, 0.06, (-2.78, -0.48, 0.82), coll, M["screen"],
        rot=(math.pi * 0.5, 0.0, 0.0), verts=18, shade=True)


# --------------------------------------------------------------------------- #
#  warning lights
# --------------------------------------------------------------------------- #

def beacon(name, loc, coll, M, lamp_mat, color, energy=45.0, size=0.16, cage=True):
    x, yy, z = loc
    box(f"{name}_bracket", (0.24, 0.16, 0.30), (x, yy + 0.08, z), coll,
        M["panel_dk"], bev=0.014)
    cyl(f"{name}_housing", size * 1.12, 0.14, (x, yy - 0.07, z), coll, M["steel"],
        rot=(math.pi * 0.5, 0.0, 0.0), verts=20, bev=0.010)
    sphere(f"{name}_dome", size, (x, yy - 0.14, z), coll, lamp_mat,
           segments=24, rings=12, scale_z=0.85)
    if cage:
        for k in range(4):
            a = k * TAU / 4.0 + math.pi / 4.0
            box(f"{name}_cage_{k}", (0.022, 0.20, size * 2.15),
                (x, yy - 0.16, z), coll, M["panel_dk"],
                rot=(0.0, a, 0.0))
        torus(f"{name}_cage_ring", size * 1.05, 0.018, (x, yy - 0.24, z), coll,
              M["panel_dk"], rot=(math.pi * 0.5, 0.0, 0.0), mseg=20, nseg=8)
    lt = bpy.data.lights.new(f"{name}_light", 'POINT')
    lt.color = color
    lt.energy = energy
    lt.shadow_soft_size = 0.10
    ob = bpy.data.objects.new(f"{name}_light", lt)
    ob.location = (x, yy - 0.34, z)
    link(ob, coll)
    return ob


def build_warning_lights(coll, M):
    beacon("beacon_L", (-1.72, -0.34, 3.34), coll, M, M["red"], (1.0, 0.12, 0.05), 55.0)
    beacon("beacon_R", (1.72, -0.34, 3.34), coll, M, M["red"], (1.0, 0.12, 0.05), 55.0)
    beacon("beacon_TL", (-3.60, -0.34, 4.10), coll, M, M["amber"],
           (1.0, 0.50, 0.10), 35.0, size=0.13)
    beacon("beacon_TR", (3.60, -0.34, 4.10), coll, M, M["amber"],
           (1.0, 0.50, 0.10), 35.0, size=0.13)
    beacon("beacon_status", (2.10, -0.30, 2.28), coll, M, M["green"],
           (0.20, 1.0, 0.35), 22.0, size=0.09, cage=False)

    # rotating hazard strobe on the header
    box("strobe_base", (0.34, 0.28, 0.12), (0.0, -0.30, OP_Z + 0.36), coll,
        M["panel_dk"], bev=0.012)
    cyl("strobe_lens", 0.13, 0.20, (0.0, -0.30, OP_Z + 0.52), coll, M["amber"],
        verts=20, shade=True)
    cyl("strobe_cap", 0.15, 0.05, (0.0, -0.30, OP_Z + 0.64), coll, M["steel"],
        verts=20, bev=0.008)
    lt = bpy.data.lights.new("strobe_light", 'POINT')
    lt.color = (1.0, 0.55, 0.12)
    lt.energy = 70.0
    lt.shadow_soft_size = 0.12
    ob = bpy.data.objects.new("strobe_light", lt)
    ob.location = (0.0, -0.55, OP_Z + 0.52)
    link(ob, coll)

    # illuminated marquee strips flanking the doorway
    for i, sx in enumerate((-1, 1)):
        box(f"marquee_{i}", (0.09, 0.05, 1.30),
            (sx * (OP_X + 0.36), -0.36, 1.60), coll, M["strip"])
        box(f"marquee_hood_{i}", (0.17, 0.13, 1.42),
            (sx * (OP_X + 0.36), -0.30, 1.60), coll, M["panel_dk"], bev=0.010)


# --------------------------------------------------------------------------- #
#  control panel
# --------------------------------------------------------------------------- #

def build_control_panel(coll, M):
    x0, z0 = 2.10, 1.35
    tilt = math.radians(-16.0)
    box("cp_body", (0.78, 0.30, 0.98), (x0, -0.20, z0), coll, M["panel_dk"],
        rot=(tilt, 0.0, 0.0), bev=0.020)
    box("cp_face", (0.68, 0.05, 0.86), (x0, -0.37, z0 + 0.01), coll, M["panel"],
        rot=(tilt, 0.0, 0.0), bev=0.012)
    box("cp_screen", (0.50, 0.02, 0.34), (x0, -0.41, z0 + 0.21), coll, M["screen"],
        rot=(tilt, 0.0, 0.0))
    for r in range(2):
        for c in range(4):
            cyl(f"cp_btn_{r}_{c}", 0.035, 0.04,
                (x0 - 0.20 + c * 0.135, -0.40 + r * 0.028, z0 - 0.10 - r * 0.14),
                coll, M["amber"] if (r + c) % 3 else M["green"],
                rot=(math.pi * 0.5 + tilt, 0.0, 0.0), verts=12, shade=True)
    cyl("cp_dial", 0.075, 0.06, (x0 + 0.20, -0.42, z0 - 0.30), coll, M["copper"],
        rot=(math.pi * 0.5 + tilt, 0.0, 0.0), verts=18, shade=True)
    box("cp_lever", (0.05, 0.05, 0.22), (x0 - 0.24, -0.45, z0 - 0.34), coll,
        M["steel"], rot=(math.radians(28.0), 0.0, 0.0), bev=0.010)
    box("cp_pedestal", (0.30, 0.26, 0.86), (x0, -0.16, 0.43), coll, M["panel"],
        bev=0.016)
    conduit("cp_feed", [(x0, -0.10, 0.06), (x0, -0.02, 0.06), (x0, -0.02, 0.90)],
            0.045, coll, M["hose"])
    box("cp_placard", (0.34, 0.03, 0.10), (x0, -0.36, z0 + 0.46), coll, M["hazard"],
        rot=(tilt, 0.0, 0.0))


# --------------------------------------------------------------------------- #
#  floor
# --------------------------------------------------------------------------- #

def build_floor(coll, M):
    box("floor_slab", (12.0, 6.6, 0.24), (0.0, -3.05, -0.12), coll, M["hull"],
        bev=0.02)
    box("floor_kerb", (12.0, 0.22, 0.14), (0.0, -6.24, 0.07), coll, M["panel_dk"],
        bev=0.012)

    # grating slats in front of the airlock
    n = 26
    y_start, y_end = -0.18, -4.20
    for i in range(n):
        yy = y_start + (y_end - y_start) * i / (n - 1.0)
        box(f"grate_slat_{i}", (7.6, 0.085, 0.09), (0.0, yy, 0.045), coll,
            M["grate"], bev=0.008)
    for i, xx in enumerate((-3.5, -1.75, 0.0, 1.75, 3.5)):
        box(f"grate_beam_{i}", (0.10, abs(y_end - y_start) + 0.2,
                                0.05), (xx, (y_start + y_end) * 0.5, 0.015),
            coll, M["steel"], bev=0.006)

    # threshold plate and hazard hatching
    box("threshold", (OP_X * 2.0 + 0.9, 0.34, 0.10), (0.0, -0.20, 0.05), coll,
        M["steel"], bev=0.010)
    box("threshold_hazard", (OP_X * 2.0 + 0.7, 0.26, 0.02), (0.0, -0.20, 0.105),
        coll, M["hazard_fl"])
    for i, sx in enumerate((-1, 1)):
        box(f"floor_mark_{i}", (0.9, 1.5, 0.015),
            (sx * 2.35, -1.35, 0.098), coll, M["hazard_fl"])

    # recessed floor lights guiding to the door
    for i in range(4):
        box(f"floor_light_{i}", (0.16, 0.05, 0.02),
            (-2.05, -0.7 - i * 0.85, 0.1), coll, M["strip"])
        box(f"floor_light_r{i}", (0.16, 0.05, 0.02),
            (2.05, -0.7 - i * 0.85, 0.1), coll, M["strip"])


# --------------------------------------------------------------------------- #
#  lighting, world, camera
# --------------------------------------------------------------------------- #

def build_world():
    world = bpy.data.worlds.new("AirlockWorld")
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (0.016, 0.020, 0.028, 1.0)
    bg.inputs["Strength"].default_value = 1.0
    bpy.context.scene.world = world


def area_light(name, loc, target, energy, size, coll, color=(1.0, 1.0, 1.0)):
    lt = bpy.data.lights.new(name, 'AREA')
    lt.energy = energy
    lt.size = size
    lt.color = color
    ob = bpy.data.objects.new(name, lt)
    ob.location = loc
    d = Vector(target) - Vector(loc)
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    link(ob, coll)
    return ob


def build_lighting(coll):
    area_light("key_light", (-5.6, -7.8, 6.4), (-0.6, 0.2, 1.9), 1400.0, 6.0,
               coll, (1.0, 0.96, 0.90))
    area_light("fill_light", (7.4, -6.2, 2.6), (0.8, 0.2, 1.6), 420.0, 5.0,
               coll, (0.62, 0.74, 1.0))
    area_light("rim_light", (0.4, 6.0, 4.6), (0.0, 0.6, 2.4), 320.0, 3.0,
               coll, (0.55, 0.80, 1.0))
    area_light("ground_bounce", (0.0, -3.2, 0.6), (0.0, 0.4, 1.4), 160.0, 4.0,
               coll, (0.85, 0.86, 0.92))

    tunnel = bpy.data.lights.new("tunnel_glow", 'POINT')
    tunnel.energy = 260.0
    tunnel.color = (0.55, 0.80, 1.0)
    tunnel.shadow_soft_size = 0.6
    ob = bpy.data.objects.new("tunnel_glow", tunnel)
    ob.location = (0.0, 2.2, 2.3)
    link(ob, coll)


def build_camera(coll):
    cam_data = bpy.data.cameras.new("AirlockCam")
    cam_data.lens = 46.0
    cam_data.sensor_width = 36.0
    cam_data.clip_start = 0.05
    cam_data.clip_end = 200.0
    cam_data.dof.use_dof = True
    cam_data.dof.focus_distance = 8.4
    cam_data.dof.aperture_fstop = 4.0
    cam = bpy.data.objects.new("AirlockCam", cam_data)
    cam.location = (4.35, -8.35, 2.75)
    target = Vector((-0.10, 0.30, 1.72))
    cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
    link(cam, coll)
    scn = bpy.context.scene
    scn.camera = cam
    scn.render.resolution_x = 1920
    scn.render.resolution_y = 1080
    return cam


# --------------------------------------------------------------------------- #
#  main
# --------------------------------------------------------------------------- #

def main():
    factory_reset()
    M = build_materials()

    c_struct = new_coll("AL_structure")
    c_doors = new_coll("AL_doors")
    c_interior = new_coll("AL_interior")
    c_conduit = new_coll("AL_conduits")
    c_lights = new_coll("AL_warning_lights")
    c_detail = new_coll("AL_details")
    c_floor = new_coll("AL_floor")
    c_rig = new_coll("AL_rig")

    build_bulkhead(c_struct, M)
    wall_greebles(c_detail, M)
    door_panel(c_doors, M, -1, seed=17)
    door_panel(c_doors, M, +1, seed=23)
    build_interior(c_interior, M)
    build_conduits(c_conduit, M)
    build_warning_lights(c_lights, M)
    build_control_panel(c_detail, M)
    build_floor(c_floor, M)

    build_world()
    build_lighting(c_rig)
    build_camera(c_rig)

    print("Airlock built: %d objects" % len(bpy.data.objects))


if __name__ == "__main__":
    main()
