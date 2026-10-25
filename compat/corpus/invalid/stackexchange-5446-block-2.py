import bpy

group = bpy.data.node_groups.new(type="ShaderNodeTree", name="testgroup")
group.inputs.new("NodeSocketFloat", "Input One")
group.inputs.new("NodeSocketFloat", "Input Two")
input_node = group.nodes.new("NodeGroupInput")
input_node.location = (0, 0)

group.outputs.new("NodeSocketFloat", "Out")
output_node = group.nodes.new("NodeGroupOutput")
output_node.location = (600, 0)

gtr_math_node = group.nodes.new(type='ShaderNodeMath')
gtr_math_node.operation = "GREATER_THAN"
gtr_math_node.name = "greater"
gtr_math_node.location = (200, 100)
group.links.new(input_node.outputs["Input One"], gtr_math_node.inputs[0])

lss_math_node = group.nodes.new(type='ShaderNodeMath')
lss_math_node.operation = "LESS_THAN"
lss_math_node.name = "less"
lss_math_node.location = (200,-100)
group.links.new(input_node.outputs["Input Two"], lss_math_node.inputs[1])

add_math_node = group.nodes.new(type='ShaderNodeMath')
add_math_node.operation = "ADD"
add_math_node.name = "add"
add_math_node.location = (400, 0)

group.links.new(gtr_math_node.outputs["Value"], add_math_node.inputs[0])
group.links.new(lss_math_node.outputs["Value"], add_math_node.inputs[1])

group.links.new(add_math_node.outputs["Value"], output_node.inputs["Out"])

tree = bpy.context.object.active_material.node_tree
group_node = tree.nodes.new("ShaderNodeGroup")
group_node.node_tree = group
