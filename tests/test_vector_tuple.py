"""Vector tuple snapshots must work in actual coordinate/geometry workflows."""
import unittest

import test_cli
import test_server


# Reduced from the track endpoint workflow in corpus/claude-140.py:492-493.
MODEL = '''import bpy
from mathutils import Vector
a=Vector((0,0,0));b=Vector((2,0,0))
ext=(b-a).normalized()*.5
start=(a-ext).to_tuple()[:2]+(0.,)
end=(b+ext).to_tuple()[:2]+(0.,)
def midpoint(start,end):return Vector(start).lerp(Vector(end),.5)
bpy.ops.mesh.primitive_cube_add(location=midpoint(start,end))
obj=bpy.context.object
obj.scale=((end[0]-start[0])/2,.125,.125)
assert obj.location.to_tuple()==(1.,0.,0.)
'''
CONTROL = '''import bpy
bpy.ops.mesh.primitive_cube_add(location=(1,0,0))
bpy.context.object.scale=(1.5,.125,.125)
'''


class VectorTuple(unittest.TestCase):
    setUp = test_cli.CLI.setUp
    tearDown = test_cli.CLI.tearDown
    hb = test_cli.CLI.hb
    script = test_cli.CLI.script
    exchange = test_server.Server.exchange

    def test_live_views_produce_independent_snapshots(self):
        self.hb('run', self.script('''import bpy
from mathutils import Matrix,Vector
bpy.ops.mesh.primitive_cube_add(location=(1.25,-1.25,2.5))
obj=bpy.context.object
view=obj.location
snapshot=view.to_tuple(1)
assert snapshot==(1.2,-1.2,2.5)
assert view.to_tuple()==(1.25,-1.25,2.5)
view.x=9
assert snapshot==(1.2,-1.2,2.5)
assert view.to_tuple()==(9.,-1.25,2.5)
vertex=obj.data.vertices[0].co
coordinates=vertex.to_tuple()
vertex.x+=1
assert vertex.to_tuple()[0]==coordinates[0]+1
assert coordinates[0]!=vertex.x
uv=obj.data.uv_layers.active.data[0].uv
before=uv.to_tuple()
uv.x+=.25
assert uv.to_tuple()[0]==before[0]+.25
m=Matrix(((1.25,-1.25),(2.5,-2.5)))
row=m[0];before=row.to_tuple(1)
assert before==(1.2,-1.2)
m[0][0]=7
assert before==(1.2,-1.2) and row.to_tuple()==(7.,-1.25)
'''))

    def test_tuple_model_and_checker_match_explicit_control(self):
        self.hb('check', self.script(MODEL))
        self.hb('run', self.script(MODEL), '--out', 'tuples.glb')
        self.hb('run', self.script(CONTROL), '--scene', 'control.hb', '--out', 'control.glb')
        actual = test_cli.revision(self.path / 'scene.hb')['scene']
        self.assertEqual(actual, test_cli.revision(self.path / 'control.hb')['scene'])
        self.assertEqual(actual['objects'][0]['location'], [1, 0, 0])
        self.assertEqual((self.path / 'tuples.glb').read_bytes(),
                         (self.path / 'control.glb').read_bytes())
        self.hb('check', self.script('''from mathutils import Vector
def direction(point=Vector((1,2,3)).to_tuple()):return Vector(point).normalized()
assert direction().length>0
'''))
        errors = self.hb('check', self.script('''import bpy
from mathutils import Vector
values=(Vector((1,2,3)).to_tuple(),bpy.context.object)
values[1].unsupported_magic()
'''), ok=False)['errors']
        self.assertTrue(any('bpy.types.Object.unsupported_magic' in e['message'] for e in errors))

    def test_precision_errors_and_failed_run_preserve_scene(self):
        self.hb('run', self.script('''from mathutils import Vector
class Precision:
    def __index__(self):return 1
v=Vector((1.25,-1.25))
assert v.to_tuple(Precision())==(1.2,-1.2)
assert v.to_tuple(True)==(1.2,-1.2)
assert v.to_tuple(False)==(1.,-1.)
for precision,error in ((None,TypeError),(1.,TypeError),('1',TypeError),
                        (-2,ValueError),(23,ValueError),
                        (-2147483648,ValueError),(2147483647,ValueError),
                        (-2147483649,OverflowError),(2147483648,OverflowError)):
    try:v.to_tuple(precision)
    except error:pass
    else:raise AssertionError('Invalid precision accepted')
for call in (lambda:v.to_tuple(precision=1),lambda:v.to_tuple(1,2)):
    try:call()
    except TypeError:pass
    else:raise AssertionError('Invalid arguments accepted')
assert v.to_tuple()==(1.25,-1.25)
'''))
        self.hb('run', self.script(CONTROL))
        before = (self.path / 'scene.hb').read_bytes()
        history = set((self.path / 'scene.hb.revisions').iterdir())
        result = self.hb('run', self.script('import bpy\n'
            'bpy.context.object.location.x=9\nbpy.context.object.location.to_tuple(23)'), ok=False)
        self.assertEqual(result['error']['code'], 'SCRIPT_ERROR')
        self.assertEqual((self.path / 'scene.hb').read_bytes(), before)
        self.assertEqual(set((self.path / 'scene.hb.revisions').iterdir()), history)
        self.assertFalse((self.path / 'scene.hb.lock').exists())

    def test_mcp_runs_tuple_model_and_recovers_after_precision_error(self):
        replies = self.exchange('--mcp', [
            test_server.request(0, 'initialize', {'protocolVersion': '2025-11-25',
                                                 'clientInfo': {}, 'capabilities': {}}),
            {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
            test_server.request(1, 'tools/call', {'name': 'hb_run', 'arguments': {
                'code': MODEL, 'args': ['--out', 'mcp.glb']}}),
            test_server.request(2, 'tools/call', {'name': 'hb_run', 'arguments': {
                'code': 'import bpy\nbpy.context.object.location.x=9\n'
                        'bpy.context.object.location.to_tuple(23)'}}),
            test_server.request(3, 'tools/call', {'name': 'hb_query',
                                                'arguments': {'args': ['stats']}}),
        ], self.path)
        self.assertFalse(replies[1]['result']['isError'], replies[1])
        self.assertTrue(replies[2]['result']['isError'])
        self.assertEqual(replies[2]['result']['structuredContent']['error']['code'], 'SCRIPT_ERROR')
        self.assertEqual(replies[3]['result']['structuredContent']['revision'],
                         replies[1]['result']['structuredContent']['revision'])
        self.hb('run', self.script(CONTROL), '--scene', 'control.hb', '--out', 'control.glb')
        self.assertEqual(test_cli.revision(self.path / 'scene.hb')['scene'],
                         test_cli.revision(self.path / 'control.hb')['scene'])
        self.assertEqual((self.path / 'mcp.glb').read_bytes(),
                         (self.path / 'control.glb').read_bytes())
