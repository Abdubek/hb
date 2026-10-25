import bpy

class CamerasSubMenu(bpy.types.Menu):
    bl_label = "Camera Properties"
    bl_idname = "view3d.camera_properties_menu"

    # <-- Line removed (menu's don't store properties)

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(context.my_camera, "lens")  # <-- Changed from original


class CamerasMenu(bpy.types.Menu):
    bl_label = "Cameras"
    bl_idname = "view3d.cameras_menu"

    def draw(self, context):
        layout = self.layout

        for camera in bpy.data.cameras:

            row = layout.row()

            row.context_pointer_set("my_camera", camera)  # <-- Added to original
            row.menu(CamerasSubMenu.bl_idname, text=camera.name)
            # <-- Line removed (camera set above)

def register():
    bpy.utils.register_class(CamerasSubMenu)
    bpy.utils.register_class(CamerasMenu)


def unregister():
    bpy.utils.unregister_class(CamerasMenu)
    bpy.utils.unregister_class(CamerasSubMenu)

if __name__ == "__main__":
    register()


bpy.ops.wm.call_menu(name=CamerasMenu.bl_idname)      
