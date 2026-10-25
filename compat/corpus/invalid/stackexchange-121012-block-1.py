import bpy
import bmesh
from mathutils import Vector
from mathutils.geometry import distance_point_to_plane

context = bpy.context
ob = context.edit_object
me = ob.data
bm = bmesh.from_edit_mesh(me)
bm.normal_update() #  maybe unneccesary if no prior ops.
verts_sel = [v for v in bm.verts if v.select is True]
n = len(verts_sel)
verts_co = [v.co for v in verts_sel]
verts_no = [v.normal for v in verts_sel]

plane_co = sum(verts_co, Vector()) / n
plane_no = sum(verts_no, Vector()).normalized()

for v in verts_sel:
    d = distance_point_to_plane(v.co, plane_co, plane_no)
    v.co -= d * plane_no

bmesh.update_edit_mesh(me)
