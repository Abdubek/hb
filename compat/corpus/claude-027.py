"""claude-027 : a rolling office chair with five casters (Blender 4.5 LTS)."""

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
        sc.cycles.samples = 96
        sc.cycles.use_denoising = True
    sc.render.resolution_x = 1400
    sc.render.resolution_y = 1600
    world = bpy.data.worlds.new("World")
    sc.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.055, 0.06, 0.07, 1.0)
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


def add_tube(bm, p1, p2, radius, segments=16, caps=True):
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


def mat_simple(name, color, rough=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    b = mat.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metallic
    return mat


def mat_noisy(name, c1, c2, scale=8.0, detail=6.0, rough=0.65,
              mapping_scale=(1.0, 1.0, 1.0), bump=0.15):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    b = nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
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
#  chair parts
# --------------------------------------------------------------------------- #

N_LEGS = 5
LEG_TIP = 0.325           # radial distance of each caster
WHEEL_R = 0.033


def build_base(plastic):
    bm = bmesh.new()
    add_cyl(bm, 0.076, 0.078, (0.0, 0.0, 0.075), segments=32)
    add_cyl(bm, 0.056, 0.055, (0.0, 0.0, 0.135), segments=28)
    for i in range(N_LEGS):
        pre = Matrix.Rotation(TAU * i / N_LEGS, 4, 'Z')
        add_box(bm, (0.300, 0.062, 0.042), (0.185, 0.0, 0.052), (0.0, 0.09, 0.0), pre=pre)
        add_box(bm, (0.100, 0.078, 0.058), (0.062, 0.0, 0.064), pre=pre)
    return finish("ChairBase", bm, plastic, bevel=0.006, bevel_seg=2)


def build_casters(plastic, rubber, steel):
    fb, wb, sb = bmesh.new(), bmesh.new(), bmesh.new()
    for i in range(N_LEGS):
        pre = Matrix.Rotation(TAU * i / N_LEGS, 4, 'Z')
        add_cyl(sb, 0.011, 0.055, (LEG_TIP, 0.0, 0.052), segments=16, pre=pre)
        add_box(fb, (0.058, 0.064, 0.030), (LEG_TIP, 0.0, 0.058), pre=pre)
        for sy in (-1, 1):
            add_box(fb, (0.046, 0.010, 0.056),
                    (LEG_TIP - 0.003, sy * 0.026, 0.036), pre=pre)
        add_cyl(wb, WHEEL_R, 0.030, (LEG_TIP - 0.003, 0.0, WHEEL_R),
                (math.pi * 0.5, 0.0, 0.0), segments=28, pre=pre)
        add_cyl(sb, 0.007, 0.064, (LEG_TIP - 0.003, 0.0, WHEEL_R),
                (math.pi * 0.5, 0.0, 0.0), segments=12, pre=pre)
    finish("CasterForks", fb, plastic, bevel=0.003, bevel_seg=1)
    finish("CasterWheels", wb, rubber)
    finish("CasterPins", sb, steel)


def build_column(plastic, alu):
    bm = bmesh.new()
    add_cyl(bm, 0.049, 0.200, (0.0, 0.0, 0.190), segments=28)
    add_cyl(bm, 0.035, 0.170, (0.0, 0.0, 0.340), segments=24)
    finish("ColumnShroud", bm, plastic, bevel=0.003, bevel_seg=1)
    bm = bmesh.new()
    add_cyl(bm, 0.029, 0.022, (0.0, 0.0, 0.416), segments=20)
    add_cyl(bm, 0.022, 0.100, (0.0, 0.0, 0.440), segments=20)
    finish("GasPiston", bm, alu)


def build_mechanism(plastic, alu):
    bm = bmesh.new()
    add_box(bm, (0.300, 0.260, 0.028), (0.0, 0.0, 0.462))
    add_box(bm, (0.104, 0.104, 0.052), (0.0, 0.0, 0.440))
    finish("TiltPlate", bm, plastic, bevel=0.004, bevel_seg=2)
    bm = bmesh.new()
    add_cyl(bm, 0.010, 0.170, (0.150, -0.070, 0.452),
            (0.0, math.pi * 0.5, 0.30), segments=12)
    add_cyl(bm, 0.010, 0.150, (-0.145, 0.030, 0.452),
            (0.0, math.pi * 0.5, -0.20), segments=12)
    finish("TiltLevers", bm, alu)


def build_seat(fabric):
    bm = bmesh.new()
    add_box(bm, (0.480, 0.460, 0.086), (0.0, 0.0, 0.519))
    add_box(bm, (0.430, 0.120, 0.070), (0.0, -0.185, 0.500))       # waterfall front
    return finish("SeatCushion", bm, fabric, bevel=0.028, bevel_seg=5)


def build_back(fabric, plastic):
    bm = bmesh.new()
    add_box(bm, (0.440, 0.062, 0.500), (0.0, 0.0, 0.0))
    add_box(bm, (0.400, 0.052, 0.170), (0.0, -0.030, -0.140))      # lumbar bulge
    finish("Backrest", bm, fabric, loc=(0.0, 0.315, 0.975),
           rot=(-0.200, 0.0, 0.0), bevel=0.030, bevel_seg=5)

    bm = bmesh.new()
    for sx in (-1, 1):
        add_tube(bm, (sx * 0.130, 0.185, 0.478), (sx * 0.130, 0.268, 0.740),
                 0.017, segments=16)
        add_box(bm, (0.070, 0.070, 0.060), (sx * 0.130, 0.190, 0.470))
    add_box(bm, (0.330, 0.055, 0.070), (0.0, 0.285, 0.760), (-0.200, 0.0, 0.0))
    finish("BackSupport", bm, plastic, bevel=0.005, bevel_seg=2)


def build_arms(plastic, alu):
    tb = bmesh.new()
    pb = bmesh.new()
    for sx in (-1, 1):
        add_tube(tb, (sx * 0.244, 0.030, 0.452), (sx * 0.244, 0.020, 0.618),
                 0.018, segments=16)
        add_box(tb, (0.055, 0.150, 0.030), (sx * 0.244, 0.030, 0.452))
        add_box(pb, (0.078, 0.250, 0.032), (sx * 0.240, -0.010, 0.640))
    finish("ArmPosts", tb, alu, bevel=0.004, bevel_seg=2)
    finish("ArmPads", pb, plastic, bevel=0.012, bevel_seg=3)


# --------------------------------------------------------------------------- #
#  scene
# --------------------------------------------------------------------------- #

def main():
    reset_scene()

    plastic = mat_simple("BlackPlastic", (0.028, 0.028, 0.032), rough=0.36)
    alu = mat_simple("Aluminium", (0.72, 0.73, 0.75), rough=0.28, metallic=1.0)
    steel = mat_simple("Steel", (0.55, 0.56, 0.58), rough=0.34, metallic=1.0)
    rubber = mat_noisy("CasterRubber", (0.030, 0.032, 0.036), (0.075, 0.078, 0.085),
                       scale=60.0, rough=0.62, bump=0.10)
    fabric = mat_noisy("SeatFabric", (0.085, 0.100, 0.150), (0.170, 0.200, 0.270),
                       scale=170.0, detail=8.0, rough=0.86, bump=0.35)
    floorm = mat_noisy("OfficeFloor", (0.30, 0.30, 0.315), (0.42, 0.42, 0.435),
                       scale=9.0, rough=0.55, bump=0.05)

    fb = bmesh.new()
    add_box(fb, (12.0, 12.0, 0.10), (0.0, 0.0, -0.05))
    finish("Floor", fb, floorm)

    build_base(plastic)
    build_casters(plastic, rubber, steel)
    build_column(plastic, alu)
    build_mechanism(plastic, alu)
    build_seat(fabric)
    build_back(fabric, plastic)
    build_arms(plastic, alu)

    add_area("Key", (1.6, -1.5, 2.4), (0.0, 0.0, 0.60), 700.0, size=2.2,
             color=(1.0, 0.97, 0.93))
    add_area("Fill", (-1.9, -1.0, 1.5), (0.0, 0.0, 0.55), 220.0, size=3.0,
             color=(0.84, 0.90, 1.0))
    add_area("Rim", (-0.8, 2.2, 2.0), (0.0, 0.15, 0.85), 420.0, size=1.8)
    add_camera((1.55, -1.85, 1.20), (0.0, 0.02, 0.56), lens=58.0)


if __name__ == "__main__":
    main()
