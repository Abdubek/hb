import json,unittest
import test_cli
from normalize import revision
from triangulate_check import compare

class Triangulate(unittest.TestCase):
    setUp=test_cli.CLI.setUp;tearDown=test_cli.CLI.tearDown;hb=test_cli.CLI.hb;script=test_cli.CLI.script
    def test_blender_topology_uv_and_custom_normals(self):
        self.hb('run',test_cli.ROOT/'compat/triangulate_probe.py')
        compare(json.loads((test_cli.ROOT/'compat/fixtures/triangulate-reference.json').read_text()),revision(self.path/'scene.hb')['scene'])

    def test_invalid_normals_are_atomic_and_smooth_reinterpret_is_explicit(self):
        self.hb('run',self.script('''import bpy
bpy.ops.mesh.primitive_plane_add()
data=bpy.context.object.data
for values in ([(0,0,1)]*3,[(0,0,1)]*3+[(0,0,0)],[(0,0,1)]*3+[(float('inf'),0,0)]):
 try:data.normals_split_custom_set(values)
 except ValueError:pass
 else:raise AssertionError('Invalid custom normals accepted')
 assert not data.has_custom_normals
data.normals_split_custom_set([(0,0,1)]*4)
data.polygons[0].use_smooth=True
modifier=bpy.context.object.modifiers.new('Triangles','TRIANGULATE')
try:bpy.ops.object.modifier_apply(modifier=modifier.name)
except Exception as error:assert 'keep_custom_normals=True' in str(error)
else:raise AssertionError('Smooth normal reinterpretation accepted')
assert len(data.polygons)==1 and len(bpy.context.object.modifiers)==1
modifier.keep_custom_normals=True
bpy.ops.object.modifier_apply(modifier=modifier.name)
assert len(bpy.context.object.data.polygons)==2 and bpy.context.object.data.has_custom_normals
'''))

if __name__=='__main__':unittest.main()
