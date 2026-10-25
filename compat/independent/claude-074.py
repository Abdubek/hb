import bpy
import math
from mathutils import Vector

# ---------------------------------------------------------------- utilities

def reset_scene():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for me in list(bpy.data.meshes):
        bpy.data.meshes.remove(me)


def make_mat(name, color, rough=0.6, metal=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    return mat


def _finish(ob, name, mat, parent):
    ob.name = name
    ob.data.name = name
    if mat:
        ob.data.materials.append(mat)
    if parent:
        ob.parent = parent
        ob.matrix_parent_inverse = parent.matrix_world.inverted()
    return ob


def box(name, dims, loc, rot=(0, 0, 0), mat=None, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
    ob = bpy.context.object
    ob.scale = dims
    return _finish(ob, name, mat, parent)


def cyl(name, r, h, loc, rot=(0, 0, 0), verts=16, mat=None, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, vertices=verts,
                                        location=loc, rotation=rot)
    return _finish(bpy.context.object, name, mat, parent)


def empty(name, loc):
    ob = bpy.data.objects.new(name, None)
    ob.empty_display_size = 0.4
    ob.location = loc
    bpy.context.scene.collection.objects.link(ob)
    return ob

# ---------------------------------------------------------------- materials

SAND = make_mat("Sand", (0.86, 0.78, 0.60), rough=0.95)
POLE = make_mat("AluPole", (0.72, 0.73, 0.75), rough=0.35, metal=1.0)
FRAME = make_mat("ChairFrame", (0.92, 0.92, 0.90), rough=0.45)
SLING = make_mat("ChairSling", (0.10, 0.32, 0.48), rough=0.85)
TEAK = make_mat("Teak", (0.55, 0.36, 0.20), rough=0.7)
CANOPY = [make_mat("CanopyRed", (0.78, 0.15, 0.12), rough=0.8),
          make_mat("CanopyCream", (0.94, 0.90, 0.78), rough=0.8),
          make_mat("CanopyTeal", (0.08, 0.52, 0.50), rough=0.8)]

# ---------------------------------------------------------------- assemblies

def build_umbrella(idx, origin, canopy_mat):
    grp = empty("Umbrella_%d" % idx, origin)
    x, y = origin[0], origin[1]
    cyl("UmbrellaPole_%d" % idx, 0.035, 2.55, (x, y, 1.275), verts=12,
        mat=POLE, parent=grp)
    bpy.ops.mesh.primitive_cone_add(radius1=1.65, radius2=0.14, depth=0.55,
                                    vertices=12, location=(x, y, 2.30))
    _finish(bpy.context.object, "UmbrellaCanopy_%d" % idx, canopy_mat, grp)
    # scalloped hem ring and top finial
    bpy.ops.mesh.primitive_torus_add(major_radius=1.63, minor_radius=0.05,
                                     major_segments=12, minor_segments=8,
                                     location=(x, y, 2.03))
    _finish(bpy.context.object, "UmbrellaHem_%d" % idx, canopy_mat, grp)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.075, segments=12, ring_count=8,
                                         location=(x, y, 2.63))
    _finish(bpy.context.object, "UmbrellaFinial_%d" % idx, POLE, grp)
    cyl("UmbrellaHub_%d" % idx, 0.09, 0.12, (x, y, 1.70), verts=12,
        mat=POLE, parent=grp)
    cyl("UmbrellaBase_%d" % idx, 0.36, 0.10, (x, y, 0.05), verts=20,
        mat=POLE, parent=grp)
    return grp


def build_lounger(name, loc, z_rot, parent):
    ang = math.radians(z_rot)
    grp = empty(name, loc)
    grp.rotation_euler = (0.0, 0.0, ang)
    grp.parent = parent
    grp.matrix_parent_inverse = parent.matrix_world.inverted()
    bpy.context.view_layer.update()

    def part(sub, dims, ploc, prot=(0, 0, 0), mat=FRAME):
        world = grp.matrix_world @ Vector(ploc)
        return box("%s_%s" % (name, sub), dims, world,
                   (prot[0], prot[1], prot[2] + ang), mat, grp)

    part("Seat", (0.62, 1.15, 0.07), (0.0, 0.0, 0.42), mat=SLING)
    tilt = math.radians(55.0)
    part("Back", (0.62, 0.80, 0.06),
         (0.0, 0.50 + 0.40 * math.cos(tilt), 0.42 + 0.40 * math.sin(tilt)),
         (tilt, 0, 0), mat=SLING)
    part("RailL", (0.05, 1.20, 0.10), (-0.32, 0.0, 0.40))
    part("RailR", (0.05, 1.20, 0.10), (0.32, 0.0, 0.40))
    for i, (lx, ly) in enumerate(((-0.29, -0.48), (0.29, -0.48),
                                  (-0.29, 0.46), (0.29, 0.46))):
        part("Leg%d" % i, (0.05, 0.05, 0.38), (lx, ly, 0.19))
    part("Armrest", (0.72, 0.06, 0.05), (0.0, 0.20, 0.60))
    return grp


def build_set(idx, x):
    grp = empty("BeachSet_%d" % idx, (x, 0.0, 0.0))
    u = build_umbrella(idx, (x, 0.55, 0.0), CANOPY[idx % len(CANOPY)])
    u.parent = grp
    u.matrix_parent_inverse = grp.matrix_world.inverted()
    build_lounger("Lounger_%dL" % idx, (x - 1.05, -0.15, 0.0), 8.0, grp)
    build_lounger("Lounger_%dR" % idx, (x + 1.05, -0.15, 0.0), -8.0, grp)
    cyl("SideTable_%d" % idx, 0.22, 0.05, (x, -1.15, 0.44), verts=16,
        mat=TEAK, parent=grp)
    cyl("SideTableLeg_%d" % idx, 0.04, 0.42, (x, -1.15, 0.21), verts=10,
        mat=POLE, parent=grp)
    return grp


def add_camera(loc, target, lens=45.0):
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = lens
    cam = bpy.data.objects.new("Camera", cam_data)
    bpy.context.scene.collection.objects.link(cam)
    cam.location = loc
    direction = Vector(target) - Vector(loc)
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam
    return cam

# ---------------------------------------------------------------- scene

reset_scene()

bpy.ops.mesh.primitive_plane_add(size=30.0, location=(0, 0, 0))
_finish(bpy.context.object, "BeachGround", SAND, None)

for i, x in enumerate((-4.4, 0.0, 4.4)):
    build_set(i, x)

sun_data = bpy.data.lights.new("Sun", type='SUN')
sun_data.energy = 4.0
sun = bpy.data.objects.new("Sun", sun_data)
sun.location = (6.0, -6.0, 12.0)
sun.rotation_euler = (math.radians(48), 0.0, math.radians(38))
bpy.context.scene.collection.objects.link(sun)

world = bpy.data.worlds.new("BeachWorld")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.45, 0.66, 0.88, 1.0)
bpy.context.scene.world = world

add_camera((7.8, -10.5, 4.6), (0.0, 0.0, 1.35))
