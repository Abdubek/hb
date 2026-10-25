"""Blender-produced scalar-material GLB imported into a nonempty scene."""
HB_GLTF_MATERIAL_NAMES=('Imported paint',)
import bpy,os
bpy.ops.mesh.primitive_cube_add(location=(-5,0,0));bpy.context.object.name='Existing'
path=os.path.join(os.path.dirname(__file__),'../fixtures/operator-import.glb')
assert bpy.ops.import_scene.gltf(filepath=path)=={'FINISHED'}
assert len(bpy.context.scene.objects)==5
assert bpy.context.object.name=='Imported root'
assert bpy.data.objects['Imported cube'].rotation_mode=='QUATERNION'
assert len(bpy.data.objects['Imported cube'].rotation_quaternion)==4
root=bpy.data.objects['Imported root']
root.rotation_quaternion=(1,0,0,0)
root.rotation_quaternion.z=.2
root.rotation_quaternion.normalize()
root.rotation_mode='XYZ'
root.rotation_mode='QUATERNION'
assert bpy.data.objects['Imported cube'].parent==bpy.data.objects['Imported root']
assert bpy.data.materials['Imported paint'].use_nodes
material=bpy.data.materials['Imported paint']
material.use_nodes=True
shader=material.node_tree.nodes['Principled BSDF']
shader.inputs['Base Color'].default_value=(.6,.2,.1,1)
shader.inputs['Metallic'].default_value=.65
shader.inputs['Roughness'].default_value=.2
shader.inputs['Alpha'].default_value=.7
