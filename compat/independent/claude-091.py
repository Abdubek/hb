import bpy
import bmesh
import math
from mathutils import Vector


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in list(coll):
            if item.users == 0:
                coll.remove(item)


def make_material(name, color, roughness=0.6, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def box_mesh(name, dims, bevel=0.0):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(dims), verts=bm.verts)
    if bevel > 0.0:
        bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                        offset=bevel, segments=2, affect='EDGES')
    bm.to_mesh(mesh)
    bm.free()
    return mesh


def add_instance(name, mesh, loc, mat, rot=(0.0, 0.0, 0.0), parent=None):
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    obj.rotation_euler = rot
    obj.parent = parent
    if mat.name not in [m.name for m in mesh.materials if m]:
        mesh.materials.append(mat)
    bpy.context.collection.objects.link(obj)
    return obj


def aim_camera(location, target, lens=40.0):
    cam_data = bpy.data.cameras.new("AuditoriumCam")
    cam_data.lens = lens
    cam = bpy.data.objects.new("AuditoriumCam", cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = location
    cam.rotation_euler = (Vector(target) - Vector(location)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam
    return cam


clear_scene()

upholstery = make_material("Seat_Upholstery", (0.35, 0.03, 0.05), roughness=0.75)
shell = make_material("Seat_Shell", (0.09, 0.08, 0.09), roughness=0.5)
chrome = make_material("Seat_Frame", (0.62, 0.63, 0.66), roughness=0.3, metallic=0.95)
step_mat = make_material("Platform_Concrete", (0.28, 0.27, 0.26), roughness=0.9)
carpet = make_material("Aisle_Carpet", (0.16, 0.05, 0.07), roughness=0.95)
screen_mat = make_material("Screen_Surface", (0.86, 0.87, 0.88), roughness=0.55)
wall_mat = make_material("Auditorium_Wall", (0.13, 0.12, 0.14), roughness=0.85)

SEAT_PITCH = 0.62
SEATS_PER_ROW = 5
ROWS = 3
ROW_DEPTH = 1.15
RISE = 0.34

row_width = SEATS_PER_ROW * SEAT_PITCH + 0.30

# Shared meshes so every seat reuses the same modest geometry.
mesh_cushion = box_mesh("SeatCushion_Mesh", (0.52, 0.52, 0.13), bevel=0.045)
mesh_back = box_mesh("SeatBack_Mesh", (0.52, 0.14, 0.66), bevel=0.045)
mesh_headrest = box_mesh("SeatHeadrest_Mesh", (0.44, 0.16, 0.16), bevel=0.05)
mesh_armrest = box_mesh("SeatArmrest_Mesh", (0.09, 0.50, 0.07), bevel=0.025)
mesh_arm_post = box_mesh("SeatArmPost_Mesh", (0.07, 0.09, 0.34))
mesh_pedestal = box_mesh("SeatPedestal_Mesh", (0.13, 0.22, 0.42))
mesh_foot = box_mesh("SeatFoot_Mesh", (0.34, 0.30, 0.05))


def build_seat(name, base_loc, parent):
    """One tip-up cinema seat: pedestal, cushion, reclined back and shared armrests."""
    x, y, z = base_loc
    add_instance(name + "_Foot", mesh_foot, (x, y, z + 0.025), chrome, parent=parent)
    add_instance(name + "_Pedestal", mesh_pedestal, (x, y, z + 0.26), shell, parent=parent)
    add_instance(name + "_Cushion", mesh_cushion, (x, y + 0.02, z + 0.46), upholstery, parent=parent)
    add_instance(name + "_Back", mesh_back, (x, y - 0.24, z + 0.83), upholstery,
                 rot=(math.radians(13.0), 0.0, 0.0), parent=parent)
    add_instance(name + "_Headrest", mesh_headrest, (x, y - 0.36, z + 1.16), upholstery,
                 rot=(math.radians(13.0), 0.0, 0.0), parent=parent)
    for side, tag in ((1.0, "L"), (-1.0, "R")):
        ax = x + side * (SEAT_PITCH * 0.5)
        add_instance("%s_ArmPost_%s" % (name, tag), mesh_arm_post, (ax, y - 0.12, z + 0.52),
                     shell, parent=parent)
        add_instance("%s_Armrest_%s" % (name, tag), mesh_armrest, (ax, y + 0.02, z + 0.72),
                     shell, parent=parent)


auditorium = bpy.data.objects.new("Auditorium", None)
bpy.context.collection.objects.link(auditorium)

platform = bpy.data.objects.new("SteppedPlatform", None)
platform.parent = auditorium
bpy.context.collection.objects.link(platform)

seating = bpy.data.objects.new("SeatRows", None)
seating.parent = auditorium
bpy.context.collection.objects.link(seating)

for row in range(ROWS):
    top = (row + 1) * RISE
    y_center = -0.2 - ROW_DEPTH * (row + 0.5)
    tread = box_mesh("StepTread_%02d_Mesh" % row, (row_width, ROW_DEPTH, top))
    add_instance("StepTread_%02d" % row, tread, (0.0, y_center, top * 0.5), step_mat,
                 parent=platform)
    nose = box_mesh("StepNose_%02d_Mesh" % row, (row_width, 0.06, 0.05))
    add_instance("StepNose_%02d" % row, nose, (0.0, y_center + ROW_DEPTH * 0.5, top - 0.02),
                 chrome, parent=platform)

    for i in range(SEATS_PER_ROW):
        x = (i - (SEATS_PER_ROW - 1) * 0.5) * SEAT_PITCH
        build_seat("Seat_R%d_S%d" % (row, i), (x, y_center - 0.06, top), seating)

floor = box_mesh("Floor_Mesh", (16.0, 16.0, 0.1))
add_instance("Floor", floor, (0.0, -2.0, -0.05), carpet, parent=auditorium)

screen_frame = box_mesh("ScreenFrame_Mesh", (6.4, 0.2, 3.3))
add_instance("ScreenFrame", screen_frame, (0.0, 4.3, 1.9), wall_mat, parent=auditorium)
screen = box_mesh("ScreenSurface_Mesh", (5.9, 0.06, 2.9))
add_instance("ScreenSurface", screen, (0.0, 4.18, 1.9), screen_mat, parent=auditorium)

for side, tag in ((1.0, "L"), (-1.0, "R")):
    wall = box_mesh("SideWall_%s_Mesh" % tag, (0.2, 11.0, 4.2))
    add_instance("SideWall_%s" % tag, wall, (side * (row_width * 0.5 + 1.1), -0.6, 2.1),
                 wall_mat, parent=auditorium)

bpy.ops.object.light_add(type='AREA', location=(0.0, 3.4, 4.0))
key = bpy.context.active_object
key.name = "ScreenBounceLight"
key.data.energy = 600.0
key.data.size = 6.0
key.rotation_euler = (math.radians(40.0), 0.0, 0.0)

bpy.ops.object.light_add(type='AREA', location=(-3.5, -4.0, 3.6))
fill = bpy.context.active_object
fill.name = "AisleFillLight"
fill.data.energy = 200.0
fill.data.size = 3.0
fill.rotation_euler = (math.radians(55.0), 0.0, math.radians(-40.0))

aim_camera((4.6, -5.6, 3.2), (0.0, -2.0, 0.9))
