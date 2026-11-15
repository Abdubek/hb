"""Coordinate-iterable dot products must drive real geometry through CLI/MCP."""
import unittest

import test_cli
import test_server


MODEL = '''import bpy
from mathutils import Vector
bpy.ops.mesh.primitive_cube_add(location=(1,2,3))
obj=bpy.context.object
assert obj.location.dot((0,0,1))==3
for vertex in obj.data.vertices:
    vertex.co.z=vertex.co.dot((0,0,2))
'''
CONTROL = MODEL.replace('.dot((0,0,1))', '.dot(Vector((0,0,1)))').replace(
    '.dot((0,0,2))', '.dot(Vector((0,0,2)))')


class VectorDot(unittest.TestCase):
    setUp = test_cli.CLI.setUp
    tearDown = test_cli.CLI.tearDown
    hb = test_cli.CLI.hb
    script = test_cli.CLI.script
    exchange = test_server.Server.exchange

    def test_iterable_dot_and_views_match_vector_control_export(self):
        self.hb('check', self.script(MODEL))
        self.hb('run', self.script(MODEL), '--out', 'dots.glb')
        self.hb('run', self.script(CONTROL), '--scene', 'control.hb', '--out', 'control.glb')
        actual = test_cli.revision(self.path / 'scene.hb')['scene']
        self.assertEqual(actual, test_cli.revision(self.path / 'control.hb')['scene'])
        self.assertEqual(sorted({v[2] for v in actual['meshes'][0]['vertices']}), [-2, 2])
        self.assertEqual((self.path / 'dots.glb').read_bytes(),
                         (self.path / 'control.glb').read_bytes())

    def test_argument_errors_and_matmul_contract(self):
        self.hb('run', self.script('''from mathutils import Vector
v=Vector((1,2,3))
for other in (None, 2, '456', [1,'bad',3], [1,2,3,'bad'], [[1],[2],[3]]):
    try:v.dot(other)
    except TypeError:pass
    else:raise AssertionError('Nonnumeric dot input accepted')
for other in ((), (1,), [1,2], iter((1,2)), Vector((1,2))):
    try:v.dot(other)
    except ValueError:pass
    else:raise AssertionError('Short dot input accepted')
for operation in (lambda:v.dot(), lambda:v.dot(v,v), lambda:v.dot(other=v),
                  lambda:v@(1,2,3)):
    try:operation()
    except TypeError:pass
    else:raise AssertionError('Invalid arguments accepted')
try:v@Vector((1,2,3,4))
except ValueError:pass
else:raise AssertionError('Mismatched matmul dimensions accepted')
assert v.dot((x for x in (4,5,6,99)))==32
assert tuple(v)==(1,2,3)
'''))

    def test_failed_dot_restores_scene_and_history(self):
        self.hb('run', self.script(CONTROL))
        before = (self.path / 'scene.hb').read_bytes()
        history = set((self.path / 'scene.hb.revisions').iterdir())
        for other in ('(1,2)', '[1,2,3,"bad"]', 'other=Vector((1,2,3))'):
            with self.subTest(other=other):
                result = self.hb('run', self.script('import bpy\nfrom mathutils import Vector\n'
                    'bpy.context.object.location.x=9\nVector((1,2,3)).dot(' + other + ')'), ok=False)
                self.assertEqual(result['error']['code'], 'SCRIPT_ERROR')
                self.assertEqual((self.path / 'scene.hb').read_bytes(), before)
                self.assertEqual(set((self.path / 'scene.hb.revisions').iterdir()), history)
                self.assertFalse((self.path / 'scene.hb.lock').exists())

    def test_mcp_runs_iterable_dot_and_continues_after_error(self):
        replies = self.exchange('--mcp', [
            test_server.request(0, 'initialize', {'protocolVersion': '2025-11-25',
                                                 'clientInfo': {}, 'capabilities': {}}),
            {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
            test_server.request(1, 'tools/call', {'name': 'hb_run', 'arguments': {
                'code': MODEL, 'args': ['--out', 'mcp.glb']}}),
            test_server.request(2, 'tools/call', {'name': 'hb_run', 'arguments': {
                'code': 'import bpy\nbpy.context.object.location.x=9\n'
                        'bpy.context.object.location.dot((1,2))'}}),
            test_server.request(3, 'tools/call', {'name': 'hb_query',
                                                'arguments': {'args': ['stats']}}),
        ], self.path)
        self.assertFalse(replies[1]['result']['isError'], replies[1])
        self.assertTrue(replies[2]['result']['isError'])
        self.assertEqual(replies[2]['result']['structuredContent']['error']['code'], 'SCRIPT_ERROR')
        self.assertEqual(replies[3]['result']['structuredContent']['result']['objects'], 1)
        self.assertEqual(replies[3]['result']['structuredContent']['revision'],
                         replies[1]['result']['structuredContent']['revision'])
        self.assertEqual((self.path / 'mcp.glb').read_bytes()[:4], b'glTF')
