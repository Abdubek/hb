import bpy
from mathutils import Vector

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

shell = material('Ocean blue polycarbonate', (0.025, 0.27, 0.36), 0.25, 0.31)
ribs = material('Raised shell ribs', (0.04, 0.33, 0.42), 0.2)
black = material('Graphite rubber', (0.025, 0.03, 0.036), 0.0, 0.57)
zipper = material('Zipper tape', (0.055, 0.07, 0.08))
metal = material('Satin aluminum', (0.65, 0.70, 0.73), 0.85, 0.23)
badge = material('Warm silver badge', (0.75, 0.69, 0.53), 0.7)
floor = material('Studio floor', (0.37, 0.40, 0.43))

def box(name, location, dimensions, mat, bevel=0.04):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    o = bpy.context.object
    o.name = name
    o.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        mod = o.modifiers.new('Rounded manufactured edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 4
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def rod(name, a, b, radius, mat):
    a, b = Vector(a), Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=radius,
                                      depth=(b-a).length, location=(a+b)/2)
    o = bpy.context.object
    o.name = name
    o.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    o.data.materials.append(mat)
    mod = o.modifiers.new('Rounded cylinder edges', 'BEVEL')
    mod.width = 0.018
    mod.segments = 3
    o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

# Two molded halves meet at the narrow zipper band around the case.
box('Central zipper band', (0, 0, 1.66), (1.95, 0.085, 2.48), zipper, 0.04)
box('Front molded shell', (0, -0.22, 1.66), (1.92, 0.42, 2.48), shell, 0.17)
box('Rear molded shell', (0, 0.22, 1.66), (1.92, 0.42, 2.48), shell, 0.17)
for y in (-0.434, 0.434):
    for i in range(7):
        x = (i-3)*0.205
        box('Molded vertical reinforcing rib', (x, y, 1.63), (0.065, 0.04, 1.83), ribs, 0.019)

# Protective caps on the eight shell corners.
for x in (-0.82, 0.82):
    for y in (-0.32, 0.32):
        for z in (0.56, 2.76):
            box('Protective corner bumper', (x, y, z), (0.32, 0.27, 0.34), black, 0.09)
            face_y = y + (-0.143 if y < 0 else 0.143)
            rod('Bumper fixing rivet', (x, face_y-0.009, z), (x, face_y+0.009, z), 0.024, metal)

for x in (-0.73, 0.73):
    for y in (-0.27, 0.27):
        rod('Spinner swivel', (x, y, 0.31), (x, y, 0.47), 0.075, metal)
        box('Spinner wheel housing', (x, y, 0.27), (0.25, 0.20, 0.22), black, 0.05)
        for dx in (-0.105, 0.105):
            rod('Spinner rubber tire', (x+dx-0.04, y, 0.17),
                (x+dx+0.04, y, 0.17), 0.17, black)
        rod('Spinner aluminum axle', (x-0.15, y, 0.17), (x+0.15, y, 0.17), 0.065, metal)

for x in (-0.46, 0.46):
    box('Telescopic handle socket', (x, 0.26, 2.83), (0.21, 0.20, 0.20), black, 0.055)
    box('Lower telescopic rail', (x, 0.26, 3.20), (0.10, 0.105, 0.84), metal, 0.022)
    box('Upper telescopic rail', (x, 0.26, 3.82), (0.075, 0.08, 0.68), metal, 0.017)
    box('Rail sleeve collar', (x, 0.26, 3.59), (0.12, 0.12, 0.065), black, 0.02)
box('Extended trolley handle grip', (0, 0.26, 4.17), (1.13, 0.23, 0.19), black, 0.085)
box('Handle release button', (0, 0.26, 4.267), (0.24, 0.11, 0.025), metal, 0.012)
for x in (-0.29, 0.29):
    box('Top carry handle anchor', (x, -0.18, 2.91), (0.14, 0.16, 0.08), metal, 0.03)
    box('Top carry handle riser', (x, -0.18, 3.0), (0.09, 0.13, 0.19), black)
box('Top carry handle', (0, -0.18, 3.08), (0.66, 0.14, 0.105), black, 0.047)
for z in (1.40, 1.93):
    box('Side handle anchor', (0.97, 0, z), (0.09, 0.18, 0.14), metal)
    box('Side handle riser', (1.04, 0, z), (0.17, 0.11, 0.09), black)
box('Side carry handle', (1.115, 0, 1.665), (0.10, 0.13, 0.61), black, 0.045)
box('Recessed combination lock', (0.987, 0, 2.39), (0.06, 0.16, 0.34), black, 0.025)
for z in (2.31, 2.39, 2.47):
    box('Lock number dial', (1.022, 0, z), (0.018, 0.09, 0.038), metal, 0.009)
for z in (2.14, 2.22):
    box('Zipper pull tab', (0.99, -0.025, z), (0.04, 0.07, 0.15), metal, 0.017)
box('Front brand plaque', (0, -0.469, 2.49), (0.34, 0.025, 0.13), badge, 0.025)
box('Ground', (0, 0, -0.07), (200, 200, 0.14), floor, 0)

bpy.ops.object.camera_add(location=(5.2, -7.7, 4.8))
camera = bpy.context.object
camera.name = 'Suitcase presentation camera'
camera.rotation_euler = (Vector((0, 0, 2.1))-camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 5.25
bpy.context.scene.camera = camera
for position, power, size in [((0, -4, 7), 1100, 5), ((-4, 2, 5), 950, 4)]:
    bpy.ops.object.light_add(type='AREA', location=position)
    light = bpy.context.object
    light.data.energy = power
    light.data.size = size
    light.rotation_euler = (Vector((0, 0, 2))-light.location).to_track_quat('-Z', 'Y').to_euler()
scene = bpy.context.scene
scene.world = bpy.data.worlds.new('Soft studio world')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.45
scene.render.resolution_x = 900
scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100
