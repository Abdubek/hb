"""Node identity and whole-image pixel assignment observed before exposure."""
HB_SYMBOLS={
'bpy.types.ShaderNode.type':'Read-only node enum for the supported Principled/output/image/normal-map nodes',
'bpy.types.ShaderNode.bl_idname':'Read-only Blender node identifier',
'bpy.types.Image.pixels':'Flat RGBA sequence supporting whole-property and indexed/slice assignment',
}
import bpy
material=bpy.data.materials.new('Node identities');material.use_nodes=True
nodes=material.node_tree.nodes
nodes.new('ShaderNodeTexImage');nodes.new('ShaderNodeNormalMap')
expected={'ShaderNodeBsdfPrincipled':'BSDF_PRINCIPLED','ShaderNodeOutputMaterial':'OUTPUT_MATERIAL','ShaderNodeTexImage':'TEX_IMAGE','ShaderNodeNormalMap':'NORMAL_MAP'}
for node in nodes:assert node.type==expected[node.bl_idname]
for floating in (False,True):
    image=bpy.data.images.new('Pixel assignment',width=2,height=2,float_buffer=floating)
    image.pixels=[.25,.5,.75,1,1,0,0,1,0,1,0,1,0,0,1,1]
    before=tuple(image.pixels)
    try:image.pixels=[1,0,0,1]
    except (ValueError,TypeError):pass
    else:raise AssertionError('Wrong pixel count accepted')
    assert tuple(image.pixels)==before
