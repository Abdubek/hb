import bpy
import bmesh
import mathutils

obj = bpy.context.edit_object
me = obj.data
bm = bmesh.from_edit_mesh(me)

verts_sel = [v for v in bm.verts if v.select is True]
verts_co = [v.co for v in verts_sel]
verts_nor = [v.normal for v in verts_sel]

axis = mathutils.Vector(sum(verts_nor, mathutils.Vector()) / len(verts_sel))
axis = axis.normalized()

origin = mathutils.Matrix.Translation(sum(verts_co, mathutils.Vector()) / len(verts_sel))
mat_sca = mathutils.Matrix.Scale(0.0, 4, axis)

mat_out = mat_sca  # Do not combine transformations

for v in verts_sel:
    vert = mathutils.Vector(v.co)
    # you have translate the "transferred vectors (vert * mat_out)" w.r.t origin 
    v.co = origin * (vert * mat_out)

bmesh.update_edit_mesh(me, True)
