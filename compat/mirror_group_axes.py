"""Mirror-group mode checks across all three axes."""
import bpy,json,os
result={}
for axis,flip in ((0,True),(1,True),(2,True),(0,False)):
    name=str(axis)+'_'+str(flip)
    data=bpy.data.meshes.new(name);data.from_pydata([(1,1,1)],[],[])
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj)
    left=obj.vertex_groups.new(name='Arm.L');obj.vertex_groups.new(name='Arm.R');left.add([0],.8,'REPLACE')
    modifier=obj.modifiers.new('Mirror','MIRROR');modifier.use_axis=(axis==0,axis==1,axis==2);modifier.use_mirror_vertex_groups=flip
    bpy.context.view_layer.objects.active=obj;obj.select_set(True);bpy.ops.object.modifier_apply(modifier=modifier.name)
    result[name]={'vertices':[list(v.co) for v in obj.data.vertices],'weights':[[[g.group,g.weight] for g in v.groups] for v in obj.data.vertices]}
with open(os.environ['HB_MIRROR_GROUP_AXES'],'w') as output:json.dump(result,output)
