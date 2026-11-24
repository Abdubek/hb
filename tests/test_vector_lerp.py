"""Coordinate iterable interpolation must drive real geometry via CLI and MCP."""
import unittest

import test_cli
import test_server


MODEL = '''import bpy
from mathutils import Vector
location=Vector((0,0,0)).lerp((2,4,6),.5)
bpy.ops.mesh.primitive_cube_add(location=location)
for vertex in bpy.context.object.data.vertices:
    vertex.co=vertex.co.lerp([0,0,0],.5)
'''
CONTROL = '''import bpy
bpy.ops.mesh.primitive_cube_add(location=(1,2,3))
for vertex in bpy.context.object.data.vertices:
    vertex.co*=.5
'''


class VectorLerp(unittest.TestCase):
    setUp = test_cli.CLI.setUp
    tearDown = test_cli.CLI.tearDown
    hb = test_cli.CLI.hb
    script = test_cli.CLI.script
    exchange = test_server.Server.exchange

    def test_iterable_interpolation_matches_control_scene_and_export(self):
        self.hb('check', self.script(MODEL))
        self.hb('run', self.script(MODEL), '--out', 'lerp.glb')
        self.hb('run', self.script(CONTROL), '--scene', 'control.hb', '--out', 'control.glb')
        actual = test_cli.revision(self.path / 'scene.hb')['scene']
        self.assertEqual(actual, test_cli.revision(self.path / 'control.hb')['scene'])
        self.assertEqual(actual['objects'][0]['location'], [1, 2, 3])
        self.assertEqual(sorted({v[2] for v in actual['meshes'][0]['vertices']}), [-.5, .5])
        self.assertEqual((self.path / 'lerp.glb').read_bytes(),
                         (self.path / 'control.glb').read_bytes())

    def test_live_views_return_independent_values_and_preserve_inputs(self):
        source = self.script('''import bpy
from mathutils import Matrix,Vector
bpy.ops.mesh.primitive_cube_add(location=(1,2,3))
view=bpy.context.object.location
result=view.lerp((3,4,5,99),.5)
assert type(result) is Vector and tuple(result)==(2,3,4)
result.x=9
assert tuple(view)==(1,2,3)
uv=bpy.context.object.data.uv_layers.active.data[0].uv
uv[:]=(.25,.5)
result=uv.lerp([.75,1,99],.5)
assert tuple(result)==(.5,.75) and tuple(uv)==(.25,.5)
matrix=Matrix(((1,2,3),(4,5,6),(7,8,9)))
result=matrix[0].lerp(iter((3,4,5)),.5)
assert tuple(result)==(2,3,4) and tuple(matrix[0])==(1,2,3)
values=[4,5,6,99]
assert tuple(Vector((1,2,3)).lerp(values,-.5))==(-.5,.5,1.5)
assert values==[4,5,6,99]
class Factor:
    def __float__(self):return .5
assert tuple(view.lerp((3,4,5),Factor()))==(2,3,4)
assert tuple(view.lerp((3,4,5),True))==(3,4,5)
''')
        self.hb('check', source)
        self.hb('run', source)

    def test_invalid_inputs_preserve_values_revision_and_history(self):
        self.hb('run', self.script('''from mathutils import Vector
v=Vector((1,2,3))
for other,error in ((None,TypeError),(3,TypeError),('456',TypeError),
                    ([1,'2',3],TypeError),([1,2,3,'bad'],TypeError),
                    ([],ValueError),((1,2),ValueError),(Vector((1,2)),ValueError)):
    try:v.lerp(other,.5)
    except error:pass
    else:raise AssertionError('Invalid endpoint accepted')
    assert tuple(v)==(1,2,3)
for factor in (None,'0.5',[]):
    try:v.lerp(Vector((4,5,6)),factor)
    except TypeError:pass
    else:raise AssertionError('Invalid factor accepted')
for call in (lambda:v.lerp(),lambda:v.lerp(v),lambda:v.lerp(v,.5,0),
             lambda:v.lerp(other=v,factor=.5),lambda:v.lerp(v,factor=.5)):
    try:call()
    except TypeError:pass
    else:raise AssertionError('Invalid call accepted')
assert tuple(v)==(1,2,3)
'''))
        self.hb('run', self.script(CONTROL))
        before = (self.path / 'scene.hb').read_bytes()
        history = set((self.path / 'scene.hb.revisions').iterdir())
        for arguments in ('(1,2),.5', '[1,2,3,"bad"],.5', 'Vector((1,2,3)),"0.5"'):
            with self.subTest(arguments=arguments):
                result = self.hb('run', self.script('import bpy\nfrom mathutils import Vector\n'
                    'bpy.context.object.location.x=9\n'
                    'bpy.context.object.location.lerp(' + arguments + ')'), ok=False)
                self.assertEqual(result['error']['code'], 'SCRIPT_ERROR')
                self.assertEqual((self.path / 'scene.hb').read_bytes(), before)
                self.assertEqual(set((self.path / 'scene.hb.revisions').iterdir()), history)
                self.assertFalse((self.path / 'scene.hb.lock').exists())

    def test_mcp_runs_iterable_interpolation_and_rolls_back_invalid_endpoint(self):
        replies = self.exchange('--mcp', [
            test_server.request(0, 'initialize', {'protocolVersion': '2025-11-25',
                                                 'clientInfo': {}, 'capabilities': {}}),
            {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
            test_server.request(1, 'tools/call', {'name': 'hb_run', 'arguments': {
                'code': MODEL, 'args': ['--out', 'mcp.glb']}}),
            test_server.request(2, 'tools/call', {'name': 'hb_run', 'arguments': {
                'code': 'import bpy\nbpy.context.object.location.x=9\n'
                        'bpy.context.object.location.lerp((1,2),.5)'}}),
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
