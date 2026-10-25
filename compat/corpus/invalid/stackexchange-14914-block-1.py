import bpy

scene = bpy.context.scene
nodes = scene.node_tree.nodes

render_layers = nodes['Render Layers']
output_file = nodes.new("CompositorNodeOutputFile")
output_file.base_path = "//maFolder/"

scene.node_tree.links.new(
    render_layers.outputs['Image'],
    output_file.inputs['Image']
)
