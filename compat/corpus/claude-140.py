"""
claude-140 — Museum gallery with partition walls, framed artworks and ceiling track lights.
Blender 4.5 LTS. Builds the scene only (no render, no file output).
"""

import bpy
import bmesh
import math
import random
from mathutils import Vector

random.seed(20250909)

CEIL_H = 4.2
ROOM_X = 9.0          # interior half-width  (x in [-9, 9])
ROOM_Y = 7.0          # interior half-depth  (y in [-7, 7])
WALL_T = 0.30
PART_T = 0.25         # partition thickness
PART_H = 3.40         # partition height


# --------------------------------------------------------------------------- #
#  Scene / collection helpers
# --------------------------------------------------------------------------- #
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scn = bpy.context.scene
    scn.unit_settings.system = 'METRIC'
    scn.unit_settings.length_unit = 'METERS'
    try:
        scn.render.engine = 'BLENDER_EEVEE_NEXT'
    except TypeError:
        pass
    world = bpy.data.worlds.new("GalleryWorld")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.045, 0.046, 0.052, 1.0)
    bg.inputs["Strength"].default_value = 1.0
    scn.world = world
    return scn


def make_collection(name):
    coll = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(coll)
    return coll


def add_object(name, mesh, coll, location=(0, 0, 0), rotation=(0, 0, 0), materials=()):
    ob = bpy.data.objects.new(name, mesh)
    ob.location = location
    ob.rotation_euler = rotation
    coll.objects.link(ob)
    for m in materials:
        ob.data.materials.append(m)
    return ob


def shade_smooth(ob, angle=math.radians(40.0)):
    me = ob.data
    for p in me.polygons:
        p.use_smooth = True
    mod = ob.modifiers.new("Smooth by Angle", 'EDGE_SPLIT')
    mod.split_angle = angle
    mod.use_edge_sharp = False


# --------------------------------------------------------------------------- #
#  Primitive builders (bmesh)
# --------------------------------------------------------------------------- #
def bm_box(bm, size, offset=(0.0, 0.0, 0.0)):
    """Axis-aligned box of given full size, centred on `offset`."""
    ret = bmesh.ops.create_cube(bm, size=1.0)
    verts = ret["verts"]
    bmesh.ops.scale(bm, vec=Vector(size), verts=verts)
    bmesh.ops.translate(bm, vec=Vector(offset), verts=verts)
    return verts


def bm_cyl(bm, radius, depth, offset=(0.0, 0.0, 0.0), segments=24, radius_top=None):
    ret = bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=segments,
        radius1=radius,
        radius2=radius if radius_top is None else radius_top,
        depth=depth,
    )
    verts = ret["verts"]
    bmesh.ops.translate(bm, vec=Vector(offset), verts=verts)
    return verts


def bevel_all(bm, offset, segments=2):
    bmesh.ops.bevel(
        bm,
        geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
        offset=offset,
        offset_type='OFFSET',
        segments=segments,
        profile=0.5,
        affect='EDGES',
        clamp_overlap=True,
    )


def box_object(name, size, location, coll, material=None, rotation=(0, 0, 0), bevel=0.0):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bm_box(bm, size)
    if bevel > 0.0:
        bevel_all(bm, bevel)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    return add_object(name, me, coll, location, rotation,
                      materials=() if material is None else (material,))


# --------------------------------------------------------------------------- #
#  Materials
# --------------------------------------------------------------------------- #
def principled(name, color, roughness=0.5, metallic=0.0, ior_level=None):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if ior_level is not None and "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = ior_level
    return mat


def emission_material(name, color, strength):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    emi = nt.nodes.new("ShaderNodeEmission")
    emi.inputs["Color"].default_value = (color[0], color[1], color[2], 1.0)
    emi.inputs["Strength"].default_value = strength
    emi.location = (-200, 0)
    nt.links.new(emi.outputs["Emission"], out.inputs["Surface"])
    return mat


PALETTES = [
    [(0.86, 0.24, 0.16), (0.95, 0.72, 0.22), (0.12, 0.16, 0.28), (0.92, 0.90, 0.84)],
    [(0.08, 0.22, 0.35), (0.25, 0.55, 0.62), (0.80, 0.84, 0.82), (0.05, 0.06, 0.09)],
    [(0.72, 0.68, 0.60), (0.40, 0.30, 0.22), (0.16, 0.14, 0.13), (0.88, 0.82, 0.70)],
    [(0.35, 0.12, 0.42), (0.78, 0.30, 0.52), (0.96, 0.86, 0.55), (0.10, 0.10, 0.16)],
    [(0.10, 0.35, 0.22), (0.55, 0.70, 0.35), (0.90, 0.88, 0.76), (0.20, 0.18, 0.14)],
    [(0.95, 0.95, 0.93), (0.72, 0.10, 0.12), (0.10, 0.11, 0.14), (0.55, 0.56, 0.58)],
]


def artwork_material(idx):
    """Procedural abstract canvas: texture -> colour ramp -> base colour."""
    mat = bpy.data.materials.new("ArtCanvas_%02d" % idx)
    mat.use_nodes = True
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    bsdf = nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = random.uniform(0.5, 0.75)
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.25

    coord = nodes.new("ShaderNodeTexCoord")
    coord.location = (-1000, 0)
    mapping = nodes.new("ShaderNodeMapping")
    mapping.location = (-800, 0)
    mapping.inputs["Rotation"].default_value = (0.0, 0.0, random.uniform(0.0, math.pi))
    s = random.uniform(1.2, 3.0)
    mapping.inputs["Scale"].default_value = (s, s * random.uniform(0.6, 1.6), s)
    links.new(coord.outputs["Generated"], mapping.inputs["Vector"])

    style = idx % 3
    if style == 0:
        tex = nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = random.uniform(2.0, 6.0)
        tex.inputs["Detail"].default_value = random.uniform(4.0, 9.0)
        tex.inputs["Roughness"].default_value = 0.55
        fac = tex.outputs["Fac"]
    elif style == 1:
        tex = nodes.new("ShaderNodeTexWave")
        tex.wave_type = 'BANDS'
        tex.bands_direction = 'X'
        tex.inputs["Scale"].default_value = random.uniform(1.5, 4.0)
        tex.inputs["Distortion"].default_value = random.uniform(1.0, 6.0)
        tex.inputs["Detail"].default_value = 3.0
        fac = tex.outputs["Fac"]
    else:
        tex = nodes.new("ShaderNodeTexVoronoi")
        tex.feature = 'F1'
        tex.inputs["Scale"].default_value = random.uniform(2.5, 6.0)
        fac = tex.outputs["Distance"]
    tex.location = (-600, 0)
    links.new(mapping.outputs["Vector"], tex.inputs["Vector"])

    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.location = (-380, 0)
    cr = ramp.color_ramp
    cr.interpolation = random.choice(['LINEAR', 'CONSTANT', 'EASE'])
    palette = list(random.choice(PALETTES))
    random.shuffle(palette)
    while len(cr.elements) > 2:
        cr.elements.remove(cr.elements[-1])
    positions = [0.0, 0.34, 0.62, 0.85]
    for i, col in enumerate(palette):
        el = cr.elements[i] if i < len(cr.elements) else cr.elements.new(positions[i])
        el.position = positions[i]
        el.color = (col[0], col[1], col[2], 1.0)
    links.new(fac, ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    return mat


# --------------------------------------------------------------------------- #
#  Architecture
# --------------------------------------------------------------------------- #
def build_shell(coll, mats):
    x, y, t = ROOM_X, ROOM_Y, WALL_T
    outer_x, outer_y = 2.0 * (x + t), 2.0 * (y + t)

    box_object("Floor", (outer_x, outer_y, 0.20), (0, 0, -0.10), coll, mats["floor"])
    box_object("Ceiling", (outer_x, outer_y, 0.30),
               (0, 0, CEIL_H + 0.15), coll, mats["ceiling"])

    box_object("Wall_North", (outer_x, t, CEIL_H), (0, y + t / 2, CEIL_H / 2), coll, mats["wall"])
    box_object("Wall_South", (outer_x, t, CEIL_H), (0, -y - t / 2, CEIL_H / 2), coll, mats["wall"])
    box_object("Wall_East", (t, 2 * y, CEIL_H), (x + t / 2, 0, CEIL_H / 2), coll, mats["wall"])
    box_object("Wall_West", (t, 2 * y, CEIL_H), (-x - t / 2, 0, CEIL_H / 2), coll, mats["wall"])

    # skirting boards, standing slightly proud of the wall faces
    sk_h, sk_d = 0.13, 0.05
    box_object("Skirt_N", (2 * x, sk_d, sk_h), (0, y - sk_d / 2, sk_h / 2), coll, mats["trim"])
    box_object("Skirt_S", (2 * x, sk_d, sk_h), (0, -y + sk_d / 2, sk_h / 2), coll, mats["trim"])
    box_object("Skirt_E", (sk_d, 2 * y, sk_h), (x - sk_d / 2, 0, sk_h / 2), coll, mats["trim"])
    box_object("Skirt_W", (sk_d, 2 * y, sk_h), (-x + sk_d / 2, 0, sk_h / 2), coll, mats["trim"])


def build_partition(name, centre, size, coll, mats):
    """Free-standing partition with a darker cap and a floor shadow-gap plinth."""
    cx, cy = centre
    sx, sy = size
    box_object(name, (sx, sy, PART_H), (cx, cy, PART_H / 2), coll, mats["wall"])
    box_object(name + "_Cap", (sx + 0.04, sy + 0.04, 0.06),
               (cx, cy, PART_H + 0.03), coll, mats["trim"])
    box_object(name + "_Plinth", (sx + 0.05, sy + 0.05, 0.10),
               (cx, cy, 0.05), coll, mats["trim"])


# --------------------------------------------------------------------------- #
#  Framed artwork
# --------------------------------------------------------------------------- #
def make_artwork(name, centre, normal, width, height, coll, frame_mat, art_mat, mats):
    """Frame + canvas + wall label, built in local space with +Z = outward normal."""
    n = Vector(normal).normalized()
    quat = n.to_track_quat('Z', 'Y')
    fw = random.uniform(0.055, 0.095)     # frame face width
    fd = random.uniform(0.06, 0.11)       # frame depth off the wall

    me = bpy.data.meshes.new(name + "_Frame")
    bm = bmesh.new()
    bm_box(bm, (width, fw, fd), (0.0, (height - fw) / 2.0, fd / 2.0))
    bm_box(bm, (width, fw, fd), (0.0, -(height - fw) / 2.0, fd / 2.0))
    inner_h = height - 2.0 * fw
    bm_box(bm, (fw, inner_h, fd), ((width - fw) / 2.0, 0.0, fd / 2.0))
    bm_box(bm, (fw, inner_h, fd), (-(width - fw) / 2.0, 0.0, fd / 2.0))
    bevel_all(bm, min(0.010, fw * 0.2))
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    frame = add_object(name + "_Frame", me, coll, materials=(frame_mat,))
    frame.location = Vector(centre)
    frame.rotation_euler = quat.to_euler()

    # canvas / print, recessed a little inside the frame rebate
    cme = bpy.data.meshes.new(name + "_Canvas")
    bm = bmesh.new()
    bm_box(bm, (width - 2.0 * fw + 0.012, inner_h + 0.012, 0.022),
           (0.0, 0.0, fd * 0.42))
    bm.normal_update()
    bm.to_mesh(cme)
    bm.free()
    canvas = add_object(name + "_Canvas", cme, coll, materials=(art_mat,))
    canvas.location = Vector(centre)
    canvas.rotation_euler = quat.to_euler()

    # wall label to the lower right of the frame
    lme = bpy.data.meshes.new(name + "_Label")
    bm = bmesh.new()
    bm_box(bm, (0.16, 0.11, 0.006),
           (width / 2.0 + 0.20, -height / 2.0 + 0.06, 0.004))
    bm.normal_update()
    bm.to_mesh(lme)
    bm.free()
    label = add_object(name + "_Label", lme, coll, materials=(mats["label"],))
    label.location = Vector(centre)
    label.rotation_euler = quat.to_euler()

    return frame


def wall_run(tag, p0, p1, normal, count, coll, frame_mats, mats, z_centre=1.62):
    """Evenly space `count` artworks between two points lying on a wall face."""
    a, b = Vector(p0), Vector(p1)
    centres = []
    for i in range(count):
        t = (i + 0.5) / count
        pos = a.lerp(b, t)
        w = random.uniform(0.85, 1.55)
        h = w * random.uniform(0.62, 1.25)
        h = min(h, 1.85)
        c = Vector((pos.x, pos.y, z_centre))
        idx = len(bpy.data.materials)
        make_artwork("Art_%s_%d" % (tag, i), c, normal, w, h, coll,
                     random.choice(frame_mats), artwork_material(idx), mats)
        centres.append(c)
    return centres


# --------------------------------------------------------------------------- #
#  Ceiling track lighting
# --------------------------------------------------------------------------- #
def build_track(name, p0, p1, coll, mat):
    a, b = Vector(p0), Vector(p1)
    d = b - a
    length = d.length
    yaw = math.atan2(d.y, d.x)
    mid = (a + b) / 2.0
    rail = box_object(name, (length, 0.075, 0.055),
                      (mid.x, mid.y, CEIL_H - 0.028), coll, mat,
                      rotation=(0.0, 0.0, yaw))
    for end in (a, b):
        box_object(name + "_End", (0.07, 0.10, 0.09),
                   (end.x, end.y, CEIL_H - 0.05), coll, mat,
                   rotation=(0.0, 0.0, yaw))
    return rail


def build_track_head(name, pos, target, coll, mats, energy=170.0):
    pos = Vector(pos)
    aim = (Vector(target) - pos).normalized()
    quat = aim.to_track_quat('-Z', 'Y')
    euler = quat.to_euler()

    # drop stem from the rail down to the head pivot
    sme = bpy.data.meshes.new(name + "_Stem")
    bm = bmesh.new()
    bm_cyl(bm, 0.022, 0.20, (0.0, 0.0, 0.10), segments=12)
    bm.normal_update()
    bm.to_mesh(sme)
    bm.free()
    stem = add_object(name + "_Stem", sme, coll, (pos.x, pos.y, pos.z),
                      materials=(mats["fixture"],))
    shade_smooth(stem)

    # barrel body, aimed along local -Z
    hme = bpy.data.meshes.new(name + "_Head")
    bm = bmesh.new()
    bm_cyl(bm, 0.052, 0.06, (0.0, 0.0, -0.03), segments=16)          # knuckle
    bm_cyl(bm, 0.078, 0.24, (0.0, 0.0, -0.18), segments=24)          # barrel
    bm_cyl(bm, 0.090, 0.06, (0.0, 0.0, -0.32), segments=24,
           radius_top=0.080)                                          # snoot ring
    bm.normal_update()
    bm.to_mesh(hme)
    bm.free()
    head = add_object(name + "_Head", hme, coll, pos, euler,
                      materials=(mats["fixture"],))
    shade_smooth(head)

    lme = bpy.data.meshes.new(name + "_Lens")
    bm = bmesh.new()
    bm_cyl(bm, 0.072, 0.008, (0.0, 0.0, -0.336), segments=24)
    bm.normal_update()
    bm.to_mesh(lme)
    bm.free()
    lens = add_object(name + "_Lens", lme, coll, pos, euler,
                      materials=(mats["lens"],))
    shade_smooth(lens)

    light = bpy.data.lights.new(name + "_Spot", 'SPOT')
    light.energy = energy
    light.color = (1.0, 0.93, 0.84)
    light.spot_size = math.radians(38.0)
    light.spot_blend = 0.38
    light.shadow_soft_size = 0.06
    lamp = add_object(name + "_Spot", light, coll, pos, euler)
    return lamp


# --------------------------------------------------------------------------- #
#  Furniture
# --------------------------------------------------------------------------- #
def build_bench(name, location, coll, mats, rot_z=0.0, length=2.0):
    box_object(name + "_Top", (length, 0.48, 0.09),
               (location[0], location[1], 0.46), coll, mats["bench"],
               rotation=(0, 0, rot_z), bevel=0.012)
    off = length / 2.0 - 0.26
    for s in (-1.0, 1.0):
        lx = location[0] + math.cos(rot_z) * off * s
        ly = location[1] + math.sin(rot_z) * off * s
        box_object(name + "_Leg", (0.10, 0.40, 0.42), (lx, ly, 0.21), coll,
                   mats["metal"], rotation=(0, 0, rot_z))


def build_plinth(name, location, coll, mats):
    box_object(name, (0.62, 0.62, 1.05),
               (location[0], location[1], 0.525), coll, mats["plinth"], bevel=0.008)
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.26, minor_radius=0.085,
        major_segments=56, minor_segments=20,
        location=(location[0], location[1], 1.32),
        rotation=(math.radians(68.0), 0.0, math.radians(25.0)),
    )
    sculpt = bpy.context.object
    for c in list(sculpt.users_collection):
        c.objects.unlink(sculpt)
    coll.objects.link(sculpt)
    sculpt.name = name + "_Sculpture"
    sculpt.data.materials.append(mats["bronze"])
    shade_smooth(sculpt)


# --------------------------------------------------------------------------- #
#  Build
# --------------------------------------------------------------------------- #
def main():
    scn = reset_scene()

    arch = make_collection("Architecture")
    art = make_collection("Artworks")
    lighting = make_collection("Lighting")
    furniture = make_collection("Furniture")

    mats = {
        "wall": principled("GalleryWall", (0.895, 0.888, 0.870), 0.82, 0.0, 0.25),
        "ceiling": principled("Ceiling", (0.80, 0.80, 0.80), 0.90),
        "floor": principled("PolishedConcrete", (0.245, 0.243, 0.238), 0.28, 0.0, 0.6),
        "trim": principled("Trim", (0.16, 0.16, 0.17), 0.55),
        "label": principled("Label", (0.95, 0.94, 0.92), 0.75),
        "fixture": principled("FixtureMetal", (0.055, 0.055, 0.058), 0.35, 0.9),
        "lens": emission_material("LensGlow", (1.0, 0.94, 0.85), 22.0),
        "bench": principled("BenchOak", (0.42, 0.30, 0.18), 0.45),
        "metal": principled("BrushedSteel", (0.62, 0.63, 0.65), 0.32, 1.0),
        "plinth": principled("Plinth", (0.93, 0.92, 0.90), 0.62),
        "bronze": principled("Bronze", (0.44, 0.29, 0.13), 0.30, 1.0),
    }
    frame_mats = [
        principled("Frame_Gilt", (0.72, 0.55, 0.22), 0.28, 1.0),
        principled("Frame_Walnut", (0.16, 0.09, 0.055), 0.42),
        principled("Frame_Black", (0.035, 0.035, 0.038), 0.40),
        principled("Frame_Alu", (0.66, 0.67, 0.69), 0.25, 1.0),
    ]

    build_shell(arch, mats)

    partitions = [
        ("Partition_A", (-2.0, -3.0), (PART_T, 6.0)),
        ("Partition_B", (3.0, 2.5), (PART_T, 7.0)),
        ("Partition_C", (-6.25, 3.0), (3.5, PART_T)),
    ]
    for name, centre, size in partitions:
        build_partition(name, centre, size, arch, mats)

    half = PART_T / 2.0 + 0.002
    runs = [
        # (tag, p0, p1, outward normal, count)
        ("N", (-7.4, ROOM_Y), (7.4, ROOM_Y), (0, -1, 0), 5),
        ("S", (-6.0, -ROOM_Y), (6.0, -ROOM_Y), (0, 1, 0), 4),
        ("W", (-ROOM_X, -5.0), (-ROOM_X, 0.6), (1, 0, 0), 3),
        ("E", (ROOM_X, -3.6), (ROOM_X, 3.6), (-1, 0, 0), 3),
        ("A1", (-2.0 + half, -5.5), (-2.0 + half, -0.5), (1, 0, 0), 2),
        ("A2", (-2.0 - half, -5.5), (-2.0 - half, -0.5), (-1, 0, 0), 2),
        ("B1", (3.0 - half, -0.6), (3.0 - half, 5.6), (-1, 0, 0), 2),
        ("B2", (3.0 + half, -0.6), (3.0 + half, 5.6), (1, 0, 0), 2),
        ("C1", (-7.7, 3.0 - half), (-4.8, 3.0 - half), (0, -1, 0), 2),
    ]

    for tag, p0, p1, normal, count in runs:
        centres = wall_run(tag, p0, p1, normal, count, art, frame_mats, mats)
        n = Vector(normal).normalized()
        offset = n * 1.25
        a = Vector((p0[0], p0[1], 0.0)) + offset
        b = Vector((p1[0], p1[1], 0.0)) + offset
        ext = (b - a).normalized() * 0.45
        build_track("Track_%s" % tag,
                    (a - ext).to_tuple()[:2] + (0.0,),
                    (b + ext).to_tuple()[:2] + (0.0,),
                    lighting, mats["fixture"])
        for i, c in enumerate(centres):
            head = Vector((c.x, c.y, CEIL_H - 0.25)) + offset
            target = c + n * 0.05
            build_track_head("Head_%s_%d" % (tag, i), head, target, lighting, mats)

    build_bench("Bench_A", (-5.4, -2.4), furniture, mats, rot_z=0.0, length=2.2)
    build_bench("Bench_B", (6.0, 1.2), furniture, mats,
                rot_z=math.radians(90.0), length=2.0)
    build_plinth("Plinth_A", (0.4, -1.6), furniture, mats)

    # soft ambient fill so the gallery does not go black between the spots
    for i, pos in enumerate(((-4.5, 2.0), (4.5, -2.0))):
        fill = bpy.data.lights.new("Fill_%d" % i, 'AREA')
        fill.shape = 'RECTANGLE'
        fill.size, fill.size_y = 7.0, 5.0
        fill.energy = 70.0
        fill.color = (0.93, 0.95, 1.0)
        fill.diffuse_factor = 1.0
        fill.specular_factor = 0.15
        add_object("Fill_%d" % i, fill, lighting,
                   (pos[0], pos[1], CEIL_H - 0.12), (0.0, 0.0, 0.0))

    cam_data = bpy.data.cameras.new("GalleryCam")
    cam_data.lens = 28.0
    cam_data.sensor_width = 36.0
    cam_data.clip_start = 0.05
    cam_data.clip_end = 200.0
    cam_data.dof.use_dof = True
    cam_data.dof.aperture_fstop = 4.0
    cam_loc = Vector((6.6, -5.2, 1.68))
    cam_target = Vector((-1.6, 1.2, 1.62))
    cam = add_object("GalleryCam", cam_data, bpy.context.scene.collection, cam_loc)
    cam.rotation_euler = (cam_target - cam_loc).to_track_quat('-Z', 'Y').to_euler()
    cam_data.dof.focus_distance = (cam_target - cam_loc).length
    scn.camera = cam

    scn.render.resolution_x = 1920
    scn.render.resolution_y = 1080
    scn.render.film_transparent = False


if __name__ == "__main__":
    main()
