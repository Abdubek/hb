import bpy
import bmesh
import math
from mathutils import Vector

# --------------------------------------------------------------- utilities


def clear_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras,
                 bpy.data.lights):
        for item in list(coll):
            coll.remove(item)


def material(name, color, metallic=0.0, roughness=0.5):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    return mat


def register(obj, name, mat, parent):
    obj.name = name
    obj.data.name = name
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    obj.parent = parent
    return obj


def box(name, size, loc, mat, parent):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    obj = bpy.context.object
    obj.scale = size
    return register(obj, name, mat, parent)


def tube(name, radius, depth, loc, mat, parent, rot=(0, 0, 0), verts=28):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth,
                                        vertices=verts, location=loc,
                                        rotation=rot)
    return register(bpy.context.object, name, mat, parent)


def taper(name, r1, r2, depth, loc, mat, parent):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=depth,
                                    vertices=24, location=loc)
    return register(bpy.context.object, name, mat, parent)


def wedge(name, loc, mat, parent):
    """Cowcatcher: wide tall back tapering to a narrow low front (+X)."""
    coords = [(0.0, -0.55, 0.15), (0.0, 0.55, 0.15),
              (0.0, 0.55, 0.75), (0.0, -0.55, 0.75),
              (0.65, -0.22, 0.02), (0.65, 0.22, 0.02),
              (0.65, 0.22, 0.38), (0.65, -0.22, 0.38)]
    faces = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 3, 7, 4),
             (1, 5, 6, 2), (0, 4, 5, 1), (3, 2, 6, 7)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(coords, [], faces)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = loc
    return register(obj, name, mat, parent)


def wheel(tag, x, radius, mats, parent):
    tyre, hub = mats
    for sign in (1, -1):
        side = 'L' if sign > 0 else 'R'
        y = sign * 0.66
        z = 0.12 + radius
        tube('Wheel_%s_%s' % (tag, side), radius, 0.12, (x, y, z), tyre,
             parent, rot=(math.radians(90), 0, 0), verts=32)
        tube('WheelHub_%s_%s' % (tag, side), radius * 0.32, 0.18,
             (x, y, z), hub, parent, rot=(math.radians(90), 0, 0), verts=16)


def aim_camera(cam, target):
    direction = Vector(target) - cam.location
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


# --------------------------------------------------------------- the build
clear_scene()

red = material('MAT_ToyRed', (0.58, 0.06, 0.05), roughness=0.35)
green = material('MAT_ToyGreen', (0.05, 0.24, 0.14), roughness=0.35)
black = material('MAT_MattBlack', (0.03, 0.03, 0.035), roughness=0.55)
brass = material('MAT_Brass', (0.72, 0.55, 0.18), metallic=1.0, roughness=0.28)
steel = material('MAT_Steel', (0.55, 0.56, 0.58), metallic=1.0, roughness=0.35)
wood = material('MAT_Sleeper', (0.24, 0.16, 0.10), roughness=0.8)
ballast = material('MAT_Ballast', (0.42, 0.41, 0.39), roughness=0.9)

bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
loco = bpy.context.object
loco.name = 'ToyLocomotive'

# track
box('Ballast_Bed', (11.0, 2.6, 0.10), (0, 0, -0.05), ballast, None)
for i in range(7):
    box('Sleeper_%02d' % (i + 1), (0.34, 2.10, 0.10),
        (-4.2 + i * 1.4, 0, 0.03), wood, None)
for sign in (1, -1):
    box('Rail_%s' % ('L' if sign > 0 else 'R'), (11.0, 0.12, 0.12),
        (0, sign * 0.66, 0.10), steel, None)

# frame and running gear
box('Chassis_Frame', (4.50, 1.15, 0.25), (-0.15, 0, 1.05), black, loco)
box('Footplate', (4.30, 1.60, 0.06), (-0.15, 0, 1.20), red, loco)
wheel('Driver_Rear', -1.45, 0.50, (black, brass), loco)
wheel('Driver_Front', -0.25, 0.50, (black, brass), loco)
wheel('Pony', 1.50, 0.32, (black, brass), loco)
for sign in (1, -1):
    box('CouplingRod_%s' % ('L' if sign > 0 else 'R'), (1.45, 0.06, 0.10),
        (-0.85, sign * 0.76, 0.62), steel, loco)

# boiler group
tube('Boiler', 0.55, 2.60, (0.55, 0, 1.75), green, loco,
     rot=(0, math.radians(90), 0), verts=32)
for i in range(3):
    tube('BoilerBand_%d' % (i + 1), 0.58, 0.07, (-0.20 + i * 0.75, 0, 1.75),
         brass, loco, rot=(0, math.radians(90), 0), verts=32)
tube('Smokebox', 0.60, 0.45, (2.05, 0, 1.75), black, loco,
     rot=(0, math.radians(90), 0), verts=32)
tube('SmokeboxDoor', 0.62, 0.06, (2.30, 0, 1.75), brass, loco,
     rot=(0, math.radians(90), 0), verts=32)
taper('Chimney', 0.20, 0.28, 0.60, (1.95, 0, 2.60), black, loco)
tube('ChimneyCap', 0.31, 0.12, (1.95, 0, 2.95), brass, loco)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.34, segments=24, ring_count=12,
                                     location=(0.75, 0, 2.24))
dome = bpy.context.object
dome.scale = (1.0, 1.0, 0.7)
register(dome, 'SteamDome', brass, loco)
tube('SafetyValve', 0.07, 0.22, (0.05, 0, 2.38), brass, loco, verts=12)
tube('Headlamp', 0.18, 0.22, (2.45, 0, 2.15), brass, loco,
     rot=(0, math.radians(90), 0), verts=20)
for sign in (1, -1):
    tube('Handrail_%s' % ('L' if sign > 0 else 'R'), 0.03, 2.40,
         (0.55, sign * 0.57, 2.05), brass, loco,
         rot=(0, math.radians(90), 0), verts=10)

# cab: side panels, corner pillars, back wall, roof
for sign in (1, -1):
    side = 'L' if sign > 0 else 'R'
    box('CabSide_%s' % side, (1.55, 0.09, 0.55),
        (-1.52, sign * 0.58, 1.62), red, loco)
    box('CabPillar_Front_%s' % side, (0.10, 0.14, 1.30),
        (-0.80, sign * 0.52, 2.02), red, loco)
    box('CabPillar_Rear_%s' % side, (0.10, 0.14, 1.30),
        (-2.22, sign * 0.52, 2.02), red, loco)
box('CabBackWall', (0.09, 1.20, 1.30), (-2.26, 0, 2.02), red, loco)
box('CabRoof', (1.75, 1.40, 0.10), (-1.52, 0, 2.72), green, loco)
tube('Whistle', 0.06, 0.26, (-0.95, 0.22, 2.90), brass, loco, verts=12)

# front end
box('BufferBeam', (0.16, 1.45, 0.50), (2.38, 0, 1.10), red, loco)
for sign in (1, -1):
    tube('Buffer_%s' % ('L' if sign > 0 else 'R'), 0.11, 0.22,
         (2.55, sign * 0.48, 1.10), steel, loco,
         rot=(0, math.radians(90), 0), verts=16)
wedge('Cowcatcher', (2.46, 0, 0.30), steel, loco)

# --------------------------------------------------------------- staging
bpy.ops.object.light_add(type='SUN', location=(5, -6, 9))
sun = bpy.context.object
sun.name = 'KeyLight_Sun'
sun.data.energy = 3.5
sun.rotation_euler = (math.radians(48), math.radians(12), math.radians(30))

bpy.ops.object.light_add(type='AREA', location=(-6, -5, 4))
fill = bpy.context.object
fill.name = 'FillLight'
fill.data.energy = 500.0
fill.data.size = 8.0
fill.rotation_euler = (math.radians(75), 0, math.radians(-55))

bpy.ops.object.camera_add(location=(6.5, -7.0, 4.0))
cam = bpy.context.object
cam.name = 'SceneCamera'
cam.data.lens = 50.0
aim_camera(cam, (-0.1, 0.0, 1.55))
bpy.context.scene.camera = cam
