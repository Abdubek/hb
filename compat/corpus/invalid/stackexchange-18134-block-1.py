import bpy
from bpy.app.handlers import persistent

def scene_update_callback(scene):

    # self-removal, only run once
    bpy.app.handlers.scene_update_pre.remove(scene_update_callback)

    ob = scene.objects.get("Cube")

    if ob is not None:
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        ob.select = True
        bpy.ops.object.delete()


@persistent
def load_post_callback(dummy):

    # self-removal, so it isn't called again
    bpy.app.handlers.load_post.remove(load_post_callback)

    # use a scene update handler to delay execution of code
    bpy.app.handlers.scene_update_pre.append(scene_update_callback)


if __name__ == '__main__':
    bpy.app.handlers.load_post.append(load_post_callback)
    bpy.ops.wm.revert_mainfile()
