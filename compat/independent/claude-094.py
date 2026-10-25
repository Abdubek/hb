import bpy
import math
from mathutils import Vector


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in list(bpy.data.meshes):
        if block.users == 0:
            bpy.data.meshes.remove(block)


def make_material(name, color, roughness=0.5, metallic=0.0, emission=None):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if emission is not None:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 4.0
    return mat


def add_box(name, size, location, material, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = Vector(size) * 0.5
    bpy.ops.object.transform_apply(scale=True)
    obj.data.materials.append(material)
    return obj


def add_cyl(name, radius, depth, location, material, rotation=(0, 0, 0), verts=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth,
                                        location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(material)
    return obj


clear_scene()

steel = make_material("PanelSteel", (0.62, 0.64, 0.66), roughness=0.35, metallic=0.9)
dark = make_material("PanelDark", (0.09, 0.09, 0.10), roughness=0.6)
glass = make_material("GaugeGlass", (0.85, 0.88, 0.90), roughness=0.1)
face = make_material("GaugeFace", (0.93, 0.92, 0.88), roughness=0.7)
needle = make_material("NeedleRed", (0.70, 0.08, 0.06), roughness=0.4)
toggle = make_material("ToggleChrome", (0.80, 0.82, 0.85), roughness=0.2, metallic=1.0)
lamp_on = make_material("LampGreen", (0.05, 0.5, 0.12), roughness=0.3, emission=(0.1, 1.0, 0.2))
lamp_warn = make_material("LampAmber", (0.6, 0.35, 0.02), roughness=0.3, emission=(1.0, 0.55, 0.05))

# Wall slab the panel is mounted to.
add_box("Wall", (3.2, 0.12, 2.4), (0.0, 0.30, 1.2),
        make_material("WallPlaster", (0.55, 0.56, 0.54), roughness=0.9))

# Panel enclosure: body plus a bevelled front face plate.
add_box("PanelBody", (1.60, 0.26, 1.05), (0.0, 0.11, 1.35), dark)
plate = add_box("PanelFacePlate", (1.52, 0.05, 0.97), (0.0, -0.02, 1.35), steel)
bev = plate.modifiers.new("Bevel", 'BEVEL')
bev.width = 0.012
bev.segments = 2

for i, x in enumerate((-0.70, 0.70)):
    for j, z in enumerate((0.94, 1.76)):
        add_cyl("MountBolt_%d_%d" % (i, j), 0.022, 0.06, (x, -0.03, z), toggle,
                rotation=(math.pi / 2, 0, 0), verts=12)


def build_gauge(name, x, z, angle_deg):
    """Round dial: bezel ring, face, glass, tick marks and a needle."""
    add_cyl(name + "_Bezel", 0.155, 0.05, (x, -0.05, z), steel, rotation=(math.pi / 2, 0, 0), verts=32)
    add_cyl(name + "_Face", 0.135, 0.02, (x, -0.075, z), face, rotation=(math.pi / 2, 0, 0), verts=32)
    add_cyl(name + "_Glass", 0.140, 0.008, (x, -0.086, z), glass, rotation=(math.pi / 2, 0, 0), verts=32)
    a = math.radians(angle_deg)
    n = add_box(name + "_Needle", (0.010, 0.006, 0.115), (x, -0.090, z), needle,
                rotation=(0, a, 0))
    n.location = Vector((x + math.sin(a) * 0.048, -0.090, z + math.cos(a) * 0.048))
    add_cyl(name + "_Hub", 0.018, 0.014, (x, -0.094, z), dark, rotation=(math.pi / 2, 0, 0), verts=16)
    for t in range(9):
        ta = math.radians(-120 + t * 30)
        add_box(name + "_Tick_%d" % t,
                (0.007, 0.004, 0.024),
                (x + math.sin(ta) * 0.112, -0.088, z + math.cos(ta) * 0.112),
                dark, rotation=(0, ta, 0))


def build_switch(name, x, z, up=True):
    add_cyl(name + "_Base", 0.042, 0.03, (x, -0.055, z), steel, rotation=(math.pi / 2, 0, 0), verts=16)
    tilt = math.radians(-28 if up else 28)
    lever = add_cyl(name + "_Lever", 0.011, 0.10, (x, -0.09, z), toggle,
                    rotation=(math.pi / 2 + tilt, 0, 0), verts=12)
    lever.location = Vector((x, -0.075 - math.cos(tilt) * 0.04, z + math.sin(tilt) * 0.04))
    tip = add_cyl(name + "_Tip", 0.019, 0.02,
                  (x, -0.075 - math.cos(tilt) * 0.085, z + math.sin(tilt) * 0.085), dark,
                  rotation=(math.pi / 2 + tilt, 0, 0), verts=12)
    return tip


build_gauge("GaugePressure", -0.44, 1.60, -55)
build_gauge("GaugeVoltage", 0.02, 1.60, 15)
build_gauge("GaugeFlow", 0.48, 1.60, 70)

switch_x = (-0.55, -0.28, -0.01, 0.26, 0.53)
for i, x in enumerate(switch_x):
    build_switch("Switch_%d" % i, x, 1.20, up=(i % 2 == 0))
    add_box("SwitchLabel_%d" % i, (0.12, 0.006, 0.035), (x, -0.05, 1.11), dark)
    add_cyl("Indicator_%d" % i, 0.032, 0.035, (x, -0.055, 1.00),
            lamp_on if i % 2 == 0 else lamp_warn, rotation=(math.pi / 2, 0, 0), verts=16)

# Emergency stop button and a rotary selector knob flanking the switch row.
add_cyl("EStopCollar", 0.10, 0.05, (0.58, -0.06, 0.98), steel,
        rotation=(math.pi / 2, 0, 0), verts=24)
add_cyl("EStopButton", 0.085, 0.09, (0.58, -0.09, 0.98), needle,
        rotation=(math.pi / 2, 0, 0), verts=24)
add_cyl("SelectorKnob", 0.06, 0.07, (-0.58, -0.08, 0.98), dark,
        rotation=(math.pi / 2, 0, 0), verts=20)
add_box("SelectorMark", (0.008, 0.02, 0.05), (-0.58, -0.115, 1.008), face)

# Conduit entering the bottom of the enclosure.
add_cyl("Conduit", 0.035, 0.55, (0.30, 0.14, 0.55), steel, verts=16)
add_cyl("ConduitGland", 0.055, 0.06, (0.30, 0.14, 0.84), toggle, verts=16)

bpy.ops.object.light_add(type='AREA', location=(1.6, -2.6, 3.0))
key = bpy.context.active_object
key.name = "KeyLight"
key.data.energy = 500
key.data.size = 3.0
key.rotation_euler = (math.radians(52), 0, math.radians(35))

bpy.ops.object.light_add(type='AREA', location=(-2.2, -2.0, 1.4))
fill = bpy.context.active_object
fill.name = "FillLight"
fill.data.energy = 150
fill.data.size = 2.5
fill.rotation_euler = (math.radians(75), 0, math.radians(-50))

bpy.ops.object.camera_add(location=(1.9, -2.9, 2.15))
cam = bpy.context.active_object
cam.name = "Camera"
cam.data.lens = 50
direction = Vector((0.0, 0.0, 1.35)) - cam.location
cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam
