import bpy, bmesh

me = bpy.context.object.data

bm = bmesh.new()
bm.from_mesh(me)

EPSILON = 1.0e-5

for vert in bm.verts:
    if -EPSILON <= vert.co.x <= EPSILON:
        vert.select = True

bm.to_mesh(me)
bm.free()
