import bpy
font=bpy.data.fonts.load(font_path)
for i,case in enumerate(cases):
 c=bpy.data.curves.new('Text_%03d'%i,'FONT');c.font=font;c.body=case['body'];c.resolution_u=case['res'];c.size=case.get('size',1.);c.align_x=case.get('align','LEFT');c.space_line=case.get('spacing',1.)
 o=bpy.data.objects.new(c.name,c);bpy.context.collection.objects.link(o)
 assert o.type=='FONT'
bpy.context.view_layer.update()
