"""claude-028 : freestanding floor lamp with an adjustable arm (Blender 4.5 LTS)."""

import bpy, bmesh, math
from mathutils import Vector, Matrix, Euler

TAU = math.pi * 2.0

# --------------------------------------------------------------------------- #
#  helpers
# --------------------------------------------------------------------------- #

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = 'METRIC'
    sc.render.engine = 'CYCLES'
    if hasattr(sc, "cycles"):
        sc.cycles.samples = 128
        sc.cycles.use_denoising = True
    sc.render.resolution_x = 1400
    sc.render.resolution_y = 1700
    world = bpy.data.worlds.new("World")
    sc.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.030, 0.033, 0.042, 1.0)
    bg.inputs["Strength"].default_value = 1.0
    return sc


def link(obj):
    bpy.context.scene.collection.objects.link(obj)
    return obj


def _M(size, loc, rot, pre=None):
    m = (Matrix.Translation(Vector(loc))
         @ Euler(rot, 'XYZ').to_matrix().to_4x4()
         @ Matrix.Diagonal(Vector(size).to_4d()))
    return (pre @ m) if pre is not None else m


def add_box(bm, size, loc=(0.0, 0.0, 0.0), rot=(0.0, 0.0, 0.0), pre=None):
    bmesh.ops.create_cube(bm, size=1.0, matrix=_M(size, loc, rot, pre), calc_uvs=True)


def add_cyl(bm, radius, depth, loc=(0.0, 0.0, 0.0), rot=(0.0, 0.0, 0.0),
            segments=24, r2=None, caps=True, pre=None):
    m = _M((1.0, 1.0, 1.0), loc, rot, pre)
    before = set(bm.faces)
    bmesh.ops.create_cone(bm, cap_ends=caps, cap_tris=False, segments=segments,
                          radius1=radius, radius2=(radius if r2 is None else r2),
                          depth=depth, matrix=m, calc_uvs=True)
    axis = (m.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized()
    for f in bm.faces:
        if f not in before and abs(f.normal.normalized().dot(axis)) < 0.85:
            f.smooth = True


def add_sphere(bm, radius, loc=(0.0, 0.0, 0.0), u=24, v=12, pre=None):
    before = set(bm.faces)
    bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=radius,
                              matrix=_M((1.0, 1.0, 1.0), loc, (0.0, 0.0, 0.0), pre),
                              calc_uvs=True)
    for f in bm.faces:
        if f not in before:
            f.smooth = True


def add_tube(bm, p1, p2, radius, segments=20, caps=True):
    a, b = Vector(p1), Vector(p2)
    d = b - a
    if d.length < 1e-6:
        return
    m = Matrix.Translation((a + b) * 0.5) @ d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
    before = set(bm.faces)
    bmesh.ops.create_cone(bm, cap_ends=caps, cap_tris=False, segments=segments,
                          radius1=radius, radius2=radius, depth=d.length,
                          matrix=m, calc_uvs=True)
    axis = d.normalized()
    for f in bm.faces:
        if f not in before and abs(f.normal.normalized().dot(axis)) < 0.85:
            f.smooth = True


def finish(name, bm, mat=None, loc=(0.0, 0.0, 0.0), rot=(0.0, 0.0, 0.0),
           bevel=0.0, bevel_seg=2):
    if bevel > 0.0:
        geom = list(bm.verts) + list(bm.edges) + list(bm.faces)
        bmesh.ops.bevel(bm, geom=geom, offset=bevel, offset_type='OFFSET',
                        segments=bevel_seg, profile=0.5, affect='EDGES',
                        clamp_overlap=True)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.validate()
    obj = bpy.data.objects.new(name, me)
    obj.location = loc
    obj.rotation_euler = rot
    if mat is not None:
        me.materials.append(mat)
    return link(obj)


def mat_simple(name, color, rough=0.5, metallic=0.0, emis=None, emis_str=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    b = mat.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metallic
    if emis is not None:
        key = "Emission Color" if "Emission Color" in b.inputs else "Emission"
        b.inputs[key].default_value = (emis[0], emis[1], emis[2], 1.0)
        b.inputs["Emission Strength"].default_value = emis_str
    return mat


def mat_noisy(name, c1, c2, scale=8.0, detail=6.0, rough=0.65,
              mapping_scale=(1.0, 1.0, 1.0), bump=0.15, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    b = nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metallic
    coord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = mapping_scale
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = scale
    noise.inputs["Detail"].default_value = detail
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.36
    ramp.color_ramp.elements[0].color = (c1[0], c1[1], c1[2], 1.0)
    ramp.color_ramp.elements[1].position = 0.64
    ramp.color_ramp.elements[1].color = (c2[0], c2[1], c2[2], 1.0)
    bumpn = nodes.new("ShaderNodeBump")
    bumpn.inputs["Strength"].default_value = bump
    links.new(coord.outputs["Object"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    links.new(noise.outputs["Fac"], bumpn.inputs["Height"])
    links.new(bumpn.outputs["Normal"], b.inputs["Normal"])
    return mat


def add_camera(loc, target, lens=50.0):
    cd = bpy.data.cameras.new("Camera")
    cd.lens = lens
    obj = bpy.data.objects.new("Camera", cd)
    obj.location = loc
    obj.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    link(obj)
    bpy.context.scene.camera = obj
    return obj


def add_area(name, loc, target, energy, size=2.0, color=(1.0, 1.0, 1.0)):
    ld = bpy.data.lights.new(name, type='AREA')
    ld.energy = energy
    ld.size = size
    ld.color = color
    obj = bpy.data.objects.new(name, ld)
    obj.location = loc
    obj.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return link(obj)


# --------------------------------------------------------------------------- #
#  lamp geometry
# --------------------------------------------------------------------------- #

POLE_TOP = 1.300
JOINT_A = Vector((0.0, 0.000, POLE_TOP))      # shoulder
JOINT_B = Vector((0.0, 0.300, 1.660))         # elbow
JOINT_C = Vector((0.0, 0.860, 1.520))         # wrist
HEAD_DIR = Vector((0.0, 0.30, -1.0)).normalized()


def build_base(brass, felt, dark):
    bm = bmesh.new()
    add_cyl(bm, 0.170, 0.030, (0.0, 0.0, 0.021), segments=48)
    add_cyl(bm, 0.168, 0.040, (0.0, 0.0, 0.056), r2=0.120, segments=48)
    add_cyl(bm, 0.052, 0.040, (0.0, 0.0, 0.094), segments=32)
    finish("LampBase", bm, brass, bevel=0.004, bevel_seg=2)

    bm = bmesh.new()
    add_cyl(bm, 0.166, 0.008, (0.0, 0.0, 0.004), segments=48)
    finish("BaseFelt", bm, felt)

    bm = bmesh.new()
    add_box(bm, (0.046, 0.036, 0.070), (0.0, -0.020, 0.900))
    add_cyl(bm, 0.013, 0.024, (0.0, -0.040, 0.912), (math.pi * 0.5, 0.0, 0.0),
            segments=16)
    finish("SwitchBlock", bm, dark, bevel=0.004, bevel_seg=2)


def build_pole(brass):
    bm = bmesh.new()
    add_cyl(bm, 0.019, 0.560, (0.0, 0.0, 0.390), segments=32)
    add_cyl(bm, 0.022, 0.026, (0.0, 0.0, 0.672), segments=32)
    add_cyl(bm, 0.015, 0.640, (0.0, 0.0, 1.000), segments=32)
    finish("LampPole", bm, brass)


def build_arm(brass, dark):
    bm = bmesh.new()
    add_sphere(bm, 0.033, JOINT_A, u=28, v=14)
    add_sphere(bm, 0.031, JOINT_B, u=28, v=14)
    add_sphere(bm, 0.029, JOINT_C, u=28, v=14)
    add_tube(bm, JOINT_A, JOINT_B, 0.0145)
    add_tube(bm, JOINT_B, JOINT_C, 0.0135)
    # counter-tension rod alongside the first segment
    add_tube(bm, JOINT_A + Vector((0.024, 0.010, 0.0)),
             JOINT_B + Vector((0.024, -0.010, 0.0)), 0.005)
    finish("LampArm", bm, brass)

    bm = bmesh.new()
    for p, r in ((JOINT_A, 0.020), (JOINT_B, 0.019), (JOINT_C, 0.018)):
        add_cyl(bm, r, 0.052, p, (0.0, math.pi * 0.5, 0.0), segments=14)
        add_cyl(bm, r * 0.45, 0.070, p, (0.0, math.pi * 0.5, 0.0), segments=10)
    finish("JointKnobs", bm, dark)


def build_head(brass, shade_in, bulb_mat, dark):
    pre = (Matrix.Translation(JOINT_C)
           @ HEAD_DIR.to_track_quat('Z', 'Y').to_matrix().to_4x4())

    bm = bmesh.new()
    add_cyl(bm, 0.028, 0.070, (0.0, 0.0, 0.030), segments=20, pre=pre)   # neck
    add_cyl(bm, 0.055, 0.210, (0.0, 0.0, 0.170), r2=0.150, segments=48,
            caps=False, pre=pre)                                        # shade shell
    add_cyl(bm, 0.152, 0.014, (0.0, 0.0, 0.272), segments=48, pre=pre)   # rim ring
    finish("ShadeOuter", bm, brass)

    bm = bmesh.new()
    add_cyl(bm, 0.050, 0.204, (0.0, 0.0, 0.170), r2=0.145, segments=48,
            caps=False, pre=pre)
    add_cyl(bm, 0.050, 0.004, (0.0, 0.0, 0.070), segments=32, pre=pre)
    finish("ShadeInner", bm, shade_in)

    bm = bmesh.new()
    add_cyl(bm, 0.020, 0.048, (0.0, 0.0, 0.098), segments=18, pre=pre)
    finish("BulbSocket", bm, dark)

    bm = bmesh.new()
    add_sphere(bm, 0.034, (0.0, 0.0, 0.155), u=28, v=16, pre=pre)
    finish("Bulb", bm, bulb_mat)

    ld = bpy.data.lights.new("BulbLight", type='POINT')
    ld.energy = 110.0
    ld.color = (1.0, 0.86, 0.68)
    ld.shadow_soft_size = 0.035
    lo = bpy.data.objects.new("BulbLight", ld)
    lo.location = JOINT_C + HEAD_DIR * 0.165
    link(lo)


def build_cord(cord_mat, dark):
    cu = bpy.data.curves.new("Cord", type='CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = 0.0065
    cu.bevel_resolution = 3
    cu.resolution_u = 12
    sp = cu.splines.new('BEZIER')
    pts = [(0.100, 0.020, 0.014), (0.430, -0.240, 0.007),
           (0.900, -0.300, 0.007), (1.380, -0.560, 0.007)]
    sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = p
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
    cu.materials.append(cord_mat)
    link(bpy.data.objects.new("Cord", cu))

    bm = bmesh.new()
    add_box(bm, (0.070, 0.048, 0.030), (1.420, -0.585, 0.016), (0.0, 0.0, -0.45))
    finish("Plug", bm, dark, bevel=0.004, bevel_seg=2)


# --------------------------------------------------------------------------- #
#  scene
# --------------------------------------------------------------------------- #

def main():
    reset_scene()

    brass = mat_noisy("BrushedBrass", (0.52, 0.40, 0.19), (0.68, 0.55, 0.28),
                      scale=140.0, mapping_scale=(1.0, 1.0, 40.0),
                      rough=0.24, bump=0.05, metallic=1.0)
    dark = mat_simple("DarkMetal", (0.045, 0.045, 0.050), rough=0.40, metallic=0.6)
    felt = mat_simple("BaseFelt", (0.055, 0.050, 0.048), rough=0.92)
    shade_in = mat_simple("ShadeInner", (0.95, 0.93, 0.88), rough=0.55)
    bulb_mat = mat_simple("BulbGlass", (1.0, 0.92, 0.78), rough=0.30,
                          emis=(1.0, 0.84, 0.62), emis_str=22.0)
    cord_mat = mat_simple("Cord", (0.035, 0.035, 0.038), rough=0.60)
    floorm = mat_noisy("FloorOak", (0.24, 0.15, 0.085), (0.42, 0.29, 0.17),
                       scale=16.0, mapping_scale=(1.0, 30.0, 1.0),
                       rough=0.42, bump=0.12)
    wallm = mat_noisy("Wall", (0.30, 0.31, 0.33), (0.40, 0.41, 0.43),
                      scale=4.0, rough=0.90, bump=0.03)

    bm = bmesh.new()
    add_box(bm, (10.0, 10.0, 0.10), (0.0, 0.0, -0.05))
    finish("Floor", bm, floorm)

    bm = bmesh.new()
    add_box(bm, (10.0, 0.10, 4.0), (0.0, 1.700, 2.0))
    finish("Wall", bm, wallm)

    build_base(brass, felt, dark)
    build_pole(brass)
    build_arm(brass, dark)
    build_head(brass, shade_in, bulb_mat, dark)
    build_cord(cord_mat, dark)

    add_area("Key", (1.7, -1.9, 2.6), (0.0, 0.35, 1.20), 300.0, size=2.4,
             color=(1.0, 0.97, 0.92))
    add_area("Fill", (-2.0, -1.4, 1.6), (0.0, 0.20, 1.00), 90.0, size=3.0,
             color=(0.80, 0.87, 1.0))
    add_area("Rim", (-1.0, 1.2, 2.4), (0.0, 0.30, 1.40), 120.0, size=1.6)
    add_camera((1.55, -2.10, 1.38), (0.0, 0.34, 1.10), lens=46.0)


if __name__ == "__main__":
    main()
