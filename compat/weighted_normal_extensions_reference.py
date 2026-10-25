import bpy,json,itertools
from pathlib import Path
out={}
configs=[]
for mode,weight,thresh,smooth,keep in itertools.product(('FACE_AREA','CORNER_ANGLE','FACE_AREA_WITH_ANGLE'),(1,25,50,51,60,75,100),(0,.01,10),(False,True),(False,True)):
 configs.append(dict(mode=mode,weight=weight,thresh=thresh,smooth=smooth,keep=keep,custom=False,group='',invert=False,strength=False))
for mode,smooth,keep,custom,group,invert,strength in itertools.product(('FACE_AREA','CORNER_ANGLE','FACE_AREA_WITH_ANGLE'),(False,True),(False,True),(False,True),('Mask','Missing'),(False,True),(False,True)):
 configs.append(dict(mode=mode,weight=75,thresh=.2,smooth=smooth,keep=keep,custom=custom,group=group,invert=invert,strength=strength))
for i,cfg in enumerate(configs):
 for obj in list(bpy.data.objects):bpy.data.objects.remove(obj,do_unlink=True)
 bpy.ops.mesh.primitive_cube_add();obj=bpy.context.object;mesh=obj.data
 for v in mesh.vertices:v.co.x*=3;v.co.y*=2
 # Break equal area/angle ties with a sloped top.
 mesh.vertices[6].co.z+=.3
 for f in mesh.polygons:f.use_smooth=cfg['smooth']
 group=obj.vertex_groups.new(name='Mask')
 for k,w in ((0,0),(1,.1),(2,.5),(3,1)):group.add([k],w,'REPLACE')
 if cfg['strength']:
  attr=mesh.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
  for k,v in enumerate(attr.data):v.value=k%3
 if cfg['custom']:mesh.normals_split_custom_set([(.2,.3,1)]*24)
 source=dict(vertices=[list(v.co) for v in mesh.vertices],faces=[list(p.vertices) for p in mesh.polygons],normals=[list(n.vector) for n in mesh.corner_normals] if mesh.has_custom_normals else [])
 mod=obj.modifiers.new('Weight','WEIGHTED_NORMAL');mod.mode=cfg['mode'];mod.weight=cfg['weight'];mod.thresh=cfg['thresh'];mod.keep_sharp=cfg['keep'];mod.vertex_group=cfg['group'];mod.invert_vertex_group=cfg['invert'];mod.use_face_influence=cfg['strength']
 bpy.ops.object.modifier_apply(modifier=mod.name)
 out[str(i)]=dict(config=cfg,source=source,normals=[list(n.vector) for n in mesh.corner_normals])
Path('/results/reference.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
print('CAPTURED',len(out))
print([(p,bpy.types.WeightedNormalModifier.bl_rna.properties[p].hard_min,bpy.types.WeightedNormalModifier.bl_rna.properties[p].hard_max) for p in ('weight','thresh')])
