"""Capture factory color-space linear matrices as numerical data, not implementation code."""
import bpy,json,sys
from mathutils import Color
from pathlib import Path
methods=('from_aces_to_scene_linear','from_scene_linear_to_aces','from_rec709_linear_to_scene_linear','from_scene_linear_to_rec709_linear','from_xyz_d65_to_scene_linear','from_scene_linear_to_xyz_d65')
matrices={name:list(map(list,zip(*(getattr(Color(tuple(int(i==j) for i in range(3))),name)() for j in range(3))))) for name in methods}
Path(sys.argv[sys.argv.index('--')+1]).write_text(json.dumps(dict(blender=bpy.app.version_string,working_space='Blender factory scene-linear configuration',matrices=matrices),indent=2,sort_keys=True)+'\n')
