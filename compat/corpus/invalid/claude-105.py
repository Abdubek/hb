"""claude-105 - Wide angle view down a furnished hotel corridor.

Builds a corridor shell (carpet, runner, wainscoted walls, coved ceiling), a repeated
door assembly (frame, panelled leaf, lever handle, room number plate) instanced along
both walls with shared mesh data, wall sconces, recessed ceiling downlights, a console
table with a lamp and artwork at the far end, and an 18mm camera on the centre line.
Scene construction only.
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


def to_object(name, bm, materials=(), smooth=False):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for mat in materials:
        me.materials.append(mat)
    if smooth:
        for poly in me.polygons:
            poly.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def bm_box(bm, center, size, mat_index=0, bevel=0.0):
    """Add a box to an existing bmesh, tagged with a material index."""
    res = bmesh.ops.create_cube(bm, size=1.0)
    verts = res["verts"]
    bmesh.ops.scale(bm, vec=Vector(size), verts=verts)
    bmesh.ops.translate(bm, vec=Vector(center), verts=verts)
    faces = set()
    for v in verts:
        faces.update(v.link_faces)
    if bevel > 0.0:
        geom = list(faces) + [e for f in faces for e in f.edges] + list(verts)
        result = bmesh.ops.bevel(bm, geom=geom, offset=bevel, segments=2,
                                 profile=0.5, affect='EDGES', clamp_overlap=True)
        faces.update(result.get("faces", []))
    for f in faces:
        f.material_index = mat_index
    return verts


def bm_cylinder(bm, center, radius, depth, mat_index=0, segments=20, axis='Z'):
    res = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False,
                                segments=segments, radius1=radius, radius2=radius,
                                depth=depth)
    verts = res["verts"]
    if axis == 'X':
        bmesh.ops.rotate(bm, verts=verts,
                         matrix=Matrix.Rotation(math.radians(90.0), 3, 'Y'))
    elif axis == 'Y':
        bmesh.ops.rotate(bm, verts=verts,
                         matrix=Matrix.Rotation(math.radians(90.0), 3, 'X'))
    bmesh.ops.translate(bm, vec=Vector(center), verts=verts)
    faces = set()
    for v in verts:
        faces.update(v.link_faces)
    for f in faces:
        f.material_index = mat_index
        f.smooth = True
    return verts


def pbr(name, base, metallic=0.0, roughness=0.5, extra=None):
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


def carpet_material():
    """Dark patterned carpet built from two noise-driven colours."""
    mat = bpy.data.materials.new("Carpet")
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.92
    if "Sheen Weight" in bsdf.inputs:
        bsdf.inputs["Sheen Weight"].default_value = 0.3

    coord = nt.nodes.new("ShaderNodeTexCoord")
    coord.location = (-1000, 0)
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.location = (-820, 0)
    mapping.inputs["Scale"].default_value = (3.0, 3.0, 3.0)
    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.location = (-640, 120)
    wave.wave_type = 'RINGS'
    wave.inputs["Scale"].default_value = 2.5
    wave.inputs["Distortion"].default_value = 12.0
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.location = (-640, -160)
    noise.inputs["Scale"].default_value = 90.0
    mix = nt.nodes.new("ShaderNodeMixRGB")
    mix.location = (-420, 0)
    mix.blend_type = 'MIX'
    mix.inputs["Color1"].default_value = (0.055, 0.030, 0.038, 1.0)
    mix.inputs["Color2"].default_value = (0.135, 0.075, 0.060, 1.0)
    bump = nt.nodes.new("ShaderNodeBump")
    bump.location = (-420, -260)
    bump.inputs["Strength"].default_value = 0.35

    nt.links.new(coord.outputs["Object"], mapping.inputs["Vector"])
    nt.links.new(mapping.outputs["Vector"], wave.inputs["Vector"])
    nt.links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
    nt.links.new(wave.outputs["Fac"], mix.inputs["Fac"])
    nt.links.new(mix.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def emission_mat(name, color, strength):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    for node in list(nt.nodes):
        if node.type != 'OUTPUT_MATERIAL':
            nt.nodes.remove(node)
    emit = nt.nodes.new("ShaderNodeEmission")
    emit.location = (-250, 0)
    emit.inputs["Color"].default_value = color
    emit.inputs["Strength"].default_value = strength
    nt.links.new(emit.outputs["Emission"],
                 nt.nodes["Material Output"].inputs["Surface"])
    return mat


# --------------------------------------------------------------------------- #
# corridor dimensions
# --------------------------------------------------------------------------- #
WIDTH = 2.40          # wall to wall
HEIGHT = 2.75         # floor to ceiling
LENGTH = 19.0         # camera end to far end wall
PITCH = 3.20          # door spacing
DOOR_COUNT = 5
HALF = WIDTH * 0.5


def build_shell(mats):
    carpet, runner_mat, wall_mat, wainscot_mat, base_mat, ceiling_mat = mats
    bm = bmesh.new()
    y_mid = LENGTH * 0.5 - 1.0

    bm_box(bm, (0.0, y_mid, -0.05), (WIDTH, LENGTH, 0.10), 0)              # floor
    bm_box(bm, (0.0, y_mid, 0.004), (1.30, LENGTH - 0.4, 0.012), 1)       # runner
    bm_box(bm, (0.0, y_mid, HEIGHT + 0.08), (WIDTH, LENGTH, 0.16), 5)     # ceiling

    for sx in (-1.0, 1.0):
        x = sx * (HALF + 0.06)
        bm_box(bm, (x, y_mid, HEIGHT * 0.5), (0.12, LENGTH, HEIGHT), 2)   # wall
        bm_box(bm, (sx * (HALF - 0.015), y_mid, 0.52), (0.03, LENGTH, 1.04), 3)
        bm_box(bm, (sx * (HALF - 0.03), y_mid, 0.075), (0.06, LENGTH, 0.15), 4)
        bm_box(bm, (sx * (HALF - 0.025), y_mid, 1.055), (0.05, LENGTH, 0.05), 4)
        # ceiling cove
        bm_box(bm, (sx * (HALF - 0.09), y_mid, HEIGHT - 0.06),
               (0.18, LENGTH, 0.12), 4)

    # far end wall
    bm_box(bm, (0.0, LENGTH - 1.0, HEIGHT * 0.5), (WIDTH, 0.12, HEIGHT), 2)
    bm_box(bm, (0.0, LENGTH - 1.08, 0.52), (WIDTH, 0.04, 1.04), 3)
    bm_box(bm, (0.0, LENGTH - 1.09, 0.075), (WIDTH, 0.06, 0.15), 4)
    # wall behind the camera closes the box off
    bm_box(bm, (0.0, -1.06, HEIGHT * 0.5), (WIDTH, 0.12, HEIGHT), 2)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return to_object("Corridor_Shell", bm,
                     (carpet, runner_mat, wall_mat, wainscot_mat, base_mat,
                      ceiling_mat))


def build_door_mesh(mats):
    """One door assembly as a single multi-material mesh, reused for every doorway.

    Local space: door leaf lies in the XZ plane, opening faces -Y (into the corridor).
    """
    trim, leaf_mat, metal = 0, 1, 2
    bm = bmesh.new()

    # reveal / casing
    bm_box(bm, (0.0, 0.10, 1.045), (1.02, 0.22, 2.09), trim)
    bm_box(bm, (-0.475, -0.015, 1.045), (0.07, 0.05, 2.09), trim)
    bm_box(bm, (0.475, -0.015, 1.045), (0.07, 0.05, 2.09), trim)
    bm_box(bm, (0.0, -0.015, 2.075), (1.02, 0.05, 0.07), trim)

    # leaf
    bm_box(bm, (0.0, 0.045, 1.02), (0.86, 0.045, 2.04), leaf_mat)
    # recessed panels
    for cz, ch in ((0.55, 0.78), (1.52, 0.78)):
        bm_box(bm, (0.0, 0.018, cz), (0.62, 0.012, ch), leaf_mat, bevel=0.006)
    # kick plate
    bm_box(bm, (0.0, 0.018, 0.10), (0.80, 0.010, 0.14), metal)

    # lever handle and escutcheon
    bm_cylinder(bm, (0.33, 0.014, 1.05), 0.038, 0.014, metal, segments=20, axis='Y')
    bm_cylinder(bm, (0.33, -0.02, 1.05), 0.012, 0.06, metal, segments=16, axis='Y')
    bm_box(bm, (0.285, -0.048, 1.05), (0.11, 0.022, 0.022), metal, bevel=0.006)
    bm_cylinder(bm, (0.33, 0.014, 0.93), 0.016, 0.016, metal, segments=16, axis='Y')

    # room number plate
    bm_box(bm, (0.0, 0.016, 1.72), (0.15, 0.008, 0.09), metal, bevel=0.004)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("Door_Assembly")
    bm.to_mesh(me)
    bm.free()
    for mat in mats:
        me.materials.append(mat)
    return me


def build_sconce_mesh(shade_mat, metal_mat):
    bm = bmesh.new()
    bm_box(bm, (0.0, 0.03, 0.0), (0.10, 0.06, 0.22), 1, bevel=0.008)
    bm_box(bm, (0.0, -0.06, 0.0), (0.16, 0.14, 0.30), 0, bevel=0.010)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("Sconce")
    bm.to_mesh(me)
    bm.free()
    me.materials.append(shade_mat)
    me.materials.append(metal_mat)
    return me


def build_downlight_mesh(trim_mat, emit_mat):
    bm = bmesh.new()
    bm_cylinder(bm, (0.0, 0.0, 0.0), 0.085, 0.04, 0, segments=24)
    bm_cylinder(bm, (0.0, 0.0, -0.021), 0.070, 0.004, 1, segments=24)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("Downlight")
    bm.to_mesh(me)
    bm.free()
    me.materials.append(trim_mat)
    me.materials.append(emit_mat)
    return me


def build_end_furniture(wood, metal, shade_mat, emit_mat, art_frame, art_canvas):
    scene = bpy.context.scene
    y_wall = LENGTH - 1.06

    bm = bmesh.new()
    bm_box(bm, (0.0, y_wall - 0.22, 0.76), (1.10, 0.40, 0.05), 0, bevel=0.008)
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            bm_cylinder(bm, (sx * 0.48, y_wall - 0.22 + sy * 0.15, 0.37),
                        0.018, 0.74, 1, segments=12)
    bm_box(bm, (0.0, y_wall - 0.22, 0.50), (1.02, 0.30, 0.04), 0, bevel=0.006)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    console = to_object("Console_Table", bm, (wood, metal), smooth=False)

    bm = bmesh.new()
    bm_cylinder(bm, (0.0, 0.0, 0.02), 0.10, 0.04, 1, segments=24)
    bm_cylinder(bm, (0.0, 0.0, 0.20), 0.016, 0.36, 1, segments=16)
    res = bmesh.ops.create_cone(bm, cap_ends=False, cap_tris=False, segments=32,
                                radius1=0.16, radius2=0.11, depth=0.22)
    bmesh.ops.translate(bm, vec=Vector((0.0, 0.0, 0.48)), verts=res["verts"])
    for v in res["verts"]:
        for f in v.link_faces:
            f.material_index = 0
            f.smooth = True
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    lamp = to_object("Console_Lamp", bm, (shade_mat, metal))
    lamp.location = (-0.32, y_wall - 0.22, 0.785)

    bulb_data = bpy.data.lights.new("Console_Lamp_Bulb", type='POINT')
    bulb_data.energy = 18.0
    bulb_data.color = (1.0, 0.80, 0.55)
    bulb_data.shadow_soft_size = 0.05
    bulb = bpy.data.objects.new("Console_Lamp_Bulb", bulb_data)
    scene.collection.objects.link(bulb)
    bulb.location = (-0.32, y_wall - 0.22, 1.24)

    bm = bmesh.new()
    bm_box(bm, (0.0, 0.0, 0.0), (0.92, 0.06, 1.16), 0, bevel=0.012)
    bm_box(bm, (0.0, -0.035, 0.0), (0.80, 0.01, 1.04), 1)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    art = to_object("End_Artwork", bm, (art_frame, art_canvas))
    art.location = (0.0, y_wall - 0.06, 1.62)
    return console, lamp, art


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def main():
    scene = clean_scene()
    scene.render.engine = 'CYCLES'
    try:
        scene.cycles.samples = 256
        scene.cycles.use_denoising = True
    except AttributeError:
        pass
    scene.render.resolution_x = 2200
    scene.render.resolution_y = 1400
    scene.view_settings.view_transform = 'AgX'

    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (
        0.010, 0.010, 0.012, 1.0)

    carpet = carpet_material()
    runner_mat = pbr("Runner", (0.115, 0.055, 0.045, 1.0), 0.0, 0.88,
                     {"Sheen Weight": 0.25})
    wall_mat = pbr("Wall Paint", (0.58, 0.545, 0.48, 1.0), 0.0, 0.72)
    wainscot_mat = pbr("Wainscot", (0.34, 0.30, 0.26, 1.0), 0.0, 0.42)
    base_mat = pbr("Trim Paint", (0.72, 0.70, 0.65, 1.0), 0.0, 0.38)
    ceiling_mat = pbr("Ceiling", (0.74, 0.73, 0.70, 1.0), 0.0, 0.85)
    door_wood = pbr("Door Wood", (0.105, 0.052, 0.028, 1.0), 0.0, 0.32,
                    {"Coat Weight": 0.5, "Coat Roughness": 0.15})
    brass = pbr("Brass Hardware", (0.78, 0.60, 0.28, 1.0), 1.0, 0.20)
    shade_mat = pbr("Lamp Shade", (0.86, 0.80, 0.68, 1.0), 0.0, 0.70)
    wood = pbr("Console Wood", (0.16, 0.085, 0.045, 1.0), 0.0, 0.30)
    art_frame = pbr("Art Frame", (0.24, 0.17, 0.09, 1.0), 0.2, 0.35)
    art_canvas = pbr("Art Canvas", (0.30, 0.26, 0.34, 1.0), 0.0, 0.65)
    sconce_glow = emission_mat("Sconce Glow", (1.0, 0.76, 0.48, 1.0), 6.0)
    downlight_glow = emission_mat("Downlight Glow", (1.0, 0.86, 0.68, 1.0), 12.0)

    build_shell((carpet, runner_mat, wall_mat, wainscot_mat, base_mat, ceiling_mat))

    door_me = build_door_mesh((base_mat, door_wood, brass))
    sconce_me = build_sconce_mesh(sconce_glow, brass)
    downlight_me = build_downlight_mesh(base_mat, downlight_glow)

    # ---- repeated doors, sconces and ceiling lights ------------------------ #
    for i in range(DOOR_COUNT):
        for sx in (-1.0, 1.0):
            y = 1.60 + i * PITCH + (0.0 if sx < 0 else PITCH * 0.5)
            if y > LENGTH - 2.2:
                continue
            name = "Door_%s_%02d" % ("L" if sx < 0 else "R", i)
            door = bpy.data.objects.new(name, door_me)
            scene.collection.objects.link(door)
            door.location = (sx * (HALF - 0.005), y, 0.0)
            # rotate rather than mirror so normals stay correct
            door.rotation_euler = (0.0, 0.0,
                                   math.radians(90.0) if sx < 0
                                   else math.radians(-90.0))

            sconce = bpy.data.objects.new(name + "_Sconce", sconce_me)
            scene.collection.objects.link(sconce)
            sconce.location = (sx * (HALF - 0.02), y + PITCH * 0.25, 1.85)
            sconce.rotation_euler = door.rotation_euler.copy()

            light_data = bpy.data.lights.new(name + "_SconceLight", type='POINT')
            light_data.energy = 12.0
            light_data.color = (1.0, 0.74, 0.46)
            light_data.shadow_soft_size = 0.06
            light = bpy.data.objects.new(name + "_SconceLight", light_data)
            scene.collection.objects.link(light)
            light.location = (sx * (HALF - 0.12), y + PITCH * 0.25, 1.87)

    n_ceiling = int((LENGTH - 1.5) / 2.6) + 1
    for i in range(n_ceiling):
        y = 0.9 + i * 2.6
        if y > LENGTH - 1.4:
            break
        can = bpy.data.objects.new("Downlight_%02d" % i, downlight_me)
        scene.collection.objects.link(can)
        can.location = (0.0, y, HEIGHT - 0.02)

        data = bpy.data.lights.new("Downlight_%02d_Light" % i, type='SPOT')
        data.energy = 55.0
        data.color = (1.0, 0.87, 0.72)
        data.spot_size = math.radians(110.0)
        data.spot_blend = 0.5
        data.shadow_soft_size = 0.07
        ob = bpy.data.objects.new("Downlight_%02d_Light" % i, data)
        scene.collection.objects.link(ob)
        ob.location = (0.0, y, HEIGHT - 0.06)
        ob.rotation_euler = (math.radians(180.0), 0.0, 0.0)

    build_end_furniture(wood, brass, shade_mat, downlight_glow, art_frame,
                        art_canvas)

    # soft ambient bounce so the far end does not go black
    amb_data = bpy.data.lights.new("Ambient_Bounce", type='AREA')
    amb_data.shape = 'RECTANGLE'
    amb_data.size = WIDTH * 0.8
    amb_data.size_y = LENGTH * 0.7
    amb_data.energy = 90.0
    amb_data.color = (1.0, 0.90, 0.78)
    amb = bpy.data.objects.new("Ambient_Bounce", amb_data)
    scene.collection.objects.link(amb)
    amb.location = (0.0, LENGTH * 0.5 - 1.0, HEIGHT - 0.25)
    amb.rotation_euler = (math.radians(180.0), 0.0, 0.0)

    # ---- wide angle camera on the centre line ------------------------------ #
    focus = bpy.data.objects.new("Corridor_Focus", None)
    focus.empty_display_type = 'PLAIN_AXES'
    focus.empty_display_size = 0.2
    focus.location = (0.0, 8.0, 1.55)
    scene.collection.objects.link(focus)

    cam_data = bpy.data.cameras.new("CorridorCam")
    cam_data.lens = 18.0
    cam_data.clip_start = 0.05
    cam_data.clip_end = 200.0
    cam_data.dof.use_dof = True
    cam_data.dof.focus_object = focus
    cam_data.dof.aperture_fstop = 5.6
    cam_data.shift_y = 0.02
    cam = bpy.data.objects.new("CorridorCam", cam_data)
    scene.collection.objects.link(cam)
    cam.location = (0.0, -0.75, 1.62)
    cam.rotation_euler = (math.radians(89.0), 0.0, 0.0)
    scene.camera = cam


if __name__ == "__main__":
    main()
