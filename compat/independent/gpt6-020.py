import bpy
import math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.45):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = roughness
    return m

armor = material('Safety yellow armor', (0.91, 0.56, 0.055), 0.3)
dark = material('Graphite chassis', (0.04, 0.055, 0.07), 0.55)
steel = material('Joint aluminum', (0.4, 0.47, 0.53), 0.8, 0.28)
rubber = material('Grippy rubber feet', (0.018, 0.023, 0.029), 0, 0.85)
lens = material('Blue optical glass', (0.015, 0.3, 0.48), 0.5, 0.17)
floor = material('Concrete', (0.28, 0.31, 0.34), 0, 0.8)

def finish(obj, name, mat, bevel=0):
    obj.name = name
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Machined edge radius', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def box(name, loc, dimensions, mat, bevel=0.04):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(obj, name, mat, bevel)

def beam(name, a, b, width, depth, mat):
    a, b = Vector(a), Vector(b)
    obj = box(name, (a+b)/2, (width, depth, (b-a).length), mat, 0.035)
    obj.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    return obj

def cylinder(name, loc, radius, depth, mat, axis=(0, 0, 1)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=depth, location=loc)
    obj = bpy.context.object
    obj.rotation_euler = Vector(axis).to_track_quat('Z', 'Y').to_euler()
    finish(obj, name, mat, 0.015)
    for p in obj.data.polygons:
        p.use_smooth = len(p.vertices) == 4
    return obj

box('Central load bearing chassis', (0, 0, 1.63), (2.25, 0.76, 0.43), dark, 0.11)
box('Upper armored shell', (0, 0, 1.89), (2.14, 0.87, 0.23), armor, 0.09)
box('Underside battery pack', (-0.16, 0, 1.37), (1.26, 0.59, 0.18), steel, 0.05)
box('Top service hatch', (-0.18, 0, 2.025), (0.91, 0.58, 0.055), dark, 0.025)
for x in [-0.54, 0.18]:
    for y in [-0.22, 0.22]:
        cylinder('Service hatch fastener', (x, y, 2.063), 0.033, 0.02, steel)
for side in [-1, 1]:
    box('Side armor rail ' + str(side), (0, side*0.443, 1.72), (1.36, 0.075, 0.22), armor)
    for i in range(6):
        box('Cooling slot %s %s' % (side, i), (-0.43+i*0.16, side*0.486, 1.74),
            (0.07, 0.018, 0.11), dark, 0.012)

# Four independent articulated legs; the front of the dog is positive X.
for fore, label in [(True, 'Front'), (False, 'Rear')]:
    x = 0.79 if fore else -0.79
    for side, side_name in [(-1, 'Right'), (1, 'Left')]:
        name = label + ' ' + side_name
        hip = Vector((x, side*0.57, 1.64))
        knee = Vector((x + (0.28 if fore else 0.35), side*0.69, 0.91))
        ankle = Vector((x - 0.12, side*0.76, 0.22))
        cylinder(name + ' hip motor', hip, 0.235, 0.27, dark, (0, 1, 0))
        cylinder(name + ' hip armor disc', hip + Vector((0, side*0.15, 0)),
                 0.18, 0.055, armor, (0, 1, 0))
        beam(name + ' upper leg', hip, knee, 0.22, 0.17, armor)
        cylinder(name + ' knee bearing', knee, 0.145, 0.25, steel, (0, 1, 0))
        cylinder(name + ' knee cap', knee + Vector((0, side*0.14, 0)),
                 0.105, 0.045, dark, (0, 1, 0))
        beam(name + ' lower leg', knee, ankle, 0.12, 0.13, dark)
        offset = Vector((0, side*0.105, 0))
        beam(name + ' exposed linkage', hip.lerp(knee, 0.35)+offset,
             knee.lerp(ankle, 0.60)+offset, 0.045, 0.045, steel)
        cylinder(name + ' ankle pivot', ankle, 0.095, 0.17, steel, (0, 1, 0))
        box(name + ' rubber foot', (ankle.x+0.035, ankle.y, 0.105),
            (0.38, 0.26, 0.19), rubber, 0.07)

beam('Short neck mount', (0.95, 0, 1.87), (1.32, 0, 2.01), 0.24, 0.3, steel)
box('Sensor head', (1.42, 0, 2.02), (0.55, 0.70, 0.38), armor, 0.09)
box('Black optical faceplate', (1.705, 0, 2.025), (0.035, 0.58, 0.26), dark, 0.025)
for y in [-0.18, 0.18]:
    cylinder('Stereo camera bezel', (1.74, y, 2.055), 0.092, 0.055, steel, (1, 0, 0))
    cylinder('Stereo camera lens', (1.775, y, 2.055), 0.067, 0.023, lens, (1, 0, 0))
box('Depth scanner aperture', (1.731, 0, 1.955), (0.025, 0.16, 0.04), lens, 0.01)
beam('Rear antenna stalk', (-1.0, 0, 1.96), (-1.34, 0, 2.32), 0.045, 0.045, dark)
box('Ground', (0, 0, -0.06), (200, 200, 0.1), floor, 0)
bpy.ops.object.camera_add(location=(5.2, -6.2, 3.8))
cam = bpy.context.object
cam.name = 'Robot dog three quarter camera'
cam.rotation_euler = (Vector((0.15, 0, 1.15))-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 4.6
bpy.context.scene.camera = cam
bpy.ops.object.light_add(type='AREA', location=(2, -3, 6))
bpy.context.object.data.energy = 1100
bpy.context.object.data.size = 5
bpy.context.scene.world.color = (0.3, 0.3, 0.3)
