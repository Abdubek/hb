import bpy

class MY_OT_custom(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.simple_operator"
    bl_label = "Simple Object Operator"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj is not None and obj.type == 'MESH')

    def execute(self, context):
        # Your code here 
        # ...
        bpy.ops.mesh.remove_doubles(threshold=0.02)   
        return {'FINISHED'}


class MY_PT_custom(bpy.types.Panel):
    """Creates a Sub-Panel in the Property Area of the 3D View"""
    bl_label = "My Tool"  
    bl_space_type = "VIEW_3D"  
    bl_region_type = "UI"
    bl_category = "My Tools"
    bl_context = "mesh_edit"

    def draw(self, context):
        obj = context.object

        layout = self.layout

        row = layout.row()
        row.label(text="Active object is: {}".format(obj.name))

        row = layout.row()
        row.prop(obj, "name")

        row = layout.row()
        row.label(text="Vertex Count: {}".format(len(obj.data.vertices)))

        row = layout.row()
        row.operator(MY_OT_custom.bl_idname)



def register():
    bpy.utils.register_class(MY_PT_custom)
    bpy.utils.register_class(MY_OT_custom)


def unregister():
    bpy.utils.unregister_class(MY_OT_custom)
    bpy.utils.unregister_class(MY_PT_custom)


if __name__ == "__main__":
    register()
