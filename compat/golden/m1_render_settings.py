HB_SYMBOLS={
'bpy.context.scene.render':'Scene render output settings',
'bpy.context.scene.render.resolution_x':'Image width',
'bpy.context.scene.render.resolution_y':'Image height',
'bpy.context.scene.render.resolution_percentage':'Resolution percentage',
'bpy.context.scene.render.pixel_aspect_x':'Horizontal pixel aspect',
'bpy.context.scene.render.pixel_aspect_y':'Vertical pixel aspect',
'bpy.context.scene.render.filepath':'Render output path',
}
import bpy
r=bpy.context.scene.render
r.resolution_x=512;r.resolution_y=256;r.resolution_percentage=50
r.pixel_aspect_x=1;r.pixel_aspect_y=2;r.filepath='/tmp/hb-preview.png'
assert (r.resolution_x,r.resolution_y,r.resolution_percentage)==(512,256,50)
assert r.pixel_aspect_x==1 and r.pixel_aspect_y==2
assert r.filepath=='/tmp/hb-preview.png'
