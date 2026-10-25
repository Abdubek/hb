import bpy, math
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)

ROWS = 6
SECTORS = 8
INNER_RADIUS = 4.0
ROW_DEPTH = 0.91
ROW_RISE = 0.34
AISLE_ANGLE = 0.145

def material(name, color, metallic=0, roughness=0.5):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    return m

concrete = material('Warm architectural concrete', (0.36, 0.37, 0.35), roughness=0.82)
carpet = material('Charcoal tier carpet', (0.055, 0.07, 0.085), roughness=0.94)
seat_mat = material('Teal upholstery', (0.035, 0.30, 0.34), roughness=0.8)
seat_back = material('Dark seat shell', (0.045, 0.075, 0.085), roughness=0.4)
metal = material('Black powder coated metal', (0.025, 0.035, 0.04), 0.6, 0.33)
wood = material('Presentation platform oak', (0.51, 0.30, 0.12), roughness=0.46)
trim = material('Brass edge trims', (0.68, 0.43, 0.13), 0.7, 0.3)
floor_mat = material('Lobby flooring', (0.20, 0.23, 0.25), roughness=0.68)
light_mat = material('Warm step lights', (1, 0.69, 0.25), roughness=0.35)
p = light_mat.node_tree.nodes.get('Principled BSDF')
p.inputs['Emission Color'].default_value = (1, 0.53, 0.13, 1)
p.inputs['Emission Strength'].default_value = 2.5

def box(name, loc, dims, mat, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        b = o.modifiers.new('Edge rounding', 'BEVEL')
        b.width = bevel
        b.segments = 2
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def sector(name, r0, r1, a0, a1, z0, z1, mat, steps=None):
    n = steps or max(2, math.ceil((a1-a0)*22))
    verts, faces = [], []
    for z, r in [(z0, r0), (z0, r1), (z1, r0), (z1, r1)]:
        verts.extend([(r*math.cos(a0+(a1-a0)*i/n), r*math.sin(a0+(a1-a0)*i/n), z) for i in range(n+1)])
    s = n+1
    for i in range(n):
        j = i+1
        faces.extend([(i, j, s+j, s+i), (2*s+i, 3*s+i, 3*s+j, 2*s+j), (i, 2*s+i, 2*s+j, j), (s+i, s+j, 3*s+j, 3*s+i)])
    faces.extend([(0, s, 3*s, 2*s), (n, 2*s+n, 3*s+n, s+n)])
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(o)
    return o

def cylinder(name, radius, depth, loc, mat, vertices=96):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)
    b = o.modifiers.new('Rounded edges', 'BEVEL')
    b.width = 0.015
    b.segments = 2
    o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

outer = INNER_RADIUS+ROWS*ROW_DEPTH
cylinder('Circular foundation', outer+1.0, 0.28, (0, 0, -0.14), concrete, 192)
cylinder('Central circulation floor', INNER_RADIUS, 0.045, (0, 0, 0.025), floor_mat, 128)

# All chairs share one multi-material mesh: useful detail with low overhead.
cv, cf, cm = [], [], []
def chair_box(center, dims, mat_index):
    x, y, z = center
    dx, dy, dz = [d/2 for d in dims]
    base = len(cv)
    cv.extend([(x-dx,y-dy,z-dz),(x+dx,y-dy,z-dz),(x+dx,y+dy,z-dz),(x-dx,y+dy,z-dz),(x-dx,y-dy,z+dz),(x+dx,y-dy,z+dz),(x+dx,y+dy,z+dz),(x-dx,y+dy,z+dz)])
    for face in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:
        cf.append(tuple(base+i for i in face))
        cm.append(mat_index)
chair_box((0, 0, 0.44), (0.47, 0.46, 0.12), 0)
chair_box((0, 0.205, 0.80), (0.49, 0.11, 0.60), 1)
chair_box((0, 0.139, 0.81), (0.43, 0.055, 0.51), 0)
for x in (-0.185, 0.185):
    chair_box((x, 0.04, 0.21), (0.045, 0.055, 0.42), 2)
    chair_box((x, 0.04, 0.035), (0.10, 0.29, 0.04), 2)
for x in (-0.27, 0.27):
    chair_box((x, 0.02, 0.64), (0.055, 0.39, 0.055), 1)
    chair_box((x, 0.15, 0.51), (0.032, 0.035, 0.23), 2)
chair_mesh = bpy.data.meshes.new('Linked auditorium chair geometry')
chair_mesh.from_pydata(cv, [], cf)
for m in (seat_mat, seat_back, metal):
    chair_mesh.materials.append(m)
for poly, idx in zip(chair_mesh.polygons, cm):
    poly.material_index = idx
chair_mesh.update()

for row in range(ROWS):
    r0 = INNER_RADIUS+row*ROW_DEPTH
    r1 = r0+ROW_DEPTH
    level = (row+1)*ROW_RISE
    for s in range(SECTORS):
        a0 = s*math.tau/SECTORS+AISLE_ANGLE/2
        a1 = (s+1)*math.tau/SECTORS-AISLE_ANGLE/2
        sector('Tier %d seating block %d' % (row+1, s+1), r0, r1, a0, a1, 0, level, concrete)
        sector('Carpeted seating terrace', r0+0.025, r1-0.025, a0, a1, level, level+0.018, carpet)
        sector('Tier front brass nosing', r0, r0+0.022, a0, a1, level, level+0.025, trim)
        seat_radius = r0+0.50
        available = (a1-a0)*seat_radius
        count = max(2, int((available-0.18)/0.63))
        for k in range(count):
            a = a0+(k+0.5)*(a1-a0)/count
            chair = bpy.data.objects.new('Seat R%02d B%02d N%02d' % (row+1, s+1, k+1), chair_mesh)
            bpy.context.collection.objects.link(chair)
            chair.location = (seat_radius*math.cos(a), seat_radius*math.sin(a), level+0.018)
            chair.rotation_euler.z = a-math.pi/2
            mod = chair.modifiers.new('Upholstery edge rounding', 'BEVEL')
            mod.width = 0.016
            mod.segments = 2
            chair.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    # Two shallow stair treads for each seating riser.
    for s in range(SECTORS):
        a = s*math.tau/SECTORS
        for sub in range(2):
            ra = r0+sub*ROW_DEPTH/2
            rb = ra+ROW_DEPTH/2
            step_z = row*ROW_RISE+(sub+1)*ROW_RISE/2
            sector('Radial aisle stair', ra, rb, a-AISLE_ANGLE/2, a+AISLE_ANGLE/2, 0, step_z, concrete, 3)
            sector('Illuminated stair nosing', ra, ra+0.028, a-AISLE_ANGLE*0.42, a+AISLE_ANGLE*0.42, step_z, step_z+0.009, light_mat, 3)

# Continuous rear concourse, with openings in its guardrail at each aisle.
rear_level = ROWS*ROW_RISE
sector('Upper circular concourse', outer, outer+0.90, 0, math.tau, 0, rear_level, concrete, 192)
for s in range(SECTORS):
    a0 = s*math.tau/SECTORS+0.09
    a1 = (s+1)*math.tau/SECTORS-0.09
    for z in (rear_level+0.55, rear_level+1.05):
        sector('Curved perimeter guardrail', outer+0.76, outer+0.80, a0, a1, z, z+0.045, metal)
    for i in range(6):
        a = a0+(a1-a0)*i/5
        cylinder('Guardrail upright', 0.025, 1.09, ((outer+0.78)*math.cos(a), (outer+0.78)*math.sin(a), rear_level+0.545), metal, 12)

cylinder('Stage lower step', 2.92, 0.15, (0, 0, 0.115), concrete, 128)
cylinder('Central oak presentation platform', 2.67, 0.23, (0, 0, 0.305), wood, 128)
sector('Stage perimeter trim', 2.62, 2.67, 0, math.tau, 0.42, 0.43, trim, 128)
# Thin parallel seams suggest oak floorboards without external textures.
for i in range(-10, 11):
    x = i*0.235
    length = 2*math.sqrt(max(0, 2.58**2-x*x))
    box('Platform board seam', (x, 0, 0.423), (0.007, length, 0.004), trim)
box('Lectern foot', (0, 0.60, 0.45), (0.62, 0.50, 0.065), metal, 0.02)
box('Lectern pedestal', (0, 0.65, 0.98), (0.22, 0.24, 1.02), wood, 0.02)
top = box('Lectern sloping top', (0, 0.61, 1.50), (0.75, 0.53, 0.06), metal, 0.02)
top.rotation_euler.x = math.radians(12)
for x in (-1.85, 1.85):
    monitor = box('Stage floor monitor', (x, 0.9, 0.63), (0.47, 0.40, 0.37), metal, 0.035)
    monitor.rotation_euler.x = math.radians(-12)
box('Studio ground', (0, 0, -0.35), (200, 200, 0.1), floor_mat)

def light(loc, energy, size):
    bpy.ops.object.light_add(type='AREA', location=loc)
    o = bpy.context.object
    o.data.energy = energy
    o.data.size = size
    o.rotation_euler = (Vector((0, 0, 0))-o.location).to_track_quat('-Z', 'Y').to_euler()
light((0, -5, 15), 3500, 10)
light((-10, -1, 10), 2300, 8)
light((5, 10, 13), 4000, 8)
bpy.ops.object.camera_add(location=(16, -21, 24))
cam = bpy.context.object
cam.rotation_euler = (Vector((0, 0, 0.6))-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 25
scene = bpy.context.scene
scene.camera = cam
scene.render.engine = 'CYCLES'
scene.render.resolution_x = 1500
scene.render.resolution_y = 1400
scene.render.resolution_percentage = 100
scene.world.color = (0.26, 0.26, 0.26)
