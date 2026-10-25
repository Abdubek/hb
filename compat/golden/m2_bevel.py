"""Bevel contracts, written before implementing the supported cuboid kernel."""
HB_SYMBOLS={
'bpy.types.BevelModifier.name':'Modifier name',
'bpy.types.BevelModifier.type':'BEVEL',
'bpy.types.BevelModifier.segments':'Rounded edge segments, 1..8 on canonical cuboids; affine primitive UV layout or separate face islands; odd textured segments require locally aligned axes',
'bpy.types.BevelModifier.offset_type':'OFFSET only',
'bpy.types.BevelModifier.limit_method':'NONE/ANGLE on supported cuboids',
'bpy.types.BevelModifier.angle_limit':'Edge angle threshold in radians',
'bpy.types.BevelModifier.profile':'0.5 circular profile only',
'bpy.types.BevelModifier.loop_slide':'True only',
'bpy.types.BevelModifier.harden_normals':'False only',
'bpy.types.BevelModifier.material':'-1 inherited source face material',
'bpy.types.BevelModifier.show_viewport':'Viewport visibility',
'bpy.types.BevelModifier.show_render':'CPU preview visibility',
}
import bpy
for n in (1,2,3,4,5,6,7,8):
    bpy.ops.mesh.primitive_cube_add(size=2,calc_uvs=False,location=(n*3,0,0))
    obj=bpy.context.object;mod=obj.modifiers.new('Bevel','BEVEL')
    assert mod.affect=='EDGES' and mod.offset_type=='OFFSET' and mod.limit_method=='ANGLE'
    assert mod.profile==.5 and mod.use_clamp_overlap and mod.loop_slide
    assert not mod.harden_normals and mod.material==-1
    mod.width=.2;mod.segments=n
    bpy.ops.object.modifier_apply(modifier=mod.name)
# Keep descriptors and test evaluated export too.
bpy.ops.mesh.primitive_cube_add(size=1,calc_uvs=False,location=(0,3,0))
mod=bpy.context.object.modifiers.new('Rounded','BEVEL');mod.width=.02;mod.segments=3

# Arbitrary applied dimensions and an orthogonal local frame, not just unit cubes.
for size,width,n in ((.7,.01,1),(1.3,.12,3),(3.5,.4,6)):
    bpy.ops.mesh.primitive_cube_add(size=size,calc_uvs=False)
    obj=bpy.context.object;obj.scale=(2,1,.7)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    mod=obj.modifiers.new('Dimensioned','BEVEL');mod.width=width;mod.segments=n;mod.limit_method='NONE'
    bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.mesh.primitive_cube_add(size=2,calc_uvs=False)
obj=bpy.context.object;obj.rotation_euler=(.2,.3,.4)
bpy.ops.object.transform_apply(location=False,rotation=True,scale=False)
mod=obj.modifiers.new('Rotated','BEVEL');mod.width=.13;mod.segments=3
bpy.ops.object.modifier_apply(modifier=mod.name)

# Uniform material/smooth propagation and genuine no-op modes.
paint=bpy.data.materials.new('Paint');paint.diffuse_color=(.2,.5,.7,1)
bpy.ops.mesh.primitive_cube_add(size=2,calc_uvs=False)
obj=bpy.context.object;obj.data.materials.append(paint);bpy.ops.object.shade_smooth()
mod=obj.modifiers.new('Smooth','BEVEL');mod.width=.15;mod.segments=4;mod.angle_limit=.3
mod.show_viewport=False;mod.show_viewport=True;mod.show_render=False;mod.show_render=True
bpy.ops.object.modifier_apply(modifier=mod.name)
for width,angle in ((0,.5),(.1,2.)):
    bpy.ops.mesh.primitive_cube_add(calc_uvs=False)
    mod=bpy.context.object.modifiers.new('Disabled','BEVEL');mod.width=width;mod.angle_limit=angle
    if width==0:
        try:bpy.ops.object.modifier_apply(modifier=mod.name)
        except RuntimeError:pass
        else:raise AssertionError('Zero-width modifier should be disabled')
    else:bpy.ops.object.modifier_apply(modifier=mod.name)
    assert len(bpy.context.object.data.vertices)==8
