"""claude-104 - Sculptural desk lamp with a three camera rig.

Builds a brass/enamel desk lamp (weighted base, swept arm, conical shade, warm
emitter) on a simple studio set, then adds three cameras:
    Cam_Hero       - 50mm three quarter beauty view with DOF
    Cam_Detail     - 85mm close up on the arm/shade joint
    Cam_Elevation  - orthographic front elevation, axis aligned
Each camera is bound to a timeline marker so they can be cut between.
Scene construction only.
"""

import bpy
import bmesh
import math
from mathutils import Vector


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def clean_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    if scene.world is None:
        scene.world = bpy.data.worlds.new("World")
    return scene


def to_object(name, bm, smooth=True):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        for poly in me.polygons:
            poly.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def lathe(name, profile, segments=72, smooth=True):
    bm = bmesh.new()
    verts = [bm.verts.new((p[0], 0.0, p[1])) for p in profile]
    edges = [bm.edges.new((verts[i], verts[i + 1])) for i in range(len(verts) - 1)]
    bmesh.ops.spin(bm, geom=verts + edges, cent=(0, 0, 0), axis=(0, 0, 1),
                   dvec=(0, 0, 0), angle=2.0 * math.pi, steps=segments,
                   use_merge=False)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return to_object(name, bm, smooth)


def tube(name, points, radii, segments=20, caps=True):
    bm = bmesh.new()
    pts = [Vector(p) for p in points]
    rings = []
    for i, p in enumerate(pts):
        if i == 0:
            tan = pts[1] - pts[0]
        elif i == len(pts) - 1:
            tan = pts[-1] - pts[-2]
        else:
            tan = pts[i + 1] - pts[i - 1]
        tan.normalize()
        ref = Vector((0, 0, 1)) if abs(tan.z) < 0.9 else Vector((1, 0, 0))
        ax = tan.cross(ref).normalized()
        ay = tan.cross(ax).normalized()
        ring = []
        for s in range(segments):
            a = 2.0 * math.pi * s / segments
            ring.append(bm.verts.new(p + ax * (math.cos(a) * radii[i])
                                       + ay * (math.sin(a) * radii[i])))
        rings.append(ring)
    for i in range(len(rings) - 1):
        for s in range(segments):
            s2 = (s + 1) % segments
            bm.faces.new((rings[i][s], rings[i][s2],
                          rings[i + 1][s2], rings[i + 1][s]))
    if caps:
        bm.faces.new(rings[0])
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return to_object(name, bm, True)


def bezier_points(p0, p1, p2, p3, count=26):
    """Sample a cubic bezier as a poly-line."""
    p0, p1, p2, p3 = (Vector(p) for p in (p0, p1, p2, p3))
    out = []
    for i in range(count):
        t = i / (count - 1.0)
        u = 1.0 - t
        out.append(u * u * u * p0 + 3 * u * u * t * p1 + 3 * u * t * t * p2
                   + t * t * t * p3)
    return out


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
    nt.links.new(emit.outputs["Emission"], nt.nodes["Material Output"].inputs["Surface"])
    return mat


def assign(ob, mat):
    ob.data.materials.clear()
    ob.data.materials.append(mat)


# --------------------------------------------------------------------------- #
# the lamp
# --------------------------------------------------------------------------- #
def build_lamp(brass, enamel, shade_inner, bulb_mat, felt):
    parts = []

    base_profile = [
        (0.000, 0.000), (0.105, 0.000), (0.112, 0.006), (0.114, 0.018),
        (0.108, 0.030), (0.070, 0.038), (0.040, 0.046), (0.030, 0.056),
        (0.026, 0.070), (0.000, 0.070),
    ]
    base = lathe("Lamp_Base", base_profile, segments=80)
    assign(base, enamel)
    parts.append(base)

    pad = lathe("Lamp_BasePad", [(0.000, -0.002), (0.104, -0.002), (0.104, 0.000),
                                 (0.000, 0.000)], segments=64)
    assign(pad, felt)
    parts.append(pad)

    collar = lathe("Lamp_Collar", [(0.000, 0.068), (0.030, 0.068), (0.032, 0.074),
                                   (0.030, 0.082), (0.022, 0.086), (0.000, 0.086)],
                   segments=64)
    assign(collar, brass)
    parts.append(collar)

    arm_pts = bezier_points((0.0, 0.0, 0.082), (0.0, 0.0, 0.400),
                            (0.0, 0.170, 0.560), (0.0, 0.290, 0.470), count=30)
    arm_radii = [0.0135 - 0.0035 * (i / 29.0) for i in range(30)]
    arm = tube("Lamp_Arm", arm_pts, arm_radii, segments=22)
    assign(arm, brass)
    parts.append(arm)

    joint = lathe("Lamp_Joint", [(0.000, -0.016), (0.020, -0.017), (0.024, -0.008),
                                 (0.024, 0.008), (0.020, 0.017), (0.000, 0.016)],
                  segments=48)
    joint.location = arm_pts[-1]
    joint.rotation_euler = (math.radians(56.0), 0.0, 0.0)
    assign(joint, brass)
    parts.append(joint)

    shade_profile = [
        (0.020, 0.000), (0.022, 0.006), (0.070, 0.108), (0.104, 0.158),
        (0.106, 0.162), (0.101, 0.162), (0.067, 0.112), (0.019, 0.010),
        (0.017, 0.000),
    ]
    shade = lathe("Lamp_Shade", shade_profile, segments=72)
    assign(shade, enamel)
    shade.location = arm_pts[-1]
    shade.rotation_euler = (math.radians(146.0), 0.0, 0.0)
    parts.append(shade)

    inner = lathe("Lamp_ShadeInner",
                  [(0.018, 0.002), (0.066, 0.106), (0.100, 0.156)], segments=72)
    assign(inner, shade_inner)
    inner.location = arm_pts[-1]
    inner.rotation_euler = (math.radians(146.0), 0.0, 0.0)
    parts.append(inner)

    bulb = lathe("Lamp_Bulb",
                 [(0.000, 0.000), (0.020, 0.006), (0.026, 0.024), (0.024, 0.046),
                  (0.012, 0.058), (0.000, 0.060)], segments=48)
    assign(bulb, bulb_mat)
    # local +Z of the shade points down-forward; place the bulb inside the cone
    shade_dir = shade.rotation_euler.to_matrix() @ Vector((0.0, 0.0, 1.0))
    bulb.location = Vector(arm_pts[-1]) + shade_dir * 0.075
    bulb.rotation_euler = shade.rotation_euler.copy()
    parts.append(bulb)

    root = bpy.data.objects.new("Desk_Lamp", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.1
    bpy.context.scene.collection.objects.link(root)
    for part in parts:
        part.parent = root

    return root, Vector(arm_pts[-1]), shade_dir


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
    scene.render.resolution_x = 1800
    scene.render.resolution_y = 1800
    scene.view_settings.view_transform = 'AgX'

    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (
        0.035, 0.036, 0.040, 1.0)

    brass = pbr("Aged Brass", (0.72, 0.53, 0.24, 1.0), 1.0, 0.24)
    enamel = pbr("Deep Green Enamel", (0.020, 0.062, 0.048, 1.0), 0.0, 0.18,
                 {"Coat Weight": 1.0, "Coat Roughness": 0.06})
    shade_inner = pbr("Shade Interior", (0.94, 0.88, 0.74, 1.0), 0.0, 0.55)
    bulb_mat = emission_mat("Bulb", (1.0, 0.80, 0.52, 1.0), 22.0)
    felt = pbr("Base Felt", (0.045, 0.045, 0.048, 1.0), 0.0, 0.90)
    floor_mat = pbr("Studio Floor", (0.19, 0.19, 0.20, 1.0), 0.0, 0.45)
    wall_mat = pbr("Studio Wall", (0.30, 0.30, 0.31, 1.0), 0.0, 0.70)

    lamp, head_pos, shade_dir = build_lamp(brass, enamel, shade_inner, bulb_mat, felt)

    # ---- simple studio set ------------------------------------------------ #
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=6.0)
    floor = to_object("Floor", bm, smooth=False)
    assign(floor, floor_mat)

    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=6.0)
    wall = to_object("Back_Wall", bm, smooth=False)
    wall.rotation_euler = (math.radians(90.0), 0.0, 0.0)
    wall.location = (0.0, 1.5, 0.0)
    assign(wall, wall_mat)

    # ---- lighting ---------------------------------------------------------- #
    def area(name, loc, target, size, size_y, energy, color=(1, 1, 1)):
        data = bpy.data.lights.new(name, type='AREA')
        data.shape = 'RECTANGLE'
        data.size = size
        data.size_y = size_y
        data.energy = energy
        data.color = color
        ob = bpy.data.objects.new(name, data)
        scene.collection.objects.link(ob)
        ob.location = loc
        ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat(
            '-Z', 'Y').to_euler()
        return ob

    aim_point = (0.0, 0.05, 0.35)
    area("Key_Soft", (-1.5, -1.3, 1.9), aim_point, 1.8, 1.8, 500.0)
    area("Fill_Broad", (1.7, -0.9, 0.9), aim_point, 2.0, 1.6, 130.0,
         color=(0.92, 0.95, 1.0))
    area("Rim_Back", (0.7, 1.25, 1.5), aim_point, 0.12, 1.4, 260.0)

    # practical light inside the shade, pointed along the shade axis
    spot_data = bpy.data.lights.new("Lamp_Practical", type='SPOT')
    spot_data.energy = 90.0
    spot_data.color = (1.0, 0.78, 0.50)
    spot_data.spot_size = math.radians(88.0)
    spot_data.spot_blend = 0.45
    spot_data.shadow_soft_size = 0.05
    spot = bpy.data.objects.new("Lamp_Practical", spot_data)
    scene.collection.objects.link(spot)
    spot.location = head_pos + shade_dir * 0.09
    spot.rotation_euler = shade_dir.to_track_quat('-Z', 'Y').to_euler()
    spot.parent = lamp

    # ---- three cameras ----------------------------------------------------- #
    target = bpy.data.objects.new("Lamp_Target", None)
    target.empty_display_type = 'SPHERE'
    target.empty_display_size = 0.05
    target.location = (0.0, 0.06, 0.34)
    scene.collection.objects.link(target)

    detail_target = bpy.data.objects.new("Joint_Target", None)
    detail_target.empty_display_type = 'SPHERE'
    detail_target.empty_display_size = 0.02
    detail_target.location = head_pos
    scene.collection.objects.link(detail_target)

    def make_camera(name, location, lens, focus=None, fstop=4.0, ortho=None,
                    rotation=None, track_target=None):
        data = bpy.data.cameras.new(name)
        if ortho is not None:
            data.type = 'ORTHO'
            data.ortho_scale = ortho
        else:
            data.lens = lens
        data.clip_start = 0.02
        data.clip_end = 100.0
        if focus is not None:
            data.dof.use_dof = True
            data.dof.focus_object = focus
            data.dof.aperture_fstop = fstop
        ob = bpy.data.objects.new(name, data)
        scene.collection.objects.link(ob)
        ob.location = location
        if rotation is not None:
            ob.rotation_euler = rotation
        if track_target is not None:
            track = ob.constraints.new('TRACK_TO')
            track.target = track_target
            track.track_axis = 'TRACK_NEGATIVE_Z'
            track.up_axis = 'UP_Y'
        return ob

    cam_hero = make_camera("Cam_Hero", (1.05, -1.55, 0.78), 50.0, focus=target,
                           fstop=3.5, track_target=target)
    cam_detail = make_camera("Cam_Detail", (0.42, -0.62, 0.66), 85.0,
                             focus=detail_target, fstop=2.8,
                             track_target=detail_target)
    # true orthographic elevation: dead on from -Y, no tracking constraint
    cam_elev = make_camera("Cam_Elevation", (0.0, -3.0, 0.34), 50.0, ortho=0.95,
                           rotation=(math.radians(90.0), 0.0, 0.0))

    scene.camera = cam_hero
    scene.frame_start = 1
    scene.frame_end = 3
    for index, cam in enumerate((cam_hero, cam_detail, cam_elev), start=1):
        marker = scene.timeline_markers.new(cam.name, frame=index)
        marker.camera = cam


if __name__ == "__main__":
    main()
