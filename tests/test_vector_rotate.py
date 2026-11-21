"""In-place rotations must affect real coordinate views and exported geometry."""
import unittest

import test_cli
import test_server


MODEL = '''import bpy,math
from mathutils import Vector,Euler,Matrix,Quaternion
direction=Vector((0,0,1))
direction.rotate(Euler((math.pi/2,0,0)))
bpy.ops.mesh.primitive_cube_add(location=direction)
obj=bpy.context.object
matrix=Matrix(((0,-1,0),(1,0,0),(0,0,1)))
obj.location.rotate(matrix)
rotation=Quaternion((0,2,0,0))
for vertex in obj.data.vertices:
    vertex.co.rotate(rotation)
    vertex.co.rotate(matrix)
'''
CONTROL = '''import bpy,math
from mathutils import Vector,Euler,Matrix,Quaternion
direction=Euler((math.pi/2,0,0)).to_matrix()@Vector((0,0,1))
bpy.ops.mesh.primitive_cube_add(location=direction)
obj=bpy.context.object
matrix=Matrix(((0,-1,0),(1,0,0),(0,0,1)))
obj.location=matrix@obj.location
rotation=Quaternion((0,2,0,0)).normalized().to_matrix()
for vertex in obj.data.vertices:
    vertex.co=matrix@(rotation@vertex.co)
'''


class VectorRotate(unittest.TestCase):
    setUp = test_cli.CLI.setUp
    tearDown = test_cli.CLI.tearDown
    hb = test_cli.CLI.hb
    script = test_cli.CLI.script
    exchange = test_server.Server.exchange

    def test_rotating_coordinates_matches_control_scene_and_export(self):
        self.hb('check', self.script(MODEL))
        self.hb('run', self.script(MODEL), '--out', 'rotated.glb')
        self.hb('run', self.script(CONTROL), '--scene', 'control.hb', '--out', 'control.glb')
        actual = test_cli.revision(self.path / 'scene.hb')['scene']
        self.assertEqual(actual, test_cli.revision(self.path / 'control.hb')['scene'])
        self.assertEqual(actual['objects'][0]['location'][:2], [1, 0])
        self.assertEqual((self.path / 'rotated.glb').read_bytes(),
                         (self.path / 'control.glb').read_bytes())

    def test_live_uv_matrix_rows_and_same_storage_rotation(self):
        source = self.script('''import bpy
from mathutils import Matrix,Quaternion,Vector
matrix=Matrix(((0,-2,0),(3,0,0),(0,0,4)))
row=matrix[0]
assert row.rotate(matrix) is None
assert tuple(row)==(2,0,0)
assert tuple(matrix[0])==(2,0,0)
m=Matrix(((0,-1),(1,0)))
bpy.ops.mesh.primitive_cube_add()
uv=bpy.context.object.data.uv_layers.active.data[0].uv
uv[:]=(.25,.5)
assert uv.rotate(m) is None
assert tuple(uv)==(-.5,.25)
row=Matrix(((1,0,0,7),(0,1,0,0),(0,0,1,0),(0,0,0,1)))[0]
assert row.rotate(Quaternion((0,0,0,2))) is None
assert tuple(row)==(-1,0,0,7)
v=Vector((1,2,3,1e20))
v.rotate(Matrix.Translation((5,6,7)))
assert tuple(v)[:3]==(1,2,3) and v.w>1e19
''')
        self.hb('check', source)
        self.hb('run', source)

    def test_invalid_rotations_leave_values_and_saved_revision_unchanged(self):
        self.hb('run', self.script('''from mathutils import Vector,Matrix,Euler,Quaternion
for dimensions,rotation,error in (
        (2,Euler(),TypeError),(2,Quaternion(),TypeError),
        (2,Matrix.Identity(3),ValueError),(3,Matrix.Identity(2),ValueError),
        (3,Matrix(((1,0,0),(0,1,0))),ValueError),(4,None,TypeError),
        (3,(1,2,3),TypeError),(3,[[1,0,0],[0,1,0],[0,0,1]],TypeError)):
    vector=Vector(range(dimensions));before=tuple(vector)
    try:vector.rotate(rotation)
    except error:pass
    else:raise AssertionError('Invalid rotation accepted')
    assert tuple(vector)==before
v=Vector((1,2,3))
for call in (lambda:v.rotate(),lambda:v.rotate(Euler(),Euler()),
             lambda:v.rotate(other=Euler())):
    try:call()
    except TypeError:pass
    else:raise AssertionError('Invalid call accepted')
for rotation in (Matrix.Diagonal((1e7,1,1)),Quaternion((1e7,0,0,0)),Euler((1e7,0,0))):
    try:v.rotate(rotation)
    except Exception as error:assert 'finite' in str(error) and '1e6' in str(error)
    else:raise AssertionError('Unverified rotation range accepted')
    assert tuple(v)==(1,2,3)
for component in (float('nan'),float('inf'),1e7):
    v=Vector((component,1,2));before=[x.hex() for x in v]
    try:v.rotate(Matrix.Identity(3))
    except Exception as error:assert 'finite' in str(error)
    else:raise AssertionError('Unverified vector range accepted')
    assert [x.hex() for x in v]==before
'''))
        self.hb('run', self.script(CONTROL))
        before = (self.path / 'scene.hb').read_bytes()
        history = set((self.path / 'scene.hb.revisions').iterdir())
        result = self.hb('run', self.script('import bpy\nfrom mathutils import Matrix\n'
            'bpy.context.object.location.x=9\nbpy.context.object.location.rotate(Matrix.Identity(2))'), ok=False)
        self.assertEqual(result['error']['code'], 'SCRIPT_ERROR')
        self.assertEqual((self.path / 'scene.hb').read_bytes(), before)
        self.assertEqual(set((self.path / 'scene.hb.revisions').iterdir()), history)
        self.assertFalse((self.path / 'scene.hb.lock').exists())

    def test_mcp_rotates_geometry_and_recovers_after_dimension_error(self):
        replies = self.exchange('--mcp', [
            test_server.request(0, 'initialize', {'protocolVersion': '2025-11-25',
                                                 'clientInfo': {}, 'capabilities': {}}),
            {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
            test_server.request(1, 'tools/call', {'name': 'hb_run', 'arguments': {
                'code': MODEL, 'args': ['--out', 'mcp.glb']}}),
            test_server.request(2, 'tools/call', {'name': 'hb_run', 'arguments': {
                'code': 'import bpy\nfrom mathutils import Matrix\n'
                        'bpy.context.object.location.x=9\n'
                        'bpy.context.object.location.rotate(Matrix.Identity(2))'}}),
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
