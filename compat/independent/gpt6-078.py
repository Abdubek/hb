import bpy
import math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.5):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color,1)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color,1)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    return m

yellow = material('Safety yellow enamel', (1.0,0.66,0.025), 0.12)
black = material('Black diagonal paint', (0.022,0.026,0.03))
steel = material('Galvanized support frame', (0.42,0.48,0.52), 0.75)
rubber = material('Rubber foot pads', (0.035,0.041,0.047))
amber = material('Amber warning lenses', (1.0,0.24,0.012), 0.05, 0.23)
ground = material('Concrete ground', (0.29,0.32,0.34))

def box(name, location, size, mat, bevel=0.02):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    ob = bpy.context.object
    ob.name = name
    ob.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(mat)
    if bevel:
        mod = ob.modifiers.new('Rounded edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        ob.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return ob

def beam(name, start, end, width, depth, mat):
    direction = Vector(end) - Vector(start)
    ob = box(name, (Vector(start)+Vector(end))/2, (width,depth,direction.length), mat)
    ob.rotation_euler = direction.to_track_quat('Z','Y').to_euler()
    return ob

def cylinder(name, location, radius, depth, mat, rotation=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=radius,
        depth=depth, location=location, rotation=rotation)
    ob = bpy.context.object
    ob.name = name
    ob.data.materials.append(mat)
    bevel = ob.modifiers.new('Edge highlight', 'BEVEL')
    bevel.width = 0.008
    bevel.segments = 2
    ob.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return ob

# Clip each diagonal paint polygon precisely to the ends of its slat.
def clip_x(poly, edge, keep_greater):
    result = []
    for a, b in zip(poly, poly[1:] + poly[:1]):
        inside_a = a[0] >= edge if keep_greater else a[0] <= edge
        inside_b = b[0] >= edge if keep_greater else b[0] <= edge
        if inside_a:
            result.append(a)
        if inside_a != inside_b:
            t = (edge-a[0])/(b[0]-a[0])
            result.append((edge, a[1]+t*(b[1]-a[1])))
    return result

def striped_slat(name, z):
    box(name, (0,-0.17,z), (4.8,0.14,0.43), yellow, 0.012)
    for side, y in [('Front',-0.241),('Back',-0.099)]:
        for i in range(-5,6):
            x = i * 0.86
            poly = [(x,z-0.2),(x+0.42,z-0.2),
                    (x+0.82,z+0.2),(x+0.4,z+0.2)]
            poly = clip_x(poly,-2.385,True)
            poly = clip_x(poly,2.385,False)
            if len(poly) < 3:
                continue
            mesh = bpy.data.meshes.new(name+' paint mesh')
            indices = list(range(len(poly)))
            if side == 'Back':
                indices.reverse()
            mesh.from_pydata([(px,y,pz) for px,pz in poly], [], [indices])
            mesh.update()
            ob = bpy.data.objects.new(name+' '+side+' stripe '+str(i),mesh)
            bpy.context.collection.objects.link(ob)
            ob.data.materials.append(black)

box('Ground slab', (0,0,-0.12), (9,7,0.24), ground, 0.05)
for x, label in [(-1.83,'Left'),(1.83,'Right')]:
    box(label+' stabilizer foot', (x,0,0.14), (0.36,1.7,0.17), steel)
    for y in (-0.7,0.7):
        box(label+' rubber ground pad', (x,y,0.045), (0.42,0.32,0.09), rubber)
    beam(label+' front A-frame leg', (x,-0.64,0.21), (x,0,2.4), 0.13,0.12,steel)
    beam(label+' rear A-frame leg', (x,0.64,0.21), (x,0,2.4), 0.13,0.12,steel)
    beam(label+' spreader brace', (x,-0.48,0.77), (x,0.48,0.77), 0.07,0.07,steel)
    box(label+' slat mounting upright', (x,-0.04,1.6), (0.13,0.12,1.62), steel)
    cylinder(label+' folding hinge', (x,0,2.32), 0.095,0.19,steel,(0,math.pi/2,0))
    box(label+' beacon base', (x,0,2.45), (0.25,0.23,0.12), black)
    cylinder(label+' amber warning beacon', (x,0,2.62), 0.105,0.23,amber)
    cylinder(label+' beacon cap', (x,0,2.745), 0.115,0.035,black)

striped_slat('Lower striped safety slat',1.12)
striped_slat('Upper striped safety slat',1.94)
for x in (-1.83,1.83):
    for z in (1.12,1.94):
        cylinder('Slat mounting washer', (x,-0.25,z), 0.044,0.015,steel,(math.pi/2,0,0))
        cylinder('Slat mounting bolt head', (x,-0.266,z), 0.025,0.021,steel,(math.pi/2,0,0))

bpy.ops.object.camera_add(location=(6.4,-9,4.6))
camera = bpy.context.object
camera.name = 'Barricade presentation camera'
camera.rotation_euler = (Vector((0,0,1.25))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 6.7
bpy.context.scene.camera = camera
bpy.ops.object.light_add(type='AREA', location=(-3,-4,7))
bpy.context.object.name = 'Large softbox'
bpy.context.object.data.energy = 1200
bpy.context.object.data.size = 5
bpy.context.scene.world.color = (0.3,0.3,0.3)
bpy.context.scene.render.resolution_x = 1400
bpy.context.scene.render.resolution_y = 1000
bpy.context.scene.render.resolution_percentage = 100
