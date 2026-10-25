import bpy

scene = bpy.context.scene
nodes = scene.node_tree.nodes

output_file = nodes.new("CompositorNodeOutputFile")
# output_file.base_path = "//maFolder/"

output_file.file_slots.remove(output_file.inputs[0])
for i in range(0, 20):
    idx = str(i + 1)
    if i < 9:
        idx = "0" + idx
    output_file.file_slots.new("set_" + idx)
