import bpy, math, random
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)
random.seed(113)

LENGTH = 11.6
RETURN_LENGTH = 2.8
COURSES = 18
PITCH = 0.26
BRICK_MODULE = 0.61
JOINT = 0.016
THICKNESS = 0.30
WINDOW_LEFT = -1.70
WINDOW_RIGHT = 1.70
WINDOW_BOTTOM = 6*PITCH
WINDOW_TOP = 14*PITCH
HEIGHT = COURSES*PITCH

def material(name, color, metallic=0, roughness=0.65):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    return m

bricks = []
for i in range(8):
    m = material('Fired clay variation %02d' % i, (0.30+0.028*i, 0.075+0.013*i, 0.035+0.008*i))
    nodes, links = m.node_tree.nodes, m.node_tree.links
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 105
    noise.inputs['Detail'].default_value = 2
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.24
    bump.inputs['Distance'].default_value = 0.024
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], nodes.get('Principled BSDF').inputs['Normal'])
    bricks.append(m)
mortar = material('Recessed warm mortar', (0.49, 0.44, 0.36), roughness=0.9)
stone = material('Sandstone sill and coping', (0.67, 0.59, 0.43), roughness=0.63)
frame_mat = material('Painted charcoal window frame', (0.055, 0.075, 0.077), 0.25, 0.32)
glass = material('Subtle blue window glass', (0.25, 0.46, 0.55), 0.12, 0.16)
glass.node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value = 0.65
glass.node_tree.nodes.get('Principled BSDF').inputs['IOR'].default_value = 1.45
floor_mat = material('Concrete display floor', (0.27, 0.29, 0.28), roughness=0.83)

def box(name, loc, dims, mat, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        b = o.modifiers.new('Rounded arrises', 'BEVEL')
        b.width = bevel
        b.segments = 2
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

half = LENGTH/2
# Mortar cores are split around the opening; there is no hidden wall in the window.
core_depth = THICKNESS-0.045
for a, b in [(-half, WINDOW_LEFT), (WINDOW_RIGHT, half)]:
    box('Mortar pier', ((a+b)/2, THICKNESS/2, HEIGHT/2), (b-a, core_depth, HEIGHT-JOINT), mortar)
for za, zb in [(0, WINDOW_BOTTOM), (WINDOW_TOP, HEIGHT)]:
    box('Mortar below or above window', ((WINDOW_LEFT+WINDOW_RIGHT)/2, THICKNESS/2, (za+zb)/2), (WINDOW_RIGHT-WINDOW_LEFT, core_depth, zb-za-JOINT), mortar)
for x in (-half+THICKNESS/2, half-THICKNESS/2):
    box('Return mortar core', (x, (THICKNESS+RETURN_LENGTH)/2, HEIGHT/2), (core_depth, RETURN_LENGTH-THICKNESS, HEIGHT-JOINT), mortar)

def intervals(start, end, module, offset):
    k = math.floor((start-offset)/module)
    while offset+k*module < end-1e-7:
        a = max(start, offset+k*module)
        b = min(end, offset+(k+1)*module)
        if b-a > JOINT+0.025:
            yield a, b
        k += 1

for row in range(COURSES):
    z = (row+0.5)*PITCH
    offset = -half+(row%2)*BRICK_MODULE/2
    # On alternating courses the return bricks own the corner volumes.
    front_start = -half+(THICKNESS if row%2 else 0)
    front_end = half-(THICKNESS if row%2 else 0)
    occupied = [(front_start, front_end)]
    if 6 <= row < 14:
        occupied = [(front_start, WINDOW_LEFT), (WINDOW_RIGHT, front_end)]
    for a, b in intervals(front_start, front_end, BRICK_MODULE, offset):
        for lo, hi in occupied:
            aa, bb = max(a, lo), min(b, hi)
            if bb-aa > JOINT+0.025:
                box('Front course %02d brick' % (row+1), ((aa+bb)/2, THICKNESS/2+random.uniform(-0.002, 0.002), z), (bb-aa-JOINT, THICKNESS, PITCH-JOINT), random.choice(bricks), 0.008)
    return_start = 0 if row%2 else THICKNESS
    for side in (-1, 1):
        x = side*(half-THICKNESS/2)
        for a, b in intervals(return_start, RETURN_LENGTH, BRICK_MODULE, (row%2)*BRICK_MODULE/2):
            box('Bonded corner return course %02d' % (row+1), (x, (a+b)/2, z), (THICKNESS, b-a-JOINT, PITCH-JOINT), random.choice(bricks), 0.008)

# Projecting sill and a segmented stone lintel frame the masonry opening.
ww = WINDOW_RIGHT-WINDOW_LEFT
wc = (WINDOW_RIGHT+WINDOW_LEFT)/2
box('Projecting window sill', (wc, THICKNESS/2-0.075, WINDOW_BOTTOM-0.065), (ww+0.30, 0.57, 0.13), stone, 0.018)
for i in range(5):
    segment = (ww+0.30)/5
    box('Stone lintel block', (wc-(ww+0.30)/2+(i+0.5)*segment, THICKNESS/2-0.025, WINDOW_TOP+0.12), (segment-0.008, 0.39, 0.24), stone, 0.012)

# Recessed four-light window, with actual solid glass panes.
frame_y = 0.19
frame_w = 0.085
for x in (WINDOW_LEFT+frame_w/2, WINDOW_RIGHT-frame_w/2):
    box('Window jamb', (x, frame_y, (WINDOW_BOTTOM+WINDOW_TOP)/2), (frame_w, 0.11, WINDOW_TOP-WINDOW_BOTTOM), frame_mat, 0.01)
for z in (WINDOW_BOTTOM+frame_w/2, WINDOW_TOP-frame_w/2):
    box('Window horizontal frame', (wc, frame_y, z), (ww, 0.11, frame_w), frame_mat, 0.01)
midz = (WINDOW_BOTTOM+WINDOW_TOP)/2
box('Window mullion', (wc, frame_y-0.008, midz), (0.075, 0.12, WINDOW_TOP-WINDOW_BOTTOM), frame_mat, 0.008)
box('Window transom', (wc, frame_y-0.008, midz), (ww, 0.12, 0.075), frame_mat, 0.008)
for xa, xb in [(WINDOW_LEFT+frame_w, wc-0.038), (wc+0.038, WINDOW_RIGHT-frame_w)]:
    for za, zb in [(WINDOW_BOTTOM+frame_w, midz-0.038), (midz+0.038, WINDOW_TOP-frame_w)]:
        box('Glass pane', ((xa+xb)/2, frame_y+0.016, (za+zb)/2), (xb-xa, 0.018, zb-za), glass, 0.003)

# Individual coping stones retain visible joints across all three wall runs.
for a, b in intervals(-half-0.045, half+0.045, 0.86, -half-0.045):
    box('Front coping stone', ((a+b)/2, THICKNESS/2, HEIGHT+0.085), (b-a-0.01, 0.43, 0.17), stone, 0.012)
for side in (-1, 1):
    for a, b in intervals(THICKNESS+0.065, RETURN_LENGTH+0.045, 0.86, THICKNESS+0.065):
        box('Return coping stone', (side*(half-THICKNESS/2), (a+b)/2, HEIGHT+0.085), (0.43, b-a-0.01, 0.17), stone, 0.012)
box('Foundation plinth', (0, 1.1, -0.16), (LENGTH+0.8, RETURN_LENGTH+1.1, 0.30), floor_mat, 0.035)
box('Ground', (0, 0, -0.35), (200, 200, 0.1), floor_mat)

def light(loc, energy, size):
    bpy.ops.object.light_add(type='AREA', location=loc)
    o = bpy.context.object
    o.data.energy = energy
    o.data.size = size
    o.rotation_euler = (Vector((0, 0.8, 2))-o.location).to_track_quat('-Z', 'Y').to_euler()
light((-5, -7, 10), 2300, 7)
light((7, -3, 7), 1600, 5)
light((1, 6, 9), 2400, 5)
bpy.ops.object.camera_add(location=(11, -16, 9))
cam = bpy.context.object
cam.rotation_euler = (Vector((0, 0.8, 2.1))-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 14.8
scene = bpy.context.scene
scene.camera = cam
scene.render.engine = 'CYCLES'
scene.render.resolution_x = 1600
scene.render.resolution_y = 1050
scene.render.resolution_percentage = 100
scene.world.color = (0.24, 0.24, 0.24)
