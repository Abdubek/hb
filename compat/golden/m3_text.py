HB_GLTF_TEXT_NODES=('Label_0','Label_1','Label_2','Label_3','Label_4')
import bpy
font=bpy.data.fonts.load(__file__.rsplit('/',2)[0]+'/fixtures/fonts/DejaVuSans.ttf')
assert font.name=='DejaVu Sans Book'
for i,body in enumerate(('AV','Hello world','Text\nnext','i!j?','O B g')):
 bpy.ops.object.text_add(location=(i*3,0,0))
 obj=bpy.context.object;obj.name='Label_%d'%i;text=obj.data;text.font=font;text.body=body;text.size=.8;text.align_x='CENTER';text.resolution_u=3
 mat=bpy.data.materials.new('Ink_%d'%i);mat.diffuse_color=(.1,.3,.7,1);text.materials.append(mat)
 assert obj.type=='FONT' and text.font.name==font.name
bpy.context.view_layer.update()
