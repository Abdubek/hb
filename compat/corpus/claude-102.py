"""claude-102 - Perfume bottle presentation.

A faceted glass flacon with amber juice, a metal collar and a heavy cap sits on a
polished plinth in front of a soft gradient backdrop.  Lit with two built softboxes
(area light + visible black shell), a hard rim light behind, and photographed with a
portrait format 100mm camera.  Scene construction only.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def clean_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    if scene.world is None:
        scene.world = bpy.data.worlds.new("World")
    return scene


def to_object(name, bm, smooth=False):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        for poly in me.polygons:
            poly.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def box(name, size, location=(0, 0, 0), bevel=0.0, bevel_segments=3, smooth=False,
        taper=1.0):
    """Axis aligned box, optionally tapered towards +Z and bevelled."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    if taper != 1.0:
        for v in bm.verts:
            if v.co.z > 0.0:
                v.co.x *= taper
                v.co.y *= taper
    if bevel > 0.0:
        bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                        offset=bevel, segments=bevel_segments, profile=0.5,
                        affect='EDGES', clamp_overlap=True)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = to_object(name, bm, smooth)
    ob.location = location
    return ob


def cylinder(name, radius, depth, location=(0, 0, 0), segments=48, radius_top=None,
             bevel=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius,
                          radius2=radius if radius_top is None else radius_top,
                          depth=depth)
    if bevel > 0.0:
        bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                        offset=bevel, segments=3, profile=0.5, affect='EDGES',
                        clamp_overlap=True)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = to_object(name, bm, smooth=True)
    ob.location = location
    return ob


def pbr(name, base, metallic=0.0, roughness=0.4, extra=None):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = base
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    for key, value in (extra or {}).items():
        if key in bsdf.inputs:
            bsdf.inputs[key].default_value = value
    return mat


def emission(name, color, strength):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    for node in list(nt.nodes):
        if node.type != 'OUTPUT_MATERIAL':
            nt.nodes.remove(node)
    out = nt.nodes["Material Output"]
    emit = nt.nodes.new("ShaderNodeEmission")
    emit.location = (-250, 0)
    emit.inputs["Color"].default_value = color
    emit.inputs["Strength"].default_value = strength
    nt.links.new(emit.outputs["Emission"], out.inputs["Surface"])
    return mat


def assign(ob, mat):
    ob.data.materials.clear()
    ob.data.materials.append(mat)


def aim(ob, target):
    direction = Vector(target) - ob.location
    ob.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


def softbox(name, location, target, width, height, energy, shell_mat,
            color=(1.0, 1.0, 1.0)):
    """Area light plus a visible dark shell so it reads in the reflections."""
    data = bpy.data.lights.new(name, type='AREA')
    data.shape = 'RECTANGLE'
    data.size = width
    data.size_y = height
    data.energy = energy
    data.color = color
    light = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(light)
    light.location = location
    aim(light, target)

    shell = box(name + "_Shell", (width * 0.53, height * 0.53, 0.18), bevel=0.01)
    shell.parent = light
    shell.matrix_parent_inverse = Matrix.Identity(4)
    shell.location = (0.0, 0.0, 0.115)
    assign(shell, shell_mat)
    return light


# --------------------------------------------------------------------------- #
# hero product
# --------------------------------------------------------------------------- #
def build_bottle(glass, juice, metal, cap_mat, label_mat):
    parts = []

    body = box("Flacon_Body", (0.058, 0.030, 0.105), location=(0, 0, 0.0525),
               bevel=0.009, bevel_segments=5, taper=0.90)
    assign(body, glass)
    parts.append(body)

    liquid = box("Flacon_Juice", (0.049, 0.022, 0.072), location=(0, 0, 0.043),
                 bevel=0.007, bevel_segments=4, taper=0.94)
    assign(liquid, juice)
    parts.append(liquid)

    shoulder = cylinder("Flacon_Shoulder", 0.016, 0.016, (0, 0, 0.111), segments=48,
                        radius_top=0.011, bevel=0.002)
    assign(shoulder, glass)
    parts.append(shoulder)

    collar = cylinder("Flacon_Collar", 0.0125, 0.010, (0, 0, 0.122), segments=64,
                      bevel=0.0015)
    assign(collar, metal)
    parts.append(collar)

    cap = box("Flacon_Cap", (0.036, 0.024, 0.040), location=(0, 0, 0.147),
              bevel=0.006, bevel_segments=5)
    assign(cap, cap_mat)
    parts.append(cap)

    plaque = box("Flacon_Plaque", (0.030, 0.002, 0.016), location=(0, -0.0285, 0.052),
                 bevel=0.0012, bevel_segments=2)
    assign(plaque, label_mat)
    parts.append(plaque)

    root = bpy.data.objects.new("Perfume_Bottle", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.05
    bpy.context.scene.collection.objects.link(root)
    for part in parts:
        part.parent = root
    root.rotation_euler = (0.0, 0.0, math.radians(18.0))
    return root


def build_set(stone, backdrop_mat):
    plinth = cylinder("Plinth", 0.16, 0.05, (0.0, 0.0, -0.025), segments=72,
                      bevel=0.004)
    assign(plinth, stone)

    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=12, y_segments=12, size=3.0)
    # bend the far edge upwards into a soft seamless sweep
    for v in bm.verts:
        if v.co.y > 0.4:
            t = (v.co.y - 0.4) / 2.6
            v.co.z += (t ** 2) * 3.0
    backdrop = to_object("Backdrop", bm, smooth=True)
    backdrop.location = (0.0, 0.0, -0.05)
    assign(backdrop, backdrop_mat)
    return plinth, backdrop


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def main():
    scene = clean_scene()
    scene.render.engine = 'CYCLES'
    try:
        scene.cycles.samples = 384
        scene.cycles.use_denoising = True
        scene.cycles.transmission_bounces = 24
        scene.cycles.transparent_max_bounces = 24
    except AttributeError:
        pass
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 1800
    scene.view_settings.view_transform = 'AgX'

    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.012, 0.012, 0.015, 1.0)

    glass = pbr("Flacon Glass", (0.92, 0.94, 0.95, 1.0), 0.0, 0.02,
                {"Transmission Weight": 1.0, "IOR": 1.52, "Roughness": 0.02})
    juice = pbr("Amber Juice", (0.72, 0.35, 0.06, 1.0), 0.0, 0.03,
                {"Transmission Weight": 1.0, "IOR": 1.36})
    metal = pbr("Polished Gold", (0.90, 0.70, 0.32, 1.0), 1.0, 0.10)
    cap_mat = pbr("Cap Lacquer", (0.045, 0.040, 0.038, 1.0), 0.0, 0.12,
                  {"Coat Weight": 1.0, "Coat Roughness": 0.03})
    label_mat = pbr("Brushed Plaque", (0.78, 0.66, 0.40, 1.0), 1.0, 0.28)
    stone = pbr("Polished Stone", (0.045, 0.046, 0.050, 1.0), 0.0, 0.08,
                {"Coat Weight": 0.8})
    backdrop_mat = pbr("Backdrop", (0.09, 0.10, 0.13, 1.0), 0.0, 0.65)
    shell_mat = pbr("Softbox Shell", (0.01, 0.01, 0.01, 1.0), 0.0, 0.7)

    build_set(stone, backdrop_mat)
    build_bottle(glass, juice, metal, cap_mat, label_mat)

    focus = (0.0, 0.0, 0.10)

    # two large softboxes, feathered left/right of the lens axis
    key = softbox("Softbox_Key", (-0.85, -0.70, 0.85), focus, 0.90, 1.40, 240.0,
                  shell_mat)
    fill = softbox("Softbox_Fill", (0.95, -0.55, 0.55), focus, 0.80, 1.20, 90.0,
                   shell_mat, color=(0.95, 0.97, 1.0))

    # hard rim from behind to draw the glass edges
    rim_data = bpy.data.lights.new("Rim_Light", type='AREA')
    rim_data.shape = 'RECTANGLE'
    rim_data.size = 0.05
    rim_data.size_y = 0.55
    rim_data.energy = 180.0
    rim_data.color = (0.85, 0.90, 1.0)
    rim = bpy.data.objects.new("Rim_Light", rim_data)
    scene.collection.objects.link(rim)
    rim.location = (0.55, 0.75, 0.55)
    aim(rim, focus)

    # small bounce card catching the amber juice from below-front
    bounce = box("Bounce_Card", (0.45, 0.005, 0.30), location=(0.0, -0.62, 0.05))
    bounce.rotation_euler = (math.radians(-18.0), 0.0, 0.0)
    assign(bounce, emission("Bounce_Emit", (1.0, 0.98, 0.94, 1.0), 1.6))

    # ---- portrait camera -------------------------------------------------- #
    target = bpy.data.objects.new("Focus_Target", None)
    target.empty_display_type = 'SPHERE'
    target.empty_display_size = 0.02
    target.location = focus
    scene.collection.objects.link(target)

    cam_data = bpy.data.cameras.new("PortraitCam")
    cam_data.lens = 100.0
    cam_data.clip_start = 0.02
    cam_data.sensor_fit = 'VERTICAL'
    cam_data.dof.use_dof = True
    cam_data.dof.focus_object = target
    cam_data.dof.aperture_fstop = 4.0
    cam_data.dof.aperture_blades = 8
    cam = bpy.data.objects.new("PortraitCam", cam_data)
    scene.collection.objects.link(cam)
    cam.location = (0.16, -1.05, 0.20)
    track = cam.constraints.new('TRACK_TO')
    track.target = target
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'
    scene.camera = cam


if __name__ == "__main__":
    main()
