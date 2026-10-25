# This example adds an object mode tool to the toolbar.
# This is just the circle-select and lasso tools tool.
import bpy
from bpy.types import WorkSpaceTool

class Circularize(WorkSpaceTool):
    bl_space_type='VIEW_3D'
    bl_context_mode='EDIT_MESH'

    # The prefix of the idname should be your add-on name.
    bl_idname = "ui_plus.circularize"
    bl_label = "Circularize"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = (
        "Move selected vertices into a circular shape"
    )
    bl_icon = "ops.generic.select_circle"
    bl_widget = None
    bl_keymap = (
        ("mesh.looptools_circle", {"type": 'LEFTMOUSE', "value": 'PRESS'},
    {"properties": [("custom_radius", False), ("radius", 1)]}),
        )


def register():
    bpy.utils.register_tool(Circularize, after={"builtin.scale_cage"}, separator=True, group=True)

def unregister():
    bpy.utils.unregister_tool(Circularize)

if __name__ == "__main__":
    register()
