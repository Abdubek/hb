"""Camera render operator: file side effect, resolution percentage, PNG output."""
HB_REFERENCE_RENDER_ENGINE=('CYCLES',)
import bpy,os,struct
bpy.ops.mesh.primitive_cube_add()
bpy.ops.object.camera_add(location=(0,-6,3),rotation=(1.1,0,0))
bpy.context.scene.camera=bpy.context.object
settings=bpy.context.scene.render
settings.resolution_x=100;settings.resolution_y=60;settings.resolution_percentage=50
path=os.path.join(os.environ.get('TMPDIR','/tmp'),'hb-render-'+str(os.getpid())+'.png')
settings.filepath=path
try:
    assert bpy.ops.render.render(write_still=False)=={'FINISHED'}
    assert not os.path.exists(path)
    assert bpy.ops.render.render(write_still=True)=={'FINISHED'}
    data=open(path,'rb').read()
    assert data[:8]==b'\x89PNG\r\n\x1a\n'
    assert struct.unpack_from('>II',data,16)==(50,30)
finally:
    if os.path.exists(path):os.unlink(path)
# Render Result is Blender's volatile render buffer, not a scene asset.
for image in list(bpy.data.images):
    if image.name=='Render Result':bpy.data.images.remove(image)
