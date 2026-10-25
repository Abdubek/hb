import bpy

# clear any existing objects
for o in bpy.data.objects:
    o.hide = False
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

grid_size = 7
# the default cube is 2 units wide, add another .2 for gap
spacing = 2.2

for x in range(grid_size):
    for y in range(grid_size):
        f = (x*grid_size) + y
        bpy.ops.mesh.primitive_cube_add (location=(x*spacing, y*spacing, 0))
        obj = bpy.context.active_object
        # key as visible on the current frame
        obj.keyframe_insert('hide',frame=f)
        obj.keyframe_insert('hide_render',frame=f)
        # hide it
        obj.hide = True
        obj.hide_render = True
        # key as hidden on the previous frame
        obj.keyframe_insert('hide',frame=f-1)
        obj.keyframe_insert('hide_render',frame=f-1)
        # key as hidden on the next frame
        obj.keyframe_insert('hide',frame=f+1)
        obj.keyframe_insert('hide_render',frame=f+1)
