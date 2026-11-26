"""Signed 2D UV areas and 3D normals must affect real exported geometry."""
import unittest

import test_cli
import test_server


PRELUDE = '''import bpy
from mathutils import Vector
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object
uv=obj.data.uv_layers.active.data
uv[0].uv[:]=(0,0)
uv[1].uv[:]=(2,0)
uv[2].uv[:]=(0,3)
'''
MODEL = PRELUDE + '''area=(uv[1].uv-uv[0].uv).cross(uv[2].uv-uv[0].uv)
assert type(area) is float and area==6
assert (uv[2].uv-uv[0].uv).cross(uv[1].uv-uv[0].uv)==-6
normal=Vector((1,0,0)).cross(iter((0,1,0)))
obj.location=normal*(abs(area)/2)
for vertex in obj.data.vertices:
    vertex.co.z*=abs(area)/2
'''
CONTROL = PRELUDE + '''obj.location=(0,0,3)
for vertex in obj.data.vertices:
    vertex.co.z*=3
'''


class VectorCross(unittest.TestCase):
    setUp = test_cli.CLI.setUp
    tearDown = test_cli.CLI.tearDown
    hb = test_cli.CLI.hb
    script = test_cli.CLI.script
    exchange = test_server.Server.exchange

    def test_uv_signed_area_and_iterator_normal_match_control_scene_and_export(self):
        self.hb('check', self.script(MODEL))
        self.hb('run', self.script(MODEL), '--out', 'cross.glb')
        self.hb('run', self.script(CONTROL), '--scene', 'control.hb', '--out', 'control.glb')
        actual = test_cli.revision(self.path / 'scene.hb')['scene']
        self.assertEqual(actual, test_cli.revision(self.path / 'control.hb')['scene'])
        self.assertEqual(actual['objects'][0]['location'], [0, 0, 3])
        self.assertEqual(sorted({v[2] for v in actual['meshes'][0]['vertices']}), [-3, 3])
        self.assertEqual((self.path / 'cross.glb').read_bytes(),
                         (self.path / 'control.glb').read_bytes())

    def test_float_result_and_independent_vector_results_on_live_views(self):
        self.hb('run', self.script('''import bpy
from mathutils import Matrix,Vector
bpy.ops.mesh.primitive_cube_add(location=(1,2,3))
location=bpy.context.object.location
result=location.cross([3,4,5])
assert type(result) is Vector and tuple(result)==(-2,4,-2)
result.x=99
assert tuple(location)==(1,2,3)
uv=bpy.context.object.data.uv_layers.active.data[0].uv
uv[:]=(1,2)
result=uv.cross((3,4))
assert type(result) is float and result==-2 and tuple(uv)==(1,2)
row=Matrix(((1,2),(3,4)))[0]
assert row.cross(iter((3,4)))==-2 and tuple(row)==(1,2)
other=Vector((3,4,5))
result=location.cross(other)
assert result is not location and result is not other
assert tuple(other)==(3,4,5)
assert Vector((1.1,2.2)).cross([2.2,4.4])==0
'''))
        # Preserve preflight validation on 3D Vector-valued cross results.
        errors = self.hb('check', self.script('from mathutils import Vector\n'
            'Vector((1,0,0)).cross((0,1,0)).freeze()'), ok=False)['errors']
        self.assertTrue(any('mathutils.Vector.freeze' in e['message'] for e in errors), errors)

    def test_errors_preserve_values_saved_scene_and_history(self):
        self.hb('run', self.script('''from mathutils import Vector
for size in (2,3):
    vector=Vector(range(size));before=tuple(vector)
    for other,error in ((None,TypeError),(3,TypeError),('12' if size==2 else '123',TypeError),
                        ([1]*(size-1)+['2'],TypeError),([],ValueError),
                        ([1]*(size-1),ValueError),([1]*(size+1),ValueError)):
        try:vector.cross(other)
        except error:pass
        else:raise AssertionError('Invalid cross operand accepted')
        assert tuple(vector)==before
    for call in (lambda:vector.cross(),lambda:vector.cross(vector,vector),
                 lambda:vector.cross(other=vector)):
        try:call()
        except TypeError:pass
        else:raise AssertionError('Invalid call accepted')
values=iter((1,2,3))
try:Vector((1,2,3,4)).cross(values)
except ValueError:pass
else:raise AssertionError('4D cross accepted')
assert list(values)==[1,2,3]
'''))
        self.hb('run', self.script(CONTROL))
        before = (self.path / 'scene.hb').read_bytes()
        history = set((self.path / 'scene.hb.revisions').iterdir())
        result = self.hb('run', self.script('import bpy\nbpy.context.object.location.x=9\n'
            'bpy.context.object.location.cross((1,2))'), ok=False)
        self.assertEqual(result['error']['code'], 'SCRIPT_ERROR')
        self.assertEqual((self.path / 'scene.hb').read_bytes(), before)
        self.assertEqual(set((self.path / 'scene.hb.revisions').iterdir()), history)
        self.assertFalse((self.path / 'scene.hb.lock').exists())

    def test_mcp_executes_area_geometry_and_continues_after_invalid_cross(self):
        replies = self.exchange('--mcp', [
            test_server.request(0, 'initialize', {'protocolVersion': '2025-11-25',
                                                 'clientInfo': {}, 'capabilities': {}}),
            {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
            test_server.request(1, 'tools/call', {'name': 'hb_run', 'arguments': {
                'code': MODEL, 'args': ['--out', 'mcp.glb']}}),
            test_server.request(2, 'tools/call', {'name': 'hb_run', 'arguments': {
                'code': 'import bpy\nbpy.context.object.location.x=9\n'
                        'bpy.context.object.location.cross((1,2))'}}),
            test_server.request(3, 'tools/call', {'name': 'hb_query',
                                                'arguments': {'args': ['stats']}}),
        ], self.path)
        self.assertFalse(replies[1]['result']['isError'], replies[1])
        self.assertTrue(replies[2]['result']['isError'])
        self.assertEqual(replies[2]['result']['structuredContent']['error']['code'], 'SCRIPT_ERROR')
        self.assertEqual(replies[3]['result']['structuredContent']['result']['objects'], 1)
        self.assertEqual(replies[3]['result']['structuredContent']['revision'],
                         replies[1]['result']['structuredContent']['revision'])
        self.hb('run', self.script(CONTROL), '--scene', 'control.hb', '--out', 'control.glb')
        self.assertEqual(test_cli.revision(self.path / 'scene.hb')['scene'],
                         test_cli.revision(self.path / 'control.hb')['scene'])
        self.assertEqual((self.path / 'mcp.glb').read_bytes(),
                         (self.path / 'control.glb').read_bytes())
