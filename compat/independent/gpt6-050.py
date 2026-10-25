import bpy
import math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0, roughness=0.4):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = roughness
    return m

white = material('Off-white turbine enamel', (0.82, 0.85, 0.87), 0.25)
blade_mat = material('Blade composite', (0.91, 0.93, 0.94), 0.12)
steel = material('Service hardware', (0.23, 0.28, 0.32), 0.75)
dark = material('Vent recesses', (0.035, 0.05, 0.06))
concrete = material('Foundation concrete', (0.45, 0.46, 0.44))
ground = material('Site grass', (0.22, 0.29, 0.18))

def box(name, loc, dims, mat, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        b = o.modifiers.new('Rounded casing edges', 'BEVEL')
        b.width = bevel
        b.segments = 3
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def cone(name, loc, r1, r2, depth, mat, axis=(0, 0, 1)):
    bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=r1, radius2=r2, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    o.rotation_euler = Vector(axis).to_track_quat('Z', 'Y').to_euler()
    o.data.materials.append(mat)
    for p in o.data.polygons:
        p.use_smooth = len(p.vertices) == 4
    return o

box('Ground', (0, 0, -0.12), (16, 16, 0.2), ground)
cone('Circular concrete foundation', (0, 0, 0.12), 0.98, 0.98, 0.28, concrete)
cone('Tower anchor flange', (0, 0, 0.29), 0.64, 0.64, 0.09, steel)
cone('Tapered tubular tower', (0, 0, 3.47), 0.48, 0.235, 6.3, white)
for i in range(12):
    a = i*math.tau/12
    cone('Foundation anchor bolt %02d' % i, (0.56*math.cos(a), 0.56*math.sin(a), 0.36),
         0.037, 0.037, 0.08, steel)
for height in (2.4, 4.5):
    radius = 0.48-(height-0.32)/6.3*0.245
    cone('Tower section joint', (0, 0, height), radius+0.008, radius+0.008, 0.032, white)
box('Service door dark gasket', (0, -0.466, 0.94), (0.32, 0.035, 0.91), dark, 0.025)
box('Tower service door', (0, -0.492, 0.94), (0.285, 0.03, 0.86), white, 0.022)
box('Door handle', (0.095, -0.523, 0.97), (0.025, 0.035, 0.12), steel, 0.008)
box('Door access step', (0, -0.67, 0.36), (0.48, 0.42, 0.1), steel, 0.015)
cone('Yaw bearing', (0, 0, 6.64), 0.32, 0.32, 0.18, steel)
box('Rounded nacelle housing', (0, 0.12, 6.99), (0.91, 1.75, 0.78), white, 0.20)
box('Nacelle service hatch', (0, 0.34, 7.391), (0.48, 0.65, 0.025), steel, 0.035)
for y in (0.36, 0.49, 0.62, 0.75):
    box('Nacelle cooling grille', (0.456, y, 6.99), (0.012, 0.055, 0.28), dark, 0.009)
cone('Rotor shaft', (0, -0.91, 6.99), 0.19, 0.19, 0.4, steel, (0, -1, 0))
cone('Rotor hub drum', (0, -1.13, 6.99), 0.33, 0.33, 0.35, white, (0, -1, 0))
cone('Aerodynamic spinner', (0, -1.45, 6.99), 0.34, 0.035, 0.45, white, (0, -1, 0))

# Each closed blade uses airfoil rings, a broad shoulder, and a swept tapered tip.
hub = Vector((0, -1.13, 6.99))
stations = [(0.23, 0.17, 0.00, 24), (0.52, 0.36, 0.01, 18),
            (0.91, 0.48, 0.03, 13), (1.65, 0.36, 0.09, 8),
            (2.45, 0.23, 0.18, 4), (3.15, 0.10, 0.27, 1),
            (3.4, 0.018, 0.30, 0)]
for blade_index in range(3):
    angle = blade_index*math.tau/3
    radial = Vector((math.sin(angle), 0, math.cos(angle)))
    tangent = Vector((math.cos(angle), 0, -math.sin(angle)))
    axial = Vector((0, -1, 0))
    vertices, faces = [], []
    ring_size = 16
    for radius, chord, sweep, twist in stations:
        pitch = math.radians(twist)
        chord_dir = tangent*math.cos(pitch)+axial*math.sin(pitch)
        thickness_dir = axial*math.cos(pitch)-tangent*math.sin(pitch)
        for j in range(ring_size):
            t = j*math.tau/ring_size
            x = (1-math.cos(t))/2
            thickness = 5*0.16*chord*(0.2969*math.sqrt(x)-0.126*x-0.3516*x*x+0.2843*x**3-0.1036*x**4)
            thickness *= 1 if j <= ring_size//2 else -1
            p = hub+radial*radius+tangent*sweep+chord_dir*((x-0.35)*chord)+thickness_dir*thickness
            vertices.append(tuple(p))
    for k in range(len(stations)-1):
        for j in range(ring_size):
            a, b = k*ring_size+j, k*ring_size+(j+1)%ring_size
            faces.append((a, b, b+ring_size, a+ring_size))
    faces.append(tuple(reversed(range(ring_size))))
    faces.append(tuple((len(stations)-1)*ring_size+j for j in range(ring_size)))
    mesh = bpy.data.meshes.new('Tapered airfoil mesh')
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new('Rotor blade %d' % (blade_index+1), mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(blade_mat)
    # Recalculate consistent outward normals on the closed surface.
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    for p in mesh.polygons:
        p.use_smooth = len(p.vertices) == 4

bpy.ops.object.camera_add(location=(12, -21, 11))
cam = bpy.context.object
cam.name = 'Turbine overview camera'
cam.rotation_euler = (Vector((0, 0, 5.0))-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 12.3
bpy.context.scene.camera = cam
bpy.ops.object.light_add(type='AREA', location=(-5, -8, 13))
bpy.context.object.data.energy = 2300
bpy.context.object.data.size = 8
scene = bpy.context.scene
scene.world.color = (0.3, 0.3, 0.3)
scene.render.resolution_x = 1000
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
