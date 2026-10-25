import bpy

# Reference the node group
geometry_node = bpy.data.node_groups['Geometry Nodes']

# Reference the String to Curves node
curve_node = geometry_node.nodes['String to Curves']

# Get the font
font = curve_node.font
print(font)
# Get the font name
print(font.name)
