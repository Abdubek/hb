import bpy,json,itertools
from pathlib import Path
out={}
for shape,scale,keep in itertools.product(('cube','opposed','collinear'),(1.,.0001,.000001),(False,True)):
 for obj in list(bpy.data.objects):bpy.data.objects.remove(obj,do_unlink=True)
 if shape=='cube':bpy.ops.mesh.primitive_cube_add();obj=bpy.context.object;mesh=obj.data
 else:
  mesh=bpy.data.meshes.new('Mesh');mesh.from_pydata([(0,0,0),(1,0,0),(0,1 if shape=='opposed' else 0,0)] if shape=='opposed' else [(0,0,0),(1,0,0),(2,0,0)],[],[(0,1,2),(2,1,0)] if shape=='opposed' else [(0,1,2)])
  obj=bpy.data.objects.new('Object',mesh);bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
 for v in mesh.vertices:v.co*=scale
 src=dict(vertices=[list(v.co) for v in mesh.vertices],faces=[list(p.vertices) for p in mesh.polygons])
 m=obj.modifiers.new('Weight','WEIGHTED_NORMAL');m.keep_sharp=keep;bpy.ops.object.modifier_apply(modifier=m.name)
 out[f'{shape}_{scale}_{keep}']=dict(source=src,keep=keep,normals=[list(n.vector) for n in mesh.corner_normals])
Path('/results/degenerate-reference.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
