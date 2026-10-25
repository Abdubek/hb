import bpy


def camera_as_planes(scene, obj):
    """
    Return planes in world-space which represent the camera view bounds.
    """
    from mathutils.geometry import normal
    print(obj.name)
    camera = obj.data
    # normalize to ignore camera scale
    matrix = obj.matrix_world.normalized()
    frame = [matrix @ v for v in camera.view_frame(scene=scene)]
    origin = matrix.to_translation()
    frame.append(origin)
    for p in frame:
        bpy.ops.object.empty_add(location=p)

# test call
scene = bpy.context.scene
cams = [o for o in scene.objects if o.type == 'CAMERA']
for cam in cams:
    camera_as_planes(scene, cam)
