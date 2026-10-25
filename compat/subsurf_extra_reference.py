import bpy,json,math
from pathlib import Path
out={}
for case in ('creased_off','finite','level6','smooth_normals','smooth_preserved','ngon_colors','branched_wire','wire_creases','surface_and_wire'):
 for obj in list(bpy.data.objects):bpy.data.objects.remove(obj,do_unlink=True)
 if case in ('branched_wire','wire_creases','surface_and_wire'):
  mesh=bpy.data.meshes.new(case)
  vs=[(0,0,0),(1,1,0),(2,0,0),(1,2,0)];es=[(0,1),(1,2),(1,3)];fs=[]
  if case=='surface_and_wire':vs += [(4,0,0),(5,0,0),(5,1,0),(4,1,0)];fs=[(4,5,6,7)]
  mesh.from_pydata(vs,es,fs);obj=bpy.data.objects.new(case,mesh);bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
 elif case=='ngon_colors':
  mesh=bpy.data.meshes.new(case);mesh.from_pydata([(math.cos(i*2*math.pi/5),math.sin(i*2*math.pi/5),0) for i in range(5)],[],[tuple(range(5))]);obj=bpy.data.objects.new(case,mesh);bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
 else:bpy.ops.mesh.primitive_cube_add();obj=bpy.context.object;mesh=obj.data
 if case in ('creased_off','finite','wire_creases'):
  a=mesh.attributes.new(name='crease_edge',type='FLOAT',domain='EDGE')
  for i,v in enumerate(a.data):v.value=(i%3)*.4
  a=mesh.attributes.new(name='crease_vert',type='FLOAT',domain='POINT')
  for i,v in enumerate(a.data):v.value=(i%4)*.25
 if case.startswith('smooth'):
  for f in mesh.polygons:f.use_smooth=True
  mesh.normals_split_custom_set([(0,.2,1)]*len(mesh.loops))
 if case=='ngon_colors':
  a=mesh.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='CORNER')
  for i,v in enumerate(a.data):v.color=(i/5,.4,.1,1)
 def record(mesh):return dict(vertices=[list(v.co) for v in mesh.vertices],edges=[list(e.vertices) for e in mesh.edges],faces=[list(p.vertices) for p in mesh.polygons],uv=[list(d.uv) for d in mesh.uv_layers[0].data] if mesh.uv_layers else [],normals=[list(n.vector) for n in mesh.corner_normals] if mesh.has_custom_normals else [],has_normals=mesh.has_custom_normals,colors=[list(d.color) for d in mesh.color_attributes['Color'].data] if mesh.color_attributes.get('Color') else [],smooth=[p.use_smooth for p in mesh.polygons],creases={name:[d.value for d in mesh.attributes[name].data] for name in ('crease_edge','crease_vert') if mesh.attributes.get(name)})
 source=record(mesh)
 mod=obj.modifiers.new('Subdivision','SUBSURF');mod.levels=6 if case=='level6' else 2
 mod.use_creases=case!='creased_off';mod.use_limit_surface=case!='finite';mod.use_custom_normals=case=='smooth_preserved'
 settings=dict(levels=mod.levels,use_creases=mod.use_creases,use_limit_surface=mod.use_limit_surface,use_custom_normals=mod.use_custom_normals)
 bpy.ops.object.modifier_apply(modifier=mod.name)
 out[case]=dict(input=source,settings=settings,output=record(obj.data))
Path('/results/reference-extra.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
