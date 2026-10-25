import bpy
import math
from mathutils import Vector

# Rooftop packaged HVAC plant; all dimensions are in meters.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.5):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    return m

steel = material('Galvanized duct steel', (0.49, 0.56, 0.60), 0.7)
paint = material('Warm gray cabinet enamel', (0.68, 0.71, 0.68), 0.35)
dark = material('Dark intake recesses', (0.035, 0.048, 0.055), 0.15)
guard = material('Fan guard steel', (0.15, 0.19, 0.21), 0.8)
roof = material('Roof membrane', (0.22, 0.25, 0.27))
concrete = material('Concrete parapet', (0.48, 0.46, 0.42))
yellow = material('Service warning yellow', (0.95, 0.57, 0.06))

def box(name, loc, dims, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        mod = o.modifiers.new('Folded edge highlights', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
    return o

def cylinder(name, loc, radius, depth, mat, vertices=48):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)
    return o

def rod(name, a, b, radius, mat):
    a, b = Vector(a), Vector(b)
    o = cylinder(name, (a+b)/2, radius, (b-a).length, mat, 12)
    o.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    return o

def ring(name, center, radius, thickness, mat):
    bpy.ops.mesh.primitive_torus_add(major_segments=48, minor_segments=6, location=center,
        major_radius=radius, minor_radius=thickness)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)

box('Roof slab', (0, 0, -0.18), (11, 9, 0.36), roof, 0.06)
box('Rear parapet', (0, 4.35, 0.28), (11, 0.3, 0.65), concrete, 0.03)
box('Left parapet', (-5.35, 0, 0.28), (0.3, 8.4, 0.65), concrete, 0.03)
for x in (-1.65, 1.65):
    box('Concrete equipment sleeper', (x, 0, 0.16), (0.5, 3.2, 0.32), concrete, 0.025)
box('Raised weatherproof roof curb', (0, 0, 0.47), (4.35, 2.85, 0.4), guard, 0.04)
box('HVAC cabinet', (0, 0, 1.43), (4.5, 2.8, 1.65), paint, 0.055)
box('Overhanging removable top', (0, 0, 2.30), (4.66, 2.96, 0.13), steel, 0.035)
# Recessed front heat-exchanger intake with closely spaced louvers.
box('Condenser intake shadow', (-0.65, -1.415, 1.44), (2.75, 0.045, 1.26), dark)
for i in range(15):
    box('Horizontal condenser louver %02d' % i, (-0.65, -1.46, 0.89+i*0.078),
        (2.73, 0.095, 0.025), steel, 0.006)
box('Service access door', (1.58, -1.435, 1.45), (1.05, 0.07, 1.39), steel, 0.018)
box('Door latch', (1.96, -1.49, 1.43), (0.07, 0.05, 0.26), guard, 0.01)
box('Electrical warning plaque', (1.58, -1.478, 1.77), (0.29, 0.015, 0.21), yellow)
for z in (0.9, 1.95):
    box('Door hinge', (1.08, -1.49, z), (0.06, 0.055, 0.17), guard)
# Two visible fans, each beneath a concentric welded-wire safety grille.
for fan_id, x in enumerate((-1.12, 1.12)):
    cylinder('Fan %d dark well' % fan_id, (x, 0, 2.381), 0.88, 0.035, dark)
    ring('Fan %d raised rim' % fan_id, (x, 0, 2.43), 0.87, 0.045, steel)
    for j in range(6):
        angle = j*math.tau/6
        blade = box('Fan %d blade %d' % (fan_id, j),
            (x+0.46*math.cos(angle), 0.46*math.sin(angle), 2.416), (0.64, 0.22, 0.025), guard, 0.035)
        blade.rotation_euler[2] = angle+0.28
    cylinder('Fan motor hub', (x, 0, 2.44), 0.17, 0.08, steel)
    for r in (0.20, 0.32, 0.44, 0.56, 0.68, 0.80):
        ring('Concentric fan guard', (x, 0, 2.51), r, 0.012, guard)
    for j in range(12):
        a = j*math.tau/12
        rod('Radial fan guard', (x, 0, 2.515), (x+0.85*math.cos(a), 0.85*math.sin(a), 2.515), 0.013, guard)
# Two rectangular ducts leave the right side, then turn down into flashed roof openings.
for y in (-0.73, 0.73):
    box('Supply or return horizontal duct', (3.23, y, 1.59), (2.0, 1.0, 0.85), steel, 0.025)
    box('Downturned duct leg', (4.03, y, 0.98), (0.85, 1.0, 1.9), steel, 0.035)
    box('Roof penetration flashing', (4.03, y, 0.075), (1.12, 1.24, 0.15), guard, 0.025)
    for x in (2.33, 3.12, 3.98):
        box('Duct top transverse seam', (x, y, 2.025), (0.055, 1.06, 0.055), guard, 0.008)
        for edge in (-0.51, 0.51):
            box('Duct side transverse seam', (x, y+edge, 1.59), (0.055, 0.035, 0.85), guard)
    for z in (0.5, 1.15):
        box('Vertical duct seam', (4.47, y, z), (0.035, 1.04, 0.055), guard)

scene = bpy.context.scene
scene.world.color = (0.22, 0.22, 0.22)
bpy.ops.object.light_add(type='AREA', location=(1, -5, 10))
bpy.context.object.name = 'Large rooftop softbox'
bpy.context.object.data.energy = 1800
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 7
bpy.ops.object.camera_add(location=(11, -13, 10))
cam = bpy.context.object
cam.name = 'HVAC overview camera'
cam.rotation_euler = (Vector((0.4, 0, 1.0))-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 13.5
scene.camera = cam
scene.render.resolution_x = 1200
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
