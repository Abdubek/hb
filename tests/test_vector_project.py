"""Coordinate-iterable projection must drive real geometry and preserve views."""
import unittest

import test_cli
import test_server


PRELUDE = '''import bpy
from mathutils import Vector
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object
'''
MODEL = PRELUDE + '''obj.location=Vector((2,4,7)).project(iter((0,0,2,99)))
for vertex in obj.data.vertices:
    vertex.co-=vertex.co.project((1,1,0))*.5
'''
CONTROL = PRELUDE + '''obj.location=(0,0,7)
for vertex in obj.data.vertices:
    x,y,z=vertex.co
    vertex.co=(.75*x-.25*y,.75*y-.25*x,z)
'''


class VectorProject(unittest.TestCase):
    setUp = test_cli.CLI.setUp
    tearDown = test_cli.CLI.tearDown
    hb = test_cli.CLI.hb
    script = test_cli.CLI.script
    exchange = test_server.Server.exchange

    def test_oblique_compression_matches_direct_scene_and_glb(self):
        self.hb('check', self.script(MODEL))
        self.hb('run', self.script(MODEL), '--out', 'project.glb')
        self.hb('run', self.script(CONTROL), '--scene', 'control.hb', '--out', 'control.glb')
        actual = test_cli.revision(self.path / 'scene.hb')['scene']
        self.assertEqual(actual, test_cli.revision(self.path / 'control.hb')['scene'])
        self.assertEqual(actual['objects'][0]['location'], [0, 0, 7])
        self.assertEqual(sorted({v[0]+v[1] for v in actual['meshes'][0]['vertices']}), [-1, 0, 1])
        self.assertEqual((self.path / 'project.glb').read_bytes(),
                         (self.path / 'control.glb').read_bytes())

    def test_independent_results_and_nonmutating_coordinate_uv_matrix_views(self):
        self.hb('run', self.script('''import bpy
from mathutils import Matrix,Vector
bpy.ops.mesh.primitive_cube_add(location=(1,2,3))
location=bpy.context.object.location
axis=Vector((0,0,2,99))
result=location.project(axis)
assert type(result) is Vector and tuple(result)==(0,0,3) and len(result)==3
assert result is not location and result is not axis
result.z=99
assert tuple(location)==(1,2,3) and tuple(axis)==(0,0,2,99)
uv=bpy.context.object.data.uv_layers.active.data[0].uv
uv[:]=(2,4)
assert tuple(uv.project(iter((0,2,99))))==(0,4) and tuple(uv)==(2,4)
row=Matrix(((2,4),(6,8)))[0]
assert tuple(row.project([2,0]))==(2,0) and tuple(row)==(2,4)
assert tuple(Vector((2,4,6,8)).project((0,0,0,2)))==(0,0,0,8)
'''))
        errors = self.hb('check', self.script('from mathutils import Vector\n'
            'Vector((1,2,3)).project((1,0,0)).freeze()'), ok=False)['errors']
        self.assertTrue(any('mathutils.Vector.freeze' in e['message'] for e in errors), errors)

    def test_zero_axes_and_errors_preserve_values_history_and_scene(self):
        self.hb('run', self.script('''import math
from mathutils import Vector
for size in (2,3,4):
    vector=Vector(range(1,size+1));before=tuple(vector)
    assert all(math.isnan(x) for x in vector.project([0]*size))
    assert all(math.isinf(x) and x>0 for x in vector.project([1e-30]*size))
    assert all(math.isinf(x) and x<0 for x in (-vector).project([1e-30]*size))
    mixed=vector.project([1e-30]+[0]*(size-1))
    assert math.isinf(mixed[0]) and all(math.isnan(x) for x in mixed[1:])
    for other,error in ((None,TypeError),(3,TypeError),('1234',TypeError),
                        ([1]*(size-1)+['2'],TypeError),([1]*size+['bad'],TypeError),
                        ([],ValueError),([1]*(size-1),ValueError)):
        try:vector.project(other)
        except error:pass
        else:raise AssertionError('Invalid projection axis accepted')
        assert tuple(vector)==before
    for call in (lambda:vector.project(),lambda:vector.project(vector,vector),
                 lambda:vector.project(other=vector)):
        try:call()
        except TypeError:pass
        else:raise AssertionError('Invalid call accepted')
'''))
        self.hb('run', self.script(CONTROL))
        before = (self.path / 'scene.hb').read_bytes()
        history = set((self.path / 'scene.hb.revisions').iterdir())
        for code in ('bpy.context.object.location.project((1,2))',
                     'bpy.context.object.location=bpy.context.object.location.project((0,0,0))'):
            result = self.hb('run', self.script('import bpy\nbpy.context.object.location.x=9\n'+code), ok=False)
            self.assertEqual(result['error']['code'], 'SCRIPT_ERROR')
            self.assertEqual((self.path / 'scene.hb').read_bytes(), before)
            self.assertEqual(set((self.path / 'scene.hb.revisions').iterdir()), history)
            self.assertFalse((self.path / 'scene.hb.lock').exists())

    def test_mcp_executes_projection_and_recovers_from_invalid_axis(self):
        replies = self.exchange('--mcp', [
            test_server.request(0, 'initialize', {'protocolVersion': '2025-11-25',
                                                 'clientInfo': {}, 'capabilities': {}}),
            {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
            test_server.request(1, 'tools/call', {'name': 'hb_run', 'arguments': {
                'code': MODEL, 'args': ['--out', 'mcp.glb']}}),
            test_server.request(2, 'tools/call', {'name': 'hb_run', 'arguments': {
                'code': 'import bpy\nbpy.context.object.location.x=9\n'
                        'bpy.context.object.location.project((1,2))'}}),
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
