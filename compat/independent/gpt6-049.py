import bpy
import math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.45):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = roughness
    return m

silver = material('Anodized aluminum', (0.48, 0.55, 0.60), 0.8)
steel = material('Galvanized support steel', (0.23, 0.29, 0.33), 0.75)
blue = material('Photovoltaic silicon', (0.012, 0.046, 0.13), 0.4, 0.23)
backing = material('Dark panel backing', (0.025, 0.032, 0.043))
wire = material('Cell conductor silver', (0.32, 0.46, 0.61), 0.7)
concrete = material('Concrete footing', (0.48, 0.47, 0.43))
ground = material('Ground', (0.19, 0.23, 0.19))

angle = math.radians(26)
u = Vector((1, 0, 0))
v = Vector((0, math.cos(angle), math.sin(angle)))
n = u.cross(v)
origin = Vector((0, 0, 1.8))

def panel_point(x, y, z=0):
    return origin + u*x + v*y + n*z

def box(name, location, scale, mat, tilt=0, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    o = bpy.context.object
    o.name = name
    o.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.rotation_euler.x = tilt
    o.data.materials.append(mat)
    if bevel:
        mod = o.modifiers.new('Soft manufactured edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        o.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    return o

def beam(name, a, b, width=0.075):
    a, b = Vector(a), Vector(b)
    o = box(name, (a+b)/2, (width, width, (b-a).length), steel, bevel=0.008)
    o.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    return o

# Six individually framed modules in a three-by-two bank.
for col in range(3):
    for row in range(2):
        cx, cy = (col-1)*1.31, (row-0.5)*1.78
        tag = f'Module {col+1}-{row+1}'
        box(tag+' backing', panel_point(cx, cy), (1.24, 1.70, 0.065), backing, angle)
        for dx in (-0.615, 0.615):
            box(tag+' side rail', panel_point(cx+dx, cy, 0.025),
                (0.035, 1.73, 0.095), silver, angle, 0.006)
        for dy in (-0.85, 0.85):
            box(tag+' end rail', panel_point(cx, cy+dy, 0.025),
                (1.26, 0.035, 0.095), silver, angle, 0.006)
        for ix in range(6):
            for iy in range(8):
                x, y = cx+(ix-2.5)*0.197, cy+(iy-3.5)*0.204
                box(tag+f' silicon cell {ix+1}-{iy+1}', panel_point(x, y, 0.043),
                    (0.187, 0.194, 0.012), blue, angle)
        for ix in range(6):
            for offset in (-0.043, 0.043):
                x = cx+(ix-2.5)*0.197+offset
                box(tag+' collector strip', panel_point(x, cy, 0.05),
                    (0.004, 1.625, 0.003), wire, angle)
        box(tag+' rear junction box', panel_point(cx, cy, -0.08),
            (0.22, 0.15, 0.09), backing, angle, 0.015)

# Two trestles carry rails underneath the array.
for x in (-1.48, 1.48):
    ends = []
    for y in (-1.32, 1.32):
        top = panel_point(x, y, -0.16)
        base = Vector((top.x, top.y, 0.21))
        box('Concrete anchor block', (base.x, base.y, 0.1), (0.48, 0.48, 0.2), concrete, bevel=0.025)
        box('Bolted foot plate', (base.x, base.y, 0.22), (0.29, 0.29, 0.04), steel)
        beam('Vertical trestle post', base, top, 0.10)
        ends.append((base, top))
    beam('Inclined trestle rafter', panel_point(x, -1.72, -0.12), panel_point(x, 1.72, -0.12), 0.11)
    beam('Diagonal trestle brace', ends[0][0]+Vector((0, 0, 0.18)), ends[1][1], 0.065)
for y in (-1.32, 0, 1.32):
    beam('Continuous transverse mounting rail', panel_point(-1.98, y, -0.075), panel_point(1.98, y, -0.075), 0.075)
beam('Rear lateral cross brace', panel_point(-1.48, 1.32, -0.19),
     (1.48, panel_point(1.48, 1.32).y, 0.42), 0.055)
box('Site ground', (0, 0, -0.07), (12, 11, 0.1), ground)

bpy.ops.object.camera_add(location=(6.3, -8.2, 6.3))
cam = bpy.context.object
cam.name = 'Array overview camera'
cam.rotation_euler = (Vector((0, 0, 1.35))-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 6.8
bpy.context.scene.camera = cam
bpy.ops.object.light_add(type='AREA', location=(1, -4, 8))
bpy.context.object.data.energy = 1500
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 6
scene = bpy.context.scene
scene.world.color = (0.25, 0.25, 0.25)
scene.render.resolution_x = 1200
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
