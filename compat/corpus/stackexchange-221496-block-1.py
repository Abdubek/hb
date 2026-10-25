import bpy

ob = bpy.context.object
assert ob.type == 'MESH'

# If in edit mode, switch to object mode and switch back at the end
was_in_edit_mode = False
if ob.mode == 'EDIT':
    bpy.ops.object.mode_set(mode='OBJECT')
    was_in_edit_mode = True

me = ob.data

for poly in me.polygons:
    if not poly.select:
        continue

    # Get loops for this poly
    # Loop = corner of a poly
    loop_start = poly.loop_start
    loop_end = loop_start + poly.loop_total
    loops = [me.loops[loopi] for loopi in range(loop_start, loop_end)]

    # Get vertex indices for each loop
    vidxs = [loop.vertex_index for loop in loops]

    # Shift
    vidxs = vidxs[1:] + vidxs[0:1]

    # Write back
    for i, loop in enumerate(loops):
        loop.vertex_index = vidxs[i]

# Not sure if you need this
me.update()

if was_in_edit_mode:
    bpy.ops.object.mode_set(mode='EDIT')
