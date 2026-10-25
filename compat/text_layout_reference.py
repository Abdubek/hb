import bpy,json,sys,string,itertools
from pathlib import Path
font=bpy.data.fonts.load('/results/DejaVuSans.ttf');cases=[]
settings=[dict(body=ch,res=res,align='LEFT',size=1.,spacing=1.) for ch,res in itertools.product(string.printable[:94],(1,3,12))]
settings += [dict(body=body,res=3,align=align,size=size,spacing=spacing) for body,align,size,spacing in itertools.product(('AV','Hello world','Text\nnext'),('LEFT','CENTER','RIGHT'),(.5,2.),(.8,1.3))]
for params in settings:
 c=bpy.data.curves.new('Text','FONT');c.font=font;c.body=params['body'];c.resolution_u=params['res'];c.align_x=params['align'];c.size=params['size'];c.space_line=params['spacing']
 o=bpy.data.objects.new('Text',c);bpy.context.collection.objects.link(o);bpy.context.view_layer.update();m=o.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
 cases.append(dict(**params,font_name=font.name,vertices=[list(v.co) for v in m.vertices],faces=[list(f.vertices) for f in m.polygons],smooth=[f.use_smooth for f in m.polygons],uv=[list(u.uv) for u in m.uv_layers.active.data] if m.uv_layers else []))
 bpy.data.objects.remove(o,do_unlink=True);bpy.data.curves.remove(c)
Path(sys.argv[-1]).write_text(json.dumps(cases))
