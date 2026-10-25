import bpy, math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def mat(name, color, metallic=0, roughness=0.45):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    return m

def finish(o, name, m, bevel=0):
    o.name = name
    o.data.materials.append(m)
    if bevel:
        mod = o.modifiers.new('Edge radii', 'BEVEL')
        mod.width = bevel
        mod.segments = 4
        o.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    return o

def box(name, loc, dim, m, bevel=0.02):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.dimensions = dim
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(o, name, m, bevel)

def rod(name, a, b, r, m, vertices=32):
    a, b = Vector(a), Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=r, depth=(b-a).length, location=(a+b)/2)
    o = bpy.context.object
    o.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    for p in o.data.polygons:
        p.use_smooth = len(p.vertices) == 4
    return finish(o, name, m, 0.004)

def path(name, coords, radius, m, cyclic=False):
    c = bpy.data.curves.new(name, 'CURVE')
    c.dimensions = '3D'
    c.bevel_depth = radius
    c.bevel_resolution = 3
    s = c.splines.new('POLY')
    s.points.add(len(coords)-1)
    for p, co in zip(s.points, coords):
        p.co = (*co, 1)
    s.use_cyclic_u = cyclic
    o = bpy.data.objects.new(name, c)
    bpy.context.collection.objects.link(o)
    c.materials.append(m)
    return o

shell = mat('Petrol blue polycarbonate', (0.022, 0.22, 0.30), 0.26, 0.3)
ribmat = mat('Raised shell ribs', (0.035, 0.29, 0.37), 0.24, 0.32)
rubber = mat('Charcoal bumpers', (0.022, 0.029, 0.035), 0, 0.65)
zipmat = mat('Zipper tape', (0.055, 0.064, 0.072), 0, 0.8)
aluminum = mat('Anodized aluminum', (0.52, 0.58, 0.62), 0.85, 0.24)
metal = mat('Dark metal hardware', (0.115, 0.14, 0.16), 0.7, 0.28)
accent = mat('Orange brand accent', (0.95, 0.28, 0.045), 0.15, 0.4)
cream = mat('Brand lettering', (0.88, 0.92, 0.91), 0.1, 0.5)
floormat = mat('Studio floor', (0.17, 0.20, 0.23), 0, 0.72)
box('Floor', (0, 0, -0.065), (200, 200, 0.1), floormat, 0)
# Upright suitcase shell, centered at z=0.97, front facing -Y.
box('Rear molded shell', (0, 0.165, 0.99), (1.06, 0.32, 1.46), shell, 0.115)
box('Front molded shell', (0, -0.165, 0.99), (1.06, 0.32, 1.46), shell, 0.115)
box('Central zipper gusset', (0, 0, 0.99), (1.055, 0.053, 1.45), zipmat, 0.10)
# Rounded rectangular zipper track in the XZ plane.
track = []
for cx, cz, start in [(0.42, 1.605, 0), (-0.42, 1.605, 90), (-0.42, 0.375, 180), (0.42, 0.375, 270)]:
    for i in range(13):
        a = math.radians(start+i*90/12)
        track.append((cx+0.106*math.cos(a), 0, cz+0.106*math.sin(a)))
path('Continuous metallic zipper coil', track, 0.0065, aluminum, True)
# Tactile vertical ribs on both broad faces.
for side in [-1, 1]:
    for i in range(-3, 4):
        x = i*0.119
        h = 1.07-0.055*abs(i)
        box('Molded vertical rib', (x, side*0.327, 0.99), (0.044, 0.027, h), ribmat, 0.020)
# Eight thick wraparound corner protectors with visible screw heads.
for x in [-0.455, 0.455]:
    for y in [-0.265, 0.265]:
        for z in [0.345, 1.635]:
            box('Rubber corner bumper', (x, y, z), (0.18, 0.17, 0.19), rubber, 0.055)
            sy = -1 if y < 0 else 1
            rod('Bumper screw', (x, y+sy*0.081, z), (x, y+sy*0.091, z), 0.013, metal, 16)
# Four twin-wheel spinner units beneath the case.
for x in [-0.385, 0.385]:
    for y in [-0.215, 0.215]:
        rod('Caster pivot', (x, y, 0.19), (x, y, 0.29), 0.052, metal)
        box('Caster fork', (x, y+0.014, 0.155), (0.065, 0.115, 0.16), rubber, 0.027)
        for s in [-1, 1]:
            wx = x+s*0.052
            rod('Spinner tire', (wx-0.023, y+0.02, 0.10), (wx+0.023, y+0.02, 0.10), 0.10, rubber)
            rod('Spinner hub', (wx-0.025, y+0.02, 0.10), (wx+0.025, y+0.02, 0.10), 0.052, aluminum)
# Extended twin-stage trolley handle mounted to the rear.
for x in [-0.235, 0.235]:
    box('Telescopic rail guide', (x, 0.225, 1.68), (0.11, 0.12, 0.11), rubber, 0.02)
    box('Lower telescoping rail', (x, 0.225, 1.935), (0.050, 0.054, 0.51), aluminum, 0.009)
    box('Upper telescoping rail', (x, 0.225, 2.285), (0.038, 0.042, 0.31), aluminum, 0.006)
    box('Rail collar', (x, 0.225, 2.175), (0.063, 0.066, 0.045), metal, 0.008)
    rod('Rail detent', (x, 0.195, 2.13), (x, 0.19, 2.13), 0.008, metal, 16)
box('Trolley hand grip', (0, 0.225, 2.465), (0.61, 0.13, 0.105), rubber, 0.044)
box('Handle release button', (0, 0.215, 2.523), (0.15, 0.07, 0.018), accent, 0.008)
# Separate short top carry handle.
for x in [-0.17, 0.17]:
    box('Top carry handle mount', (x, -0.065, 1.726), (0.095, 0.10, 0.04), metal, 0.015)
path('Top carry handle', [(-0.17, -0.065, 1.742), (-0.14, -0.065, 1.82), (-0.105, -0.065, 1.835), (0.105, -0.065, 1.835), (0.14, -0.065, 1.82), (0.17, -0.065, 1.742)], 0.027, rubber)
# Side carry handle, two zipper pulls and a combination lock.
for z in [0.91, 1.23]:
    box('Side handle mount', (0.537, 0, z), (0.044, 0.115, 0.08), metal, 0.012)
path('Side carry handle', [(0.555, 0, 0.92), (0.615, 0, 0.96), (0.63, 0, 1.18), (0.555, 0, 1.23)], 0.025, rubber)
box('Combination lock body', (0.539, 0, 1.46), (0.036, 0.17, 0.21), metal, 0.015)
for z in [1.41, 1.46, 1.51]:
    rod('Combination dial', (0.555, -0.026, z), (0.555, 0.026, z), 0.025, aluminum, 20)
    box('Dial index mark', (0.581, -0.005, z), (0.003, 0.012, 0.005), rubber, 0)
for z in [1.32, 1.37]:
    path('Zipper pull loop', [(0.545, -0.012, z), (0.59, -0.012, z-0.025), (0.60, 0.016, z-0.028), (0.552, 0.016, z)], 0.006, aluminum, True)
box('Front brand badge', (0, -0.351, 1.39), (0.225, 0.022, 0.085), metal, 0.018)
curve = bpy.data.curves.new('Brand label', 'FONT')
curve.body = 'N O M A D'
curve.align_x = 'CENTER'
curve.align_y = 'CENTER'
curve.size = 0.025
curve.extrude = 0.0005
o = bpy.data.objects.new('NOMAD badge lettering', curve)
bpy.context.collection.objects.link(o)
o.location = (0, -0.364, 1.39)
o.rotation_euler = (math.pi/2, 0, 0)
curve.materials.append(cream)

scene = bpy.context.scene
scene.world = scene.world or bpy.data.worlds.new('World')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.25, 0.31, 0.38, 1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.42
for loc, energy, size in [((3, -4, 5), 900, 4), ((-3, -1, 3), 600, 3), ((1, 3, 4), 1100, 3)]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    o = bpy.context.object
    o.data.energy = energy
    o.data.size = size
    o.rotation_euler = (Vector((0, 0, 1.15))-o.location).to_track_quat('-Z', 'Y').to_euler()
bpy.ops.object.camera_add(location=(3.5, -6, 3.15))
cam = bpy.context.object
cam.rotation_euler = (Vector((0, 0, 1.25))-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 3.15
scene.camera = cam
scene.render.resolution_x = 1000
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
