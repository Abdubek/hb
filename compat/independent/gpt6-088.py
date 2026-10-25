import bpy
import math
from mathutils import Vector

# Single-axle open utility trailer; front and hitch face negative X.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0, roughness=0.5):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color,1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color,1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = roughness
    return m

steel = material('Charcoal painted steel', (0.075,0.09,0.105), 0.7, 0.35)
zinc = material('Galvanized metal', (0.49,0.54,0.59), 0.8, 0.3)
wood = material('Pressure treated timber', (0.34,0.24,0.12), 0, 0.85)
wood_alt = material('Alternate timber boards', (0.41,0.30,0.16), 0, 0.85)
rubber = material('Black tire rubber', (0.022,0.026,0.032), 0, 0.88)
red = material('Red rear lamp lenses', (0.65,0.018,0.012), 0.15, 0.25)
amber = material('Amber side reflectors', (1,0.24,0.015), 0.15, 0.25)
ground = material('Neutral ground', (0.29,0.31,0.33))

def box(name, loc, dims, mat, bevel=0.015):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Fabricated edge rounding','BEVEL')
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return obj

def bar(name, a, b, width, height, mat):
    direction = Vector(b)-Vector(a)
    obj = box(name, (Vector(a)+Vector(b))/2, (width,height,direction.length), mat)
    obj.rotation_euler = direction.to_track_quat('Z','Y').to_euler()
    return obj

def cylinder(name, a, b, radius, mat, vertices=24):
    direction = Vector(b)-Vector(a)
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=direction.length, location=(Vector(a)+Vector(b))/2)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = direction.to_track_quat('Z','Y').to_euler()
    obj.data.materials.append(mat)
    for face in obj.data.polygons:
        face.use_smooth = len(face.vertices) == 4
    return obj

# Bed frame and longitudinal wood decking.
for y in [-0.94,0.94]:
    box('Main chassis side channel', (0,y,0.76), (3.8,0.10,0.18), steel)
for x in [-1.85,-0.95,0,0.95,1.85]:
    box('Underbed crossmember', (x,0,0.75), (0.09,1.8,0.13), steel)
for i in range(9):
    y = (i-4)*0.202
    box('Deck plank %02d' % (i+1), (0,y,0.88), (3.68,0.192,0.075), wood if i%2 else wood_alt, 0.005)
    for x in [-1.68,1.68]:
        cylinder('Deck carriage bolt', (x,y,0.916), (x,y,0.923), 0.017, zinc, 12)
for y in [-0.94,0.94]:
    box('Side top rail', (0,y,1.46), (3.8,0.065,0.065), steel)
    box('Side middle rail', (0,y,1.16), (3.8,0.045,0.045), steel)
    for x in [-1.86,0,1.86]:
        box('Side upright stake', (x,y,1.15), (0.065,0.065,0.62), steel)
for x, label in [(-1.86,'Front headboard'),(1.86,'Rear tailgate')]:
    for z in [1.0,1.45]:
        box(label+' horizontal rail', (x,0,z), (0.065,1.88,0.065), steel)
    for y in [-0.62,-0.31,0,0.31,0.62]:
        box(label+' vertical slat', (x,y,1.22), (0.04,0.035,0.43), steel, 0.005)
for y in [-0.65,0.65]:
    cylinder('Tailgate hinge barrel', (1.91,y-0.1,0.98), (1.91,y+0.1,0.98), 0.032, zinc)
    box('Tailgate latch', (1.91,y,1.42), (0.06,0.15,0.07), zinc)

# Axle, layered leaf springs, wheels, and angular mudguards.
cylinder('Continuous transverse axle', (0.35,-1.24,0.48), (0.35,1.24,0.48), 0.066, steel)
for side in [-1,1]:
    y = side*1.17
    for layer in range(3):
        box('Leaf spring layer', (0.35,side*0.74,0.55+layer*0.025), (1.12-layer*0.20,0.09,0.022), steel, 0.005)
    for x in [-0.21,0.91]:
        box('Suspension hanger', (x,side*0.74,0.64), (0.10,0.13,0.23), zinc)
    bpy.ops.mesh.primitive_torus_add(major_segments=40, minor_segments=12, location=(0.35,y,0.48), major_radius=0.345, minor_radius=0.13, rotation=(math.pi/2,0,0))
    tire = bpy.context.object
    tire.name = 'Left tire' if side < 0 else 'Right tire'
    tire.data.materials.append(rubber)
    for p in tire.data.polygons:
        p.use_smooth = True
    cylinder('Wheel rim', (0.35,y-0.115,0.48), (0.35,y+0.115,0.48), 0.255, zinc)
    outer = y+side*0.125
    cylinder('Recessed wheel center', (0.35,outer,0.48), (0.35,outer+side*0.014,0.48), 0.19, steel)
    cylinder('Hub dust cap', (0.35,outer,0.48), (0.35,outer+side*0.085,0.48), 0.085, zinc)
    for i in range(5):
        angle = i*math.tau/5
        x, z = 0.35+0.13*math.cos(angle), 0.48+0.13*math.sin(angle)
        cylinder('Hex wheel nut', (x,outer+side*0.017,z), (x,outer+side*0.044,z), 0.023, zinc, 6)
    box('Mudguard crown', (0.35,y,1.04), (0.82,0.41,0.045), zinc)
    for end in [-1,1]:
        bar('Sloped mudguard wing', (0.35+end*0.41,y,1.04), (0.35+end*0.66,y,0.66), 0.045,0.41,zinc)
    box('Rear rubber mudflap', (1.015,y,0.48), (0.028,0.36,0.35), rubber)
    box('Amber side marker', (-1.6,side*0.997,0.79), (0.16,0.022,0.075), amber)
    box('Rear lamp housing', (1.96,side*0.74,0.78), (0.12,0.28,0.16), rubber)
    box('Rear red lens', (2.025,side*0.74,0.78), (0.025,0.23,0.11), red)

# A-frame tongue, ball coupler, latch, and grounded parking jack.
for y in [-0.88,0.88]:
    bar('A-frame drawbar', (-1.82,y,0.73), (-3.23,0,0.73), 0.11,0.13,steel)
box('Tongue center tube', (-3.24,0,0.73), (0.78,0.14,0.14), steel)
box('Coupler socket housing', (-3.65,0,0.74), (0.46,0.23,0.18), zinc, 0.065)
box('Coupler latch pedestal', (-3.57,0,0.85), (0.11,0.09,0.07), steel)
bar('Coupler locking lever', (-3.70,0,0.90), (-3.43,0,0.93), 0.055,0.045,zinc)
cylinder('Tongue jack outer sleeve', (-2.75,0.22,0.38), (-2.75,0.22,0.95), 0.055, zinc)
cylinder('Tongue jack sliding leg', (-2.75,0.22,0.06), (-2.75,0.22,0.48), 0.038, steel)
box('Tongue jack footplate', (-2.75,0.22,0.045), (0.27,0.22,0.055), zinc)
box('Jack mounting bracket', (-2.75,0.10,0.73), (0.19,0.29,0.07), steel)
cylinder('Jack crank arm', (-2.75,0.22,0.98), (-2.75,0.40,0.98), 0.018, zinc)
cylinder('Jack crank grip', (-2.75,0.40,0.97), (-2.75,0.40,1.08), 0.028, rubber)
box('Ground', (0,0,-0.055), (200,200,0.1), ground, 0)
bpy.ops.object.camera_add(location=(-6.6,-6.5,4.8))
camera = bpy.context.object
camera.name = 'Trailer three-quarter camera'
camera.rotation_euler = (Vector((-0.8,0,0.7))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 7.4
bpy.context.scene.camera = camera
bpy.ops.object.light_add(type='AREA', location=(-3,-4,7))
bpy.context.object.data.energy = 1500
bpy.context.object.data.size = 5
bpy.context.scene.world.color = (0.3,0.3,0.3)
bpy.context.scene.render.resolution_x = 1200
bpy.context.scene.render.resolution_y = 850
bpy.context.scene.render.resolution_percentage = 100
