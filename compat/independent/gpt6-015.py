import bpy
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.5):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Metallic'].default_value = metallic
    shader.inputs['Roughness'].default_value = roughness
    return mat

stucco = material('Warm ivory stucco', (0.73, 0.65, 0.51))
stone = material('Pale limestone trim', (0.9, 0.85, 0.73))
metal = material('Graphite powder coated metal', (0.065, 0.085, 0.095), 0.7, 0.3)
glass = material('Blue reflective glazing', (0.08, 0.22, 0.29), 0.55, 0.16)
wood = material('Walnut entrance', (0.24, 0.105, 0.045))
paving = material('Concrete paving', (0.34, 0.36, 0.37))
soil = material('Planter soil', (0.07, 0.04, 0.02))
green = material('Clipped green shrubs', (0.12, 0.25, 0.075))

def box(name, location, size, mat, bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Small edge bevel', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    return obj

def framed_opening(name, x, bottom, width, height):
    # The facade faces negative Y; glazing is layered ahead of its solid backing.
    z = bottom + height / 2
    box(name + ' dark recess', (x, -2.035, z), (width + 0.22, 0.10, height + 0.18), metal)
    box(name + ' glazing', (x, -2.10, z), (width, 0.045, height), glass, 0.005)
    for dx in (-width / 2, 0, width / 2):
        box(name + ' vertical frame', (x + dx, -2.15, z), (0.065, 0.10, height + 0.08), metal, 0.008)
    for dz in (-height / 2, height / 2):
        box(name + ' horizontal frame', (x, -2.15, z + dz), (width + 0.10, 0.10, 0.075), metal, 0.008)
    box(name + ' sill', (x, -2.23, bottom - 0.07), (width + 0.35, 0.42, 0.12), stone)

def balcony(name, x, level):
    width = 2.55
    box(name + ' cantilever slab', (x, -2.77, level), (width + 0.20, 1.70, 0.20), stone)
    rail_z = level + 1.16
    box(name + ' front handrail', (x, -3.53, rail_z), (width, 0.075, 0.075), metal, 0.012)
    box(name + ' front lower rail', (x, -3.53, level + 0.26), (width, 0.05, 0.05), metal, 0.008)
    for i in range(13):
        px = x - width / 2 + width * i / 12
        box(name + ' front baluster %02d' % i, (px, -3.53, level + 0.66), (0.04, 0.045, 1.00), metal, 0.006)
    for side in (-1, 1):
        sx = x + side * width / 2
        box(name + ' side handrail', (sx, -2.79, rail_z), (0.075, 1.55, 0.075), metal, 0.01)
        for j in range(1, 6):
            box(name + ' side baluster', (sx, -3.53 + j * 0.25, level + 0.66), (0.04, 0.04, 1.0), metal, 0.005)

box('Sidewalk plinth', (0, -0.45, -0.15), (12.8, 9.3, 0.3), paving)
box('Three story building mass', (0, 0, 4.65), (10.6, 4.0, 9.3), stucco, 0.06)
box('Ground floor stone base', (0, -2.055, 0.25), (10.7, 0.16, 0.50), stone)
for x in (-5.18, 5.18):
    box('Facade corner pilaster', (x, -2.10, 4.65), (0.28, 0.23, 9.3), stone)
for z in (3.1, 6.2, 9.3):
    box('Floor string course', (0, -2.11, z), (10.85, 0.30, 0.18), stone)
box('Projecting roof cornice', (0, 0, 9.47), (11.05, 4.45, 0.22), stone)
box('Flat roof surface', (0, 0, 9.61), (10.5, 3.95, 0.08), metal)
for x in (-5.15, 5.15):
    box('Roof side parapet', (x, 0, 9.83), (0.20, 4.05, 0.42), stucco)
for y in (-1.95, 1.95):
    box('Roof parapet', (0, y, 9.83), (10.5, 0.20, 0.42), stucco)
for story in range(3):
    for bay, x in enumerate((-3.35, 0, 3.35)):
        if story == 0 and bay == 1:
            continue
        bottom = 0.80 if story == 0 else story * 3.1 + 0.20
        height = 1.85 if story == 0 else 2.45
        label = 'Floor %d bay %d' % (story + 1, bay + 1)
        framed_opening(label, x, bottom, 1.78, height)
        if story:
            balcony(label + ' balcony', x, story * 3.1 + 0.09)
box('Entrance stone surround', (0, -2.08, 1.43), (2.12, 0.23, 2.86), stone)
box('Entrance door', (0, -2.23, 1.38), (1.78, 0.12, 2.70), wood)
for x in (-0.43, 0.43):
    box('Entrance glazed inset', (x, -2.30, 1.67), (0.68, 0.035, 1.75), glass)
    box('Brass door pull', (x * 0.30, -2.37, 1.08), (0.035, 0.06, 0.37), metal, 0.01)
box('Entrance canopy', (0, -2.65, 2.91), (2.65, 1.35, 0.12), metal)
box('Entrance step', (0, -2.40, 0.065), (2.25, 0.85, 0.13), stone)
for x in (-1.8, 1.8):
    box('Entrance planter', (x, -2.65, 0.33), (0.65, 0.65, 0.66), stone)
    box('Visible soil', (x, -2.65, 0.665), (0.54, 0.54, 0.035), soil)
    box('Clipped shrub', (x, -2.65, 0.95), (0.64, 0.64, 0.55), green, 0.16)

scene = bpy.context.scene
scene.world.color = (0.25, 0.25, 0.25)
bpy.ops.object.light_add(type='AREA', location=(-6, -10, 15))
bpy.context.object.data.energy = 2200
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 8
bpy.ops.object.camera_add(location=(14, -22, 13))
camera = bpy.context.object
camera.name = 'Facade overview camera'
camera.rotation_euler = (Vector((0, -0.8, 4.7)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 18
scene.camera = camera
scene.render.resolution_x = 1200
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
