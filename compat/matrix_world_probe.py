"""Replay captured Blender object-matrix inputs and compare before/after RNA."""
import bpy
from mathutils import Matrix
for key,row in references.items():
    bpy.ops.object.select_all(action='DESELECT')
    parent=None
    if row['parent_kind']!='none':
        parent=bpy.data.objects.new('Parent'+key,None);bpy.context.collection.objects.link(parent)
        parent.location=(2,-1,3);parent.rotation_euler=(.2,-.4,.7)
        parent.scale={'uniform':(2,2,2),'nonuniform':(1.2,.7,2),'reflected':(-1,2,1)}[row['parent_kind']]
    obj=bpy.data.objects.new('Object'+key,None);bpy.context.collection.objects.link(obj)
    obj.rotation_mode=row['mode'];obj.location=(1,2,3);obj.rotation_euler=(.2,.3,.4)
    obj.rotation_quaternion=(.9,.1,.2,.3);obj.scale=(1.1,.8,1.3)
    if parent is not None:
        obj.select_set(True);parent.select_set(True);bpy.context.view_layer.objects.active=parent
        bpy.ops.object.parent_set(type='OBJECT',keep_transform=False)
        parent.location.x+=1.7;parent.rotation_euler.y+=.25
    for stage in ('before','after'):
        if stage=='after':obj.matrix_world=Matrix(row['target'])
        expected=row[stage]
        for field,actual in (('location',obj.location),('rotation_euler',obj.rotation_euler),('rotation_quaternion',obj.rotation_quaternion),('scale',obj.scale)):
            assert max(abs(a-b) for a,b in zip(actual,expected[field]))<=1e-5,(key,stage,field,list(actual),expected[field])
        assert max(abs(a-b) for ar,br in zip(obj.matrix_world,expected['world']) for a,b in zip(ar,br))<=1e-5,(key,stage,'world',[list(r) for r in obj.matrix_world],expected['world'])
