import bpy,json,sys
from pathlib import Path
font=bpy.data.fonts.load('/results/DejaVuSans.ttf')
cases=[]
for body in ('A','V','AV','Hi','O','B','g',' ','A B','Hello','Text\nnext'):
 for res in (1,3,12):
  c=bpy.data.curves.new('Text','FONT');c.font=font;c.body=body;c.resolution_u=res
  o=bpy.data.objects.new('Text',c);bpy.context.collection.objects.link(o);bpy.context.view_layer.update()
  m=o.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
  cases.append(dict(body=body,res=res,defaults={k:getattr(c,k) for k in ('size','space_character','space_word','space_line','align_x','align_y','extrude','bevel_depth','offset')},vertices=[list(v.co) for v in m.vertices],faces=[list(f.vertices) for f in m.polygons],uv=[list(u.uv) for u in m.uv_layers.active.data] if m.uv_layers else []))
  bpy.data.objects.remove(o,do_unlink=True);bpy.data.curves.remove(c)
Path(sys.argv[-1]).write_text(json.dumps(cases))
