"""Principled plus image texture contract, authored before shader implementation."""
HB_SYMBOLS={
'bpy.data.images':'Image data blocks',
'bpy.data.images.new':'new(name, width, height, alpha=True, float_buffer=False, stereo3d=False, is_data=False, tiled=False); non-tiled mono images',
'bpy.data.images.load':'load(filepath, check_existing=False); PNG and JPEG',
'bpy.data.images.remove':'remove(image, do_unlink=True)',
'bpy.types.Image.name':'Unique image name',
'bpy.types.Image.size':'Pixel width and height',
'bpy.types.Image.pixels':'RGBA float pixel buffer with slice read/write',
'bpy.types.Image.filepath':'Image source path',
'bpy.types.Image.colorspace_settings.name':'sRGB or Non-Color',
'bpy.types.Material.node_tree.nodes':'Single Principled, material output, image textures and normal maps',
'bpy.types.Material.node_tree.nodes.get':'Node lookup by name',
'bpy.types.Material.node_tree.nodes.new':'ShaderNodeTexImage and ShaderNodeNormalMap; Principled/Output after clearing',
'bpy.types.Material.node_tree.nodes.clear':'Remove nodes and links',
'bpy.types.Material.node_tree.links.new':'Connect supported image/Principled/material output sockets',
'bpy.types.ShaderNode.name':'Unique node name',
'bpy.types.ShaderNode.inputs':'Supported named input sockets',
'bpy.types.ShaderNode.outputs':'Supported named output sockets',
'bpy.types.ShaderNode.image':'Image texture data',
'bpy.types.NodeSocket.default_value':'Base Color, Metallic, Roughness, Alpha, Emission Color/Strength; normal-map strength',
'bpy.types.Mesh.uv_layers':'UV layers',
'bpy.types.Mesh.uv_layers.new':'new(name="UVMap", do_init=True)',
'bpy.types.Mesh.uv_layers.active':'Active UV layer',
'bpy.types.MeshUVLoopLayer.name':'UV layer name',
'bpy.types.MeshUVLoopLayer.data':'Loop UV values',
'bpy.types.MeshUVLoop.uv':'UV pair, assignment and indexed access',
}
import bpy
m=bpy.data.materials.new('Paint')
m.use_nodes=True
nodes=m.node_tree.nodes
bsdf=nodes.get('Principled BSDF')
assert bsdf == nodes['Principled BSDF']
bsdf.inputs['Base Color'].default_value=(.8,.04,.02,1)
bsdf.inputs['Metallic'].default_value=.3
bsdf.inputs['Roughness'].default_value=.35
bsdf.inputs['Alpha'].default_value=.9
bsdf.inputs['Emission Color'].default_value=(.01,.01,.01,1)
bsdf.inputs['Emission Strength'].default_value=.2
assert abs(bsdf.inputs['Metallic'].default_value-.3)<1e-6
image=bpy.data.images.new('Checker',width=2,height=2,alpha=True)
assert tuple(image.size)==(2,2)
image.pixels[:]=[1,0,0,1, 0,1,0,1, 0,0,1,1, 1,1,1,1]
assert tuple(image.pixels[:4])==(1,0,0,1)
texture=nodes.new('ShaderNodeTexImage');texture.image=image
texture.name='Color Texture'
assert texture.image is image
m.node_tree.links.new(texture.outputs['Color'],bsdf.inputs['Base Color'])
normal_image=bpy.data.images.new('Normal',width=1,height=1,is_data=True)
normal_image.pixels[:]=[.5,.5,1,1]
normal_image.colorspace_settings.name='Non-Color'
normal=nodes.new('ShaderNodeNormalMap')
normal.inputs['Strength'].default_value=.5
tex=nodes.new('ShaderNodeTexImage');tex.image=normal_image
m.node_tree.links.new(tex.outputs['Color'],normal.inputs['Color'])
m.node_tree.links.new(normal.outputs['Normal'],bsdf.inputs['Normal'])
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.name='TexturedCube';obj.data.materials.append(m)
assert len(obj.data.uv_layers.active.data)==24
obj.data.uv_layers.active.data[0].uv=(.1,.2)
new=obj.data.uv_layers.new(name='Detail')
assert new.name=='Detail' and len(new.data)==24
unused=bpy.data.images.new('Unused',1,1);bpy.data.images.remove(unused)
other=bpy.data.materials.new('Rebuilt');other.use_nodes=True
other.node_tree.nodes.clear()
p=other.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
out=other.node_tree.nodes.new('ShaderNodeOutputMaterial')
other.node_tree.links.new(p.outputs['BSDF'],out.inputs['Surface'])
other.use_nodes=False
assert other.node_tree is not None

import os
path=os.path.join(os.path.dirname(__file__),'../fixtures/checker.png')
loaded=bpy.data.images.load(path)
assert tuple(loaded.size)==(2,2)
assert tuple(loaded.pixels[:4])==(0,0,1,1)
assert bpy.data.images.load(path,check_existing=True) is loaded
loaded.filepath=path
assert loaded.filepath==path
assert tuple(normal_image.pixels[:])==(0,0,0,1)
