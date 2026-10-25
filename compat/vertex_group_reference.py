import bpy,json,os
for block in list(bpy.data.objects):bpy.data.objects.remove(block,do_unlink=True)
mesh=bpy.data.meshes.new('Weights');mesh.from_pydata([(0,0,0),(1,0,0),(2,0,0)],[],[])
obj=bpy.data.objects.new('Weights',mesh);bpy.context.collection.objects.link(obj)
result={}
def capture(name):result[name]={'names':[g.name for g in obj.vertex_groups],'weights':[[[g.group,g.weight] for g in v.groups] for v in mesh.vertices]}
a=obj.vertex_groups.new(name='Arm.L');b=obj.vertex_groups.new(name='Arm.L');c=obj.vertex_groups.new(name='Center');capture('new')
a.add([0,1],.8,'REPLACE');a.add([0],.4,'ADD');a.add([1],.3,'SUBTRACT');a.add([2],.5,'SUBTRACT');capture('edit')
b.add([0,2],0,'REPLACE');c.add([1,2],2,'REPLACE');capture('clamp_zero')
a.remove([0,2]);capture('remove_weights')
obj.vertex_groups.remove(b);capture('remove_group')
result['weight_errors']=[]
for vertex in (-1,0,99):
 try:result['weight_errors'].append(a.weight(vertex))
 except Exception as e:result['weight_errors'].append(type(e).__name__)
obj.vertex_groups.clear();capture('clear')
with open(os.environ['HB_VERTEX_GROUP_RESULTS'],'w') as output:json.dump(result,output)
