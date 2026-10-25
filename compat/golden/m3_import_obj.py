"""Legacy OBJ operator contract, measured against Blender 3.6.23."""
HB_BLENDER_REFERENCE=('3.6',)
HB_EQUIVALENT_MESH_PREFIXES=('Imported panel','Imported triangle','operator-plain')
import bpy,os
bpy.ops.mesh.primitive_cube_add(location=(-5,0,0));bpy.context.object.name='Existing'
path=os.path.join(os.path.dirname(__file__),'../fixtures/operator-import.obj')
assert bpy.ops.import_scene.obj(filepath=path)=={'FINISHED'}
assert len(bpy.context.scene.objects)==3
assert bpy.data.materials['OBJ paint'].use_nodes
assert len(bpy.context.selected_objects)==2
assert bpy.context.object.name=='Existing'
path=os.path.join(os.path.dirname(__file__),'../fixtures/operator-plain.obj')
assert bpy.ops.import_scene.obj(filepath=path,axis_forward='Y',axis_up='Z')=={'FINISHED'}
assert len(bpy.context.scene.objects)==4
assert len(bpy.context.selected_objects)==1
assert len(bpy.data.meshes['operator-plain'].uv_layers)==0
assert [m.name for m in bpy.data.meshes['operator-plain'].materials]==['Default OBJ']
