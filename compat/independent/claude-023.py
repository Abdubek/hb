import bpy
import math
from mathutils import Vector


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


def make_material(name, color, roughness=0.6, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    return mat


def assign(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    return obj


def cylinder(name, radius, depth, location, mat, verts=24, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius,
                                        depth=depth, location=location,
                                        rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    bpy.ops.object.shade_smooth()
    return assign(obj, mat)


def cone(name, r1, r2, depth, location, mat, verts=32):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2,
                                    depth=depth, location=location)
    obj = bpy.context.active_object
    obj.name = name
    bpy.ops.object.shade_smooth()
    return assign(obj, mat)


def beam(name, p0, p1, radius, mat, verts=10):
    """Round structural member spanning two world-space points."""
    p0, p1 = Vector(p0), Vector(p1)
    v = p1 - p0
    obj = cylinder(name, radius, v.length, (p0 + p1) / 2.0, mat, verts=verts)
    obj.rotation_euler = v.to_track_quat('Z', 'Y').to_euler()
    return obj


clear_scene()

STEEL = make_material('MAT_Steel', (0.55, 0.57, 0.60), roughness=0.40, metallic=1.0)
TANK = make_material('MAT_TankPaint', (0.78, 0.79, 0.76), roughness=0.55)
ROOF = make_material('MAT_RoofPaint', (0.16, 0.32, 0.42), roughness=0.50)
GRASS = make_material('MAT_Ground', (0.26, 0.32, 0.18), roughness=0.95)
CONCRETE = make_material('MAT_Concrete', (0.62, 0.61, 0.58), roughness=0.85)

# --- site -----------------------------------------------------------------
bpy.ops.mesh.primitive_plane_add(size=40.0, location=(0, 0, 0))
bpy.context.active_object.name = 'Ground'
assign(bpy.context.active_object, GRASS)

# --- geometry parameters --------------------------------------------------
BASE_R = 3.4          # leg spread at the footings
TOP_R = 1.9           # leg spread where the legs meet the tank skirt
LEG_TOP_Z = 8.0
TANK_R = 2.4
TANK_H = 3.2
TANK_BOTTOM_Z = LEG_TOP_Z + 0.2
LEG_COUNT = 4


def leg_point(i, t):
    """Point on leg i, t=0 at the footing, t=1 at the top of the leg."""
    a = math.radians(45 + i * (360.0 / LEG_COUNT))
    r = BASE_R + (TOP_R - BASE_R) * t
    return Vector((r * math.cos(a), r * math.sin(a), LEG_TOP_Z * t))


# --- tank -----------------------------------------------------------------
tank_mid = TANK_BOTTOM_Z + TANK_H / 2.0
cylinder('Tank_Shell', TANK_R, TANK_H, (0, 0, tank_mid), TANK, verts=40)
cone('Tank_BottomCone', TANK_R, 0.7, 1.4, (0, 0, TANK_BOTTOM_Z - 0.7), TANK, verts=40)
cone('Tank_Roof', TANK_R + 0.12, 0.25, 1.3,
     (0, 0, TANK_BOTTOM_Z + TANK_H + 0.65), ROOF, verts=40)
cylinder('Tank_RoofHatch', 0.35, 0.30, (0.9, 0, TANK_BOTTOM_Z + TANK_H + 0.55),
         STEEL, verts=16)
cylinder('Tank_VentPipe', 0.16, 1.0, (0, 0, TANK_BOTTOM_Z + TANK_H + 1.6), STEEL, verts=16)

for idx, z in enumerate((TANK_BOTTOM_Z + 0.7, TANK_BOTTOM_Z + TANK_H - 0.7)):
    bpy.ops.mesh.primitive_torus_add(major_radius=TANK_R + 0.04, minor_radius=0.07,
                                     major_segments=40, minor_segments=8,
                                     location=(0, 0, z))
    band = bpy.context.active_object
    band.name = 'Tank_Band_%d' % (idx + 1)
    bpy.ops.object.shade_smooth()
    assign(band, STEEL)

# downpipe from the tank to the ground
beam('Riser_Pipe', (0, 0, 0.1), (0, 0, TANK_BOTTOM_Z - 1.2), 0.22, STEEL, verts=16)

# --- legs, footings, bracing ---------------------------------------------
for i in range(LEG_COUNT):
    p0 = leg_point(i, 0.0)
    p1 = leg_point(i, 1.0)
    beam('Leg_%d' % (i + 1), p0 + Vector((0, 0, 0.15)), p1, 0.16, STEEL, verts=14)
    cylinder('Footing_%d' % (i + 1), 0.55, 0.4, (p0.x, p0.y, 0.18), CONCRETE, verts=20)

for level, t in enumerate((0.34, 0.66, 0.98)):
    for i in range(LEG_COUNT):
        j = (i + 1) % LEG_COUNT
        beam('Girt_L%d_%d' % (level + 1, i + 1),
             leg_point(i, t), leg_point(j, t), 0.075, STEEL)

for level, (ta, tb) in enumerate(((0.02, 0.34), (0.34, 0.66), (0.66, 0.98))):
    for i in range(LEG_COUNT):
        j = (i + 1) % LEG_COUNT
        beam('Brace_L%d_%dA' % (level + 1, i + 1),
             leg_point(i, ta), leg_point(j, tb), 0.055, STEEL, verts=8)
        beam('Brace_L%d_%dB' % (level + 1, i + 1),
             leg_point(j, ta), leg_point(i, tb), 0.055, STEEL, verts=8)

# --- catwalk handrail around the tank base -------------------------------
bpy.ops.mesh.primitive_torus_add(major_radius=TANK_R + 0.55, minor_radius=0.06,
                                 major_segments=48, minor_segments=8,
                                 location=(0, 0, TANK_BOTTOM_Z + 1.15))
rail = bpy.context.active_object
rail.name = 'Catwalk_Handrail'
bpy.ops.object.shade_smooth()
assign(rail, STEEL)

# --- ladder ---------------------------------------------------------------
LADDER_Y = -(TANK_R + 0.5)
LADDER_TOP = TANK_BOTTOM_Z + 1.2
for sx, tag in ((-0.32, 'L'), (0.32, 'R')):
    beam('Ladder_Rail_%s' % tag, (sx, LADDER_Y, 0.6), (sx, LADDER_Y, LADDER_TOP),
         0.045, STEEL, verts=10)

rung_z = 0.9
rung_i = 0
while rung_z < LADDER_TOP - 0.2:
    beam('Ladder_Rung_%02d' % rung_i, (-0.32, LADDER_Y, rung_z),
         (0.32, LADDER_Y, rung_z), 0.03, STEEL, verts=8)
    rung_z += 0.38
    rung_i += 1

for k, z in enumerate((2.6, 5.4, LADDER_TOP - 0.3)):
    beam('Ladder_Standoff_%d' % (k + 1), (0, LADDER_Y, z), (0, LADDER_Y + 0.7, z),
         0.035, STEEL, verts=8)

# --- lighting and camera --------------------------------------------------
bpy.ops.object.light_add(type='SUN', location=(8, -10, 16))
sun = bpy.context.active_object
sun.name = 'Sun'
sun.data.energy = 4.0
sun.rotation_euler = (Vector((0, 0, 6)) - sun.location).to_track_quat('-Z', 'Y').to_euler()

target = Vector((0, 0, 6.2))
bpy.ops.object.camera_add(location=(16, -19, 12))
cam = bpy.context.active_object
cam.name = 'Camera_Main'
cam.data.lens = 45
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam
