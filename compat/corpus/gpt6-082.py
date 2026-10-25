import bpy, math
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name, color, metallic=0, roughness=0.45):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    return m

def box(name, loc, size, material, bevel=0.02):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    if bevel:
        mod = o.modifiers.new('Edge detail', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def rod(name, a, b, radius, material):
    a, b = Vector(a), Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=radius, depth=(b-a).length, location=(a+b)/2)
    o = bpy.context.object
    o.name = name
    o.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    o.data.materials.append(material)
    for p in o.data.polygons:
        p.use_smooth = True
    return o

def curve(name, coords, radius, material):
    c = bpy.data.curves.new(name, 'CURVE')
    c.dimensions = '3D'
    c.bevel_depth = radius
    c.bevel_resolution = 3
    s = c.splines.new('POLY')
    s.points.add(len(coords)-1)
    for p, co in zip(s.points, coords):
        p.co = (*co, 1)
    o = bpy.data.objects.new(name, c)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(material)

roofmat = mat('Pearl roof skin', (0.78, 0.8, 0.76), 0.5, 0.3)
wood = mat('Warm cedar soffit', (0.4, 0.19, 0.07), 0, 0.53)
metal = mat('Bronze columns', (0.16, 0.12, 0.07), 0.75, 0.28)
stone = mat('Limestone paving', (0.63, 0.62, 0.55), 0, 0.78)
dark = mat('Shadow joints', (0.15, 0.17, 0.15), 0, 0.8)
grass = mat('Landscape green', (0.2, 0.29, 0.17), 0, 0.9)
water = mat('Reflection pool', (0.045, 0.19, 0.19), 0.45, 0.16)
soil = mat('Planter soil', (0.065, 0.045, 0.026), 0, 1)

box('Landscape platform', (0, 0, -0.27), (22, 18, 0.5), grass, 0.22)
box('Pavilion foundation', (0, 0, 0.12), (13.4, 8.8, 0.35), dark, 0.07)
for i in range(13):
    for j in range(8):
        box('Limestone floor tile', (-6+i, -3.5+j, 0.345), (0.987, 0.987, 0.16), stone, 0.008)
for i in range(3):
    box('Broad entry step', (0, -4.55-i*0.38, 0.26-i*0.09), (6, 0.8, 0.16), stone, 0.025)

# A shallow barrel vault rises at its center and lifts gently toward the rear.
def height(x, y):
    return 4.25 + 1.05*(1-(x/7.0)**2) + 0.12*math.sin(y*math.pi/9)

nx, ny = 64, 20
verts = []
for j in range(ny+1):
    y = -4.8 + 9.6*j/ny
    for i in range(nx+1):
        x = -7 + 14*i/nx
        verts.append((x, y, height(x, y)))
faces = []
for j in range(ny):
    for i in range(nx):
        a = j*(nx+1)+i
        faces.append((a, a+1, a+nx+2, a+nx+1))
mesh = bpy.data.meshes.new('Curved roof shell mesh')
mesh.from_pydata(verts, [], faces)
mesh.update()
roof = bpy.data.objects.new('Continuous curved canopy', mesh)
bpy.context.collection.objects.link(roof)
roof.data.materials.append(roofmat)
roof.data.materials.append(wood)
for p in mesh.polygons:
    p.use_smooth = True
solid = roof.modifiers.new('Roof thickness', 'SOLIDIFY')
solid.thickness = 0.18
solid.offset = -1
solid.material_offset = 1
solid.material_offset_rim = 0
bevel = roof.modifiers.new('Rounded fascia edge', 'BEVEL')
bevel.width = 0.028
bevel.segments = 3

for y in (-3.35, 0, 3.35):
    curve('Exposed curved support rib', [(x, y, height(x, y)-0.23) for x in [-6.5+i*13/96 for i in range(97)]], 0.085, wood)
    for x in (-5.6, 5.6):
        top = height(x, y)-0.22
        rod('Slender bronze column', (x, y, 0.43), (x, y, top), 0.085, metal)
        box('Column baseplate', (x, y, 0.46), (0.28, 0.28, 0.06), metal, 0.015)
        box('Column headplate', (x, y, top), (0.3, 0.3, 0.08), metal, 0.015)
for i in range(57):
    x = -6.8+i*13.6/56
    curve('Cedar soffit batten', [(x, y, height(x, y)-0.205) for y in [-4.65+j*9.3/24 for j in range(25)]], 0.025, wood)
for x in (-7, 7):
    curve('Canopy edge flashing', [(x, y, height(x, y)-0.04) for y in [-4.8+j*9.6/40 for j in range(41)]], 0.045, roofmat)

for x in (-3.1, 3.1):
    for y in (1.8, 2.3):
        box('Bench stone pedestal', (x, y, 0.66), (0.25, 0.27, 0.48), dark)
    for j in range(4):
        box('Bench cedar seat slat', (x, 1.75+j*0.18, 0.94), (2.4, 0.16, 0.12), wood, 0.025)
box('Pool stone surround', (0, 6.4, 0.08), (12.5, 2.6, 0.25), stone, 0.06)
box('Pool water inset', (0, 6.4, 0.216), (12.0, 2.1, 0.035), water, 0.02)
for x in (-8.4, 8.4):
    box('Planter vessel', (x, 1.7, 0.42), (1.4, 2.7, 0.85), stone, 0.07)
    box('Planter soil', (x, 1.7, 0.86), (1.2, 2.5, 0.045), soil, 0.01)
    for k in range(7):
        y = 0.7+k*0.32
        for s in (-1, 0, 1):
            rod('Ornamental grass blade', (x+s*0.22, y, 0.86), (x+s*0.38, y+0.1, 1.45+0.12*math.sin(k)), 0.022, grass)

world = bpy.data.worlds.new('Daylight')
bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.73, 0.81, 0.91, 1)
world.node_tree.nodes['Background'].inputs[1].default_value = 0.5
bpy.ops.object.light_add(type='SUN', location=(0, 0, 12))
bpy.context.object.rotation_euler = (0.5, -0.45, -0.5)
bpy.context.object.data.energy = 2.5
bpy.context.object.data.angle = 0.15
bpy.ops.object.light_add(type='AREA', location=(0, -5, 9))
bpy.context.object.data.energy = 1000
bpy.context.object.data.size = 10
bpy.ops.object.camera_add(location=(18, -22, 13))
cam = bpy.context.object
cam.rotation_euler = (Vector((0, 0, 2))-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 26
scene = bpy.context.scene
scene.camera = cam
scene.render.engine = 'CYCLES'
scene.cycles.samples = 64
scene.render.resolution_x = 1600
scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'AgX'
