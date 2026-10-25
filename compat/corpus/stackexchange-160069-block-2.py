import bpy

newmat = bpy.data.materials.new("VertCol")
newmat.use_nodes = True
node_tree = newmat.node_tree
nodes = node_tree.nodes

bsdf = nodes.get("Principled BSDF") 
'''
# alternatively

output, bsdf = nodes
'''


assert(bsdf) # make sure it exists to continue

vcol = nodes.new(type="ShaderNodeVertexColor")
vcol.layer_name = "VColor" # the vertex color layer name

# make links

node_tree.links.new(vcol.outputs[0], bsdf.inputs[0])
