import bpy
bpy.ops.mesh.primitive_plane_add(size=2)
material=bpy.data.materials.new('USD_texture');material.use_nodes=True
shader=material.node_tree.nodes['Principled BSDF']
image=bpy.data.images.new('USD_image',width=2,height=2,alpha=True,float_buffer=True)
image.pixels=[1,0,0,1,.25,.5,.75,.5,0,1,0,1,0,0,1,0]
texture=material.node_tree.nodes.new('ShaderNodeTexImage');texture.image=image
material.node_tree.links.new(texture.outputs['Color'],shader.inputs['Base Color'])
material.node_tree.links.new(texture.outputs['Alpha'],shader.inputs['Alpha'])
bpy.context.object.data.materials.append(material)
