import bpy

# if named..
# obj = bpy.data.objects['IcoSphere']  
obj = bpy.context.active_object  
me = obj.data

# must be in object mode, to refresh face selections and data
bpy.ops.object.mode_set(mode = 'OBJECT') 

faces = me.polygons
for f in faces:
    f.select = (f.normal.y < 0.0)

# to remove using this method we switch to edit mode, and back after removal.

bpy.ops.object.mode_set(mode = 'EDIT') 
bpy.ops.mesh.delete(type='FACE')
bpy.ops.object.mode_set(mode = 'OBJECT') 
