import bpy
from bpy.types import Operator, Menu
from bl_operators.presets import AddPresetBase
from bpy.props import StringProperty

class ExecutePreset(Operator):
    """Execute a preset"""
    bl_idname = "script.execute_preset_float_boat"
    bl_label = "Execute a Python Preset"

    filepath: StringProperty(
        subtype='FILE_PATH',
        options={'SKIP_SAVE'},
    )
    menu_idname: StringProperty(
        name="Menu ID Name",
        description="ID name of the menu this was called from",
        options={'SKIP_SAVE'},
    )

    def execute(self, context):
        from os.path import basename, splitext
        filepath = self.filepath

        # change the menu title to the most recently chosen option
        preset_class = getattr(bpy.types, self.menu_idname)
        preset_class.bl_label = bpy.path.display_name(basename(filepath))

        ext = splitext(filepath)[1].lower()

        if ext not in {".py", ".xml"}:
            self.report({'ERROR'}, "unknown filetype: %r" % ext)
            return {'CANCELLED'}

        if hasattr(preset_class, "reset_cb"):
            preset_class.reset_cb(context)

        if ext == ".py":
            try:
                bpy.utils.execfile(filepath)
            except Exception as ex:
                self.report({'ERROR'}, "Failed to execute the preset: " + repr(ex))

        elif ext == ".xml":
            import rna_xml
            rna_xml.xml_file_run(context,
                                 filepath,
                                 preset_class.preset_xml_map)

        if hasattr(preset_class, "post_cb"):
            preset_class.post_cb(context)

        return {'FINISHED'}

class OBJECT_MT_display_presets(Menu):
    bl_label = "Object Display Presets"
    preset_subdir = "object/display"
    preset_operator = "script.execute_preset_float_boat"
    preset_operator_defaults = {
            "menu_idname" : 'OBJECT_MT_display_presets'
            }
    draw = Menu.draw_preset
    @classmethod
    def reset_cb(self, context):
        print("Reset")
    @classmethod        
    def post_cb(self, context):
        print("Post Callback")


class AddPresetObjectDisplay(AddPresetBase, Operator):
    '''Add a Object Display Preset'''
    bl_idname = "camera.object_display_preset_add"
    bl_label = "Add Object Display Preset"
    preset_menu = "OBJECT_MT_display_presets"

    # variable used for all preset values
    preset_defines = [
        "obj = bpy.context.object"
    ]

    # properties to store in the preset
    preset_values = [
        "obj.display_type",
        "obj.show_bounds",
        "obj.display_bounds_type",
        "obj.show_name",
        "obj.show_axis",
        "obj.show_wire",
    ]

    # where to store the preset
    preset_subdir = "object/display"


# Display into an existing panel
def panel_func(self, context):
    layout = self.layout

    row = layout.row(align=True)
    row.menu(OBJECT_MT_display_presets.__name__, text=OBJECT_MT_display_presets.bl_label)
    row.operator(AddPresetObjectDisplay.bl_idname, text="", icon='ZOOM_IN')
    row.operator(AddPresetObjectDisplay.bl_idname, text="", icon='ZOOM_OUT').remove_active = True


classes = (
    ExecutePreset,
    OBJECT_MT_display_presets,
    AddPresetObjectDisplay,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.OBJECT_PT_display.prepend(panel_func)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.OBJECT_PT_display.remove(panel_func)


if __name__ == "__main__":
    register()
