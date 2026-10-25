import bpy
import math
from mathutils import Vector

# Tiny cottage; front faces negative Y.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Roughness'].default_value = 0.65
    bs.inputs['Metallic'].default_value = metallic
    return m

sage = material('Sage painted siding', (0.32, 0.46, 0.37))
cream = material('Warm ivory trim', (0.88, 0.84, 0.70))
roofmat = material('Charcoal standing seam roof', (0.09, 0.13, 0.16), 0.45)
wood = material('Honey cedar', (0.43, 0.24, 0.10))
brick = material('Chimney brick', (0.40, 0.16, 0.10))
stone = material('Foundation concrete', (0.40, 0.41, 0.38))
glass = material('Blue window glass', (0.12, 0.29, 0.36), 0.35)
black = material('Dark hardware and flue', (0.035, 0.04, 0.04), 0.35)
ground = material('Ground', (0.27, 0.32, 0.24))

def box(name, loc, scale, mat, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        mod = o.modifiers.new('Soft edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def beam(name, a, b, width, depth, mat):
    delta = Vector(b) - Vector(a)
    o = box(name, (Vector(a) + Vector(b)) / 2, (width, depth, delta.length), mat)
    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = delta.to_track_quat('Z', 'Y')
    return o

box('Landscape plinth', (0, -0.6, -0.14), (9, 10, 0.25), ground, 0.08)
box('Concrete foundation', (0, 0, 0.23), (4.15, 4.15, 0.46), stone, 0.04)
box('House walls', (0, 0, 1.66), (4, 4, 2.42), sage)
verts = [(-2,-2,2.87),(2,-2,2.87),(0,-2,4.05),
         (-2,2,2.87),(2,2,2.87),(0,2,4.05)]
mesh = bpy.data.meshes.new('Gable mesh')
mesh.from_pydata(verts, [], [(0,1,2),(5,4,3),(0,3,4,1),(1,4,5,2),(2,5,3,0)])
mesh.update()
gable = bpy.data.objects.new('Solid gabled attic', mesh)
bpy.context.collection.objects.link(gable)
gable.data.materials.append(sage)
# Separate thin boards express horizontal clapboard siding.
for i in range(13):
    z = 0.54 + i * 0.18
    box('Front siding course %02d' % i, (0,-2.012,z), (4,0.025,0.025), cream)
    for x in (-2.012, 2.012):
        box('Side siding course', (x,0,z), (0.025,4,0.025), sage)
for x in (-1.95, 1.95):
    for y in (-2.04, 2.04):
        box('Corner trim', (x,y,1.67), (0.14,0.12,2.44), cream)
# Roof slope follows the gable, extending beyond all walls.
slope = 1.18 / 2
for side in (-1, 1):
    panel = box('Pitched roof plane', (side*1.17,0,4.05-1.17*slope),
                (2.34*math.sqrt(1+slope*slope),4.65,0.12), roofmat)
    panel.rotation_euler[1] = side * math.atan(slope)
    for y in (-2.34, 2.34):
        beam('Gable fascia', (0,y,4.10), (side*2.38,y,2.70), 0.13,0.14,cream)
    for j in range(10):
        y = -2.2 + j*0.49
        beam('Raised roof seam', (0,y,4.13), (side*2.34,y,2.75), 0.025,0.025,roofmat)
box('Ridge cap', (0,0,4.13), (0.16,4.7,0.10), roofmat, 0.035)
box('Front door surround', (-0.72,-2.075,1.47), (1.05,0.13,2.08), cream)
box('Cedar front door', (-0.72,-2.155,1.44), (0.86,0.08,1.93), wood, 0.015)
box('Door upper glass', (-0.72,-2.205,1.91), (0.56,0.025,0.62), glass)
box('Door handle', (-0.40,-2.23,1.30), (0.045,0.08,0.16), black, 0.015)

def window(name, center, side=False):
    x,y,z = center
    def piece(label, dx, dz, w, h, depth, mat):
        loc = (x+depth,y+dx,z+dz) if side else (x+dx,y-depth,z+dz)
        size = (0.07,w,h) if side else (w,0.07,h)
        box(name+' '+label, loc, size, mat)
    piece('trim backing',0,0,1.25,1.18,0,cream)
    piece('glass',0,0,1.06,0.99,0.05,glass)
    piece('vertical mullion',0,0,0.055,1.04,0.10,cream)
    piece('horizontal mullion',0,0,1.1,0.055,0.10,cream)
    piece('projecting sill',0,-0.60,1.36,0.09,0.12,cream)
window('Front window',(0.92,-2.075,1.81))
window('Right window',(2.075,0.15,1.76),True)
box('Porch rim', (0,-2.88,0.32), (4.45,1.80,0.25), wood)
for i in range(12):
    box('Porch deck board %02d' % i, (0,-2.07-i*0.145,0.48), (4.45,0.135,0.10), wood,0.008)
for x in (-2.1,2.1):
    for y in (-2.18,-3.63):
        box('Porch post',(x,y,1.07),(0.13,0.13,1.20),cream,0.01)
    box('Side handrail',(x,-2.90,1.63),(0.16,1.60,0.12),cream,0.015)
    for j in range(6):
        box('Side baluster',(x,-2.27-j*0.25,1.06),(0.055,0.055,0.96),cream)
box('Lower entrance step',(-0.72,-4.19,0.10),(1.55,0.58,0.20),stone,0.02)
box('Upper entrance step',(-0.72,-3.91,0.24),(1.55,0.42,0.28),wood,0.02)
box('Brick chimney',(1.05,0.90,3.97),(0.58,0.65,1.75),brick,0.015)
for i in range(6):
    box('Chimney mortar band',(1.05,0.90,4.05+i*0.13),(0.59,0.66,0.02),stone)
box('Chimney cap',(1.05,0.90,4.88),(0.76,0.82,0.12),stone,0.025)
box('Flue opening',(1.05,0.90,4.948),(0.38,0.43,0.015),black)
for i in range(3):
    box('Path stepping stone',(-0.72,-4.75-i*0.65,0.015),(1.1,0.46,0.055),stone,0.03)
bpy.ops.object.camera_add(location=(8,-11,7))
cam = bpy.context.object
cam.name = 'Cottage presentation camera'
cam.rotation_euler = (Vector((0,-0.6,1.8))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 10.5
bpy.context.scene.camera = cam
bpy.ops.object.light_add(type='AREA', location=(2,-5,9))
bpy.context.object.data.energy = 1500
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 7
bpy.context.scene.world.color = (0.35,0.35,0.35)
