"""claude-016 - Bus shelter with roof, bench and transparent side panels.

Builds the scene only: no rendering, no file output, no external assets.
"""

import bpy
import bmesh
import math
from mathutils import Vector


# ----------------------------------------------------------------------------
# generic helpers
# ----------------------------------------------------------------------------

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = 'METRIC'


def new_material(name, base=(0.8, 0.8, 0.8), metallic=0.0, rough=0.5,
                 transmission=0.0, alpha=1.0, ior=1.45,
                 emission=None, emit_strength=0.0, coat=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")

    def put(key, value):
        if bsdf and key in bsdf.inputs:
            bsdf.inputs[key].default_value = value

    put("Base Color", (base[0], base[1], base[2], 1.0))
    put("Metallic", metallic)
    put("Roughness", rough)
    put("IOR", ior)
    put("Transmission Weight", transmission)
    put("Alpha", alpha)
    put("Coat Weight", coat)
    if emission is not None:
        put("Emission Color", (emission[0], emission[1], emission[2], 1.0))
        put("Emission Strength", emit_strength)
    if alpha < 1.0 or transmission > 0.0:
        try:
            mat.blend_method = 'BLEND'
        except Exception:
            pass
    return mat


def shade_auto(ob, angle=math.radians(35.0)):
    """Smooth shading with sharp edges above `angle` (4.x sharp-edge workflow)."""
    me = ob.data
    for poly in me.polygons:
        poly.use_smooth = True
    bm = bmesh.new()
    bm.from_mesh(me)
    for edge in bm.edges:
        if len(edge.link_faces) == 2:
            edge.smooth = edge.calc_face_angle() < angle
        else:
            edge.smooth = False
    bm.to_mesh(me)
    bm.free()


def _finish(bm, name, loc, rot, mat, smooth, smooth_angle):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = rot
    bpy.context.collection.objects.link(ob)
    if mat is not None:
        me.materials.append(mat)
    if smooth:
        shade_auto(ob, smooth_angle)
    return ob


def add_box(name, size, loc=(0, 0, 0), rot=(0, 0, 0), mat=None,
            bevel=0.0, seg=2, smooth=False):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    if bevel > 0.0:
        bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                        offset=bevel, offset_type='OFFSET', segments=seg,
                        profile=0.5, affect='EDGES', clamp_overlap=True)
    return _finish(bm, name, loc, rot, mat, smooth, math.radians(35.0))


def add_cyl(name, radius, depth, loc=(0, 0, 0), rot=(0, 0, 0), mat=None,
            segments=32, bevel=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius, radius2=radius, depth=depth)
    if bevel > 0.0:
        bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                        offset=bevel, offset_type='OFFSET', segments=2,
                        profile=0.5, affect='EDGES', clamp_overlap=True)
    return _finish(bm, name, loc, rot, mat, True, math.radians(40.0))


def add_sphere(name, radius, loc=(0, 0, 0), mat=None, useg=32, vseg=16,
               scale=(1, 1, 1)):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=useg, v_segments=vseg, radius=radius)
    bmesh.ops.scale(bm, vec=Vector(scale), verts=bm.verts)
    return _finish(bm, name, loc, (0, 0, 0), mat, True, math.radians(60.0))


def aim(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def add_light(name, ltype, loc, energy, color=(1.0, 1.0, 1.0), size=1.0,
              target=None):
    data = bpy.data.lights.new(name, ltype)
    data.energy = energy
    data.color = color
    if ltype == 'AREA':
        data.size = size
    elif ltype == 'SUN':
        data.angle = math.radians(2.0)
    else:
        data.shadow_soft_size = size
    ob = bpy.data.objects.new(name, data)
    ob.location = loc
    bpy.context.collection.objects.link(ob)
    if target is not None:
        aim(ob, target)
    return ob


def setup_world(color=(0.35, 0.45, 0.6), strength=1.0):
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (color[0], color[1], color[2], 1.0)
    bg.inputs[1].default_value = strength


def add_camera(loc, target, lens=45.0, name="Camera"):
    data = bpy.data.cameras.new(name)
    data.lens = lens
    ob = bpy.data.objects.new(name, data)
    ob.location = loc
    bpy.context.collection.objects.link(ob)
    aim(ob, target)
    bpy.context.scene.camera = ob
    return ob


# ----------------------------------------------------------------------------
# build
# ----------------------------------------------------------------------------

reset_scene()
setup_world((0.36, 0.46, 0.62), 1.1)

CONCRETE = new_material("Concrete", (0.52, 0.51, 0.49), rough=0.88)
ASPHALT = new_material("Asphalt", (0.055, 0.055, 0.062), rough=0.92)
STEEL = new_material("BrushedSteel", (0.63, 0.65, 0.68), metallic=1.0, rough=0.3)
DARKMET = new_material("DarkMetal", (0.07, 0.075, 0.08), metallic=0.9, rough=0.42)
GLASS = new_material("SafetyGlass", (0.74, 0.84, 0.82), rough=0.02,
                     transmission=1.0, alpha=0.16, ior=1.52)
WOOD = new_material("BenchWood", (0.33, 0.19, 0.10), rough=0.52)
POSTER = new_material("LitPoster", (0.9, 0.9, 0.88),
                      emission=(0.98, 0.95, 0.85), emit_strength=3.2)
STRIP = new_material("CeilingStrip", (0.9, 0.9, 0.9),
                     emission=(1.0, 0.97, 0.9), emit_strength=6.0)
SIGNBLUE = new_material("SignBlue", (0.05, 0.16, 0.48), rough=0.35, coat=0.4)
SIGNWHITE = new_material("SignWhite", (0.92, 0.92, 0.9), rough=0.4)

# shelter footprint
W, D, H = 3.60, 1.50, 2.32
hx, hy = W * 0.5, D * 0.5

# ---- ground ---------------------------------------------------------------
add_box("Pavement", (16.0, 5.2, 0.2), (0.0, 0.0, -0.1), mat=CONCRETE)
add_box("Kerb", (16.0, 0.18, 0.16), (0.0, -2.55, -0.02), mat=CONCRETE, bevel=0.012)
add_box("Road", (16.0, 8.0, 0.2), (0.0, -6.7, -0.19), mat=ASPHALT)
add_box("RoadMark", (2.2, 0.14, 0.01), (1.0, -5.4, -0.083), mat=SIGNWHITE)
add_box("RoadMark2", (2.2, 0.14, 0.01), (-4.0, -5.4, -0.083), mat=SIGNWHITE)
add_box("TactilePad", (3.4, 0.9, 0.02), (0.0, -2.0, -0.005), mat=CONCRETE)

# ---- frame ----------------------------------------------------------------
post_positions = [(-hx + 0.06, hy - 0.06), (hx - 0.06, hy - 0.06),
                  (-hx + 0.06, -hy + 0.06), (hx - 0.06, -hy + 0.06),
                  (0.0, hy - 0.06)]
for i, (px, py) in enumerate(post_positions):
    add_box("Post_%d" % i, (0.085, 0.085, H), (px, py, H * 0.5),
            mat=STEEL, bevel=0.008)
    add_box("PostFoot_%d" % i, (0.16, 0.16, 0.03), (px, py, 0.015),
            mat=DARKMET, bevel=0.004)

# horizontal rails (top and bottom of the glazing)
for z, tag in ((2.26, "Top"), (0.32, "Bot")):
    add_box("RailBack%s" % tag, (W - 0.12, 0.07, 0.07), (0.0, hy - 0.06, z),
            mat=STEEL, bevel=0.008)
    for sx in (-1, 1):
        add_box("RailSide%s_%d" % (tag, sx), (0.07, D - 0.12, 0.07),
                (sx * (hx - 0.06), 0.0, z), mat=STEEL, bevel=0.008)

# ---- transparent panels ---------------------------------------------------
# back glazing: three panes separated by slim mullions
pane_w = (W - 0.22) / 3.0
for i in range(3):
    cx = -hx + 0.11 + pane_w * (i + 0.5)
    add_box("BackPane_%d" % i, (pane_w - 0.03, 0.012, 1.86),
            (cx, hy - 0.06, 1.29), mat=GLASS)
for sx in (-1, 1):
    add_box("Mullion_%d" % sx, (0.04, 0.06, 1.92),
            (sx * pane_w * 0.5, hy - 0.06, 1.29), mat=STEEL, bevel=0.005)
    # side glazing
    add_box("SidePane_%d" % sx, (0.012, D - 0.16, 1.86),
            (sx * (hx - 0.06), 0.0, 1.29), mat=GLASS)

# partial front wind panel on the right hand side
add_box("FrontPane", (0.85, 0.012, 1.86), (hx - 0.52, -hy + 0.06, 1.29), mat=GLASS)
add_box("FrontEdge", (0.05, 0.07, 1.92), (hx - 0.945, -hy + 0.06, 1.29),
        mat=STEEL, bevel=0.006)

# ---- roof -----------------------------------------------------------------
roof_tilt = math.radians(3.5)
add_box("Roof", (W + 0.34, D + 0.30, 0.055), (0.0, -0.04, H + 0.06),
        rot=(roof_tilt, 0, 0), mat=STEEL, bevel=0.012)
add_box("RoofFascia", (W + 0.34, 0.055, 0.16), (0.0, -(hy + 0.13), H + 0.02),
        mat=DARKMET, bevel=0.008)
add_box("RoofCeiling", (W - 0.02, D - 0.02, 0.02), (0.0, -0.02, H - 0.02),
        rot=(roof_tilt, 0, 0), mat=new_material("Ceiling", (0.78, 0.78, 0.76),
                                                rough=0.6))
for sx in (-1, 1):
    add_box("LightStrip_%d" % sx, (1.35, 0.11, 0.018),
            (sx * 0.86, 0.02, H - 0.045), mat=STRIP)

# roof gutter downpipe at one end
add_cyl("Downpipe", 0.035, H, (hx - 0.06, hy + 0.11, H * 0.5), mat=DARKMET,
        segments=20)

# ---- bench ----------------------------------------------------------------
seat_z = 0.46
for i in range(4):
    add_box("SeatSlat_%d" % i, (W - 0.62, 0.085, 0.032),
            (0.0, 0.20 + i * 0.115, seat_z), mat=WOOD, bevel=0.008)
for i in range(2):
    add_box("BackSlat_%d" % i, (W - 0.62, 0.075, 0.03),
            (0.0, hy - 0.14, 0.76 + i * 0.155), rot=(math.radians(-8), 0, 0),
            mat=WOOD, bevel=0.007)
for bx in (-1.28, 0.0, 1.28):
    add_box("BenchLeg_%.2f" % bx, (0.05, 0.05, seat_z - 0.03),
            (bx, 0.24, (seat_z - 0.03) * 0.5), mat=STEEL, bevel=0.005)
    add_box("BenchArm_%.2f" % bx, (0.05, 0.46, 0.05), (bx, 0.40, seat_z - 0.045),
            mat=STEEL, bevel=0.005)
    add_box("BenchBrace_%.2f" % bx, (0.045, 0.045, 0.42),
            (bx, hy - 0.10, seat_z + 0.19), mat=STEEL, bevel=0.005)

# ---- timetable / info panel on the left side glazing ----------------------
add_box("InfoFrame", (0.03, 0.60, 0.85), (-hx + 0.10, 0.06, 1.48),
        mat=DARKMET, bevel=0.006)
add_box("InfoPoster", (0.008, 0.53, 0.78), (-hx + 0.122, 0.06, 1.48), mat=POSTER)

# ---- litter bin -----------------------------------------------------------
add_cyl("Bin", 0.185, 0.72, (hx + 0.55, -0.30, 0.36), mat=DARKMET,
        segments=28, bevel=0.01)
add_cyl("BinRim", 0.20, 0.05, (hx + 0.55, -0.30, 0.735), mat=STEEL, segments=28,
        bevel=0.008)
add_cyl("BinMouth", 0.16, 0.02, (hx + 0.55, -0.30, 0.745),
        mat=new_material("BinHole", (0.02, 0.02, 0.02), rough=0.9), segments=24)

# ---- bus stop sign --------------------------------------------------------
add_cyl("SignPole", 0.035, 2.70, (hx + 1.15, -0.55, 1.35), mat=STEEL, segments=20)
add_cyl("SignDisc", 0.29, 0.028, (hx + 1.15, -0.62, 2.52),
        rot=(math.radians(90), 0, 0), mat=SIGNBLUE, segments=48)
add_cyl("SignInner", 0.235, 0.012, (hx + 1.15, -0.645, 2.52),
        rot=(math.radians(90), 0, 0), mat=SIGNWHITE, segments=48)
add_box("SignBusBody", (0.24, 0.008, 0.13), (hx + 1.15, -0.655, 2.53),
        mat=SIGNBLUE, bevel=0.01)
for i, ox in enumerate((-0.07, 0.07)):
    add_cyl("SignWheel_%d" % i, 0.022, 0.008, (hx + 1.15 + ox, -0.662, 2.462),
            rot=(math.radians(90), 0, 0), mat=SIGNBLUE, segments=16)

# ---- lighting -------------------------------------------------------------
sun = add_light("Sun", 'SUN', (-6.0, -7.0, 9.0), 3.4, (1.0, 0.96, 0.88),
                target=(0.0, 0.2, 1.0))
add_light("SkyFill", 'AREA', (2.0, -6.5, 5.0), 900.0, (0.72, 0.82, 1.0),
          size=9.0, target=(0.0, 0.3, 1.1))
add_light("InteriorBounce", 'AREA', (0.0, 0.1, 2.15), 60.0, (1.0, 0.95, 0.85),
          size=2.6, target=(0.0, 0.1, 0.4))

# ---- camera ---------------------------------------------------------------
add_camera((6.4, -6.9, 2.95), (0.1, 0.15, 1.22), lens=45.0)

bpy.context.view_layer.update()
