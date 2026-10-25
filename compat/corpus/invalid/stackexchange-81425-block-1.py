import bpy
import bmesh

obj = bpy.context.object
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_mode(type='FACE')
bpy.ops.mesh.select_all(action='DESELECT')
bm = bmesh.from_edit_mesh(obj.data)

for face in bm.faces:
    if not face.hide:
        face.select = True
        bm.faces.active = face
        bpy.ops.mesh.select_linked(delimit={'SEAM'})
        bpy.ops.uv.follow_active_quads(mode='EVEN')
        bpy.ops.mesh.hide(unselected=False)

bpy.ops.mesh.reveal()
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.unwrap()
bpy.ops.object.mode_set(mode='OBJECT')
bm.free()
