"""Procedural cell-noise displacements, authored against Blender first."""
import bpy, math
HB_EQUIVALENT_MESH_PREFIXES=('Displace sphere',)
HB_SYMBOLS={
'bpy.data.textures.new':'Create a CLOUDS procedural texture',
'bpy.data.textures.remove':'Remove textures and unlink modifier users',
'bpy.types.CloudsTexture.name':'Texture data-block name',
'bpy.types.CloudsTexture.type':'CLOUDS type',
'bpy.types.CloudsTexture.users':'Texture user count',
'bpy.types.CloudsTexture.noise_basis':'CELL_NOISE evaluation; BLENDER_ORIGINAL default readable',
'bpy.types.CloudsTexture.noise_scale':'Procedural noise scale',
'bpy.types.CloudsTexture.noise_depth':'Noise octaves, 0..30',
'bpy.types.CloudsTexture.noise_type':'SOFT_NOISE or HARD_NOISE',
'bpy.types.CloudsTexture.cloud_type':'GRAYSCALE',
'bpy.types.CloudsTexture.intensity':'Texture brightness',
'bpy.types.CloudsTexture.contrast':'Texture contrast',
'bpy.types.CloudsTexture.evaluate':'Evaluate cell-noise texture at local coordinates',
'bpy.types.DisplaceModifier.name':'Modifier name',
'bpy.types.DisplaceModifier.type':'DISPLACE type',
'bpy.types.DisplaceModifier.texture':'Procedural CLOUDS texture or None',
'bpy.types.DisplaceModifier.strength':'Displacement strength',
'bpy.types.DisplaceModifier.mid_level':'Neutral intensity',
'bpy.types.DisplaceModifier.direction':'NORMAL, X, Y or Z',
'bpy.types.DisplaceModifier.space':'LOCAL',
'bpy.types.DisplaceModifier.texture_coords':'LOCAL',
'bpy.types.DisplaceModifier.show_viewport':'Viewport evaluation flag',
'bpy.types.DisplaceModifier.show_render':'Render evaluation flag',
}
tex=bpy.data.textures.new('Cell texture',type='CLOUDS')
assert tex.type=='CLOUDS' and tex.noise_basis=='BLENDER_ORIGINAL'
assert tex.noise_scale==.25 and tex.noise_depth==2 and tex.noise_type=='SOFT_NOISE'
assert tex.cloud_type=='GRAYSCALE' and tex.intensity==1 and tex.contrast==1
tex.noise_basis='CELL_NOISE';tex.cloud_type='GRAYSCALE';tex.noise_scale=.37;tex.noise_depth=3;tex.noise_type='HARD_NOISE';tex.intensity=.8;tex.contrast=1.2
# Values separately asserted to cover the evaluate return convention.
values=[list(tex.evaluate(p)) for p in [(0,0,0),(.1,.2,.3),(-1,.25,2)]]
for value in values:assert len(value)==4 and value[:3]==[0,0,0]
for direction in ('NORMAL','X','Y','Z'):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=1.3,location=(0,0,0))
    o=bpy.context.object;o.name='Displace '+direction;o.data.name='Displace sphere'
    m=o.modifiers.new('Noise','DISPLACE');assert m.direction=='NORMAL' and m.strength==1 and m.mid_level==.5 and m.space=='LOCAL' and m.texture_coords=='LOCAL' and m.texture is None
    m.texture=tex;m.strength=.27;m.mid_level=.4;m.direction=direction;m.space='LOCAL';m.texture_coords='LOCAL';m.vertex_group='';m.invert_vertex_group=False
    m.show_render=False;m.show_render=True;m.show_viewport=False;m.show_viewport=True
    assert m.type=='DISPLACE' and m.texture.name==tex.name
    bpy.ops.object.modifier_apply(modifier=m.name)
assert tex.users==0
# Retained texture and stack descriptors plus a zero-strength modifier.
bpy.ops.mesh.primitive_plane_add(size=3);o=bpy.context.object
s=o.modifiers.new('Grid','SUBSURF');s.subdivision_type='SIMPLE';s.levels=3
m=o.modifiers.new('Noise','DISPLACE');m.texture=tex;m.strength=.2;m.direction='Z'
assert tex.users==1
tex.name='Rock grain'
other=bpy.data.textures.new('Unused',type='CLOUDS');bpy.data.textures.remove(other)
# Missing texture gives constant normal displacement, including loose vertices.
for direction in ('NORMAL','X','Y','Z'):
    mesh=bpy.data.meshes.new('Displaced surface');mesh.from_pydata([(0,0,0),(2,0,0),(2,1,.5),(0,1,0),(3,0,0)],[],[(0,1,2,3)])
    obj=bpy.data.objects.new('Uniform '+direction,mesh);bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
    m=obj.modifiers.new('Uniform','DISPLACE');m.direction=direction;m.strength=.13;m.mid_level=.3
    bpy.ops.object.modifier_apply(modifier=m.name)
# Capture evaluation reference as mesh data, with deterministic coordinates.
mesh=bpy.data.meshes.new('Texture samples');mesh.from_pydata([(v[3],i,0) for i,v in enumerate(values)],[],[])
o=bpy.data.objects.new('Texture samples',mesh);bpy.context.collection.objects.link(o)
