"""claude-099 - A traditional mailbox on a post with flag.

The tunnel shaped body is an arch profile swept along Y and thickened with a
solidify modifier so the interior is hollow, the front door hangs open on its
bottom hinge, and the semaphore flag is raised on a pivot empty.  Sits on a
wooden post in a small patch of ground, sunlit with a sky world.
"""

import bpy
import bmesh
import math
from mathutils import Vector


# --------------------------------------------------------------------------
# generic helpers
# --------------------------------------------------------------------------
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = 'METRIC'


def make_world(color=(0.28, 0.42, 0.62), strength=1.2):
    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (*color, 1.0)
    bg.inputs[1].default_value = strength
    bpy.context.scene.world = world
    return world


def mat_pbr(name, color, metallic=0.0, roughness=0.5):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def assign(obj, mat):
    if mat is not None:
        obj.data.materials.append(mat)
    return obj


def box(name, size, loc, mat=None, rot=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    ob.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return assign(ob, mat)


def cyl(name, radius, depth, loc, mat=None, rot=(0.0, 0.0, 0.0), verts=24):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth,
                                        vertices=verts, location=loc,
                                        rotation=rot)
    ob = bpy.context.object
    ob.name = name
    return assign(ob, mat)


def cone(name, r1, r2, depth, loc, mat=None, rot=(0.0, 0.0, 0.0), verts=12):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=depth,
                                    vertices=verts, location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    return assign(ob, mat)


def bevel_mod(obj, width=0.004, segments=2, angle=40.0):
    m = obj.modifiers.new("Bevel", 'BEVEL')
    m.width = width
    m.segments = segments
    m.limit_method = 'ANGLE'
    m.angle_limit = math.radians(angle)
    return obj


def smooth(obj, angle=40.0):
    try:
        for o in bpy.context.selected_objects:
            o.select_set(False)
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.shade_auto_smooth(angle=math.radians(angle))
    except Exception:
        for p in obj.data.polygons:
            p.use_smooth = True
    return obj


def look_at(obj, target):
    d = Vector(target) - obj.location
    obj.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


# --------------------------------------------------------------------------
# geometry constants
# --------------------------------------------------------------------------
HW = 0.098               # mailbox half width
SIDE_H = 0.085           # straight side wall height
BOX_LEN = 0.470          # front to back length
BOX_Z0 = 1.325           # floor of the mailbox in world Z
Y_FRONT = -BOX_LEN / 2.0
Y_BACK = BOX_LEN / 2.0
ARC_SEGS = 14


def arch_profile():
    """Open polyline in the XZ plane: up the left wall, over the arch, down."""
    pts = [(-HW, 0.0), (-HW, SIDE_H)]
    for i in range(ARC_SEGS + 1):
        a = math.pi - math.pi * i / ARC_SEGS
        pts.append((HW * math.cos(a), SIDE_H + HW * math.sin(a)))
    pts.append((HW, SIDE_H))
    pts.append((HW, 0.0))
    return pts


def build_materials():
    return {
        "paint": mat_pbr("MailboxPaint", (0.16, 0.17, 0.19), 0.25, 0.36),
        "paint_in": mat_pbr("MailboxInner", (0.30, 0.31, 0.33), 0.20, 0.55),
        "red": mat_pbr("FlagRed", (0.62, 0.06, 0.05), 0.05, 0.35),
        "steel": mat_pbr("Steel", (0.55, 0.56, 0.58), 1.0, 0.35),
        "chrome": mat_pbr("Chrome", (0.82, 0.83, 0.85), 1.0, 0.18),
        "wood": mat_pbr("PostWood", (0.42, 0.30, 0.19), 0.0, 0.72),
        "wood_dark": mat_pbr("PostWoodDark", (0.33, 0.23, 0.14), 0.0, 0.78),
        "paper": mat_pbr("Envelope", (0.90, 0.88, 0.82), 0.0, 0.62),
        "stamp": mat_pbr("Stamp", (0.72, 0.55, 0.25), 0.0, 0.55),
        "grass": mat_pbr("Grass", (0.20, 0.32, 0.13), 0.0, 0.85),
        "grass2": mat_pbr("GrassTuft", (0.26, 0.40, 0.16), 0.0, 0.85),
        "dirt": mat_pbr("Dirt", (0.26, 0.20, 0.14), 0.0, 0.90),
        "plaque": mat_pbr("Plaque", (0.88, 0.88, 0.86), 0.0, 0.40),
        "digit": mat_pbr("Digit", (0.08, 0.08, 0.09), 0.0, 0.50),
    }


# --------------------------------------------------------------------------
# mailbox body
# --------------------------------------------------------------------------
def build_body(M):
    pts = arch_profile()
    bm = bmesh.new()
    row_f = [bm.verts.new((p[0], Y_FRONT, BOX_Z0 + p[1])) for p in pts]
    row_b = [bm.verts.new((p[0], Y_BACK, BOX_Z0 + p[1])) for p in pts]
    for i in range(len(pts) - 1):
        bm.faces.new((row_f[i], row_f[i + 1], row_b[i + 1], row_b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    me = bpy.data.meshes.new("MailboxShell")
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    shell = bpy.data.objects.new("MailboxShell", me)
    bpy.context.collection.objects.link(shell)
    assign(shell, M["paint"])

    sol = shell.modifiers.new("Solidify", 'SOLIDIFY')
    sol.thickness = 0.010
    sol.offset = 1.0
    smooth(shell, 30.0)

    parts = [shell]

    # floor pan of the box
    floor = box("MailboxFloor", (2 * HW + 0.02, BOX_LEN, 0.012),
                (0.0, 0.0, BOX_Z0 - 0.006), M["paint"])
    bevel_mod(floor, 0.003, 2)
    parts.append(floor)
    parts.append(box("MailboxFloorIn", (2 * HW - 0.014, BOX_LEN - 0.02, 0.004),
                     (0.0, 0.0, BOX_Z0 + 0.003), M["paint_in"]))

    # rear cap plate, matching the arch outline
    bm2 = bmesh.new()
    cap_pts = pts + [(HW, 0.0), (-HW, 0.0)]
    cverts = [bm2.verts.new((p[0], Y_BACK + 0.006, BOX_Z0 + p[1]))
              for p in pts]
    bm2.faces.new(cverts)
    bmesh.ops.recalc_face_normals(bm2, faces=bm2.faces)
    me2 = bpy.data.meshes.new("MailboxBack")
    bm2.normal_update()
    bm2.to_mesh(me2)
    bm2.free()
    back = bpy.data.objects.new("MailboxBack", me2)
    bpy.context.collection.objects.link(back)
    assign(back, M["paint"])
    sol2 = back.modifiers.new("Solidify", 'SOLIDIFY')
    sol2.thickness = 0.012
    sol2.offset = 1.0
    smooth(back, 30.0)
    parts.append(back)

    # front rim the door closes against
    rim_pts = pts
    bm3 = bmesh.new()
    outer = [bm3.verts.new((p[0], Y_FRONT - 0.004, BOX_Z0 + p[1]))
             for p in rim_pts]
    inner = [bm3.verts.new((p[0] * 0.86, Y_FRONT - 0.004,
                            BOX_Z0 + 0.010 + p[1] * 0.90)) for p in rim_pts]
    for i in range(len(rim_pts) - 1):
        bm3.faces.new((outer[i], outer[i + 1], inner[i + 1], inner[i]))
    bmesh.ops.recalc_face_normals(bm3, faces=bm3.faces)
    me3 = bpy.data.meshes.new("MailboxRim")
    bm3.normal_update()
    bm3.to_mesh(me3)
    bm3.free()
    rim = bpy.data.objects.new("MailboxRim", me3)
    bpy.context.collection.objects.link(rim)
    assign(rim, M["paint"])
    sol3 = rim.modifiers.new("Solidify", 'SOLIDIFY')
    sol3.thickness = 0.008
    sol3.offset = -1.0
    smooth(rim, 30.0)
    parts.append(rim)

    # stiffening ribs along the arch
    for y in (-0.10, 0.10):
        ribs = []
        bmr = bmesh.new()
        rv = [bmr.verts.new((p[0] * 1.02, y, BOX_Z0 + p[1] * 1.02))
              for p in pts]
        for i in range(len(rv) - 1):
            bmr.edges.new((rv[i], rv[i + 1]))
        mer = bpy.data.meshes.new("Rib")
        bmr.to_mesh(mer)
        bmr.free()
        rib = bpy.data.objects.new("Rib", mer)
        bpy.context.collection.objects.link(rib)
        assign(rib, M["paint"])
        sk = rib.modifiers.new("Skin", 'SKIN')
        for v in rib.data.skin_vertices[0].data:
            v.radius = (0.005, 0.005)
        smooth(rib, 40.0)
        parts.append(rib)

    # house number plaque on the left flank
    plaque = box("Plaque", (0.006, 0.130, 0.048), (-HW - 0.008, 0.05,
                                                   BOX_Z0 + 0.058),
                 M["plaque"])
    parts.append(plaque)
    for i, dy in enumerate((-0.040, 0.000, 0.040)):
        parts.append(box("Digit_%d" % i, (0.004, 0.018, 0.030),
                         (-HW - 0.013, 0.05 + dy, BOX_Z0 + 0.058),
                         M["digit"]))
    return parts


def build_door(M):
    """Arch shaped door hinged along its bottom front edge."""
    pts = arch_profile()
    bm = bmesh.new()
    verts = [bm.verts.new((p[0] * 0.985, 0.0, p[1] * 0.985)) for p in pts]
    bm.faces.new(verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges), offset=0.004,
                    segments=2, affect='EDGES', clamp_overlap=True)
    me = bpy.data.meshes.new("MailboxDoor")
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    door = bpy.data.objects.new("MailboxDoor", me)
    bpy.context.collection.objects.link(door)
    assign(door, M["paint"])
    sol = door.modifiers.new("Solidify", 'SOLIDIFY')
    sol.thickness = 0.012
    sol.offset = -1.0
    smooth(door, 30.0)

    hinge = bpy.data.objects.new("DoorHinge", None)
    hinge.empty_display_type = 'PLAIN_AXES'
    hinge.empty_display_size = 0.06
    bpy.context.collection.objects.link(hinge)
    hinge.location = (0.0, Y_FRONT - 0.016, BOX_Z0 - 0.004)
    bpy.context.view_layer.update()

    parts = [door]
    # knob and lip on the outer face of the door
    knob = cyl("DoorKnob", 0.017, 0.026, (0.0, -0.024, SIDE_H + 0.030),
               M["chrome"], rot=(math.radians(90.0), 0.0, 0.0), verts=20)
    smooth(knob)
    parts.append(knob)
    parts.append(box("DoorLip", (0.10, 0.020, 0.012), (0.0, -0.020, 0.004),
                     M["paint"]))
    for sx in (-1, 1):
        parts.append(cyl("HingePin_%d" % (sx + 1), 0.006, 0.020,
                         (sx * (HW - 0.014), -0.006, 0.004), M["steel"],
                         rot=(0.0, math.radians(90.0), 0.0), verts=12))

    inv = hinge.matrix_world.inverted()
    for ob in parts:
        ob.parent = hinge
        ob.matrix_parent_inverse = inv
    hinge.rotation_euler = (math.radians(98.0), 0.0, 0.0)
    parts.append(hinge)
    return parts


def build_flag(M):
    pivot_x = HW + 0.010
    pivot = bpy.data.objects.new("FlagPivot", None)
    pivot.empty_display_type = 'PLAIN_AXES'
    pivot.empty_display_size = 0.05
    bpy.context.collection.objects.link(pivot)
    pivot.location = (pivot_x, Y_FRONT + 0.085, BOX_Z0 + 0.045)
    bpy.context.view_layer.update()

    parts = []
    bolt = cyl("FlagBolt", 0.011, 0.020, (pivot_x + 0.002,
                                          Y_FRONT + 0.085, BOX_Z0 + 0.045),
               M["steel"], rot=(0.0, math.radians(90.0), 0.0), verts=16)
    smooth(bolt)
    parts.append(bolt)

    arm = box("FlagArm", (0.007, 0.022, 0.175),
              (pivot_x + 0.006, Y_FRONT + 0.085, BOX_Z0 + 0.130), M["red"])
    bevel_mod(arm, 0.002, 2)
    parts.append(arm)

    blade = box("FlagBlade", (0.007, 0.090, 0.072),
                (pivot_x + 0.006, Y_FRONT + 0.122, BOX_Z0 + 0.238), M["red"])
    bevel_mod(blade, 0.004, 3)
    smooth(blade)
    parts.append(blade)

    parts.append(box("FlagBrace", (0.006, 0.050, 0.012),
                     (pivot_x + 0.006, Y_FRONT + 0.100, BOX_Z0 + 0.198),
                     M["red"]))

    inv = pivot.matrix_world.inverted()
    for ob in parts:
        ob.parent = pivot
        ob.matrix_parent_inverse = inv
    pivot.rotation_euler = (math.radians(-4.0), 0.0, 0.0)  # flag raised
    parts.append(pivot)
    return parts


def build_mail(M):
    """An envelope resting inside, poking through the open door."""
    parts = []
    env = box("Envelope", (0.115, 0.190, 0.008),
              (0.005, Y_FRONT + 0.055, BOX_Z0 + 0.026), M["paper"],
              rot=(math.radians(-9.0), 0.0, math.radians(4.0)))
    bevel_mod(env, 0.002, 2)
    parts.append(env)
    parts.append(box("Stamp", (0.026, 0.032, 0.002),
                     (0.043, Y_FRONT - 0.015, BOX_Z0 + 0.044), M["stamp"],
                     rot=(math.radians(-9.0), 0.0, math.radians(4.0))))
    parts.append(box("Envelope2", (0.110, 0.175, 0.006),
                     (-0.012, Y_FRONT + 0.115, BOX_Z0 + 0.014), M["paper"],
                     rot=(0.0, 0.0, math.radians(-6.0))))
    return parts


def build_post(M):
    parts = []
    post = box("Post", (0.092, 0.092, 1.34), (0.0, 0.06, 0.66), M["wood"])
    bevel_mod(post, 0.005, 2)
    parts.append(post)

    # cross board carrying the mailbox
    board = box("CrossBoard", (0.240, 0.520, 0.040), (0.0, 0.0, 1.302),
                M["wood"])
    bevel_mod(board, 0.005, 2)
    parts.append(board)

    # diagonal brace from post to board
    brace = box("Brace", (0.060, 0.230, 0.032), (0.0, -0.130, 1.190),
                M["wood_dark"], rot=(math.radians(38.0), 0.0, 0.0))
    bevel_mod(brace, 0.004, 2)
    parts.append(brace)

    for sx in (-1, 1):
        parts.append(cyl("Screw_%d" % (sx + 1), 0.007, 0.012,
                         (sx * 0.075, 0.20, 1.322), M["steel"], verts=10))

    # ground mound and turf
    bpy.ops.mesh.primitive_plane_add(size=14.0, location=(0.0, 0.0, 0.0))
    ground = bpy.context.object
    ground.name = "Ground"
    assign(ground, M["grass"])
    parts.append(ground)

    mound = cyl("Mound", 0.24, 0.055, (0.0, 0.06, 0.020), M["dirt"], verts=24)
    smooth(mound)
    parts.append(mound)

    tufts = [(-0.30, -0.10, 0.16), (0.28, 0.22, 0.13), (-0.18, 0.34, 0.18),
             (0.36, -0.26, 0.11), (0.05, -0.38, 0.15), (-0.42, 0.10, 0.12)]
    for i, (x, y, h) in enumerate(tufts):
        t = cone("Tuft_%d" % i, 0.045, 0.004, h, (x, y, h / 2.0), M["grass2"],
                 verts=6, rot=(math.radians(6.0 * (i - 3)), 0.0, 0.0))
        parts.append(t)
    return parts


def build_lighting():
    sun_data = bpy.data.lights.new("Sun", 'SUN')
    sun_data.energy = 4.0
    sun_data.angle = math.radians(1.6)
    sun_data.color = (1.0, 0.95, 0.86)
    sun = bpy.data.objects.new("Sun", sun_data)
    sun.location = (-3.0, -2.5, 5.0)
    bpy.context.collection.objects.link(sun)
    look_at(sun, (0.0, 0.0, 1.3))

    fill_data = bpy.data.lights.new("Bounce", 'AREA')
    fill_data.energy = 60.0
    fill_data.size = 2.5
    fill = bpy.data.objects.new("BounceLight", fill_data)
    fill.location = (1.8, -1.4, 0.9)
    bpy.context.collection.objects.link(fill)
    look_at(fill, (0.0, -0.1, 1.35))


def build_camera():
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = 55.0
    cam = bpy.data.objects.new("Camera", cam_data)
    cam.location = (1.10, -1.45, 1.72)
    bpy.context.collection.objects.link(cam)
    look_at(cam, (0.0, -0.06, 1.34))
    bpy.context.scene.camera = cam
    return cam


def main():
    reset_scene()
    make_world((0.30, 0.45, 0.66), 1.1)
    M = build_materials()

    objs = []
    objs += build_post(M)
    objs += build_body(M)
    objs += build_door(M)
    objs += build_mail(M)
    objs += build_flag(M)

    build_lighting()
    build_camera()

    print("claude-099: mailbox built with %d objects" % len(objs))


if __name__ == "__main__":
    main()
