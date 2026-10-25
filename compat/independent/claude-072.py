import bpy
import bmesh
import math
from mathutils import Vector, Matrix


def make_material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def add_box(name, size, location, material, rotation=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.scale = size
    obj.data.materials.append(material)
    return obj


def add_cylinder(name, radius, depth, location, material, rotation=(0.0, 0.0, 0.0), verts=24):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=verts,
                                        location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    return obj


def strut(bm, p0, p1, radius, segments=6):
    """Add a capped cylinder spanning two points into an existing bmesh."""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    length = d.length
    if length < 1e-6:
        return
    basis = d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
    matrix = Matrix.Translation((p0 + p1) * 0.5) @ basis
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius, radius2=radius, depth=length, matrix=matrix)


def build_net(name, center, top_radius, bottom_radius, drop, material,
              strands=12, rows=4, cord=0.006):
    """Cone shaped net woven from thin cords hanging under the rim."""
    cx, cy, cz = center
    levels = []
    for j in range(rows + 1):
        t = j / rows
        r = top_radius + (bottom_radius - top_radius) * t
        z = cz - drop * t
        ring = []
        for i in range(strands):
            a = 2.0 * math.pi * i / strands
            ring.append((cx + r * math.cos(a), cy + r * math.sin(a), z))
        levels.append(ring)

    bm = bmesh.new()
    for j in range(rows):
        for i in range(strands):
            nxt = (i + 1) % strands
            strut(bm, levels[j][i], levels[j + 1][nxt], cord)
            strut(bm, levels[j][nxt], levels[j + 1][i], cord)
        for i in range(strands):
            strut(bm, levels[j + 1][i], levels[j + 1][(i + 1) % strands], cord)

    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(material)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def aim_camera(location, target, lens=45.0):
    cam_data = bpy.data.cameras.new("HoopCam")
    cam_data.lens = lens
    cam = bpy.data.objects.new("HoopCam", cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = location
    direction = Vector(target) - Vector(location)
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam
    return cam


# ---------------------------------------------------------------- materials
mat_court = make_material("CourtSurface", (0.32, 0.20, 0.13), roughness=0.85)
mat_pole = make_material("PolePaint", (0.10, 0.11, 0.13), roughness=0.4, metallic=0.7)
mat_glass = make_material("BackboardGlass", (0.80, 0.86, 0.88), roughness=0.15)
mat_white = make_material("BackboardTrim", (0.92, 0.92, 0.90), roughness=0.35)
mat_rim = make_material("RimPaint", (0.85, 0.22, 0.06), roughness=0.35, metallic=0.6)
mat_net = make_material("NetCord", (0.90, 0.89, 0.85), roughness=0.75)
mat_pad = make_material("PolePad", (0.05, 0.18, 0.42), roughness=0.8)

# ---------------------------------------------------------------- ground + base
add_box("CourtGround", (14.0, 14.0, 0.08), (0.0, 3.0, -0.04), mat_court)
add_box("BaseAnchor", (1.30, 1.30, 0.18), (0.0, 1.35, 0.09), mat_pole)

# ---------------------------------------------------------------- support pole
POLE_Y = 1.35
add_cylinder("SupportPole", 0.095, 3.55, (0.0, POLE_Y, 1.775), mat_pole)
add_cylinder("PolePadding", 0.135, 1.90, (0.0, POLE_Y, 1.13), mat_pad, verts=20)

# extension arm reaching from the pole out to the backboard
add_box("ExtensionArm", (0.10, POLE_Y + 0.05, 0.12), (0.0, POLE_Y * 0.5, 3.42), mat_pole)
brace_len = math.hypot(POLE_Y - 0.12, 0.85)
brace_angle = math.atan2(POLE_Y - 0.12, 0.85)
add_box("DiagonalBrace", (0.08, 0.08, brace_len),
        (0.0, (POLE_Y + 0.12) * 0.5, 2.95), mat_pole,
        rotation=(brace_angle, 0.0, 0.0))
add_box("BoardMountPlate", (0.55, 0.09, 0.45), (0.0, 0.075, 3.20), mat_pole)

# ---------------------------------------------------------------- backboard
BOARD_Z = 3.45
add_box("Backboard", (1.83, 0.04, 1.07), (0.0, 0.0, BOARD_Z), mat_glass)
add_box("BackboardFrameTop", (1.90, 0.07, 0.05), (0.0, 0.0, BOARD_Z + 0.55), mat_white)
add_box("BackboardFrameBottom", (1.90, 0.07, 0.05), (0.0, 0.0, BOARD_Z - 0.55), mat_white)
add_box("BackboardFrameLeft", (0.05, 0.07, 1.17), (-0.925, 0.0, BOARD_Z), mat_white)
add_box("BackboardFrameRight", (0.05, 0.07, 1.17), (0.925, 0.0, BOARD_Z), mat_white)

# painted shooter's square on the front face
SQ_Z = 3.29
add_box("SquareTop", (0.62, 0.01, 0.05), (0.0, -0.026, SQ_Z + 0.225), mat_white)
add_box("SquareBottom", (0.62, 0.01, 0.05), (0.0, -0.026, SQ_Z - 0.225), mat_white)
add_box("SquareLeft", (0.05, 0.01, 0.50), (-0.285, -0.026, SQ_Z), mat_white)
add_box("SquareRight", (0.05, 0.01, 0.50), (0.285, -0.026, SQ_Z), mat_white)

# ---------------------------------------------------------------- rim and net
RIM_R = 0.2286
RIM_Z = 3.05
RIM_Y = -(0.02 + 0.155 + RIM_R)
add_box("RimBracket", (0.28, 0.20, 0.10), (0.0, -0.11, RIM_Z), mat_rim)
bpy.ops.mesh.primitive_torus_add(major_radius=RIM_R, minor_radius=0.011,
                                 major_segments=32, minor_segments=8,
                                 location=(0.0, RIM_Y, RIM_Z))
rim = bpy.context.object
rim.name = "Rim"
rim.data.materials.append(mat_rim)

build_net("Net", (0.0, RIM_Y, RIM_Z - 0.015), RIM_R * 0.97, 0.115, 0.45, mat_net)

# ---------------------------------------------------------------- lighting + camera
sun_data = bpy.data.lights.new("KeySun", type='SUN')
sun_data.energy = 4.0
sun = bpy.data.objects.new("KeySun", sun_data)
bpy.context.collection.objects.link(sun)
sun.location = (5.0, -6.0, 9.0)
sun.rotation_euler = (math.radians(52.0), 0.0, math.radians(35.0))

fill_data = bpy.data.lights.new("FillLamp", type='AREA')
fill_data.energy = 400.0
fill_data.size = 4.0
fill = bpy.data.objects.new("FillLamp", fill_data)
bpy.context.collection.objects.link(fill)
fill.location = (-4.0, -5.0, 4.0)
fill.rotation_euler = (math.radians(65.0), 0.0, math.radians(-40.0))

aim_camera((3.6, -6.4, 3.4), (0.0, -0.25, 2.95))
