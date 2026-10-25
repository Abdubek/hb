import bpy

for area in bpy.context.screen.areas:
    if area.type == "NODE_EDITOR":
        override = {'screen': bpy.context.screen, 'area': area}

# create a group
test_group = bpy.data.node_groups.new('testGroup', 'ShaderNodeTree')

# create group inputs
group_inputs = test_group.nodes.new('NodeGroupInput')
group_inputs.location = (-350,0)

# create group outputs
group_outputs = test_group.nodes.new('NodeGroupOutput')
group_outputs.location = (300,0)

# add group to active material
bpy.ops.node.add_node(override,settings=[{"name":"node_tree", "value":"bpy.data.node_groups['"+test_group.name+"']"}], type="ShaderNodeGroup")
# put group into edit mode
bpy.ops.node.group_edit(override)

# create group input/output sockets
bpy.ops.node.tree_socket_add(override, in_out='IN')
test_group.inputs[0].name = 'in_to_greater'
bpy.ops.node.tree_socket_add(override, in_out='IN')
test_group.inputs[1].name = 'in_to_less'
bpy.ops.node.tree_socket_add(override, in_out='OUT')
test_group.outputs[0].name = 'out_result'

# create three math nodes in a group
node_add = test_group.nodes.new('ShaderNodeMath')
node_add.operation = 'ADD'
node_add.location = (100,0)

node_greater = test_group.nodes.new('ShaderNodeMath')
node_greater.operation = 'GREATER_THAN'
node_greater.label = 'greater'
node_greater.location = (-100,100)

node_less = test_group.nodes.new('ShaderNodeMath')
node_less.operation = 'LESS_THAN'
node_less.label = 'less'
node_less.location = (-100,-100)

# link nodes together
test_group.links.new(node_add.inputs[0], node_greater.outputs[0])
test_group.links.new(node_add.inputs[1], node_less.outputs[0])
test_group.links.new(group_inputs.outputs[0], node_greater.inputs[0])
test_group.links.new(group_inputs.outputs[1], node_less.inputs[0])
test_group.links.new(node_add.outputs[0], group_outputs.inputs[0])
