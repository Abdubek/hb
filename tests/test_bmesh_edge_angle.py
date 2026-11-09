"""Edge angles must drive real geometry and preserve fallback API provenance."""
import unittest

import test_cli
import test_server


class BMeshEdgeAngle(unittest.TestCase):
    setUp = test_cli.CLI.setUp
    tearDown = test_cli.CLI.tearDown
    hb = test_cli.CLI.hb
    script = test_cli.CLI.script
    exchange = test_server.Server.exchange

    def test_reference_and_angle_selected_mesh_export(self):
        fixture = test_cli.ROOT / 'compat/golden/m3_bmesh_edge_angle.py'
        self.hb('check', fixture)
        self.hb('run', fixture, '--out', 'angles.glb')
        self.hb('run', self.script('''import bpy
mesh=bpy.data.meshes.new('Angles')
mesh.from_pydata([(0,0,0),(1,0,2),(0,1,0),(1,1,2),(1,1,1)],[],
                 [(0,1,2),(1,3,2),(1,4,3)])
obj=bpy.data.objects.new('Angles',mesh)
bpy.context.collection.objects.link(obj)
'''), '--scene', 'control.hb', '--out', 'control.glb')
        self.assertEqual((self.path / 'angles.glb').read_bytes(),
                         (self.path / 'control.glb').read_bytes())

    def test_checker_parameters_fallback_provenance_and_rollback(self):
        setup = '''import bpy,bmesh
bm=bmesh.new()
a=bm.verts.new((0,0,0));b=bm.verts.new((1,0,0))
edge=bm.edges.new((a,b))
'''
        for expression, expected in (
            ('edge.calc_face_angle(0,1)', 'bmesh.types.BMEdge.calc_face_angle'),
            ('edge.calc_face_angle(fallback=0)', 'bmesh.types.BMEdge.calc_face_angle'),
            ('edge.calc_face_angle_signed()', 'bmesh.types.BMEdge.calc_face_angle_signed'),
            ('edge.smooth=False', 'bmesh.types.BMEdge.smooth'),
            ('value=edge.calc_face_angle(bpy.context.object)\nvalue.unsupported_magic()',
             'bpy.types.Object.unsupported_magic'),
        ):
            with self.subTest(expression=expression):
                result = self.hb('check', self.script(setup + expression), ok=False)
                self.assertTrue(any(expected in e['message'] for e in result['errors']))
        self.hb('run', self.script(setup + '''
try:edge.calc_face_angle(fallback=0)
except TypeError:pass
else:raise AssertionError('Keyword accepted')
try:edge.calc_face_angle(0,1)
except TypeError:pass
else:raise AssertionError('Excess arguments accepted')
bm.free()
'''))
        self.hb('run', self.script('import bpy\nbpy.ops.mesh.primitive_cube_add()'))
        before = (self.path / 'scene.hb').read_bytes()
        result = self.hb('run', self.script(setup + '''
bpy.context.object.location.x=9
edge.calc_face_angle()
'''), ok=False)
        self.assertEqual(result['error']['code'], 'SCRIPT_ERROR')
        self.assertIn("doesn't use 2 faces", result['error']['message'])
        self.assertEqual((self.path / 'scene.hb').read_bytes(), before)
        result = self.hb('run', self.script(setup + '''
c=bm.verts.new((0,1,0));d=bm.verts.new((0,0,1))
bm.faces.new((a,b,c));bm.faces.new((b,a,d))
a.co=(float('nan'),0,0)
bm.normal_update()
edge.calc_face_angle()
'''), ok=False)
        self.assertEqual(result['error']['code'], 'UNSUPPORTED_API')
        self.assertIn('must be finite', result['error']['message'])
        self.assertEqual((self.path / 'scene.hb').read_bytes(), before)

    def test_mcp_executes_edge_angle_geometry(self):
        request = test_server.request
        fixture = test_cli.ROOT / 'compat/golden/m3_bmesh_edge_angle.py'
        replies = self.exchange('--mcp', [
            request(0, 'initialize', {'protocolVersion': '2025-11-25',
                                      'clientInfo': {}, 'capabilities': {}}),
            {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
            request(1, 'tools/call', {'name': 'hb_run', 'arguments': {
                'args': [str(fixture), '--out', 'angles.glb']}}),
            request(2, 'tools/call', {'name': 'hb_query', 'arguments': {'args': ['stats']}}),
        ], self.path)
        self.assertFalse(replies[1]['result']['isError'])
        self.assertTrue(replies[1]['result']['structuredContent']['ok'])
        stats = replies[2]['result']['structuredContent']['result']
        self.assertEqual((stats['objects'], stats['triangles']), (1, 3))
