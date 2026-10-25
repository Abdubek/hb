import bpy
import blf
import bmesh

bmeshes = {}
#from gi.repository import Gdk
class DrawingClass:
    def __init__(self, context, prop):
        self.prop = prop
        self.handle = bpy.types.SpaceView3D.draw_handler_add(
                   self.draw_text_callback,(context,),
                   'WINDOW', 'POST_PIXEL')

    def draw_text_callback(self, context):
        font_id = 0  # XXX, need to find out how best to get this.
        # draw some text
        blf.position(font_id, 15, 50, 20)
        blf.size(font_id, 20, 72)

        ob = context.object
        meshes = set(o.data for o in context.selected_objects if o.mode == 'EDIT')
        if context.mode == 'EDIT_MESH':
            for m in meshes:
                bmeshes.setdefault(m.name, bmesh.from_edit_mesh(m))
        else:
            bmeshes.clear()
            return
        me = ob.data
        blf.draw(font_id, f"{bmeshes[me.name].select_history.active}")

    def remove_handle(self):
         bpy.types.SpaceView3D.draw_handler_remove(self.handle, 'WINDOW')

if __name__ == "__main__":
    # test call            
    dc = DrawingClass(bpy.context, "Auto Layer Running......")
    dns = bpy.app.driver_namespace
    dns["dc"] = dc
