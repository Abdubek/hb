import bpy

class FilterPanel(bpy.types.Panel):
    bl_category = "EasyFX"
    bl_label = "Filter"
    bl_idname = "Filter"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        col = layout.column(align=True)
        row = col.row(align=True)

        #Checkbox Here
        #(implied from property type = bool)
        row.prop(scene, "my_prop")

def register():
    # add your custom property to the Scene, but if you
    # have to register many properties consider using a 
    # property group. 
    bpy.types.Scene.my_prop = bpy.props.BoolProperty(
        name="Prop name",
        description="Some tooltip",
        default = True)

    bpy.utils.register_class(FilterPanel)

def unregister():
    bpy.utils.unregister_class(FilterPanel)
    del bpy.types.Scene.my_prop
