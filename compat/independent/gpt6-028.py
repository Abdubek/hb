import bpy
import math
from mathutils import Vector

# Freestanding articulated reading lamp with an open metal shade.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.4):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    return m

paint = material('Mustard enamel', (0.65, 0.31, 0.045), 0.35, 0.28)
steel = material('Brushed steel', (0.34, 0.37, 0.40), 0.85, 0.27)
black = material('Black rubber and controls', (0.025, 0.029, 0.032), roughness=0.65)
inside = material('Ivory shade interior', (0.87, 0.83, 0.70), 0.12, 0.35)
bulb_mat = material('Warm frosted bulb', (1.0, 0.85, 0.58), roughness=0.3)
bulb_bsdf = bulb_mat.node_tree.nodes.get('Principled BSDF')
bulb_bsdf.inputs['Emission Color'].default_value = (1, 0.72, 0.35, 1)
bulb_bsdf.inputs['Emission Strength'].default_value = 1.5
floor_mat = material('Neutral floor', (0.28, 0.30, 0.31), roughness=0.85)

def rod(name, start, end, radius, mat, bevel=0.004):
    a, b = Vector(start), Vector(end)
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius,
                                      depth=(b-a).length, location=(a+b)/2)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Soft machined edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    for face in obj.data.polygons:
        face.use_smooth = len(face.vertices) == 4
    return obj

def cable(name, points, radius, mat):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = radius
    curve.bevel_resolution = 3
    spline = curve.splines.new('BEZIER')
    spline.bezier_points.add(len(points)-1)
    for point, co in zip(spline.bezier_points, points):
        point.co = co
        point.handle_left_type = 'AUTO'
        point.handle_right_type = 'AUTO'
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj

def joint(name, point, radius):
    p = Vector(point)
    rod(name + ' pivot housing', p+Vector((0, -0.052, 0)),
        p+Vector((0, 0.052, 0)), radius, paint)
    rod(name + ' locking knob', p+Vector((0, -0.09, 0)),
        p+Vector((0, -0.055, 0)), radius*0.63, black)
    rod(name + ' axle cap', p+Vector((0, 0.052, 0)),
        p+Vector((0, 0.059, 0)), radius*0.42, steel, 0.002)

rod('Base rubber foot', (0, 0, 0.012), (0, 0, 0.035), 0.32, black)
rod('Heavy circular weighted base', (0, 0, 0.03), (0, 0, 0.10), 0.34, paint, 0.015)
rod('Base mast socket', (0, 0, 0.09), (0, 0, 0.19), 0.065, steel)
rod('Upright column', (0, 0, 0.13), (0, 0, 1.34), 0.025, paint)
rod('Height adjustment collar', (0, 0, 1.12), (0, 0, 1.20), 0.036, steel)
rod('Collar thumbscrew', (0, -0.028, 1.16), (0, -0.075, 1.16), 0.019, black)
shoulder = Vector((0, 0, 1.34))
elbow = Vector((0.42, 0, 1.98))
head = Vector((0.91, 0, 1.80))
rod('Rising adjustable arm', shoulder, elbow, 0.023, paint)
rod('Forward adjustable arm', elbow, head, 0.021, paint)
joint('Shoulder', shoulder, 0.066)
joint('Elbow', elbow, 0.057)
joint('Shade tilt', head, 0.045)
cable('Exposed flexible elbow wire', [(0.32, 0.035, 1.84), (0.34, 0.055, 2.04),
                                     (0.48, 0.055, 2.05), (0.55, 0.035, 1.94)], 0.009, black)

axis = Vector((0.22, 0, -1)).normalized()
rotation = axis.to_track_quat('Z', 'Y')
shade_top = head + axis*0.06
rod('Shade neck', head, shade_top+axis*0.018, 0.025, steel)
# Four rings form an outer wall, rolled lip, inner wall and rear annulus.
segments = 48
rings = [(0.064, 0), (0.205, 0.245), (0.197, 0.245), (0.056, 0)]
vertices = []
for radius, z in rings:
    for i in range(segments):
        angle = 2*math.pi*i/segments
        local = Vector((radius*math.cos(angle), radius*math.sin(angle), z))
        vertices.append(tuple(shade_top + rotation @ local))
faces = []
for ring in range(4):
    following = (ring+1) % 4
    for i in range(segments):
        j = (i+1) % segments
        faces.append((ring*segments+i, ring*segments+j,
                      following*segments+j, following*segments+i))
mesh = bpy.data.meshes.new('Hollow spun shade mesh')
mesh.from_pydata(vertices, [], faces)
mesh.update()
shade = bpy.data.objects.new('Open flared metal shade', mesh)
bpy.context.collection.objects.link(shade)
mesh.materials.append(paint)
mesh.materials.append(inside)
for face in mesh.polygons:
    face.material_index = 1 if face.index // segments == 2 else 0
    face.use_smooth = face.index // segments in (0, 2)
rod('Shade rear cap', shade_top-axis*0.005, shade_top+axis*0.008, 0.064, paint)
rod('Bulb socket', shade_top+axis*0.01, shade_top+axis*0.085, 0.037, black)
bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=0.057,
                                    location=shade_top+axis*0.133)
bulb = bpy.context.object
bulb.name = 'Recessed frosted bulb'
bulb.data.materials.append(bulb_mat)
for face in bulb.data.polygons:
    face.use_smooth = True
cable('Power cord on floor', [(0, 0.28, 0.05), (0.08, 0.44, 0.012),
                             (0.45, 0.54, 0.012), (0.62, 0.80, 0.012)], 0.009, black)
rod('Inline foot switch', (0.31, 0.52, 0.013), (0.31, 0.52, 0.043), 0.056, black)
bpy.ops.mesh.primitive_plane_add(size=200)
bpy.context.object.name = 'Floor'
bpy.context.object.data.materials.append(floor_mat)
bpy.ops.object.camera_add(location=(3.1, -4.8, 2.7))
camera = bpy.context.object
camera.name = 'Lamp presentation camera'
camera.rotation_euler = (Vector((0.35, 0, 1.03))-camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 2.75
bpy.context.scene.camera = camera
bpy.ops.object.light_add(type='AREA', location=(0, -3, 4))
bpy.context.object.name = 'Studio softbox'
bpy.context.object.data.energy = 500
bpy.context.object.data.size = 4
bpy.context.scene.world.color = (0.22, 0.22, 0.22)
bpy.context.scene.render.resolution_x = 900
bpy.context.scene.render.resolution_y = 1100
bpy.context.scene.render.resolution_percentage = 100
