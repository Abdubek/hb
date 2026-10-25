import bpy

# ensure we are in edit mode
bpy.ops.object.mode_set(mode="EDIT")

# configurable parameters
src_group = "Arm_03.L"
dst_group = "Arm_02.L"

obj = bpy.context.edit_object
src_group_index = obj.vertex_groups[src_group].index
dst_group_index = obj.vertex_groups[dst_group].index

mesh = obj.data

# Saving vertex indices only, instead of vertex objects in this list
# Copy v.groups.group, do not reference v.groups (unstable)
sel_verts_ig = [[v.index, [g.group for g in v.groups]] for v in mesh.vertices if v.select]

# no more SEGFAULT in this line
bpy.ops.object.mode_set(mode="OBJECT")

print("Working")

for ig in sel_verts_ig:
    v1in = False
    v2in = False
    i = ig[0]
    for g in ig[1]:
        if g == src_group_index:
            v1in = True
        if g == dst_group_index:
            v2in = True
    if v1in and v2in:
        obj.vertex_groups[dst_group].add([i], 1.0 - obj.vertex_groups[src_group].weight(i), 'REPLACE')

print("Finished")
