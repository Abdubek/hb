import bpy
import math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0, roughness=0.4):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    return mat

ivory = material('Ivory enamel optical tube', (0.82, 0.79, 0.66), 0.2)
black = material('Black anodized hardware', (0.035, 0.043, 0.055), 0.45)
silver = material('Satin aluminum tripod', (0.48, 0.54, 0.60), 0.8)
rubber = material('Rubber grips and feet', (0.025, 0.028, 0.035), 0, 0.7)
blue = material('Blue coated objective', (0.035, 0.16, 0.26), 0.65, 0.12)
brass = material('Brass adjustment details', (0.65, 0.38, 0.11), 0.7)
floor = material('Studio ground', (0.18, 0.21, 0.25))

def finish(obj, name, mat, bevel=0.01):
    obj.name = name
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Machined edge bevel', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def cylinder(name, loc, radius, depth, mat, axis=(0, 0, 1), vertices=40):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    obj = bpy.context.object
    obj.rotation_euler = Vector(axis).to_track_quat('Z', 'Y').to_euler()
    return finish(obj, name, mat)

def rod(name, a, b, radius, mat):
    a, b = Vector(a), Vector(b)
    return cylinder(name, (a+b)/2, radius, (b-a).length, mat, b-a)

def box(name, loc, dimensions, mat, bevel=0.02):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(obj, name, mat, bevel)

def ring(name, loc, major, minor, mat, axis):
    bpy.ops.mesh.primitive_torus_add(major_segments=48, minor_segments=10, major_radius=major, minor_radius=minor, location=loc)
    obj = bpy.context.object
    obj.rotation_euler = Vector(axis).to_track_quat('Z', 'Y').to_euler()
    return finish(obj, name, mat, 0)

def knob(name, loc, radius, depth, axis):
    axis = Vector(axis).normalized()
    cylinder(name + ' fluted grip', loc, radius, depth, rubber, axis, 16)
    cylinder(name + ' metal center', Vector(loc)+axis*(depth/2+0.007), radius*0.43, 0.018, brass, axis)

# Three splayed telescopic legs and an accessory/spreader tray.
for i in range(3):
    angle = math.radians(30+i*120)
    radial = Vector((math.cos(angle), math.sin(angle), 0))
    top = radial*0.19 + Vector((0, 0, 1.57))
    bottom = radial*1.05 + Vector((0, 0, 0.09))
    collar = top.lerp(bottom, 0.59)
    rod('Tripod leg %d upper sleeve' % (i+1), top, collar, 0.063, silver)
    rod('Tripod leg %d extension' % (i+1), collar, bottom, 0.043, silver)
    cylinder('Leg %d locking collar' % (i+1), collar, 0.080, 0.12, black, bottom-top)
    knob('Leg %d clamp screw' % (i+1), collar+radial*0.10, 0.045, 0.045, radial)
    cylinder('Leg %d rubber foot' % (i+1), bottom, 0.079, 0.14, rubber)
    rod('Leg %d spreader brace' % (i+1), (0, 0, 0.76), top.lerp(bottom, 0.58), 0.022, black)
cylinder('Circular accessory tray', (0, 0, 0.78), 0.38, 0.055, black)
cylinder('Tripod crown', (0, 0, 1.58), 0.27, 0.16, black)
cylinder('Azimuth rotating head', (0, 0, 1.72), 0.21, 0.14, silver)
knob('Azimuth locking knob', (0, -0.31, 1.70), 0.10, 0.13, (0, -1, 0))

# Optical axis points upward; a fork carries the altitude bearings.
center = Vector((0, 0, 2.17))
axis = Vector((0.88, 0, 0.475)).normalized()
up = Vector((-axis.z, 0, axis.x))
for side in (-1, 1):
    box('Altitude fork upright', (0, side*0.36, 1.97), (0.18, 0.13, 0.53), black)
    cylinder('Altitude bearing', (0, side*0.37, 2.17), 0.14, 0.13, silver, (0, 1, 0))
cylinder('Altitude pivot axle', center, 0.072, 0.88, silver, (0, 1, 0))
knob('Large altitude tension wheel', (0, -0.51, 2.17), 0.18, 0.13, (0, -1, 0))
cylinder('Main refractor optical tube', center, 0.255, 1.65, ivory, axis)
for distance in (-0.38, 0.38):
    cylinder('Tube mounting band', center+axis*distance, 0.271, 0.075, black, axis)
# Recess the objective behind an open rim, leaving the front visibly uncovered.
cylinder('Objective cell', center+axis*0.86, 0.285, 0.12, black, axis)
cylinder('Objective blue glass', center+axis*0.927, 0.249, 0.016, blue, axis)
ring('Raised objective rim', center+axis*0.95, 0.268, 0.020, black, axis)
cylinder('Rear focusing housing', center-axis*0.88, 0.18, 0.19, black, axis)
cylinder('Polished focuser drawtube', center-axis*1.06, 0.085, 0.22, silver, axis)
cylinder('Eyepiece barrel', center-axis*1.23, 0.09, 0.16, black, axis)
ring('Rubber eyecup', center-axis*1.32, 0.072, 0.020, rubber, axis)
focus_center = center-axis*0.91-up*0.09
cylinder('Focus pinion shaft', focus_center, 0.035, 0.48, silver, (0, 1, 0))
for side in (-1, 1):
    knob('Fine focus wheel', focus_center+Vector((0, side*0.25, 0)), 0.09, 0.06, (0, side, 0))
finder = center+up*0.43-axis*0.19
for offset in (-0.15, 0.15):
    rod('Finder scope support', finder+axis*offset-up*0.19, finder+axis*offset, 0.035, black)
cylinder('Finder scope tube', finder, 0.065, 0.53, ivory, axis)
cylinder('Finder front lens bezel', finder+axis*0.28, 0.076, 0.06, black, axis)
cylinder('Finder front glass', finder+axis*0.314, 0.054, 0.009, blue, axis)
box('Ground', (0, 0, -0.025), (200, 200, 0.05), floor, 0)
bpy.ops.object.camera_add(location=(4.8, -6.2, 3.9))
camera = bpy.context.object
camera.name = 'Telescope presentation camera'
camera.rotation_euler = (Vector((0, 0, 1.45))-camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 4.4
bpy.context.scene.camera = camera
for loc, energy, size in [((2, -4, 6), 1200, 4), ((-3, 2, 5), 900, 3)]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    light = bpy.context.object
    light.data.energy = energy
    light.data.size = size
    light.rotation_euler = (Vector((0, 0, 1.5))-light.location).to_track_quat('-Z', 'Y').to_euler()
scene = bpy.context.scene
scene.world = bpy.data.worlds.new('Studio world')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.35
scene.render.resolution_x = 1000
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
