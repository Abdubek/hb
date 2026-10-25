"""

The code for this art project:
https://www.artstation.com/artwork/48wX6L

Tested using: Blender 2.93

Author: Viktor Stepanov

License info: https://choosealicense.com/licenses/mit/

=============================================================================
MIT License

Copyright (c) 2021 Viktor Stepanov

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
=============================================================================

"""

import contextlib
import random
import time
import math

import bpy
import bmesh
import mathutils
import addon_utils

################################################################
# helpder functions BEGIN
################################################################


def enable_extra_curves():
    """
    Add Curve Extra Objects
    https://docs.blender.org/manual/en/2.93/addons/add_curve/extra_objects.html
    """
    loaded_default, loaded_state = addon_utils.check("add_curve_extra_objects")
    if not loaded_state:
        addon_utils.enable("add_curve_extra_objects")


def delete_all_objects():
    """
    Removing all of the objects from the scene
    """
    if bpy.context.active_object and bpy.context.active_object.mode == "EDIT":
        bpy.ops.object.editmode_toggle()

    for obj in bpy.data.objects:
        obj.hide_set(False)
        obj.hide_select = False
        obj.hide_viewport = False

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

    collection_names = [col.name for col in bpy.data.collections]
    for name in collection_names:
        bpy.data.collections.remove(bpy.data.collections[name])

    action_names = [action.name for action in bpy.data.actions]
    for name in action_names:
        bpy.data.actions.remove(bpy.data.actions[name])

    camera_names = [camera.name for camera in bpy.data.cameras]
    for name in camera_names:
        bpy.data.cameras.remove(bpy.data.cameras[name])

    curve_names = [curve.name for curve in bpy.data.curves]
    for name in curve_names:
        bpy.data.curves.remove(bpy.data.curves[name])

    # free the rest of the data materials, particles, textures, meshes, geo nodes
    bpy.ops.outliner.orphans_purge(
        do_local_ids=True,
        do_linked_ids=True,
        do_recursive=True,
    )


def get_random_pallet_color(context):
    return random.choice(context["colors"])


def active_obj():
    """
    returns the active object
    """
    return bpy.context.active_object


def time_seed():
    """
    Sets the random seed based on the time
    and copies the seed into the clipboard
    """
    seed = time.time()
    print(f"seed: {seed}")
    random.seed(seed)

    bpy.context.window_manager.clipboard = str(seed)

    return seed


def add_ctrl_empty(name=None):
    bpy.ops.object.empty_add(type="PLAIN_AXES", align="WORLD")
    empty_ctrl = bpy.context.active_object
    if name:
        empty_ctrl.name = name
    else:
        empty_ctrl.name = "empty.cntrl"
    return empty_ctrl


def apply_mat(material):
    obj = bpy.context.active_object
    obj.data.materials.append(material)


def make_active(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def track_empty(cam):
    bpy.ops.object.empty_add(type="PLAIN_AXES", align="WORLD", location=(0, 0, 0))
    empty = active_obj()
    empty.name = "tracker-target"

    make_active(cam)
    bpy.ops.object.constraint_add(type="TRACK_TO")
    bpy.context.object.constraints["Track To"].target = empty

    return empty


def setup_camera(loc, rot):
    bpy.ops.object.camera_add(
        enter_editmode=False, align="VIEW", location=loc, rotation=rot
    )
    cam = bpy.context.active_object
    bpy.context.scene.camera = cam
    bpy.context.object.data.lens = 70
    bpy.context.object.data.passepartout_alpha = 0.9

    empty = track_empty(cam)

    return empty


def set_1k_square_render_res():
    """
    Set the resolution of the rendered image to 1080 by 1080
    """
    bpy.context.scene.render.resolution_x = 1080
    bpy.context.scene.render.resolution_y = 1080


def set_scene_props(fps, loop_sec):
    """
    Set scene properties
    """
    frame_count = fps * loop_sec

    scene = bpy.context.scene
    scene.frame_end = frame_count

    world = bpy.data.worlds["World"]
    if "Background" in world.node_tree.nodes:
        world.node_tree.nodes["Background"].inputs[0].default_value = (0.0, 0.0, 0.0, 1)

    scene.render.fps = fps

    scene.frame_current = 1
    scene.frame_start = 1

    bpy.context.preferences.edit.use_negative_frames = True

    scene.eevee.use_bloom = True
    scene.eevee.bloom_intensity = 0.005

    scene.eevee.gtao_distance = 4
    scene.eevee.gtao_factor = 5

    scene.eevee.use_gtao = True
    scene.eevee.use_ssr = True
    scene.eevee.use_ssr_halfres = False
    scene.eevee.ssr_quality = 1

    scene.eevee.taa_render_samples = 64

    scene.view_settings.look = "Very High Contrast"

    set_1k_square_render_res()


def create_collection(col_name):
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.collection.create(name=col_name)
    collection = bpy.data.collections[col_name]
    bpy.context.scene.collection.children.link(collection)

    return collection


@contextlib.contextmanager
def editmode():
    # enter editmode
    bpy.ops.object.editmode_toggle()

    yield  # return out of the function in editmode

    # exit editmode
    bpy.ops.object.editmode_toggle()


def get_vert_coordinates_list(obj):

    coordinates_list = []
    with editmode():
        bm = bmesh.from_edit_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        for vert in bm.verts:
            vector = mathutils.Vector((vert.co.x, vert.co.y, vert.co.z))
            coordinates_list.append(vector)

    return coordinates_list


def make_ramp_from_colors(colors, color_ramp_node):
    """
    Creates new sliders on a Color Ramp Node and
    applies the list of colors on each slider
    """
    color_count = len(colors)

    step = 1 / color_count
    cur_pos = step
    # -2 is for the two sliders that are present on the ramp
    for _ in range(color_count - 2):
        color_ramp_node.elements.new(cur_pos)
        cur_pos += step

    for i, color in enumerate(colors):
        color_ramp_node.elements[i].color = color


def get_color_palette():
    # https://www.colourlovers.com/palette/2943292
    # palette = ['#D7CEA3FF', '#907826FF', '#A46719FF', '#CE3F0EFF', '#1A0C47FF']

    palette = [
        [0.83984375, 0.8046875, 0.63671875, 0.99609375],
        [0.5625, 0.46875, 0.1484375, 0.99609375],
        [0.640625, 0.40234375, 0.09765625, 0.99609375],
        [0.8046875, 0.24609375, 0.0546875, 0.99609375],
        [0.1015625, 0.046875, 0.27734375, 0.99609375],
    ]

    return palette


def apply_location():
    bpy.ops.object.transform_apply(location=True)


def add_lights():
    """
    To keep the code simple I have decided not to include the HDRI downloading and applying code.

    I plan to make a tutorial video explaining how this can be done.

    For what it's worth I used this HDRI: https://hdrihaven.com/hdri/?h=dresden_station_night

    Please consider supporting hdrihaven.com @ https://www.patreon.com/polyhaven/overview
    """
    # url = "https://dl.polyhaven.com/file/ph-assets/HDRIs/hdr/2k/dresden_station_night_2k.hdr"
    # apply_hdri(url)
    pass


################################################################
# helpder functions END
################################################################


def get_coordinates_list(radius, index):
    vertices = 512 * radius

    bpy.ops.mesh.primitive_circle_add(
        vertices=vertices,
        radius=radius,
        enter_editmode=False,
        location=(0, 0, 0.1 * index),
    )

    apply_location()

    obj = active_obj()
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR", center="MEDIAN")

    coordinates_list = get_vert_coordinates_list(obj)

    bpy.data.objects.remove(bpy.data.objects[obj.name])

    return coordinates_list


def gen_perlin_curve(context, random_location, radius, index, collection_name):
    coordinates_list = get_coordinates_list(radius, index)

    non_deform_coords = coordinates_list
    deform_coords = []

    current_z = 0.1 * index
    curve_origin = mathutils.Vector((0, 0, current_z))
    for coord in non_deform_coords:
        new_location = random_location + coord
        noise_value = mathutils.noise.noise(new_location)
        noise_value = noise_value / 2

        deform_vector = (coord - curve_origin) * noise_value

        deform_coord = coord + deform_vector
        deform_coords.append(deform_coord)

    curve_obj = gen_curve_form_coords(index, deform_coords, collection_name)
    make_active(curve_obj)

    bpy.context.object.data.bevel_mode = "OBJECT"
    bpy.context.object.data.bevel_object = context["bevel_obj"]

    curve_obj.data.materials.append(context["material"])
    bpy.ops.object.shade_flat()

    shape_key = add_shape_key(curve_obj, non_deform_coords)

    return shape_key


def animate_curve(context, shape_key, start_frame):
    start_value = 0
    mid_value = 1
    loop_len = context["frame_count"] - context["curve_count"]

    shape_key.value = start_value
    shape_key.keyframe_insert("value", frame=start_frame)

    current_frame = start_frame + (loop_len) / 2
    shape_key.value = mid_value
    shape_key.keyframe_insert("value", frame=current_frame)

    current_frame = start_frame + loop_len
    shape_key.value = start_value
    shape_key.keyframe_insert("value", frame=current_frame)

    frame_step = 1
    start_frame += frame_step

    return start_frame


def gen_curve_form_coords(index, coords, collection_name):
    curve_name = f"curve_{index}"

    curve_data = bpy.data.curves.new(curve_name, type="CURVE")
    poly_spline_data = curve_data.splines.new("POLY")
    curve_obj = bpy.data.objects.new(curve_name, curve_data)

    collection = bpy.data.collections[collection_name]
    collection.objects.link(curve_obj)

    point_count = len(coords) - 1
    poly_spline_data.points.add(point_count)
    poly_spline_data.use_cyclic_u = True  # make it loop

    weight = 1
    for i, coord in enumerate(coords):
        poly_spline_data.points[i].co = (coord.x, coord.y, coord.z, weight)

    return curve_obj


def add_shape_key(curve_obj, non_deform_coords):

    curve_obj.shape_key_add(name="Basis")

    shape_key = curve_obj.shape_key_add(name="Deform")

    for i, coord in enumerate(non_deform_coords):
        shape_key.data[i].co = coord
    shape_key.value = 1

    return shape_key


def create_bevel_object():
    bpy.ops.curve.simple(
        Simple_Type="Rectangle",
        edit_mode=False,
    )
    bpy.context.object.scale.x = 0.26
    bpy.context.object.scale.y = 0.05
    bpy.context.object.name = "bevel_object"

    return active_obj()


def setup_material(context):
    material_ctrl = add_ctrl_empty()

    material, nodes = gen_base_material()
    nodes["Texture Coordinate"].object = material_ctrl
    nodes["Mapping"].inputs[3].default_value[2] = 0.1
    make_ramp_from_colors(context["colors"], nodes["ColorRamp"].color_ramp)

    return material


def gen_centerpiece(context):

    context["material"] = setup_material(context)
    context["bevel_obj"] = create_bevel_object()

    random_location = mathutils.Vector(
        (random.uniform(0, 100), random.uniform(0, 100), random.uniform(0, 100))
    )

    collection_name = f"perlin_curves"
    create_collection(collection_name)

    count = 100
    context["curve_count"] = count
    radius = 1.1
    start_frame = 1
    for i in range(count):
        shape_key = gen_perlin_curve(
            context, random_location, radius, i, collection_name
        )
        start_frame = animate_curve(context, shape_key, start_frame)


def gen_scene(context):
    gen_centerpiece(context)
    add_lights()


def gen_base_material():
    material = bpy.data.materials.new(name="base_material")
    material.use_nodes = True

    mat_output = None
    to_rm = []
    for node in material.node_tree.nodes:
        if node.type == "OUTPUT_MATERIAL":
            mat_output = node
            continue
        to_rm.append(node)

    for node in to_rm:
        print("Removing", node.name)
        material.node_tree.nodes.remove(node)

    node_dict = dict()
    mat_output.location = mathutils.Vector((300.0, 300.0))

    bsdf_principled_node = material.node_tree.nodes.new(type="ShaderNodeBsdfPrincipled")
    bsdf_principled_node.location = mathutils.Vector((10.0, 300.0))
    bsdf_principled_node.name = "Principled BSDF"
    # bsdf_principled_node.label = ""
    node_dict["Principled BSDF"] = bsdf_principled_node

    color_ramp_node = material.node_tree.nodes.new(type="ShaderNodeValToRGB")
    color_ramp_node.location = mathutils.Vector((-533.505, 168.539))
    color_ramp_node.name = "ColorRamp"
    # color_ramp_node.label = ""
    node_dict["ColorRamp"] = color_ramp_node

    texture_coordinate_node = material.node_tree.nodes.new(type="ShaderNodeTexCoord")
    texture_coordinate_node.location = mathutils.Vector((-1397.75, 89.254))
    texture_coordinate_node.name = "Texture Coordinate"
    # texture_coordinate_node.label = ""
    node_dict["Texture Coordinate"] = texture_coordinate_node

    mapping_node = material.node_tree.nodes.new(type="ShaderNodeMapping")
    mapping_node.location = mathutils.Vector((-1197.749, 106.254))
    mapping_node.name = "Mapping"
    # mapping_node.label = ""
    node_dict["Mapping"] = mapping_node

    mapping_node.inputs["Rotation"].default_value = mathutils.Euler(
        (0.0, math.radians(90), 0.0)
    )

    gradient_texture_node = material.node_tree.nodes.new(type="ShaderNodeTexGradient")
    gradient_texture_node.location = mathutils.Vector((-877.749, 133.323))
    gradient_texture_node.name = "Gradient Texture"
    # gradient_texture_node.label = ""
    node_dict["Gradient Texture"] = gradient_texture_node

    # links begin
    from_node = material.node_tree.nodes.get("Principled BSDF")
    to_node = material.node_tree.nodes.get("Material Output")
    material.node_tree.links.new(from_node.outputs["BSDF"], to_node.inputs["Surface"])
    from_node = material.node_tree.nodes.get("ColorRamp")
    to_node = material.node_tree.nodes.get("Principled BSDF")
    material.node_tree.links.new(
        from_node.outputs["Color"], to_node.inputs["Base Color"]
    )
    from_node = material.node_tree.nodes.get("Mapping")
    to_node = material.node_tree.nodes.get("Gradient Texture")
    material.node_tree.links.new(from_node.outputs["Vector"], to_node.inputs["Vector"])
    from_node = material.node_tree.nodes.get("Texture Coordinate")
    to_node = material.node_tree.nodes.get("Mapping")
    material.node_tree.links.new(from_node.outputs["Object"], to_node.inputs["Vector"])
    from_node = material.node_tree.nodes.get("Gradient Texture")
    to_node = material.node_tree.nodes.get("ColorRamp")
    material.node_tree.links.new(from_node.outputs["Color"], to_node.inputs["Fac"])
    # links end

    return material, node_dict


def setup_scene():
    fps = 30
    loop_sec = 6
    frame_count = fps * loop_sec

    day = "324"
    scene_num = 1
    bpy.context.scene.render.image_settings.file_format = "PNG"
    bpy.context.scene.render.filepath = f"/tmp/day{day}_{scene_num}/"

    seed = 1634522379.592337
    if seed:
        random.seed(seed)
    else:
        seed = time_seed()

    # Utility Building Blocks
    delete_all_objects()
    set_scene_props(fps, loop_sec)

    loc = (-8.022, -6.212, 7.46)
    rot = (1.299, -0.0, -0.912)
    cam_empty = setup_camera(loc, rot)
    cam_empty.location.z = 4.5

    context = {
        "frame_count": frame_count,
    }

    context["colors"] = get_color_palette()

    enable_extra_curves()

    return context


def main():
    """
    Python code for this art project
    https://www.artstation.com/artwork/48wX6L
    """
    context = setup_scene()
    gen_scene(context)


if __name__ == "__main__":
    main()
