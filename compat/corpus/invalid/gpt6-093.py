import bpy, math
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)

def material(name, color, metallic=0, roughness=0.45):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    return m

def box(name, loc, dims, mat, bevel=0.012):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        b = o.modifiers.new('Edge finish', 'BEVEL')
        b.width = bevel
        b.segments = 3
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

stone = material('Warm limestone pedestal', (0.58, 0.54, 0.46), roughness=0.7)
metal = material('Dark bronze frame', (0.075, 0.052, 0.028), 0.8, 0.28)
felt = material('Exhibit suede', (0.095, 0.11, 0.10), roughness=0.95)
bronze = material('Artifact aged bronze', (0.20, 0.30, 0.22), 0.65, 0.48)
gold = material('Artifact raised bands', (0.46, 0.27, 0.085), 0.7, 0.38)
white = material('Label stock', (0.86, 0.83, 0.73), roughness=0.8)
ink = material('Label lettering', (0.055, 0.06, 0.052), roughness=0.6)
floor = material('Museum floor', (0.25, 0.28, 0.30), roughness=0.55)
glass = material('Clear low iron glass', (0.94, 0.99, 0.98), roughness=0.035)
p = glass.node_tree.nodes.get('Principled BSDF')
p.inputs['Transmission Weight'].default_value = 1
p.inputs['IOR'].default_value = 1.45

box('Gallery floor', (0, 0, -0.075), (12, 12, 0.15), floor)
box('Recessed toe plinth', (0, 0, 0.075), (1.12, 0.92, 0.15), metal)
box('Stone pedestal', (0, 0, 0.57), (1.25, 1.05, 0.90), stone, 0.025)
box('Upper shadow reveal', (0, 0, 1.028), (1.23, 1.03, 0.025), metal, 0.005)
box('Display base slab', (0, 0, 1.07), (1.34, 1.14, 0.065), stone)
box('Suede interior bed', (0, 0, 1.109), (1.22, 1.02, 0.018), felt, 0.003)

bottom, top = 1.12, 2.28
for x in [-0.65, 0.65]:
    box('Side glass panel', (x, 0, (bottom+top)/2), (0.008, 1.10, top-bottom), glass, 0.001)
for y in [-0.55, 0.55]:
    box('Front glass panel' if y < 0 else 'Rear glass door', (0, y, (bottom+top)/2), (1.292, 0.008, top-bottom), glass, 0.001)
box('Glass roof', (0, 0, top+0.004), (1.308, 1.108, 0.008), glass, 0.001)
for z in [bottom, top]:
    for y in [-0.55, 0.55]:
        box('Horizontal frame rail', (0, y, z), (1.34, 0.018, 0.024), metal, 0.003)
    for x in [-0.65, 0.65]:
        box('Side frame rail', (x, 0, z), (0.018, 1.10, 0.024), metal, 0.003)
for x in [-0.65, 0.65]:
    for y in [-0.55, 0.55]:
        box('Slim corner upright', (x, y, (top+bottom)/2), (0.016, 0.016, top-bottom), metal, 0.003)
for z in [1.36, 2.04]:
    box('Rear door hinge', (-0.651, 0.561, z), (0.038, 0.028, 0.085), metal, 0.005)
box('Door lock', (0.60, 0.567, 1.67), (0.047, 0.025, 0.055), metal, 0.008)

box('Artifact riser', (0, 0.075, 1.16), (0.53, 0.47, 0.085), metal)
# Revolved closed cross-section: exterior, rolled rim, interior and cavity floor.
profile = [(0,0), (0.13,0), (0.16,0.035), (0.115,0.085), (0.13,0.12), (0.23,0.22), (0.255,0.36), (0.225,0.46), (0.135,0.54), (0.115,0.66), (0.155,0.69), (0.16,0.715), (0.135,0.728), (0.113,0.697), (0.09,0.66), (0.109,0.535), (0.199,0.449), (0.228,0.357), (0.206,0.23), (0.104,0.14), (0,0.14)]
verts, faces = [], []
segments = 64
for r, z in profile:
    for j in range(segments):
        a = 2*math.pi*j/segments
        verts.append((r*math.cos(a), 0.075+r*math.sin(a), 1.205+z))
for i in range(len(profile)-1):
    for j in range(segments):
        k = (j+1) % segments
        faces.append((i*segments+j, i*segments+k, (i+1)*segments+k, (i+1)*segments+j))
mesh = bpy.data.meshes.new('Hollow urn mesh')
mesh.from_pydata(verts, [], faces)
mesh.update()
urn = bpy.data.objects.new('Bronze ceremonial urn', mesh)
bpy.context.collection.objects.link(urn)
urn.data.materials.append(bronze)
# Weld the coincident axial vertices into clean pole fans.
import bmesh
bm = bmesh.new()
bm.from_mesh(mesh)
bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=0.00001)
bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
bm.to_mesh(mesh)
bm.free()
for poly in mesh.polygons:
    poly.use_smooth = True
for z, r in [(1.255, 0.145), (1.45, 0.24), (1.665, 0.223), (1.905, 0.147)]:
    bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=0.009, major_segments=64, minor_segments=10, location=(0, 0.075, z))
    bpy.context.object.name = 'Urn decorative band'
    bpy.context.object.data.materials.append(gold)
for side in [-1, 1]:
    curve = bpy.data.curves.new('Urn handle curve', 'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = 0.018
    curve.bevel_resolution = 4
    spline = curve.splines.new('BEZIER')
    spline.bezier_points.add(3)
    for p, co in zip(spline.bezier_points, [(side*0.13,0.075,1.83),(side*0.31,0.075,1.81),(side*0.34,0.075,1.62),(side*0.23,0.075,1.52)]):
        p.co = co
        p.handle_left_type = 'AUTO'
        p.handle_right_type = 'AUTO'
    o = bpy.data.objects.new('Loop handle', curve)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(gold)

box('Museum caption plaque', (0, -0.534, 0.87), (0.65, 0.016, 0.17), white, 0.005)
bpy.ops.object.text_add(location=(-0.29, -0.545, 0.895), rotation=(math.pi/2, 0, 0))
t = bpy.context.object
t.name = 'Exhibit caption'
t.data.body = 'CEREMONIAL VESSEL\nBronze study  /  Collection 024'
t.data.size = 0.031
t.data.space_line = 1.35
t.data.extrude = 0.0003
t.data.materials.append(ink)

scene = bpy.context.scene
scene.world.color = (0.23, 0.23, 0.23)
for loc, power, size in [((2, -4, 5), 700, 4), ((-3, -1, 3), 450, 3), ((1, 3, 4), 600, 3)]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    o = bpy.context.object
    o.data.energy = power
    o.data.size = size
    o.rotation_euler = (Vector((0, 0, 1.3)) - o.location).to_track_quat('-Z', 'Y').to_euler()
bpy.ops.object.camera_add(location=(3.4, -5, 3.2))
camera = bpy.context.object
camera.rotation_euler = (Vector((0, 0, 1.15)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 3.25
scene.camera = camera
scene.render.engine = 'CYCLES'
scene.cycles.transmission_bounces = 12
scene.render.resolution_x = 1100
scene.render.resolution_y = 1400
scene.render.resolution_percentage = 100
