"""claude-125 - A docked spacecraft assembled from a capsule, fuel tanks,
thruster pods and landing legs, mated to an orbital station node.

Blender 4.5 LTS.  Scene construction only: nothing is rendered or written out.
"""

import math

import bpy
import bmesh
from mathutils import Vector, Matrix

TAU = math.tau


# ---------------------------------------------------------------------------
# scene bootstrap
# ---------------------------------------------------------------------------

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 96
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.film_transparent = False
    return scene


def make_world():
    world = bpy.data.worlds.new("Orbit")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.008, 0.011, 0.022, 1.0)
    bg.inputs["Strength"].default_value = 1.0
    bpy.context.scene.world = world
    return world


# ---------------------------------------------------------------------------
# materials
# ---------------------------------------------------------------------------

def make_material(name, base, metallic=0.0, roughness=0.5,
                  emission=None, emission_strength=0.0, anisotropic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (base[0], base[1], base[2], 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if "Anisotropic" in bsdf.inputs:
        bsdf.inputs["Anisotropic"].default_value = anisotropic
    if emission is not None:
        bsdf.inputs["Emission Color"].default_value = (
            emission[0], emission[1], emission[2], 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat


def build_materials():
    return {
        "hull": make_material("Hull_White", (0.78, 0.79, 0.80),
                              metallic=0.25, roughness=0.42),
        "hull_grey": make_material("Hull_Grey", (0.30, 0.32, 0.35),
                                   metallic=0.65, roughness=0.38),
        "steel": make_material("Steel", (0.55, 0.57, 0.60),
                               metallic=1.0, roughness=0.28, anisotropic=0.3),
        "dark": make_material("Dark_Metal", (0.055, 0.058, 0.065),
                              metallic=0.85, roughness=0.35),
        "gold": make_material("Gold_Foil", (0.92, 0.66, 0.20),
                              metallic=1.0, roughness=0.24),
        "copper": make_material("Nozzle_Copper", (0.62, 0.32, 0.16),
                                metallic=1.0, roughness=0.30),
        "glass": make_material("Window_Glass", (0.02, 0.035, 0.05),
                               metallic=0.4, roughness=0.06,
                               emission=(0.10, 0.18, 0.28), emission_strength=0.6),
        "glow": make_material("Thruster_Glow", (0.05, 0.05, 0.05),
                              metallic=0.0, roughness=0.5,
                              emission=(1.0, 0.55, 0.22), emission_strength=6.0),
        "panel": make_material("Solar_Cell", (0.020, 0.035, 0.11),
                               metallic=0.75, roughness=0.16),
        "marker": make_material("Marker_Red", (0.62, 0.06, 0.05),
                                metallic=0.2, roughness=0.45),
    }


# ---------------------------------------------------------------------------
# geometry helpers - everything accumulates into one bmesh per material key
# ---------------------------------------------------------------------------

PARTS = {}


def bm(key):
    if key not in PARTS:
        PARTS[key] = bmesh.new()
    return PARTS[key]


def xform(loc=(0.0, 0.0, 0.0), quat=None, scale=(1.0, 1.0, 1.0)):
    m = Matrix.Translation(Vector(loc))
    if quat is not None:
        m = m @ quat.to_matrix().to_4x4()
    return m @ Matrix.Diagonal(Vector(scale)).to_4x4()


def add_cyl(key, radius1, radius2, depth, loc=(0, 0, 0), quat=None,
            segments=32, caps=True, scale=(1.0, 1.0, 1.0)):
    bmesh.ops.create_cone(
        bm(key),
        cap_ends=caps, cap_tris=False, segments=segments,
        radius1=radius1, radius2=radius2, depth=depth,
        matrix=xform(loc, quat, scale), calc_uvs=True)


def add_tube(key, p1, p2, r1, r2=None, segments=16, caps=True):
    """Cylinder/cone spanning two world-space points."""
    a, b = Vector(p1), Vector(p2)
    d = b - a
    length = d.length
    if length < 1e-6:
        return
    quat = Vector((0.0, 0.0, 1.0)).rotation_difference(d)
    add_cyl(key, r1, r1 if r2 is None else r2, length,
            loc=(a + b) * 0.5, quat=quat, segments=segments, caps=caps)


def add_sphere(key, center, radius, u=28, v=16, scale=(1.0, 1.0, 1.0)):
    bmesh.ops.create_uvsphere(
        bm(key), u_segments=u, v_segments=v, radius=radius,
        matrix=xform(center, None, scale), calc_uvs=True)


def add_box(key, size, loc=(0, 0, 0), quat=None):
    bmesh.ops.create_cube(
        bm(key), size=1.0,
        matrix=xform(loc, quat, size), calc_uvs=True)


def polar(radius, angle_deg, z):
    a = math.radians(angle_deg)
    return (radius * math.cos(a), radius * math.sin(a), z)


def z_quat(angle_deg):
    return Matrix.Rotation(math.radians(angle_deg), 4, 'Z').to_quaternion()


def finalize(materials, smooth_angle=40.0):
    objects = []
    for key, mesh_data in PARTS.items():
        me = bpy.data.meshes.new(key)
        mesh_data.to_mesh(me)
        mesh_data.free()
        me.update()
        for poly in me.polygons:
            poly.use_smooth = True
        ob = bpy.data.objects.new(key, me)
        ob.data.materials.append(materials[key])
        mod = ob.modifiers.new("Sharpen", 'EDGE_SPLIT')
        mod.use_edge_angle = True
        mod.split_angle = math.radians(smooth_angle)
        mod.use_edge_sharp = True
        bpy.context.collection.objects.link(ob)
        objects.append(ob)
    PARTS.clear()
    return objects


# ---------------------------------------------------------------------------
# spacecraft dimensions
# ---------------------------------------------------------------------------

SM_R = 1.30           # service / propulsion module radius
SM_Z0, SM_Z1 = 0.0, 2.40
CAP_Z0, CAP_Z1 = 2.40, 4.30
CAP_R0, CAP_R1 = 1.36, 0.62
PORT_Z = 4.96         # top of the docking collar

LEG_ANGLES = (45.0, 135.0, 225.0, 315.0)
TANK_ANGLES = (0.0, 90.0, 180.0, 270.0)
POD_ANGLES = (45.0, 135.0, 225.0, 315.0)


# ---------------------------------------------------------------------------
# spacecraft body
# ---------------------------------------------------------------------------

def build_propulsion_module():
    # main hull barrel
    add_cyl("hull", SM_R, SM_R, SM_Z1 - SM_Z0,
            loc=(0, 0, (SM_Z0 + SM_Z1) * 0.5), segments=40)

    # foil-wrapped mid section
    add_cyl("gold", SM_R * 1.012, SM_R * 1.012, 0.62,
            loc=(0, 0, 1.12), segments=40, caps=False)

    # stiffening bands
    for z in (0.22, 0.72, 1.62, 2.10):
        add_cyl("hull_grey", SM_R * 1.03, SM_R * 1.03, 0.075,
                loc=(0, 0, z), segments=40)

    # longitudinal stringers
    for i in range(12):
        ang = i * 30.0 + 15.0
        add_box("hull_grey", (0.075, 0.05, 1.95),
                loc=polar(SM_R * 1.01, ang, 1.20), quat=z_quat(ang))

    # thrust plate + engine bell
    add_cyl("hull_grey", SM_R * 1.02, SM_R * 0.98, 0.14,
            loc=(0, 0, -0.07), segments=40)
    add_cyl("steel", 0.30, 0.36, 0.28, loc=(0, 0, -0.26), segments=28)
    add_cyl("copper", 0.36, 0.88, 0.92, loc=(0, 0, -0.86),
            segments=36, caps=False)
    add_cyl("copper", 0.90, 0.90, 0.06, loc=(0, 0, -1.32), segments=36)
    add_cyl("glow", 0.30, 0.30, 0.03, loc=(0, 0, -0.40), segments=24)

    # engine gimbal actuators
    for ang in (30.0, 150.0, 270.0):
        add_tube("steel", polar(0.82, ang, -0.10), polar(0.42, ang, -0.52),
                 0.055, segments=12)

    # plumbing manifold ring under the tanks
    for ang in TANK_ANGLES:
        add_tube("steel", polar(1.62, ang, 0.34), polar(0.55, ang, -0.02),
                 0.055, segments=12)


def build_capsule():
    # conical crew capsule
    add_cyl("hull", CAP_R0, CAP_R1, CAP_Z1 - CAP_Z0,
            loc=(0, 0, (CAP_Z0 + CAP_Z1) * 0.5), segments=40)

    # base flange where the capsule meets the propulsion module
    add_cyl("hull_grey", CAP_R0 * 1.04, CAP_R0 * 1.04, 0.12,
            loc=(0, 0, CAP_Z0 + 0.05), segments=40)

    # ablative / foil skirt
    add_cyl("gold", 1.20, 0.98, 0.46, loc=(0, 0, 2.86),
            segments=40, caps=False)

    # windows
    for ang in (0.0, 72.0, 288.0):
        r_at = 1.08
        pos = polar(r_at, ang, 3.42)
        q = z_quat(ang) @ Matrix.Rotation(math.radians(76.0), 4, 'Y').to_quaternion()
        add_cyl("hull_grey", 0.26, 0.26, 0.06, loc=pos, quat=q, segments=20)
        add_cyl("glass", 0.20, 0.20, 0.05,
                loc=(pos[0] * 1.03, pos[1] * 1.03, pos[2]), quat=q, segments=20)

    # crew hatch
    hatch_ang = 180.0
    hpos = polar(1.06, hatch_ang, 3.36)
    hq = z_quat(hatch_ang) @ Matrix.Rotation(math.radians(76.0), 4, 'Y').to_quaternion()
    add_cyl("hull_grey", 0.42, 0.42, 0.07, loc=hpos, quat=hq, segments=28)
    add_cyl("steel", 0.09, 0.09, 0.10,
            loc=(hpos[0] * 1.06, hpos[1] * 1.06, hpos[2]), quat=hq, segments=14)

    # hull markings
    add_cyl("marker", 1.30, 1.30, 0.05, loc=(0, 0, 2.62), segments=40)

    # handrails up the flank
    for ang in (36.0, 144.0, 216.0, 324.0):
        for z in (2.95, 3.45, 3.95):
            r_at = CAP_R0 + (CAP_R1 - CAP_R0) * (z - CAP_Z0) / (CAP_Z1 - CAP_Z0)
            a = polar(r_at * 0.99, ang - 5.0, z)
            b = polar(r_at * 0.99, ang + 5.0, z)
            mid_out = 0.10
            am = polar(r_at + mid_out, ang - 5.0, z)
            bm_ = polar(r_at + mid_out, ang + 5.0, z)
            add_tube("steel", a, am, 0.022, segments=8)
            add_tube("steel", am, bm_, 0.022, segments=8)
            add_tube("steel", bm_, b, 0.022, segments=8)

    # forward RCS quads
    for ang in (18.0, 108.0, 198.0, 288.0):
        base = polar(0.68, ang, 4.06)
        add_box("hull_grey", (0.26, 0.22, 0.18), loc=base, quat=z_quat(ang))
        for (dx, dz) in ((0.14, 0.05), (0.14, -0.05)):
            p = polar(0.68 + dx, ang, 4.06 + dz)
            add_cyl("dark", 0.035, 0.055, 0.10, loc=p,
                    quat=z_quat(ang) @ Matrix.Rotation(math.radians(90.0), 4, 'Y').to_quaternion(),
                    segments=12)


def build_docking_interface():
    # androgynous docking adapter on the capsule nose
    add_cyl("hull_grey", 0.54, 0.54, 0.42, loc=(0, 0, 4.51), segments=32)
    add_cyl("steel", 0.66, 0.66, 0.22, loc=(0, 0, 4.85), segments=32)
    add_cyl("dark", 0.46, 0.46, 0.24, loc=(0, 0, 4.86), segments=28)

    # capture latches around the ring
    for i in range(8):
        ang = i * 45.0
        add_box("steel", (0.10, 0.07, 0.16), loc=polar(0.64, ang, PORT_Z + 0.02),
                quat=z_quat(ang))

    # alignment targets and umbilicals
    for ang in (0.0, 120.0, 240.0):
        add_tube("gold", polar(0.50, ang, 4.36), polar(0.62, ang, 4.86),
                 0.045, segments=10)


# ---------------------------------------------------------------------------
# strap-on propellant tanks
# ---------------------------------------------------------------------------

def build_fuel_tanks():
    tank_r = 0.44
    ring_r = 1.80
    z0, z1 = 0.42, 2.02

    for i, ang in enumerate(TANK_ANGLES):
        cx, cy, _ = polar(ring_r, ang, 0.0)
        skin = "hull" if i % 2 == 0 else "gold"

        # barrel + domed ends
        add_cyl(skin, tank_r, tank_r, z1 - z0,
                loc=(cx, cy, (z0 + z1) * 0.5), segments=32)
        add_sphere(skin, (cx, cy, z1), tank_r, u=28, v=14, scale=(1, 1, 0.82))
        add_sphere(skin, (cx, cy, z0), tank_r, u=28, v=14, scale=(1, 1, 0.82))

        # retention straps
        for z in (z0 + 0.30, z1 - 0.30):
            add_cyl("steel", tank_r * 1.05, tank_r * 1.05, 0.07,
                    loc=(cx, cy, z), segments=32)

        # mounting struts back to the hull
        for z in (z0 + 0.30, z1 - 0.30):
            inner = polar(SM_R * 0.99, ang, z)
            outer = polar(ring_r - tank_r * 0.9, ang, z)
            add_tube("steel", inner, outer, 0.06, segments=12)
            for off in (-16.0, 16.0):
                add_tube("steel", polar(SM_R * 0.99, ang + off, z),
                         outer, 0.04, segments=10)

        # top pressurisation fitting
        add_cyl("steel", 0.09, 0.09, 0.18, loc=(cx, cy, z1 + 0.36), segments=14)
        add_tube("steel", (cx, cy, z1 + 0.44), polar(SM_R * 0.98, ang, 2.28),
                 0.045, segments=10)


# ---------------------------------------------------------------------------
# thruster pods
# ---------------------------------------------------------------------------

def build_thruster_pods():
    pod_z = 2.16
    pod_r = 1.52

    for ang in POD_ANGLES:
        q = z_quat(ang)
        base = polar(pod_r, ang, pod_z)

        # pylon and pod body
        add_tube("steel", polar(SM_R * 0.98, ang, pod_z),
                 polar(pod_r - 0.20, ang, pod_z), 0.085, segments=14)
        add_box("hull_grey", (0.46, 0.52, 0.46), loc=base, quat=q)
        add_box("gold", (0.40, 0.44, 0.12), loc=(base[0], base[1], base[2] + 0.24),
                quat=q)

        radial = Vector((math.cos(math.radians(ang)), math.sin(math.radians(ang)), 0.0))
        tangent = Vector((-radial.y, radial.x, 0.0))
        origin = Vector(base)

        # four canted nozzles: outward pair, up and down
        directions = [
            (radial, origin + radial * 0.24 + tangent * 0.14),
            (radial, origin + radial * 0.24 - tangent * 0.14),
            (Vector((0, 0, 1)), origin + Vector((0, 0, 0.24)) + radial * 0.08),
            (Vector((0, 0, -1)), origin + Vector((0, 0, -0.24)) + radial * 0.08),
        ]
        for d, p in directions:
            nq = Vector((0.0, 0.0, 1.0)).rotation_difference(d)
            throat = p + d * 0.04
            bell = p + d * 0.20
            add_cyl("dark", 0.055, 0.115, 0.20, loc=(p + d * 0.10),
                    quat=nq, segments=16, caps=False)
            add_cyl("glow", 0.045, 0.045, 0.02, loc=throat, quat=nq, segments=12)
            add_cyl("steel", 0.115, 0.115, 0.02, loc=bell, quat=nq, segments=16)


# ---------------------------------------------------------------------------
# landing legs
# ---------------------------------------------------------------------------

def build_landing_legs():
    hip_r, hip_z = SM_R * 0.98, 1.34
    foot_r, foot_z = 3.05, -1.58
    brace_z = 0.22

    for ang in LEG_ANGLES:
        hip = Vector(polar(hip_r, ang, hip_z))
        foot = Vector(polar(foot_r, ang, foot_z))
        knee = hip.lerp(foot, 0.55)

        # primary strut with a shock-absorber section
        add_tube("steel", hip, knee, 0.135, 0.115, segments=18)
        add_tube("hull_grey", hip.lerp(foot, 0.18), hip.lerp(foot, 0.50),
                 0.165, segments=18)
        add_tube("steel", knee, foot, 0.095, 0.085, segments=16)

        # hip fitting
        add_box("hull_grey", (0.30, 0.34, 0.30), loc=hip, quat=z_quat(ang))

        # A-frame secondary braces
        for off in (-19.0, 19.0):
            root = Vector(polar(hip_r, ang + off, brace_z))
            add_tube("steel", root, hip.lerp(foot, 0.72), 0.062, segments=12)
            add_box("hull_grey", (0.20, 0.18, 0.20), loc=root, quat=z_quat(ang + off))

        # footpad
        pad = (foot.x, foot.y, foot.z - 0.06)
        add_cyl("hull_grey", 0.50, 0.44, 0.15, loc=pad, segments=28)
        add_cyl("gold", 0.52, 0.52, 0.04, loc=(pad[0], pad[1], pad[2] + 0.08),
                segments=28)
        add_sphere("steel", (foot.x, foot.y, foot.z + 0.05), 0.13, u=18, v=10)

        # contact probe
        add_tube("dark", (pad[0], pad[1], pad[2] - 0.07),
                 (pad[0], pad[1], pad[2] - 0.55), 0.022, segments=8)


# ---------------------------------------------------------------------------
# station node the spacecraft is docked to
# ---------------------------------------------------------------------------

ST_R = 1.62
ST_Z = 6.60
ST_LEN = 9.40


def build_station():
    y_quat = Matrix.Rotation(math.radians(90.0), 4, 'X').to_quaternion()

    # pressurised module along Y with domed end caps
    add_cyl("hull", ST_R, ST_R, ST_LEN, loc=(0, 0, ST_Z), quat=y_quat, segments=44)
    for sy in (-1.0, 1.0):
        add_sphere("hull", (0, sy * ST_LEN * 0.5, ST_Z), ST_R,
                   u=36, v=20, scale=(1.0, 0.55, 1.0))
        add_cyl("hull_grey", ST_R * 0.62, ST_R * 0.52, 0.30,
                loc=(0, sy * (ST_LEN * 0.5 + 0.80), ST_Z), quat=y_quat, segments=28)

    # rib rings and micrometeoroid blanket bands
    for i in range(-4, 5):
        y = i * 1.05
        add_cyl("hull_grey", ST_R * 1.03, ST_R * 1.03, 0.10,
                loc=(0, y, ST_Z), quat=y_quat, segments=44)
    add_cyl("gold", ST_R * 1.015, ST_R * 1.015, 1.70,
            loc=(0, 2.60, ST_Z), quat=y_quat, segments=44, caps=False)
    add_cyl("gold", ST_R * 1.015, ST_R * 1.015, 1.70,
            loc=(0, -2.60, ST_Z), quat=y_quat, segments=44, caps=False)

    # handrails along the top
    for i in range(-4, 5):
        y = i * 1.05 + 0.52
        a = (0.34, y, ST_Z + ST_R * 0.96)
        b = (0.34, y + 0.72, ST_Z + ST_R * 0.96)
        au = (0.34, y, ST_Z + ST_R + 0.14)
        bu = (0.34, y + 0.72, ST_Z + ST_R + 0.14)
        add_tube("steel", a, au, 0.024, segments=8)
        add_tube("steel", au, bu, 0.024, segments=8)
        add_tube("steel", bu, b, 0.024, segments=8)

    # nadir docking node the capsule is berthed to
    node_top = ST_Z - ST_R * 0.85
    add_cyl("hull_grey", 0.86, 0.78, node_top - 5.06,
            loc=(0, 0, (node_top + 5.06) * 0.5), segments=32)
    add_cyl("steel", 0.80, 0.80, 0.24, loc=(0, 0, 5.12), segments=32)
    add_cyl("dark", 0.50, 0.50, 0.30, loc=(0, 0, 5.06), segments=28)
    for i in range(8):
        ang = i * 45.0 + 22.5
        add_box("steel", (0.10, 0.07, 0.18), loc=polar(0.78, ang, 5.06),
                quat=z_quat(ang))
    # docking floodlights and cameras
    for ang in (60.0, 240.0):
        add_cyl("hull_grey", 0.10, 0.10, 0.16, loc=polar(1.00, ang, 5.62),
                segments=14)
        add_cyl("glow", 0.085, 0.085, 0.03, loc=polar(1.00, ang, 5.53),
                segments=14)

    # radiators on the zenith side
    for sy in (-1.0, 1.0):
        add_box("hull_grey", (2.60, 0.06, 1.30),
                loc=(0.0, sy * 2.40, ST_Z + ST_R + 0.85))
        add_tube("steel", (0.0, sy * 2.40, ST_Z + ST_R * 0.9),
                 (0.0, sy * 2.40, ST_Z + ST_R + 0.25), 0.07, segments=12)

    build_solar_wings()


def build_solar_wings():
    for sx in (-1.0, 1.0):
        # mast out of the module flank
        add_tube("steel", (sx * ST_R * 0.9, 0.0, ST_Z),
                 (sx * 2.35, 0.0, ST_Z), 0.13, segments=16)
        add_box("hull_grey", (0.42, 0.60, 0.42), loc=(sx * 2.35, 0.0, ST_Z))

        for sy in (-1.0, 1.0):
            cx = sx * (2.35 + 0.30 + 2.60)
            cy = sy * 1.45
            # blanket
            add_box("panel", (5.20, 2.60, 0.05), loc=(cx, cy, ST_Z))
            # frame
            add_box("steel", (5.34, 0.09, 0.10), loc=(cx, cy + sy * 1.30, ST_Z))
            add_box("steel", (5.34, 0.09, 0.10), loc=(cx, cy - sy * 1.30, ST_Z))
            add_box("steel", (0.09, 2.70, 0.10), loc=(cx - sx * 2.60, cy, ST_Z))
            add_box("steel", (0.09, 2.70, 0.10), loc=(cx + sx * 2.60, cy, ST_Z))
            # cell dividers
            for i in range(-3, 4):
                add_box("steel", (0.05, 2.56, 0.07),
                        loc=(cx + i * 0.65, cy, ST_Z + 0.03))
            # yoke
            add_tube("steel", (sx * 2.55, sy * 0.20, ST_Z),
                     (cx - sx * 2.60, cy, ST_Z), 0.075, segments=12)


# ---------------------------------------------------------------------------
# lighting and camera
# ---------------------------------------------------------------------------

def add_area_light(name, location, target, energy, size, color):
    data = bpy.data.lights.new(name, type='AREA')
    data.energy = energy
    data.size = size
    data.color = color
    ob = bpy.data.objects.new(name, data)
    ob.location = location
    direction = Vector(target) - Vector(location)
    ob.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(ob)
    return ob


def build_lighting():
    add_area_light("Key", (9.5, -10.0, 10.5), (0.0, 0.0, 3.6),
                   energy=6000.0, size=9.0, color=(1.0, 0.95, 0.88))
    add_area_light("Fill", (-11.0, -5.0, 1.5), (0.0, 0.0, 3.0),
                   energy=900.0, size=12.0, color=(0.45, 0.60, 1.0))

    sun = bpy.data.lights.new("Rim", type='SUN')
    sun.energy = 4.0
    sun.angle = math.radians(1.0)
    sun.color = (0.85, 0.90, 1.0)
    sun_ob = bpy.data.objects.new("Rim", sun)
    sun_ob.location = (-6.0, 12.0, 8.0)
    sun_ob.rotation_euler = (Vector((0.0, 0.0, 3.5)) - Vector(sun_ob.location)
                             ).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(sun_ob)


def build_camera(scene):
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = 52.0
    cam_data.clip_end = 500.0
    cam_data.dof.use_dof = True

    cam = bpy.data.objects.new("Camera", cam_data)
    cam.location = (12.5, -14.5, 8.2)
    target = Vector((0.0, 0.0, 3.6))
    cam.rotation_euler = (target - Vector(cam.location)).to_track_quat('-Z', 'Y').to_euler()
    cam_data.dof.focus_distance = (target - Vector(cam.location)).length
    cam_data.dof.aperture_fstop = 5.0
    bpy.context.collection.objects.link(cam)
    scene.camera = cam
    return cam


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    scene = reset_scene()
    make_world()
    materials = build_materials()

    build_propulsion_module()
    build_capsule()
    build_docking_interface()
    build_fuel_tanks()
    build_thruster_pods()
    build_landing_legs()
    build_station()

    objects = finalize(materials)

    # group everything under a single empty for easy transforms
    root = bpy.data.objects.new("DockedStack", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 2.0
    bpy.context.collection.objects.link(root)
    for ob in objects:
        ob.parent = root

    build_lighting()
    build_camera(scene)

    print("claude-125: built %d meshes" % len(objects))


if __name__ == "__main__":
    main()
