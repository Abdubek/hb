import bpy
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.45):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = roughness
    return m

green = material('Enamel green tray', (0.09, 0.29, 0.12), 0.45)
frame = material('Galvanized steel frame', (0.36, 0.42, 0.44), 0.8)
rubber = material('Black tire and grips', (0.022, 0.025, 0.029), 0, 0.8)
hub = material('Cream painted wheel', (0.72, 0.67, 0.49), 0.5)
ground = material('Neutral ground', (0.29, 0.30, 0.27), 0, 0.85)

def rod(name, a, b, radius, mat, vertices=24):
    d = Vector(b) - Vector(a)
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius,
        depth=d.length, location=(Vector(a) + Vector(b)) / 2)
    o = bpy.context.object
    o.name = name
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    o.data.materials.append(mat)
    bevel = o.modifiers.new('Rounded edges', 'BEVEL')
    bevel.width = 0.008
    bevel.segments = 2
    o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def box(name, location, dimensions, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    o = bpy.context.object
    o.name = name
    o.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    b = o.modifiers.new('Soft edges', 'BEVEL')
    b.width = 0.015
    b.segments = 2
    o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

# Tray points run counterclockwise; the wheel is at negative X.
bottom = [(-0.74, -0.29, 0.84), (-0.58, -0.44, 0.84),
          (0.52, -0.44, 0.84), (0.69, -0.28, 0.84),
          (0.69, 0.28, 0.84), (0.52, 0.44, 0.84),
          (-0.58, 0.44, 0.84), (-0.74, 0.29, 0.84)]
rim = [(-1.15, -0.40, 1.43), (-0.90, -0.66, 1.40),
       (0.76, -0.66, 1.35), (0.98, -0.43, 1.35),
       (0.98, 0.43, 1.35), (0.76, 0.66, 1.35),
       (-0.90, 0.66, 1.40), (-1.15, 0.40, 1.43)]
faces = [tuple(reversed(range(8)))]
for i in range(8):
    j = (i + 1) % 8
    faces.append((i, j, j + 8, i + 8))
mesh = bpy.data.meshes.new('Open tray shell mesh')
mesh.from_pydata(bottom + rim, [], faces)
mesh.update()
tray = bpy.data.objects.new('Deep open tapered tray', mesh)
bpy.context.collection.objects.link(tray)
tray.data.materials.append(green)
solid = tray.modifiers.new('Sheet steel thickness', 'SOLIDIFY')
solid.thickness = 0.025
bevel = tray.modifiers.new('Pressed tray corners', 'BEVEL')
bevel.width = 0.045
bevel.segments = 3
tray.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
for i in range(8):
    rod('Rolled tray lip %d' % i, rim[i], rim[(i + 1) % 8], 0.025, green)

# Twin rails continue behind the tray as lifting handles.
for side in [-1, 1]:
    y = side * 0.37
    points = [(-1.04, y, 0.38), (-0.69, y, 0.74),
              (0.57, y, 0.78), (1.67, side * 0.49, 1.07)]
    for i in range(len(points) - 1):
        rod('Frame rail %s segment %d' % (side, i), points[i], points[i + 1], 0.043, frame)
    rod('Handle grip %s' % side, (1.43, side * 0.464, 1.007),
        (1.83, side * 0.507, 1.112), 0.057, rubber)
    # Flat-bottomed U supports keep the parked wheelbarrow level.
    leg = [(0.29, y, 0.77), (0.40, y, 0.075),
           (0.80, y, 0.075), (0.65, y, 0.80)]
    for i in range(3):
        rod('Parking leg %s segment %d' % (side, i), leg[i], leg[i + 1], 0.035, frame)
    box('Support foot %s' % side, (0.60, y, 0.043), (0.44, 0.12, 0.055), frame)
    rod('Front tray brace %s' % side, (-1.04, y, 0.43), (-0.94, side * 0.49, 1.12), 0.028, frame)
    box('Tray saddle %s' % side, (-0.05, y, 0.803), (1.13, 0.11, 0.075), frame)
rod('Rear support crossbar', (0.55, -0.37, 0.25), (0.55, 0.37, 0.25), 0.028, frame)
rod('Front frame crossbar', (-0.58, -0.37, 0.74), (-0.58, 0.37, 0.74), 0.03, frame)

# One broad pneumatic tire centered on a transverse axle.
center = Vector((-1.04, 0, 0.38))
bpy.ops.mesh.primitive_torus_add(major_segments=40, minor_segments=16,
    location=center, major_radius=0.265, minor_radius=0.115)
tire = bpy.context.object
 tire_placeholder = None
