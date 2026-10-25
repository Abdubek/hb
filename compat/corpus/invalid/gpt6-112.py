import bpy, math
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)

# Editable architectural parameters, in metres.
WIDTH = 10.8
HEIGHT = 5.7
DEPTH = 0.28
CELL_RADIUS = 0.49
WEB_THICKNESS = 0.065
FRAME_WIDTH = 0.16
DOOR_WIDTH = 2.05
DOOR_HEIGHT = 3.55
DOOR_CENTER = -0.65

def material(name, color, metallic=0, roughness=0.45):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    return m

wood = material('Warm honey colored cell structure', (0.62, 0.32, 0.105), 0.15, 0.36)
frame_mat = material('Bronze perimeter and portal', (0.12, 0.16, 0.17), 0.76, 0.29)
metal = material('Anchor hardware', (0.43, 0.47, 0.47), 0.85, 0.28)
floor_mat = material('Warm limestone floor', (0.48, 0.46, 0.41), 0, 0.75)

def box(name, loc, dims, mat, bevel=0.015):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        b = o.modifiers.new('Soft manufactured edges', 'BEVEL')
        b.width = bevel
        b.segments = 2
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

# Clip every hexagonal web to the frame and to three disjoint regions
# surrounding the doorway. Cells terminate cleanly against the portal.
left = -WIDTH/2 + FRAME_WIDTH
right = WIDTH/2 - FRAME_WIDTH
bottom = FRAME_WIDTH
top = HEIGHT - FRAME_WIDTH
dl = DOOR_CENTER - DOOR_WIDTH/2
dr = DOOR_CENTER + DOOR_WIDTH/2
portal_l = dl-FRAME_WIDTH
portal_r = dr+FRAME_WIDTH
portal_top = DOOR_HEIGHT+FRAME_WIDTH
regions = [(left, portal_l, bottom, top), (portal_r, right, bottom, top), (portal_l, portal_r, portal_top, top)]

def clip_edge(poly, axis, bound, keep_greater):
    if not poly:
        return []
    result = []
    a = poly[-1]
    ina = a[axis] >= bound-1e-9 if keep_greater else a[axis] <= bound+1e-9
    for b in poly:
        inb = b[axis] >= bound-1e-9 if keep_greater else b[axis] <= bound+1e-9
        if ina != inb:
            t = (bound-a[axis])/(b[axis]-a[axis])
            result.append((a[0]+t*(b[0]-a[0]), a[1]+t*(b[1]-a[1])))
        if inb:
            result.append(b)
        a, ina = b, inb
    return result

def clip_rect(poly, rect):
    xmin, xmax, zmin, zmax = rect
    for axis, bound, greater in [(0, xmin, True), (0, xmax, False), (1, zmin, True), (1, zmax, False)]:
        poly = clip_edge(poly, axis, bound, greater)
    return poly

vertices, faces = [], []
def extrude(poly):
    clean = []
    for p in poly:
        if not clean or math.dist(p, clean[-1]) > 1e-7:
            clean.append(p)
    if len(clean) > 1 and math.dist(clean[0], clean[-1]) < 1e-7:
        clean.pop()
    if len(clean) < 3:
        return
    area = sum(clean[i][0]*clean[(i+1)%len(clean)][1]-clean[(i+1)%len(clean)][0]*clean[i][1] for i in range(len(clean)))
    if abs(area) < 1e-8:
        return
    if area < 0:
        clean.reverse()
    start, n = len(vertices), len(clean)
    vertices.extend([(x, -DEPTH/2, z) for x, z in clean])
    vertices.extend([(x, DEPTH/2, z) for x, z in clean])
    faces.append(tuple(start+i for i in range(n)))
    faces.append(tuple(start+n+i for i in reversed(range(n))))
    for i in range(n):
        j = (i+1)%n
        faces.append((start+i, start+n+i, start+n+j, start+j))

pitch_x = math.sqrt(3)*CELL_RADIUS
pitch_z = 1.5*CELL_RADIUS
inner_radius = CELL_RADIUS-WEB_THICKNESS/(2*math.cos(math.pi/6))
rows = math.ceil(HEIGHT/pitch_z)+2
cols = math.ceil(WIDTH/pitch_x)+3
for row in range(-1, rows):
    cz = row*pitch_z
    for col in range(-cols, cols+1):
        cx = col*pitch_x+(row%2)*pitch_x/2
        outer = [(cx+CELL_RADIUS*math.cos(math.pi/6+k*math.pi/3), cz+CELL_RADIUS*math.sin(math.pi/6+k*math.pi/3)) for k in range(6)]
        inner = [(cx+inner_radius*math.cos(math.pi/6+k*math.pi/3), cz+inner_radius*math.sin(math.pi/6+k*math.pi/3)) for k in range(6)]
        # Pointy-top tiling: vertices are rotated 30 degrees.
        for k in range(6):
            j = (k+1)%6
            web = [outer[k], outer[j], inner[j], inner[k]]
            for rect in regions:
                extrude(clip_rect(web, rect))
mesh = bpy.data.meshes.new('Clipped honeycomb lattice mesh')
mesh.from_pydata(vertices, [], faces)
mesh.materials.append(wood)
mesh.update()
o = bpy.data.objects.new('Parametric honeycomb partition', mesh)
bpy.context.collection.objects.link(o)
bevel = o.modifiers.new('Fine web edge highlights', 'BEVEL')
bevel.width = 0.004
bevel.segments = 2
o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')

for x in (-WIDTH/2+FRAME_WIDTH/2, WIDTH/2-FRAME_WIDTH/2):
    box('Outer vertical frame', (x, 0, HEIGHT/2), (FRAME_WIDTH, DEPTH+0.10, HEIGHT), frame_mat)
box('Top frame', (0, 0, HEIGHT-FRAME_WIDTH/2), (WIDTH, DEPTH+0.10, FRAME_WIDTH), frame_mat)
for a, b in [(-WIDTH/2, portal_l), (portal_r, WIDTH/2)]:
    box('Interrupted base frame', ((a+b)/2, 0, FRAME_WIDTH/2), (b-a, DEPTH+0.10, FRAME_WIDTH), frame_mat)
for x in (dl-FRAME_WIDTH/2, dr+FRAME_WIDTH/2):
    box('Door jamb', (x, 0, DOOR_HEIGHT/2), (FRAME_WIDTH, DEPTH+0.18, DOOR_HEIGHT), frame_mat)
box('Door lintel', (DOOR_CENTER, 0, DOOR_HEIGHT+FRAME_WIDTH/2), (DOOR_WIDTH+2*FRAME_WIDTH, DEPTH+0.18, FRAME_WIDTH), frame_mat)
# The clear opening has no threshold, so the doorway remains traversable.
for x in (-WIDTH/2+FRAME_WIDTH/2, dl-FRAME_WIDTH/2, dr+FRAME_WIDTH/2, WIDTH/2-FRAME_WIDTH/2):
    box('Floor anchor plate', (x, 0, 0.025), (0.32, 0.68, 0.05), frame_mat, 0.008)
    for y in (-0.245, 0.245):
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.035, depth=0.022, location=(x, y, 0.061))
        bpy.context.object.name = 'Visible anchor bolt'
        bpy.context.object.data.materials.append(metal)
box('Architectural floor', (0, 0, -0.13), (200, 200, 0.2), floor_mat, 0)

def light(loc, energy, size):
    bpy.ops.object.light_add(type='AREA', location=loc)
    o = bpy.context.object
    o.data.energy = energy
    o.data.size = size
    o.rotation_euler = (Vector((0, 0, 2.4))-o.location).to_track_quat('-Z', 'Y').to_euler()
light((0, -5, 10), 2100, 7)
light((-7, -2, 5), 1200, 5)
light((5, 4, 8), 2500, 6)
bpy.ops.object.camera_add(location=(10, -17, 9))
cam = bpy.context.object
cam.rotation_euler = (Vector((0, 0, 2.55))-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 13.7
scene = bpy.context.scene
scene.camera = cam
scene.render.engine = 'CYCLES'
scene.render.resolution_x = 1600
scene.render.resolution_y = 1050
scene.render.resolution_percentage = 100
scene.world.color = (0.25, 0.25, 0.25)
