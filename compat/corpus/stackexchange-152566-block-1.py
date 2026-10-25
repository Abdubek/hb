import bpy

class MY_MT_CustomMenu(bpy.types.Menu):
    bl_label = "First Menu"
    bl_idname = "OBJECT_MT_custom_menu"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Hello First Menu!", icon='WORLD_DATA')

         # call the second custom menu
        layout.menu("OBJECT_MT_sub_menu", icon="COLLAPSEMENU")


class MY_MT_CustomSubMenu(bpy.types.Menu):
    bl_label = "Sub Menu"
    bl_idname = "OBJECT_MT_sub_menu"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Hello Second Menu!", icon='WORLD_DATA')

        # call another predefined menu
        layout.operator("wm.call_menu", text="Unwrap").name = "VIEW3D_MT_uv_map" 


def draw_menu(self, context):
    self.layout.menu(MY_MT_CustomMenu.bl_idname)


def register():
    bpy.utils.register_class(MY_MT_CustomMenu)
    bpy.utils.register_class(MY_MT_CustomSubMenu)
    bpy.types.VIEW3D_MT_curve_add.append(draw_menu)

def unregister():
    bpy.types.VIEW3D_MT_curve_add.remove(draw_menu)
    bpy.utils.unregister_class(MY_MT_CustomSubMenu)
    bpy.utils.unregister_class(MY_MT_CustomMenu)    


if __name__ == "__main__":
    register()
