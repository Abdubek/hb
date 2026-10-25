import bpy
from bpy.app.handlers import persistent

@persistent
def load_handler(dummy):

    # only apply to startup
    if not bpy.data.filepath:
        return

    bpy.ops.object.lamp_add(type='POINT', view_align=False, location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))

bpy.app.handlers.load_post.append(load_handler)
