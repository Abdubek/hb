"""Preflight must follow real BMesh primitive output dictionaries."""
import unittest

import test_cli
import test_server


PRIMITIVES = (
    'create_cube(bm,size=2)',
    'create_grid(bm,x_segments=1,y_segments=1,size=1)',
    'create_uvsphere(bm,u_segments=8,v_segments=4,radius=1)',
    'create_cone(bm,segments=8,radius1=1,radius2=.5,depth=2)',
    'create_circle(bm,segments=8,radius=1)',
)
EXTRACTIONS = (
    "result['verts'][0]",
    "result.get('verts',())[0]",
    "result.copy().get('verts')[0]",
    "next(iter(result.values()))[0]",
    "list(result.items())[0][1][0]",
    "result.setdefault('verts',())[0]",
    "result.pop('verts')[0]",
)
CONTROL = '''import bpy,bmesh
bm=bmesh.new()
cube=bmesh.ops.create_cube(bm,size=2)['verts']
bmesh.ops.translate(bm,verts=cube,vec=(0,0,.5))
mesh=bpy.data.meshes.new('Mesh')
bm.to_mesh(mesh)
bm.free()
obj=bpy.data.objects.new('Result',mesh)
bpy.context.collection.objects.link(obj)
'''


class CheckerBMeshResults(unittest.TestCase):
    setUp = test_cli.CLI.setUp
    tearDown = test_cli.CLI.tearDown
    hb = test_cli.CLI.hb
    script = test_cli.CLI.script
    exchange = test_server.Server.exchange

    def test_primitive_dictionary_helpers_execute_and_match_control(self):
        source = test_cli.ROOT / 'compat/golden/m3_checker_bmesh_results.py'
        self.hb('check', source)
        self.hb('run', source, '--out', 'results.glb')
        self.hb('run', self.script(CONTROL), '--scene', 'control.hb', '--out', 'control.glb')
        actual = test_cli.revision(self.path / 'scene.hb')['scene']
        self.assertEqual(actual, test_cli.revision(self.path / 'control.hb')['scene'])
        self.assertEqual(sorted({v[2] for v in actual['meshes'][0]['vertices']}), [-.5, 1.5])
        self.assertEqual((self.path / 'results.glb').read_bytes(),
                         (self.path / 'control.glb').read_bytes())

    def test_every_primitive_retains_vertex_api_after_dictionary_access(self):
        for primitive in PRIMITIVES:
            for extraction in EXTRACTIONS:
                with self.subTest(primitive=primitive, extraction=extraction):
                    source = ('import bmesh\nbm=bmesh.new()\nresult=bmesh.ops.' + primitive +
                              '\nvertex=' + extraction + '\nvertex.calc_shell_factor()')
                    errors = self.hb('check', self.script(source), ok=False)['errors']
                    self.assertEqual(len(errors), 1, errors)
                    self.assertIn('bmesh.types.BMVert.calc_shell_factor', errors[0]['message'])

    def test_items_and_helper_returns_keep_vertex_api(self):
        cases = [
            "for key,group in result.items():\n    group[0].calc_shell_factor()",
            "def unpack(output):return output.get('verts',())\nunpack(result)[0].calc_shell_factor()",
            "values=[result]\nvalues[0].get('verts')[0].calc_shell_factor()",
            "for group in result.values():\n    group[0].calc_shell_factor()",
        ]
        for body in cases:
            with self.subTest(body=body):
                errors = self.hb('check', self.script('import bmesh\nbm=bmesh.new()\n'
                    'result=bmesh.ops.create_cube(bm,size=2)\n' + body), ok=False)['errors']
                self.assertEqual(len(errors), 1, errors)
                self.assertIn('bmesh.types.BMVert.calc_shell_factor', errors[0]['message'])

    def test_mcp_checks_extracted_vertices_before_execution_and_recovers(self):
        source = '''import bmesh
open('executed','w').write('preflight was bypassed')
bm=bmesh.new()
result=bmesh.ops.create_cube(bm,size=2)
result.get('verts',())[0].calc_shell_factor()
'''
        replies = self.exchange('--mcp', [
            test_server.request(0, 'initialize', {'protocolVersion': '2025-11-25',
                                                 'clientInfo': {}, 'capabilities': {}}),
            {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
            test_server.request(1, 'tools/call', {'name': 'hb_run', 'arguments': {'code': source}}),
            test_server.request(2, 'tools/call', {'name': 'hb_run', 'arguments': {
                'code': (test_cli.ROOT / 'compat/golden/m3_checker_bmesh_results.py').read_text(),
                'args': ['--out', 'mcp.glb']}}),
            test_server.request(3, 'tools/call', {'name': 'hb_query',
                                                'arguments': {'args': ['stats']}}),
        ], self.path)
        self.assertTrue(replies[1]['result']['isError'])
        errors = replies[1]['result']['structuredContent']['errors']
        self.assertEqual(len(errors), 1, errors)
        self.assertIn('bmesh.types.BMVert.calc_shell_factor', errors[0]['message'])
        self.assertFalse((self.path / 'executed').exists())
        self.assertFalse(replies[2]['result']['isError'], replies[2])
        self.assertEqual(replies[3]['result']['structuredContent']['result']['objects'], 1)
        self.assertEqual(replies[3]['result']['structuredContent']['revision'],
                         replies[2]['result']['structuredContent']['revision'])
        self.hb('run', self.script(CONTROL), '--scene', 'control.hb', '--out', 'control.glb')
        self.assertEqual(test_cli.revision(self.path / 'scene.hb')['scene'],
                         test_cli.revision(self.path / 'control.hb')['scene'])
        self.assertEqual((self.path / 'mcp.glb').read_bytes(),
                         (self.path / 'control.glb').read_bytes())
