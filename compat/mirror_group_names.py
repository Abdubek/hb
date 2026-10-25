import bpy,json,os
for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
data=bpy.data.meshes.new('Names');data.from_pydata([(1,1,1)],[],[])
obj=bpy.data.objects.new('Names',data);bpy.context.collection.objects.link(obj)
pairs=[('Arm.L','Arm.R'),('Arm_l','Arm_r'),('Arm-L','Arm-R'),('L.Arm','R.Arm'),('l_arm','r_arm'),('LeftArm','RightArm'),('left_arm','right_arm'),('ArmLeft','ArmRight'),('armleft','armright'),('Arm.L.001','Arm.R.001'),('L','R'),('ArmL','ArmR'),('left','right')]
for a,b in pairs:obj.vertex_groups.new(name=a);obj.vertex_groups.new(name=b)
for a,b in pairs:obj.vertex_groups[a].add([0],.4,'REPLACE')
modifier=obj.modifiers.new('Mirror','MIRROR');bpy.context.view_layer.objects.active=obj;obj.select_set(True);bpy.ops.object.modifier_apply(modifier=modifier.name)
result=[obj.vertex_groups[g.group].name for g in obj.data.vertices[1].groups]
with open(os.environ['HB_MIRROR_GROUP_NAMES'],'w') as output:json.dump(result,output)
