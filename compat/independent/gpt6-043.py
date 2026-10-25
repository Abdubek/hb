import bpy
import math
from mathutils import Vector

# Public fountain: adult and accessible-height drinking stations.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.4):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = roughness
    return m

steel = material('Brushed stainless steel', (0.49, 0.56, 0.59), 0.85, 0.27)
paint = material('Deep blue powder coat', (0.035, 0.15, 0.22), 0.35)
dark = material('Drain recesses and rubber', (0.025, 0.034, 0.04))
concrete = material('Pale concrete paving', (0.55, 0.53, 0.48), roughness=0.85)
blue = material('Blue activation buttons', (0.035, 0.38, 0.75), 0.25)

def box(name, location, scale, mat, bevel=0.03):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    ob = bpy.context.object
    ob.name = name
    ob.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(mat)
    if bevel:
        mod = ob.modifiers.new('Soft manufactured edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        ob.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    return ob

def cylinder(name, location, radius, depth, mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=depth, location=location)
    ob = bpy.context.object
    ob.name = name
    ob.data.materials.append(mat)
    bevel = ob.modifiers.new('Edge rounding', 'BEVEL')
    bevel.width = 0.007
    bevel.segments = 2
    ob.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return ob

def tube(name, points, radius, mat):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = radius
    curve.bevel_resolution = 3
    spline = curve.splines.new('POLY')
    spline.points.add(len(points)-1)
    for p, co in zip(spline.points, points):
        p.co = (*co, 1)
    ob = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat)
    return ob

def basin(name, x, y, z):
    # Closed revolved section, with a shallow concave interior and drain hole.
    profile = [(0.055,-0.135), (0.17,-0.115), (0.31,-0.065),
               (0.395,-0.005), (0.407,0.012), (0.43,0.012),
               (0.44,-0.01), (0.42,-0.06), (0.33,-0.13),
               (0.18,-0.175), (0.055,-0.175)]
    n = 64
    verts = [(x+r*math.cos(2*math.pi*j/n), y+r*math.sin(2*math.pi*j/n), z+h)
             for r,h in profile for j in range(n)]
    faces = []
    for i in range(len(profile)):
        k = (i+1) % len(profile)
        for j in range(n):
            q = (j+1) % n
            faces.append((i*n+j, k*n+j, k*n+q, i*n+q))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    ob = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(steel)
    for poly in mesh.polygons:
        poly.use_smooth = True
    cylinder(name+' drain well', (x,y,z-0.151), 0.055, 0.025, dark)
    for offset in (-0.03,-0.015,0,0.015,0.03):
        box(name+' drain grate', (x+offset,y,z-0.135), (0.005,0.075,0.005), steel, 0)
    cylinder(name+' bubbler base', (x,y+0.29,z+0.02), 0.061, 0.07, steel)
    tube(name+' curved bubbler', [(x,y+0.29,z+0.045), (x,y+0.29,z+0.105),
         (x,y+0.26,z+0.135), (x,y+0.215,z+0.13)], 0.024, steel)
    nozzle = cylinder(name+' nozzle opening', (x,y+0.207,z+0.13), 0.015, 0.01, dark)
    nozzle.rotation_euler[0] = math.pi/2
    button = cylinder(name+' push button', (x,y-0.38,z-0.07), 0.035, 0.024, blue)
    button.rotation_euler[0] = math.pi/2

box('Concrete apron', (0,0,-0.08), (3.8,3.0,0.16), concrete)
box('Anchored foot plate', (0,0.33,0.045), (0.65,0.62,0.09), steel)
box('Service pedestal', (0,0.33,0.64), (0.43,0.43,1.17), paint)
box('Removable service panel', (0,0.106,0.52), (0.32,0.015,0.66), steel, 0.01)
for x in (-0.24,0.24):
    for y in (0.12,0.54):
        cylinder('Anchor bolt', (x,y,0.099), 0.028, 0.021, steel)
for name, x, z in [('Adult station',-0.53,1.22), ('Accessible station',0.53,0.86)]:
    box(name+' cantilever arm', (x/2,0.22,z-0.19), (abs(x)+0.2,0.22,0.15), paint)
    basin(name+' basin', x,0,z)
box('Pedestal top cap', (0,0.33,1.24), (0.45,0.45,0.055), steel)

bpy.ops.object.camera_add(location=(3.3,-4.5,3.0))
camera = bpy.context.object
camera.name = 'Fountain presentation camera'
camera.rotation_euler = (Vector((0,0,0.72))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 3.55
bpy.context.scene.camera = camera
bpy.ops.object.light_add(type='AREA', location=(0,-3,5))
bpy.context.object.data.energy = 700
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 4
bpy.context.scene.world.color = (0.22,0.22,0.22)
