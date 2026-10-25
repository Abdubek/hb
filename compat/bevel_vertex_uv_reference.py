"""Vertex-bevel UV interpolation across widths, seam layouts and local frames."""
import bpy
for mode in ('default','islands'):
    for segments in range(1,9):
        for width in (.005,.014,.0142,.03,.21):
            bpy.ops.mesh.primitive_cube_add()
            obj=bpy.context.object;obj.name=f'{mode}-{segments}-{width}'
            obj.scale=(1.7,.6,1.2)
            bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
            if mode=='islands':
                for polygon in obj.data.polygons:
                    for j,li in enumerate(polygon.loop_indices):
                        obj.data.uv_layers.active.data[li].uv=(polygon.index*2+(j in (1,2)),j in (2,3))
            secondary=obj.data.uv_layers.new(name='Secondary')
            for loop in secondary.data:loop.uv=(loop.uv.x*.7+.2,loop.uv.y*.9-.1)
            mod=obj.modifiers.new('Rounded','BEVEL');mod.width=width;mod.segments=segments;mod.affect='VERTICES'
            bpy.ops.object.modifier_apply(modifier=mod.name)
            assert len(obj.data.uv_layers)==2
# Even segment counts also support an arbitrary orthogonal local frame.
for segments in (2,4,6,8):
    bpy.ops.mesh.primitive_cube_add()
    obj=bpy.context.object;obj.rotation_euler=(.2,.3,.4)
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=False)
    mod=obj.modifiers.new('Rotated UV','BEVEL');mod.width=.07;mod.segments=segments;mod.affect='VERTICES'
    bpy.ops.object.modifier_apply(modifier=mod.name)
