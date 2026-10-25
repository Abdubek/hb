import bpy
import bmesh
import math
from mathutils import Vector, Euler

# --- Lecture podium ------------------------------------------------------
# Slanted reading surface, tapered body, gooseneck microphone.

SLANT = math.radians(-14.0)          # reading surface tilt toward speaker (-Y front)
DESK = Vector((0.0, 0.0, 1.10))      # centre of the reading surface


def reset_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    mat.diffuse_color = (*color, 1.0)
    return mat


def finish(name, bm, mat, location=(0, 0, 0), rotation=(0, 0, 0), smooth=False):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        for poly in me.polygons:
            poly.use_smooth = True
    obj = bpy.data.objects.new(name, me)
    obj.location = location
    obj.rotation_euler = rotation
    obj.data.materials.append(mat)
    bpy.context.collection.objects.link(obj)
    return obj


def box(name, size, location, mat, rotation=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    return finish(name, bm, mat, location, rotation)


def cylinder(name, radius, depth, location, mat, rotation=(0, 0, 0), segments=24):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius, radius2=radius, depth=depth)
    return finish(name, bm, mat, location, rotation, smooth=False)


def sphere(name, radius, location, mat, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=radius, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.name = name
    obj.scale = scale
    obj.data.materials.append(mat)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    return obj


def tapered_body(name, mat):
    """Podium cabinet: wider at the floor, narrower at the desk."""
    bx, by, tx, ty = 0.36, 0.26, 0.31, 0.22
    z0, z1 = 0.06, 1.05
    bm = bmesh.new()
    low = [bm.verts.new(v) for v in ((-bx, -by, z0), (bx, -by, z0), (bx, by, z0), (-bx, by, z0))]
    high = [bm.verts.new(v) for v in ((-tx, -ty, z1), (tx, -ty, z1), (tx, ty, z1), (-tx, ty, z1))]
    bm.faces.new(low)
    bm.faces.new(high)
    for i in range(4):
        bm.faces.new((low[i], low[(i + 1) % 4], high[(i + 1) % 4], high[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return finish(name, bm, mat)


def on_desk(local):
    """Local coordinate on the tilted reading surface -> world coordinate."""
    return DESK + Euler((SLANT, 0.0, 0.0)).to_matrix() @ Vector(local)


def gooseneck(name, mat, location):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = 0.006
    curve.bevel_resolution = 3
    curve.resolution_u = 10
    spline = curve.splines.new('BEZIER')
    spline.bezier_points.add(2)
    for bp, co in zip(spline.bezier_points,
                      ((0.0, 0.0, 0.0), (0.0, -0.04, 0.20), (-0.03, -0.21, 0.27))):
        bp.co = co
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
    obj = bpy.data.objects.new(name, curve)
    obj.location = location
    obj.rotation_euler = (SLANT, 0.0, 0.0)
    obj.data.materials.append(mat)
    bpy.context.collection.objects.link(obj)
    return obj


def add_light(name, kind, energy, location, rotation=(0, 0, 0), size=2.0):
    data = bpy.data.lights.new(name, kind)
    data.energy = energy
    if kind == 'AREA':
        data.size = size
    obj = bpy.data.objects.new(name, data)
    obj.location = location
    obj.rotation_euler = rotation
    bpy.context.collection.objects.link(obj)
    return obj


def add_camera(location, target):
    data = bpy.data.cameras.new("Camera")
    data.lens = 50.0
    cam = bpy.data.objects.new("Camera", data)
    cam.location = location
    cam.rotation_euler = (Vector(target) - Vector(location)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    return cam


reset_scene()

oak = material("MAT_Oak", (0.34, 0.19, 0.09), roughness=0.42)
dark_wood = material("MAT_WalnutTrim", (0.13, 0.07, 0.04), roughness=0.35)
felt = material("MAT_DeskFelt", (0.09, 0.11, 0.16), roughness=0.85)
steel = material("MAT_BrushedSteel", (0.62, 0.63, 0.65), roughness=0.32, metallic=1.0)
foam = material("MAT_MicFoam", (0.04, 0.04, 0.05), roughness=0.95)
paper = material("MAT_Paper", (0.92, 0.91, 0.87), roughness=0.7)
brass = material("MAT_Brass", (0.71, 0.53, 0.20), roughness=0.28, metallic=1.0)
floor_mat = material("MAT_StageFloor", (0.19, 0.18, 0.17), roughness=0.6)

box("Stage_Floor", (7.0, 7.0, 0.06), (0.0, 0.0, -0.03), floor_mat)

box("Podium_Plinth", (0.78, 0.58, 0.06), (0.0, 0.0, 0.03), dark_wood)
tapered_body("Podium_Body", oak)
box("Podium_TopCap", (0.76, 0.56, 0.03), (0.0, 0.0, 1.065), dark_wood)
cylinder("Podium_Emblem", 0.13, 0.02, (0.0, -0.235, 0.60), brass,
         rotation=(math.radians(90.0), 0.0, 0.0), segments=32)
cylinder("Podium_EmblemInlay", 0.09, 0.024, (0.0, -0.237, 0.60), oak,
         rotation=(math.radians(90.0), 0.0, 0.0), segments=32)

box("Desk_ReadingSurface", (0.74, 0.48, 0.035), tuple(DESK), oak, rotation=(SLANT, 0, 0))
box("Desk_FeltPad", (0.66, 0.40, 0.004), tuple(on_desk((0.0, 0.0, 0.020))), felt,
    rotation=(SLANT, 0, 0))
box("Desk_FrontLip", (0.74, 0.035, 0.05), tuple(on_desk((0.0, -0.245, 0.020))), dark_wood,
    rotation=(SLANT, 0, 0))

box("Notes_PaperStack", (0.21, 0.30, 0.012), tuple(on_desk((-0.14, 0.0, 0.028))), paper,
    rotation=(SLANT, 0, 0.06))
box("Notes_TopSheet", (0.21, 0.30, 0.002), tuple(on_desk((-0.11, -0.01, 0.037))), paper,
    rotation=(SLANT, 0, -0.04))

mic_base = on_desk((0.23, 0.13, 0.020))
cylinder("Mic_BasePlate", 0.055, 0.018, tuple(mic_base), steel, rotation=(SLANT, 0, 0), segments=32)
cylinder("Mic_Collar", 0.022, 0.03, tuple(on_desk((0.23, 0.13, 0.040))), steel,
         rotation=(SLANT, 0, 0), segments=20)
gooseneck("Mic_Gooseneck", steel, tuple(on_desk((0.23, 0.13, 0.052))))
capsule = on_desk((0.20, -0.08, 0.32))
cylinder("Mic_Capsule", 0.016, 0.06, tuple(capsule), steel,
         rotation=(math.radians(58.0), 0.0, 0.0), segments=20)
sphere("Mic_Windscreen", 0.030, tuple(capsule + Vector((0.0, -0.035, -0.020))), foam,
       scale=(1.0, 1.25, 1.0))

add_light("Key_Area", 'AREA', 420.0, (1.8, -2.2, 3.2),
          rotation=(math.radians(48.0), 0.0, math.radians(38.0)), size=3.0)
add_light("Fill_Area", 'AREA', 120.0, (-2.4, -1.4, 2.4),
          rotation=(math.radians(58.0), 0.0, math.radians(-52.0)), size=2.5)
add_light("Sun", 'SUN', 1.6, (0.0, 3.0, 4.0), rotation=(math.radians(-35.0), 0.0, 0.0))

add_camera((1.95, -2.45, 1.85), (0.0, -0.05, 0.92))
