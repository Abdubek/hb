import bpy
from collections import deque
from itertools import accumulate

rotate = 1 # rotate 1 to right

context = bpy.context

ob = context.object
me = ob.data
n = len(me.polygons)

loop_starts = [0] * n
me.polygons.foreach_get("loop_start", loop_starts)
loop_ends = [0] * n
me.polygons.foreach_get("loop_total", loop_ends)
loop_ends = accumulate(loop_ends)
face_select = [False] * n
me.polygons.foreach_get("select", face_select)
vert_indices = [0] * len(me.loops)
me.loops.foreach_get("vertex_index", vert_indices)
'''
# Note same as
me.polygons.foreach_get("vertices", vert_indices)
'''

for select, start, end in zip(
        face_select,
        loop_starts,
        loop_ends
        ):
    if select: 
        face_verts = deque(vert_indices[start : end])
        face_verts.rotate(rotate)
        vert_indices[start : end] = face_verts

me.loops.foreach_set("vertex_index", vert_indices)
#print(me.validate()) # while testing just in case.
