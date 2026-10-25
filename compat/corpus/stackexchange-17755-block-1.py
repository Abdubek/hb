import bpy

class SimpleOperator(bpy.types.Operator):
    bl_label = "Simple Operator"
    bl_idname = "object.simple_operator"
    
    my_enum: bpy.props.EnumProperty(
        items=(
            ('ONE', "One", ""),
            ('TWO', "Two", ""),
            ('THREE', "Three", "")
        ),
        default='ONE'
    )
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def execute(self, context):
        self.report({'INFO'}, self.my_enum)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(SimpleOperator)

def unregister():
    bpy.utils.unregister_class(SimpleOperator)

if __name__ == "__main__":
    register()

    bpy.ops.object.simple_operator('INVOKE_DEFAULT')
