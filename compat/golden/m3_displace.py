"""Vertex-group displacement and corner normals, from Blender reference probes."""
import bpy
for direction in ('NORMAL','X','Y','Z'):
    for invert in (False,True):
        bpy.ops.mesh.primitive_cube_add()
        obj=bpy.context.object;obj.name=f'Displace {direction} {invert}'
        group=obj.vertex_groups.new(name='Mask')
        for i in range(7):group.add([i],(i%4)/3,'REPLACE')
        obj.data.normals_split_custom_set([(.2,.3,1)]*24)
        texture=bpy.data.textures.new('Cells',type='CLOUDS');texture.noise_basis='CELL_NOISE';texture.noise_depth=2;texture.noise_scale=.35
        modifier=obj.modifiers.new('Displace','DISPLACE');modifier.direction=direction
        modifier.strength=.4;modifier.mid_level=.2;modifier.texture=texture
        modifier.vertex_group='Mask';modifier.invert_vertex_group=invert
        bpy.ops.object.modifier_apply(modifier=modifier.name)
