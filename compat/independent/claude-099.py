import bpy
import bmesh
import math
from mathutils import Vector

HALF_W = 0.115      # mailbox half width
SIDE_H = 0.085      # straight side height before the arch starts
BODY_L = 0.42       # front-to-back length
POST_H = 1.05
BODY_Z = POST_H + 0.03


def reset_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in list(coll):
            if item.users == 0:
                coll.remove(item)


def material(name, color, rough=0.4, metal=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    return mat


def finish(obj, name, mat, smooth=False):
    obj.name = name
    obj.data.name = name
    obj.data.materials.append(mat)
    if smooth:
        obj.data.polygons.foreach_set("use_smooth", [True] * len(obj.data.polygons))
        obj.data.update()
    return obj


def box(name, mat, scale, loc, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=2.0, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.scale = scale
    return finish(obj, name, mat)


def cyl(name, mat, radius, depth, loc, rot=(0, 0, 0), verts=24):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=verts,
                                        location=loc, rotation=rot)
    return finish(bpy.context.object, name, mat, smooth=True)


def profile_points(half_w, side_h, segments=14):
    """Classic tunnel outline in the XZ plane: flat floor, straight sides, arched roof."""
    pts = [(-half_w, 0.0), (half_w, 0.0), (half_w, side_h)]
    for i in range(1, segments):
        a = math.pi * i / segments
        pts.append((half_w * math.cos(a), side_h + half_w * math.sin(a)))
    pts.append((-half_w, side_h))
    return pts


def bm_to_object(bm, name, loc):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = loc
    return obj


def build_body(name, mat, pts, length, thickness):
    """Extrude the outline as an open tube, cap the back, then solidify into a shell."""
    bm = bmesh.new()
    verts = [bm.verts.new((x, 0.0, z)) for x, z in pts]
    n = len(verts)
    edges = [bm.edges.new((verts[i], verts[(i + 1) % n])) for i in range(n)]
    ret = bmesh.ops.extrude_edge_only(bm, edges=edges)
    moved = [g for g in ret["geom"] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=moved, vec=(0.0, length, 0.0))
    bmesh.ops.contextual_create(bm, geom=edges)  # rear wall
    obj = bm_to_object(bm, name, (0.0, -length * 0.5, BODY_Z))
    solid = obj.modifiers.new("Shell", 'SOLIDIFY')
    solid.thickness = thickness
    solid.offset = 1.0
    return finish(obj, name, mat, smooth=True)


def build_door(name, mat, pts, depth, loc):
    bm = bmesh.new()
    verts = [bm.verts.new((x, 0.0, z)) for x, z in pts]
    face = bm.faces.new(verts)
    ret = bmesh.ops.extrude_face_region(bm, geom=[face])
    moved = [g for g in ret["geom"] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=moved, vec=(0.0, depth, 0.0))
    return finish(bm_to_object(bm, name, loc), name, mat, smooth=True)


def add_camera(loc, target, lens=48.0):
    data = bpy.data.cameras.new("Camera")
    data.lens = lens
    cam = bpy.data.objects.new("Camera", data)
    bpy.context.collection.objects.link(cam)
    cam.location = loc
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam


def add_lights():
    sun_data = bpy.data.lights.new("Sun", 'SUN')
    sun_data.energy = 4.0
    sun = bpy.data.objects.new("Sun", sun_data)
    bpy.context.collection.objects.link(sun)
    sun.location = (2.5, -2.0, 4.0)
    sun.rotation_euler = (math.radians(48.0), math.radians(8.0), math.radians(30.0))
    fill_data = bpy.data.lights.new("Fill", 'AREA')
    fill_data.energy = 80.0
    fill_data.size = 2.0
    fill = bpy.data.objects.new("Fill", fill_data)
    bpy.context.collection.objects.link(fill)
    fill.location = (-1.6, -1.8, 1.8)
    fill.rotation_euler = (math.radians(60.0), 0.0, math.radians(-45.0))


def main():
    reset_scene()

    galv = material("GalvanizedSteel", (0.66, 0.68, 0.70), rough=0.35, metal=1.0)
    flag_red = material("FlagRed", (0.62, 0.05, 0.04), rough=0.45)
    wood = material("PostWood", (0.34, 0.21, 0.12), rough=0.75)
    dark = material("DarkTrim", (0.06, 0.06, 0.07), rough=0.50, metal=0.6)
    grass = material("Ground", (0.22, 0.32, 0.14), rough=0.85)

    bpy.ops.mesh.primitive_plane_add(size=5.0, location=(0.0, 0.0, 0.0))
    finish(bpy.context.object, "Ground", grass)

    # post, mounting board and angled braces
    box("Post", wood, (0.045, 0.045, POST_H * 0.5), (0.0, 0.0, POST_H * 0.5))
    box("MountBoard", wood, (0.105, BODY_L * 0.5, 0.015), (0.0, 0.0, POST_H + 0.015))
    for side in (-1, 1):
        box("Brace" + ("Front" if side < 0 else "Back"), wood,
            (0.030, 0.075, 0.016), (0.0, side * 0.10, POST_H - 0.085),
            rot=(math.radians(45.0 * side), 0.0, 0.0))

    pts = profile_points(HALF_W, SIDE_H)
    build_body("MailboxBody", galv, pts, BODY_L, 0.007)

    # front door plate, latch and hinge
    door_pts = profile_points(HALF_W * 0.97, SIDE_H * 0.97)
    build_door("MailboxDoor", galv, door_pts, 0.014,
               (0.0, -BODY_L * 0.5 - 0.016, BODY_Z + 0.002))
    cyl("DoorLatch", dark, 0.014, 0.03, (0.0, -BODY_L * 0.5 - 0.030, BODY_Z + 0.075),
        rot=(math.radians(90.0), 0.0, 0.0), verts=16)
    box("DoorHinge", dark, (0.075, 0.010, 0.008), (0.0, -BODY_L * 0.5 - 0.012, BODY_Z + 0.004))

    # raised signal flag on the right-hand side
    flag_x = HALF_W + 0.014
    cyl("FlagPivot", dark, 0.012, 0.012, (flag_x - 0.008, -0.13, BODY_Z + 0.03),
        rot=(0.0, math.radians(90.0), 0.0), verts=16)
    cyl("FlagRod", flag_red, 0.008, 0.21, (flag_x, -0.13, BODY_Z + 0.125), verts=12)
    box("FlagBlade", flag_red, (0.005, 0.055, 0.045), (flag_x, -0.072, BODY_Z + 0.185))

    # name plate on the side panel
    box("NamePlate", dark, (0.004, 0.13, 0.028), (-HALF_W - 0.004, 0.02, BODY_Z + 0.045))

    add_lights()
    add_camera((1.25, -1.65, 1.55), (0.0, -0.05, 1.02))


main()
