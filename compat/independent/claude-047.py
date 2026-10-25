import bpy
import math
from mathutils import Vector


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in list(coll):
            if item.users == 0:
                coll.remove(item)


def mat(name, color, rough=0.6, metal=0.0):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m


def box(name, size, loc, material, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    ob.scale = size
    ob.data.materials.append(material)
    return ob


def cyl(name, radius, depth, loc, material, verts=32, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=verts,
                                        location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    ob.data.materials.append(material)
    return ob


def sphere(name, radius, loc, material, segs=20):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, segments=segs,
                                         ring_count=max(4, segs // 2), location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.data.materials.append(material)
    return ob


def add_camera(loc, target, lens=35.0):
    cam = bpy.data.objects.new("CourtyardCamera", bpy.data.cameras.new("CourtyardCamera"))
    cam.data.lens = lens
    cam.location = loc
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    return cam


clear_scene()

M_PAVING = mat("Court_PavingGrey", (0.42, 0.41, 0.38), rough=0.85)
M_PLAZA = mat("Court_PlazaStone", (0.62, 0.58, 0.50), rough=0.75)
M_WALL = mat("Court_WallPlaster", (0.78, 0.72, 0.60), rough=0.8)
M_COPING = mat("Court_Coping", (0.55, 0.52, 0.47), rough=0.7)
M_STONE = mat("Court_FountainStone", (0.70, 0.68, 0.62), rough=0.6)
M_WATER = mat("Court_Water", (0.10, 0.30, 0.38), rough=0.05)
M_SOIL = mat("Court_Soil", (0.14, 0.09, 0.05), rough=0.95)
M_LEAF = mat("Court_Foliage", (0.10, 0.28, 0.09), rough=0.8)
M_BARK = mat("Court_Bark", (0.20, 0.13, 0.08), rough=0.85)
M_METAL = mat("Court_DarkMetal", (0.05, 0.05, 0.05), rough=0.4, metal=0.9)
M_GLOBE = mat("Court_LampGlobe", (0.95, 0.90, 0.70), rough=0.25)

# --- ground and central paving disc --------------------------------------
box("Court_GroundPaving", (17.0, 17.0, 0.2), (0.0, 0.0, -0.1), M_PAVING)
cyl("Court_PlazaRing", 5.6, 0.06, (0.0, 0.0, 0.02), M_COPING, verts=48)
cyl("Court_PlazaDisc", 5.2, 0.08, (0.0, 0.0, 0.04), M_PLAZA, verts=48)


# --- perimeter walls (opening on the south side) -------------------------
def wall(name, size, loc):
    box(name + "_Body", size, (loc[0], loc[1], size[2] / 2.0), M_WALL)
    box(name + "_Coping", (size[0] + 0.14, size[1] + 0.14, 0.12),
        (loc[0], loc[1], size[2] + 0.06), M_COPING)


WALL_H = 1.4
wall("Wall_North", (16.0, 0.4, WALL_H), (0.0, 8.0))
wall("Wall_East", (0.4, 16.0, WALL_H), (8.0, 0.0))
wall("Wall_West", (0.4, 16.0, WALL_H), (-8.0, 0.0))
wall("Wall_SouthLeft", (5.6, 0.4, WALL_H), (-5.2, -8.0))
wall("Wall_SouthRight", (5.6, 0.4, WALL_H), (5.2, -8.0))

for i, (px, py) in enumerate(((-8.0, 8.0), (8.0, 8.0), (-8.0, -8.0), (8.0, -8.0),
                              (-2.4, -8.0), (2.4, -8.0))):
    box("Pilaster_%02d" % (i + 1), (0.7, 0.7, WALL_H + 0.55),
        (px, py, (WALL_H + 0.55) / 2.0), M_WALL)
    box("PilasterCap_%02d" % (i + 1), (0.85, 0.85, 0.14), (px, py, WALL_H + 0.62), M_COPING)

# --- fountain ------------------------------------------------------------
cyl("Fountain_BasinWall", 2.20, 0.60, (0.0, 0.0, 0.30), M_STONE, verts=48)
cyl("Fountain_BasinRim", 2.34, 0.14, (0.0, 0.0, 0.63), M_COPING, verts=48)
cyl("Fountain_WaterSurface", 2.02, 0.44, (0.0, 0.0, 0.24), M_WATER, verts=48)
cyl("Fountain_Pedestal", 0.42, 0.95, (0.0, 0.0, 0.95), M_STONE)
bpy.ops.mesh.primitive_cone_add(radius1=0.22, radius2=1.10, depth=0.36, vertices=40,
                                location=(0.0, 0.0, 1.58))
bowl = bpy.context.object
bowl.name = "Fountain_UpperBowl"
bowl.data.materials.append(M_STONE)
cyl("Fountain_BowlWater", 1.02, 0.08, (0.0, 0.0, 1.73), M_WATER, verts=40)
cyl("Fountain_Stem", 0.14, 0.55, (0.0, 0.0, 2.03), M_STONE, verts=20)
sphere("Fountain_Finial", 0.20, (0.0, 0.0, 2.38), M_STONE)
cyl("Fountain_Jet", 0.035, 0.45, (0.0, 0.0, 2.72), M_WATER, verts=12)


# --- planters with shrubs ------------------------------------------------
def planter(idx, loc, angle):
    name = "Planter_%02d" % idx
    box(name + "_Box", (2.4, 0.9, 0.65), (loc[0], loc[1], 0.325), M_WALL, rot=(0, 0, angle))
    box(name + "_Rim", (2.55, 1.05, 0.12), (loc[0], loc[1], 0.69), M_COPING, rot=(0, 0, angle))
    box(name + "_Soil", (2.2, 0.7, 0.06), (loc[0], loc[1], 0.70), M_SOIL, rot=(0, 0, angle))
    for k in range(3):
        off = (k - 1) * 0.75
        ox = loc[0] + math.cos(angle) * off
        oy = loc[1] + math.sin(angle) * off
        sphere(name + "_Shrub_%d" % (k + 1), 0.34, (ox, oy, 0.95), M_LEAF, segs=16)


RING = 6.4
for i in range(4):
    a = math.radians(45 + i * 90)
    planter(i + 1, (math.cos(a) * RING, math.sin(a) * RING), a + math.pi / 2.0)

# --- accent trees --------------------------------------------------------
for i, (tx, ty) in enumerate(((-6.3, 0.0), (6.3, 0.0))):
    cyl("Tree_%02d_Trunk" % (i + 1), 0.16, 2.1, (tx, ty, 1.05), M_BARK, verts=12)
    sphere("Tree_%02d_Crown" % (i + 1), 1.05, (tx, ty, 2.55), M_LEAF, segs=18)

# --- benches -------------------------------------------------------------
for i, (bx, by) in enumerate(((0.0, 4.6), (0.0, -4.6))):
    box("Bench_%02d_Seat" % (i + 1), (2.2, 0.5, 0.1), (bx, by, 0.48), M_BARK)
    for s in (-0.85, 0.85):
        box("Bench_%02d_Leg" % (i + 1), (0.14, 0.45, 0.43), (bx + s, by, 0.215), M_METAL)

# --- lamp posts ----------------------------------------------------------
for i, (lx, ly) in enumerate(((-4.6, -4.6), (4.6, 4.6))):
    cyl("Lamp_%02d_Base" % (i + 1), 0.20, 0.25, (lx, ly, 0.12), M_METAL, verts=14)
    cyl("Lamp_%02d_Post" % (i + 1), 0.08, 3.0, (lx, ly, 1.5), M_METAL, verts=14)
    sphere("Lamp_%02d_Globe" % (i + 1), 0.24, (lx, ly, 3.12), M_GLOBE, segs=16)
    lit = bpy.data.objects.new("Lamp_%02d_Light" % (i + 1),
                               bpy.data.lights.new("LampData_%02d" % (i + 1), 'POINT'))
    lit.data.energy = 120.0
    lit.location = (lx, ly, 3.12)
    bpy.context.collection.objects.link(lit)

# --- sun and camera ------------------------------------------------------
sun = bpy.data.objects.new("Court_Sun", bpy.data.lights.new("Court_SunData", 'SUN'))
sun.data.energy = 3.2
sun.location = (6.0, -6.0, 12.0)
sun.rotation_euler = (math.radians(52), math.radians(12), math.radians(-40))
bpy.context.collection.objects.link(sun)

add_camera((11.0, -12.5, 7.2), (0.0, 0.0, 1.4))
bpy.context.scene.world = bpy.data.worlds.new("CourtyardWorld")
bpy.context.scene.world.use_nodes = True
bg = bpy.context.scene.world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.45, 0.58, 0.75, 1.0)
bg.inputs[1].default_value = 0.6
