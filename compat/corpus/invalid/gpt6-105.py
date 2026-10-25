import bpy, math
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 96
scene.render.resolution_x = 1800
scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'AgX'
scene.world.color = (0.08,0.08,0.08)

def mat(name,color,metal=0,rough=0.5):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color,1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color,1)
    p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough
    return m
wall = mat('Warm plaster',(0.68,0.62,0.51),0,0.85)
ceiling = mat('Ivory ceiling',(0.8,0.78,0.7),0,0.82)
walnut = mat('Walnut doors and panels',(0.17,0.075,0.033),0,0.36)
trim = mat('Dark stained oak trim',(0.075,0.038,0.021),0,0.4)
brass = mat('Brushed brass hardware',(0.58,0.39,0.16),0.8,0.28)
carpet = mat('Blue charcoal woven carpet',(0.045,0.085,0.10),0,0.94)
stripe = mat('Carpet woven accent',(0.19,0.24,0.23),0,0.95)
black = mat('Dark fixtures',(0.014,0.018,0.022),0.25,0.3)
linen = mat('Sconce linen',(0.9,0.79,0.58),0,0.8)
p = linen.node_tree.nodes.get('Principled BSDF')
p.inputs['Emission Color'].default_value = (1,0.66,0.32,1)
p.inputs['Emission Strength'].default_value = 1.5
lightmat = mat('Recessed luminous diffuser',(1,0.87,0.66),0,0.3)
p = lightmat.node_tree.nodes.get('Principled BSDF')
p.inputs['Emission Color'].default_value = (1,0.78,0.49,1)
p.inputs['Emission Strength'].default_value = 4
fabric = mat('Bench upholstery',(0.23,0.29,0.25),0,0.85)
ceramic = mat('Glazed ceramic',(0.22,0.29,0.27),0.1,0.23)
leaves = mat('Plant leaves',(0.045,0.17,0.065),0,0.55)
paper = mat('Artwork paper',(0.8,0.75,0.61),0,0.9)
art = mat('Artwork burnt orange',(0.45,0.14,0.055),0,0.8)
# Directional wood grain and fine carpet weave, generated without image assets.
for m,scale,strength,distance in [(walnut,(6,6,0.28),0.15,0.006),(carpet,(120,120,120),0.35,0.002)]:
    n,l = m.node_tree.nodes,m.node_tree.links
    c = n.new('ShaderNodeTexCoord')
    v = n.new('ShaderNodeVectorMath')
    v.operation = 'MULTIPLY'
    v.inputs[1].default_value = scale
    noise = n.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 3
    bump = n.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = strength
    bump.inputs['Distance'].default_value = distance
    l.new(c.outputs['Object'],v.inputs[0])
    l.new(v.outputs['Vector'],noise.inputs['Vector'])
    l.new(noise.outputs['Fac'],bump.inputs['Height'])
    l.new(bump.outputs['Normal'],n.get('Principled BSDF').inputs['Normal'])

def box(name,loc,dims,m,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(m)
    if bevel:
        b = o.modifiers.new('Edge softness','BEVEL')
        b.width = bevel
        b.segments = 3
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def cyl(name,loc,r,depth,m):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=r,depth=depth,location=loc)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(m)
    for p in o.data.polygons:
        p.use_smooth = True
    b = o.modifiers.new('Edge softness','BEVEL')
    b.width = min(0.008,depth*0.15)
    b.segments = 3
    o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def aim(o,target):
    o.rotation_euler = (Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
def area(name,loc,target,power,size,color=(1,0.79,0.55)):
    d = bpy.data.lights.new(name,'AREA')
    d.energy = power
    d.size = size
    o = bpy.data.objects.new(name,d)
    scene.collection.objects.link(o)
    o.location = loc
    d.color = color
    aim(o,target)
    return o

def text(name,body,size,loc,rotation,m):
    c = bpy.data.curves.new(name,'FONT')
    c.body = body
    c.align_x = 'CENTER'
    c.align_y = 'CENTER'
    c.size = size
    c.extrude = 0.0007
    o = bpy.data.objects.new(name,c)
    scene.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = rotation
    c.materials.append(m)
    return o

# Corridor runs along +Y; doors sit within genuinely segmented side walls.
box('Continuous carpet floor',(0,11,-0.045),(3.6,26,0.09),carpet)
box('Ceiling',(0,11,3.16),(3.9,26,0.16),ceiling)
for x in (-1.24,1.24):
    box('Carpet border stripe',(x,11,0.002),(0.025,26,0.004),stripe)
for y in range(-1,24):
    box('Carpet subtle cross weave',(0,y,0.001),(2.45,0.012,0.002),stripe)
centers = [2.0,5.5,9.0,12.5,16.0,19.5]
for side in (-1,1):
    x = side*1.9
    spans = []
    start = -2
    for y in centers:
        spans.append((start,y-0.57))
        start = y+0.57
    spans.append((start,24))
    for a,b in spans:
        mid = (a+b)*0.5
        box('Plaster wall pier',(x,mid,1.55),(0.2,b-a,3.1),wall)
        box('Walnut lower wall panel',(side*1.785,mid,0.48),(0.035,b-a,0.88),walnut,0.005)
        box('Brass chair rail',(side*1.756,mid,0.96),(0.027,b-a,0.024),brass,0.005)
        box('Oak skirting',(side*1.756,mid,0.09),(0.045,b-a,0.18),trim,0.008)
    box('Continuous door header wall',(x,11,2.77),(0.2,26,0.66),wall)
    box('Ceiling perimeter cornice',(side*1.73,11,3.04),(0.15,26,0.12),ceiling,0.012)
    for i,y in enumerate(centers):
        box('Recess shadow around room door',(side*1.89,y,1.2),(0.075,1.14,2.4),black)
        box('Walnut guest room door',(side*1.83,y,1.19),(0.065,1.04,2.34),walnut,0.012)
        for edge in (-0.59,0.59):
            box('Door jamb',(side*1.747,y+edge,1.23),(0.11,0.09,2.46),trim,0.009)
        box('Door architrave lintel',(side*1.747,y,2.43),(0.11,1.27,0.09),trim,0.009)
        box('Brass threshold',(side*1.81,y,0.012),(0.22,1.08,0.024),brass,0.004)
        box('Door inset panel',(side*1.789,y,1.31),(0.016,0.78,1.6),trim,0.006)
        box('Door inset walnut face',(side*1.777,y,1.31),(0.012,0.74,1.56),walnut,0.006)
        handle_y = y-0.34
        box('Electronic lock plate',(side*1.757,handle_y,1.02),(0.035,0.10,0.27),brass,0.012)
        box('Keycard reader',(side*1.733,handle_y,1.105),(0.012,0.064,0.075),black,0.006)
        box('Lever stem',(side*1.70,handle_y,0.975),(0.10,0.027,0.027),brass,0.008)
        box('Door lever',(side*1.648,handle_y+0.057,0.975),(0.027,0.15,0.027),brass,0.009)
        sign_y = y+0.83
        box('Room number plaque',(side*1.768,sign_y,1.62),(0.032,0.25,0.15),brass,0.01)
        rotation = (math.pi/2,0,math.pi/2 if side == -1 else -math.pi/2)
        text('Room number',str(201+i*2+(1 if side == 1 else 0)),0.068,(side*1.748,sign_y,1.62),rotation,black)
        # Sconces occupy the solid pier beyond each door.
        sy = y+1.5
        box('Sconce backplate',(side*1.745,sy,1.96),(0.09,0.16,0.35),brass,0.018)
        box('Sconce luminous shade',(side*1.64,sy,2.03),(0.17,0.27,0.32),linen,0.035)
        area('Sconce wall and floor wash',(side*1.51,sy,2.08),(0,sy,1.25),32,0.28)

for y in (0,3.5,7,10.5,14,17.5,21.5):
    cyl('Recessed downlight trim',(0,y,3.073),0.125,0.015,brass)
    cyl('Recessed downlight diffuser',(0,y,3.059),0.10,0.009,lightmat)
    area('Ceiling pool light',(0,y,3.04),(0,y,0),110,0.5)

# Furnished end landing closes the long perspective.
box('End wall',(0,24.05,1.55),(3.9,0.18,3.1),wall)
box('End wall skirting',(0,23.94,0.09),(3.6,0.045,0.18),trim,0.008)
box('End console top',(0,23.35,0.82),(1.8,0.48,0.07),walnut,0.025)
for x in (-0.76,0.76):
    for y in (23.19,23.51):
        box('Console brass leg',(x,y,0.40),(0.035,0.035,0.80),brass,0.006)
box('End artwork frame',(0,23.92,1.99),(1.34,0.055,1.22),brass,0.012)
box('End artwork paper',(0,23.882,1.99),(1.23,0.014,1.11),paper)
for x,z,r,m in [(-0.24,2.15,0.25,art),(0.23,1.84,0.30,ceramic)]:
    o = cyl('Abstract artwork circle',(x,23.87,z),r,0.009,m)
    o.rotation_euler.x = math.pi/2
box('Abstract artwork line',(0.02,23.858,1.98),(0.024,0.006,0.88),trim)
cyl('Console vase',(0.48,23.31,0.99),0.095,0.27,ceramic)
for i in range(3):
    box('Stacked display book',(-0.46,23.30,0.873+i*0.038),(0.36,0.26,0.035),paper if i%2 else fabric,0.005)

# A compact bench and framed print furnish the near right-hand pier.
box('Upholstered corridor bench',(1.43,3.76,0.47),(0.49,1.14,0.16),fabric,0.065)
for y in (3.32,4.20):
    for x in (1.26,1.61):
        box('Bench leg',(x,y,0.22),(0.035,0.035,0.43),brass,0.006)
box('Near framed print',(1.752,3.8,1.93),(0.06,0.85,0.93),brass,0.009)
box('Near print paper',(1.713,3.8,1.93),(0.016,0.76,0.84),paper)
box('Near print abstract rectangle',(1.701,3.70,1.93),(0.008,0.23,0.57),art)
box('Near print abstract stripe',(1.698,3.99,1.86),(0.009,0.17,0.36),ceramic)
# Procedural broad-leaf plant at the far landing.
cyl('Plant pot',(-1.22,23.22,0.22),0.22,0.44,ceramic)
cyl('Pot soil',(-1.22,23.22,0.44),0.19,0.014,trim)
for i in range(11):
    a = i*2.39996
    base = Vector((-1.22,23.22,0.44))
    tip = base + Vector((0.32*math.cos(a),0.32*math.sin(a),0.55+0.045*(i%5)))
    mid = (base+tip)*0.5
    bpy.ops.mesh.primitive_cylinder_add(vertices=10,radius=0.007,depth=(tip-base).length,location=mid)
    stem = bpy.context.object
    stem.name = 'Plant stem'
    stem.rotation_euler = (tip-base).to_track_quat('Z','Y').to_euler()
    stem.data.materials.append(leaves)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=1,location=tip)
    leaf = bpy.context.object
    leaf.name = 'Broad sculpted leaf'
    leaf.scale = (0.105,0.028,0.255)
    leaf.rotation_euler = Vector((math.cos(a),math.sin(a),0.65)).to_track_quat('Z','Y').to_euler()
    leaf.data.materials.append(leaves)
    for p in leaf.data.polygons:
        p.use_smooth = True
area('End artwork wash',(0,23.25,2.9),(0,23.90,1.9),90,0.6)
area('Entrance soft fill',(0,-1.4,2.5),(0,4,1.2),180,2,(0.77,0.85,1))
bpy.ops.object.camera_add(location=(-0.24,-1.25,1.55))
cam = bpy.context.object
cam.name = 'Wide-angle hotel corridor perspective'
cam.data.lens = 20
cam.data.sensor_width = 36
cam.data.clip_start = 0.05
cam.data.clip_end = 150
cam.data.dof.use_dof = False
aim(cam,(0.08,23.9,1.55))
scene.camera = cam
