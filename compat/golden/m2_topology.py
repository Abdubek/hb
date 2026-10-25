"""Topology modifier contracts, authored before implementation."""
HB_SYMBOLS={
'bpy.types.MirrorModifier.name':'Modifier name', 'bpy.types.MirrorModifier.type':'MIRROR',
'bpy.types.MirrorModifier.use_axis':'X/Y/Z axis flags; axes applied in order',
'bpy.types.MirrorModifier.use_mirror_merge':'Merge matching vertices across the mirror plane',
'bpy.types.MirrorModifier.merge_threshold':'Mirror seam distance threshold',
'bpy.types.MirrorModifier.use_clip':'Edit-mode clipping flag; no effect on object-mode evaluation',
'bpy.types.MirrorModifier.show_viewport':'Viewport evaluation flag', 'bpy.types.MirrorModifier.show_render':'CPU preview evaluation flag',
'bpy.types.TriangulateModifier.name':'Modifier name', 'bpy.types.TriangulateModifier.type':'TRIANGULATE',
'bpy.types.TriangulateModifier.min_vertices':'Minimum face vertex count',
'bpy.types.TriangulateModifier.show_viewport':'Viewport evaluation flag', 'bpy.types.TriangulateModifier.show_render':'CPU preview evaluation flag',
'bpy.types.SolidifyModifier.name':'Modifier name', 'bpy.types.SolidifyModifier.type':'SOLIDIFY',
'bpy.types.SolidifyModifier.solidify_mode':'EXTRUDE on oriented manifold surfaces',
'bpy.types.SolidifyModifier.thickness':'Signed shell thickness', 'bpy.types.SolidifyModifier.offset':'Thickness offset -1..1',
'bpy.types.SolidifyModifier.use_rim':'Generate boundary walls', 'bpy.types.SolidifyModifier.use_rim_only':'Keep original surface and boundary walls; omit the inner shell',
'bpy.types.SolidifyModifier.use_even_offset':'False only', 'bpy.types.SolidifyModifier.use_quality_normals':'False only',
'bpy.types.SolidifyModifier.thickness_clamp':'0 only', 'bpy.types.SolidifyModifier.material_offset':'Inner shell material offset',
'bpy.types.SolidifyModifier.material_offset_rim':'Rim material offset',
'bpy.types.SolidifyModifier.show_viewport':'Viewport evaluation flag', 'bpy.types.SolidifyModifier.show_render':'CPU preview evaluation flag',
}
import bpy

def sheet(name,vertices,faces):
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces)
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active=obj;obj.select_set(True)
    layer=mesh.uv_layers.new(name='UV')
    for i,loop in enumerate(layer.data):loop.uv=((i%4)/3,(i%3)/2)
    for i in range(3):
        paint=bpy.data.materials.new(name+str(i));paint.diffuse_color=(.2+i*.2,.3,.5,1);mesh.materials.append(paint)
    return obj
for axes,merge in [((True,False,False),False),((True,False,False),True),((True,True,False),True),((False,False,True),False)]:
    obj=sheet('Mirror',[(0,-1,0),(2,-1,0),(2,1,0),(0,1,0)],[(0,1,2,3)])
    modifier=obj.modifiers.new('Mirror','MIRROR')
    assert modifier.type=='MIRROR' and tuple(modifier.use_axis)==(True,False,False)
    assert modifier.use_mirror_merge and not modifier.use_clip
    modifier.use_axis=axes;modifier.use_mirror_merge=merge;modifier.merge_threshold=.001;modifier.use_clip=True
    modifier.show_viewport=False;modifier.show_viewport=True;modifier.show_render=False;modifier.show_render=True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
for method in ('FIXED','FIXED_ALTERNATE','SHORTEST_DIAGONAL','LONGEST_DIAGONAL'):
    obj=sheet('Triangles',[(0,0,0),(3,0,0),(2,1,0),(0,2,0),(0,3,0)],[(0,1,2,3),(3,2,4)])
    modifier=obj.modifiers.new('Triangulate','TRIANGULATE')
    assert modifier.type=='TRIANGULATE' and modifier.min_vertices==4 and not modifier.keep_custom_normals
    modifier.quad_method=method;modifier.ngon_method='CLIP';modifier.min_vertices=4
    modifier.show_viewport=True;modifier.show_render=True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    assert len(obj.data.polygons)==3
for thickness,offset,rim,rim_only in [(.2,-1,True,False),(.3,0,True,False),(-.2,1,True,False),(.2,-1,False,False),(.2,-1,True,True)]:
    obj=sheet('Shell',[(0,0,0),(2,0,0),(2,1,0),(0,1,0)],[(0,1,2,3)])
    modifier=obj.modifiers.new('Solidify','SOLIDIFY')
    assert modifier.type=='SOLIDIFY' and modifier.solidify_mode=='EXTRUDE'
    assert modifier.offset==-1 and modifier.use_rim and not modifier.use_rim_only
    assert not modifier.use_even_offset and not modifier.use_quality_normals and modifier.thickness_clamp==0
    modifier.thickness=thickness;modifier.offset=offset;modifier.use_rim=rim;modifier.use_rim_only=rim_only
    modifier.material_offset=1;modifier.material_offset_rim=2
    modifier.show_viewport=True;modifier.show_render=True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    assert len(obj.data.polygons)==(5 if rim_only else 6 if rim else 2)
# Keep an evaluated stack to compare non-destructive GLB export too.
obj=sheet('Stack',[(0,0,0),(2,0,0),(2,1,0),(0,1,0)],[(0,1,2,3)])
modifier=obj.modifiers.new('Mirror','MIRROR')
modifier=obj.modifiers.new('Shell','SOLIDIFY');modifier.thickness=.25
modifier=obj.modifiers.new('Triangles','TRIANGULATE');modifier.quad_method='FIXED'
assert len(obj.data.polygons)==1

# Boundary, concave quad, folded shell and closed rim-only regressions.
obj=sheet('Seam',[(0,0,0),(0,1,0),(0,1,1),(0,0,1)],[(0,1,2,3)])
mod=obj.modifiers.new('Seam','MIRROR');bpy.ops.object.modifier_apply(modifier=mod.name)
obj=sheet('Concave',[(0,0,0),(3,0,0),(.5,.5,0),(0,3,0)],[(0,1,2,3)])
mod=obj.modifiers.new('Concave','TRIANGULATE');mod.quad_method='FIXED_ALTERNATE';bpy.ops.object.modifier_apply(modifier=mod.name)
obj=sheet('Fold',[(0,0,0),(1,0,0),(1,1,0),(0,1,0),(1,0,1),(1,1,1)],[(0,1,2,3),(2,1,4,5)])
mod=obj.modifiers.new('Fold','SOLIDIFY');mod.thickness=.2;bpy.ops.object.modifier_apply(modifier=mod.name)
for d in (.00025,.0005,.00075):
 m=bpy.data.meshes.new('Threshold');m.from_pydata([(d,0,0),(1,0,0),(1,1,0),(d,1,0)],[],[(0,1,2,3)]);o=bpy.data.objects.new('Threshold',m);bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o;o.select_set(True);mod=o.modifiers.new('Mirror','MIRROR');bpy.ops.object.modifier_apply(modifier=mod.name)
for only,rim in ((True,True),(True,False),(False,True)):
 bpy.ops.mesh.primitive_cube_add();o=bpy.context.object;mod=o.modifiers.new('Shell','SOLIDIFY');mod.use_rim_only=only;mod.use_rim=rim;bpy.ops.object.modifier_apply(modifier=mod.name)

obj=sheet('DisabledAxes',[(0,0,0),(1,0,0),(1,1,0),(0,1,0)],[(0,1,2,3)])
mod=obj.modifiers.new('Disabled','MIRROR');mod.use_axis[0]=False
bpy.ops.object.modifier_apply(modifier=mod.name)
assert len(obj.data.vertices)==4
obj=sheet('SkippedNgon',[(0,0,0),(2,0,0),(3,1,0),(1,2,0),(0,1,0)],[(0,1,2,3,4)])
mod=obj.modifiers.new('Skip','TRIANGULATE');mod.min_vertices=6
bpy.ops.object.modifier_apply(modifier=mod.name)
assert len(obj.data.polygons)==1
