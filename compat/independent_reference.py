"""Blender-side independent script runner; invoked only inside the isolated image."""
import bpy,json,sys,traceback,random
from pathlib import Path
script,result,export=sys.argv[sys.argv.index('--')+1:]
phase='script'
try:
    for kind in ('objects','meshes','materials','cameras','lights','images','textures','curves','collections'):
        db=getattr(bpy.data,kind)
        for block in list(db):db.remove(block)
    c=bpy.data.collections.new('Collection');bpy.context.scene.collection.children.link(c)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children['Collection']
    bpy.context.scene.camera=None
    random.seed(0)
    exec(compile(Path(script).read_text(),script,'exec'),{'__name__':'__main__','__file__':script})
    bpy.context.view_layer.update()
    summary=[{'name':o.name,'type':o.type} for o in bpy.context.scene.objects]
    phase='export'
    bpy.ops.export_scene.gltf(filepath=export,export_format='GLB',export_cameras=True,export_lights=True,export_apply=True)
    data={'ok':True,'objects':summary,'blender':bpy.app.version_string}
except BaseException as exc:
    data={'ok':False,'phase':phase,'error':type(exc).__name__+': '+str(exc),'traceback':traceback.format_exc(),'blender':bpy.app.version_string}
Path(result).write_text(json.dumps(data,indent=2)+'\n')
