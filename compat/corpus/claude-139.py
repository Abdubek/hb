# claude-139 : "A dining room with an oval table, upholstered chairs and sculptural chandelier"
# Blender 4.5 LTS  --  scene construction only (no render, no file output)

import bpy
import bmesh
import math
from mathutils import Vector

TAU = math.pi * 2.0
D2R = math.radians


# ----------------------------------------------------------------------------
# scene bootstrap
# ----------------------------------------------------------------------------
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    try:
        scene.cycles.samples = 256
        scene.cycles.preview_samples = 32
        scene.cycles.max_bounces = 16
        scene.cycles.transmission_bounces = 12
        scene.cycles.use_denoising = True
    except AttributeError:
        pass
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1280
    scene.render.film_transparent = False
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.length_unit = 'METERS'
    return scene


def collection(name):
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(coll)
    return coll


def link(obj, coll_name):
    collection(coll_name).objects.link(obj)
    return obj


# ----------------------------------------------------------------------------
# material helpers
# ----------------------------------------------------------------------------
def base_material(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    out.location = (400, 0)
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (80, 0)
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat, nt, bsdf


def set_in(node, key, value):
    if key in node.inputs:
        node.inputs[key].default_value = value


def simple_mat(name, color, roughness=0.5, metallic=0.0, ior=1.5,
               sheen=0.0, coat=0.0, transmission=0.0,
               emission=None, emission_strength=0.0):
    mat, nt, bsdf = base_material(name)
    set_in(bsdf, 'Base Color', (*color, 1.0))
    set_in(bsdf, 'Roughness', roughness)
    set_in(bsdf, 'Metallic', metallic)
    set_in(bsdf, 'IOR', ior)
    set_in(bsdf, 'Sheen Weight', sheen)
    set_in(bsdf, 'Coat Weight', coat)
    set_in(bsdf, 'Transmission Weight', transmission)
    if emission is not None:
        set_in(bsdf, 'Emission Color', (*emission, 1.0))
        set_in(bsdf, 'Emission Strength', emission_strength)
    if transmission > 0.5:
        mat.use_backface_culling = False
        try:
            mat.blend_method = 'BLEND'
        except AttributeError:
            pass
    return mat


def wood_mat(name, c_light, c_dark, grain_scale=(3.0, 40.0, 3.0),
             roughness=0.28, bump=0.14, coat=0.25):
    """Procedural wood: distorted wave bands driving colour + bump."""
    mat, nt, bsdf = base_material(name)
    coords = nt.nodes.new('ShaderNodeTexCoord')
    coords.location = (-1000, 0)
    mapping = nt.nodes.new('ShaderNodeMapping')
    mapping.location = (-820, 0)
    mapping.inputs['Scale'].default_value = grain_scale

    wave = nt.nodes.new('ShaderNodeTexWave')
    wave.location = (-620, 120)
    wave.wave_type = 'BANDS'
    wave.bands_direction = 'X'
    wave.wave_profile = 'SIN'
    set_in(wave, 'Scale', 1.6)
    set_in(wave, 'Distortion', 6.0)
    set_in(wave, 'Detail', 4.0)
    set_in(wave, 'Detail Scale', 1.4)

    fibre = nt.nodes.new('ShaderNodeTexNoise')
    fibre.location = (-620, -180)
    set_in(fibre, 'Scale', 60.0)
    set_in(fibre, 'Detail', 8.0)
    set_in(fibre, 'Roughness', 0.7)

    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.location = (-400, 120)
    ramp.color_ramp.interpolation = 'EASE'
    ramp.color_ramp.elements[0].position = 0.25
    ramp.color_ramp.elements[0].color = (*c_dark, 1.0)
    ramp.color_ramp.elements[1].position = 0.8
    ramp.color_ramp.elements[1].color = (*c_light, 1.0)

    mix = nt.nodes.new('ShaderNodeMixRGB')
    mix.location = (-160, 120)
    mix.blend_type = 'MULTIPLY'
    mix.inputs['Fac'].default_value = 0.25

    rough_mix = nt.nodes.new('ShaderNodeMapRange')
    rough_mix.location = (-160, -80)
    set_in(rough_mix, 'To Min', roughness * 0.75)
    set_in(rough_mix, 'To Max', roughness * 1.3)

    bump_n = nt.nodes.new('ShaderNodeBump')
    bump_n.location = (-160, -320)
    set_in(bump_n, 'Strength', bump)
    set_in(bump_n, 'Distance', 0.004)

    L = nt.links.new
    L(coords.outputs['Object'], mapping.inputs['Vector'])
    L(mapping.outputs['Vector'], wave.inputs['Vector'])
    L(mapping.outputs['Vector'], fibre.inputs['Vector'])
    L(wave.outputs['Fac'], ramp.inputs['Fac'])
    L(ramp.outputs['Color'], mix.inputs['Color1'])
    L(fibre.outputs['Color'], mix.inputs['Color2'])
    L(mix.outputs['Color'], bsdf.inputs['Base Color'])
    L(wave.outputs['Fac'], rough_mix.inputs['Value'])
    L(rough_mix.outputs['Result'], bsdf.inputs['Roughness'])
    L(wave.outputs['Fac'], bump_n.inputs['Height'])
    L(bump_n.outputs['Normal'], bsdf.inputs['Normal'])
    set_in(bsdf, 'Coat Weight', coat)
    set_in(bsdf, 'Coat Roughness', 0.12)
    return mat


def fabric_mat(name, color, roughness=0.85, sheen=0.5, weave=180.0, bump=0.35):
    mat, nt, bsdf = base_material(name)
    coords = nt.nodes.new('ShaderNodeTexCoord')
    coords.location = (-800, -200)
    noise = nt.nodes.new('ShaderNodeTexNoise')
    noise.location = (-600, -200)
    set_in(noise, 'Scale', weave)
    set_in(noise, 'Detail', 6.0)
    set_in(noise, 'Roughness', 0.75)
    bump_n = nt.nodes.new('ShaderNodeBump')
    bump_n.location = (-360, -240)
    set_in(bump_n, 'Strength', bump)
    set_in(bump_n, 'Distance', 0.0015)

    tint = nt.nodes.new('ShaderNodeMixRGB')
    tint.location = (-360, 60)
    tint.blend_type = 'MIX'
    tint.inputs['Fac'].default_value = 0.12
    tint.inputs['Color1'].default_value = (*color, 1.0)
    tint.inputs['Color2'].default_value = (color[0] * 0.65,
                                          color[1] * 0.65,
                                          color[2] * 0.65, 1.0)
    L = nt.links.new
    L(coords.outputs['Object'], noise.inputs['Vector'])
    L(noise.outputs['Fac'], tint.inputs['Fac'])
    L(noise.outputs['Fac'], bump_n.inputs['Height'])
    L(bump_n.outputs['Normal'], bsdf.inputs['Normal'])
    L(tint.outputs['Color'], bsdf.inputs['Base Color'])
    set_in(bsdf, 'Roughness', roughness)
    set_in(bsdf, 'Sheen Weight', sheen)
    set_in(bsdf, 'Sheen Roughness', 0.4)
    return mat


def plaster_mat(name, color, roughness=0.75, bump=0.12):
    mat, nt, bsdf = base_material(name)
    coords = nt.nodes.new('ShaderNodeTexCoord')
    coords.location = (-700, -200)
    noise = nt.nodes.new('ShaderNodeTexNoise')
    noise.location = (-520, -200)
    set_in(noise, 'Scale', 22.0)
    set_in(noise, 'Detail', 8.0)
    set_in(noise, 'Roughness', 0.6)
    bump_n = nt.nodes.new('ShaderNodeBump')
    bump_n.location = (-300, -220)
    set_in(bump_n, 'Strength', bump)
    set_in(bump_n, 'Distance', 0.002)
    L = nt.links.new
    L(coords.outputs['Object'], noise.inputs['Vector'])
    L(noise.outputs['Fac'], bump_n.inputs['Height'])
    L(bump_n.outputs['Normal'], bsdf.inputs['Normal'])
    set_in(bsdf, 'Base Color', (*color, 1.0))
    set_in(bsdf, 'Roughness', roughness)
    return mat


# ----------------------------------------------------------------------------
# geometry helpers
# ----------------------------------------------------------------------------
def finalize(name, bm, mat, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1),
             smooth_angle=None, coll='Room', parent=None):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if smooth_angle is not None:
        for f in bm.faces:
            f.smooth = True
        for e in bm.edges:
            if len(e.link_faces) == 2:
                e.smooth = e.calc_face_angle() <= smooth_angle
            else:
                e.smooth = False
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.validate()
    if mat is not None:
        me.materials.append(mat)
    obj = bpy.data.objects.new(name, me)
    obj.location = loc
    obj.rotation_euler = rot
    obj.scale = scale
    link(obj, coll)
    if parent is not None:
        obj.parent = parent
    return obj


def box(name, size, mat, loc=(0, 0, 0), rot=(0, 0, 0), bevel=0.0,
        segments=2, coll='Room', parent=None, smooth_angle=None):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= size[0]
        v.co.y *= size[1]
        v.co.z *= size[2]
    if bevel > 0.0:
        r = min(bevel, min(size) * 0.48)
        bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges),
                        offset=r, segments=segments, affect='EDGES',
                        profile=0.5, clamp_overlap=True)
    return finalize(name, bm, mat, loc, rot, smooth_angle=smooth_angle,
                    coll=coll, parent=parent)


def revolve(name, profile, mat, loc=(0, 0, 0), rot=(0, 0, 0), steps=56,
            closed=False, coll='Room', parent=None, smooth_angle=D2R(38)):
    """Lathe a 2D (radius, z) profile about the Z axis."""
    bm = bmesh.new()
    verts = [bm.verts.new((float(r), 0.0, float(z))) for r, z in profile]
    edges = []
    for i in range(len(verts) - 1):
        edges.append(bm.edges.new((verts[i], verts[i + 1])))
    if closed:
        edges.append(bm.edges.new((verts[-1], verts[0])))
    bmesh.ops.spin(bm, geom=edges + verts, cent=(0, 0, 0), axis=(0, 0, 1),
                   dvec=(0, 0, 0), angle=TAU, steps=steps, use_duplicate=False)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-5)
    return finalize(name, bm, mat, loc, rot, smooth_angle=smooth_angle,
                    coll=coll, parent=parent)


def sphere(name, radius, mat, loc=(0, 0, 0), subdiv=3, coll='Room',
           parent=None, scale=(1, 1, 1)):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=radius)
    return finalize(name, bm, mat, loc, scale=scale,
                    smooth_angle=D2R(90), coll=coll, parent=parent)


def strut(name, p0, p1, s0, s1, mat, bevel=0.005, coll='Room', parent=None):
    """Tapered square-section member running from p0 to p1."""
    a, b = Vector(p0), Vector(p1)
    d = (b - a)
    length = d.length
    d.normalize()
    ref = Vector((0, 0, 1))
    if abs(d.dot(ref)) > 0.98:
        ref = Vector((1, 0, 0))
    ax = d.cross(ref).normalized()
    ay = d.cross(ax).normalized()
    bm = bmesh.new()
    rings = []
    for p, s in ((a, s0), (b, s1)):
        ring = []
        for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            ring.append(bm.verts.new(p + ax * (sx * s * 0.5) + ay * (sy * s * 0.5)))
        rings.append(ring)
    r0, r1 = rings
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
    bm.faces.new(tuple(reversed(r0)))
    bm.faces.new(tuple(r1))
    if bevel > 0.0:
        bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges),
                        offset=min(bevel, length * 0.2), segments=2,
                        affect='EDGES', profile=0.5, clamp_overlap=True)
    return finalize(name, bm, mat, smooth_angle=D2R(35), coll=coll, parent=parent)


def oval_slab(name, rx, ry, thickness, mat, loc=(0, 0, 0), segments=72,
              rim=0.012, coll='Room', parent=None, smooth_angle=D2R(36)):
    """Elliptical slab: top face at local z = 0, extruded downward."""
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=True, cap_tris=False,
                            radius=1.0, segments=segments)
    for v in bm.verts:
        v.co.x *= rx
        v.co.y *= ry
    res = bmesh.ops.extrude_face_region(bm, geom=list(bm.faces))
    new_verts = [e for e in res['geom'] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=new_verts, vec=(0, 0, -thickness))
    if rim > 0.0:
        rim_edges = [e for e in bm.edges
                     if any(len(f.verts) > 4 for f in e.link_faces)]
        bmesh.ops.bevel(bm, geom=rim_edges, offset=min(rim, thickness * 0.4),
                        segments=3, affect='EDGES', profile=0.6,
                        clamp_overlap=True)
    return finalize(name, bm, mat, loc, smooth_angle=smooth_angle,
                    coll=coll, parent=parent)


def tube_curve(name, pts, depth, mat, loc=(0, 0, 0), rot=(0, 0, 0),
               coll='Room', parent=None, taper_end=False):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.resolution_u = 10
    cu.bevel_depth = depth
    cu.bevel_resolution = 4
    cu.use_fill_caps = True
    sp = cu.splines.new('BEZIER')
    sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = Vector(p)
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
        bp.radius = 1.0
    if taper_end:
        sp.bezier_points[0].radius = 1.25
        sp.bezier_points[-1].radius = 0.6
    cu.materials.append(mat)
    obj = bpy.data.objects.new(name, cu)
    obj.location = loc
    obj.rotation_euler = rot
    link(obj, coll)
    if parent is not None:
        obj.parent = parent
    return obj


def empty(name, loc=(0, 0, 0), rot=(0, 0, 0), coll='Room'):
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = 'PLAIN_AXES'
    obj.empty_display_size = 0.2
    obj.location = loc
    obj.rotation_euler = rot
    link(obj, coll)
    return obj


# ----------------------------------------------------------------------------
# materials
# ----------------------------------------------------------------------------
MAT = {}


def build_materials():
    MAT['floor'] = wood_mat('Wood.Floor', (0.30, 0.17, 0.095),
                            (0.115, 0.058, 0.032),
                            grain_scale=(1.2, 26.0, 1.2),
                            roughness=0.34, bump=0.30, coat=0.12)
    MAT['walnut'] = wood_mat('Wood.Walnut', (0.205, 0.105, 0.058),
                             (0.062, 0.028, 0.016),
                             grain_scale=(2.6, 34.0, 2.6),
                             roughness=0.24, bump=0.10, coat=0.4)
    MAT['oak'] = wood_mat('Wood.Oak', (0.34, 0.22, 0.125),
                          (0.15, 0.085, 0.045),
                          grain_scale=(5.0, 46.0, 5.0),
                          roughness=0.32, bump=0.12, coat=0.2)
    MAT['wall'] = plaster_mat('Paint.Wall', (0.415, 0.455, 0.415), 0.78, 0.14)
    MAT['trim'] = plaster_mat('Paint.Trim', (0.86, 0.855, 0.825), 0.42, 0.06)
    MAT['ceiling'] = plaster_mat('Paint.Ceiling', (0.895, 0.895, 0.885), 0.85, 0.10)
    MAT['fabric'] = fabric_mat('Fabric.Upholstery', (0.72, 0.665, 0.575),
                               roughness=0.86, sheen=0.55, weave=210.0)
    MAT['fabric_dark'] = fabric_mat('Fabric.Seat.Dark', (0.28, 0.325, 0.315),
                                    roughness=0.88, sheen=0.45, weave=190.0)
    MAT['rug'] = fabric_mat('Fabric.Rug', (0.34, 0.30, 0.265),
                            roughness=0.92, sheen=0.25, weave=90.0, bump=0.6)
    MAT['rug_border'] = fabric_mat('Fabric.Rug.Border', (0.51, 0.40, 0.30),
                                   roughness=0.92, sheen=0.25, weave=90.0, bump=0.6)
    MAT['brass'] = simple_mat('Metal.Brass', (0.735, 0.555, 0.275),
                              roughness=0.22, metallic=1.0)
    MAT['brass_dark'] = simple_mat('Metal.Brass.Aged', (0.44, 0.335, 0.185),
                                   roughness=0.42, metallic=1.0)
    MAT['glass'] = simple_mat('Glass.Shade', (0.96, 0.94, 0.90),
                              roughness=0.06, ior=1.46, transmission=1.0)
    MAT['glass_frosted'] = simple_mat('Glass.Frosted', (0.98, 0.96, 0.92),
                                      roughness=0.28, ior=1.45, transmission=1.0)
    MAT['window_glass'] = simple_mat('Glass.Window', (0.94, 0.96, 0.98),
                                     roughness=0.02, ior=1.5, transmission=1.0)
    MAT['bulb'] = simple_mat('Emit.Bulb', (1.0, 0.86, 0.66), roughness=0.4,
                             emission=(1.0, 0.80, 0.55), emission_strength=28.0)
    MAT['candle'] = simple_mat('Wax.Candle', (0.92, 0.89, 0.80), roughness=0.45)
    MAT['flame'] = simple_mat('Emit.Flame', (1.0, 0.72, 0.35), roughness=0.5,
                              emission=(1.0, 0.62, 0.28), emission_strength=45.0)
    MAT['porcelain'] = simple_mat('Porcelain', (0.90, 0.90, 0.88),
                                  roughness=0.10, coat=0.6)
    MAT['fruit_a'] = simple_mat('Fruit.Green', (0.30, 0.42, 0.13), roughness=0.35)
    MAT['fruit_b'] = simple_mat('Fruit.Red', (0.44, 0.10, 0.075), roughness=0.30)
    MAT['canvas'] = simple_mat('Art.Canvas', (0.55, 0.50, 0.44), roughness=0.7)
    MAT['stone'] = simple_mat('Stone.Top', (0.72, 0.70, 0.66),
                              roughness=0.18, coat=0.3)


# ----------------------------------------------------------------------------
# room shell
# ----------------------------------------------------------------------------
RX, RY, RZ = 3.25, 2.50, 3.00      # interior half-width, half-depth, height
WT = 0.12                          # wall thickness

WINDOWS = [(-1.55, 1.15, 0.85, 2.45), (1.55, 1.15, 0.85, 2.45)]  # cx,w,z0,z1


def build_room():
    coll = 'Room'
    # floor & ceiling
    box('Floor', (RX + WT, RY + WT, 0.06), MAT['floor'],
        loc=(0, 0, -0.06), coll=coll)
    box('Ceiling', (RX + WT, RY + WT, 0.08), MAT['ceiling'],
        loc=(0, 0, RZ + 0.08), coll=coll)

    # walls (interior faces at +-RX / +-RY)
    walls = {
        'Wall.South': ((RX + WT, WT * 0.5, RZ * 0.5), (0, -RY - WT * 0.5, RZ * 0.5)),
        'Wall.West': ((WT * 0.5, RY, RZ * 0.5), (-RX - WT * 0.5, 0, RZ * 0.5)),
        'Wall.East': ((WT * 0.5, RY, RZ * 0.5), (RX + WT * 0.5, 0, RZ * 0.5)),
    }
    for name, (size, loc) in walls.items():
        box(name, size, MAT['wall'], loc=loc, coll=coll)

    # north wall with window openings cut by boolean modifiers
    north = box('Wall.North', (RX + WT, WT * 0.5, RZ * 0.5), MAT['wall'],
                loc=(0, RY + WT * 0.5, RZ * 0.5), coll=coll)
    for i, (cx, w, z0, z1) in enumerate(WINDOWS):
        cutter = box('WindowCut.%d' % i,
                     (w * 0.5, WT * 1.6, (z1 - z0) * 0.5), None,
                     loc=(cx, RY + WT * 0.5, (z0 + z1) * 0.5), coll='Utility')
        cutter.display_type = 'WIRE'
        cutter.hide_viewport = True
        cutter.hide_render = True
        mod = north.modifiers.new('WindowCut.%d' % i, 'BOOLEAN')
        mod.operation = 'DIFFERENCE'
        mod.object = cutter
        mod.solver = 'EXACT'

    build_windows()
    build_mouldings()


def build_windows():
    frame_d = WT + 0.05
    for i, (cx, w, z0, z1) in enumerate(WINDOWS):
        root = empty('Window.%d' % i, loc=(cx, RY + WT * 0.5, 0), coll='Room')
        hw, h = w * 0.5, z1 - z0
        cz = (z0 + z1) * 0.5
        j = 0.055                       # jamb / casing thickness
        # jambs, head, sill
        box('Window.%d.JambL' % i, (j * 0.5, frame_d * 0.5, h * 0.5 + j),
            MAT['trim'], loc=(-hw + j * 0.5, 0, cz), coll='Room', parent=root,
            bevel=0.006)
        box('Window.%d.JambR' % i, (j * 0.5, frame_d * 0.5, h * 0.5 + j),
            MAT['trim'], loc=(hw - j * 0.5, 0, cz), coll='Room', parent=root,
            bevel=0.006)
        box('Window.%d.Head' % i, (hw, frame_d * 0.5, j * 0.5),
            MAT['trim'], loc=(0, 0, z1 - j * 0.5), coll='Room', parent=root,
            bevel=0.006)
        box('Window.%d.Sill' % i, (hw + 0.075, frame_d * 0.62, 0.035),
            MAT['trim'], loc=(0, -0.03, z0 + 0.02), coll='Room', parent=root,
            bevel=0.01)
        # mullions
        box('Window.%d.MullionV' % i, (0.022, 0.03, h * 0.5 - j),
            MAT['trim'], loc=(0, -WT * 0.5, cz), coll='Room', parent=root,
            bevel=0.004)
        for k in range(1, 3):
            zz = z0 + h * k / 3.0
            box('Window.%d.MullionH%d' % (i, k), (hw - j, 0.028, 0.019),
                MAT['trim'], loc=(0, -WT * 0.5, zz), coll='Room', parent=root,
                bevel=0.004)
        # glazing
        box('Window.%d.Glass' % i, (hw - j, 0.006, h * 0.5 - j),
            MAT['window_glass'], loc=(0, 0.01, cz), coll='Room', parent=root)
        # interior curtain panels either side of the opening
        for s in (-1, 1):
            bm = bmesh.new()
            bmesh.ops.create_grid(bm, x_segments=14, y_segments=18, size=1.0)
            for v in bm.verts:
                u = (v.co.x + 1.0) * 0.5
                t = (v.co.y + 1.0) * 0.5
                v.co.x = -0.30 * u
                v.co.z = -h * 0.5 - 0.12 + t * (h + 0.34)
                v.co.y = 0.045 * math.sin(u * math.pi * 5.0) * (0.35 + 0.65 * t)
            bm.normal_update()
            drape = finalize('Window.%d.Curtain.%d' % (i, s), bm,
                             MAT['fabric'],
                             loc=(s * (hw + 0.10), -WT - 0.09, cz),
                             scale=(s, 1, 1),
                             smooth_angle=D2R(60), coll='Room', parent=root)
            drape.modifiers.new('Solidify', 'SOLIDIFY').thickness = 0.008
        # curtain rod
        rod = revolve('Window.%d.Rod' % i,
                      [(0, 0), (0.016, 0), (0.016, w + 0.42), (0, w + 0.42)],
                      MAT['brass_dark'], loc=(-(hw + 0.21), -WT - 0.10, z1 + 0.13),
                      rot=(0, D2R(90), 0), steps=20, coll='Room', parent=root)
        rod.rotation_euler = (0, D2R(90), 0)


def build_mouldings():
    t = 0.022
    # skirting + chair rail on all four walls, crown at the ceiling
    runs = [
        ('S', (RX, t, 1), (0, -RY + t, 0), 0),
        ('N', (RX, t, 1), (0, RY - t, 0), 0),
        ('W', (t, RY, 1), (-RX + t, 0, 0), 0),
        ('E', (t, RY, 1), (RX - t, 0, 0), 0),
    ]
    for tag, size, loc, _ in runs:
        sx, sy, _ = size
        box('Skirting.%s' % tag, (sx, sy, 0.065), MAT['trim'],
            loc=(loc[0], loc[1], 0.065), coll='Room', bevel=0.008)
        box('ChairRail.%s' % tag, (sx, sy * 0.8, 0.026), MAT['trim'],
            loc=(loc[0], loc[1], 0.98), coll='Room', bevel=0.007)
        box('Crown.%s' % tag, (sx, sy * 1.5, 0.055), MAT['trim'],
            loc=(loc[0], loc[1], RZ - 0.055), coll='Room', bevel=0.014)

    # wainscot field with stiles on the south and west walls
    for tag, along, axis in (('S', RX, 'x'), ('W', RY, 'y')):
        if axis == 'x':
            box('Wainscot.%s' % tag, (RX - 0.005, 0.008, 0.44), MAT['trim'],
                loc=(0, -RY + 0.012, 0.51), coll='Room')
            n = 9
            for i in range(n + 1):
                x = -RX + 0.02 + (2 * RX - 0.04) * i / n
                box('Stile.%s.%d' % (tag, i), (0.033, 0.014, 0.44),
                    MAT['trim'], loc=(x, -RY + 0.02, 0.51), coll='Room',
                    bevel=0.005)
        else:
            box('Wainscot.%s' % tag, (0.008, RY - 0.005, 0.44), MAT['trim'],
                loc=(-RX + 0.012, 0, 0.51), coll='Room')
            n = 7
            for i in range(n + 1):
                y = -RY + 0.02 + (2 * RY - 0.04) * i / n
                box('Stile.%s.%d' % (tag, i), (0.014, 0.033, 0.44),
                    MAT['trim'], loc=(-RX + 0.02, y, 0.51), coll='Room',
                    bevel=0.005)

    # ceiling rose for the chandelier
    revolve('CeilingRose',
            [(0, 0), (0.34, 0), (0.36, -0.018), (0.30, -0.038),
             (0.16, -0.046), (0.14, -0.062), (0, -0.062)],
            MAT['ceiling'], loc=(0, 0, RZ), steps=64, coll='Room')


# ----------------------------------------------------------------------------
# rug
# ----------------------------------------------------------------------------
def build_rug():
    oval_slab('Rug', 2.35, 1.72, 0.016, MAT['rug'], loc=(0, 0, 0.017),
              segments=90, rim=0.005, coll='Decor')
    oval_slab('Rug.Border', 2.20, 1.57, 0.006, MAT['rug_border'],
              loc=(0, 0, 0.0185), segments=90, rim=0.002, coll='Decor')
    oval_slab('Rug.Field', 2.06, 1.44, 0.005, MAT['rug'],
              loc=(0, 0, 0.020), segments=90, rim=0.002, coll='Decor')


# ----------------------------------------------------------------------------
# oval dining table
# ----------------------------------------------------------------------------
TABLE_A = 1.16      # semi-axis along X
TABLE_B = 0.79      # semi-axis along Y
TABLE_H = 0.755
TOP_T = 0.052


def build_table():
    root = empty('Table', coll='Table')

    # top: elliptical slab with a moulded edge and an inlaid banding
    oval_slab('Table.Top', TABLE_A, TABLE_B, TOP_T, MAT['walnut'],
              loc=(0, 0, TABLE_H), segments=96, rim=0.018, coll='Table',
              parent=root)
    oval_slab('Table.Banding', TABLE_A - 0.075, TABLE_B - 0.052, 0.0025,
              MAT['oak'], loc=(0, 0, TABLE_H + 0.0012), segments=96,
              rim=0.001, coll='Table', parent=root)
    oval_slab('Table.Inlay', TABLE_A - 0.105, TABLE_B - 0.073, 0.002,
              MAT['walnut'], loc=(0, 0, TABLE_H + 0.0022), segments=96,
              rim=0.001, coll='Table', parent=root)

    # apron following the ellipse, tucked under the top
    bm = bmesh.new()
    seg = 96
    ring_top, ring_bot = [], []
    for i in range(seg):
        a = TAU * i / seg
        x = (TABLE_A - 0.085) * math.cos(a)
        y = (TABLE_B - 0.062) * math.sin(a)
        ring_top.append(bm.verts.new((x, y, -0.012)))
        ring_bot.append(bm.verts.new((x * 0.985, y * 0.985, -0.10)))
    for i in range(seg):
        j = (i + 1) % seg
        bm.faces.new((ring_top[i], ring_top[j], ring_bot[j], ring_bot[i]))
    finalize('Table.Apron', bm, MAT['walnut'], loc=(0, 0, TABLE_H - TOP_T),
             smooth_angle=D2R(30), coll='Table', parent=root)

    # twin turned pedestals
    ped_profile = [
        (0.000, 0.000), (0.150, 0.000), (0.235, 0.012), (0.250, 0.034),
        (0.232, 0.058), (0.170, 0.082), (0.150, 0.104), (0.128, 0.118),
        (0.104, 0.150), (0.098, 0.205), (0.112, 0.240), (0.100, 0.270),
        (0.078, 0.320), (0.072, 0.420), (0.084, 0.500), (0.076, 0.545),
        (0.092, 0.575), (0.086, 0.600), (0.120, 0.628), (0.128, 0.648),
        (0.108, 0.660), (0.108, 0.672), (0.000, 0.672),
    ]
    for s in (-1, 1):
        px = s * 0.615
        revolve('Table.Pedestal.%s' % ('L' if s < 0 else 'R'),
                ped_profile, MAT['walnut'], loc=(px, 0, 0.028),
                steps=64, coll='Table', parent=root, smooth_angle=D2R(32))
        # splayed feet
        for fy in (-1, 1):
            for fx in (-1, 1):
                strut('Table.Foot.%s%d%d' % ('L' if s < 0 else 'R', fx, fy),
                      (px + fx * 0.055, fy * 0.055, 0.10),
                      (px + fx * 0.30, fy * 0.30, 0.032),
                      0.075, 0.055, MAT['walnut'], bevel=0.010,
                      coll='Table', parent=root)
                sphere('Table.FootPad.%s%d%d' % ('L' if s < 0 else 'R', fx, fy),
                       0.032, MAT['brass_dark'],
                       loc=(px + fx * 0.315, fy * 0.315, 0.028),
                       subdiv=2, coll='Table', parent=root,
                       scale=(1, 1, 0.7))
        # capital plate under the top
        box('Table.Cap.%s' % ('L' if s < 0 else 'R'), (0.19, 0.13, 0.014),
            MAT['walnut'], loc=(px, 0, 0.712), bevel=0.008, coll='Table',
            parent=root)

    # stretcher joining the pedestals
    strut('Table.Stretcher', (-0.60, 0, 0.235), (0.60, 0, 0.235),
          0.085, 0.085, MAT['walnut'], bevel=0.014, coll='Table', parent=root)
    revolve('Table.Stretcher.Ring', [(0, -0.05), (0.075, -0.05),
                                     (0.075, 0.05), (0, 0.05)],
            MAT['brass_dark'], loc=(0, 0, 0.235), steps=32,
            coll='Table', parent=root)


# ----------------------------------------------------------------------------
# upholstered chair
# ----------------------------------------------------------------------------
def build_chair(index, position, yaw, fabric):
    """Chair modelled facing +Y (back panel toward -Y), then placed."""
    root = empty('Chair.%02d' % index, loc=position, rot=(0, 0, yaw),
                 coll='Chairs')
    n = 'Chair.%02d' % index
    seat_h = 0.455
    wood = MAT['walnut']

    # --- frame -------------------------------------------------------------
    # front legs: tapered, slightly splayed
    for sx in (-1, 1):
        strut('%s.LegF.%d' % (n, sx),
              (sx * 0.205, 0.185, 0.0), (sx * 0.185, 0.170, seat_h - 0.055),
              0.048, 0.033, wood, bevel=0.006, coll='Chairs', parent=root)
    # rear legs continue upward into the back posts
    for sx in (-1, 1):
        strut('%s.LegB.%d' % (n, sx),
              (sx * 0.200, -0.180, 0.0), (sx * 0.188, -0.205, seat_h - 0.02),
              0.048, 0.040, wood, bevel=0.006, coll='Chairs', parent=root)
        strut('%s.Post.%d' % (n, sx),
              (sx * 0.188, -0.205, seat_h - 0.03), (sx * 0.178, -0.285, 1.005),
              0.042, 0.032, wood, bevel=0.006, coll='Chairs', parent=root)
        # rear foot pad
        sphere('%s.Pad.%d' % (n, sx), 0.024, MAT['brass_dark'],
               loc=(sx * 0.200, -0.180, 0.012), subdiv=2,
               scale=(1, 1, 0.55), coll='Chairs', parent=root)

    # seat rails
    rails = [((-0.20, 0.175, seat_h - 0.075), (0.20, 0.175, seat_h - 0.075)),
             ((-0.20, -0.185, seat_h - 0.075), (0.20, -0.185, seat_h - 0.075)),
             ((-0.195, -0.180, seat_h - 0.075), (-0.195, 0.175, seat_h - 0.075)),
             ((0.195, -0.180, seat_h - 0.075), (0.195, 0.175, seat_h - 0.075))]
    for i, (p0, p1) in enumerate(rails):
        strut('%s.Rail.%d' % (n, i), p0, p1, 0.042, 0.042, wood,
              bevel=0.006, coll='Chairs', parent=root)

    # cross stretcher between the side rails
    strut('%s.Stretcher' % n, (-0.19, -0.005, 0.155), (0.19, -0.005, 0.155),
          0.026, 0.026, wood, bevel=0.004, coll='Chairs', parent=root)

    # top rail crowning the back
    strut('%s.TopRail' % n, (-0.178, -0.285, 1.005), (0.178, -0.285, 1.005),
          0.052, 0.052, wood, bevel=0.010, coll='Chairs', parent=root)

    # --- upholstery --------------------------------------------------------
    # seat cushion: rounded box, gently crowned
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= 0.455
        v.co.y *= 0.415
        v.co.z *= 0.105
    bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges), offset=0.035,
                    segments=4, affect='EDGES', profile=0.55,
                    clamp_overlap=True)
    bmesh.ops.subdivide_edges(bm, edges=list(bm.edges), cuts=1,
                              use_grid_fill=True)
    for v in bm.verts:
        u = min(1.0, (v.co.x / 0.2275) ** 2 + (v.co.y / 0.2075) ** 2)
        if v.co.z > 0.0:
            v.co.z += 0.022 * (1.0 - u)
        v.co.y *= 1.0 + 0.02 * (1.0 - u)
    finalize('%s.Seat' % n, bm, fabric, loc=(0, -0.005, seat_h),
             smooth_angle=D2R(46), coll='Chairs', parent=root)

    # back panel: rounded box bent to wrap the sitter, with button tufting
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= 0.395
        v.co.y *= 0.105
        v.co.z *= 0.455
    bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges), offset=0.035,
                    segments=4, affect='EDGES', profile=0.55,
                    clamp_overlap=True)
    bmesh.ops.subdivide_edges(bm, edges=list(bm.edges), cuts=2,
                              use_grid_fill=True)
    for v in bm.verts:
        t = abs(v.co.x) / 0.1975
        v.co.y += 0.055 * t * t                  # wrap forward at the edges
        v.co.z += 0.012 * (1.0 - t)              # slight crown
        if v.co.y < -0.02:
            v.co.y -= 0.01
    finalize('%s.Back' % n, bm, fabric, loc=(0, -0.245, 0.745),
             rot=(D2R(-7), 0, 0), smooth_angle=D2R(46),
             coll='Chairs', parent=root)

    # tufting buttons on the front face of the back panel
    for bx in (-0.115, 0.0, 0.115):
        for bz in (0.655, 0.815):
            t = abs(bx) / 0.1975
            by = -0.245 + 0.055 * t * t - 0.055 - 0.008
            sphere('%s.Button.%d.%d' % (n, int(bx * 1000), int(bz * 1000)),
                   0.014, MAT['brass'], loc=(bx, by, bz), subdiv=2,
                   scale=(1, 0.55, 1), coll='Chairs', parent=root)

    # welt cord around the seat perimeter
    pts = []
    for i in range(13):
        a = -math.pi * 0.5 + math.pi * i / 12.0
        pts.append((0.235 * math.sin(a), -0.005 + 0.215 * math.cos(a),
                    seat_h - 0.048))
    tube_curve('%s.Welt' % n, pts, 0.007, MAT['fabric_dark'],
               coll='Chairs', parent=root)
    return root


def build_chairs():
    a, b = TABLE_A, TABLE_B
    clearance = 0.44
    angles = [0, 52, 90, 128, 180, 232, 270, 308]
    for i, deg in enumerate(angles):
        t = D2R(deg)
        px = (a + clearance) * math.cos(t)
        py = (b + clearance) * math.sin(t)
        # outward normal of the ellipse at this parameter
        nx, ny = math.cos(t) / a, math.sin(t) / b
        ln = math.hypot(nx, ny)
        nx, ny = nx / ln, ny / ln
        yaw = math.atan2(-ny, -nx) - math.pi * 0.5   # chair faces inward
        fabric = MAT['fabric'] if deg not in (0, 180) else MAT['fabric_dark']
        build_chair(i, (px, py, 0.0), yaw, fabric)


# ----------------------------------------------------------------------------
# sculptural chandelier
# ----------------------------------------------------------------------------
def build_chandelier():
    root = empty('Chandelier', loc=(0, 0, 0), coll='Chandelier')
    hub_z = 2.28

    # canopy, suspension rod and hub
    revolve('Chand.Canopy',
            [(0, 0), (0.13, -0.005), (0.145, -0.030), (0.115, -0.060),
             (0.030, -0.075), (0.026, -0.090), (0, -0.090)],
            MAT['brass'], loc=(0, 0, RZ - 0.002), steps=48,
            coll='Chandelier', parent=root)
    revolve('Chand.Rod', [(0, 0), (0.017, 0), (0.017, RZ - hub_z - 0.24),
                          (0, RZ - hub_z - 0.24)],
            MAT['brass'], loc=(0, 0, hub_z + 0.24), steps=24,
            coll='Chandelier', parent=root)
    revolve('Chand.Hub',
            [(0, 0.30), (0.055, 0.285), (0.085, 0.230), (0.070, 0.180),
             (0.105, 0.140), (0.150, 0.075), (0.155, 0.030),
             (0.120, -0.010), (0.060, -0.040), (0, -0.050)],
            MAT['brass'], loc=(0, 0, hub_z), steps=64,
            coll='Chandelier', parent=root, smooth_angle=D2R(34))

    # three sculptural tiers of sweeping arms
    tiers = [
        dict(count=6, r=0.34, z_tip=2.12, sag=-0.10, twist=0.0, drop=0.0),
        dict(count=9, r=0.58, z_tip=1.95, sag=-0.16, twist=20.0, drop=0.0),
        dict(count=12, r=0.84, z_tip=1.82, sag=-0.22, twist=35.0, drop=0.10),
    ]
    for ti, tier in enumerate(tiers):
        cnt = tier['count']
        r = tier['r']
        z_tip = tier['z_tip']
        # brass ring linking the arm tips (torus, lathed circle profile)
        ring_prof = []
        for k in range(14):
            a = TAU * k / 14
            ring_prof.append((r + 0.011 * math.cos(a), 0.011 * math.sin(a)))
        revolve('Chand.Ring.%d' % ti, ring_prof, MAT['brass'],
                loc=(0, 0, z_tip - 0.035), steps=88, closed=True,
                coll='Chandelier', parent=root, smooth_angle=D2R(60))

        for i in range(cnt):
            ang = TAU * i / cnt + D2R(tier['twist'])
            pts = [
                (0.05, 0.0, hub_z - 0.02 - tier['drop']),
                (r * 0.35, 0.0, hub_z - 0.06 + tier['sag'] - tier['drop']),
                (r * 0.72, 0.0, z_tip - 0.16),
                (r * 0.98, 0.0, z_tip - 0.045),
                (r, 0.0, z_tip + 0.035),
            ]
            tube_curve('Chand.Arm.%d.%d' % (ti, i), pts, 0.0135,
                       MAT['brass'], rot=(0, 0, ang), coll='Chandelier',
                       parent=root, taper_end=True)

            cx, cy = r * math.cos(ang), r * math.sin(ang)
            # socket cup
            revolve('Chand.Cup.%d.%d' % (ti, i),
                    [(0, 0), (0.028, 0.004), (0.040, 0.028),
                     (0.034, 0.040), (0.021, 0.040), (0.021, 0.062),
                     (0, 0.062)],
                    MAT['brass'], loc=(cx, cy, z_tip + 0.035), steps=28,
                    coll='Chandelier', parent=root)
            # blown-glass shade (open bell), lathed
            shade_prof = [
                (0.020, 0.000), (0.030, 0.010), (0.034, 0.045),
                (0.060, 0.075), (0.082, 0.115), (0.088, 0.160),
                (0.078, 0.200), (0.052, 0.228), (0.030, 0.238),
            ]
            shade = revolve('Chand.Shade.%d.%d' % (ti, i), shade_prof,
                            MAT['glass'], loc=(cx, cy, z_tip + 0.085),
                            steps=48, coll='Chandelier', parent=root,
                            smooth_angle=D2R(60))
            sol = shade.modifiers.new('Solidify', 'SOLIDIFY')
            sol.thickness = 0.004
            sol.offset = 0.0
            # bulb
            sphere('Chand.Bulb.%d.%d' % (ti, i), 0.036, MAT['bulb'],
                   loc=(cx, cy, z_tip + 0.155), subdiv=2,
                   scale=(1, 1, 1.25), coll='Chandelier', parent=root)

    # cascading glass drops hung between the tiers -> the "sculptural" core
    drop_prof = [(0.0, 0.0), (0.026, 0.030), (0.038, 0.075),
                 (0.030, 0.120), (0.014, 0.150), (0.0, 0.158)]
    rings = [(0.20, 7, 2.06, 0.0), (0.44, 11, 1.90, 15.0),
             (0.68, 14, 1.76, 28.0)]
    for ri, (rr, cnt, zz, off) in enumerate(rings):
        for i in range(cnt):
            ang = TAU * i / cnt + D2R(off)
            dx, dy = rr * math.cos(ang), rr * math.sin(ang)
            dz = zz - 0.05 * ((i % 3) - 1)
            revolve('Chand.Drop.%d.%d' % (ri, i), drop_prof,
                    MAT['glass'], loc=(dx, dy, dz), steps=32,
                    coll='Chandelier', parent=root, smooth_angle=D2R(60))
            tube_curve('Chand.DropWire.%d.%d' % (ri, i),
                       [(dx, dy, dz + 0.30), (dx, dy, dz + 0.16)],
                       0.0025, MAT['brass'], coll='Chandelier', parent=root)

    # central frosted orb for a soft glow
    orb = sphere('Chand.Orb', 0.115, MAT['glass_frosted'],
                 loc=(0, 0, 1.98), subdiv=3, coll='Chandelier', parent=root)
    sphere('Chand.Orb.Core', 0.060, MAT['bulb'], loc=(0, 0, 1.98),
           subdiv=2, coll='Chandelier', parent=root)
    orb.modifiers.new('Solidify', 'SOLIDIFY').thickness = 0.004

    # finial
    revolve('Chand.Finial',
            [(0, 0), (0.045, -0.02), (0.055, -0.06), (0.035, -0.11),
             (0.020, -0.14), (0.026, -0.18), (0.010, -0.23), (0, -0.245)],
            MAT['brass'], loc=(0, 0, 1.88), steps=40,
            coll='Chandelier', parent=root)
    return root


# ----------------------------------------------------------------------------
# table decor
# ----------------------------------------------------------------------------
def build_decor():
    top = TABLE_H + 0.003

    # centrepiece bowl with fruit
    revolve('Bowl',
            [(0.000, 0.000), (0.085, 0.004), (0.140, 0.028), (0.175, 0.072),
             (0.190, 0.112), (0.185, 0.122), (0.160, 0.086), (0.120, 0.042),
             (0.070, 0.020), (0.000, 0.016)],
            MAT['porcelain'], loc=(0, 0, top), steps=64, coll='Decor',
            smooth_angle=D2R(40))
    fruit = [(-0.06, 0.02, 0.055, MAT['fruit_a']),
             (0.055, -0.03, 0.052, MAT['fruit_b']),
             (0.01, 0.07, 0.050, MAT['fruit_b']),
             (0.00, -0.02, 0.048, MAT['fruit_a']),
             (0.075, 0.055, 0.045, MAT['fruit_a']),
             (-0.02, 0.01, 0.046, MAT['fruit_b'])]
    for i, (fx, fy, fr, fm) in enumerate(fruit):
        sphere('Fruit.%d' % i, fr, fm,
               loc=(fx, fy, top + 0.062 + (0.03 if i > 3 else 0.0)),
               subdiv=3, scale=(1, 1, 0.92), coll='Decor')

    # pair of turned brass candlesticks with candles
    stick = [(0.000, 0.000), (0.062, 0.002), (0.070, 0.012), (0.050, 0.026),
             (0.026, 0.040), (0.020, 0.075), (0.030, 0.098), (0.020, 0.115),
             (0.018, 0.150), (0.028, 0.168), (0.020, 0.185), (0.045, 0.205),
             (0.048, 0.216), (0.030, 0.222), (0.024, 0.230), (0.000, 0.230)]
    for s, sx in enumerate((-0.60, 0.60)):
        revolve('Candlestick.%d' % s, stick, MAT['brass'],
                loc=(sx, 0.0, top), steps=48, coll='Decor',
                smooth_angle=D2R(34))
        revolve('Candle.%d' % s,
                [(0, 0), (0.019, 0), (0.019, 0.215), (0.014, 0.228), (0, 0.230)],
                MAT['candle'], loc=(sx, 0.0, top + 0.226), steps=28,
                coll='Decor')
        sphere('Flame.%d' % s, 0.014, MAT['flame'],
               loc=(sx, 0.0, top + 0.472), subdiv=2, scale=(1, 1, 2.0),
               coll='Decor')

    # place settings: plate, napkin, glass and cutlery at each chair
    a, b = TABLE_A, TABLE_B
    for i, deg in enumerate([0, 52, 90, 128, 180, 232, 270, 308]):
        t = D2R(deg)
        nx, ny = math.cos(t) / a, math.sin(t) / b
        ln = math.hypot(nx, ny)
        nx, ny = nx / ln, ny / ln
        px = (a - 0.245) * math.cos(t)
        py = (b - 0.245) * math.sin(t)
        revolve('Plate.%d' % i,
                [(0.000, 0.010), (0.075, 0.004), (0.115, 0.008),
                 (0.135, 0.021), (0.138, 0.024), (0.118, 0.014),
                 (0.070, 0.000), (0.000, 0.000)],
                MAT['porcelain'], loc=(px, py, top), steps=48,
                coll='Decor', smooth_angle=D2R(36))
        # wine glass, offset to the upper right of the setting
        tx, ty = -ny, nx
        gx = px + tx * 0.135 - nx * 0.10
        gy = py + ty * 0.135 - ny * 0.10
        glass = revolve('WineGlass.%d' % i,
                        [(0.000, 0.000), (0.042, 0.002), (0.044, 0.008),
                         (0.010, 0.018), (0.007, 0.070), (0.020, 0.088),
                         (0.038, 0.112), (0.044, 0.150), (0.040, 0.185),
                         (0.036, 0.196)],
                        MAT['glass'], loc=(gx, gy, top), steps=40,
                        coll='Decor', smooth_angle=D2R(60))
        glass.modifiers.new('Solidify', 'SOLIDIFY').thickness = 0.0025
        # folded napkin on the plate
        box('Napkin.%d' % i, (0.055, 0.055, 0.006), MAT['fabric'],
            loc=(px, py, top + 0.028), rot=(0, 0, D2R(deg) + D2R(18)),
            bevel=0.004, coll='Decor')
        # cutlery
        for k, sgn in ((0, -1), (1, 1)):
            cx = px + tx * sgn * 0.185
            cy = py + ty * sgn * 0.185
            box('Cutlery.%d.%d' % (i, k), (0.008, 0.055, 0.003),
                MAT['brass_dark'], loc=(cx, cy, top + 0.002),
                rot=(0, 0, math.atan2(ty, tx)), bevel=0.002, coll='Decor')


def build_sideboard():
    root = empty('Sideboard', loc=(-RX + 0.26, -0.35, 0), rot=(0, 0, D2R(-90)),
                 coll='Decor')
    w, d, h = 1.60, 0.46, 0.80
    # carcass
    box('Sideboard.Body', (w * 0.5, d * 0.5, h * 0.5 - 0.02), MAT['walnut'],
        loc=(0, 0, 0.20 + h * 0.5 - 0.02), bevel=0.008, coll='Decor',
        parent=root)
    box('Sideboard.Top', (w * 0.5 + 0.03, d * 0.5 + 0.025, 0.021),
        MAT['stone'], loc=(0, 0, 0.20 + h - 0.02 + 0.021), bevel=0.008,
        coll='Decor', parent=root)
    # doors and hardware
    for s in (-1, 1):
        box('Sideboard.Door.%d' % s, (w * 0.245, 0.012, h * 0.5 - 0.09),
            MAT['oak'], loc=(s * w * 0.25, -d * 0.5 - 0.010,
                             0.20 + h * 0.5 - 0.02),
            bevel=0.008, coll='Decor', parent=root)
        revolve('Sideboard.Knob.%d' % s,
                [(0, 0), (0.014, 0.0), (0.020, 0.014), (0.014, 0.028), (0, 0.030)],
                MAT['brass'], loc=(s * 0.10, -d * 0.5 - 0.022,
                                   0.20 + h * 0.5 - 0.02),
                rot=(D2R(-90), 0, 0), steps=24, coll='Decor', parent=root)
    # tapered legs
    for sx in (-1, 1):
        for sy in (-1, 1):
            strut('Sideboard.Leg.%d.%d' % (sx, sy),
                  (sx * (w * 0.5 - 0.05), sy * (d * 0.5 - 0.05), 0.0),
                  (sx * (w * 0.5 - 0.06), sy * (d * 0.5 - 0.06), 0.215),
                  0.055, 0.032, MAT['walnut'], bevel=0.005,
                  coll='Decor', parent=root)
    # objects on top
    revolve('Sideboard.Vase',
            [(0.000, 0.000), (0.070, 0.000), (0.075, 0.030), (0.098, 0.090),
             (0.100, 0.160), (0.072, 0.230), (0.052, 0.270), (0.056, 0.300),
             (0.048, 0.310), (0.044, 0.300), (0.044, 0.230), (0.062, 0.160),
             (0.060, 0.060), (0.000, 0.030)],
            MAT['porcelain'], loc=(-0.42, 0.0, 0.20 + h + 0.022), steps=52,
            coll='Decor', parent=root, smooth_angle=D2R(40))
    for i, (bx, br) in enumerate(((0.38, 0.055), (0.50, 0.042))):
        sphere('Sideboard.Orb.%d' % i, br, MAT['brass_dark'],
               loc=(bx, 0.02, 0.20 + h + 0.022 + br), subdiv=3,
               coll='Decor', parent=root)

    # framed artwork above the sideboard
    art = empty('Artwork', loc=(-RX + 0.03, -0.35, 1.85), rot=(0, 0, D2R(-90)),
                coll='Decor')
    box('Artwork.Frame', (0.52, 0.035, 0.38), MAT['brass_dark'],
        loc=(0, 0, 0), bevel=0.012, coll='Decor', parent=art)
    box('Artwork.Canvas', (0.475, 0.010, 0.335), MAT['canvas'],
        loc=(0, -0.030, 0), coll='Decor', parent=art)


# ----------------------------------------------------------------------------
# lighting, world and camera
# ----------------------------------------------------------------------------
def build_lighting():
    # cool daylight pushed through each window
    for i, (cx, w, z0, z1) in enumerate(WINDOWS):
        ld = bpy.data.lights.new('Daylight.%d' % i, 'AREA')
        ld.shape = 'RECTANGLE'
        ld.size = w * 0.95
        ld.size_y = (z1 - z0) * 0.95
        ld.energy = 420.0
        ld.color = (0.78, 0.86, 1.0)
        ld.spread = D2R(105)
        obj = bpy.data.objects.new('Daylight.%d' % i, ld)
        obj.location = (cx, RY + 0.22, (z0 + z1) * 0.5)
        obj.rotation_euler = (D2R(90), 0, math.pi)   # emit toward -Y
        link(obj, 'Lights')

    # warm practical inside the chandelier
    lp = bpy.data.lights.new('Chandelier.Lamp', 'POINT')
    lp.energy = 110.0
    lp.color = (1.0, 0.79, 0.58)
    lp.shadow_soft_size = 0.22
    obj = bpy.data.objects.new('Chandelier.Lamp', lp)
    obj.location = (0, 0, 2.0)
    link(obj, 'Lights')

    # soft bounce fill from the room's near corner, plus a gentle wall wash
    lf = bpy.data.lights.new('Fill.Area', 'AREA')
    lf.shape = 'RECTANGLE'
    lf.size = 3.2
    lf.size_y = 2.2
    lf.energy = 55.0
    lf.color = (1.0, 0.94, 0.86)
    obj = bpy.data.objects.new('Fill.Area', lf)
    obj.location = (1.7, -2.1, 2.72)
    obj.rotation_euler = (D2R(28), D2R(-14), 0)
    link(obj, 'Lights')

    lu = bpy.data.lights.new('Wall.Wash', 'AREA')
    lu.shape = 'RECTANGLE'
    lu.size = 2.0
    lu.size_y = 1.2
    lu.energy = 22.0
    lu.color = (1.0, 0.87, 0.72)
    obj = bpy.data.objects.new('Wall.Wash', lu)
    obj.location = (-RX + 0.35, -0.35, 1.05)
    obj.rotation_euler = (0, D2R(78), 0)
    link(obj, 'Lights')


def build_world():
    world = bpy.data.worlds.get('World') or bpy.data.worlds.new('World')
    bpy.context.scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputWorld')
    out.location = (400, 0)
    bg = nt.nodes.new('ShaderNodeBackground')
    bg.location = (180, 0)
    bg.inputs['Strength'].default_value = 1.4
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.location = (-60, 0)
    ramp.color_ramp.elements[0].position = 0.32
    ramp.color_ramp.elements[0].color = (0.55, 0.60, 0.58, 1.0)
    ramp.color_ramp.elements[1].position = 0.62
    ramp.color_ramp.elements[1].color = (0.42, 0.60, 0.92, 1.0)
    grad = nt.nodes.new('ShaderNodeTexGradient')
    grad.location = (-280, 0)
    grad.gradient_type = 'EASING'
    mapping = nt.nodes.new('ShaderNodeMapping')
    mapping.location = (-470, 0)
    mapping.inputs['Rotation'].default_value = (0, D2R(-90), 0)
    coords = nt.nodes.new('ShaderNodeTexCoord')
    coords.location = (-660, 0)
    L = nt.links.new
    L(coords.outputs['Generated'], mapping.inputs['Vector'])
    L(mapping.outputs['Vector'], grad.inputs['Vector'])
    L(grad.outputs['Fac'], ramp.inputs['Fac'])
    L(ramp.outputs['Color'], bg.inputs['Color'])
    L(bg.outputs['Background'], out.inputs['Surface'])


def build_camera():
    cam_data = bpy.data.cameras.new('Camera')
    cam_data.lens = 28.0
    cam_data.sensor_width = 36.0
    cam_data.clip_start = 0.02
    cam_data.clip_end = 120.0
    cam_data.dof.use_dof = True
    cam_data.dof.aperture_fstop = 3.2
    cam = bpy.data.objects.new('Camera', cam_data)
    cam.location = (2.62, -2.02, 1.66)
    link(cam, 'Lights')

    target = empty('Camera.Target', loc=(-0.12, 0.18, 1.02), coll='Lights')
    con = cam.constraints.new('TRACK_TO')
    con.target = target
    con.track_axis = 'TRACK_NEGATIVE_Z'
    con.up_axis = 'UP_Y'
    cam_data.dof.focus_object = target

    bpy.context.scene.camera = cam
    return cam


# ----------------------------------------------------------------------------
# assemble
# ----------------------------------------------------------------------------
def main():
    reset_scene()
    for name in ('Room', 'Table', 'Chairs', 'Chandelier', 'Decor',
                 'Lights', 'Utility'):
        collection(name)
    build_materials()
    build_room()
    build_rug()
    build_table()
    build_chairs()
    build_chandelier()
    build_decor()
    build_sideboard()
    build_lighting()
    build_world()
    build_camera()
    bpy.context.view_layer.update()


main()
