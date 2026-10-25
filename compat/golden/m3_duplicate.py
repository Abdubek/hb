"""Selected-object duplication, data sharing, parents and collection links."""
import bpy
bpy.ops.mesh.primitive_cube_add(location=(1,2,3))
seed=bpy.context.object;seed.name='Seed'
material=bpy.data.materials.new('Shared material');seed.data.materials.append(material)
seed.modifiers.new('Repeat','ARRAY').count=2
peer=seed.copy();peer.name='Peer';bpy.context.collection.objects.link(peer);peer.location=(4,5,6)
extra=bpy.data.collections.new('Extra');bpy.context.scene.collection.children.link(extra);extra.objects.link(seed)
bpy.ops.object.empty_add(location=(.5,0,0));group=bpy.context.object;group.name='Group'
seed.parent=group;peer.parent=group
bpy.ops.object.camera_add(location=(0,-6,3));camera=bpy.context.object;camera.name='View'
bpy.ops.object.light_add(type='POINT',location=(0,0,6));light=bpy.context.object;light.name='Lamp'
bpy.ops.object.select_all(action='SELECT');bpy.context.view_layer.objects.active=seed
assert bpy.ops.object.duplicate(linked=False)=={'FINISHED'}
copy=bpy.context.object
assert copy.name=='Seed.001'
assert copy.data!=seed.data and copy.data==bpy.data.objects['Peer.001'].data
assert copy.parent==bpy.data.objects['Group.001']
assert len(copy.users_collection)==2
assert copy.data.materials[0]==material
assert bpy.data.objects['View.001'].data!=camera.data
assert bpy.data.objects['Lamp.001'].data!=light.data
assert len(bpy.context.selected_objects)==5
assert not seed.select_get()
assert bpy.ops.object.duplicate(linked=True)=={'FINISHED'}
linked=bpy.context.object
assert linked.name=='Seed.002' and linked.data==copy.data
assert linked.parent==bpy.data.objects['Group.002']
assert bpy.data.objects['View.002'].data==bpy.data.objects['View.001'].data
assert bpy.data.objects['Lamp.002'].data==bpy.data.objects['Lamp.001'].data
assert len(bpy.context.selected_objects)==5
