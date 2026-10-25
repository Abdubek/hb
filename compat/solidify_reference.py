import bpy,json,os

result={}
def sample(name,vertices,faces,**settings):
 for obj in list(bpy.data.objects):bpy.data.objects.remove(obj,do_unlink=True)
 data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces)
 obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj)
 mod=obj.modifiers.new('Solidify','SOLIDIFY');mod.thickness=.2;mod.offset=0
 if settings.pop('groups',False):
  group=obj.vertex_groups.new(name='Thickness');group.add([0],.25,'REPLACE');group.add([1],.75,'REPLACE');mod.vertex_group='Thickness';obj.vertex_groups.new(name='Shell');obj.vertex_groups.new(name='Rim')
 for key,value in settings.items():setattr(mod,key,value)
 bpy.context.view_layer.objects.active=obj;obj.select_set(True);bpy.ops.object.modifier_apply(modifier=mod.name)
 result[name]={'vertices':[list(v.co) for v in obj.data.vertices],'faces':[list(p.vertices) for p in obj.data.polygons],'weights':[[[g.group,g.weight] for g in v.groups] for v in obj.data.vertices]}
flat=[(0,0,0),(1,0,0),(1,1,0),(0,1,0)];ff=[(0,1,2,3)]
fold=flat+[(1,0,1),(1,1,1)];faces=ff+[(2,1,4,5)]
for mode in ('EXTRUDE','NON_MANIFOLD'):
 for even,quality in ((False,False),(True,False),(False,True),(True,True)):
  sample(mode+'_'+str(even)+'_'+str(quality),fold,faces,solidify_mode=mode,use_even_offset=even,use_quality_normals=quality)
 sample(mode+'_flat',flat,ff,solidify_mode=mode)
 sample(mode+'_groups',flat,ff,solidify_mode=mode,groups=True,thickness_vertex_group=.1)
 sample(mode+'_invert',flat,ff,solidify_mode=mode,groups=True,thickness_vertex_group=.1,invert_vertex_group=True)
 for clamp in (.5,1.):sample(mode+'_clamp'+str(clamp),fold,faces,solidify_mode=mode,thickness=4,thickness_clamp=clamp)
sample('nonmanifold_three',[(0,0,0),(1,0,0),(0,1,0),(0,-1,0),(0,0,1)],[(0,1,2),(1,0,3),(0,1,4)],solidify_mode='NON_MANIFOLD')

for mode in ('EXTRUDE','NON_MANIFOLD'):
 sample(mode+'_output_groups',flat,ff,solidify_mode=mode,groups=True,shell_vertex_group='Shell',rim_vertex_group='Rim')
 sample(mode+'_negative',fold,faces,solidify_mode=mode,thickness=-.2,offset=.5)
 sample(mode+'_rim_only',fold,faces,solidify_mode=mode,use_rim_only=True)
 sample(mode+'_no_rim',fold,faces,solidify_mode=mode,use_rim=False)
 sample(mode+'_zero',flat,ff,solidify_mode=mode,thickness=0)
 sample(mode+'_asymmetric_quality',[(0,0,0),(3,0,0),(2,1,0),(0,1,0),(3,0,2),(2,1,2)],faces,solidify_mode=mode,use_quality_normals=True)
verts=[(x,y,0) for y in range(3) for x in range(3)]
faces=[(y*3+x,y*3+x+1,y*3+x+4,y*3+x+3) for y in range(2) for x in range(2)]
for mode in ('EXTRUDE','NON_MANIFOLD'):
 sample(mode+'_grid_rim_only',verts,faces,solidify_mode=mode,use_rim_only=True)
 sample(mode+'_grid_flat',verts,faces,solidify_mode=mode,use_quality_normals=True,use_even_offset=True)
 sample(mode+'_group_offset_negative',flat,ff,solidify_mode=mode,groups=True,vertex_group='Thickness',offset=-1)
 sample(mode+'_group_offset_positive',flat,ff,solidify_mode=mode,groups=True,vertex_group='Thickness',offset=1)
sample('NON_MANIFOLD_rim_groups',flat,ff,solidify_mode='NON_MANIFOLD',groups=True,shell_vertex_group='Shell',rim_vertex_group='Rim',use_rim_only=True)
sample('NON_MANIFOLD_zero_groups',flat,ff,solidify_mode='NON_MANIFOLD',groups=True,shell_vertex_group='Shell',rim_vertex_group='Rim',thickness=0)
sample('NON_MANIFOLD_junction_groups',[(0,0,0),(1,0,0),(0,1,0),(0,-1,0),(0,0,1)],[(0,1,2),(1,0,3),(0,1,4)],solidify_mode='NON_MANIFOLD',groups=True,thickness_vertex_group=.1,shell_vertex_group='Shell',rim_vertex_group='Rim')
open(os.environ['HB_SOLIDIFY_RESULTS'],'w').write(json.dumps(result,indent=2)+'\n')
