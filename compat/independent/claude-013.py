import bpy
from math import radians
from mathutils import Vector

PLINTH_W, PLINTH_D, PLINTH_H = 0.440, 0.360, 0.076
FOOT_H = 0.018
PLINTH_TOP = FOOT_H + PLINTH_H
PLATTER_R = 0.150


def reset_scene():
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for mesh in list(bpy.data.meshes):
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)


def material(name, color, roughness=0.5, metallic=0.0, alpha=1.0):
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], alpha)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if alpha < 1.0:
        bsdf.inputs["Alpha"].default_value = alpha
        # Transparency flag moved from blend_method to surface_render_method in 4.2+.
        if hasattr(mat, "surface_render_method"):
            mat.surface_render_method = 'BLENDED'
        elif hasattr(mat, "blend_method"):
            mat.blend_method = 'BLEND'
    return mat


def finish(obj, name, mat, bevel=0.0):
    obj.name = name
    obj.data.name = name
    obj.data.materials.append(mat)
    if bevel > 0.0:
        mod = obj.modifiers.new("Bevel", 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        mod.limit_method = 'ANGLE'
        mod.angle_limit = radians(40.0)
    return obj


def box(name, size, location, mat, bevel=0.0, rotation=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(obj, name, mat, bevel)


def cyl(name, radius, depth, location, mat, rotation=(0.0, 0.0, 0.0), verts=48, bevel=0.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth,
                                        location=location, rotation=rotation)
    return finish(bpy.context.active_object, name, mat, bevel)


def parent_keep_transform(child, parent):
    child.parent = parent
    child.matrix_parent_inverse = parent.matrix_world.inverted()


def build_plinth(mats):
    box("Plinth", (PLINTH_W, PLINTH_D, PLINTH_H), (0.0, 0.0, FOOT_H + PLINTH_H / 2.0),
        mats['wood'], bevel=0.006)
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        cyl("Foot_%d" % (i + 1), 0.017, FOOT_H,
            (sx * (PLINTH_W / 2.0 - 0.036), sy * (PLINTH_D / 2.0 - 0.034), FOOT_H / 2.0),
            mats['rubber'], verts=24)
    # Shallow recess the platter sits down into.
    cyl("Platter_Well", PLATTER_R + 0.008, 0.006, (0.0, 0.022, PLINTH_TOP - 0.002),
        mats['dark'], verts=64)


def build_platter(mats):
    cx, cy = 0.0, 0.022
    base_z = PLINTH_TOP + 0.002
    cyl("Platter", PLATTER_R, 0.016, (cx, cy, base_z + 0.008), mats['metal'], verts=64, bevel=0.002)
    cyl("Slipmat", PLATTER_R - 0.003, 0.003, (cx, cy, base_z + 0.017), mats['felt'], verts=64)
    cyl("Record", PLATTER_R + 0.002, 0.002, (cx, cy, base_z + 0.020), mats['vinyl'], verts=64)
    cyl("Record_Label", 0.051, 0.001, (cx, cy, base_z + 0.0215), mats['label'], verts=48)
    cyl("Spindle", 0.0035, 0.030, (cx, cy, base_z + 0.030), mats['chrome'], verts=16)


def build_tonearm(mats):
    pivot_pos = Vector((0.172, 0.126, PLINTH_TOP))
    cyl("Arm_Base", 0.028, 0.014, (pivot_pos.x, pivot_pos.y, pivot_pos.z + 0.007),
        mats['metal'], verts=32, bevel=0.002)
    cyl("Arm_Post", 0.011, 0.034, (pivot_pos.x, pivot_pos.y, pivot_pos.z + 0.028),
        mats['chrome'], verts=24)

    pivot = bpy.data.objects.new("Tonearm_Pivot", None)
    pivot.empty_display_size = 0.03
    pivot.location = (pivot_pos.x, pivot_pos.y, pivot_pos.z + 0.046)
    bpy.context.collection.objects.link(pivot)
    bpy.context.view_layer.update()

    px, py, pz = pivot.location
    # Arm parts are laid out along -X from the pivot, then swung inward as one unit.
    tube = cyl("Tonearm_Tube", 0.0048, 0.230, (px - 0.085, py, pz), mats['chrome'],
               rotation=(0.0, radians(90), 0.0), verts=24)
    weight = cyl("Counterweight", 0.018, 0.028, (px + 0.042, py, pz), mats['dark'],
                 rotation=(0.0, radians(90), 0.0), verts=32, bevel=0.003)
    head = box("Headshell", (0.030, 0.017, 0.012), (px - 0.196, py, pz - 0.006),
               mats['metal'], bevel=0.002)
    cart = box("Cartridge", (0.020, 0.013, 0.010), (px - 0.200, py, pz - 0.016),
               mats['label'], bevel=0.002)
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.0022, radius2=0.0, depth=0.010,
                                    location=(px - 0.206, py, pz - 0.025),
                                    rotation=(radians(180), 0.0, 0.0))
    stylus = finish(bpy.context.active_object, "Stylus", mats['chrome'])
    lever = box("Cue_Lever", (0.036, 0.008, 0.006), (px - 0.030, py - 0.020, pz - 0.014),
                mats['dark'], bevel=0.002)

    for part in (tube, weight, head, cart, stylus, lever):
        parent_keep_transform(part, pivot)
    pivot.rotation_euler = (0.0, 0.0, radians(-34.0))

    box("Arm_Rest", (0.014, 0.030, 0.026),
        (pivot_pos.x - 0.012, pivot_pos.y + 0.050, PLINTH_TOP + 0.013), mats['dark'], bevel=0.003)


def build_controls(mats):
    cyl("Speed_Knob", 0.020, 0.012, (-0.170, -0.128, PLINTH_TOP + 0.006), mats['dark'],
        verts=32, bevel=0.002)
    cyl("Power_Knob", 0.014, 0.010, (-0.170, -0.060, PLINTH_TOP + 0.005), mats['dark'],
        verts=32, bevel=0.002)
    box("Pitch_Slider_Slot", (0.020, 0.070, 0.004), (0.176, -0.098, PLINTH_TOP + 0.001), mats['dark'])
    box("Pitch_Slider_Knob", (0.016, 0.016, 0.008), (0.176, -0.088, PLINTH_TOP + 0.006),
        mats['metal'], bevel=0.002)
    cyl("Strobe_Light", 0.005, 0.004, (0.176, -0.038, PLINTH_TOP + 0.002), mats['label'], verts=16)


def build_dust_cover(mats):
    hinge_y = PLINTH_D / 2.0 - 0.004
    hinge_z = PLINTH_TOP + 0.150
    for side, x in (("L", -0.120), ("R", 0.120)):
        box("Cover_Hinge_" + side, (0.030, 0.020, 0.026), (x, hinge_y, PLINTH_TOP + 0.010),
            mats['dark'], bevel=0.003)

    hinge = bpy.data.objects.new("Cover_Hinge_Pivot", None)
    hinge.empty_display_size = 0.04
    hinge.location = (0.0, hinge_y, hinge_z)
    bpy.context.collection.objects.link(hinge)
    bpy.context.view_layer.update()

    depth = PLINTH_D + 0.010
    width = PLINTH_W + 0.016
    height = 0.140
    panels = [
        box("Cover_Top", (width, depth, 0.006), (0.0, hinge_y - depth / 2.0, hinge_z),
            mats['acrylic']),
        box("Cover_Front", (width, 0.006, height), (0.0, hinge_y - depth, hinge_z - height / 2.0),
            mats['acrylic']),
        box("Cover_Side_L", (0.006, depth, height),
            (-width / 2.0, hinge_y - depth / 2.0, hinge_z - height / 2.0), mats['acrylic']),
        box("Cover_Side_R", (0.006, depth, height),
            (width / 2.0, hinge_y - depth / 2.0, hinge_z - height / 2.0), mats['acrylic']),
    ]
    for panel in panels:
        parent_keep_transform(panel, hinge)
    # Negative X rotation lifts the forward edge, leaving the lid ajar.
    hinge.rotation_euler = (radians(-32.0), 0.0, 0.0)


def add_lighting():
    sun_data = bpy.data.lights.new("Key_Sun", type='SUN')
    sun_data.energy = 3.0
    sun = bpy.data.objects.new("Key_Sun", sun_data)
    sun.rotation_euler = (radians(50), radians(10), radians(-35))
    bpy.context.collection.objects.link(sun)

    area_data = bpy.data.lights.new("Fill_Area", type='AREA')
    area_data.energy = 120.0
    area_data.size = 1.4
    area = bpy.data.objects.new("Fill_Area", area_data)
    area.location = (-0.9, -0.8, 1.1)
    area.rotation_euler = (radians(45), 0.0, radians(-45))
    bpy.context.collection.objects.link(area)


def add_camera(location, target, lens=50.0):
    cam_data = bpy.data.cameras.new("Scene_Camera")
    cam_data.lens = lens
    cam = bpy.data.objects.new("Scene_Camera", cam_data)
    cam.location = location
    cam.rotation_euler = (Vector(target) - Vector(location)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    return cam


def main():
    reset_scene()
    mats = {
        'wood': material("Plinth_Walnut", (0.20, 0.105, 0.055), roughness=0.42),
        'dark': material("Matte_Black", (0.030, 0.030, 0.033), roughness=0.65),
        'metal': material("Brushed_Alu", (0.62, 0.63, 0.65), roughness=0.34, metallic=1.0),
        'chrome': material("Polished_Chrome", (0.80, 0.81, 0.83), roughness=0.12, metallic=1.0),
        'rubber': material("Foot_Rubber", (0.045, 0.045, 0.048), roughness=0.9),
        'felt': material("Slipmat_Felt", (0.10, 0.10, 0.12), roughness=0.95),
        'vinyl': material("Vinyl_Black", (0.015, 0.015, 0.017), roughness=0.28),
        'label': material("Label_Red", (0.52, 0.07, 0.06), roughness=0.55),
        'acrylic': material("Dust_Cover_Acrylic", (0.72, 0.76, 0.80), roughness=0.06, alpha=0.22),
    }
    build_plinth(mats)
    build_platter(mats)
    build_tonearm(mats)
    build_controls(mats)
    build_dust_cover(mats)

    box("Table_Surface", (1.8, 1.4, 0.020), (0.0, 0.0, -0.010),
        material("Table_Grey", (0.28, 0.29, 0.30), roughness=0.7))

    add_lighting()
    add_camera((0.62, -0.72, 0.52), (0.0, 0.010, 0.130))


main()
