import bpy
font=bpy.data.fonts.load(__file__.rsplit('/',2)[0]+'/fixtures/fonts/DejaVuSans.ttf')
bpy.ops.object.text_add()
o=bpy.context.object;o.name='Raised label';o.data.font=font;o.data.body='HB 3D'
o.data.extrude=.08;o.data.size=2.
bpy.context.view_layer.update()
assert abs(o.dimensions.z-.16)<1e-6
assert o.data.extrude>.079
