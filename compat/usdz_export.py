"""Blender-only USDZ export oracle, using the normal fixture reset."""
import sys
from pathlib import Path
fixture, output = sys.argv[sys.argv.index('--') + 1:]
runner = Path(__file__).with_name('run_blender.py')
sys.argv = ['blender', '--', fixture, output + '.json']
exec(runner.read_text(), {'__file__': str(runner)})
import bpy
assert bpy.ops.wm.usd_export(filepath=output, export_materials=True, export_textures=True,
                             export_normals=True, export_uvmaps=True,
                             export_cameras=True, export_lights=True) == {'FINISHED'}
