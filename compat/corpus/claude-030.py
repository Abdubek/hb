"""claude-030 : compact counterbalance forklift (Blender 4.5 LTS).

The truck faces +X: mast, carriage and forks are at the front, the
counterweight at the rear.
"""

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
    sc.render.resolution_x = 1800
    sc.render.resolution_y = 1200
    world = bpy.data.worlds.new("World")
    sc.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.050, 0.055, 0.068, 1.0)
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


def add_sphere(bm, radius, loc=(0.0, 0.0, 0.0), u=20, v=10, pre=None):
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


def add_torus(bm, major_r, minor_r, loc=(0.0, 0.0, 0.0), rot=(0.0, 0.0, 0.0),
              major=32, minor=12, pre=None):
    m = _M((1.0, 1.0, 1.0), loc, rot, pre)
    rings = []
    for i in range(major):
        u = TAU * i / major
        ring = []
        for j in range(minor):
            v = TAU * j / minor
            rr = major_r + minor_r * math.cos(v)
            p = Vector((rr * math.cos(u), rr * math.sin(u), minor_r * math.sin(v)))
            ring.append(bm.verts.new(m @ p))
        rings.append(ring)
    for i in range(major):
        for j in range(minor):
            f = bm.faces.new((rings[i][j],
                              rings[(i + 1) % major][j],
                              rings[(i + 1) % major][(j + 1) % minor],
                              rings[i][(j + 1) % minor]))
            f.smooth = True
    bm.normal_update()


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


def text_obj(name, body, size, loc, rot, mat, extrude=0.0015):
    cu = bpy.data.curves.new(name, type='FONT')
    cu.body = body
    cu.size = size
    cu.align_x = 'CENTER'
    cu.align_y = 'CENTER'
    cu.extrude = extrude
    obj = bpy.data.objects.new(name, cu)
    obj.location = loc
    obj.rotation_euler = rot
    if mat is not None:
        cu.materials.append(mat)
    return link(obj)


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
#  truck geometry
# --------------------------------------------------------------------------- #

FRONT_WHEEL = (0.580, 0.460, 0.300)      # x, |y|, radius
REAR_WHEEL = (-0.780, 0.440, 0.220)
MAST_X = 0.860


def build_chassis(paint, dark):
    bm = bmesh.new()
    add_box(bm, (1.760, 0.680, 0.460), (-0.075, 0.0, 0.450))            # main frame
    add_box(bm, (0.420, 0.720, 0.660), (-1.070, 0.0, 0.620))            # counterweight
    add_box(bm, (0.560, 0.700, 0.300), (-0.575, 0.0, 0.830))            # hood
    add_box(bm, (0.240, 0.640, 0.150), (0.640, 0.0, 0.720))             # front deck
    for sy in (-1, 1):                                                  # wheel arches
        add_box(bm, (0.700, 0.120, 0.220), (0.580, sy * 0.330, 0.560))
    finish("Chassis", bm, paint, bevel=0.030, bevel_seg=3)

    bm = bmesh.new()
    add_box(bm, (0.680, 0.660, 0.040), (0.020, 0.0, 0.690))             # floor plate
    add_box(bm, (0.070, 0.660, 0.070), (0.330, 0.0, 0.700))             # toe kick
    for sy in (-1, 1):
        add_box(bm, (0.640, 0.030, 0.180), (0.020, sy * 0.330, 0.780))  # side screens
    add_box(bm, (0.150, 0.560, 0.220), (-0.180, 0.0, 0.830), (0.0, -0.18, 0.0))
    finish("Cab", bm, dark, bevel=0.010, bevel_seg=2)


def build_operator(vinyl, dark, steel):
    bm = bmesh.new()
    add_box(bm, (0.400, 0.420, 0.100), (-0.550, 0.0, 1.030))            # cushion
    add_box(bm, (0.120, 0.420, 0.440), (-0.775, 0.0, 1.270), (0.0, -0.12, 0.0))
    finish("Seat", bm, vinyl, bevel=0.022, bevel_seg=3)

    bm = bmesh.new()
    add_box(bm, (0.300, 0.440, 0.070), (-0.550, 0.0, 0.965))            # seat frame
    add_cyl(bm, 0.045, 0.420, (-0.145, 0.0, 0.930), (0.0, -0.38, 0.0), segments=20)
    add_box(bm, (0.180, 0.300, 0.120), (-0.140, 0.0, 0.740))            # column base
    add_box(bm, (0.070, 0.055, 0.300), (-0.180, -0.300, 1.000), (0.0, -0.10, 0.0))
    add_cyl(bm, 0.022, 0.240, (-0.360, 0.300, 1.030), (0.0, -0.25, 0.0), segments=14)
    add_cyl(bm, 0.022, 0.240, (-0.360, 0.230, 1.030), (0.0, -0.25, 0.0), segments=14)
    finish("CabHardware", bm, dark, bevel=0.006, bevel_seg=2)

    bm = bmesh.new()
    add_torus(bm, 0.145, 0.017, (-0.055, 0.0, 1.148), (0.0, 0.42, 0.0),
              major=36, minor=10)
    finish("SteeringRim", bm, dark)

    bm = bmesh.new()
    pre = (Matrix.Translation(Vector((-0.055, 0.0, 1.148)))
           @ Matrix.Rotation(0.42, 4, 'Y'))
    add_cyl(bm, 0.048, 0.040, (0.0, 0.0, 0.0), segments=20, pre=pre)
    for a in (0.0, TAU / 3.0, 2.0 * TAU / 3.0):
        add_box(bm, (0.115, 0.030, 0.014),
                (0.072 * math.cos(a), 0.072 * math.sin(a), 0.0),
                (0.0, 0.0, a), pre=pre)
    add_sphere(bm, 0.026, (-0.360, 0.300, 1.155), u=16, v=8)            # lever knobs
    add_sphere(bm, 0.026, (-0.360, 0.230, 1.155), u=16, v=8)
    finish("SteeringHub", bm, steel)


def build_guard(paint, dark):
    bm = bmesh.new()
    for sy in (-1, 1):
        add_box(bm, (0.065, 0.065, 1.350), (0.300, sy * 0.330, 1.375))
        add_tube(bm, (-0.860, sy * 0.330, 0.960), (-0.790, sy * 0.330, 2.050), 0.034)
    for sy in (-1, 1):
        add_box(bm, (1.220, 0.060, 0.060), (-0.270, sy * 0.330, 2.030))
    for x in (0.310, -0.845):
        add_box(bm, (0.060, 0.720, 0.060), (x, 0.0, 2.030))
    for x in (-0.700, -0.470, -0.240, -0.010, 0.220):
        add_box(bm, (0.075, 0.700, 0.035), (x, 0.0, 2.055))
    finish("OverheadGuard", bm, paint, bevel=0.008, bevel_seg=2)

    bm = bmesh.new()
    add_box(bm, (0.120, 0.120, 0.030), (-0.470, 0.240, 2.088))
    finish("BeaconBase", bm, dark, bevel=0.005, bevel_seg=2)


def build_mast(paint, steel, chrome, dark):
    bm = bmesh.new()
    for sy in (-1, 1):                                                  # outer rails
        add_box(bm, (0.090, 0.100, 1.900), (MAST_X, sy * 0.300, 1.200))
    add_box(bm, (0.100, 0.780, 0.110), (MAST_X, 0.0, 0.300))            # crossmembers
    add_box(bm, (0.100, 0.780, 0.100), (MAST_X, 0.0, 2.100))
    add_box(bm, (0.180, 0.780, 0.130), (MAST_X - 0.060, 0.0, 0.310))    # tilt trunnion
    finish("MastOuter", bm, paint, bevel=0.010, bevel_seg=2)

    bm = bmesh.new()
    for sy in (-1, 1):                                                  # inner rails
        add_box(bm, (0.070, 0.080, 1.700), (MAST_X + 0.055, sy * 0.235, 1.350))
    add_box(bm, (0.070, 0.560, 0.090), (MAST_X + 0.055, 0.0, 2.170))
    add_cyl(bm, 0.056, 1.050, (MAST_X, 0.0, 0.880), segments=20)        # lift ram body
    for sy in (-1, 1):                                                  # chain sprockets
        add_cyl(bm, 0.055, 0.030, (MAST_X, sy * 0.130, 1.980),
                (math.pi * 0.5, 0.0, 0.0), segments=20)
    finish("MastInner", bm, steel, bevel=0.006, bevel_seg=2)

    bm = bmesh.new()
    add_cyl(bm, 0.032, 0.700, (MAST_X, 0.0, 1.680), segments=18)        # piston rod
    for sy in (-1, 1):                                                  # lift chains
        add_tube(bm, (MAST_X, sy * 0.130, 1.980), (MAST_X + 0.010, sy * 0.130, 0.760),
                 0.009, segments=8)
    finish("LiftRam", bm, chrome)

    bm = bmesh.new()
    for sy in (-1, 1):                                                  # hydraulic hoses
        add_tube(bm, (MAST_X - 0.070, sy * 0.190, 0.400),
                 (MAST_X - 0.020, sy * 0.190, 1.700), 0.012, segments=10)
    finish("Hoses", bm, dark)


def build_carriage_and_forks(steel, fork_mat):
    bm = bmesh.new()
    add_box(bm, (0.050, 0.860, 0.700), (0.980, 0.0, 0.530))             # backrest plate
    add_box(bm, (0.060, 0.900, 0.055), (0.995, 0.0, 0.845))             # upper fork bar
    add_box(bm, (0.060, 0.900, 0.055), (0.995, 0.0, 0.235))             # lower fork bar
    for sy in (-1, 1):
        add_box(bm, (0.070, 0.070, 0.640), (0.945, sy * 0.380, 0.540))  # side stiffeners
    for i in range(5):                                                  # load backrest
        add_box(bm, (0.030, 0.860, 0.045), (0.955, 0.0, 0.900 + i * 0.115))
    add_box(bm, (0.035, 0.860, 0.045), (0.955, 0.0, 1.480))
    finish("Carriage", bm, steel, bevel=0.008, bevel_seg=2)

    bm = bmesh.new()
    for sy in (-1, 1):
        pre = Matrix.Translation(Vector((0.0, sy * 0.260, 0.0)))
        add_box(bm, (0.055, 0.140, 0.800), (1.045, 0.0, 0.500), pre=pre)   # shank
        add_box(bm, (1.080, 0.140, 0.050), (1.585, 0.0, 0.075), pre=pre)   # blade
        add_box(bm, (0.100, 0.140, 0.060), (1.045, 0.0, 0.870), pre=pre)   # upper hook
        add_box(bm, (0.100, 0.140, 0.050), (1.045, 0.0, 0.240), pre=pre)   # lower hook
    tip_x = 1.585 + 0.540
    for v in bm.verts:                                                     # taper the tips
        if v.co.x > tip_x - 1e-4 and v.co.z > 0.070:
            v.co.z = 0.062
    finish("Forks", bm, fork_mat, bevel=0.005, bevel_seg=1)


def build_wheels(rubber, rim_mat):
    rb, hb = bmesh.new(), bmesh.new()
    for (cx, ay, r, width, lugs) in ((FRONT_WHEEL[0], FRONT_WHEEL[1], FRONT_WHEEL[2], 0.200, 22),
                                     (REAR_WHEEL[0], REAR_WHEEL[1], REAR_WHEEL[2], 0.150, 18)):
        for sy in (-1, 1):
            cy = sy * ay
            add_cyl(rb, r, width, (cx, cy, r), (math.pi * 0.5, 0.0, 0.0), segments=36)
            for i in range(lugs):
                t = TAU * i / lugs
                add_box(rb, (0.055, width + 0.008, 0.060),
                        (cx + (r - 0.012) * math.cos(t), cy, r + (r - 0.012) * math.sin(t)),
                        (0.0, -t, 0.0))
            add_cyl(hb, r * 0.55, width + 0.014, (cx, cy, r),
                    (math.pi * 0.5, 0.0, 0.0), segments=26)
            add_cyl(hb, r * 0.24, width + 0.055, (cx, cy, r),
                    (math.pi * 0.5, 0.0, 0.0), segments=18)
            for i in range(5):
                t = TAU * i / 5.0
                add_cyl(hb, 0.017, width + 0.040,
                        (cx + r * 0.33 * math.cos(t), cy, r + r * 0.33 * math.sin(t)),
                        (math.pi * 0.5, 0.0, 0.0), segments=8)
    finish("Tyres", rb, rubber)
    finish("Rims", hb, rim_mat)


def build_details(dark, lens_mat, beacon_mat, ink, steel):
    bm = bmesh.new()
    for sy in (-1, 1):                                                  # headlight cans
        add_cyl(bm, 0.058, 0.070, (0.735, sy * 0.250, 0.660),
                (0.0, math.pi * 0.5, 0.0), segments=20)
        add_cyl(bm, 0.050, 0.060, (-1.285, sy * 0.250, 0.760),
                (0.0, math.pi * 0.5, 0.0), segments=18)                 # rear work lamp
    add_box(bm, (0.120, 0.140, 0.090), (-1.190, 0.0, 0.980))            # exhaust box
    add_cyl(bm, 0.028, 0.220, (-1.190, 0.0, 1.100), segments=14)        # stack
    finish("LampBodies", bm, dark, bevel=0.005, bevel_seg=2)

    bm = bmesh.new()
    for sy in (-1, 1):
        add_cyl(bm, 0.050, 0.014, (0.772, sy * 0.250, 0.660),
                (0.0, math.pi * 0.5, 0.0), segments=20)
        add_cyl(bm, 0.043, 0.012, (-1.317, sy * 0.250, 0.760),
                (0.0, math.pi * 0.5, 0.0), segments=18)
    finish("LampLenses", bm, lens_mat)

    bm = bmesh.new()
    add_cyl(bm, 0.052, 0.080, (-0.470, 0.240, 2.143), segments=24)
    add_sphere(bm, 0.052, (-0.470, 0.240, 2.183), u=20, v=10)
    finish("Beacon", bm, beacon_mat)

    bm = bmesh.new()
    add_cyl(bm, 0.010, 0.340, (-0.480, -0.330, 2.230), segments=10)     # aerial
    finish("Aerial", bm, steel)

    text_obj("DecalCapacity", "2.5 t", 0.115,
             (-1.070, -0.362, 0.640), (math.pi * 0.5, 0.0, 0.0), ink)
    text_obj("DecalName", "LIFTMASTER  C25", 0.058,
             (-0.575, -0.352, 0.870), (math.pi * 0.5, 0.0, 0.0), ink)


# --------------------------------------------------------------------------- #
#  scene
# --------------------------------------------------------------------------- #

def main():
    reset_scene()

    paint = mat_noisy("ForkliftYellow", (0.78, 0.52, 0.030), (0.90, 0.66, 0.070),
                      scale=30.0, rough=0.32, bump=0.05)
    dark = mat_simple("DarkPlastic", (0.035, 0.035, 0.040), rough=0.42)
    vinyl = mat_noisy("SeatVinyl", (0.045, 0.045, 0.050), (0.085, 0.085, 0.095),
                      scale=150.0, rough=0.55, bump=0.25)
    steel = mat_simple("Steel", (0.42, 0.43, 0.45), rough=0.40, metallic=1.0)
    chrome = mat_simple("Chrome", (0.80, 0.81, 0.83), rough=0.14, metallic=1.0)
    fork_mat = mat_noisy("ForkSteel", (0.30, 0.30, 0.32), (0.48, 0.48, 0.50),
                         scale=45.0, rough=0.34, bump=0.08, metallic=1.0)
    rubber = mat_noisy("TyreRubber", (0.026, 0.028, 0.030), (0.070, 0.072, 0.078),
                       scale=55.0, rough=0.72, bump=0.18)
    rim_mat = mat_simple("Rim", (0.52, 0.53, 0.55), rough=0.38, metallic=0.9)
    lens_mat = mat_simple("Headlight", (1.0, 0.96, 0.86), rough=0.12,
                          emis=(1.0, 0.95, 0.82), emis_str=9.0)
    beacon_mat = mat_simple("Beacon", (0.90, 0.34, 0.02), rough=0.20,
                            emis=(1.0, 0.42, 0.05), emis_str=14.0)
    ink = mat_simple("Decal", (0.045, 0.045, 0.050), rough=0.45)
    concrete = mat_noisy("Concrete", (0.25, 0.25, 0.26), (0.39, 0.39, 0.40),
                         scale=4.0, rough=0.88, bump=0.05)

    bm = bmesh.new()
    add_box(bm, (24.0, 24.0, 0.12), (0.0, 0.0, -0.06))
    finish("Floor", bm, concrete)

    build_chassis(paint, dark)
    build_operator(vinyl, dark, steel)
    build_guard(paint, dark)
    build_mast(paint, steel, chrome, dark)
    build_carriage_and_forks(steel, fork_mat)
    build_wheels(rubber, rim_mat)
    build_details(dark, lens_mat, beacon_mat, ink, steel)

    add_area("Key", (3.4, -3.6, 5.2), (0.20, 0.0, 1.00), 4200.0, size=4.0,
             color=(1.0, 0.97, 0.92))
    add_area("Fill", (-4.2, -3.0, 2.6), (-0.30, 0.0, 0.90), 1200.0, size=5.0,
             color=(0.82, 0.88, 1.0))
    add_area("Rim", (-2.0, 4.2, 3.4), (-0.40, 0.20, 1.30), 1800.0, size=3.0)
    add_camera((3.80, -4.40, 2.35), (0.35, 0.0, 0.95), lens=50.0)


if __name__ == "__main__":
    main()
