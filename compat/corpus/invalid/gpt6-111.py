import bpy, math
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)

def material(name, color, metallic=0.0, roughness=0.4):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    return m

steel = material('Machined titanium', (0.40, 0.48, 0.53), 0.88, 0.26)
housing = material('Graphite housing', (0.065, 0.095, 0.12), 0.8, 0.32)
rim_mat = material('Polished rim', (0.56, 0.62, 0.66), 0.9, 0.23)
black = material('Recesses', (0.018, 0.025, 0.03), 0.5, 0.38)
orange = material('Safety orange', (0.95, 0.23, 0.035), 0.45, 0.34)
floor_mat = material('Studio floor', (0.12, 0.15, 0.18), 0.1, 0.58)

def finish(obj, mat, bevel=0):
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Edge machining', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def box(name, loc, scale, mat, bevel=0.03):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(o, mat, bevel)

def cylinder(name, radius, depth, z, mat, xy=(0, 0), vertices=96):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=(*xy, z))
    o = bpy.context.object
    o.name = name
    finish(o, mat, 0.018)
    for p in o.data.polygons:
        p.use_smooth = len(p.vertices) == 4
    return o

def ring(name, inner, outer, bottom, top, mat, segments=128):
    v, f = [], []
    for z, r in [(bottom, inner), (bottom, outer), (top, inner), (top, outer)]:
        v.extend([(r*math.cos(2*math.pi*i/segments), r*math.sin(2*math.pi*i/segments), z) for i in range(segments)])
    for i in range(segments):
        j = (i+1) % segments
        f.extend([(i, j, segments+j, segments+i),
                  (2*segments+i, 3*segments+i, 3*segments+j, 2*segments+j),
                  (i, 2*segments+i, 2*segments+j, j),
                  (segments+i, segments+j, 3*segments+j, 3*segments+i)])
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(v, [], f)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(o)
    finish(o, mat, 0.014)
    for index, p in enumerate(mesh.polygons):
        p.use_smooth = index % 4 in (2, 3)
    return o

# An open axial housing keeps the rotor and its tip clearance visible.
ring('Main cylindrical casing', 3.63, 4.00, 0.15, 1.20, housing)
ring('Upper mounting flange', 3.61, 4.25, 1.17, 1.34, rim_mat)
ring('Lower mounting flange', 3.61, 4.18, 0.07, 0.24, rim_mat)
ring('Inner wear liner', 3.57, 3.635, 0.34, 1.14, black)
ring('Orange flange identification ring', 4.10, 4.17, 1.343, 1.355, orange)

# Radial support struts lie beneath the rotating assembly.
for i in range(6):
    a = i*math.tau/6
    o = box('Stationary bearing support %02d' % i, (2.15*math.cos(a), 2.15*math.sin(a), 0.33), (2.9, 0.17, 0.17), housing)
    o.rotation_euler.z = a
cylinder('Bearing sleeve', 0.68, 0.54, 0.37, housing)
cylinder('Rotor root drum', 1.16, 0.38, 0.76, steel)
ring('Hub rim', 0.95, 1.18, 0.95, 1.03, rim_mat)

# Closed airfoil sections are lofted along a swept, twisted radial span.
sections, samples = 11, 24
verts, faces = [], []
for j in range(sections):
    t = j/(sections-1)
    r = 1.04 + 2.43*t
    sweep = -0.28*t*t
    chord = 0.74 + 0.24*math.sin(math.pi*t) - 0.12*t
    twist = math.radians(44 - 24*t)
    center_z = 0.78 + 0.06*math.sin(math.pi*t)
    for k in range(samples):
        u = math.tau*k/samples
        s = 0.5*chord*math.cos(u)
        thickness = 0.065*(1-0.35*t)*math.sin(u)
        tangent = s*math.cos(twist) - thickness*math.sin(twist)
        z = center_z + s*math.sin(twist) + thickness*math.cos(twist)
        verts.append((r*math.cos(sweep)-tangent*math.sin(sweep), r*math.sin(sweep)+tangent*math.cos(sweep), z))
for j in range(sections-1):
    for k in range(samples):
        n = (k+1) % samples
        faces.append((j*samples+k, j*samples+n, (j+1)*samples+n, (j+1)*samples+k))
faces.append(tuple(reversed(range(samples))))
faces.append(tuple((sections-1)*samples+k for k in range(samples)))
mesh = bpy.data.meshes.new('Swept airfoil master mesh')
mesh.from_pydata(verts, [], faces)
mesh.materials.append(steel)
mesh.update()
for p in mesh.polygons:
    p.use_smooth = len(p.vertices) == 4
for i in range(18):
    o = bpy.data.objects.new('Rotor blade %02d' % (i+1), mesh)
    bpy.context.collection.objects.link(o)
    o.rotation_euler.z = i*math.tau/18

# Rounded spinner, retention bolts and casing fasteners.
bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=24, location=(0, 0, 1.02))
spinner = bpy.context.object
spinner.name = 'Ellipsoidal hub spinner'
spinner.scale = (0.96, 0.96, 0.52)
finish(spinner, steel)
for p in spinner.data.polygons:
    p.use_smooth = True
cylinder('Spinner center cap', 0.19, 0.05, 1.54, black)
for i in range(12):
    a = i*math.tau/12
    cylinder('Hub retention screw', 0.042, 0.04, 1.052, black, (1.075*math.cos(a), 1.075*math.sin(a)), 6)
for i in range(24):
    a = i*math.tau/24
    xy = (3.92*math.cos(a), 3.92*math.sin(a))
    cylinder('Flange washer', 0.11, 0.022, 1.357, black, xy, 32)
    cylinder('Flange hex bolt', 0.073, 0.075, 1.40, steel, xy, 6)
for x in (-2.85, 2.85):
    box('Mounting foot', (x, 0, -0.12), (0.65, 4.6, 0.36), housing, 0.08)
    for y in (-1.8, 1.8):
        cylinder('Foot anchor', 0.10, 0.09, 0.095, steel, (x, y), 6)
box('Ground', (0, 0, -0.42), (200, 200, 0.2), floor_mat, 0)

def area(name, loc, power, size, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    o = bpy.context.object
    o.name = name
    o.data.energy = power
    o.data.shape = 'DISK'
    o.data.size = size
    o.rotation_euler = (Vector(target)-o.location).to_track_quat('-Z', 'Y').to_euler()
area('Large key', (1, -4, 10), 1800, 7, (0, 0, 0))
area('Cool fill', (-6, -1, 5), 1200, 5, (0, 0, 0.5))
area('Rim light', (3, 6, 7), 2200, 5, (0, 0, 0.5))
bpy.ops.object.camera_add(location=(8, -10, 12))
cam = bpy.context.object
cam.rotation_euler = (Vector((0, 0, 0.45))-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 11.8
scene = bpy.context.scene
scene.camera = cam
scene.render.engine = 'CYCLES'
scene.render.resolution_x = 1400
scene.render.resolution_y = 1400
scene.render.resolution_percentage = 100
scene.world.color = (0.22, 0.22, 0.22)
