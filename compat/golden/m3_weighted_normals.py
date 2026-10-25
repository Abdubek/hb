"""Bounded weight/threshold, membership and reserved face-strength contracts."""
import bpy
for mode in ('FACE_AREA','CORNER_ANGLE','FACE_AREA_WITH_ANGLE'):
    for keep in (False,True):
        for invert in (False,True):
            bpy.ops.mesh.primitive_cube_add()
            obj=bpy.context.object;obj.name=f'Weighted {mode} {keep} {invert}'
            mesh=obj.data
            for v in mesh.vertices:v.co.x*=3;v.co.y*=2
            mesh.vertices[6].co.z+=.3
            group=obj.vertex_groups.new(name='Mask')
            for i,weight in ((0,0),(1,.1),(2,.5),(3,1)):group.add([i],weight,'REPLACE')
            mesh.normals_split_custom_set([(.2,.3,1)]*24)
            strength=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
            assert strength.name=='__mod_weightednormals_faceweight' and strength.domain=='FACE' and strength.data_type=='INT'
            assert mesh.attributes.get(strength.name) is not None
            for i,value in enumerate(strength.data):value.value=i%3
            mod=obj.modifiers.new('Weighted','WEIGHTED_NORMAL');mod.mode=mode;mod.weight=75;mod.thresh=.2
            mod.vertex_group='Mask';mod.invert_vertex_group=invert;mod.keep_sharp=keep;mod.use_face_influence=True
            bpy.ops.object.modifier_apply(modifier=mod.name)
