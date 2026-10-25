import bpy
# Hierarchy baking, including reflected local scale and child compensation.
bpy.ops.mesh.primitive_cube_add(size=1,location=(1,2,3),rotation=(.3,-.4,.7));obj=bpy.context.object;obj.name='ApplyTarget';obj.scale=(-.5,1.2,2)
parent=bpy.data.objects.new('ApplyParent',None);bpy.context.collection.objects.link(parent);parent.location=(2,-3,1);parent.rotation_euler=(-.2,.3,.5);parent.scale=(1.2,.8,2);obj.parent=parent
child=bpy.data.objects.new('ApplyChild',None);bpy.context.collection.objects.link(child);child.location=(2,-1,3);child.rotation_euler=(-.3,.4,-.1);child.parent=obj
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
# Isolating one user preserves the other data owner.
bpy.ops.mesh.primitive_cube_add(size=.7,location=(5,1,0));obj=bpy.context.object;obj.name='Isolated';obj.scale=(.6,1.3,2)
shared=bpy.data.objects.new('UnselectedUser',obj.data);bpy.context.collection.objects.link(shared);shared.location=(7,1,0)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True,isolate_users=True)
# Selecting all users transforms data once and compensates their channels.
bpy.ops.mesh.primitive_cube_add(size=.7,location=(10,1,0),rotation=(.3,-.4,.7));obj=bpy.context.object;obj.name='SharedTarget';obj.scale=(.5,1.2,2)
shared=bpy.data.objects.new('SelectedUser',obj.data);bpy.context.collection.objects.link(shared);shared.location=(12,1,0);shared.rotation_euler=(.2,.4,-.7);shared.scale=(.8,1.3,1.7);shared.select_set(True)
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
# Join a reflected source into a parented active target, keeping a shared owner.
bpy.ops.mesh.primitive_cube_add(size=.8,location=(0,5,1),rotation=(.2,.3,.4));active=bpy.context.object;active.name='Joined';active.scale=(.6,1.3,2)
parent=bpy.data.objects.new('JoinParent',None);bpy.context.collection.objects.link(parent);parent.location=(2,-1,1);parent.rotation_euler=(.1,-.3,.2);active.parent=parent
shared=bpy.data.objects.new('SharedJoinData',active.data);bpy.context.collection.objects.link(shared);shared.location=(5,5,1)
bpy.ops.mesh.primitive_cube_add(size=.5,location=(2,6,1));source=bpy.context.object;source.name='Source';source.scale=(-.7,1.3,2)
child=bpy.data.objects.new('DetachedChild',None);bpy.context.collection.objects.link(child);child.location=(2,0,1);child.parent=source
active.select_set(True);bpy.context.view_layer.objects.active=active;bpy.ops.object.join()
