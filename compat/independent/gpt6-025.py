import bpy
import math
from mathutils import Vector

# Circular timber gazebo with an open entrance and a faceted metal roof.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = 0.42
    return mat

wood = material('Warm cedar', (0.36, 0.16, 0.065))
trim = material('Light cedar trim', (0.58, 0.31, 0.13))
roof_mat = material('Patinated green metal', (0.075, 0.23, 0.20), 0.65)
stone = material('Sandstone foundation', (0.56, 0.53, 0.44))
ground = material('Ground', (0.23, 0.29, 0.22))

def cube(name, location, scale, mat, bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Soft edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def cylinder(name, radius, depth, z, mat, vertices=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=(0, 0, z))
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    return obj

def beam(name, a, b, width, height, mat):
    a, b = Vector(a), Vector(b)
    obj = cube(name, (a+b)/2, (width, height, (b-a).length), mat, 0.012)
    obj.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    return obj

cylinder('Circular stone footing', 3.1, 0.24, 0.12, stone)
cylinder('Raised timber deck fascia', 2.94, 0.22, 0.35, wood)
# Chord-length planks keep the floor circular.
for i in range(-12, 13):
    y = i * 0.225
    length = 2 * math.sqrt(2.90**2 - (abs(y)+0.10)**2)
    cube('Deck plank %02d' % (i+13), (0, y, 0.48), (length, 0.211, 0.08), trim, 0.008)
cube('Entrance lower step', (0, -3.27, 0.09), (1.85, 0.72, 0.18), stone)
cube('Entrance upper step', (0, -2.94, 0.23), (1.72, 0.60, 0.28), wood)

points = []
for i in range(8):
    angle = -math.pi/2 - math.pi/8 + i*math.tau/8
    x, y = 2.57*math.cos(angle), 2.57*math.sin(angle)
    points.append(Vector((x, y, 0)))
    cube('Post %02d' % (i+1), (x, y, 1.93), (0.20, 0.20, 2.82), wood)
    cube('Post shoe %02d' % (i+1), (x, y, 0.64), (0.29, 0.29, 0.24), trim)
    cube('Post capital %02d' % (i+1), (x, y, 3.22), (0.32, 0.32, 0.17), trim)
for i, p in enumerate(points):
    q = points[(i+1) % 8]
    beam('Eave ring beam %02d' % i, p+Vector((0,0,3.36)), q+Vector((0,0,3.36)), 0.21, 0.24, wood)
    direction = (q-p).normalized()
    for anchor, sign in [(p, 1), (q, -1)]:
        beam('Diagonal knee brace', anchor+Vector((0,0,2.79)), anchor+direction*sign*0.48+Vector((0,0,3.30)), 0.11, 0.11, trim)
    if i == 0:  # Entrance bay faces the camera.
        continue
    for z, size in [(0.75, 0.09), (1.48, 0.12)]:
        beam('Railing horizontal', p+Vector((0,0,z)), q+Vector((0,0,z)), size, size, trim)
    for j in range(1, 8):
        v = p.lerp(q, j/8)
        cube('Railing baluster', (v.x, v.y, 1.10), (0.055, 0.055, 0.69), wood, 0.008)

# A low-poly conical roof with visible radial standing seams.
count = 16
verts = [(0, 0, 4.90)] + [(3.30*math.cos(i*math.tau/count), 3.30*math.sin(i*math.tau/count), 3.47) for i in range(count)]
faces = [(0, i+1, (i+1) % count+1) for i in range(count)]
mesh = bpy.data.meshes.new('Roof shell mesh')
mesh.from_pydata(verts, [], faces)
mesh.update()
roof = bpy.data.objects.new('Sixteen-sided pitched roof', mesh)
bpy.context.collection.objects.link(roof)
roof.data.materials.append(roof_mat)
solid = roof.modifiers.new('Roof sheet thickness', 'SOLIDIFY')
solid.thickness = 0.065
for i in range(count):
    beam('Roof standing seam %02d' % i, verts[i+1], (0,0,4.92), 0.025, 0.025, roof_mat)
cylinder('Roof finial', 0.085, 0.30, 5.02, roof_mat, 16)
cube('Ground plane', (0,0,-0.10), (200,200,0.16), ground, 0)

bpy.ops.object.camera_add(location=(8,-11,7))
camera = bpy.context.object
camera.name = 'Gazebo overview camera'
camera.rotation_euler = (Vector((0,0,2.1))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 10.6
bpy.context.scene.camera = camera
bpy.ops.object.light_add(type='AREA', location=(2,-5,10))
bpy.context.object.data.energy = 1800
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 7
scene = bpy.context.scene
scene.world = bpy.data.worlds.new('Gazebo world')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.55,0.65,0.78,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.45
scene.render.resolution_x = 1200
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
