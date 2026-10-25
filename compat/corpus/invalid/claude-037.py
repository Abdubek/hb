"""claude-037: A toaster with two slots and side controls.

Builds a chrome two-slice toaster headlessly from factory startup:
rounded stainless body with two top slots (real openings cut with a
boolean), dark slot liners with heating elements, a side carriage lever
in a recessed track, a browning dial with tick marks, two push buttons,
a plastic base with feet and a power cord.  Materials, three-point area
lighting and a camera are included.  Nothing is rendered or saved.
"""

import math

import bmesh
import bpy
from mathutils import Matrix, Vector

# ---------------------------------------------------------------------------
# scene / utility helpers
# ---------------------------------------------------------------------------


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 96
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.length_unit = "CENTIMETERS"


def make_world(color=(0.045, 0.048, 0.055), strength=1.0):
    world = bpy.data.worlds.new("ToasterWorld")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*color, 1.0)
    bg.inputs["Strength"].default_value = strength
    bpy.context.scene.world = world
    return world


def make_material(name, base_color, metallic=0.0, roughness=0.5,
                  emission=None, emission_strength=0.0, ior=1.45):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*base_color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if "IOR" in bsdf.inputs:
        bsdf.inputs["IOR"].default_value = ior
    if emission is not None:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat


def new_object(name, bm, material=None, smooth_angle=None):
    """Consume a bmesh into a fresh object linked to the scene."""
    mesh = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    mesh.validate()
    obj = bpy.data.objects.new(name, mesh)
    if material is not None:
        obj.data.materials.append(material)
    bpy.context.scene.collection.objects.link(obj)
    if smooth_angle is not None:
        auto_smooth(obj, smooth_angle)
    return obj


def auto_smooth(obj, angle_deg=32.0):
    """Smooth shading limited by edge angle (4.x 'Smooth by Angle')."""
    activate(obj)
    try:
        bpy.ops.object.shade_auto_smooth(angle=math.radians(angle_deg))
    except Exception:
        for poly in obj.data.polygons:
            poly.use_smooth = True


def activate(obj):
    view_layer = bpy.context.view_layer
    for other in view_layer.objects:
        other.select_set(False)
    obj.select_set(True)
    view_layer.objects.active = obj


# ---------------------------------------------------------------------------
# bmesh primitive helpers
# ---------------------------------------------------------------------------


def bm_box(bm, center, size, bevel=0.0, segments=3):
    verts = bmesh.ops.create_cube(bm, size=1.0)["verts"]
    bmesh.ops.scale(bm, vec=Vector(size), verts=verts)
    bmesh.ops.translate(bm, vec=Vector(center), verts=verts)
    if bevel > 0.0:
        edges = set()
        faces = set()
        for v in verts:
            edges.update(v.link_edges)
            faces.update(v.link_faces)
        bmesh.ops.bevel(
            bm,
            geom=list(verts) + list(edges) + list(faces),
            offset=bevel,
            offset_type="OFFSET",
            segments=segments,
            profile=0.5,
            affect="EDGES",
            clamp_overlap=True,
        )
    return verts


def bm_cylinder(bm, center, radius, depth, axis="Z", segments=32):
    rot = {
        "Z": Matrix.Identity(4),
        "X": Matrix.Rotation(math.radians(90.0), 4, "Y"),
        "Y": Matrix.Rotation(math.radians(90.0), 4, "X"),
    }[axis]
    matrix = Matrix.Translation(Vector(center)) @ rot
    return bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=segments,
        radius1=radius,
        radius2=radius,
        depth=depth,
        matrix=matrix,
    )["verts"]


def open_top_box(bm, center, size):
    """Box with its top face removed (for solidified slot liners)."""
    verts = bm_box(bm, center, size)
    faces = set()
    for v in verts:
        faces.update(v.link_faces)
    top = max(faces, key=lambda f: f.calc_center_median().z)
    bmesh.ops.delete(bm, geom=[top], context="FACES")
    return verts


def boolean_apply(target, cutter, operation="DIFFERENCE"):
    mod = target.modifiers.new("Bool", "BOOLEAN")
    mod.operation = operation
    mod.object = cutter
    mod.solver = "EXACT"
    activate(target)
    bpy.ops.object.modifier_apply(modifier=mod.name)


# ---------------------------------------------------------------------------
# dimensions (metres) -- a ~28 x 18 x 18 cm two slice toaster
# ---------------------------------------------------------------------------

BODY_X, BODY_Y = 0.280, 0.180
BODY_Z0, BODY_Z1 = 0.022, 0.200

SLOT_Y = 0.043           # offset of each slot from centre
SLOT_HALF_X = 0.100      # slot half length
SLOT_HALF_Y = 0.014      # slot half width
SLOT_FLOOR = 0.058       # inner bottom of the bread cavity

FRONT_Y = BODY_Y * 0.5   # +Y face carries the controls
LEVER_X = 0.104          # lever track centre
DIAL_X = 0.010           # browning dial centre


# ---------------------------------------------------------------------------
# materials
# ---------------------------------------------------------------------------

MAT = {
    "chrome": make_material("Chrome", (0.760, 0.775, 0.790), 1.0, 0.135),
    "steel_brushed": make_material("BrushedSteel", (0.640, 0.655, 0.670), 1.0, 0.310),
    "plastic_dark": make_material("PlasticDark", (0.032, 0.033, 0.036), 0.0, 0.395),
    "plastic_matte": make_material("PlasticMatte", (0.055, 0.056, 0.060), 0.0, 0.640),
    "cavity": make_material("SlotCavity", (0.018, 0.017, 0.016), 0.0, 0.780),
    "element": make_material(
        "HeatingElement", (0.180, 0.055, 0.030), 0.25, 0.560,
        emission=(1.000, 0.230, 0.055), emission_strength=1.6,
    ),
    "led": make_material(
        "IndicatorLED", (0.240, 0.030, 0.020), 0.0, 0.180,
        emission=(1.000, 0.120, 0.070), emission_strength=6.0,
    ),
    "marker": make_material("DialMarker", (0.880, 0.880, 0.885), 0.0, 0.330),
    "rubber": make_material("CordRubber", (0.026, 0.026, 0.028), 0.0, 0.560),
    "floor": make_material("Floor", (0.215, 0.205, 0.195), 0.0, 0.520),
}


# ---------------------------------------------------------------------------
# body shell
# ---------------------------------------------------------------------------


def build_body():
    bm = bmesh.new()
    cz = (BODY_Z0 + BODY_Z1) * 0.5
    bm_box(
        bm,
        (0.0, 0.0, cz),
        (BODY_X, BODY_Y, BODY_Z1 - BODY_Z0),
        bevel=0.016,
        segments=6,
    )
    return new_object("ToasterBody", bm, MAT["chrome"], smooth_angle=34.0)


def build_body_cutter():
    """Single cutter mesh: two bread slots, lever track, dial recess."""
    bm = bmesh.new()

    # bread slots, cut clean through the crowned top
    for sign in (-1.0, 1.0):
        z0, z1 = SLOT_FLOOR, BODY_Z1 + 0.02
        bm_box(
            bm,
            (0.0, sign * SLOT_Y, (z0 + z1) * 0.5),
            (SLOT_HALF_X * 2.0, SLOT_HALF_Y * 2.0, z1 - z0),
        )

    # recessed vertical track for the carriage lever
    bm_box(
        bm,
        (LEVER_X, FRONT_Y - 0.004, 0.118),
        (0.030, 0.024, 0.104),
    )

    # shallow circular recess seating the browning dial
    bm_cylinder(
        bm,
        (DIAL_X, FRONT_Y - 0.004, 0.104),
        0.031,
        0.014,
        axis="Y",
        segments=48,
    )

    obj = new_object("BodyCutter", bm)
    return obj


def build_slot_liners():
    """Dark inner cavity walls, one open-topped solidified shell per slot."""
    liners = []
    for index, sign in enumerate((-1.0, 1.0)):
        bm = bmesh.new()
        z0, z1 = SLOT_FLOOR - 0.002, BODY_Z1 + 0.002
        open_top_box(
            bm,
            (0.0, sign * SLOT_Y, (z0 + z1) * 0.5),
            ((SLOT_HALF_X - 0.001) * 2.0, (SLOT_HALF_Y - 0.001) * 2.0, z1 - z0),
        )
        obj = new_object("SlotLiner_%d" % index, bm, MAT["cavity"])
        mod = obj.modifiers.new("Solidify", "SOLIDIFY")
        mod.thickness = 0.0026
        mod.offset = 1.0
        liners.append(obj)
    return liners


def build_heating_elements():
    """Fine horizontal wires on both walls of both slots."""
    bm = bmesh.new()
    levels = (0.076, 0.104, 0.132, 0.160, 0.184)
    for sign in (-1.0, 1.0):
        for wall in (-1.0, 1.0):
            y = sign * SLOT_Y + wall * (SLOT_HALF_Y - 0.0035)
            for z in levels:
                bm_cylinder(
                    bm,
                    (0.0, y, z),
                    0.0013,
                    SLOT_HALF_X * 2.0 - 0.014,
                    axis="X",
                    segments=8,
                )
    # vertical mica-support posts across each slot
    for sign in (-1.0, 1.0):
        for x in (-0.070, 0.0, 0.070):
            bm_cylinder(
                bm,
                (x, sign * SLOT_Y, 0.126),
                0.0016,
                0.130,
                axis="Z",
                segments=8,
            )
    return new_object("HeatingElements", bm, MAT["element"], smooth_angle=40.0)


# ---------------------------------------------------------------------------
# side controls
# ---------------------------------------------------------------------------


def build_lever():
    """Carriage lever: shaft in the track plus a ribbed outer knob."""
    bm = bmesh.new()
    # shaft riding in the recessed track
    bm_box(bm, (LEVER_X, FRONT_Y - 0.006, 0.150), (0.016, 0.022, 0.030))
    # thumb knob outside the shell
    bm_box(
        bm,
        (LEVER_X, FRONT_Y + 0.016, 0.156),
        (0.030, 0.030, 0.020),
        bevel=0.005,
        segments=4,
    )
    # grip ribs on the top of the knob
    for i in range(3):
        bm_cylinder(
            bm,
            (LEVER_X, FRONT_Y + 0.006 + i * 0.009, 0.1665),
            0.0022,
            0.028,
            axis="X",
            segments=10,
        )
    return new_object("CarriageLever", bm, MAT["plastic_dark"], smooth_angle=36.0)


def build_dial():
    """Browning-control rotary dial with a white index marker."""
    bm = bmesh.new()
    y_face = FRONT_Y - 0.002
    bm_cylinder(bm, (DIAL_X, y_face + 0.008, 0.104), 0.028, 0.020, axis="Y", segments=56)
    # knurling around the rim
    for i in range(24):
        a = i * (2.0 * math.pi / 24.0)
        bm_cylinder(
            bm,
            (DIAL_X + math.cos(a) * 0.0281, y_face + 0.008, 0.104 + math.sin(a) * 0.0281),
            0.0016,
            0.018,
            axis="Y",
            segments=6,
        )
    dial = new_object("BrowningDial", bm, MAT["plastic_dark"], smooth_angle=30.0)

    bm = bmesh.new()
    bm_box(bm, (DIAL_X, y_face + 0.0182, 0.1215), (0.0045, 0.0025, 0.017))
    marker = new_object("DialMarker", bm, MAT["marker"])

    # engraved tick marks fanned around the dial on the shell face
    bm = bmesh.new()
    for i in range(7):
        a = math.radians(-125.0 + i * 250.0 / 6.0)
        length = 0.010 if i % 3 == 0 else 0.006
        r = 0.036 + length * 0.5
        cx = DIAL_X + math.sin(a) * r
        cz = 0.104 + math.cos(a) * r
        verts = bm_box(bm, (0.0, 0.0, 0.0), (0.0026, 0.0022, length))
        bmesh.ops.rotate(
            bm, verts=verts, cent=(0.0, 0.0, 0.0),
            matrix=Matrix.Rotation(a, 3, "Y"),
        )
        bmesh.ops.translate(bm, verts=verts, vec=(cx, y_face + 0.001, cz))
    ticks = new_object("DialTicks", bm, MAT["marker"])
    return [dial, marker, ticks]


def build_buttons():
    """Two function push buttons plus a power indicator LED."""
    parts = []
    bm = bmesh.new()
    for x in (0.048, 0.076):
        bm_cylinder(bm, (x, FRONT_Y + 0.002, 0.062), 0.011, 0.014, axis="Y", segments=32)
    parts.append(new_object("FunctionButtons", bm, MAT["plastic_matte"], smooth_angle=30.0))

    bm = bmesh.new()
    bm_cylinder(bm, (LEVER_X, FRONT_Y + 0.001, 0.062), 0.0055, 0.010, axis="Y", segments=24)
    parts.append(new_object("IndicatorLED", bm, MAT["led"], smooth_angle=30.0))
    return parts


# ---------------------------------------------------------------------------
# base, feet, crumb tray, cord
# ---------------------------------------------------------------------------


def build_base():
    bm = bmesh.new()
    bm_box(bm, (0.0, 0.0, 0.0175), (0.300, 0.196, 0.025), bevel=0.006, segments=4)
    base = new_object("BasePlinth", bm, MAT["plastic_matte"], smooth_angle=34.0)

    bm = bmesh.new()
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            bm_cylinder(
                bm,
                (sx * 0.118, sy * 0.070, 0.0035),
                0.013,
                0.008,
                axis="Z",
                segments=24,
            )
    feet = new_object("Feet", bm, MAT["rubber"], smooth_angle=30.0)

    # crumb tray front panel with a pull handle
    bm = bmesh.new()
    bm_box(bm, (0.0, FRONT_Y + 0.002, 0.0165), (0.250, 0.008, 0.014))
    bm_box(bm, (0.0, FRONT_Y + 0.010, 0.0165), (0.056, 0.010, 0.008), bevel=0.002, segments=3)
    tray = new_object("CrumbTray", bm, MAT["plastic_dark"], smooth_angle=34.0)
    return [base, feet, tray]


def build_cord():
    curve = bpy.data.curves.new("CordCurve", "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = 0.0048
    curve.bevel_resolution = 5
    curve.resolution_u = 12
    spline = curve.splines.new("BEZIER")
    points = [
        (-0.060, -0.092, 0.058),
        (-0.090, -0.170, 0.040),
        (-0.170, -0.230, 0.006),
        (-0.330, -0.180, 0.006),
    ]
    spline.bezier_points.add(len(points) - 1)
    for bp, co in zip(spline.bezier_points, points):
        bp.co = Vector(co)
        bp.handle_left_type = "AUTO"
        bp.handle_right_type = "AUTO"
    obj = bpy.data.objects.new("PowerCord", curve)
    obj.data.materials.append(MAT["rubber"])
    bpy.context.scene.collection.objects.link(obj)

    # strain relief boot where the cord leaves the shell
    bm = bmesh.new()
    bm_cylinder(bm, (-0.060, -0.086, 0.058), 0.010, 0.024, axis="Y", segments=20)
    boot = new_object("CordBoot", bm, MAT["plastic_dark"], smooth_angle=30.0)
    return [obj, boot]


def build_floor():
    bm = bmesh.new()
    bm_box(bm, (0.0, 0.0, -0.005), (4.0, 4.0, 0.01))
    return new_object("Floor", bm, MAT["floor"])


# ---------------------------------------------------------------------------
# lighting and camera
# ---------------------------------------------------------------------------


def add_area_light(name, location, target, energy, size, color=(1.0, 1.0, 1.0)):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.size = size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    obj.location = location
    direction = Vector(target) - Vector(location)
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.collection.objects.link(obj)
    return obj


def setup_lighting():
    add_area_light("KeyLight", (0.62, -0.68, 0.82), (0.02, 0.0, 0.12), 220.0, 0.90)
    add_area_light("FillLight", (-0.78, -0.44, 0.36), (0.0, 0.0, 0.10), 70.0, 1.10,
                   color=(0.86, 0.90, 1.0))
    add_area_light("RimLight", (-0.30, 0.76, 0.66), (0.0, 0.03, 0.15), 150.0, 0.55)
    # soft bounce card to give the chrome something to reflect
    add_area_light("BounceCard", (0.10, -0.20, 1.10), (0.0, 0.0, 0.15), 45.0, 1.60)


def setup_camera():
    data = bpy.data.cameras.new("Camera")
    data.lens = 62.0
    data.sensor_width = 36.0
    obj = bpy.data.objects.new("Camera", data)
    location = Vector((0.60, -0.58, 0.34))
    target = Vector((0.0, 0.005, 0.112))
    obj.location = location
    obj.rotation_euler = (target - location).to_track_quat("-Z", "Y").to_euler()
    data.dof.use_dof = True
    data.dof.focus_distance = (target - location).length
    data.dof.aperture_fstop = 5.0
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.scene.camera = obj
    return obj


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main():
    reset_scene()
    make_world()

    body = build_body()
    cutter = build_body_cutter()
    boolean_apply(body, cutter)
    bpy.data.objects.remove(cutter, do_unlink=True)
    auto_smooth(body, 34.0)

    parts = [body]
    parts += build_slot_liners()
    parts.append(build_heating_elements())
    parts.append(build_lever())
    parts += build_dial()
    parts += build_buttons()
    parts += build_base()
    parts += build_cord()

    build_floor()
    setup_lighting()
    setup_camera()

    for obj in parts:
        obj.select_set(False)
    activate(body)
    print("Toaster scene built: %d objects" % len(bpy.context.scene.objects))


if __name__ == "__main__":
    main()
