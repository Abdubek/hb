import bpy
from bl_operators.presets import AddPresetBase

class RENDER_OT_my_preset_add(AddPresetBase, bpy.types.Operator):
    """Add a new render preset."""
    bl_idname = 'render.my_preset_add'
    bl_label = 'Add My Render Preset'
    bl_options = {'REGISTER', 'UNDO'}
    preset_menu = 'RENDER_MT_my_presets'
    preset_subdir = 'my_render_preset'

    preset_defines = [
        "scene  = bpy.context.scene",
        "render = bpy.context.scene.render",
        "image  = bpy.context.scene.render.image_settings",
        ]

    preset_values = [
        "scene.use_preview_range",
        "render.engine",
        "render.use_stamp",
        "image.file_format",
        ]
