"""Z-up OBJ/MTL reference for CLI export of evaluated transformed assets."""
HB_BLENDER_REFERENCE=('3.6',)
HB_EQUIVALENT_MESH_PREFIXES=('Icosphere',)
import bpy,os
bpy.ops.mesh.primitive_cube_add(location=(1,2,3))
cube=bpy.context.object;cube.name='CLI cube';cube.scale=(-2,1,1);cube.rotation_euler=(.2,.4,.6)
modifier=cube.modifiers.new('Copies','ARRAY');modifier.count=2
material=bpy.data.materials.new('CLI paint');material.use_nodes=True
shader=material.node_tree.nodes['Principled BSDF']
shader.inputs['Base Color'].default_value=(.2,.4,.6,1);shader.inputs['Metallic'].default_value=.3
shader.inputs['Roughness'].default_value=.25;shader.inputs['Alpha'].default_value=.8
try:shader.inputs['Emission Color'].default_value=(0,0,0,1)
except KeyError:shader.inputs['Emission'].default_value=(0,0,0,1)
shader.inputs['Emission Strength'].default_value=0
cube.data.materials.append(material)
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.3,location=(0,0,2))
child=bpy.context.object;child.name='CLI child';child.parent=cube;child.data.materials.append(material)
output=os.environ.get('HB_CLI_OBJ_REFERENCE')
if output:bpy.ops.export_scene.obj(filepath=output,axis_forward='Y',axis_up='Z')
