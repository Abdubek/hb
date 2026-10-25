"""claude-101 - Studio product shot: brushed steel electric kettle on a seamless backdrop.

Builds a cyclorama, a lathed kettle (body, lid, knob, spout, handle, power base),
a key/fill/rim studio rig with a black flag and an 85mm product camera with mild DOF.
Scene construction only: nothing is rendered or written to disk.
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


def lathe(name, profile, segments=96, smooth=True):
    """Revolve a list of (radius, z) points around the Z axis."""
    bm = bmesh.new()
    verts = [bm.verts.new((p[0], 0.0, p[1])) for p in profile]
    edges = [bm.edges.new((verts[i], verts[i + 1])) for i in range(len(verts) - 1)]
    bmesh.ops.spin(bm, geom=verts + edges, cent=(0, 0, 0), axis=(0, 0, 1),
                   dvec=(0, 0, 0), angle=2.0 * math.pi, steps=segments,
                   use_merge=False)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return to_object(name, bm, smooth)


def tube(name, points, radii, segments=24, caps=True):
    """Sweep a circle of varying radius along a poly-line."""
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


def assign(ob, mat):
    ob.data.materials.clear()
    ob.data.materials.append(mat)


def area_light(name, location, target, size, energy, shape='RECTANGLE', size_y=None):
    data = bpy.data.lights.new(name, type='AREA')
    data.shape = shape
    data.size = size
    if size_y is not None:
        data.size_y = size_y
    data.energy = energy
    ob = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = location
    direction = Vector(target) - Vector(location)
    ob.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    return ob


# --------------------------------------------------------------------------- #
# materials
# --------------------------------------------------------------------------- #
def brushed_steel():
    """Anisotropic steel with vertically stretched roughness streaks."""
    mat = bpy.data.materials.new("Brushed Steel")
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.62, 0.64, 0.66, 1.0)
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.22
    if "Anisotropic" in bsdf.inputs:
        bsdf.inputs["Anisotropic"].default_value = 0.75

    coord = nt.nodes.new("ShaderNodeTexCoord")
    coord.location = (-1100, -150)
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.location = (-900, -150)
    mapping.inputs["Scale"].default_value = (140.0, 140.0, 2.0)
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.location = (-700, -150)
    noise.inputs["Scale"].default_value = 6.0
    noise.inputs["Detail"].default_value = 4.0
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.location = (-500, -150)
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (0.13, 0.13, 0.13, 1.0)
    ramp.color_ramp.elements[1].position = 0.65
    ramp.color_ramp.elements[1].color = (0.30, 0.30, 0.30, 1.0)
    tangent = nt.nodes.new("ShaderNodeTangent")
    tangent.location = (-500, -420)
    tangent.direction_type = 'RADIAL'
    tangent.axis = 'Z'

    nt.links.new(coord.outputs["Object"], mapping.inputs["Vector"])
    nt.links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
    nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Roughness"])
    if "Tangent" in bsdf.inputs:
        nt.links.new(tangent.outputs["Tangent"], bsdf.inputs["Tangent"])
    return mat


# --------------------------------------------------------------------------- #
# set pieces
# --------------------------------------------------------------------------- #
def build_cyclorama(width=7.0, front=-4.0, corner=1.6, radius=2.0, top=5.0,
                    arc_steps=18, width_steps=8):
    prof = [(front, 0.0), (corner, 0.0)]
    for i in range(1, arc_steps + 1):
        t = (math.pi / 2.0) * i / arc_steps
        prof.append((corner + radius * math.sin(t), radius - radius * math.cos(t)))
    prof.append((corner + radius, top))

    bm = bmesh.new()
    grid = []
    for j in range(width_steps + 1):
        x = -width * 0.5 + width * j / width_steps
        grid.append([bm.verts.new((x, y, z)) for (y, z) in prof])
    for j in range(width_steps):
        for i in range(len(prof) - 1):
            bm.faces.new((grid[j][i], grid[j][i + 1],
                          grid[j + 1][i + 1], grid[j + 1][i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return to_object("Backdrop_Cyclorama", bm, smooth=True)


def build_kettle(steel, plastic, glass):
    parts = []

    body_profile = [
        (0.000, 0.0225), (0.062, 0.0225), (0.074, 0.0270), (0.079, 0.0350),
        (0.081, 0.0600), (0.081, 0.1250), (0.078, 0.1750), (0.071, 0.2100),
        (0.066, 0.2280), (0.068, 0.2340), (0.064, 0.2370), (0.062, 0.2320),
        (0.062, 0.1000), (0.000, 0.0950),
    ]
    body = lathe("Kettle_Body", body_profile, segments=96)
    assign(body, steel)
    parts.append(body)

    lid_profile = [
        (0.000, 0.2560), (0.020, 0.2545), (0.038, 0.2490), (0.053, 0.2410),
        (0.062, 0.2340), (0.064, 0.2300), (0.059, 0.2270), (0.059, 0.2200),
        (0.052, 0.2190), (0.000, 0.2220),
    ]
    lid = lathe("Kettle_Lid", lid_profile, segments=96)
    assign(lid, steel)
    parts.append(lid)

    knob_profile = [
        (0.000, 0.2560), (0.014, 0.2565), (0.019, 0.2620), (0.019, 0.2700),
        (0.014, 0.2760), (0.000, 0.2775),
    ]
    knob = lathe("Kettle_Knob", knob_profile, segments=48)
    assign(knob, plastic)
    parts.append(knob)

    spout_path = [(0.070, 0.0, 0.150), (0.104, 0.0, 0.176), (0.134, 0.0, 0.206),
                  (0.152, 0.0, 0.229), (0.160, 0.0, 0.241)]
    spout_radii = [0.026, 0.021, 0.016, 0.012, 0.010]
    spout = tube("Kettle_Spout", spout_path, spout_radii, segments=28)
    assign(spout, steel)
    parts.append(spout)

    handle_path = [(-0.072, 0.0, 0.205), (-0.120, 0.0, 0.222), (-0.152, 0.0, 0.200),
                   (-0.160, 0.0, 0.150), (-0.150, 0.0, 0.100), (-0.115, 0.0, 0.062),
                   (-0.076, 0.0, 0.055)]
    handle_radii = [0.013, 0.014, 0.014, 0.013, 0.013, 0.012, 0.011]
    handle = tube("Kettle_Handle", handle_path, handle_radii, segments=24)
    assign(handle, plastic)
    parts.append(handle)

    window = lathe("Kettle_WaterWindow",
                   [(0.0805, 0.070), (0.0812, 0.075), (0.0812, 0.185), (0.0805, 0.190)],
                   segments=96)
    window.scale = (1.0, 0.28, 1.0)
    window.location = (0.0, -0.058, 0.0)
    assign(window, glass)
    parts.append(window)

    base_profile = [
        (0.000, 0.000), (0.088, 0.000), (0.094, 0.004), (0.096, 0.012),
        (0.092, 0.020), (0.070, 0.021), (0.066, 0.0225), (0.000, 0.0225),
    ]
    base = lathe("Kettle_PowerBase", base_profile, segments=96)
    assign(base, plastic)
    parts.append(base)

    root = bpy.data.objects.new("Kettle", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.08
    bpy.context.scene.collection.objects.link(root)
    for part in parts:
        part.parent = root
    root.rotation_euler = (0.0, 0.0, math.radians(24.0))
    return root


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
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 2000
    scene.render.film_transparent = False
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium Contrast'

    # very dim ambient so the lights do all the shaping
    world_nodes = scene.world.node_tree if scene.world.use_nodes else None
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.02, 0.022, 0.025, 1.0)
    bg.inputs["Strength"].default_value = 1.0

    steel = brushed_steel()
    plastic = pbr("Dark Plastic", (0.020, 0.021, 0.023, 1.0), 0.0, 0.35,
                  {"Coat Weight": 0.4, "Coat Roughness": 0.15})
    glass = pbr("Gauge Glass", (0.85, 0.90, 0.92, 1.0), 0.0, 0.05,
                {"Transmission Weight": 1.0, "IOR": 1.45})
    sweep = pbr("Backdrop Paper", (0.80, 0.80, 0.81, 1.0), 0.0, 0.55)
    flag_mat = pbr("Flag Black", (0.008, 0.008, 0.008, 1.0), 0.0, 0.85)

    backdrop = build_cyclorama()
    assign(backdrop, sweep)

    build_kettle(steel, plastic, glass)

    # ---- lighting -------------------------------------------------------- #
    aim_at = (0.0, 0.0, 0.14)
    key = area_light("Key_Softbox", (-1.15, -1.05, 1.35), aim_at,
                     size=1.30, size_y=1.90, energy=420.0)
    fill = area_light("Fill_Softbox", (1.35, -0.85, 0.75), aim_at,
                      size=1.60, size_y=1.60, energy=110.0)
    rim = area_light("Rim_Strip", (0.35, 1.05, 1.55), aim_at,
                     size=0.16, size_y=1.60, energy=260.0)
    rim.data.color = (0.92, 0.95, 1.0)
    kicker = area_light("Edge_Kicker", (0.95, 0.55, 0.28), aim_at,
                        size=0.10, size_y=0.90, energy=90.0)

    # negative fill so the steel keeps a dark contour on camera right
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.6)
    flag = to_object("Negative_Fill_Flag", bm, smooth=False)
    flag.location = (0.85, -0.55, 0.30)
    flag.rotation_euler = (math.radians(90.0), 0.0, math.radians(-62.0))
    flag.scale = (1.0, 1.4, 1.0)
    assign(flag, flag_mat)

    # ---- camera ---------------------------------------------------------- #
    target = bpy.data.objects.new("CAM_Target", None)
    target.empty_display_type = 'SPHERE'
    target.empty_display_size = 0.03
    target.location = (0.0, 0.0, 0.135)
    scene.collection.objects.link(target)

    cam_data = bpy.data.cameras.new("ProductCam")
    cam_data.lens = 85.0
    cam_data.clip_start = 0.05
    cam_data.clip_end = 60.0
    cam_data.dof.use_dof = True
    cam_data.dof.focus_object = target
    cam_data.dof.aperture_fstop = 5.6
    cam = bpy.data.objects.new("ProductCam", cam_data)
    scene.collection.objects.link(cam)
    cam.location = (0.30, -1.75, 0.42)
    track = cam.constraints.new('TRACK_TO')
    track.target = target
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'
    scene.camera = cam


if __name__ == "__main__":
    main()
