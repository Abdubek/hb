import bpy
import random as r
import math as m
n=25

for i in range(1,n+1):
    ob = bpy.context.object
    material_i= bpy.data.materials.new(f'm{i}')
    material_i.diffuse_color=(r.uniform(0,1),r.uniform(0,1),r.uniform(0,1),1)
    if not ob.material_slots:
        bpy.ops.object.material_slot_add()
        new_mat = material_i
        ob.material_slots[0].material = new_mat
    else:
        new_mat = material_i
        ob.material_slots[0].material = new_mat
    angle = ((i-1)*4*(m.pi))/n
    bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'})
    bpy.context.object.rotation_euler[2] = angle
