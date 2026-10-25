import bpy
import bmesh
import math
from mathutils import Vector

RIM_Z = 0.78          # height of the basin rim
BOWL_SCALE = (0.30, 0.24, 0.18)


def reset_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in list(coll):
            if item.users == 0:
                coll.remove(item)


def material(name, color, rough=0.35, metal=0.0):
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


def cyl(name, mat, radius, depth, loc, rot=(0, 0, 0), verts=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=verts,
                                        location=loc, rotation=rot)
    return finish(bpy.context.object, name, mat, smooth=True)


def box(name, mat, scale, loc, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=2.0, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.scale = scale
    return finish(obj, name, mat)


def ring(name, mat, major, minor, loc, y_squash=1.0):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                     major_segments=40, minor_segments=12, location=loc)
    obj = bpy.context.object
    obj.scale = (1.0, y_squash, 1.0)
    return finish(obj, name, mat, smooth=True)


def build_bowl(mat):
    """Open ceramic bowl: a UV sphere cut at the equator, then given wall thickness."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=36, v_segments=18, radius=1.0)
    upper = [v for v in bm.verts if v.co.z > 1e-6]
    bmesh.ops.delete(bm, geom=upper, context='VERTS')
    mesh = bpy.data.meshes.new("Basin")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("Basin", mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = (0.0, 0.0, RIM_Z)
    obj.scale = BOWL_SCALE
    solid = obj.modifiers.new("Wall", 'SOLIDIFY')
    solid.thickness = 0.02
    solid.offset = -1.0
    return finish(obj, "Basin", mat, smooth=True)


def build_faucet_arch(mat, arc_r, profile_r, loc):
    """Gooseneck: a circular profile spun 180 degrees to sweep a pipe arch."""
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=False, segments=14, radius=profile_r)
    bmesh.ops.translate(bm, verts=bm.verts, vec=(arc_r, 0.0, 0.0))
    bmesh.ops.spin(bm, geom=bm.verts[:] + bm.edges[:], cent=(0.0, 0.0, 0.0),
                   axis=(0.0, 1.0, 0.0), dvec=(0.0, 0.0, 0.0),
                   angle=-math.pi, steps=24, use_duplicate=False)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new("FaucetArch")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("FaucetArch", mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = (0.0, 0.0, math.radians(90.0))  # arch swings front-to-back
    return finish(obj, "FaucetArch", mat, smooth=True)


def add_camera(loc, target, lens=45.0):
    data = bpy.data.cameras.new("Camera")
    data.lens = lens
    cam = bpy.data.objects.new("Camera", data)
    bpy.context.collection.objects.link(cam)
    cam.location = loc
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam


def add_lights():
    sun_data = bpy.data.lights.new("Sun", 'SUN')
    sun_data.energy = 3.0
    sun = bpy.data.objects.new("Sun", sun_data)
    bpy.context.collection.objects.link(sun)
    sun.location = (2.0, -2.0, 3.0)
    sun.rotation_euler = (math.radians(50.0), 0.0, math.radians(35.0))
    fill_data = bpy.data.lights.new("Fill", 'AREA')
    fill_data.energy = 60.0
    fill_data.size = 1.5
    fill = bpy.data.objects.new("Fill", fill_data)
    bpy.context.collection.objects.link(fill)
    fill.location = (-1.2, -1.4, 1.6)
    fill.rotation_euler = (math.radians(55.0), 0.0, math.radians(-40.0))


def main():
    reset_scene()

    ceramic = material("Ceramic", (0.94, 0.94, 0.92), rough=0.12)
    chrome = material("Chrome", (0.82, 0.83, 0.85), rough=0.08, metal=1.0)
    dark = material("DarkMetal", (0.09, 0.09, 0.10), rough=0.40, metal=1.0)
    tile = material("WallTile", (0.80, 0.83, 0.84), rough=0.25)
    floor_mat = material("Floor", (0.42, 0.40, 0.38), rough=0.60)

    bpy.ops.mesh.primitive_plane_add(size=3.0, location=(0.0, 0.0, 0.0))
    finish(bpy.context.object, "Floor", floor_mat)
    box("WallPanel", tile, (0.60, 0.03, 0.75), (0.0, 0.33, 0.75))

    # pedestal column and plinth
    bpy.ops.mesh.primitive_cone_add(radius1=0.155, radius2=0.115, depth=0.62,
                                    vertices=40, location=(0.0, 0.0, 0.31))
    finish(bpy.context.object, "Pedestal", ceramic, smooth=True)
    cyl("PedestalFoot", ceramic, 0.175, 0.035, (0.0, 0.0, 0.018), verts=40)

    # bowl, rim and rear deck for the tapware
    build_bowl(ceramic)
    ring("BasinRim", ceramic, BOWL_SCALE[0], 0.018, (0.0, 0.0, RIM_Z), y_squash=0.8)
    box("FaucetDeck", ceramic, (0.22, 0.048, 0.015), (0.0, 0.27, 0.785))

    # drain assembly at the bottom of the bowl
    bowl_floor = RIM_Z - BOWL_SCALE[2] + 0.02
    ring("DrainFlange", chrome, 0.030, 0.006, (0.0, 0.0, bowl_floor + 0.004))
    cyl("DrainGrate", dark, 0.026, 0.008, (0.0, 0.0, bowl_floor + 0.002), verts=24)

    # faucet: riser, swept arch, down spout, aerator
    cyl("FaucetRiser", chrome, 0.024, 0.12, (0.0, 0.255, 0.845))
    cyl("FaucetBase", chrome, 0.038, 0.02, (0.0, 0.255, 0.795))
    build_faucet_arch(chrome, 0.14, 0.022, (0.0, 0.115, 0.90))
    cyl("FaucetSpout", chrome, 0.022, 0.07, (0.0, -0.025, 0.868))
    ring("Aerator", dark, 0.020, 0.005, (0.0, -0.025, 0.838))

    # two mixer handles
    for side, tag in ((-1, "Cold"), (1, "Hot")):
        x = side * 0.145
        cyl("HandleStem" + tag, chrome, 0.018, 0.055, (x, 0.255, 0.812))
        box("HandleLever" + tag, chrome, (0.052, 0.012, 0.008),
            (x + side * 0.03, 0.255, 0.842), rot=(0.0, math.radians(-8.0 * side), 0.0))

    add_lights()
    add_camera((0.95, -1.15, 1.32), (0.0, 0.0, 0.72))


main()
