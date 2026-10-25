import bpy
import math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = 0.38
    return m

steel = material('Painted blue steel', (0.12, 0.32, 0.43), 0.6)
frame = material('Dark structural steel', (0.11, 0.15, 0.18), 0.7)
silver = material('Galvanized ladder', (0.57, 0.64, 0.66), 0.75)
concrete = material('Concrete foundations', (0.47, 0.46, 0.41))
ground = material('Ground', (0.24, 0.29, 0.23))

def finish(obj, name, mat):
    obj.name = name
    obj.data.materials.append(mat)
    return obj

def box(name, location, scale, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = finish(bpy.context.object, name, mat)
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return obj

def cylinder(name, radius, depth, location, mat, vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location)
    return finish(bpy.context.object, name, mat)

def beam(name, a, b, radius, mat):
    a, b = Vector(a), Vector(b)
    obj = cylinder(name, radius, (b-a).length, (a+b)/2, mat, 12)
    obj.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    return obj

def ring(name, radius, z, thickness, mat):
    bpy.ops.mesh.primitive_torus_add(major_segments=48, minor_segments=8, location=(0, 0, z), major_radius=radius, minor_radius=thickness)
    return finish(bpy.context.object, name, mat)

box('Landscape slab', (0, 0, -0.15), (12, 12, 0.3), ground)
corners = [(-1,-1), (1,-1), (1,1), (-1,1)]
def leg_point(i, z):
    spread = 1.8 - (z-0.3) * 0.6 / 4.65
    sx, sy = corners[i]
    return (sx*spread, sy*spread, z)

for i, (sx, sy) in enumerate(corners):
    box('Concrete footing %d' % i, (sx*1.8, sy*1.8, 0.15), (0.8, 0.8, 0.3), concrete)
    box('Leg baseplate %d' % i, (sx*1.8, sy*1.8, 0.32), (0.42, 0.42, 0.05), frame)
    beam('Tower leg %d' % i, leg_point(i, 0.3), leg_point(i, 4.95), 0.105, frame)
    for z in (0.65, 2.65, 4.6):
        beam('Horizontal tie %d %.2f' % (i,z), leg_point(i,z), leg_point((i+1)%4,z), 0.055, frame)
    for low, high in ((0.65,2.65), (2.65,4.6)):
        beam('Cross brace A %d %.2f' % (i,low), leg_point(i,low), leg_point((i+1)%4,high), 0.035, silver)
        beam('Cross brace B %d %.2f' % (i,low), leg_point((i+1)%4,low), leg_point(i,high), 0.035, silver)

cylinder('Maintenance deck', 2.05, 0.15, (0,0,4.7), frame, 64)
bpy.ops.mesh.primitive_cone_add(vertices=64, radius1=0.6, radius2=1.6, depth=0.7, location=(0,0,5.05))
finish(bpy.context.object, 'Tapered tank bottom', steel)
cylinder('Water storage tank', 1.6, 1.9, (0,0,6.35), steel, 64)
for z in (5.43, 6.35, 7.27):
    ring('Tank reinforcing band %.2f' % z, 1.61, z, 0.045, silver)
bpy.ops.mesh.primitive_cone_add(vertices=64, radius1=1.72, radius2=0.15, depth=0.48, location=(0,0,7.54))
finish(bpy.context.object, 'Conical weather roof', steel)
cylinder('Roof vent', 0.13, 0.28, (0,0,7.86), silver)
cylinder('Vent cap', 0.22, 0.06, (0,0,8.03), frame)
beam('Downpipe', (0.35,0.35,0.45), (0.35,0.35,4.72), 0.11, steel)
beam('Outlet elbow branch', (0.35,0.35,0.45), (1.1,0.35,0.45), 0.11, steel)

# Leave an opening in the deck guardrail at the ladder landing.
for i in range(24):
    a = math.radians(-78 + i * 336/24)
    b = math.radians(-78 + (i+1) * 336/24)
    p = (1.98*math.cos(a), 1.98*math.sin(a))
    q = (1.98*math.cos(b), 1.98*math.sin(b))
    beam('Guardrail post %02d' % i, (*p,4.77), (*p,5.65), 0.025, silver)
    for z in (5.18,5.65):
        beam('Deck railing %02d %.2f' % (i,z), (*p,z), (*q,z), 0.025, silver)
for x in (-0.28,0.28):
    beam('Ladder upright', (x,-2.12,0.15), (x,-2.12,5.65), 0.035, silver)
    for z in (1.1,2.9,4.7):
        beam('Ladder stand-off', (x,-2.12,z), (x,-1.82,z), 0.028, frame)
for i in range(16):
    z = 0.25 + i*0.29
    beam('Ladder rung %02d' % i, (-0.28,-2.12,z), (0.28,-2.12,z), 0.026, silver)

world = bpy.context.scene.world or bpy.data.worlds.new('World')
bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.65,0.75,0.85,1)
world.node_tree.nodes['Background'].inputs[1].default_value = 0.5
bpy.ops.object.light_add(type='AREA', location=(4,-6,11))
bpy.context.object.data.energy = 1800
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 7
bpy.ops.object.camera_add(location=(11,-15,10))
camera = bpy.context.object
camera.rotation_euler = (Vector((0,0,4))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 11.5
bpy.context.scene.camera = camera
