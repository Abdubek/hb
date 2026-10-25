"""Run preserved public examples in a networkless, read-only Blender container."""
import bpy,json,sys,traceback,random
from pathlib import Path
script,result,export=sys.argv[sys.argv.index('--')+1:]
sys.path.insert(0,str(Path(script).parent))
phase='script'
try:
    random.seed(0)
    exec(compile(Path(script).read_text(),script,'exec'),{'__name__':'__main__','__file__':script})
    bpy.context.view_layer.update()
    phase='export'
    bpy.ops.export_scene.gltf(filepath=export,export_format='GLB',export_cameras=True,export_lights=True,export_apply=True)
    data={'ok':True,'blender':bpy.app.version_string}
except BaseException as exc:
    data={'ok':False,'phase':phase,'error':type(exc).__name__+': '+str(exc),'traceback':traceback.format_exc(),'blender':bpy.app.version_string}
Path(result).write_text(json.dumps(data,indent=2)+'\n')
