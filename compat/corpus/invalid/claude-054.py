# claude-054 : Satellite with solar wings and a high-gain dish antenna
# Blender 4.5 LTS - headless scene construction only (no render, no save)

import bpy
import bmesh
import math
from mathutils import Vector, Euler

# ----------------------------------------------------------------------------
# scene reset
# ----------------------------------------------------------------------------

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    try:
        scene.render.engine = 'BLENDER_EEVEE_NEXT'
    except TypeError:
        scene.render.engine = 'CYCLES'
    scene.unit_settings.system = 'METRIC'
    return scene


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------

def set_in(node, name, value):
    if name in node.inputs:
        node.inputs[name].default_value = value


def make_material(name, color, metallic=0.0, roughness=0.5,
                  emission=None, emission_strength=0.0, ior=1.45):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        bsdf = mat.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
    set_in(bsdf, "Base Color", (*color, 1.0))
    set_in(bsdf, "Metallic", metallic)
    set_in(bsdf, "Roughness", roughness)
    set_in(bsdf, "IOR", ior)
    if emission is not None:
        set_in(bsdf, "Emission Color", (*emission, 1.0))
        set_in(bsdf, "Emission Strength", emission_strength)
    return mat


def link(ob):
    bpy.context.scene.collection.objects.link(ob)
    return ob


def mesh_from_bmesh(name, bm, mats=()):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    for m in mats:
        ob.data.materials.append(m)
    return link(ob)


def assign(ob, *mats):
    ob.data.materials.clear()
    for m in mats:
        ob.data.materials.append(m)
    return ob


def smooth(ob, angle=40.0):
    for p in ob.data.polygons:
        p.use_smooth = True
    mod = ob.modifiers.new("EdgeSplit", 'EDGE_SPLIT')
    mod.split_angle = math.radians(angle)
    mod.use_edge_angle = True
    mod.use_edge_sharp = False
    return ob


def bevel(ob, width=0.02, segments=2, angle=40.0):
    mod = ob.modifiers.new("Bevel", 'BEVEL')
    mod.width = width
    mod.segments = segments
    mod.limit_method = 'ANGLE'
    mod.angle_limit = math.radians(angle)
    mod.harden_normals = False
    return ob


def add_cube(name, size, loc, rot=(0.0, 0.0, 0.0), mat=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    ob.scale = size
    if mat:
        ob.data.materials.append(mat)
    return ob


def add_cylinder(name, radius, depth, loc, rot=(0.0, 0.0, 0.0), segs=24, mat=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=segs,
                                        location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    if mat:
        ob.data.materials.append(mat)
    smooth(ob)
    return ob


def add_cone(name, r1, r2, depth, loc, rot=(0.0, 0.0, 0.0), segs=20, mat=None):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=depth,
                                    vertices=segs, location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    if mat:
        ob.data.materials.append(mat)
    smooth(ob)
    return ob


def add_sphere(name, radius, loc, mat=None, segs=24, rings=12):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, segments=segs,
                                         ring_count=rings, location=loc)
    ob = bpy.context.object
    ob.name = name
    if mat:
        ob.data.materials.append(mat)
    smooth(ob, 60.0)
    return ob


def add_tube(name, p1, p2, radius, mat=None, segs=10):
    """Cylinder spanning two world-space points (struts, booms, masts)."""
    a, b = Vector(p1), Vector(p2)
    d = b - a
    length = d.length
    if length < 1e-6:
        return None
    rot = Vector((0.0, 0.0, 1.0)).rotation_difference(d.normalized()).to_euler()
    return add_cylinder(name, radius, length, (a + b) * 0.5, rot, segs, mat)


# ----------------------------------------------------------------------------
# materials
# ----------------------------------------------------------------------------

MLI_GOLD = make_material("MLI_Gold", (0.82, 0.55, 0.13), metallic=1.0, roughness=0.34)
MLI_DARK = make_material("MLI_Bronze", (0.35, 0.22, 0.07), metallic=1.0, roughness=0.45)
RADIATOR = make_material("Radiator_White", (0.86, 0.87, 0.88), metallic=0.0, roughness=0.32)
ALU = make_material("Aluminium", (0.62, 0.63, 0.65), metallic=1.0, roughness=0.28)
STRUCT = make_material("Structure_Grey", (0.40, 0.41, 0.44), metallic=0.85, roughness=0.42)
BLACK_ANO = make_material("Black_Anodised", (0.035, 0.035, 0.04), metallic=0.7, roughness=0.35)
SOLAR_CELL = make_material("Solar_Cell", (0.012, 0.035, 0.11), metallic=0.75, roughness=0.18)
PANEL_FRAME = make_material("Panel_Frame", (0.55, 0.56, 0.58), metallic=1.0, roughness=0.36)
PANEL_BACK = make_material("Panel_Back", (0.72, 0.70, 0.66), metallic=0.2, roughness=0.62)
DISH_FACE = make_material("Dish_Face", (0.90, 0.90, 0.91), metallic=0.35, roughness=0.20)
DISH_BACK = make_material("Dish_Back", (0.78, 0.52, 0.14), metallic=1.0, roughness=0.40)
LENS_GLOW = make_material("Sensor_Lens", (0.02, 0.03, 0.05), metallic=0.9, roughness=0.08,
                          emission=(0.15, 0.35, 0.6), emission_strength=1.5)


# ----------------------------------------------------------------------------
# spacecraft bus
# ----------------------------------------------------------------------------

BUS = Vector((1.30, 1.10, 1.55))          # full X/Y/Z extents of the main body
HX, HY, HZ = BUS.x * 0.5, BUS.y * 0.5, BUS.z * 0.5


def build_bus():
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, verts=bm.verts, vec=BUS)
    bm.faces.ensure_lookup_table()
    # gold MLI on the ends, white radiator panels on the four sides
    for f in bm.faces:
        f.material_index = 0 if abs(f.normal.z) > 0.7 else 1
    ob = mesh_from_bmesh("Satellite_Bus", bm, (MLI_GOLD, RADIATOR))
    bevel(ob, width=0.035, segments=3)

    # equipment / launch-adapter ring on the -Z face
    ring = add_cylinder("Adapter_Ring", 0.42, 0.16, (0.0, 0.0, -HZ - 0.07), segs=32, mat=STRUCT)
    bevel(ring, 0.02, 2)

    # louvre strips on the -Y radiator for a bit of surface interest
    for i in range(5):
        y = -HY - 0.012
        z = -0.55 + i * 0.28
        strip = add_cube("Louvre_%d" % i, (BUS.x * 0.78, 0.03, 0.14),
                         (0.0, y, z), mat=ALU)
        bevel(strip, 0.008, 2)

    # avionics box + star tracker on the +Y wall
    box = add_cube("Avionics_Box", (0.42, 0.22, 0.34), (0.32, HY + 0.10, 0.36), mat=MLI_DARK)
    bevel(box, 0.02, 2)
    tracker = add_cylinder("Star_Tracker", 0.11, 0.30, (-0.34, HY + 0.16, 0.48),
                           rot=(math.radians(70.0), 0.0, 0.0), segs=20, mat=BLACK_ANO)
    baffle = add_cone("Tracker_Baffle", 0.115, 0.15, 0.20,
                      (-0.34, HY + 0.28, 0.60), rot=(math.radians(70.0), 0.0, 0.0),
                      segs=20, mat=BLACK_ANO)

    # thrusters on the aft (-Z) corners
    for sx in (-1, 1):
        for sy in (-1, 1):
            add_cone("Thruster_%d%d" % (sx, sy), 0.028, 0.075, 0.17,
                     (sx * (HX - 0.16), sy * (HY - 0.16), -HZ - 0.09),
                     rot=(math.pi, 0.0, 0.0), segs=16, mat=ALU)

    # magnetometer boom trailing off -X
    add_tube("Mag_Boom", (-HX, 0.0, -0.45), (-HX - 1.45, 0.0, -0.62), 0.022, STRUCT, 10)
    add_cube("Magnetometer", (0.11, 0.11, 0.16), (-HX - 1.52, 0.0, -0.63), mat=BLACK_ANO)
    return ob


# ----------------------------------------------------------------------------
# solar wings
# ----------------------------------------------------------------------------

PANEL_X = 1.22       # chord  (along X)
PANEL_Y = 1.15       # span per section (along Y)
PANEL_T = 0.035
GAP = 0.035
YOKE = 0.55


def build_panel(name, loc):
    """A framed photovoltaic section: grid of inset cells on both faces."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, verts=bm.verts, vec=(PANEL_X, PANEL_Y, PANEL_T))

    flats = [f for f in bm.faces if abs(f.normal.z) > 0.9]
    edges = {e for f in flats for e in f.edges}
    bmesh.ops.subdivide_edges(bm, edges=list(edges), cuts=3, use_grid_fill=True)

    bm.faces.ensure_lookup_table()
    top = [f for f in bm.faces if f.normal.z > 0.9]
    bot = [f for f in bm.faces if f.normal.z < -0.9]
    for f in bm.faces:
        f.material_index = 0                      # frame / structure

    bmesh.ops.inset_individual(bm, faces=top, thickness=0.022, depth=-0.004,
                               use_even_offset=True)
    for f in top:
        f.material_index = 1                      # cells, sun side
    bmesh.ops.inset_individual(bm, faces=bot, thickness=0.022, depth=-0.003,
                               use_even_offset=True)
    for f in bot:
        f.material_index = 2                      # substrate, shadow side

    ob = mesh_from_bmesh(name, bm, (PANEL_FRAME, SOLAR_CELL, PANEL_BACK))
    ob.location = loc
    return ob


def build_wing(side):
    """side = +1 (+Y wing) or -1 (-Y wing)."""
    tag = "P" if side > 0 else "M"
    root = side * (HY + YOKE)

    # drive motor and yoke arms out to the wing root
    add_cylinder("SADA_%s" % tag, 0.17, 0.24, (0.0, side * (HY + 0.10), 0.0),
                 rot=(math.radians(90.0), 0.0, 0.0), segs=24, mat=ALU)
    for sx in (-1, 1):
        add_tube("Yoke_%s%d" % (tag, sx),
                 (sx * 0.10, side * (HY + 0.14), 0.0),
                 (sx * PANEL_X * 0.33, root, 0.0), 0.035, STRUCT, 10)

    for i in range(4):
        y = root + side * (PANEL_Y * 0.5 + i * (PANEL_Y + GAP))
        build_panel("SolarPanel_%s%d" % (tag, i), (0.0, y, 0.0))
        if i < 3:                                  # hinge line between sections
            hy = y + side * (PANEL_Y * 0.5 + GAP * 0.5)
            for sx in (-1, 1):
                add_cylinder("Hinge_%s%d_%d" % (tag, i, sx), 0.032, 0.11,
                             (sx * PANEL_X * 0.35, hy, 0.0),
                             rot=(math.radians(90.0), 0.0, 0.0), segs=12, mat=ALU)


# ----------------------------------------------------------------------------
# high-gain parabolic antenna
# ----------------------------------------------------------------------------

DISH_R = 0.95
DISH_D = 0.30                                     # rim depth
FOCAL = DISH_R ** 2 / (4.0 * DISH_D)
DISH_ORIGIN = Vector((HX + 0.72, 0.0, 0.30))      # dish vertex, boresight along +X


def build_dish():
    rings, segs = 9, 48
    bm = bmesh.new()
    centre = bm.verts.new((0.0, 0.0, 0.0))
    grid = []
    for i in range(1, rings + 1):
        r = DISH_R * i / rings
        z = r * r / (4.0 * FOCAL)
        grid.append([bm.verts.new((r * math.cos(2.0 * math.pi * j / segs),
                                   r * math.sin(2.0 * math.pi * j / segs), z))
                     for j in range(segs)])
    bm.verts.ensure_lookup_table()
    for j in range(segs):
        k = (j + 1) % segs
        bm.faces.new((centre, grid[0][j], grid[0][k]))
        for i in range(rings - 1):
            bm.faces.new((grid[i][j], grid[i + 1][j], grid[i + 1][k], grid[i][k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    ob = mesh_from_bmesh("HGA_Reflector", bm, (DISH_FACE, DISH_BACK))
    ob.location = DISH_ORIGIN
    ob.rotation_euler = Euler((0.0, math.radians(90.0), 0.0), 'XYZ')   # +Z -> +X
    for p in ob.data.polygons:
        p.use_smooth = True
    sol = ob.modifiers.new("Solidify", 'SOLIDIFY')
    sol.thickness = 0.025
    sol.offset = -1.0
    sol.use_rim = True
    sol.material_offset = 1
    sol.material_offset_rim = 1

    def to_world(local):
        x, y, z = local
        return DISH_ORIGIN + Vector((z, y, -x))    # 90 deg about Y

    focus = to_world((0.0, 0.0, FOCAL))

    # feed horn at the focus, looking back into the reflector
    horn_dir = (to_world((0.0, 0.0, 0.0)) - focus).normalized()
    horn_rot = Vector((0.0, 0.0, 1.0)).rotation_difference(horn_dir).to_euler()
    add_cone("Feed_Horn", 0.055, 0.145, 0.30, focus + horn_dir * 0.16,
             rot=horn_rot, segs=24, mat=MLI_GOLD)
    add_cylinder("Feed_Body", 0.075, 0.20, focus - horn_dir * 0.08,
                 rot=horn_rot, segs=20, mat=ALU)

    # tripod struts from rim to feed
    for k in range(3):
        a = 2.0 * math.pi * k / 3.0 + math.radians(30.0)
        rim = to_world((DISH_R * math.cos(a) * 0.94, DISH_R * math.sin(a) * 0.94, DISH_D * 0.88))
        add_tube("HGA_Strut_%d" % k, rim, focus - horn_dir * 0.14, 0.017, STRUCT, 8)

    # two-axis gimbal and support mast back to the bus
    mast_base = Vector((HX + 0.06, 0.0, 0.30))
    add_tube("HGA_Mast", mast_base, DISH_ORIGIN - Vector((0.10, 0.0, 0.0)), 0.055, STRUCT, 14)
    add_sphere("HGA_Gimbal", 0.13, mast_base + Vector((0.16, 0.0, 0.0)), ALU, 20, 12)
    add_cylinder("HGA_Backing", 0.20, 0.14, DISH_ORIGIN - Vector((0.09, 0.0, 0.0)),
                 rot=(0.0, math.radians(90.0), 0.0), segs=20, mat=MLI_DARK)
    return ob


def build_secondary_antennas():
    # steerable medium-gain dish on top
    small = add_cone("MGA_Dish", 0.34, 0.30, 0.05, (-0.30, -0.18, HZ + 0.44),
                     rot=(math.radians(-28.0), 0.0, 0.0), segs=32, mat=DISH_FACE)
    sol = small.modifiers.new("Solidify", 'SOLIDIFY')
    sol.thickness = 0.02
    add_tube("MGA_Mast", (-0.30, -0.18, HZ), (-0.30, -0.18, HZ + 0.36), 0.04, STRUCT, 10)
    add_sphere("MGA_Hub", 0.07, (-0.30, -0.18, HZ + 0.38), ALU, 16, 10)
    add_cone("MGA_Feed", 0.03, 0.06, 0.13, (-0.30, -0.06, HZ + 0.66),
             rot=(math.radians(-28.0), 0.0, 0.0), segs=16, mat=MLI_GOLD)

    # omni low-gain whips
    for sx, sy in ((1, 1), (-1, -1)):
        base = (sx * (HX - 0.18), sy * (HY - 0.18), HZ)
        tip = (sx * (HX - 0.18), sy * (HY - 0.18), HZ + 0.85)
        add_tube("LGA_Whip_%d" % sx, base, tip, 0.014, ALU, 8)
        add_sphere("LGA_Tip_%d" % sx, 0.045, tip, MLI_GOLD, 16, 8)
        add_cylinder("LGA_Base_%d" % sx, 0.05, 0.08, (base[0], base[1], HZ + 0.04),
                     segs=14, mat=BLACK_ANO)

    # earth-sensor / imager aperture on the nadir (-Z) deck
    add_cylinder("Imager_Barrel", 0.16, 0.34, (0.30, -0.22, -HZ - 0.17), segs=24, mat=BLACK_ANO)
    add_cylinder("Imager_Lens", 0.135, 0.03, (0.30, -0.22, -HZ - 0.335), segs=24, mat=LENS_GLOW)


# ----------------------------------------------------------------------------
# lighting, world, camera
# ----------------------------------------------------------------------------

def build_lighting():
    world = bpy.data.worlds.new("SpaceWorld")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    set_in(bg, "Color", (0.008, 0.012, 0.025, 1.0))
    set_in(bg, "Strength", 1.0)
    bpy.context.scene.world = world

    sun_data = bpy.data.lights.new("Sun", 'SUN')
    sun_data.energy = 6.0
    sun_data.angle = math.radians(0.53)
    sun_data.color = (1.0, 0.97, 0.92)
    sun = link(bpy.data.objects.new("Sun", sun_data))
    sun.rotation_euler = Euler((math.radians(52.0), 0.0, math.radians(38.0)), 'XYZ')

    fill_data = bpy.data.lights.new("EarthFill", 'AREA')
    fill_data.energy = 260.0
    fill_data.size = 12.0
    fill_data.color = (0.35, 0.55, 0.85)
    fill = link(bpy.data.objects.new("EarthFill", fill_data))
    fill.location = (2.0, 3.0, -7.5)
    fill.rotation_euler = Euler((math.radians(-160.0), 0.0, 0.0), 'XYZ')

    rim_data = bpy.data.lights.new("RimLight", 'AREA')
    rim_data.energy = 180.0
    rim_data.size = 6.0
    rim_data.color = (0.75, 0.82, 1.0)
    rim = link(bpy.data.objects.new("RimLight", rim_data))
    rim.location = (-6.0, 5.5, 3.0)
    rim.rotation_euler = Euler((math.radians(62.0), 0.0, math.radians(-135.0)), 'XYZ')


def build_camera():
    target = link(bpy.data.objects.new("CamTarget", None))
    target.empty_display_size = 0.3
    target.location = (0.3, 0.0, 0.1)

    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = 60.0
    cam_data.clip_end = 500.0
    cam_data.dof.use_dof = True
    cam_data.dof.focus_object = target
    cam_data.dof.aperture_fstop = 6.0
    cam = link(bpy.data.objects.new("Camera", cam_data))
    cam.location = (9.0, -11.0, 5.2)

    con = cam.constraints.new('TRACK_TO')
    con.target = target
    con.track_axis = 'TRACK_NEGATIVE_Z'
    con.up_axis = 'UP_Y'
    bpy.context.scene.camera = cam
    return cam


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------

def main():
    reset_scene()
    build_bus()
    build_wing(+1)
    build_wing(-1)
    build_dish()
    build_secondary_antennas()
    build_lighting()
    build_camera()
    bpy.context.view_layer.update()


main()
