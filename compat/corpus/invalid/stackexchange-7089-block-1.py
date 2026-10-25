import bpy

class OBJECT_OT_my_operator(bpy.types.Operator):
    bl_idname = "object.my_operator"
    bl_label = "My Operator"

    def invoke(self, context, event):
        print("hello invoke")
        return {'FINISHED'}

    def execute(self, context):
        print("hello execute")        
        return {'FINISHED'}

def draw(self, context):
    layout = self.layout
    layout.operator(OBJECT_OT_my_operator.bl_idname, text="Operator 1 - invoke (default)")

    col = layout.column()
    col.operator_context = 'EXEC_DEFAULT'
    col.operator(OBJECT_OT_my_operator.bl_idname, text="Operator 1 - execute")


def register():
    bpy.utils.register_class(OBJECT_OT_my_operator)
    bpy.types.RENDER_PT_render.append(draw)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_my_operator)
    bpy.types.RENDER_PT_render.remove(draw)

if __name__ == "__main__":
    register()
