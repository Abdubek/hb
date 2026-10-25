import bpy

class OBJECT_PT_modifiers(bpy.types.Panel):
    bl_idname = "OBJECT_PT_modifiers"
    bl_label = "Modifiers"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout

        rows = 2
        ob = context.object
        idx = ob.modifier_active_index

        try:
            mod = ob.modifiers[idx]
            layout.label("%s (%s)" % (mod.name, mod.type), icon="MODIFIER")
        except IndexError:
            layout.label("no modifier selected")

        row = layout.row()
        row.template_list("UI_UL_list", "modifiers", ob, "modifiers", ob, "modifier_active_index", rows=rows)

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Object.modifier_active_index = bpy.props.IntProperty()

def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Object.modifier_active_index

if __name__ == "__main__":
    register()
