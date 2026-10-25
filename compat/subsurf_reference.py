import bpy,json
from pathlib import Path
out={}
for case in ('cube','crease_edge','crease_vert','custom','wire','loose_vertex'):
 for level in (1,2,4):
  for simple in (False,True):
   for obj in list(bpy.data.objects):bpy.data.objects.remove(obj,do_unlink=True)
   if case in ('wire','loose_vertex'):
    mesh=bpy.data.meshes.new(case);mesh.from_pydata([(0,0,0),(1,1,0),(2,0,0),(3,1,0)] if case=='wire' else [(2,3,4)],[(0,1),(1,2),(2,3)] if case=='wire' else [],[])
    obj=bpy.data.objects.new(case,mesh);bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
   else:bpy.ops.mesh.primitive_cube_add();obj=bpy.context.object;mesh=obj.data
   if case.startswith('crease'):
    attr=mesh.attributes.new(name=case,type='FLOAT',domain='EDGE' if case=='crease_edge' else 'POINT')
    for i,d in enumerate(attr.data):d.value=(i%3)*.5
   if case=='custom':
    mesh.normals_split_custom_set([(0,.2,1)]*24)
    color=mesh.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='CORNER')
    for i,d in enumerate(color.data):d.color=(i/24,.2,.4,1)
   mod=obj.modifiers.new('Subdivision','SUBSURF');mod.levels=level;mod.subdivision_type='SIMPLE' if simple else 'CATMULL_CLARK'
   bpy.ops.object.modifier_apply(modifier=mod.name)
   mesh=obj.data
   out[f'{case}_{level}_{simple}']=dict(vertices=[list(v.co) for v in mesh.vertices],edges=[list(e.vertices) for e in mesh.edges],faces=[list(p.vertices) for p in mesh.polygons],uv=[list(d.uv) for d in mesh.uv_layers[0].data] if mesh.uv_layers else [],normals=[list(n.vector) for n in mesh.corner_normals] if mesh.has_custom_normals else [],has_normals=mesh.has_custom_normals,colors=[list(d.color) for d in mesh.color_attributes['Color'].data] if mesh.color_attributes.get('Color') else [],creases={name:[d.value for d in mesh.attributes[name].data] for name in ('crease_edge','crease_vert') if mesh.attributes.get(name)})
Path('/results/reference.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
