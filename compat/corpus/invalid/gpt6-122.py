import bpy, math
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name, rgb, metallic=0, emission=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*rgb, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*rgb, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = 0.38
    if emission:
        p.inputs['Emission Color'].default_value = (*rgb, 1)
        p.inputs['Emission Strength'].default_value = emission
    return m

def finish(o, name, material, bevel=0.025):
    o.name = name
    o.data.materials.append(material)
    if bevel:
        b = o.modifiers.new('Edge chamfers', 'BEVEL')
        b.width, b.segments = bevel, 2
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def box(name, loc, size, material, bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(o, name, material, bevel)

def beam(name, a, b, width, depth, material):
    a, b = Vector(a), Vector(b)
    o = box(name, (a+b)/2, (width, depth, (b-a).length), material)
    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = (b-a).to_track_quat('Z', 'Y')
    return o

def cyl(name, a, b, r, material, vertices=24):
    a, b = Vector(a), Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=r, depth=(b-a).length, location=(a+b)/2)
    o = bpy.context.object
    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = (b-a).to_track_quat('Z', 'Y')
    finish(o, name, material, 0.008)
    for p in o.data.polygons:
        p.use_smooth = len(p.vertices) == 4
    return o

def text(body, loc, size, material):
    c = bpy.data.curves.new('Station signage', 'FONT')
    c.body, c.size, c.align_x = body, size, 'CENTER'
    c.extrude = 0.001
    o = bpy.data.objects.new(body, c)
    bpy.context.collection.objects.link(o)
    o.location = loc
    o.rotation_euler.x = math.pi/2
    o.data.materials.append(material)

def area(name, loc, target, energy, color, size):
    d = bpy.data.lights.new(name, 'AREA')
    d.energy, d.color, d.size = energy, color, size
    o = bpy.data.objects.new(name, d)
    bpy.context.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = (Vector(target)-o.location).to_track_quat('-Z', 'Y').to_euler()

shell = mat('Ceramic grey wall panels', (0.34, 0.42, 0.47), 0.45)
rib = mat('Structural gunmetal', (0.055, 0.105, 0.14), 0.8)
metal = mat('Pipe stainless', (0.43, 0.53, 0.58), 0.85)
dark = mat('Panel gaps and rubber', (0.012, 0.022, 0.028), 0.15)
floor = mat('Deck panels', (0.16, 0.21, 0.25), 0.7)
yellow = mat('Safety yellow', (0.95, 0.56, 0.055), 0.25)
blue = mat('Cool guide lights', (0.03, 0.55, 1), 0.15, 4)
white = mat('Ceiling diffusers', (0.7, 0.9, 1), 0, 5)
ink = mat('Pale lettering', (0.82, 0.9, 0.93))

# Six identical 2.4 m bays, with an open entrance and closed terminal bulkhead.
length = 14.4
box('Foundation', (0, length/2, -0.2), (6.5, length+0.3, 0.4), rib)
box('Ceiling backing', (0, length/2, 5.12), (4.3, length, 0.18), dark)
for bay in range(6):
    y = bay*2.4+1.2
    for side in (-1, 1):
        box('Bay %02d wall backing'%bay, (side*3.06, y, 2.3), (0.18, 2.35, 3.4), dark)
        for z, h in ((1.14, 0.95), (2.37, 1.35), (3.49, 0.64)):
            box('Removable wall cassette', (side*2.94, y, z), (0.12, 2.14, h), shell, 0.045)
        box('Wall belt trim', (side*2.83, y, 1.79), (0.1, 2.25, 0.08), yellow, 0.012)
        beam('Lower diagonal wall', (side*2.08, y, 0.08), (side*3.0, y, 0.9), 0.12, 2.25, shell)
        beam('Upper diagonal wall', (side*3.0, y, 3.8), (side*2.08, y, 5.0), 0.12, 2.25, shell)
        box('Wall ventilation recess', (side*2.859, y, 1.13), (0.025, 1.4, 0.45), dark, 0.015)
        for j in range(9):
            box('Vent vertical fin', (side*2.825, y-0.61+j*0.15, 1.13), (0.055, 0.035, 0.39), metal, 0.006)
        box('Recessed guide light', (side*2.57, y, 0.48), (0.09, 1.72, 0.1), blue, 0.015)
        box('Ceiling strip housing', (side*1.4, y, 4.94), (0.43, 2.06, 0.15), rib)
        box('Ceiling strip diffuser', (side*1.4, y, 4.85), (0.26, 1.84, 0.025), white, 0.008)
    for x in (-1.38, 0, 1.38):
        box('Bolted modular floor tile', (x, y, 0.027), (1.31, 2.25, 0.065), floor, 0.025)
        for dx in (-0.52, 0.52):
            for dy in (-0.96, 0.96):
                cyl('Deck fastener', (x+dx, y+dy, 0.058), (x+dx, y+dy, 0.072), 0.034, metal, 12)
        for j in range(6):
            box('Deck antislip tread', (x, y-0.78+j*0.3, 0.066), (0.92, 0.022, 0.012), dark, 0.003)
    for side in (-1, 1):
        box('Longitudinal floor stripe', (side*1.98, y, 0.073), (0.055, 2.25, 0.012), yellow, 0)
    area('Bay practical light', (0, y, 4.65), (0, y, 0), 260, (0.68, 0.83, 1), 2.0)

profile = [(-2.1, 0.08), (-3, 0.9), (-3, 3.8), (-2.1, 5), (2.1, 5), (3, 3.8), (3, 0.9), (2.1, 0.08)]
for n in range(7):
    y = n*2.4
    for i in range(len(profile)-1):
        a, b = profile[i], profile[i+1]
        beam('Rib %02d segment %d'%(n, i), (a[0], y, a[1]), (b[0], y, b[1]), 0.2, 0.27, rib)
    for side in (-1, 1):
        for z in (1, 3.65):
            box('Rib junction plate', (side*2.88, y, z), (0.16, 0.4, 0.38), metal)
        box('Rib amber marker', (side*2.83, y-0.15, 2.72), (0.09, 0.035, 0.42), yellow)
    box('Overhead service crossbar', (0, y, 4.61), (1.85, 0.15, 0.12), metal)
for i, x in enumerate((-0.66, -0.23, 0.23, 0.66)):
    cyl('Continuous ceiling utility pipe', (x, -0.05, 4.77), (x, length, 4.77), 0.11 if i%2 else 0.14, metal)
    for n in range(7):
        y = n*2.4
        cyl('Ceiling pipe coupling', (x, y-0.09, 4.77), (x, y+0.09, 4.77), 0.17, rib)
    for y in (3.3, 8.1, 12.9):
        cyl('Pipe identification collar', (x, y, 4.77), (x, y+0.16, 4.77), 0.146 if i%2 == 0 else 0.116, yellow)
box('Terminal bulkhead', (0, 14.55, 2.55), (6.2, 0.32, 5.1), rib, 0.05)
box('Terminal door frame', (0, 14.32, 2.26), (3.5, 0.25, 4.38), metal, 0.12)
box('Terminal door gasket', (0, 14.16, 2.25), (3.14, 0.12, 4.08), dark, 0.1)
for side in (-1, 1):
    box('Terminal door leaf', (side*0.75, 14.07, 2.25), (1.46, 0.14, 3.87), shell, 0.06)
    box('Terminal luminous jamb', (side*1.64, 14.1, 2.45), (0.055, 0.04, 2.85), blue, 0.01)
text('HABITAT  /  B-06', (0, 14.365, 4.62), 0.25, ink)
text('06', (0, 13.987, 2.45), 0.58, ink)
area('Entrance fill', (0, -3, 4), (0, 6, 2), 800, (0.8, 0.9, 1), 4)
bpy.ops.object.camera_add(location=(0.35, -4.0, 2.65))
cam = bpy.context.object
cam.rotation_euler = (Vector((0, 9, 2.55))-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 23
cam.data.clip_end = 100
scene = bpy.context.scene
scene.camera = cam
scene.world.color = (0.045, 0.055, 0.08)
scene.render.engine = 'CYCLES'
scene.render.resolution_x, scene.render.resolution_y = 1500, 1050
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'AgX'
